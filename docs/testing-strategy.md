# Testing Strategy

## Test levels

| Level | Coverage |
|---|---|
| Unit | Normalizer, fingerprints, grouping, config validation, Rule Engine, Pydantic contracts, template rendering |
| Contract | Every adapter against shared contracts, pagination, errors, incompatible capabilities, JSON Mode validation |
| Integration | Mock services, then separate corporate test instances; read-only first |
| Evaluation | Historical failures with verified QA labels, independent holdout and quality measurement |
| End-to-end | Fixture -> analysis -> plan -> dry-run -> test Jira/Confluence -> resume |

## Mandatory acceptance scenarios

| ID | Scenario | Expected result |
|---|---|---|
| AC-01 | Successful run without failures | Correct statistics, report according to policy, no Jira Bug |
| AC-02 | New supported Product/Automation Bug | One issue per confirmed group |
| AC-03 | Known open Bug/Task | One comment for new occurrences |
| AC-04 | Repeat the same run, including restart | No duplicate issue/comment/page with supported markers |
| AC-05 | Unknown/ambiguous duplicate | Investigation Task with hypotheses, evidence and candidates; no duplicate Task on repeat |
| AC-06 | Closed issue | Apply Status/Resolution policy; defer if no rule exists |
| AC-07 | Same symptom on two stands | No merge without adequate support; Stand Issue scoped by stand |
| AC-08 | Campaign with late/unfinished stand | wait/partial/skip according to config; late stand updates report |
| AC-09 | Jira search failed | No blind Bug/Task creation; publication pending |
| AC-10 | Jira timeout after actual write | Reconcile; do not retry automatically without confirming absence |
| AC-11 | LLM unavailable / malformed JSON | Bounded retries; partial report, technical status, no fabricated defects |
| AC-12 | Confluence unavailable after Jira | Resume publishes report without repeating Jira operations |
| AC-13 | Dry-run with any input combination | Zero external write calls |
| AC-14 | Git SHA mismatch / DUT log missing | Missing data; no references to mismatched code |
| AC-15 | Prompt injection in logs | Instructions ignored, secrets redacted, write tools unavailable |
| AC-16 | Jenkins/GitLab/CLI with equivalent manifest | Same normalized context and decisions |
| AC-17 | Missing route/required field | Block affected publication and provide explicit reason |
| AC-18 | Individual analysis after group analysis | No repeated comments for covered occurrences |

## LLM quality evaluation

Collect historical examples with independent engineer classification and evidence. Split datasets by defect/campaign to prevent repeated failures leaking into the holdout. Measure class precision/recall, deduplication precision, proportion of supported findings, Unknown rate, false issue creation and missed defects. Compare to human labels, not model self-confidence. Agree automation thresholds after baseline evaluation; arbitrary confidence is not evidence. Disable production publication until acceptance criteria are agreed and dry-run succeeds.

## Dependency gate

On target Linux/CPython 3.14, run `uv lock`, `uv sync --locked --all-extras --group dev`, `uv run --locked pytest`, `uv run --locked ruff check .`, `uv run --locked ruff format --check .`, `uv run --locked mypy src` and `uv build`. Check real imports, safe XML/HTML parsing, MCP initialize/list_tools/call_tool using fixtures, HTTP/LLM mocks, container build and smoke tests. Scan full lockfile and images with an approved vulnerability scanner. Perform checks after skeleton implementation; see [dependencies.md](dependencies.md).
