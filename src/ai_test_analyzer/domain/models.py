"""Versioned contracts; missing context never becomes invented metadata."""

from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9_.:-]{1,128}$")]
MetadataOrigin = Literal["context", "junit", "both", "conflict", "missing"]
GitSHA = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class FileContext(Contract):
    schema_version: Literal["1.0"] = "1.0"
    source_instance: Identifier | None = None
    project_key: Identifier | None = None
    run_id: Identifier | None = None
    stand_id: Identifier | None = None
    campaign_id: Identifier | None = None
    git_sha: GitSHA | None = None
    firmware_version: Identifier | None = None
    software_version: Identifier | None = None


class Settings(Contract):
    schema_version: Literal["1.0"] = "1.0"
    publish_enabled: Literal[False] = False
    max_xml_bytes: Annotated[int, Field(strict=True, ge=1, le=100 * 1024 * 1024)] = (
        10 * 1024 * 1024
    )


class RawCase(Contract):
    identity_digest: str
    status: Literal["passed", "failed", "error", "skipped"]
    duration_seconds: Annotated[float, Field(ge=0)] | None = None


class SourceRun(Contract):
    artifact_digest: str
    context: FileContext
    cases: tuple[RawCase, ...]
    started_at: AwareDatetime | None = None
    missing_data: tuple[str, ...] = ()
    data_conflicts: tuple[str, ...] = ()


class EvidenceRef(Contract):
    evidence_id: str
    source_type: Literal["junit"] = "junit"
    source_uri_or_id: str
    artifact_sha256: str
    testcase_index: int
    availability: Literal["local_input_required"] = "local_input_required"


class TestItem(Contract):
    item_key: str
    identity_digest: str
    node_id: None = None
    attempt: None = None
    status: Literal["passed", "failed", "error", "skipped"]
    duration_seconds: float | None
    evidence_refs: tuple[EvidenceRef, ...]


class Statistics(Contract):
    total: int
    passed: int
    failed: int
    error: int
    skipped: int
    counting_unit: Literal["testcase_records"] = "testcase_records"


class TestRun(Contract):
    schema_version: Literal["1.0"] = "1.0"
    run_key: str
    context: FileContext
    metadata_provenance: dict[
        str, Literal["context", "junit", "both", "conflict", "missing"]
    ]
    artifact_digest: str
    started_at: AwareDatetime | None
    statistics: Statistics
    test_items: tuple[TestItem, ...]
    missing_data: tuple[str, ...]
    data_conflicts: tuple[str, ...]


class DeferredInvestigation(Contract):
    item_key: str
    action: Literal["investigation_required"] = "investigation_required"
    analysis_status: Literal["not_performed"] = "not_performed"
    duplicate_lookup_status: Literal["not_performed"] = "not_performed"
    publication_status: Literal["blocked"] = "blocked"
    reason: Literal["Analysis and duplicate lookup are not implemented"] = (
        "Analysis and duplicate lookup are not implemented"
    )


class DryRunPlan(Contract):
    schema_version: Literal["1.0"] = "1.0"
    run_key: str
    config_digest: str
    mode: Literal["dry_run"] = "dry_run"
    external_operations: tuple[()] = ()
    investigations: tuple[DeferredInvestigation, ...]
    limitations: tuple[str, ...] = (
        "No cause classification, grouping, LLM analysis or Jira lookup performed",
        "No executable publication payload or corporate integration is available",
        "Raw names, messages, logs and arbitrary properties are omitted",
        "Evidence requires the original authorized local artifact matching its digest",
    )
