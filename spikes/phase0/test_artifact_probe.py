"""Adversarial checks for the inspection experiment, not production contracts."""

import pytest
from defusedxml.ElementTree import fromstring

from inspect_artifacts import phase_matches, read_bounded


def test_phase_is_preserved_and_requires_independent_xml_hint():
    case = fromstring(
        '<testcase classname="tests.test_probe.Example" name="test_a"><error message="failed on setup"/></testcase>'
    )
    items = [
        {"testId": "tests/test_probe.py::Example::test_a::setup", "result": "Error"}
    ]
    assert phase_matches(case, items) == [(items[0]["testId"], "setup")]
    case.find("error").set("message", "unspecified error")
    assert phase_matches(case, items) == []


def test_duplicate_phase_candidates_remain_ambiguous():
    case = fromstring(
        '<testcase classname="tests.test_probe" name="test_a"><error message="failed on setup"/></testcase>'
    )
    item = {"testId": "tests/test_probe.py::test_a::setup", "result": "Error"}
    assert len(phase_matches(case, [item, item])) == 2


def test_inspection_rejects_oversize_and_outside_symlink(tmp_path):
    root = tmp_path / "artifacts"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.write_bytes(b"12345")
    link = root / "link"
    link.symlink_to(outside)
    with pytest.raises(ValueError, match="outside"):
        read_bounded(link, root, 10)
    inside = root / "large"
    inside.write_bytes(b"12345")
    with pytest.raises(ValueError, match="size budget"):
        read_bounded(inside, root, 4)
