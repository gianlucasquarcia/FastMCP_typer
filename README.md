# FastMCP Test
![Python](https://img.shields.io/badge/python-3.12%20+-blue.svg)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

A small FastMCP server example with a Typer CLI wrapper and both an HTTP client and a stdio client example.

## Features

- Exposes a `long_running_greet` MCP tool that simulates a slow async task
- Exposes a `time` MCP tool that returns the current UTC time
- Includes a Typer CLI for starting the server with stdio or HTTP transport
- Uses environment-based settings for the default port and transport
- Includes an HTTP client and a stdio client example for testing and local integration

## Project layout

- `mcp_server.py` — FastMCP server and Typer CLI entry point
- `mcp_http_client.py` — HTTP MCP client that connects to the running server
- `mcp_stdio_client.py` — stdio client that spawns the server as a subprocess
- `settings.py` — environment-backed configuration
- `tests/test_mcp_server.py` — tests for tool behavior and CLI commands

## Setup

Install dependencies with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

The project metadata in `pyproject.toml` declares the dependencies:

- `fastmcp`
- `typer`
- `pytest`

## Using uv

Run the server:

```bash
uv run mcp_server.py run
uv run mcp_server.py run --transport streamable-http --port 8000
```

Run a client:

```bash
uv run mcp_http_client.py
uv run mcp_stdio_client.py
```

Run tests:

```bash
uv run pytest tests/test_mcp_server.py -q
```

Add a new dependency (updates `pyproject.toml` and `uv.lock`):

```bash
uv add <package>
```

## Run the server

Run in stdio mode (default):

```bash
uv run mcp_server.py run
```

Run in HTTP mode:

```bash
uv run mcp_server.py run --transport streamable-http --port 8000
```

The CLI uses these defaults:

- `transport = "stdio"`
- `port = 8000`

Those defaults come from environment variables when present:

- `MCP_SERVER_DEFAULT_PORT`
- `MCP_SERVER_DEFAULT_TRANSPORT`

## List registered tools

```bash
uv run mcp_server.py list-tools
```

This calls the Typer `list_tools` command and prints the registered MCP tools and their schema metadata.

## Start the HTTP client

Start the server in HTTP mode first:

```bash
uv run mcp_server.py run --transport streamable-http --port 8000
```

Then run the client:

```bash
uv run mcp_http_client.py
```

The client connects to:

```text
http://localhost:8000/mcp
```

## Start the stdio client

This client launches the server as a subprocess and communicates with it over stdin/stdout:

```bash
uv run mcp_stdio_client.py
```

The script starts `mcp_server.py run` using the current Python interpreter and then calls the `time` tool over stdio transport.

## Run tests

```bash
uv run pytest tests/test_mcp_server.py -q
```

## FastMCP CLI

`fastmcp` also ships its own CLI (installed as part of the `fastmcp` dependency), which can inspect and run the server object directly without going through the project's Typer wrapper. Reference the server as `mcp_server.py:mcp` (module file plus the exported `FastMCP` instance).

Inspect the server (tools, prompts, resources, versions):

```bash
uv run fastmcp inspect mcp_server.py:mcp
```

Run the server directly with the FastMCP CLI:

```bash
uv run fastmcp run mcp_server.py:mcp --transport stdio
uv run fastmcp run mcp_server.py:mcp --transport http --port 8000
```

Display FastMCP version and environment info:

```bash
uv run fastmcp version
```

See `uv run fastmcp --help` for the full command list, including `call`, `dev`, and `install`.

## Notes

- `stdio` is used for local process-to-process MCP communication.
- `streamable-http` is used for HTTP-based MCP transport.
- The async tool (`long_running_greet`) works without wrapping `mcp.run()` in `asyncio.run(...)`.
