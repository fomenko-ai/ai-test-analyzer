# AI Test Analyzer

Design documentation version: **0.1.0 (MVP)**. 

**Status:** Stage 1 implements a local JUnit dry-run: configuration/context validation, normalized results, evidence references, an HTML report and a non-executable plan. Corporate integrations and cause analysis are not implemented. See [Stage 1 results](docs/stage1-results.md) and [Phase 0 results](docs/technical-spike-results.md).

`ai-test-analyzer` is a CI/CD-independent, AI-powered test results analyzer. It collects results and logs, groups failures, identifies known defects, analyzes unknown failures using a corporate LLM, applies business rules, creates Jira issues and comments, and publishes Confluence reports. It is not limited to nightly runs or regression testing.

## Documentation

| Document | Contents |
|---|---|
| [AGENTS.md](AGENTS.md) | Instructions for any AI coding agent |
| [requirements.md](docs/requirements.md) | Agreed requirements and MVP scope |
| [dependencies.md](docs/dependencies.md) | Python 3.14, dependency and Docker candidates, update policy |
| [architecture.md](docs/architecture.md) | Components, dependencies and adapters |
| [data-model.md](docs/data-model.md) | Data models and contracts |
| [analysis-pipeline.md](docs/analysis-pipeline.md) | Analysis workflow, reruns and campaigns |
| [decision-rules.md](docs/decision-rules.md) | Classification, routing and deduplication |
| [integrations.md](docs/integrations.md) | ReportPortal, Jira, Confluence, LLM, Git and files |
| [ci-cd.md](docs/ci-cd.md) | CLI, Jenkins, GitLab, cron and polling |
| [security.md](docs/security.md) | Security and operational restrictions |
| [testing-strategy.md](docs/testing-strategy.md) | Tests, historical evaluation and acceptance criteria |
| [implementation-plan.md](docs/implementation-plan.md) | Implementation stages and technical checks |
| [adr.md](docs/adr.md) | Architecture decision records |
| [examples/](examples/) | Configuration, context, analysis and bootstrap examples |
| [SKILL.md](skills/test-failure-investigation/SKILL.md) | Instructions for an external investigation agent |
| [Corporate collection task](docs/development-prompts/02-corporate-collection.md) | Next Stage 2 task for the authorized corporate environment; execute only when requested |
| [Report adaptation skill](skills/adapt-internal-test-reports/SKILL.md) | Adapt analyzer code to real internal test reports and failure examples |

## Local dry-run

Requires Linux, uv 0.13.10 and CPython 3.14.10. The commands below were exercised inside the pinned official uv container; the host toolchain was not upgraded. Installation may access public PyPI; the analyzer itself uses local files only.

```sh
uv sync --locked --all-extras --group dev
uv run --locked ai-test-analyzer --help
uv run --locked ai-test-analyzer analyze \
  --source junit --input tests/fixtures/results.xml \
  --config config/local.yaml --context examples/contracts/file-context.json \
  --output data/fixture-1
```

The fixture is synthetic. Choose a **new** output directory on every run. Outputs are `normalized.json`, `plan.json` and `report.html`, with private filesystem permissions. Repeating the same inputs/context preserves identifiers; existing output directories are rejected. The original XML is never copied or modified.

Configuration and context are optional. Settings default to dry-run and a 10 MiB XML limit. Unknown/duplicate keys, invalid values and publication enablement are rejected. Explicit context supplements JUnit metadata; differing values produce a conflict and a null effective value. Missing stand, campaign, SHA or versions remain missing. See [the implemented contract and limitations](docs/stage1-results.md).

The plan records a required investigation for each failed/error testcase, blocked pending analysis and duplicate lookup. It contains no executable Jira payload. Testcase records are counted without interpreting retries. Raw names/messages/logs and arbitrary properties are omitted; evidence uses the source SHA256 and zero-based testcase index. Keep the original authorized XML available to inspect evidence.

Exit codes: 0 successful local dry-run, 2 report produced with data conflicts, 1 input/configuration/output failure; argparse usage errors return 2. Test failures are statistics and do not themselves fail the analyzer. A complete local dry-run does not mean cause analysis has run or corporate publication is ready.

```sh
docker build -t ai-test-analyzer:0.1.0 .
docker run --rm --network none ai-test-analyzer:0.1.0 --help
docker run --rm --network none --read-only \
  --tmpfs /tmp:rw,nosuid,nodev,size=32m \
  -v "$PWD/tests/fixtures:/fixtures:ro" \
  ai-test-analyzer:0.1.0 analyze --input /fixtures/results.xml --output /tmp/fixture
```

The last command is a disposable smoke test; its report disappears with the container. For retained reports, mount an authorized writable destination and supply a new output path. The image runs as UID/GID 10001 and has no corporate credentials or Docker socket. `examples/config/default.yaml` and the ReportPortal RunContext example remain future specifications, not supported local configuration.

## Development checks

```sh
uv sync --locked --all-extras --group dev
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv build
```

Ruff checks E/F/I excluding E501; experimental spike files and bootstrap templates have separate checks. Dependencies are locked and must not be updated on each CI run. Stage 2 corporate collection requires the missing access/contracts; see the implementation plan. Publication remains unavailable.

## MVP limitations

One test project, multiple stands, 100–1000 tests per considered run/campaign (actual load per stand must be measured). Only one publishing instance may operate at a time: this is an operational restriction, not a distributed locking guarantee. A separate database is not mandatory. The AI Investigation Agent is an external tool, not an application dependency. Automatic test code changes, equipment restarts and automatic closure of investigations are out of scope.

## Development environment

Linux, CPython 3.14.10 and uv 0.13.10. The root `pyproject.toml`, `uv.lock`, `.python-version` and digest-pinned Dockerfile define the implemented application. Current public metadata and actual verification are recorded in [docs/stage1-results.md](docs/stage1-results.md). Bootstrap examples are historical templates; the root project is authoritative. No production baseline or corporate integration acceptance is claimed.
