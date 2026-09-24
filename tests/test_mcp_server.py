import asyncio
import re

import pytest
from typer.testing import CliRunner

import mcp_server
import mcp_server_cli

runner = CliRunner()


def test_long_running_greet_returns_expected_message(monkeypatch):
    async def fake_sleep(_seconds):
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    result = asyncio.run(mcp_server.long_running_greet("Alice"))

    assert result == "Hello, Alice!"


def test_time_tool_returns_formatted_message():
    result = mcp_server.time("Alice")

    assert result.startswith("Hello, Alice, the current time is ")
    assert re.search(r"\d{4}-\d{2}-\d{2}", result)


def test_mcp_lists_expected_tools():
    tools = asyncio.run(mcp_server.mcp.list_tools())
    tools_by_name = {tool.name: tool for tool in tools}

    assert {"long_running_greet", "time", "open_meteo_current_forecast"}.issubset(
        tools_by_name
    )
    assert tools_by_name["long_running_greet"].title == "Delayed greeting"
    assert tools_by_name["long_running_greet"].tags == {"async", "demo", "greeting"}
    assert tools_by_name["long_running_greet"].annotations.read_only_hint is True
    assert tools_by_name["long_running_greet"].annotations.destructive_hint is False
    assert tools_by_name["time"].annotations.idempotent_hint is False
    assert tools_by_name["open_meteo_current_forecast"].tags == {
        "external-api",
        "forecast",
        "weather",
    }
    assert (
        tools_by_name["open_meteo_current_forecast"].annotations.open_world_hint is True
    )


def test_open_meteo_current_forecast_returns_response_json(monkeypatch):
    response_data = {"current": {"temperature_2m": 21.5}}
    requests = []

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return response_data

    class FakeSession:
        def mount(self, _prefix, _adapter):
            return None

        def get(self, url, **kwargs):
            requests.append((url, kwargs))
            return FakeResponse()

    monkeypatch.setattr(mcp_server.requests, "Session", FakeSession)

    assert mcp_server.open_meteo_current_forecast(45.0, 9.0) == response_data
    assert "latitude=45.0&longitude=9.0" in requests[0][0]
    assert requests[0][1] == {
        "verify": mcp_server.settings.HTTP_REQUEST_TLS_VERIFY,
        "timeout": mcp_server.settings.HTTP_REQUEST_TIMEOUT,
    }


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [(-90.1, 0), (90.1, 0), (0, -180.1), (0, 180.1)],
)
def test_open_meteo_current_forecast_rejects_invalid_coordinates(latitude, longitude):
    with pytest.raises(ValueError, match="Latitude must be between"):
        mcp_server.open_meteo_current_forecast(latitude, longitude)


def test_server_list_mcp_tools_prints_tool_metadata(monkeypatch, capsys):
    class FakeTool:
        def __init__(self):
            self.name = "example"
            self.title = "Example"
            self.description = "Example tool"
            self.tags = {"example", "test"}
            self.annotations = {"readOnlyHint": True}
            self.parameters = {"type": "object"}
            self.output_schema = {"type": "string"}

    async def fake_list_tools():
        return [FakeTool()]

    monkeypatch.setattr(mcp_server.mcp, "list_tools", fake_list_tools)

    asyncio.run(mcp_server.list_mcp_tools())

    output = capsys.readouterr().out
    assert "Tool: example" in output
    assert "Title: Example" in output
    assert "Description: Example tool" in output
    assert "Tags: example, test" in output
    assert "Annotations: {'readOnlyHint': True}" in output
    assert "Parameters:" in output
    assert "Output Schema:" in output


def test_run_command_uses_stdio_by_default(monkeypatch):
    calls = {}

    def fake_run(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs

    monkeypatch.setattr(mcp_server.mcp, "run", fake_run)

    result = runner.invoke(mcp_server.mcp_typer, ["run"])

    assert result.exit_code == 0
    assert calls == {"args": (), "kwargs": {}}


def test_run_command_uses_http_transport_when_requested(monkeypatch):
    calls = {}

    def fake_run(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs

    monkeypatch.setattr(mcp_server.mcp, "run", fake_run)

    result = runner.invoke(
        mcp_server.mcp_typer, ["run", "--transport", "http", "--port", "9001"]
    )

    assert result.exit_code == 0
    assert calls == {
        "args": (),
        "kwargs": {"transport": "streamable-http", "port": 9001},
    }


def test_cli_list_tools_prints_tool_metadata(monkeypatch, capsys):
    class FakeTool:
        def __init__(self):
            self.name = "example"
            self.title = "Example"
            self.description = "Example tool"
            self.tags = {"example", "test"}
            self.annotations = {"readOnlyHint": True}
            self.parameters = {"type": "object"}
            self.output_schema = {"type": "string"}

    class FakeMcp:
        async def list_tools(self):
            return [FakeTool()]

    monkeypatch.setattr(mcp_server, "mcp", FakeMcp())

    asyncio.run(mcp_server_cli.list_mcp_tools())

    output = capsys.readouterr().out
    assert "Tool: example" in output
    assert "Title: Example" in output
    assert "Description: Example tool" in output
    assert "Tags: example, test" in output
    assert "Annotations: {'readOnlyHint': True}" in output
    assert "Parameters:" in output
    assert "Output Schema:" in output


def test_cli_list_tools_command(monkeypatch):
    calls = []

    def fake_run(coroutine):
        calls.append(coroutine)
        coroutine.close()

    monkeypatch.setattr(mcp_server_cli.asyncio, "run", fake_run)

    result = runner.invoke(mcp_server_cli.mcp_typer, ["list-tools"])

    assert result.exit_code == 0
    assert len(calls) == 1
