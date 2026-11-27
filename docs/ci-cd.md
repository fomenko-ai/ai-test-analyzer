# Execution and Operations

Stage 1 supports only local `analyze --source junit --input FILE --output NEW_DIRECTORY [--config YAML] [--context JSON]`. See README.md and [stage1-results.md](stage1-results.md) for exercised commands, the implemented file context and exit behavior. The ReportPortal/group/publish/discover/poll/resume examples below remain future contracts. CI installation must use `uv sync --locked`; no CI provider or corporate manifest integration has been tested.

The following CLI contract and integration scenarios describe the future application, not commands of an installed package. Jenkins and GitLab supply the same RunContext and share business logic. Support uv and Docker Compose on Linux.

```bash
# Analysis without external writes (default)
uv run ai-test-analyzer analyze --launch-id 12345 --stand-id stand-01
uv run ai-test-analyzer analyze --campaign-id campaign-001 --context context.json
uv run ai-test-analyzer analyze --launch-id 12345 --launch-id 12346 --context context.json
uv run ai-test-analyzer analyze --source junit --input results.xml --context context.json
# Explicit opt-in to publish an existing plan
uv run ai-test-analyzer publish --analysis-id analysis-001 --execute
# Discover and process new runs: no external writes unless explicitly enabled
uv run ai-test-analyzer discover --once
uv run ai-test-analyzer poll
# Recovery: reconcile before retrying writes
uv run ai-test-analyzer resume --analysis-id analysis-001
```

Required fields depend on mode. Context may contain source instance/project, Launch IDs, campaign_id, expected_stands, Git SHA, CI build URL, firmware/software versions and artifact references. Do not assume CI pipeline IDs are globally unique. Document and test CLI/config precedence.

## Jenkins

At test job completion, including failures, preserve the manifest and required artifacts. An independent analysis job/step consumes the manifest, waits for a terminal ReportPortal status and runs the analyzer. Report analysis failures separately; never rewrite test outcomes. If Jenkins is not the canonical publisher, transfer the plan and artifacts to the selected publisher or remain in dry-run. Do not start a second publisher concurrently.

## GitLab

Use a separate analysis job after testing, including failed tests; retain manifest artifacts even when tests fail. Publish separately according to the single-publisher policy. GitLab job serialization does not protect against Jenkins/cron/CLI. Validate CI syntax in the installed GitLab and Jenkins versions; create actual Jenkinsfile/.gitlab-ci.yml after confirming the environment and manifest transfer method.

## Cron and polling

Cron invokes one-shot discovery/analysis; a polling service periodically uses the same use case. Store source filters and cursor in the state adapter, with overlap/lookback and run_key deduplication; recheck unfinished launches. For campaigns, wait for expected stands or apply the configured incomplete policy. Cron and polling must not publish simultaneously. Configure interval, wait window, backlog and retries.

## Docker Compose

One publisher/poller instance in MVP; persistent volumes for JSON and artifacts; read-only configuration and Git mounts. MCP may use a local process or corporate endpoint after validation. Do not include unnecessary external services in Compose. CLI and polling use the same image and core.

## Statuses

Proposed exit code contract: 0 complete, 2 partial/pending, 1 fatal/config error. A successful dry-run is complete. This is a technical default, not an agreed corporate standard. Report test and analyzer statuses separately in CI, using separate jobs/statuses where required. Preserve a JSON summary even on partial/fatal results when technically possible.

## Runtime and container versions

See [dependencies.md](dependencies.md). Inherited image candidates: `python:3.14.10-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.10`; Compose plugin candidate 5.8.0. Use standard `services` and `docker compose` commands without experimental jobs or scheduling features. Verify current releases, architecture and digests before production; pin images in Dockerfile, not floating `latest`. Jenkins and GitLab use the same built application image. Do not include Docker socket, PostgreSQL or Redis in MVP.
