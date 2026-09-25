import datetime
import json

from fastmcp import FastMCP

mcp = FastMCP("Resources")


@mcp.resource(
    "resource://greeting",
    name="Greeting",
    description="Return a greeting after the configured simulated delay.",
)
def get_greeting() -> str:
    """Provides a simple greeting message."""
    return "Hello from FastMCP Resources!"


@mcp.resource(
    "resource://config",
    name="Application configuration",
    description="Read the current application theme, version, and enabled features.",
)
def get_config() -> str:
    """Provides application configuration as JSON."""
    return json.dumps(
        {
            "theme": "dark",
            "version": "1.2.0",
            "features": ["tools", "resources"],
        }
    )


@mcp.resource(
    "resource://time",
    name="Current UTC time",
    description="Return the current UTC time.",
)
def get_current_time() -> str:
    """Provides the current UTC time."""
    now = datetime.datetime.now(tz=datetime.UTC)
    return f"RESOURCE: The current UTC time is {now}."
