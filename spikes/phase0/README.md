# Isolated Phase 0 dependency probes

These files are experiments, not the application skeleton. SDK/server test data is synthetic; sample_summary.json is derived from real local artifacts as described below. No corporate integration has been tested, and none of the tests publishes externally. metadata.json records public PyPI metadata observed during this run; pyproject.toml selects the reported stable candidates for joint resolution. The probe has no build backend because it is not a distributable application. uv_build compatibility and the application wheel/container build remain separate checks.

HTTPX2 is the approved direct runtime HTTP client; legacy HTTPX is included only in the dev group for comparison probes. build_probe/ contains a synthetic package to exercise uv_build, not an application skeleton.

The official derived uv image was selected following the owner's suggestion. Its manifest was inspected at ghcr.io/astral-sh/uv:python3.14-trixie-slim and identified uv 0.13.10 with amd64/arm64 support. Use the observed immutable index digest:

```text
ghcr.io/astral-sh/uv@sha256:b093dbbd7963c765325ecdf866d42915f5327e135569f9dae9c77cac63559bf2
```

Inside the container, working in this directory:

```sh
python -VV
uv --version
uv lock --default-index https://pypi.org/simple
uv sync --locked --all-extras --group dev
uv run --locked pytest -q -p no:cacheprovider
uv run --locked ruff check --select E,F,I --ignore E501 .
uv run --locked ruff format --check .
```

Set UV_PROJECT_ENVIRONMENT and UV_CACHE_DIR to writable temporary paths outside the source directory. Do not mount the Docker socket or corporate credentials into the container. Docker daemon access is needed only by the host process launching it. Review actual outcomes in ../../docs/technical-spike-results.md; a published tag or manifest is not evidence that the image executes correctly.

## Real artifact inspection

Run inspect_artifacts.py with --artifacts-dir pointing to a read-only mounted artifact directory and --output pointing to a writable summary file. It selects the newest JUnit sample per outcome by mtime and reads HTML/log files from the same run directory. The saved sample_summary.json contains derived structural metadata and hashes, not raw reports, hostnames, personal paths, traceback contents or test names. It records unresolved mapping and metadata limitations explicitly. Do not infer a production adapter contract or verified cause from this inspection.

Optional --git-repo verifies only that each recorded full SHA resolves to a commit object using git cat-file; it does not read source files. Mount this repository read-only too. Phase-aware HTML candidates are recorded separately and do not change exact-ID bijection results.

Local Phase 0 closeout is recorded in the results document. Stage 1 application implementation has not started.

Example inspection command inside a prepared probe container (both input mounts read-only):

```sh
uv run --locked --offline python inspect_artifacts.py \
  --artifacts-dir /samples --git-repo /test-repo --output /tmp/sample_summary.json
```

Copy only the resulting structural JSON to sample_summary.json after review; never copy raw reports. --git-repo must be the repository that produced the selected samples. The Git safe.directory override is scoped to this explicit read-only location and subprocess only.
