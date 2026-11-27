"""Synthetic dependency probes only; these are not analyzer acceptance tests."""

import asyncio
import importlib
import json
import sys
from pathlib import Path

import pytest
import yaml
from bs4 import BeautifulSoup
from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import fromstring
from jinja2 import Environment, StrictUndefined, UndefinedError
from openai import APIConnectionError, AsyncOpenAI
from pydantic import BaseModel, ConfigDict, ValidationError


class ProbeResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    evidence_ids: list[str]


@pytest.fixture(params=["httpx", "httpx2"])
def http_backend(request):
    return importlib.import_module(request.param)


def test_structure_and_evidence_are_separate():
    result = ProbeResult.model_validate_json('{"evidence_ids":["invented"]}')
    assert not set(result.evidence_ids) <= {"fixture-evidence"}
    with pytest.raises(ValidationError):
        ProbeResult.model_validate({"evidence_ids": "invalid"})
    with pytest.raises(ValidationError):
        ProbeResult.model_validate({"evidence_ids": [], "action": "publish"})


def test_xml_entities_rejected():
    with pytest.raises(DefusedXmlException):
        fromstring('<!DOCTYPE x [<!ENTITY e "expanded">]><x>&e;</x>')
    assert fromstring('<testsuite tests="1"/>').attrib["tests"] == "1"


def test_html_is_parsed_as_data():
    soup = BeautifulSoup("<p>failed</p><script>raise Error()</script>", "html.parser")
    assert soup.p.text == "failed"


def test_yaml_does_not_construct_objects():
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load('!!python/object/apply:os.system ["false"]')


def test_template_requires_values():
    with pytest.raises(UndefinedError):
        Environment(undefined=StrictUndefined).from_string("{{ missing }}").render()


@pytest.mark.asyncio
async def test_sdk_json_mode_against_in_memory_http(http_backend):
    httpx = http_backend
    requests = []

    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        return httpx.Response(
            200,
            json={
                "id": "fixture",
                "object": "chat.completion",
                "created": 0,
                "model": "fixture-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "not valid JSON"},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        async with AsyncOpenAI(
            api_key="synthetic-placeholder",
            base_url="https://fixture.invalid/v1",
            http_client=http,
            max_retries=0,
        ) as client:
            response = await client.chat.completions.create(
                model="fixture-model",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": "Return JSON"}],
            )
    assert requests[0]["response_format"] == {"type": "json_object"}
    assert "tools" not in requests[0]
    with pytest.raises(ValidationError):
        ProbeResult.model_validate_json(response.choices[0].message.content)


@pytest.mark.asyncio
async def test_sdk_connection_error_has_no_implicit_retry(http_backend):
    httpx = http_backend
    calls = 0

    def fail(request):
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("synthetic outage", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(fail)) as http:
        async with AsyncOpenAI(
            api_key="synthetic-placeholder",
            base_url="https://fixture.invalid/v1",
            http_client=http,
            max_retries=0,
        ) as client:
            with pytest.raises(APIConnectionError):
                await client.chat.completions.create(model="fixture", messages=[])
    assert calls == 1


@pytest.mark.asyncio
async def test_rest_stream_status_and_timeout_contract(http_backend):
    httpx = http_backend

    def respond(request):
        assert request.url.params["page"] == "2"
        assert request.headers["authorization"] == "Bearer synthetic"
        assert request.extensions["timeout"]["read"] == 3.0
        return httpx.Response(503, content=b"synthetic-unavailable")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(respond),
        timeout=httpx.Timeout(3.0),
        trust_env=False,
        follow_redirects=False,
    ) as client:
        async with client.stream(
            "GET",
            "https://fixture.invalid/results",
            params={"page": "2"},
            headers={"Authorization": "Bearer synthetic"},
        ) as response:
            assert await response.aread() == b"synthetic-unavailable"
            with pytest.raises(httpx.HTTPStatusError):
                response.raise_for_status()


@pytest.mark.asyncio
async def test_bounded_async_work():
    semaphore = asyncio.Semaphore(2)
    active = peak = 0

    async def work():
        nonlocal active, peak
        async with semaphore:
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0)
            active -= 1

    await asyncio.gather(*(work() for _ in range(10)))
    assert peak == 2


@pytest.mark.asyncio
async def test_mcp_stdio_initialize_list_call():
    from mcp import ClientSession, StdioServerParameters, stdio_client

    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).with_name("mcp_fixture.py"))],
    )
    async with asyncio.timeout(15):
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                initialized = await session.initialize()
                assert initialized.server_info.name == "phase0-fixture"
                tools = await session.list_tools()
                assert [tool.name for tool in tools.tools] == ["read_fixture"]
                result = await session.call_tool("read_fixture", {})
                assert not result.is_error
                assert any(
                    getattr(content, "text", None) == "fixture-evidence"
                    for content in result.content
                )
