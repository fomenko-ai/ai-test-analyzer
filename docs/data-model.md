# Data Model and Identifiers

Versioned JSON contracts with Pydantic. External object identifiers are strings; do not assume different sources share ID formats. Preserve timezone-aware timestamps (UTC), full SHA and source provenance. Represent missing values as null rather than inventing data.

| Entity | Main fields |
|---|---|
| RunContext | schema_version, run_refs, campaign_id?, expected_stands?, ci_provider?, build_url?, repo_ref?, git_sha?, metadata |
| TestRun | run_key, source_instance, project_key, launch_id?, stand_id, start/end, status, git_sha?, firmware_version?, software_version?, test_items, completeness |
| TestItem | item_key, node_id?, status, attempt?, duration, error, evidence_refs, parent?, parameter_identity |
| EvidenceRef | evidence_id, source_type, source_uri_or_id, item_key?, range?, sha?, excerpt_digest?, availability |
| FailureGroup | group_id, member_item_keys, candidate_scope, symptom, fingerprint, related_groups, evidence_refs |
| AnalysisResult | group_id, analysis_status, category, symptom, root_cause?, hypotheses, evidence_ids, missing_data, suggested_checks, model_id, prompt_version |
| DuplicateMatch | status, candidate_keys, verified_issue_key?, rationale, lookup_status |
| Decision | rule_id, config_version, group_id, action, target_issue?, route, reason |
| PublicationIntent | action_key, run_or_campaign_key, target, payload_hash, status, external_id?, error? |
| ReportRecord | report_key, revision, page_id?, outcome, referenced_issues |

## Identity and statuses

- `run_key`: namespaced source instance + project + launch ID; for files use manifest run_id or a stable key based on context and artifact hash, not date alone.
- `campaign_key`: namespaced project + explicit campaign_id; a manual group uses a stable hash of sorted run_keys and preserves membership. Adding to a campaign retains the key and changes the revision.
- `item_key`: stable source item ID or run_key + node ID + parameters + attempt. Distinguish retries; compute summary statistics using the chosen retry policy. If semantics are unknown, explicitly report attempt counts.
- `fingerprint`: version + category scope + normalized stable signature. Do not use arbitrary LLM-generated UUIDs as keys. Preserve algorithm version and provide migration support.
- `analysis_status`: analyzed, needs_investigation, insufficient_data, technical_error. A technical error is not an Unknown defect.
- `duplicate_status`: confirmed, not_found, ambiguous, lookup_failed. The last is not equivalent to not_found.
- `publication_status`: planned, in_flight, confirmed, uncertain, retryable_error, blocked. `uncertain` requires reconciliation.

## Action idempotency

A comment key includes the confirmed defect ID and occurrence ID (run_key + corresponding group/items), not the date or new analysis ID. Group comments contain covered occurrence IDs; overlapping campaign analysis must not comment again on covered occurrences. A Bug creation key derives from stable defect identity. Ambiguous matches and Investigation Tasks use a separate stable symptom/scope key. A report key is determined by report scope, not publication time; reruns update the existing page. Choose external marker formats after validating Jira/Confluence capabilities.

Input and model response examples: `../examples/contracts/`. They are illustrative; generate final JSON Schemas from implemented models and verify them in contract tests.

## Stage 1 implemented subset

The Pydantic contracts in `src/ai_test_analyzer/domain/models.py` implement FileContext, Settings, SourceRun, TestRun, TestItem, EvidenceRef, Statistics and a non-executable DryRunPlan. The larger entity table above remains the target design. FileContext is a separate local input contract; it does not replace the future ReportPortal RunContext example.

`file-v1-` run keys hash the effective file context and exact artifact digest, so conflicting file revisions cannot silently share a key. Moving the same bytes to another authorized path does not change the key. Item keys include the run, hashed original classname/name and document-order index; duplicate testcase records are preserved. These local keys are not defect fingerprints or adopted publication markers. Changing artifact bytes, record order or context can change keys; cross-revision source identity and retry reconciliation remain future work.

Evidence addresses the exact artifact SHA256 and zero-based testcase document-order index. It requires the original authorized file and is not a public URL. SHA presence in metadata does not verify Git source availability. Raw test names, source paths, messages, logs and arbitrary properties are deliberately omitted from saved outputs; node_id and attempt are null because no pytest node reconstruction or retry interpretation is performed.

Statistics count records once from JUnit only. Conflicting context/source values become null with provenance `conflict`; missing metadata remains null. Source count disagreements are explicit data conflicts, not silently corrected source results. Aware suite timestamps are normalized to UTC; the earliest timestamp is used only when all suites supply aware timestamps. Missing/naive/invalid timestamps leave started_at null.
