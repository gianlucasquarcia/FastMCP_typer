from fastmcp import FastMCP

from mcp_server_cli import mcp_typer

mcp = FastMCP("My Server")

# Import after `mcp` is defined so their @mcp.tool/@mcp.resource decorators
# register against this server instance (imports placed at module level
# would create a circular import, since these modules import `mcp` back
# from this file).
import mcp_server_resources  # noqa: F401
import mcp_server_tools  # noqa: F401

if __name__ == "__main__":  # pragma: no cover
    mcp_typer()
