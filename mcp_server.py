import asyncio
import datetime
import json

import requests
from fastmcp import FastMCP
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from mcp_server_cli import mcp_typer
from settings import settings

mcp = FastMCP("My Server")


@mcp.tool(description="Just_say_hello")
async def long_running_greet(name: str) -> str:
    await asyncio.sleep(
        settings.LONG_RUNNING_TASK_FAKE_DELAY
    )  # Simulate a long-running task
    return f"Hello, {name}!"


@mcp.tool(description="current time")
def time(name: str) -> str:
    now = datetime.datetime.now(tz=datetime.UTC)
    return f"Hello, {name}, the current time is {now}!"


@mcp.tool(description="Open-Meteo Current Forecast")
def open_meteo_current_forecast(latitude: float, longitude: float) -> dict:
    """
    Get the current weather forecast for a given latitude and longitude using the Open-Meteo API.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

    Returns:
        dict: A dictionary containing the current weather forecast data.
    """

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError(
            "Latitude must be between -90 and 90, and longitude must be between -180 and 180."
        )

    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    req = requests.Session()
    req.mount("https://", adapter)
    req.mount("http://", adapter)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = req.get(
        url,
        verify=settings.HTTP_REQUEST_TLS_VERIFY,
        timeout=settings.HTTP_REQUEST_TIMEOUT,
    )
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()


async def list_mcp_tools():
    tools = await mcp.list_tools()
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Parameters: {json.dumps(tool.parameters, indent=4)}")
        print(f"Output Schema: {json.dumps(tool.output_schema, indent=4)}")
        print("-" * 40)


if __name__ == "__main__":  # pragma: no cover
    mcp_typer()
