# Skeleton template: requires real uv.lock and source package before build.
# Verify and pin both image digests before production.
FROM ghcr.io/astral-sh/uv:0.13.10 AS uv_bin
FROM python:3.14.10-slim-trixie
COPY --from=uv_bin /uv /uvx /bin/
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system analyzer && useradd --system --gid analyzer --create-home analyzer \
    && mkdir -p /app/data && chown analyzer:analyzer /app/data
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --all-extras --no-install-project
COPY src/ ./src/
RUN uv sync --locked --no-dev --all-extras --no-editable
ENV PATH="/app/.venv/bin:$PATH"
USER analyzer
ENTRYPOINT ["ai-test-analyzer"]
CMD ["--help"]
