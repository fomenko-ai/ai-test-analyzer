# Dependencies and Runtime

Phase 0 execution update (2026-11-26): the isolated probe successfully resolved and installed runtime, extras and dev dependencies under CPython 3.14.10 using the official uv 0.13.10 Python image. OpenAI 3.60.0 and owner-approved HTTPX2 2.16.2 replace their inherited candidates in this document and bootstrap template. See [technical-spike-results.md](technical-spike-results.md) and [probe lockfile](../spikes/phase0/uv.lock). Application builds and corporate checks are still pending; the probe lockfile is not an application lockfile.

The original candidate snapshot is dated 2026-11-25, with the Phase 0 updates above. Joint probe installation has been demonstrated on Linux amd64 only. Recheck current stable releases and perform the actual application installation/build on the target platform before adopting a production baseline. This table is not a lockfile.

## Runtime

| Component | Candidate | Purpose / source |
|---|---|---|
| CPython | 3.14.10 | [Release](https://www.python.org/downloads/release/python-31410/), standard GIL build; `>=3.14.10,<3.15` |
| uv | 0.13.10 | [Releases](https://github.com/astral-sh/uv/releases), dependency manager |
| uv_build | 0.13.10 | [PyPI](https://pypi.org/project/uv-build/0.13.10/), build backend |
| openai | 3.60.0 | [PyPI](https://pypi.org/project/openai/), Chat Completions with corporate base_url; updated after isolated probe |
| mcp | 2.3.0 | [PyPI](https://pypi.org/project/mcp/), client SDK; candidate major v2, do not copy v1 API examples without checking |
| pydantic | 2.14.4 | [PyPI](https://pypi.org/project/pydantic/), contracts |
| pydantic-settings | 2.16.3 | [PyPI](https://pypi.org/project/pydantic-settings/), configuration and environment |
| httpx2 | 2.16.2 | [PyPI](https://pypi.org/project/httpx2/), REST and CI artifacts; owner-approved replacement for httpx |
| PyYAML | 6.0.4 | [PyPI](https://pypi.org/project/PyYAML/), safe_load + validation |
| Jinja2 | 3.1.6 | [PyPI](https://pypi.org/project/Jinja2/), controlled templates |
| beautifulsoup4 | 4.15.0 | [PyPI](https://pypi.org/project/beautifulsoup4/), extra `html`, built-in html.parser |
| defusedxml | 0.7.1 | [PyPI](https://pypi.org/project/defusedxml/), extra `junit`, bound XML size; explicit 3.14 smoke test needed for this older release |

## Development

| Library | Candidate | Purpose |
|---|---|---|
| pytest | 9.2.0 | [PyPI](https://pypi.org/project/pytest/), tests |
| pytest-asyncio | 1.5.0 | [PyPI](https://pypi.org/project/pytest-asyncio/), async MCP and HTTP |
| pytest-cov | 7.1.0 | [PyPI](https://pypi.org/project/pytest-cov/), coverage |
| ruff | 0.17.6 | [PyPI](https://pypi.org/project/ruff/), lint/format, target py314 |
| mypy | 2.4.1 | [PyPI](https://pypi.org/project/mypy/), types; add stubs only as needed |

Resolve transitive libraries (e.g. pydantic-core, anyio, httpcore, MarkupSafe, coverage) through uv; do not impose arbitrary independent pins. Use the standard library for JSON, SHA256, CLI, retry/backoff, subprocess, Git CLI, logging and polling where sufficient. Git and CA certificates are system dependencies. Requests, aiohttp, GitPython, LangChain, Hermes, Celery, PostgreSQL/Redis, FastAPI and third-party Jira SDKs are not required in MVP. Kilo Code is not a mandatory dependency.

## Docker

| Artifact | Candidate | Source / caveat |
|---|---|---|
| Python runtime | `python:3.14.10-slim-trixie` | [Official image](https://hub.docker.com/_/python), Debian 13 glibc |
| uv binary | `ghcr.io/astral-sh/uv:0.13.10` | [Registry](https://github.com/astral-sh/uv/pkgs/container/uv), copy binaries |
| ReportPortal MCP (optional) | `reportportal/mcp-server:1.4.1` | [Releases](https://github.com/reportportal/reportportal-mcp-server/releases); registry tag/manifest unconfirmed. Verify before use. ReportPortal >=25.1, API >=5.14.0; check MCP protocol negotiation |
| Compose plugin | 5.8.0 | [Release](https://github.com/docker/compose/releases/tag/v5.8.0); host tooling, not an image; use standard services without jobs |
| Jira / Confluence MCP | TBD | Corporate implementations unknown; do not invent images |

Choose Docker Engine / Buildx according to corporate Linux and supported security releases. They are host tooling, not Python dependencies. Pin each external image by digest in production after confirming availability and architecture in the approved registry. Verify MCP server protocol versions, transport and tools separately. Do not require external servers to run Python 3.14. Do not mount the Docker socket; use a separate process/container or endpoint for local MCP. Build the analyzer image after skeleton implementation and reuse it for CLI, polling and CI/CD.

## Reproducibility and gate

Copy `../examples/bootstrap/` templates into the future repository root. Create `src/ai_test_analyzer/` and the entry point before building. Template pins are a snapshot: verify current stable releases and choose the latest compatible combination (no prereleases). If versions conflict or do not exist in the approved registry, document the constraint and actual resolver result, then update all related pins consistently. Do not change the Python minor branch without approval.

```bash
uv --version
uv python install 3.14.10
uv python pin 3.14.10
uv lock
uv sync --locked --all-extras --group dev
uv run --locked python -VV
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv build
# Inspect manifests for the target Linux architecture.
# For ReportPortal, first confirm the candidate tag exists.
docker buildx imagetools inspect python:3.14.10-slim-trixie
docker buildx imagetools inspect ghcr.io/astral-sh/uv:0.13.10
docker buildx imagetools inspect reportportal/mcp-server:1.4.1
# After pinning verified FROM image digests and creating the skeleton:
docker build -t ai-test-analyzer:0.1.0 .
docker run --rm ai-test-analyzer:0.1.0 --help
```

Commit `pyproject.toml`, `.python-version`, the actual generated `uv.lock` and Dockerfile with verified digests. CI uses `uv sync --locked` and does not modify the lockfile. Update through merge requests (`uv lock --upgrade` after updating direct pins), the full test suite, lockfile/image vulnerability scans, rebuild and dry-run. Use approved corporate mirrors, TLS and CAs; never disable verification. Record public metadata checks, resolver results, unit/smoke tests and corporate integration checks separately.
