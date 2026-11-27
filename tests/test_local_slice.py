"""Synthetic acceptance and adversarial inputs; no corporate integration claims."""

import asyncio
import json
import socket
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_test_analyzer.adapters.config import load_context, load_settings
from ai_test_analyzer.adapters.files import InputError, read_bounded
from ai_test_analyzer.adapters.junit import parse_junit
from ai_test_analyzer.bootstrap import analyze_file
from ai_test_analyzer.cli import main
from ai_test_analyzer.domain.models import FileContext, Settings
from ai_test_analyzer.domain.models import TestRun as NormalizedRun
from ai_test_analyzer.domain.normalize import normalize, plan

FIXTURE = Path(__file__).parent / "fixtures/results.xml"


def test_fixture_end_to_end_has_no_network_and_preserves_evidence(
    tmp_path, monkeypatch
):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network access is forbidden in this slice")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    first = asyncio.run(analyze_file(FIXTURE, tmp_path / "first", None, None))
    second = asyncio.run(analyze_file(FIXTURE, tmp_path / "second", None, None))
    assert first == second
    assert first.statistics.model_dump() == {
        "total": 4,
        "passed": 1,
        "failed": 1,
        "error": 1,
        "skipped": 1,
        "counting_unit": "testcase_records",
    }
    assert first.started_at.isoformat() == "2026-11-27T09:00:00+00:00"
    assert first.context.stand_id is None
    assert "context.stand_id" in first.missing_data
    assert first.metadata_provenance["run_id"] == "junit"
    reloaded = NormalizedRun.model_validate_json(
        (tmp_path / "first/normalized.json").read_text()
    )
    assert reloaded == first
    planned = json.loads((tmp_path / "first/plan.json").read_text())
    assert planned["external_operations"] == []
    assert len(planned["investigations"]) == 2
    assert all(
        item["duplicate_lookup_status"] == "not_performed"
        for item in planned["investigations"]
    )
    for index, item in enumerate(first.test_items):
        assert item.evidence_refs[0].testcase_index == index
        assert item.evidence_refs[0].artifact_sha256 == first.artifact_digest
    assert (tmp_path / "first/report.html").stat().st_mode & 0o777 == 0o600


def test_missing_naive_time_duplicates_and_metadata_conflicts():
    source = parse_junit(b"""<testsuite timestamp="2026-11-27T00:00:00" tests="1">
      <properties><property name="stand" value="observed"/></properties>
      <testcase name="same"/><testcase name="same"/>
    </testsuite>""")
    run = normalize(source, FileContext(stand_id="supplied"))
    assert run.context.stand_id is None
    assert run.metadata_provenance["stand_id"] == "conflict"
    assert run.statistics.total == 2
    assert run.started_at is None
    assert "started_at" in run.missing_data
    assert "attempt_semantics" in run.missing_data
    assert "junit.declared_tests" in run.data_conflicts
    assert len({case.item_key for case in run.test_items}) == 2


@pytest.mark.parametrize(
    "xml",
    [
        b"<testsuite>",
        b"<unknown/>",
        b'<testsuite><testcase name="x" time="NaN"/></testsuite>',
        b'<testsuite><testcase name="x" time="-1"/></testsuite>',
        b'<testsuite><testcase name="x"><error/><skipped/></testcase></testsuite>',
        b'<!DOCTYPE testsuite [<!ENTITY x SYSTEM "file:///etc/passwd">]><testsuite>&x;</testsuite>',
        b"<testsuite><unknown/></testsuite>",
        b'<testsuite><testcase name="x"><testcase name="nested"/></testcase></testsuite>',
        b'<testsuite><testcase name="x" status="notrun"/></testsuite>',
        b'<testsuite><testcase name="x"><rerunFailure/></testcase></testsuite>',
        b"<testsuite>" * 65 + b"</testsuite>" * 65,
    ],
)
def test_invalid_xml_is_explicitly_rejected(xml):
    with pytest.raises(Exception):
        parse_junit(xml)


@pytest.mark.parametrize(
    "content",
    [
        "publish_enabled: true",
        "unexpected: true",
        "max_xml_bytes: -1",
        "max_xml_bytes: 1\nmax_xml_bytes: 2",
        "!!python/object:builtins.object {}",
        "max_xml_bytes: '100'",
    ],
)
def test_invalid_settings_rejected_before_source_read(tmp_path, content):
    config = tmp_path / "settings.yaml"
    config.write_text(content)
    with pytest.raises(Exception):
        load_settings(config)
    assert (
        main(
            [
                "analyze",
                "--input",
                str(tmp_path / "missing.xml"),
                "--config",
                str(config),
                "--output",
                str(tmp_path / "out"),
            ]
        )
        == 1
    )
    assert not (tmp_path / "out").exists()


def test_context_rejects_invalid_sha_unknown_and_duplicate_keys(tmp_path):
    context = tmp_path / "context.json"
    for content in (
        '{"git_sha":"main"}',
        '{"unknown":1}',
        '{"run_id":"a","run_id":"b"}',
    ):
        context.write_text(content)
        with pytest.raises((ValidationError, InputError)):
            load_context(context)


def test_bounded_input_rejects_symlink_escape_and_nonregular_file(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    source = tmp_path / "outside.xml"
    source.write_bytes(b"12345")
    link = root / "link.xml"
    link.symlink_to(source)
    with pytest.raises(InputError):
        read_bounded(link, 10)
    with pytest.raises(InputError):
        read_bounded(source, 4)
    with pytest.raises((InputError, OSError)):
        read_bounded(root, 10)


def test_raw_secret_sentinels_and_paths_are_not_saved_or_logged(tmp_path, capsys):
    source = tmp_path / "results.xml"
    secret = "SYNTHETIC_SECRET_SENTINEL"
    source.write_text(f'''<testsuite><testcase name="{secret}" classname="/home/example/internal">
      <failure message="{secret}">{secret}</failure><system-out>{secret}</system-out>
    </testcase></testsuite>''')
    output = tmp_path / "out"
    assert main(["analyze", "--input", str(source), "--output", str(output)]) == 0
    for path in output.iterdir():
        assert secret not in path.read_text()
        assert "/home/" not in path.read_text()
    assert secret not in capsys.readouterr().out
    source.write_text(f"<broken {secret}")
    assert (
        main(["analyze", "--input", str(source), "--output", str(tmp_path / "invalid")])
        == 1
    )
    captured = capsys.readouterr()
    assert secret not in captured.err
    assert str(tmp_path) not in captured.err


def test_existing_output_and_source_remain_unchanged(tmp_path):
    output = tmp_path / "out"
    output.mkdir()
    marker = output / "keep"
    marker.write_text("original")
    before = FIXTURE.read_bytes()
    assert main(["analyze", "--input", str(FIXTURE), "--output", str(output)]) == 1
    assert marker.read_text() == "original"
    assert FIXTURE.read_bytes() == before


def test_no_failed_tests_do_not_create_investigations():
    run = normalize(
        parse_junit(b'<testsuite tests="1"><testcase name="x"/></testsuite>'),
        FileContext(),
    )
    assert plan(run, Settings()).investigations == ()


def test_cli_conflict_is_partial(tmp_path):
    source = tmp_path / "results.xml"
    source.write_text('<testsuite tests="99"><testcase name="x"/></testsuite>')
    assert (
        main(["analyze", "--input", str(source), "--output", str(tmp_path / "out")])
        == 2
    )
