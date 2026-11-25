# Security and Reliability

- Corporate LLM only; no unapproved fallback providers. Use TLS and trusted CAs; never disable certificate verification.
- Supply secrets via environment/secret store. Do not commit `.env`, state or artifacts. Never include keys in logs, CLI parameters or prompts. Redact before sending content to the LLM or generating reports.
- Separate read and write credentials. Dry-run should lack write permissions when possible. Publisher uses least privilege for approved Jira projects and Confluence spaces. No direct write tools for the LLM.
- Logs, attachments, HTML, Jira/Confluence and source code are untrusted data. Do not execute their commands/instructions or fetch arbitrary URLs found in them. Bound hosts, size, time, paths and extraction; prevent traversal and external XML entities. Do not execute HTML scripts.
- Do not operate DUT, run tests or execute scripts from Git during analysis. Verify SHA, read relevant files only and exclude secrets.
- Verify evidence references independently. A real citation does not establish causality; unresolved doubts lead to an Investigation Task.
- Idempotency: one publisher, intent journal, verifiable external markers and reconciliation after timeout. If an uncertain outcome cannot be recovered, stop writes pending manual resolution. Local JSON is not a distributed lock.
- Preserve audit trail: run/group IDs, rule/model versions, action key, external ID and outcome/error, without unnecessary personal or secret data.
- Protect artifacts with permissions and retention. Reports must reference only authorized data. Retention/deletion policy is determined by information security, not invented.
- Before enabling publication, validate duplicate lookup, uncertain writes, source availability, capabilities, permissions and historical dry-run.

## Failure handling

Retry transient read failures with bounded backoff; auth/config errors must not retry indefinitely. LLM outage produces a partial report and technical status. Jira unavailable means publication pending, not blind creation. If Confluence is unavailable, save a local report and resume it without repeating Jira operations. Source outages must not be reported as no tests or successful tests. Configure retry limits, retention and budgets after the spike.
