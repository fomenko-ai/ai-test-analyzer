# Phase 0 — Technical Spike Results

Date: 2026-11-27. Status: local Phase 0 closeout; corporate checks remain blocked. Public sources were approved by the owner. No application implementation, corporate integration tests or external writes have been performed. Stage 1 had not started at this closeout, following the owner's stop instruction. Subsequent authorized implementation is recorded separately in [stage1-results.md](stage1-results.md).

## Local environment inventory

Commands executed locally:

| Command | Observed result | Limitation |
|---|---|---|
| uv --version | uv 0.11.23 (x86_64-unknown-linux-gnu) | Installed tool differs from inherited 0.13.10 candidate; no update performed |
| python3 --version | Python 3.14.4 | Required minor branch present; inherited patch candidate 3.14.10 not installed or verified by this command |
| docker --version | Docker 29.8.0, build 88096ef | Client availability only; daemon access and image builds untested |
| docker compose version | v5.5.1 | Differs from candidate v5.8.0; no upgrade performed |
| docker buildx version | v0.37.1 | Manifest access untested |
| uv python list --only-installed | Failed: read-only default uv cache path | No interpreter inventory obtained; subsequent probes need an explicitly writable cache or approved filesystem access |

No environment-variable values, credentials or corporate endpoint configuration were collected.

## Check status

| Checks | Status | Next prerequisite |
|---|---|---|
| S01 | Local probe passed: metadata, joint lock/sync, imports and synthetic backend build | Actual application build and target production platform remain unverified |
| S02 | Local: 16 tests passed at closeout; corporate behavior unverified | Real TLS/proxy behavior, size limits and corporate transports remain unverified |
| S03 | Partial: image manifests and uv runtime verified | Production platform confirmation and vulnerability scans remain pending |
| S04 | Partial: real JUnit/HTML/log structures inspected | ReportPortal/DUT/CI samples, retry/campaign semantics still pending |
| S05–S07, S09–S11 | Blocked for real contract validation | Relevant read-only corporate access and verified historical causes required; no production formats or markers invented |
| S08 | SDK mock behavior passed; corporate checks blocked | Corporate model/base_url, approved data policy and read access required |
| S12–S13 | Partial: bounded concurrency and parser probes passed | No application journal/publisher exists; recovery, redaction and operational decisions remain pending |
| S14 | Blocked for representative measurements | Real sanitized samples and labeled history |
| Sandbox publication | Not authorized | Separate explicit authorization and test destinations |

## Public-source and container verification

The owner authorized public sources and suggested using the uv image. The official image ghcr.io/astral-sh/uv:python3.14-trixie-slim was inspected and executed pinned to index digest sha256:b093dbbd7963c765325ecdf866d42915f5327e135569f9dae9c77cac63559bf2. The manifest supports linux/amd64 and linux/arm64; execution was tested only on local linux/amd64. Inside the container: CPython 3.14.10 (GCC 14.2.0), uv 0.13.10. This is a dependency-probe container, not the analyzer application image.

The Python candidate python:3.14.10-slim-trixie manifest was also inspected: index digest sha256:22eafb370920ad8b429e0aec3fff433e0669968519f5d60469d83729c138b28b, amd64 manifest sha256:080b4f1282edb604b21e61dfca35d1d215ed6cd1c17de27ccfc34e6fadc4ee49. That separate image was not executed. Vulnerability scans remain pending.

Public PyPI metadata was retrieved using spikes/phase0/collect_metadata.py and saved in spikes/phase0/metadata.json. OpenAI 3.60.0 was published on the execution date and supersedes the inherited 3.59.0 candidate. Other direct package candidates match the planning snapshot; uv and uv_build report 0.13.10. The probe selects OpenAI 3.60.0. Metadata is not a compatibility guarantee.

Executed in spikes/phase0 using the pinned uv image: uv lock --default-index https://pypi.org/simple; uv sync --locked --all-extras --group dev; uv run --locked python with imports of openai, mcp, pydantic, httpx, yaml, jinja2, bs4 and defusedxml. All exited successfully. The initial real probe uv.lock resolved 60 entries, with 56 packages installed on this Linux platform. After the approved HTTPX2 change and addition of uv_build to the probe dev group, the regenerated lock resolves 61 entries. Locked sync and all 13 tests passed again (0.98s). This lock belongs to the isolated probe, not the future application.

uv_build 0.13.10 was installed and exercised through uv build --directory build_probe with a disposable output directory. Both phase0_build_probe-0.0.0.tar.gz and phase0_build_probe-0.0.0-py3-none-any.whl were successfully built. The wheel was installed with --no-deps into the disposable probe environment and imported successfully (BUILD_PROBE_IMPORT_OK). Artifacts remain outside the repository, not in Git. This verifies a synthetic package/backend combination, not analyzer packaging. The final basic lint and format checks passed.

Additional S03 metadata check: docker buildx imagetools inspect reportportal/mcp-server:2.0.0 succeeded. Observed index digest sha256:ead2e004765592f94207d28cf1f814763f82c82ce228ead8f7ebe1b8cdbbb43b with linux/amd64 and linux/arm64 manifests. No server container was run, and compatibility with the corporate ReportPortal version remains unverified. The inherited 1.4.1 candidate is not silently upgraded in production configuration.

Observed dependency detail: OpenAI 3.60.0 and MCP 2.3.0 both depend on httpx2 2.16.2; the proposed explicit REST dependency httpx 0.28.1 installs alongside it. Injected-client compatibility requires a separate behavior probe before deciding whether clients can be shared. No application interface change is adopted here.

This observation describes the initial comparison baseline. The later HTTPX2 decision below supersedes the proposed direct HTTPX runtime dependency; synthetic client compatibility passed for both libraries, without establishing that SDKs can safely share one client lifecycle.

## Synthetic behavior results

The initial run passed eight tests and failed the MCP probe because the probe used v1-style Python attributes. Inspection of installed SDK v2 showed server_info and is_error; correcting the probe produced nine passing tests. This is a probe correction, not evidence of a broken SDK. Explicit pytest-asyncio fixture-loop scope was added to avoid its deprecation warning.

At the owner's request, repeated the SDK probes with both httpx 0.28.1 and httpx2 2.16.2 and added identical REST streaming/status/timeout-configuration checks. Final run in the pinned uv container with network disabled: 13 passed in 1.02s. Basic Ruff E/F/I checks (excluding E501) and formatting passed. An earlier broader Ruff invocation reported import ordering and nested-context style suggestions; imports were fixed, and the final lint scope is explicitly limited rather than claimed as a project-wide lint pass.

Passed scenarios: strict Pydantic structure versus separately checked evidence IDs; malicious XML entity rejection; HTML treated as data; unsafe YAML constructor rejection; missing template-variable rejection; SDK JSON Mode request generation and rejection of malformed response content; one SDK call on synthetic connection failure with automatic SDK retries disabled; REST query/auth headers, streamed error response and configured timeout propagation for both HTTP clients; bounded asyncio concurrency; actual stdio MCP initialize/list_tools/call_tool against a synthetic read-only subprocess server. No network TLS handshake, real request deadline, corporate CA/proxy, exhaustive parser bounds, prompt-injection defense, application publication policy or recovery guarantee is established by these tests.

## HTTP client decision (owner approved)

The owner approved HTTPX2 and requested a current-version check. Public PyPI was queried again: 2.16.2 remains current, requires Python >=3.11, published 2026-11-16, with non-yanked wheel/sdist. Metadata is saved in spikes/phase0/metadata.json. HTTPX2 is now the sole direct runtime HTTP client in the bootstrap and probe configurations. Legacy HTTPX remains only in the comparison probe dev group. OpenAI was also synchronized to the tested 3.60.0 in the bootstrap. See ADR-020. Application code and its lockfile do not yet exist.

Primary sources: [HTTPX2 project](https://pypi.org/project/httpx2/) and [official documentation](https://pydantic.dev/docs/httpx2/get-started/). HTTPX2 is maintained by Pydantic and uses httpcore2/truststore. Its default trust behavior differs from HTTPX's certifi-based default. Before corporate deployment, explicitly configure the agreed SSLContext and test corporate CAs, environment/proxy handling, streaming bounds, timeout/cancellation and each SDK transport. Do not enable optional HTTP/2/WebSocket extras without a concrete integration requirement. No throughput or security superiority was measured.

Container and package operations required host network/Docker permission outside the sandbox. The original default-cache failure was avoided using a writable /tmp cache. A subsequent attempt to copy the first container's cache failed because the --rm container had already exited; this does not invalidate the successful installation. The behavior-test container uses persistent cache/environment paths under /tmp instead.

## Initial prerequisite (resolved)

The owner confirmed public package/image sources and subsequently supplied local report samples (see below). Corporate endpoints, verified historical root-cause labels and production architecture/retention decisions remain unavailable. Credentials must be configured through an approved local secret mechanism, not committed or included in chat.

## Real local artifact inspection

The owner supplied a local artifact directory and requested the freshest examples. inspect_artifacts.py accepts the location as --artifacts-dir; no personal absolute paths are stored. Inputs were mounted read-only into a network-disabled uv container. Original reports/logs were not copied into this repository. Only structural counts, property names and content digests were persisted in [sample_summary.json](../spikes/phase0/sample_summary.json). No test source was read or executed; no test stand was operated. This is a real artifact-format check, not a corporate integration test.

Inventoried 186 JUnit reports; 12 contain a failure or error. Selection used file modification time, with report timestamps checked separately; modification time alone does not establish chronology. Selected the newest report without failures, newest with a failure, and newest with an error. The paired HTML and log came from the same run directory; the mutable latest.log alias was not used as independent evidence.

| Sample | Run directory | JUnit outcomes | HTML comparison |
|---|---|---|---|
| Latest without failures | 2026-11-19_09-28-34_279603 | 230 passed, 9 skipped; 239 total | Same outcomes; all 239 candidate IDs mapped bijectively |
| Latest failure | 2026-10-23_14-27-34_238287 | 51 passed, 1 failure; 52 total | Same outcomes; all 52 candidate IDs mapped bijectively |
| Latest error | 2026-09-14_07-43-52_277984 | 1 error | Same aggregate outcome; candidate ID reconstruction did not match |

For the selected reports, declared JUnit totals match actual testcase outcomes; duplicate testcase IDs were not observed. Timestamps contain explicit offsets. run_id matches directory membership and HTML environment metadata. git_revision has the full 40-hex shape and matches HTML metadata; commit-object presence was checked separately with Git (see closeout below); correspondence of test source remains unverified. The recent samples contain neither stand nor campaign properties; the older error sample has a stand property. Missing metadata must come from the configured context/manifest rather than be inferred from dates or paths.

Observed HTML format: data-container with a data-jsonblob attribute containing environment and per-test records (testId, result, duration, extras, resultsTableRow and log). Parsed embedded JSON as data without running scripts or opening report URLs. Reconstructing pytest node IDs from JUnit classname/name requires distinguishing module and class boundaries: the simplest dot-to-slash conversion matched only 213/239 recent cases. Trying candidate module/class splits and requiring a unique one-to-one HTML match yielded 239/239. This is a bounded experiment for the observed format, not a universal mapping algorithm or approved adapter contract. The older error sample has no exact candidate-ID match. The phase-aware experiment below records a separate setup candidate without treating it as an exact-ID join.

The newest successful run's log contains one ERROR-level mention even though JUnit/HTML contain no failed tests. Log severity is enrichment, not an independent test outcome or defect classification. A JUnit error in the historical sample describes a test execution/setup outcome; it is not an analyzer technical_error merely because both use the word error. No root-cause category was assigned from these files alone.

Probe limits: XML 10 MiB, HTML 4 MiB, log 1 MiB per file; resolved paths must remain under the supplied root; XML uses defusedxml. These limits are experiment safeguards, not adopted product budgets. No retry policy, campaign completeness, cross-source authority for ReportPortal, failure cause, secret-redaction coverage or production performance threshold is established. Original personal paths and hostnames are omitted from committed summaries.


## Local closeout and Stage 1 boundary (2026-11-27)

The owner requested completion of the available local spike and a stop before Stage 1. This supersedes the attached handoff's instruction to immediately implement the skeleton. Local readiness does not mean every original S01–S14 acceptance criterion passed: corporate contracts and production decisions remain blocked or deferred as listed above. These do not prevent a later file/fixture vertical slice.

No surviving Phase 0 container was found. The named probe volume remained available; unrelated containers were left untouched. The interrupted run had no recoverable confirmed test result, so the current source was checked again. The first offline locked sync failed because required wheels were absent from the cache; this was an environment recovery failure, not a test failure. Dependency recovery uses the existing lockfile and public PyPI; it does not upgrade the baseline. Release currency must be rechecked before Stage 1 implementation per dependencies.md; the recorded release metadata remains the 2026-11-26 observation.

The artifact inspector now optionally accepts --git-repo and uses only git cat-file -e <full-sha>^{commit}, with a bounded subprocess timeout. It does not read test source or change the neighboring repository. Phase candidates remain separate from exact-ID matches: only an independent setup/teardown hint in the JUnit error message allows the corresponding HTML suffix candidate, and duplicate candidates remain ambiguous. This does not establish a general identity, retry or root-cause contract.

Deferred to Stage 1: root pyproject.toml, application uv.lock, CLI, domain/application/adapters, actual analyzer wheel/container, typing and application acceptance checks. No application success is claimed from synthetic backend builds. Corporate ReportPortal, Jira, Confluence, LLM, CI/DUT transport, TLS/proxy/CA, marker/search behavior, publication recovery and labeled historical evaluation remain unverified. No production fingerprint/marker format or template was invented. Sandbox publication remains unauthorized; scans and target production architecture confirmation remain pending.


Confirmed closeout verification:

- Pinned official uv image on local Linux amd64: CPython 3.14.10, uv 0.13.10. `uv sync --locked --all-extras --group dev --default-index https://pypi.org/simple` succeeded; 61 lock entries, 57 installed packages. Subsequent `uv sync --locked --offline --all-extras --group dev` succeeded. No lockfile update was performed.
- With container networking disabled: `uv run --locked --offline pytest -q -p no:cacheprovider` passed all 16 tests in 1.79s, including three artifact phase/ambiguity/size/symlink checks. `uv run --locked --offline ruff check --select E,F,I --ignore E501 .` passed; `uv run --locked --offline ruff format --check .` passed (seven Python files). Import ordering and formatting in the two unfinished artifact-probe files were corrected. These are isolated spike checks, not application-wide typing/security acceptance.
- Synthetic backend build was repeated offline with `uv build --offline --directory build_probe --out-dir /tmp/dist`; sdist and wheel were built successfully. `uv pip install --python /probe-state/venv/bin/python --no-index --no-deps /tmp/dist/phase0_build_probe-0.0.0-py3-none-any.whl` and the direct import succeeded (`BUILD_PROBE_IMPORT_OK`). This remains a synthetic package, not an analyzer build.
- Real-artifact inspection was repeated with read-only mounts and networking disabled: 186 JUnit files, 12 runs with a failure/error, the same three selected runs and unchanged source content digests/counts. The older error has one phase-aware setup candidate; exact-ID bijection remains false. No sources were combined into additional test counts.
- The derived summary records commit-object verification for all three full SHAs. The minimal uv image has no Git executable, so the optional in-container Git check failed explicitly with FileNotFoundError. Artifact inspection was rerun without that option; host Git then successfully executed `git cat-file -e <sha>^{commit}` for each sample. Each XML digest was checked against the derived summary before extracting its full SHA for this check. Only the structural summary was saved. No test source was read.

The available local Phase 0 work is complete with the documented scope exclusions. The project is ready for a separately started Stage 1 file/fixture slice; implementation is intentionally stopped at this boundary. Corporate verification and publication remain blocked, not passed.
