"""Deterministic local identities are versioned, not defect fingerprints."""

import hashlib
import json
from collections import Counter

from ai_test_analyzer.domain.models import (
    DeferredInvestigation,
    DryRunPlan,
    EvidenceRef,
    FileContext,
    MetadataOrigin,
    Settings,
    SourceRun,
    Statistics,
    TestItem,
    TestRun,
)


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def normalize(source: SourceRun, context: FileContext) -> TestRun:
    merged: dict[str, object] = {}
    provenance: dict[str, MetadataOrigin] = {}
    missing = list(source.missing_data)
    conflicts = list(source.data_conflicts)
    for field in FileContext.model_fields:
        if field == "schema_version":
            continue
        supplied, observed = getattr(context, field), getattr(source.context, field)
        if supplied is not None and observed is not None and supplied != observed:
            merged[field] = None
            provenance[field] = "conflict"
            conflicts.append(f"context.{field}")
        elif supplied is not None:
            merged[field] = supplied
            provenance[field] = "both" if observed is not None else "context"
        elif observed is not None:
            merged[field] = observed
            provenance[field] = "junit"
        else:
            merged[field] = None
            provenance[field] = "missing"
            missing.append(f"context.{field}")
    effective = FileContext.model_validate(merged)
    # Including content avoids merging conflicting artifacts with the same run_id.
    run_key = "file-v1-" + digest(
        {"context": effective.model_dump(), "artifact": source.artifact_digest}
    )
    items = []
    for index, case in enumerate(source.cases):
        item_key = "item-v1-" + digest([run_key, case.identity_digest, index])
        evidence = EvidenceRef(
            evidence_id="evidence-v1-" + digest([source.artifact_digest, index]),
            source_uri_or_id=f"artifact:sha256:{source.artifact_digest}",
            artifact_sha256=source.artifact_digest,
            testcase_index=index,
        )
        items.append(
            TestItem(
                item_key=item_key,
                identity_digest=case.identity_digest,
                status=case.status,
                duration_seconds=case.duration_seconds,
                evidence_refs=(evidence,),
            )
        )
    counts = Counter(case.status for case in source.cases)
    return TestRun(
        run_key=run_key,
        context=effective,
        metadata_provenance=provenance,
        artifact_digest=source.artifact_digest,
        started_at=source.started_at,
        statistics=Statistics(
            total=len(items),
            passed=counts["passed"],
            failed=counts["failed"],
            error=counts["error"],
            skipped=counts["skipped"],
        ),
        test_items=tuple(items),
        missing_data=tuple(sorted(set(missing))),
        data_conflicts=tuple(sorted(set(conflicts))),
    )


def plan(run: TestRun, settings: Settings) -> DryRunPlan:
    return DryRunPlan(
        run_key=run.run_key,
        config_digest=digest(settings.model_dump()),
        investigations=tuple(
            DeferredInvestigation(item_key=item.item_key)
            for item in run.test_items
            if item.status in {"failed", "error"}
        ),
    )
