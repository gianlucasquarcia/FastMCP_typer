# FastMCP Test

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

Create a virtual environment and install project dependencies:

```bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

The project metadata in `pyproject.toml` declares the dependencies:

- `fastmcp`
- `typer`
- `pytest`

## Run the server

Run in stdio mode (default):

```bash
python mcp_server.py run
```

Run in HTTP mode:

```bash
python mcp_server.py run --transport streamable-http --port 8000
```

The CLI uses these defaults:

- `transport = "stdio"`
- `port = 8000`

Those defaults come from environment variables when present:

- `MCP_SERVER_DEFAULT_PORT`
- `MCP_SERVER_DEFAULT_TRANSPORT`

## List registered tools

```bash
python mcp_server.py list-tools
```

This calls the Typer `list_tools` command and prints the registered MCP tools and their schema metadata.

## Start the HTTP client

Start the server in HTTP mode first:

```bash
python mcp_server.py run --transport streamable-http --port 8000
```

Then run the client:

```bash
python mcp_http_client.py
```

The client connects to:

```text
http://localhost:8000/mcp
```

## Start the stdio client

This client launches the server as a subprocess and communicates with it over stdin/stdout:

```bash
python mcp_stdio_client.py
```

The script starts `mcp_server.py run` using the current Python interpreter and then calls the `time` tool over stdio transport.

## Run tests

```bash
python -m pytest tests/test_mcp_server.py -q
```

## Notes

- `stdio` is used for local process-to-process MCP communication.
- `streamable-http` is used for HTTP-based MCP transport.
- The async tool (`long_running_greet`) works without wrapping `mcp.run()` in `asyncio.run(...)`.
