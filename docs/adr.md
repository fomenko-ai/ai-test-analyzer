# Architecture Decision Records

Statuses: Agreed means an explicit requirement; Design decision means a proposed technical implementation based on those requirements. Changes require review and an explanation of their consequences.

| ADR | Decision | Status | Rationale / trade-off |
|---|---|---|---|
| 001 | `ai-test-analyzer`, without nightly/regression | Agreed | Test type and execution time do not limit the product |
| 002 | Python modular monolith, Ports and Adapters | Design decision | Independent integrations without microservices; typed boundaries |
| 003 | CI-agnostic CLI + discovery | Agreed | Jenkins/GitLab/manual/cron/poll use one core |
| 004 | One Launch per stand; campaign_id/manual list | Agreed | Correlation without grouping by date; completeness requires expected stands |
| 005 | MCP preferred / REST fallback | Agreed | MCP capabilities vary; never use blind fallback after a write timeout |
| 006 | JSON + Jira, replaceable adapters | Agreed | No separate database; Jira stores persistent defects, JSON stores technical state |
| 007 | One publisher in MVP | Agreed | Operational restriction, no distributed lock; replace state store/lock if needed later |
| 008 | Markdown + YAML + Python Rule Engine | Design decision | AI analyzes; deterministic policy controls writes |
| 009 | Unknown -> Investigation Task, ambiguous -> Task | Agreed | Jira is the investigation queue; no hidden failures or forced classification |
| 010 | External AI Investigation Agent, manual start | Agreed | No Kilo Code/Hermes dependency; engineer decides how to resolve Task |
| 011 | JSON Mode + Pydantic | Design decision | JSON Mode does not guarantee schema compliance; optional Tool Calling |
| 012 | Dry-run before production | Agreed | Evaluate historical failures and quality before automatic writes |
| 013 | Configurable fingerprint storage, route and scope | Agreed | Jira fields and workflows differ; identical text does not establish a common defect |
| 014 | Independent analyzer status | Agreed | LLM/integration failure does not change test results |
| 015 | uv, Linux, Docker Compose | Agreed | Consistent runtime; one canonical publisher as a design default |
| 016 | Jinja2 templates | Design decision | Separate presentation from logic; adapt existing Confluence template |

## ADR-017 — CPython 3.14 and reproducible dependencies

Status: Python 3.14 is an agreed requirement; candidate versions and library choices are described in [dependencies.md](dependencies.md). Pin Python patch, uv, lockfile and verified OCI digests. Use the latest stable compatible releases, not floating latest at execution time. Update through reviewed merge requests. Joint dependency resolution and smoke tests are mandatory; unverified versions are not a production baseline.
