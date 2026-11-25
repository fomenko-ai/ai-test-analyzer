# Requirements

## Agreed scope

| ID | Requirement |
|---|---|
| FR-01 | Support manual execution, post-test execution from Jenkins/GitLab, and discovery of new runs using cron or a polling service. |
| FR-02 | One ReportPortal Launch per stand. Analyze a single Launch or a group identified by campaign_id or an explicit list of Launch IDs. |
| FR-03 | Expected stands are defined in configuration or supplied by CI/CD; incomplete campaign behavior is configurable. |
| FR-04 | Independent adapters for ReportPortal, JUnit XML, HTML, DUT logs, firmware/software version metadata; access to ReportPortal, Jenkins/GitLab and filesystem artifacts. |
| FR-05 | Access source code through local Git, CI checkout or clone, with full Git SHA verification. |
| FR-06 | Normalize data, group failures and use history; cross-stand correlation is configurable by category. |
| FR-07 | Use a corporate OpenAI-compatible API, Chat Completions and JSON Mode. Tool Calling is available but an agent loop is not required for MVP. |
| FR-08 | Automatically register new Product Bug, Automation Bug, Stand Issue and Unknown (Investigation Task); route by category and stand. Other categories are report-only by default until additional rules are agreed. |
| FR-09 | Comment on known issues; apply Status/Resolution rules for closed issues. Create an Investigation Task with candidate links for ambiguous matches. |
| FR-10 | Preserve manual investigation results in Jira; verified fingerprints are available to future runs. Fingerprint storage is configurable. |
| FR-11 | Engineers manually investigate a Task by Jira key using any AI Investigation Agent; engineers decide how to resolve the Task. |
| FR-12 | Configurable Confluence reports per run, stand, campaign or hierarchy, with configurable publication conditions and language. Adapt the existing corporate Confluence template when available; develop missing Jira issue and comment templates. |
| FR-13 | JSON + Jira by default; replaceable state adapters. ReportPortal holds original test history. A separate database is not mandatory. |
| FR-14 | Prefer MCP; use REST for unsupported operations. Actual Jira/Confluence MCP implementations are unknown. |
| FR-15 | Retry LLM outages, then produce a partial report with technical statuses and no unsupported Bugs. |
| FR-16 | Evaluate historical results in dry-run before automatic publication. |

## Non-functional requirements

- NFR-01: Linux, CPython 3.14, CLI via uv, Docker Compose plugin. See [dependencies.md](dependencies.md). Environments: local computer, server, CI runner.
- NFR-02: One test project, multiple stands, 100–1000 tests. Measure performance and model limits during the spike.
- NFR-03: Independent analyzer status; never overwrite test results.
- NFR-04: Support reruns, recovery after partial publication and traceability of rules, prompts, model versions and sources.
- NFR-05: One active publishing instance in MVP, enforced operationally. Parallel dry-runs are permitted with isolated directories. Local locks are not distributed locks.
- NFR-06: Least privilege, corporate LLM only, secret redaction, evidence-backed findings and no external writes in dry-run.

## Outside MVP scope

Mandatory agent runtime, automatic test code changes, automated equipment operations, separate database, UI, multi-agent orchestration and distributed publication. Interfaces do not require all alternative stores to be implemented immediately.

## Proposed technical defaults (not corporate requirements)

Pydantic, Jinja2, YAML, Markdown, OpenAI SDK, one publisher and dry-run by default. Do not guess unknown routing or closed-issue policies: defer actions and report why. Jira fields, project/type IDs, SLAs, retention, timeouts and waiting windows will be configured after infrastructure validation. “Nightly” describes an execution scenario, not the product name.
