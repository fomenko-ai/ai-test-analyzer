# Stage 1 — Local JUnit vertical slice

Date: 2026-11-27. Status: local Stage 1 complete; corporate checks and production acceptance remain pending. The owner authorized continuation after the Phase 0 stop. This stage implements a local, file-based dry-run. Stage 2 ReportPortal collection, cause analysis and all corporate publication remain unimplemented.

## Implemented behavior

The CLI validates settings and file context before loading input, reads bounded JUnit XML, produces normalized results and evidence references, and writes `normalized.json`, `plan.json` and a Jinja2 `report.html` in a new private directory. The composition root wires an asynchronous source port and a local report writer into an asynchronous application use case. Domain normalization and planning are synchronous and import no network, filesystem or LLM implementations. File reads run in a worker thread; no network client is constructed.

Settings are YAML: `schema_version: '1.0'`, `publish_enabled: false`, and `max_xml_bytes` (default 10485760; allowed positive integer up to 104857600). Context is JSON: schema_version plus optional source_instance, project_key, run_id, stand_id, campaign_id, git_sha, firmware_version and software_version. Identifiers allow 1–128 ASCII letters/digits and `_ . : -`; SHA is exactly 40 lowercase hex digits. Supply identifiers only, never credentials. Unknown and duplicate configuration keys, unsafe YAML constructors, invalid values and publication enablement are rejected. FileContext is an explicitly separate local contract; the original ReportPortal RunContext and corporate configuration examples remain future specifications.

JUnit metadata recognizes run_id, stand/stand_id, campaign_id, git_revision/git_sha, firmware_version and software_version. Context supplements absent values; equal values have provenance `both`. Disagreement becomes null with a data conflict, without choosing a source silently. Missing metadata remains null. Invalid or contradictory source properties are recorded as conflicts, without copying their values. Source test counts are checked against observed testcase records; mismatches remain visible, while observed outcomes are preserved.

Supported XML is the observed non-namespaced pytest-style testsuite/testsuites dialect: testcase outcomes use failure/error/skipped child elements; otherwise passed. Unknown structures, contradictory outcomes, DTD/entities, non-finite or negative durations and attribute-based outcome dialects are rejected. XML is bounded by configured bytes and 64 levels of nesting. The parser does not execute scripts or fetch referenced resources. Inputs must be regular files; an input symlink resolving outside its supplied parent directory is rejected. Zero-test reports remain zero records, not a fabricated successful test.

Counts refer to testcase records, without resolving retries. Every duplicate record retains a distinct item and an evidence locator. SHA256 content references and zero-based testcase indices identify the original authorized XML without storing a personal absolute path. The original XML is neither copied nor modified. Raw names, messages, logs, tracebacks and arbitrary properties are omitted from output; test identity is hashed, node_id and attempt remain null. This intentionally limits report detail while avoiding transfer of unreviewed raw content. It is not a general secret-redaction implementation or an HTML/log adapter.

Local identifiers are reproducible for identical bytes/context and independent of input/output paths. They are versioned local keys, not publication markers or defect fingerprints. Different bytes/context may change them; no cross-revision identity guarantee is claimed. Timestamps require explicit offsets and normalize to UTC; incomplete/naive timestamps leave started_at null with missing_data. Source SHA metadata is preserved but not verified against Git by this stage.

The plan records a blocked `investigation_required` entry per failed/error record. Analysis and duplicate lookup are `not_performed`; there are no executable Jira payloads, external operations or invented classifications. A successful local collection does not claim a completed cause investigation or absence of defects. Passing/skipped-only input has no required failure investigations.

Output directories must be new, including on rerun. Directories use mode 0700 and files 0600. Existing destinations are rejected. Files are prepared in a temporary directory before reserving the destination; this is not a durable publication journal or a fully atomic bundle transaction. An I/O failure during final placement can leave an incomplete destination and returns failure; choose a new directory after resolving it. No restart/idempotency guarantee for corporate operations is claimed.

Exit codes: 0 complete local dry-run, 2 local report with data conflicts, 1 configuration/context/source/output/dependency failure. Argparse usage errors also return 2. Failure/error test outcomes do not change the analyzer exit code by themselves. Missing information is explicit in the report and does not fabricate a failed integration call. Diagnostics omit raw exception text and input contents.

## Dependency and build evidence

Public PyPI metadata was rechecked on 2026-11-27, including non-yanked published artifacts. Direct stable versions match the Phase 0 candidates: OpenAI 3.60.0, MCP 2.3.0, HTTPX2 2.16.2, Pydantic 2.14.4, pydantic-settings 2.16.3, PyYAML 6.0.4, Jinja2 3.1.6, beautifulsoup4 4.15.0, defusedxml 0.7.1, pytest 9.2.0, pytest-asyncio 1.5.0, pytest-cov 7.1.0, Ruff 0.17.6, mypy 2.4.1, uv/uv_build 0.13.10. The official Python FTP directory's latest numeric 3.14 patch observed was 3.14.10. See [recorded metadata](stage1-dependency-metadata.json); metadata alone does not establish compatibility.

A new application `uv.lock` was generated by `uv lock --default-index https://pypi.org/simple`, not copied from the spike. It resolves 57 entries. `uv sync --locked --all-extras --group dev` succeeded under CPython 3.14.10 / uv 0.13.10 on Linux amd64, installing 54 packages including the application. Offline locked sync was repeated successfully. All inherited runtime dependencies remain pinned; their presence does not mean their corporate adapters exist.

The checks below were executed inside the official uv Python image, with the repository mounted and UV_PROJECT_ENVIRONMENT/UV_CACHE_DIR directed to the preserved probe volume. The host's older Python/uv were not upgraded. Networking was disabled for behavior checks.

| Check | Confirmed outcome |
|---|---|
| `uv run --locked --offline pytest -q` | 25 synthetic tests passed |
| `uv run --locked --offline ruff check .` | Passed; E/F/I excluding E501; spike/bootstrap files excluded |
| `uv run --locked --offline ruff format --check .` | Passed |
| `uv run --locked --offline mypy src` | Passed, 15 source files |
| `uv build --offline` | Application sdist and wheel built |
| Wheel installation | Built wheel installed with --no-deps --reinstall over verified locked dependencies; import location confirmed inside site-packages |
| Installed-wheel CLI | --help and fixture dry-run succeeded, including packaged Jinja2 template |
| Fixture dry-run with config/context | 4 total: 1 passed, 1 failed, 1 error, 1 skipped; UTC timestamp and provenance preserved |
| Rerun/security tests | Identical normalized results on separate outputs; existing destination/source preserved; network connect prohibited; raw secret sentinel omitted; malformed XML/config, duplicate records, symlink escape and size/depth limits tested |

Initial mypy errors were corrected and checks repeated. A fresh-environment wheel-install attempt first used unsupported extras syntax, then offline dependency resolution lacked registry metadata. Neither was reported as a successful check. The confirmed wheel smoke uses dependencies already installed from the application lock and verifies that imports come from the installed wheel, not editable source.

## Real artifact and container evidence

The final application was run against the three Phase 0 selections, with source directories mounted read-only and container networking disabled. Raw reports were not copied into Git; generated local bundles remained outside the repository. These are real local artifact checks, not corporate integration tests. No neighboring test source was read, no tests in that project were executed and no equipment was operated.

| Run directory | Expected and observed testcase statistics |
|---|---|
| 2026-11-19_09-28-34_279603 | 239 total; 230 passed, 9 skipped |
| 2026-10-23_14-27-34_238287 | 52 total; 51 passed, 1 failed |
| 2026-09-14_07-43-52_277984 | 1 total; 1 error |

Only JUnit contributes counts. HTML/log data and ERROR-level log mentions do not create additional results or change test outcomes.

Image manifests were inspected again and the Dockerfile pins the observed index digests:

- Build: `ghcr.io/astral-sh/uv@sha256:b093dbbd7963c765325ecdf866d42915f5327e135569f9dae9c77cac63559bf2` (CPython 3.14.10, uv 0.13.10).
- Runtime: `python:3.14.10-slim-trixie@sha256:22eafb370920ad8b429e0aec3fff433e0669968519f5d60469d83729c138b28b`.

`docker build -t ai-test-analyzer:0.1.0 .` succeeded. The final image runs as UID/GID 10001, installs all runtime extras with --locked and excludes development dependencies. --help and a fixture dry-run succeeded without networking. Fixture and real-artifact dry-runs also succeeded with read-only root filesystem and writable temporary output only. README contains the exercised commands. Execution was verified on local Linux amd64 only; multi-architecture execution was not tested. No image was pushed or deployed.

## Remaining boundaries

Corporate ReportPortal, Jira, Confluence, LLM and CI/DUT services remain blocked for real validation. Grouping, cause analysis, duplicate search, configurable Jira actions, publication, journal/recovery, scheduler and universal HTML parsing are outside this stage. Production fingerprints/markers, routing, template formats and retention remain unresolved corporate decisions. No corporate writes are enabled or exposed by the CLI.

Approved dependency/image vulnerability scans and production target-platform confirmation remain pending, as in Phase 0. No security certification, complete corporate dependency gate or production baseline acceptance is claimed. Further development must preserve the distinction between local fixtures/artifacts and tested integrations.
