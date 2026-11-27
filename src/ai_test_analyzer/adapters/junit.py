"""JUnit testcase records are authoritative for this bounded local slice."""

import asyncio
import hashlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element

from defusedxml.ElementTree import fromstring  # type: ignore[import-untyped]
from pydantic import ValidationError

from ai_test_analyzer.adapters.files import InputError, read_bounded
from ai_test_analyzer.domain.models import FileContext, RawCase, SourceRun
from ai_test_analyzer.domain.normalize import digest

PROPERTY_FIELDS = {
    "run_id": "run_id",
    "stand": "stand_id",
    "stand_id": "stand_id",
    "campaign_id": "campaign_id",
    "git_revision": "git_sha",
    "git_sha": "git_sha",
    "firmware_version": "firmware_version",
    "software_version": "software_version",
}


def outcome(case: Element) -> str:
    outcomes = [
        tag for tag in ("failure", "error", "skipped") if case.find(tag) is not None
    ]
    if len(outcomes) > 1:
        raise InputError("JUnit testcase has conflicting outcomes")
    return {"failure": "failed", "error": "error", "skipped": "skipped"}.get(
        outcomes[0] if outcomes else "", "passed"
    )


def parse_junit(data: bytes) -> SourceRun:
    root = fromstring(data, forbid_dtd=True)
    if root.tag not in {"testsuite", "testsuites"}:
        raise InputError("Unsupported JUnit root or namespace")
    # Reject unknown structure instead of quietly reporting zero tests.
    allowed_children = {
        "testsuites": {"testsuite", "testsuites"},
        "testsuite": {
            "testsuite",
            "testcase",
            "properties",
            "system-out",
            "system-err",
        },
        "testcase": {
            "failure",
            "error",
            "skipped",
            "properties",
            "system-out",
            "system-err",
        },
        "properties": {"property"},
        "property": set(),
        "failure": set(),
        "error": set(),
        "skipped": set(),
        "system-out": set(),
        "system-err": set(),
    }
    pending = [(root, 1)]
    while pending:
        parent, depth = pending.pop()
        if depth > 64:
            raise InputError("JUnit XML exceeds the supported nesting depth")
        pending.extend((child, depth + 1) for child in parent)
        if parent.tag in allowed_children:
            if any(child.tag not in allowed_children[parent.tag] for child in parent):
                raise InputError("Unsupported JUnit suite structure")
    cases = []
    missing = [
        "attempt_semantics",
        "git_source_not_verified",
        "cause_analysis_not_performed",
    ]
    conflicts = []
    for index, case in enumerate(root.iter("testcase")):
        if "status" in case.attrib or "result" in case.attrib:
            raise InputError("Attribute-based JUnit outcomes are unsupported")
        if not case.get("name"):
            missing.append(f"testcase.{index}.name")
        duration = case.get("time")
        if duration is None:
            missing.append(f"testcase.{index}.duration")
        cases.append(
            RawCase.model_validate(
                {
                    "identity_digest": digest(
                        [case.get("classname"), case.get("name")]
                    ),
                    "status": outcome(case),
                    "duration_seconds": float(duration)
                    if duration is not None
                    else None,
                }
            )
        )
    for suite in root.iter():
        if suite.tag not in {"testsuite", "testsuites"}:
            continue
        counts = Counter(outcome(case) for case in suite.iter("testcase"))
        expected = {
            "tests": sum(counts.values()),
            "failures": counts["failed"],
            "errors": counts["error"],
            "skipped": counts["skipped"],
        }
        for field, value in expected.items():
            declared = suite.get(field)
            if declared is not None and (
                not declared.isdecimal() or int(declared) != value
            ):
                conflicts.append(f"junit.declared_{field}")
    properties: dict[str, set[str]] = {}
    for suite in root.iter("testsuite"):
        for prop in suite.findall("properties/property"):
            property_field = PROPERTY_FIELDS.get(prop.get("name", ""))
            if property_field:
                properties.setdefault(property_field, set()).add(prop.get("value", ""))
    metadata = {}
    for field, values in properties.items():
        if len(values) != 1:
            conflicts.append(f"junit.metadata.{field}")
            continue
        metadata_value = next(iter(values))
        try:
            FileContext.model_validate({field: metadata_value})
        except ValidationError:
            conflicts.append(f"junit.invalid_metadata.{field}")
        else:
            metadata[field] = metadata_value
    starts = []
    suites = list(root.iter("testsuite"))
    for suite in suites:
        timestamp = suite.get("timestamp")
        try:
            start = datetime.fromisoformat(timestamp) if timestamp else None
        except ValueError:
            start = None
        if start is None or start.tzinfo is None:
            missing.append("started_at")
        else:
            starts.append(start.astimezone(timezone.utc))
    started_at = min(starts) if starts and len(starts) == len(suites) else None
    if started_at is None:
        missing.append("started_at")
    return SourceRun(
        artifact_digest=hashlib.sha256(data).hexdigest(),
        context=FileContext.model_validate(metadata),
        cases=tuple(cases),
        started_at=started_at,
        missing_data=tuple(missing),
        data_conflicts=tuple(conflicts),
    )


class JUnitSource:
    def __init__(self, path: Path, maximum: int) -> None:
        self.path = path
        self.maximum = maximum

    async def load(self) -> SourceRun:
        return await asyncio.to_thread(self._load)

    def _load(self) -> SourceRun:
        try:
            data = read_bounded(self.path, self.maximum)
        except InputError:
            raise
        except OSError:
            raise InputError("JUnit source is unavailable") from None
        try:
            return parse_junit(data)
        except Exception:
            raise InputError("Invalid or unsupported JUnit XML") from None
