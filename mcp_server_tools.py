import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from mcp_server import mcp
from settings import settings


@mcp.tool(
    title="Sort Numbers",
    description="Sort a list of numbers in ascending order.",
    tags={"demo", "sorting", "numbers"},
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def sort_numbers(numbers: list[int]) -> list[int]:
    """
    Sort a list of numbers in ascending order.

    Args:
        numbers (list[int]): A list of numbers to be sorted.

    Returns:
        list[int]: The sorted list of numbers in ascending order.
    """
    return sorted(numbers)


@mcp.tool(
    title="Current GPS Position",
    description="Return the current GPS position of the server.",
    tags={"demo", "gps", "position"},
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def get_current_gps_position() -> dict:
    """
    Get the current GPS position of the server.

    Returns:
        dict: A dictionary containing the latitude and longitude of the server's current GPS position.
    """
    # For demonstration purposes, we return a fixed GPS position.
    # In a real implementation, you would retrieve the actual GPS position from a GPS device or service.
    return {"latitude": 37.7749, "longitude": -122.4194}  # Example: San Francisco, CA


@mcp.tool(
    title="Open-Meteo current forecast",
    description="Get the current temperature and wind speed for geographic coordinates.",
    tags={"weather", "forecast", "external-api"},
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
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
