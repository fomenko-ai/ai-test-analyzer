# Phase 0 — Technical Spike Plan

Date: 2026-11-26; closeout update: 2026-11-27. Status: available local execution completed; corporate checks remain blocked. The owner requested a stop before Stage 1. Dependency probes used public sources and the official uv image. See [technical-spike-results.md](technical-spike-results.md) for actual observations. The remaining sections preserve the approved plan and planning-time review, not successful verification results.

## Review scope and conclusions

Reviewed AGENTS.md, README.md, all documents in docs/ (including the initialization prompt), all examples including the hidden bootstrap Python version, and the external investigation skill. The repository is a design package with illustrative configuration and contracts, not an application. No source package or real lockfile exists. Requirements support a fixture-based vertical slice without corporate access; production publication remains blocked until infrastructure validation.

The design consistently separates analysis from deterministic publication, preserves test outcomes, requires matching source SHA, and supports one publisher with recovery. JSON journaling is not an exactly-once or distributed-lock guarantee. Candidate fingerprint similarity does not prove common causality. Pydantic and valid evidence IDs cannot establish root cause on their own.

Resolved owner decisions: asynchronous network I/O with a synchronous domain core (ADR-018); configurable test-analysis actions; other categories default to report-only even with insufficient evidence; analyzer technical failures always report-only (ADR-019). The generic insufficient-evidence example rules have been narrowed to eligible categories. Independently verified known occurrences may still receive comments during an LLM outage.

The external investigation skill was reviewed as an artifact; it was not invoked. It remains manually started by engineers and does not become a runtime dependency.

## Evidence levels and public metadata review

Keep four independent evidence levels: public release metadata, approved-registry resolution/installation, local fixture tests, and corporate integration tests. Success at one level does not imply another. No candidate is an adopted baseline yet. Public PyPI pages were inspected for the following candidate artifacts on 2026-11-26; their presence does not demonstrate joint CPython 3.14 compatibility or guarantee that no newer stable release exists.

| Package | Candidate artifact observed | Source |
|---|---|---|
| openai | 3.59.0 | [PyPI](https://pypi.org/project/openai/) |
| mcp | 2.3.0 | [PyPI](https://pypi.org/project/mcp/) |
| pydantic | 2.14.4 | [PyPI](https://pypi.org/project/pydantic/) |
| pydantic-settings | 2.16.3 | [PyPI](https://pypi.org/project/pydantic-settings/) |
| httpx | 0.28.1 | [PyPI](https://pypi.org/project/httpx/) |
| PyYAML | 6.0.4 | [PyPI](https://pypi.org/project/PyYAML/) |
| Jinja2 | 3.1.6 | [PyPI](https://pypi.org/project/Jinja2/) |
| beautifulsoup4 | 4.15.0 | [PyPI](https://pypi.org/project/beautifulsoup4/) |
| defusedxml | 0.7.1 | [PyPI](https://pypi.org/project/defusedxml/) |
| pytest | 9.2.0 | [PyPI](https://pypi.org/project/pytest/) |
| pytest-asyncio | 1.5.0 | [PyPI](https://pypi.org/project/pytest-asyncio/) |
| pytest-cov | 7.1.0 | [PyPI](https://pypi.org/project/pytest-cov/) |
| ruff | 0.17.6 | [PyPI](https://pypi.org/project/ruff/) |
| mypy | 2.4.1 | [PyPI](https://pypi.org/project/mypy/) |
| uv / uv_build | Public pages inspected; inherited 0.13.10 remains pending release-history confirmation | [uv](https://pypi.org/project/uv/), [uv-build](https://pypi.org/project/uv-build/) |

[CPython 3.14.10](https://www.python.org/downloads/release/python-31410/) is published; installation is pending. [Compose latest](https://github.com/docker/compose/releases/latest) resolved to v5.8.0. [ReportPortal MCP latest](https://github.com/reportportal/reportportal-mcp-server/releases/latest) resolved to 2.0.0, newer than inherited 1.4.1. Evaluate the stable 2.0.0 contract before selecting a server version; do not assume the installed corporate server can be upgraded.

The [Python image catalog](https://hub.docker.com/_/python) and [uv container catalog](https://github.com/astral-sh/uv/pkgs/container/uv) were accessible. Exact candidate manifests, architecture coverage, digests, approved-mirror availability and executable compatibility remain unverified. Release publication does not confirm a container tag. Bootstrap pins remain explicitly unverified and unchanged.

## Execution boundaries and order

1. Obtain approval for this plan, then confirm the approved registries, target Linux architecture and safe evidence locations. Collect sanitized source samples and read-only integration access.
2. Perform dependency and image metadata checks, then isolated dependency probes and fixture contract experiments. These are disposable spike artifacts, not the application skeleton.
3. Run authorized corporate read-only probes. Mark unavailable integrations blocked; use explicitly labeled fixtures for local work.
4. Present findings, measured limits and proposed contracts for review. Agree fingerprint/marker formats and configuration decisions before implementing them.
5. Test external write capabilities only under a separate explicit sandbox-write authorization. This initialization task authorizes no Jira/Confluence writes, including sandbox writes.
6. Stage 1 implements the actual skeleton, generates its real uv.lock, runs the full checks and builds the analyzer container. A dependency-only spike environment does not satisfy the application build gate.

## Investigations, acceptance criteria and evidence

All checks below are pending. Each record must contain the environment, versions, date, command or operation, sanitized input identifier, actual outcome, limitations and pass/fail/blocked status. Keep raw sensitive evidence outside Git under the approved retention policy.

| ID | Investigation and method | Acceptance criteria | Required evidence |
|---|---|---|---|
| S01 | Dependencies: query release histories and Requires-Python in the approved registry; exclude prereleases/yanked releases; resolve runtime, extras and dev together on standard-GIL CPython 3.14 | Latest stable compatible combination selected with documented constraints; real isolated lock/sync succeeds; native wheels or approved source-build requirements identified | Registry provenance, version matrix, interpreter/platform output, resolver and install logs, generated probe lock |
| S02 | Imports and local SDK/parser probes with the resolved environment | Imports work; Pydantic rejects invalid contracts; HTTP and LLM mocks exercise timeout/error handling; safe XML/HTML parsing rejects malicious/oversized inputs; async MCP initialize/list/call works against a local fixture server | Executable probe scripts, fixture provenance, test output; explicitly no corporate-integration claim |
| S03 | Image/host tooling: inspect manifests in approved registries for Python, uv and optional ReportPortal MCP; inspect latest compatible stable alternatives | Exact tags and platform digests recorded; target architecture supported; Git/CA requirements understood; no Docker socket required | Manifest output, architecture matrix, host Engine/Buildx/Compose versions, scanner findings; analyzer build deferred to Stage 1 |
| S04 | Source samples: successful/failed RP launches, retries, JUnit, supported HTML, DUT and CI metadata | Explicit authoritative status source, ID/attempt mapping and enrichment rules; counts reconcile without double counting; missing/conflicting data visible; campaign membership is explicit | Sanitized samples and expected normalized records; timezone/encoding/status/attempt mapping table (AC-01/08/14) |
| S05 | ReportPortal read contracts: introspect installed MCP; compare required REST capabilities | Launch IDs distinguished from UUID/sequence; pagination complete; terminal states, attributes, logs, attachments and history retrieved or a bounded limitation recorded; no RP mutation | Installed version/tool inventory, sanitized paginated responses, capability/fallback matrix and permission failures |
| S06 | Git and CI artifact access using authorized samples | Full SHA verified before source reads; mismatched/unavailable SHA yields missing data; paths, hosts, sizes and archives bounded; equivalent Jenkins/GitLab/manual manifests normalize identically | SHA/read examples, denied-path and missing-commit results, manifest comparison (AC-14/16) |
| S07 | Jira read/search contracts: inspect actual MCP, fields, types, workflows, candidate markers and visibility | Search failure remains lookup_failed; selected marker is reliably searchable with known indexing/permission limitations; routes and closed Status/Resolution pairs documented; missing fields block publication | Capability matrix, sanitized search responses, proposed marker and routing specification; actual marker write/index tests deferred to sandbox authorization (AC-05/06/09/17) |
| S08 | Corporate LLM: authorized bounded Chat Completions JSON Mode probes with redacted fixtures | Model/base_url/auth/TLS verified; JSON parsing, schema and evidence checks remain independent; malformed/truncated output, 429, auth errors and outages handled within budget; no tools for writes or public fallback | Sanitized request/response summaries, usage/finish reasons, measured limits, errors and bounded retry observations (AC-11/15) |
| S09 | Fingerprints, grouping and manual investigation mapping against labeled samples | Versioned deterministic candidate keys; Stand Issues stand-scoped by default; identical text alone cannot merge causes; Unknown and ambiguous Tasks use stable symptom scope; manual verified mapping format proposed | Positive/negative grouping pairs, proposed key specification, migration considerations, engineer review (AC-02/05/07/18) |
| S10 | Configurable policy and contracts using decision tables | Other categories default report-only even with insufficient evidence; explicit category overrides work; analyzer technical failures cannot create issues; known independently verified occurrences remain eligible for comments; guards cannot be bypassed; invalid/conflicting rules rejected before external calls | Policy truth table, proposed schema and fixture outcomes, including malformed configuration (AC-03/09/11/13/17) |
| S11 | Confluence read capabilities and corporate template review | Body/version/parent/space contracts established; stable report lookup proposed; manual content preservation supported or separate analyzer-owned pages agreed | Sanitized template, capability matrix, managed-block and report-key proposal; update/conflict tests deferred to sandbox authorization |
| S12 | Journal/recovery and async behavior with mock services and injected failures | At most configured concurrent reads/analyses; external writes sequential; intent durable before call; cancellation/crash/timeout produces reconciliation rather than blind retries; overlapping occurrences not repeated; dry-run makes zero external write calls | Ordered mock-call traces, crash/restart cases, journal examples and concurrency measurements (AC-04/10/12/13/18) |
| S13 | Security and operations review | Injection content treated as data; secret sentinels absent from prompts/logs/reports; unsafe URLs/paths/XML blocked; publisher/state ownership and retention proposals documented; test outcomes unchanged | Sanitized security fixture results, data-flow review, deployment/state-transfer proposal (AC-13/15/16) |
| S14 | Representative 100–1000-test samples and historical evaluation design | Measure elapsed time, memory, token volume, truncation and requests without inventing SLOs; split historical labels by defect/campaign; propose thresholds for owner approval | Measurement environment/results, dataset provenance, holdout strategy and quality-metric definitions; no automatic publication threshold adopted |

## Separately authorized sandbox publication checks

After explicit authorization and identification of test projects/spaces, validate issue creation/comments, optional links/transitions, Confluence create/update/conflicts, marker indexing and visibility, timeout-after-write reconciliation, restart and overlapping campaign reruns. Require confirmed external IDs and sanitized journal/call traces for AC-02–06/10/12/17/18. Never infer absence from a failed search, blindly switch to REST after timeout, or clean up by deleting records without authorization. Sandbox success is not production acceptance.

## Required access, decisions and blockers

| Prerequisite | Needed for | Current status / safe fallback |
|---|---|---|
| Approved package/image registries, corporate CA, target architecture, scanner | S01–03 | Not supplied; public metadata only, installation pending |
| Sanitized real results/logs, launches, retry semantics and labeled failures | S04/09/14 | Not supplied; illustrative examples are not real source samples |
| RP endpoint/version, read credentials and MCP transport/tool inventory | S05 | Not supplied; local fixtures only |
| Git repository/commits and authorized CI artifacts | S06 | Not supplied; no source/test-stand execution |
| Jira read access, actual fields/workflows, routes and marker candidates | S07 | Not supplied; publication blocked until verified |
| Corporate LLM endpoint/model, CA/auth, data policy and request allowance | S08 | Not supplied; mocks only |
| Confluence read access and existing report template | S11 | Not supplied; no corporate template invented |
| Canonical publisher, persistent state, handover, permissions and retention | S12–13 | Operational decisions pending; isolated fixture directories only |
| Separate sandbox write permission and test destinations | Sandbox checks | Not granted; no external writes |

These are prerequisites to individual spike checks, not reasons to invent infrastructure or block fixture-based core development. Technical details that can be measured remain investigations; missing information affecting a contract must be presented as a specific question before adopting that contract. Proposed CLI precedence, retry/statistics policy, category vocabulary beyond the four named categories, evidence-support criteria, marker schema and report ownership need explicit review when concrete proposals are available. No new alternative category names or production defaults are adopted by this plan.

## Completion and handoff

Deliver a spike results matrix with each check passed, failed or blocked, sanitized evidence references, selected dependency/image candidates, contract proposals, measured limitations and remaining production blockers. Obtain owner decisions for interface/architecture changes. Keep corporate results separate from fixtures.

Stage 1 must generate the actual application uv.lock and pass locked installation of all extras/dev under CPython 3.14, tests, lint, formatting, typing, wheel build, container build and CLI smoke test as specified in dependencies.md. Package/mount configuration, prompts and templates; exclude credentials/state/artifacts from the build context and verify non-root writable storage. No successful installation, test or build is claimed in this planning document.

Stop at this plan's review gate. Approval to execute Phase 0 is required before probes; application implementation and sandbox writes require their respective subsequent authorization.
