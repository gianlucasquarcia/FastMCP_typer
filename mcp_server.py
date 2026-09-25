from fastmcp import FastMCP

from mcp_server_cli import mcp_typer

mcp = FastMCP("My Server")


if __name__ == "__main__":  # pragma: no cover
    mcp_typer()
