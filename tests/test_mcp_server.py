import asyncio
import re

from typer.testing import CliRunner

import mcp_server

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
    names = {tool.name for tool in tools}

    assert {"long_running_greet", "time"}.issubset(names)


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
