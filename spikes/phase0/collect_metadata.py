"""Collect public metadata; this is a disposable spike, not application code."""

import concurrent.futures
import json
import urllib.request
from pathlib import Path

PACKAGES = (
    "openai",
    "mcp",
    "pydantic",
    "pydantic-settings",
    "httpx2",
    "PyYAML",
    "Jinja2",
    "beautifulsoup4",
    "defusedxml",
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "ruff",
    "mypy",
    "uv",
    "uv-build",
)


def collect(name):
    url = f"https://pypi.org/pypi/{name}/json"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.load(response)
    version = data["info"]["version"]
    return name, {
        "version": version,
        "requires_python": data["info"]["requires_python"],
        "source": url,
        "files": [
            {
                key: item[key]
                for key in (
                    "filename",
                    "requires_python",
                    "yanked",
                    "upload_time_iso_8601",
                )
            }
            for item in data["releases"][version]
        ],
    }


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = dict(pool.map(collect, PACKAGES))
    Path(__file__).with_name("metadata.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    for name, record in results.items():
        print(name, record["version"], record["requires_python"])
