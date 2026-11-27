"""Write a complete local bundle to a new private directory."""

import os
import tempfile
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, StrictUndefined

from ai_test_analyzer.domain.models import DryRunPlan, TestRun


class LocalReportWriter:
    def __init__(self, output: Path) -> None:
        self.output = output

    def write(self, run: TestRun, plan: DryRunPlan) -> None:
        template = files("ai_test_analyzer.adapters").joinpath(
            "templates/report.html.j2"
        )
        html = (
            Environment(autoescape=True, undefined=StrictUndefined)
            .from_string(template.read_text())
            .render(run=run, plan=plan)
        )
        # A pre-existing destination is an error: never overwrite source artifacts
        # or a previous bundle, including when it is reached through a symlink.
        self.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=".analyzer-", dir=self.output.parent
        ) as tmp:
            staging = Path(tmp) / "bundle"
            staging.mkdir(mode=0o700)
            for name, value in (
                ("normalized.json", run.model_dump_json(indent=2)),
                ("plan.json", plan.model_dump_json(indent=2)),
                ("report.html", html),
            ):
                path = staging / name
                with path.open("x", encoding="utf-8") as stream:
                    os.chmod(path, 0o600)
                    stream.write(value + "\n")
            # mkdir reserves the destination; rename into it is intentionally
            # avoided because POSIX rename may replace an existing empty directory.
            self.output.mkdir(mode=0o700)
            for path in staging.iterdir():
                path.replace(self.output / path.name)
