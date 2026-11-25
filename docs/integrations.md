# Integrations

General policy: prefer MCP, use REST for unsupported operations. Return typed results; support bounded read timeout/retry, pagination and capability checks. Do not fix MCP tool names until introspection. Never supply credentials as CLI arguments, prompts or Git content.

| System | Required operations | Pre-production checks |
|---|---|---|
| ReportPortal 25.1+ | Discover launches, status, test tree, logs, attachments, attributes, history | Installed MCP/API compatibility, pagination, log completeness, campaign_id, terminal states, permissions |
| Jira | Search/get, create Bug/Task, comment, marker lookup, optional transitions/links | Unknown MCP implementation; JQL/fingerprint indexing, projects, types, required fields, status/Resolution, comment visibility, timeout recovery |
| Confluence | Find report, create/update page, version/conflict management | Unknown MCP implementation; body format, parent/space, template, stable marker, page updates |
| Corporate LLM | Chat Completions, JSON Mode; optional Tool Calling | base_url/model, auth, TLS, rate/context limits, JSON validity, errors/retries, data policy |
| Git | Resolve full SHA, read source at SHA | Repository and commit availability; local/CI checkout/clone; do not execute code |
| Jenkins/GitLab | Links and authorized artifact retrieval | API access, retention, authorization, size limits |
| Files | JUnit, HTML, DUT logs | Real examples, encoding, timezone, test ID mapping, HTML format, safe parsing |

## ReportPortal

One Launch per stand. Do not assume launch UUID, ID and sequence number are interchangeable. Instance key and project are required. Support individual and group modes. If campaign_id is unavailable through MCP, read attributes through REST or use an explicit manifest. Do not trigger ReportPortal auto-analysis or modify its defect classification without a separate requirement.

## Jira and Confluence

Isolate domain-to-payload conversion in adapters. Check search and write capabilities before publication; never simulate successful writes. REST is permitted for unsupported write tools, but after an uncertain outcome reconcile before any fallback write. Real project, field, type, space and parent page identifiers come from corporate configuration. Status transition permissions are needed only when closed-issue policies permit them.

## LLM

Separate instructions from context. Explicitly request JSON in JSON Mode and validate with Pydantic. The model does not make final write decisions. Preserve model identifier, prompt/config version, usage, finish reason and error class. Retain request contents only when policy permits. Do not send the full repository or all logs. Additional read-only tools may be introduced as an extension when needed.

## File sources and Git

JUnit may omit logs. The HTML adapter supports agreed formats rather than arbitrary HTML. Record missing_data for unavailable sources. DUT and CI logs enrich TestRun but must not duplicate result counts. Verify full SHA; if mismatched, read Git objects or use a separate checkout without changing the engineer's working files. If the SHA is unavailable, report that source analysis is unavailable.
