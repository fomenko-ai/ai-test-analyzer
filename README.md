# AI Test Analyzer

Design documentation version: **0.1.0 (MVP)**. 

**Status:** Local Phase 0 closeout is documented in [technical-spike-results.md](docs/technical-spike-results.md); corporate checks remain blocked. Stage 1 has not started. Requirements agreed; architecture proposed. This is a design package, not a working application. Commands, configuration schemas and contracts describe the future implementation. Corporate integrations have not been tested.

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

## Getting started

For AI-assisted development, start with [the project initialization prompt](docs/development-prompts/01-project-initialization.md). Ask your coding agent to read and execute that file. Review the resulting Technical Spike plan before approving implementation.

1. Read `AGENTS.md`, the requirements and the architecture.
2. Perform the technical spike described in `docs/implementation-plan.md` without writing to production systems.
3. Implement an end-to-end dry-run using fixtures before enabling publication.
4. Evaluate historical failures and agree on automation thresholds.
5. Enable automatic publication only after meeting the acceptance criteria.

## MVP limitations

One test project, multiple stands, 100–1000 tests per considered run/campaign (actual load per stand must be measured). Only one publishing instance may operate at a time: this is an operational restriction, not a distributed locking guarantee. A separate database is not mandatory. The AI Investigation Agent is an external tool, not an application dependency. Automatic test code changes, equipment restarts and automatic closure of investigations are out of scope.

## Development environment

Linux, CPython 3.14 and uv. The inherited candidate baseline is dated 2026-11-25; see [docs/dependencies.md](docs/dependencies.md). `examples/bootstrap/` contains a proposed `pyproject.toml`, `.python-version` and Dockerfile for the future skeleton. These are specifications, not a verified build. Generate a real `uv.lock` during implementation, after checking the latest stable compatible versions. Do not deploy unverified versions to production.
