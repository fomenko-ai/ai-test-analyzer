"""Composition root for the implemented local adapters."""

from pathlib import Path

from ai_test_analyzer.adapters.config import load_context, load_settings
from ai_test_analyzer.adapters.junit import JUnitSource
from ai_test_analyzer.adapters.report import LocalReportWriter
from ai_test_analyzer.application.analyze import analyze
from ai_test_analyzer.domain.models import TestRun


async def analyze_file(
    source: Path, output: Path, config: Path | None, context: Path | None
) -> TestRun:
    settings = load_settings(config)
    manifest = load_context(context)
    return await analyze(
        JUnitSource(source, settings.max_xml_bytes),
        LocalReportWriter(output),
        manifest,
        settings,
    )
