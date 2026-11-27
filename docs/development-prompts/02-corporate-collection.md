# Stage 2 — Corporate read-only collection and real report adaptation

Execute this task only when the project owner explicitly asks to continue with it. Creating or reading this document does not authorize its execution. The initialization prompt `01-project-initialization.md` is historical context; do not repeat initialization or stop at its superseded planning gate.

## Objective and execution boundary

Continue `ai-test-analyzer` in the authorized corporate environment. Implement the Stage 2 collection slice using actual internal report examples, authorized read-only ReportPortal access and the matching Git revision:

```text
CLI -> validated configuration/context -> ReportPortal or JUnit source
    -> normalized results and verified evidence references
    -> local report and non-executable dry-run plan
```

Adapt the existing implementation rather than starting a second analyzer. Make concrete, tested changes after establishing the necessary source contracts. Do not stop at another general plan when the required information is available.

Stop and ask a specific question when a missing fact or conflicting requirement affects a contract, source authority, retry interpretation, data handling or architecture. Continue safely testable technical investigation without asking again about documented decisions. Do not treat a timeout, denied request or missing sample as permission to invent a corporate contract.

Stop after this collection slice. Do not start Stage 3 analysis, publication or deployment. Do not create a commit; propose an English commit message at the end.

## Restore context first

Locate the checkout in the corporate workspace; do not assume the previous workstation's absolute paths or Docker resources exist. Inspect `git status`, the recent history and both staged and unstaged diffs. Stage 1 changes may already be staged but uncommitted. Preserve the owner's changes and staging choices.

Read:

1. `AGENTS.md` and `README.md`.
2. `docs/implementation-plan.md`, `docs/stage1-results.md`, `docs/technical-spike-results.md` and the relevant check definitions in `docs/technical-spike-plan.md`.
3. `docs/requirements.md`, `docs/architecture.md`, `docs/adr.md`, `docs/data-model.md` and `docs/analysis-pipeline.md`.
4. `docs/integrations.md`, `docs/security.md`, `docs/testing-strategy.md`, `docs/dependencies.md`, `docs/decision-rules.md` and `docs/ci-cd.md`.
5. [The report-adaptation skill](../../skills/adapt-internal-test-reports/SKILL.md). Apply it when inspecting the supplied report/failure samples and changing their adapters. This repository skill can be read directly even if the corporate agent has not registered it for automatic discovery.

Inspect the actual implementation:

- Root `pyproject.toml`, `uv.lock`, `.python-version`, `Dockerfile` and `.dockerignore`.
- `src/ai_test_analyzer/domain/models.py` and `domain/normalize.py`.
- `application/analyze.py`, `ports/local.py`, `bootstrap.py` and `cli.py`.
- `adapters/files.py`, `config.py`, `junit.py`, `report.py` and `templates/report.html.j2`.
- `tests/test_local_slice.py`, `tests/fixtures/results.xml`, `config/local.yaml` and `examples/contracts/file-context.json`.

The other contracts/configuration in `examples/` describe future interfaces; they are not proof of implemented behavior. `examples/bootstrap/` is historical scaffolding, not a replacement for the root application project.

Use `spikes/phase0/README.md`, `inspect_artifacts.py`, `sample_summary.json` and the probe tests for structural observations only. Do not copy experimental parsing or node-ID reconstruction into production without validating it against the corporate examples.

## Starting facts and limits

The last documented Stage 1 run used Linux amd64, CPython 3.14.10 and uv/uv_build 0.13.10. It passed 25 synthetic tests, lint/format/typing, locked extras/dev installation, application wheel and container checks, plus three real local JUnit reports. Verify the current state instead of claiming those checks passed in the corporate environment.

Stage 1 currently:

- Reads a bounded, non-namespaced pytest-style JUnit dialect.
- Counts testcase records without interpreting retries.
- Stores explicit missing data, conflicts, metadata provenance and aware UTC timestamps.
- Uses content-bound local run/item keys, not defect fingerprints or publication markers.
- Describes evidence using artifact SHA256 and zero-based testcase index; it does not yet resolve evidence content.
- Preserves SHA metadata without application-level Git verification.
- Omits raw test names, errors, tracebacks, logs and arbitrary properties from saved outputs; node_id and attempt are null.
- Produces a local report and blocked investigation entries with analysis/duplicate lookup marked not_performed.
- Rejects existing output directories and exposes no external publication command.

Do not silently change these public contracts, identifier semantics or raw-content handling. Propose any required incompatible change and ask the owner before implementing it. Preserve the independently usable JUnit/file path.

## Establish the corporate inputs

Inspect available approved connections and non-secret configuration before asking for information already present. Do not dump environment variables, credential files, MCP responses or raw report bodies into the conversation.

Establish the following with the owner or existing approved configuration:

| Input | What must be known |
|---|---|
| Data handling | Authorized sources, local storage location, permitted excerpts, sanitization/export rules and approved tools |
| Real reports | Exact input files or launch references; at least one completed successful run and one failed run; setup/error, skipped and retry examples when available |
| ReportPortal | Approved endpoint/project, server/API version, actual MCP transport and available tools or approved REST capability, read-only credential mechanism and bounded launch scope |
| Correlation | How JUnit/HTML/log files belong to the same run/stand/launch; which source owns result counts and statuses |
| Metadata | Where stand, campaign, full Git SHA and software/firmware versions are recorded; what remains unavailable |
| Git | Approved repository location and availability of the exact commit; explicit files needed for source evidence |
| Toolchain | Approved package/image registries, corporate CA/proxy setup, target platform and available scanning tools |

A report may be a test-result input or a desired analyzer output/template. Determine its role before changing a parser or renderer. If the intended role is ambiguous, ask. Output-template work is outside this collection slice unless the owner explicitly includes it; record that follow-up without publishing or guessing a body format.

Do not request Jira/Confluence write credentials or LLM access for this stage. Do not request secrets in chat. Previous permission to use public registries on a workstation does not establish permission to send corporate data to public services or bypass corporate egress rules. Use approved mirrors/CAs and keep TLS verification enabled.

## Implementation work

### 1. Characterize real reports and test failures

Apply the report-adaptation skill to compare the actual sample structure with the current adapter contract. Record a sanitized mapping of source fields, outcomes, phases, identifiers, timestamps, metadata, declared counts and evidence locations. Distinguish observed test outcomes from engineer-confirmed root causes.

Do not infer stand/campaign/SHA from directory dates, force ambiguous ID joins, turn ERROR-level log lines into failed tests or merge unrelated failures because their messages match. Unknown retry semantics remain explicit record/attempt counts until resolved. Record format/version support and fail clearly for unsupported formats.

Create the smallest sanitized or synthetic regression fixtures that preserve the relevant structure and expected outcomes. Keep raw internal samples outside version control and public artifacts. Test both a successful and a failing case so that adaptation cannot simply mark every sample failed or successful.

### 2. Verify ReportPortal reads and implement the source adapter

Inspect installed MCP capabilities first. Establish actual tool schemas, identifier meanings, pagination and status/metadata availability through bounded reads of the approved launches. Launch ID, UUID and sequence number are not interchangeable.

Implement only the operations needed by this slice behind typed ports. Prefer MCP where it supports the operation; use HTTPX2 REST for verified missing capabilities. Do not invent tool names or implement unused abstraction layers. Preserve SDK/client details in adapters and validate configuration before calls.

Bound timeouts, retries, response/attachment size, pages and concurrent reads. Read permission/auth failures must not be retried indefinitely. Detect incomplete pagination, running launches, unavailable data and malformed responses explicitly. Do not report a failed request as an empty successful launch.

Do not trigger tests, ReportPortal auto-analysis, result classification changes or other mutations. Verify the semantics of operations before calling them; an HTTP method alone does not establish that an MCP tool is read-only.

For ReportPortal plus file enrichment, establish the authoritative status source from the observed contracts. Count a testcase/attempt once and retain provenance, conflicts and unavailable evidence. Implement the supported single-run slice first; full campaign scheduling/completeness and generalized HTML/DUT/CI adapters remain later-stage work.

### 3. Verify Git and resolve evidence

Verify the full supplied SHA as a commit in the approved repository. Distinguish missing SHA, unavailable repository, missing commit and technical failure. Do not substitute HEAD or the current working tree. Read only necessary, explicitly selected files from the verified commit using bounded operations; do not checkout, alter the test repository or execute its code. If remote retrieval is necessary, establish its authorization and an isolated destination first.

Resolve JUnit evidence only after checking the digest of the bytes actually read and the testcase index. For ReportPortal evidence, establish the real source identity, locator and retrieval guarantees. Reject mismatched/stale locators rather than citing a different record. Preserve unavailable/truncated evidence explicitly and prevent unsafe URL/path/redirect/archive traversal.

Before exposing raw error/log/source excerpts in reports or prompts, establish the permitted handling policy and contract. Stage 1 omission of raw text is not a general redaction implementation. Verify approved redaction with synthetic secret sentinels; do not upload real samples to a public LLM, web search or external test service.

### 4. Integrate the CLI and local report

Connect the verified source adapters through the application and composition root. Document and test implemented source selection and configuration/context precedence. Keep network I/O asynchronous and domain normalization synchronous. Use YAML for settings/policy and Jinja2 for presentation.

Preserve test outcomes independently of collection failures. A completed local dry-run is not completed cause analysis. Keep the plan honest: no fabricated LLM findings, Jira duplicate searches, created issues or publication outcomes. All external writes remain disabled.

## Scope exclusions and blocked work

Do not implement Stage 3 grouping, fingerprints, Jira search, LLM analysis or business action rules; Stage 4 publication/journal recovery; scheduler/poller; equipment operations; or generalized report support unrelated to the supplied samples.

If corporate access is unavailable, record exactly which checks are blocked. Real report adaptation and the independently testable file/Git/evidence work may proceed where their inputs are available. Do not mark all of Stage 2 complete when ReportPortal is only mocked. When no authorized independent work remains, stop with the concrete missing prerequisite rather than inventing success or repeating inaccessible protocol research.

## Validation and evidence

Follow `docs/dependencies.md`: verify current stable compatible candidates in an approved registry before implementation; retain the locked baseline unless a justified, documented update is needed. Do not use prereleases, change Python minor branch or update the lock on every run. A denied registry or unavailable approved scanner is a reported blocker, not a reason to disable TLS or fabricate a result.

Run the relevant checks on the required CPython 3.14 toolchain:

```sh
uv sync --locked --all-extras --group dev
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv build
docker build -t ai-test-analyzer:0.1.0 .
docker run --rm --network none ai-test-analyzer:0.1.0 --help
```

Run a fixture dry-run in the built image, then separate approved corporate read-only smoke tests. The current slim image does not include Git; address and verify that runtime dependency if the implemented adapter needs it. Do not assume the previous host's caches or Docker daemon permissions are available.

Include meaningful tests for pagination/partial reads, denied access, timeouts, malformed responses, source conflicts, deterministic identity, no double counting, absent/mismatched SHA and evidence, bounded parsing and secret-safe diagnostics. Mock tests must verify zero external write calls; actual network tests must use the approved read-only scope. Retain the original Stage 1 fixture behavior and rerun available real samples without changing their sources.

Distinguish public metadata, locked installation, synthetic fixtures, mock-service contracts, real local artifacts and actual corporate service checks. Record command/operation, environment, sanitized sample identifier, actual result and limitation. Never save credentials, signed URLs, raw internal payloads or personal absolute paths in Git or unrestricted logs.

## Deliverables and stopping point

- Working source/evidence/Git changes within the verified collection slice, with appropriate tests.
- Updated README commands and implemented contracts; explicitly identify any owner-approved changes.
- A Stage 2 results document under `docs/` recording actual source capabilities, format support, evidence mapping, checks, limitations and remaining prerequisites without confidential payloads.
- Updated implementation-plan status that distinguishes completed local work from blocked corporate validation.
- A final explanation of what changed, what was actually tested, what remains blocked/pending and whether Stage 2 exit criteria were met.
- A proposed English commit message; do not stage, commit, push, publish or deploy as part of this task.

Stop before the next implementation stage. Do not declare fingerprints, routing, corporate publication safety or production readiness verified by this collection work.
