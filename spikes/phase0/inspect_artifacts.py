"""Read real artifacts locally and emit structural summaries without raw content."""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from defusedxml.ElementTree import fromstring

MAX_XML_BYTES = 10 * 1024 * 1024
MAX_HTML_BYTES = 4 * 1024 * 1024
MAX_LOG_BYTES = 1024 * 1024


def read_bounded(path, root, maximum):
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError("Artifact resolves outside the supplied directory")
    with resolved.open("rb") as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError("Artifact exceeds the probe size budget")
    return data


def status(case):
    tags = {child.tag for child in case}
    for tag in ("error", "failure", "skipped"):
        if tag in tags:
            return {"error": "error", "failure": "failed", "skipped": "skipped"}[tag]
    return "passed"


def candidate_ids(case):
    parts = case.get("classname", "").split(".")
    return {
        "/".join(parts[:i]) + ".py::" + "::".join(parts[i:] + [case.get("name", "")])
        for i in range(1, len(parts) + 1)
    }


def phase_matches(case, html_items):
    """Preserve phase; match suffix only when XML independently names that phase."""
    error = case.find("error")
    message = error.get("message", "").lower() if error is not None else ""
    candidates = candidate_ids(case)
    return [
        (item["testId"], phase)
        for item in html_items
        if item["result"] == "Error"
        for phase in ("setup", "teardown")
        if phase in message
        and item["testId"].endswith("::" + phase)
        and item["testId"][: -(len(phase) + 2)] in candidates
    ]


def summarize(xml_path, root, xml_bytes, tree, git_repo=None):
    run = xml_path.parent.parent
    html_path = run / "reports" / "report.html"
    log_path = run / "pytest.log"
    html_bytes = read_bounded(html_path, root, MAX_HTML_BYTES)
    log_bytes = read_bounded(log_path, root, MAX_LOG_BYTES)
    soup = BeautifulSoup(html_bytes.decode("utf-8"), "html.parser")
    container = soup.find(id="data-container")
    if container is None:
        raise ValueError("Unsupported HTML format: missing data-container")
    payload = json.loads(container["data-jsonblob"])
    html_items = [item for items in payload["tests"].values() for item in items]
    html_ids = Counter(item["testId"] for item in html_items)
    cases = list(tree.iter("testcase"))
    mapping_counts = Counter()
    matched_ids = []
    phase_counts = Counter()
    for case in cases:
        candidates = candidate_ids(case)
        matches = candidates & html_ids.keys()
        mapping_counts[len(matches)] += 1
        if len(matches) == 1:
            matched_ids.append(next(iter(matches)))
        else:
            phase_counts[len(phase_matches(case, html_items))] += 1
    properties = {item.get("name"): item.get("value") for item in tree.iter("property")}
    suites = list(tree.iter("testsuite"))
    environment = payload.get("environment", {})
    sha = properties.get("git_revision") or ""
    timestamps = [datetime.fromisoformat(suite.attrib["timestamp"]) for suite in suites]
    declared = {
        key: sum(int(suite.get(key, "0")) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    observed = Counter(status(case) for case in cases)
    junit_ids = Counter((case.get("classname"), case.get("name")) for case in cases)
    return {
        "run_directory": run.name,
        "files": {
            label: {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for label, data in (
                ("junit.xml", xml_bytes),
                ("report.html", html_bytes),
                ("pytest.log", log_bytes),
            )
        },
        "junit_declared": declared,
        "junit_observed": dict(observed),
        "declared_counts_match_cases": declared
        == {
            "tests": len(cases),
            "failures": observed["failed"],
            "errors": observed["error"],
            "skipped": observed["skipped"],
        },
        "duplicate_junit_id_count": sum(count - 1 for count in junit_ids.values()),
        "html_outcomes": dict(Counter(item["result"] for item in html_items)),
        "html_record_count": len(html_items),
        "html_duplicate_test_id_count": sum(count - 1 for count in html_ids.values()),
        "candidate_mapping_match_counts": {
            str(key): value for key, value in mapping_counts.items()
        },
        "candidate_mapping_is_bijective": (
            len(matched_ids) == len(cases) == len(html_items)
            and len(set(matched_ids)) == len(matched_ids)
        ),
        "unmatched_cases_phase_candidate_counts": {
            str(key): value for key, value in phase_counts.items()
        },
        "junit_property_names": sorted(properties),
        "run_id_matches_directory": properties.get("run_id") == run.name,
        "html_run_id_matches_junit": environment.get("run_id")
        == properties.get("run_id"),
        "git_sha_has_full_shape": bool(re.fullmatch(r"[0-9a-f]{40}", sha)),
        "html_sha_matches_junit": environment.get("git_revision") == sha,
        "git_object_verified": (
            subprocess.run(
                [
                    "git",
                    "-c",
                    f"safe.directory={git_repo}",
                    "-C",
                    str(git_repo),
                    "cat-file",
                    "-e",
                    f"{sha}^{{commit}}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            ).returncode
            == 0
            if git_repo is not None and re.fullmatch(r"[0-9a-f]{40}", sha)
            else False
        ),
        "timestamps_timezone_aware": all(
            value.tzinfo is not None for value in timestamps
        ),
        "timestamps_utc": [
            value.astimezone(timezone.utc).isoformat()
            for value in timestamps
            if value.tzinfo
        ],
        "log_line_count": len(log_bytes.splitlines()),
        "log_level_mentions": dict(
            Counter(
                re.findall(
                    r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b",
                    log_bytes.decode("utf-8"),
                )
            )
        ),
        "test_source_read": False,
        "external_writes": False,
    }


def inspect(root, git_repo=None):
    root = root.resolve(strict=True)
    files = sorted(
        root.glob("*/reports/junit.xml"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    selected = {}
    failing_runs = 0
    for path in files:
        data = read_bounded(path, root, MAX_XML_BYTES)
        tree = fromstring(data)
        outcomes = Counter(status(case) for case in tree.iter("testcase"))
        if outcomes["failed"] or outcomes["error"]:
            failing_runs += 1
        label = (
            "latest_error"
            if outcomes["error"]
            else "latest_failure"
            if outcomes["failed"]
            else "latest_without_failures"
        )
        if label not in selected:
            selected[label] = summarize(path, root, data, tree, git_repo)
    return {
        "selection": "Newest file mtime per outcome; report timestamps recorded separately; not a chronology guarantee",
        "junit_file_count": len(files),
        "runs_with_failure_or_error": failing_runs,
        "samples": selected,
        "limitations": [
            "Original contents, local absolute paths, hostnames and test names are omitted",
            "Candidate ID reconstruction is an experiment for this pytest-html format, not an adopted adapter contract",
            "Retry, campaign and stand semantics are not inferred",
            "JUnit is used as the counting source for this probe only; HTML and logs are not added to its totals",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--git-repo",
        type=Path,
        help="Verify commit objects only; never read test source",
    )
    args = parser.parse_args()
    result = inspect(args.artifacts_dir, args.git_repo)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "junit_files": result["junit_file_count"],
                "selected": list(result["samples"]),
            }
        )
    )
