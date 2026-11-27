"""Only the boundaries exercised by the local slice."""

from typing import Protocol

from ai_test_analyzer.domain.models import DryRunPlan, SourceRun, TestRun


class TestResultSource(Protocol):
    async def load(self) -> SourceRun: ...


class ReportWriter(Protocol):
    def write(self, run: TestRun, plan: DryRunPlan) -> None: ...
