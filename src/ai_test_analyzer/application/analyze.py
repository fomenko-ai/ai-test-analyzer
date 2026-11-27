"""Collect and normalize; no publisher or model is connected."""

from ai_test_analyzer.domain.models import FileContext, Settings, TestRun
from ai_test_analyzer.domain.normalize import normalize, plan
from ai_test_analyzer.ports.local import ReportWriter, TestResultSource


async def analyze(
    source: TestResultSource,
    writer: ReportWriter,
    context: FileContext,
    settings: Settings,
) -> TestRun:
    run = normalize(await source.load(), context)
    writer.write(run, plan(run, settings))
    return run
