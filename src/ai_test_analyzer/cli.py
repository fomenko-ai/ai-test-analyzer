"""CLI boundary. Input data and third-party exception text are never logged."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from ai_test_analyzer.adapters.files import InputError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai-test-analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="Local JUnit dry-run only")
    analyze.add_argument("--source", choices=["junit"], default="junit")
    analyze.add_argument("--input", required=True, type=Path)
    analyze.add_argument(
        "--output", required=True, type=Path, help="New output directory"
    )
    analyze.add_argument("--config", type=Path)
    analyze.add_argument("--context", type=Path)
    args = parser.parse_args(argv)
    try:
        from ai_test_analyzer.bootstrap import analyze_file

        run = asyncio.run(
            analyze_file(args.input, args.output, args.config, args.context)
        )
    except InputError as error:
        print(f"Analysis failed: {error}. No external writes.", file=sys.stderr)
        return 1
    except Exception:
        # Validation exceptions may contain credentials or raw artifact fragments.
        print(
            "Analysis failed: invalid/unavailable input, configuration, dependency or output. No external writes.",
            file=sys.stderr,
        )
        return 1
    print(
        json.dumps(
            {
                "run_key": run.run_key,
                "mode": "dry_run",
                "analyzer_status": "partial" if run.data_conflicts else "complete",
                "statistics": run.statistics.model_dump(),
                "analysis_performed": False,
                "external_writes": 0,
            }
        )
    )
    return 2 if run.data_conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
