# Business Rules and Jira

## Separation of responsibilities

Markdown tells the model how to analyze; YAML defines actions for validated facts; Python executes the rules. Jinja2 templates handle presentation. Validate configuration and reject unknown keys, categories, condition types and conflicting priorities. Preserve the effective configuration version in artifacts. Example: `../examples/config/decision_rules.yaml`.

## Decision order

| Priority | Condition | Action |
|---|---|---|
| 1 | Jira lookup_failed, missing route or uncertain previous write | Block write and record the reason |
| 2 | Confirmed open defect/Task | Comment on new occurrences |
| 3 | Confirmed closed issue | Apply Status + Resolution policy; defer if no rule exists |
| 4 | Technical analysis failure | Partial report; do not fabricate a Bug |
| 5 | Ambiguous candidates | Create an Investigation Task with links unless an equivalent Task already exists |
| 6 | New, supported Product Bug or Automation Bug | Create Bug |
| 7 | Supported Stand Issue | Create an issue using stand/category routing |
| 8 | Analysis completed, but cause is Unknown or evidence is insufficient | Investigation Task |
| 9 | Other category | Report only unless explicitly configured |

A confirmed known defect may receive a comment during an LLM outage if the match was independently verified and Jira is available. An unavailable source does not imply absence of defects. For Investigation Tasks, first search by stable symptom key to avoid creating a new Task each night for the same ambiguous case.

## Deduplication and grouping

Fingerprints use stable features: component, operation, exception type, normalized signature, context and scope. Normally exclude timestamps, random UUIDs and durations. Versions and stands remain evidence; inclusion in the key depends on category. Product Bug may span stands if a common cause is supported; Stand Issue is stand-scoped by default. Automation Bug and Unknown use configurable scope. Identical text is not sufficient: a normalized signature identifies a candidate, not proof of causality. Check incompatible versions/configurations and current Jira mapping.

Fingerprint storage uses an adapter capable of searching and writing Jira custom fields, labels, structured description blocks or issue properties when validated. JSON is a local cache. The chosen field must support reliable marker lookup; a write API does not guarantee indexing. After manual investigation, the engineer records the verified cause and Bug link. Automatic import requires an agreed marker format.

## Routing

Proposed precedence: exact category + stand override, then category default. For cross-stand groups with differing routes, use an explicitly configured group route; otherwise block publication. Do not invent priority or assignee without a configured rule. Closed issue policies: comment, reopen, create_linked_issue or defer, only for explicitly configured Status/Resolution pairs and with adequate permissions. Test reopening in a Jira test environment.

## Investigation Task

Required content: observed symptom, affected tests/stands, versions, SHA, launch/run keys and CI/log links, primary finding (Unknown), hypotheses, evidence, checks already performed, missing information, recommended investigation steps, potential duplicates and fingerprint/occurrence markers. Artifact links must be accessible to engineers or carry access/retention limitations. The engineer decides whether to close, convert or link the Task to a Bug. No automatic status transition.

## Confluence

Include scope, completeness, source-derived statistics, failure groups, rationale, Jira outcomes/keys, pending/technical errors, rule/model metadata and evidence links. Adapt the existing corporate template when received. Locate existing pages by stable report key. Preserve manual changes outside the managed block when supported; otherwise agree on separate analyzer-owned pages.
