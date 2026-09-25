import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = ROOT / "mcp_server.py"


async def main() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH), "run"],
        cwd=str(ROOT),
    )

    async with Client(server) as client:
        tools_result = await client.list_tools()
        print("Available tools:")
        for tool in tools_result.tools:
            print(f"- {tool.name}: {tool.description}")

        print("\nCalling tool 'time'...")
        result = await client.call_tool("time", {"name": "Alice"})
        print(result.structured_content)

        content_greeting = await client.read_resource("resource://greeting")
        print(content_greeting.contents[0].text)

        content_config = await client.read_resource("resource://config")
        print(content_config.contents[0].text)

        time_resource = await client.read_resource("resource://time")
        print(time_resource.contents[0].text)


if __name__ == "__main__":
    asyncio.run(main())
