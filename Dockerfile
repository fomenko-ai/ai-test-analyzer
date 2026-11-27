# Verified public manifests; execution evidence: docs/stage1-results.md.
FROM ghcr.io/astral-sh/uv@sha256:b093dbbd7963c765325ecdf866d42915f5327e135569f9dae9c77cac63559bf2 AS build
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy UV_DEFAULT_INDEX=https://pypi.org/simple
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --all-extras --no-install-project
COPY src/ ./src/
RUN uv sync --locked --no-dev --all-extras --no-editable

FROM python:3.14.10-slim-trixie@sha256:22eafb370920ad8b429e0aec3fff433e0669968519f5d60469d83729c138b28b
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=build /app/.venv /app/.venv
RUN mkdir /data && chown 10001:10001 /data
USER 10001:10001
WORKDIR /data
ENTRYPOINT ["ai-test-analyzer"]
CMD ["--help"]
