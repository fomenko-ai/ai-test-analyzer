# Implementation Plan

This is not a calendar schedule. Progress depends on exit criteria. Start with a vertical slice, then extend adapters. Development commands describe future implementation; corporate endpoints were not available during design.

| Stage | Deliverable | Exit criteria |
|---|---|---|
| 0. Technical spike | Source samples, MCP/REST contracts, LLM probe, agreed fingerprint format, Confluence template | Read-only checks and documented limitations; write capabilities separately tested in test Jira/Confluence |
| 1. Skeleton | pyproject/uv.lock, CPython 3.14, CLI, Pydantic, domain, ports, config, fixtures | CLI dry-run on one fixture with no external writes |
| 2. Collection | ReportPortal read + JUnit, Normalizer, Git SHA, evidence refs | Reproducible normalized data, no double counting |
| 3. Analysis | Grouping, fingerprint, Jira read, LLM, Validator, Rule Engine | Bug/Task/Comment plans; AC-01–07, AC-09/11/13/14 |
| 4. Publication | JSON journal, Jira & Confluence adapters, templates, resume | Sandbox tests AC-04/06/10/12/17/18; dry-run unchanged |
| 5. Sources & campaigns | HTML/DUT/CI artifacts, expected stands, group analysis | AC-08, valid references and source conflicts handled |
| 6. Operations | Jenkins/GitLab manifests, cron/poller, Compose, single publisher | AC-16, independent status, restart recovery and security restrictions |
| 7. Evaluation & rollout | Historical dry-run, engineer evaluation, thresholds, enablement | Agreed quality criteria, test writes and rollback plan |

## Technical spike checklist

- Obtain sanitized JUnit, HTML, DUT logs, successful and failed ReportPortal launches with campaign_id, and historical defects with verified causes. Determine actual formats and test ID mapping.
- Obtain Jira/Confluence MCP tools and transport/auth details. Verify reads, searches, write formats, fields, transitions, links and post-write lookup. API access does not imply idempotency.
- Validate installed ReportPortal MCP, attributes, pagination, logs/attachments, status and history access. Use REST fallback for missing capabilities.
- Validate corporate base_url/model, JSON Mode, optional Tool Calling, limits, data security, tokens, errors and retries.
- Obtain the existing Confluence Report template; agree Bug/Investigation/Comment templates and managed page format.
- Determine Jira routing, closed Status/Resolution policies, fingerprint field, external action marker, visibility/indexing and ambiguous-result policy.
- Select a canonical publisher, persistent state path, exclusive schedule and plan transfer rules between environments. Agree artifact retention and access permissions.
- Verify full Git SHA for every source, engineer evidence access and metadata/manifest from Jenkins/GitLab.

## Production blockers (do not block core development)

Unknown MCP implementations, actual required Jira fields/workflows, existing Confluence template, verified JSON Mode behavior, source formats, fingerprint/search marker and secret policy. Use mocks/fixtures and dry-run until resolved. Do not guess production configuration. Agree quantitative quality thresholds after measurement.

## Dependency gate before implementation

At stage 0, check [dependencies.md](dependencies.md): current stable releases, wheels for target Linux architecture, joint resolution of runtime/extras/dev, imports, mock MCP/HTTP/LLM, JUnit/HTML tests, image availability and digests in the corporate registry. At stage 1, generate a real `uv.lock`, build the wheel and Docker image from the skeleton. Freeze the baseline only after the gate passes. Public catalog checks do not replace this gate.
