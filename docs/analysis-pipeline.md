# Analysis Pipeline

1. Validate configuration, source, mode and required port capabilities. Load the checkpoint. Do not write externally in dry-run.
2. Resolve a single Launch, campaign_id or list of Launch IDs; verify expected stands and terminal state of each run. Do not treat missing stands as successful.
3. Collect statistics, results, metadata and log references. When combining adapters, choose an authoritative status source and enrich without double counting. Mark discrepancies as data conflicts.
4. Normalize statuses, errors and timestamps; redact secrets and assign evidence IDs. Support only known HTML formats and never execute scripts.
5. Group symptoms within each stand first, then investigate cross-stand causes. Preserve every failure's membership, including cascading tests.
6. Generate fingerprints and find candidates in Jira/ReportPortal/JSON. Reuse only verified matches and check current Jira status. If lookup is unavailable, do not blindly create a Bug or Task.
7. Build bounded context for unknown groups: traceback, preceding and following events, versions, relevant files at the correct SHA, history and Jira candidates. Send data as untrusted content to the corporate LLM.
8. Validate JSON parsing, Pydantic schema, allowed categories, existence of evidence IDs and consistency with facts. Semantic verification of causality is limited; do not present hypotheses as established facts. Allow bounded retries for invalid JSON. If analysis completes but the cause is unknown, create an Investigation Task. LLM failure yields technical_error and a partial report, not a fabricated defect.
9. Apply the Rule Engine to validated facts and generate an action plan. Dry-run ends with a local report and plan without external writes.
10. On publish, check that the plan matches current context and rule version, and recheck duplicates/statuses. Record intent before each external operation. Publish Jira before Confluence; persist each outcome. Do not repeat uncertain writes without reconciliation.
11. Build the report from verified data and actual Jira outcomes (planned does not mean created). If Jira is unavailable, a partial Confluence report marked pending is permitted when Confluence is available. Update the same report after recovery.
12. Save local artifacts and status: complete, partial, failed or pending_publication. Never change the test status.

## Campaigns

An explicit campaign_id is supplied in each Launch's metadata or run context. CI may provide a manifest of expected stands; otherwise use the configured list. If both are provided and disagree, record the conflict instead of guessing. For a manual list, default scope is the specified runs; expected membership must be supplied explicitly to assess completeness. Incomplete policies: wait until deadline, partial or skip. When a late stand arrives, update the existing report and add only new occurrences. Do not group solely by calendar date.

## Analysis budgets

Configure log volume, tokens, request count, time, retries and analysis concurrency. Record context truncation and availability issues. Start with ordinary Chat Completions; tool calling is not needed for the first version. Example budgets are not measured performance figures.

## Resume

Read/analysis operations may be retried within budget; writes require a journal and verifiable key. For in_flight after a crash, first reconcile the external marker/ID. If outcome cannot be determined, set uncertain rather than retrying automatically. Moving between machines requires current state or recovery from confirmed external markers. Until these mechanisms are tested, publication is allowed only on one canonical instance.
