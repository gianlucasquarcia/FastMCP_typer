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


if __name__ == "__main__":
    asyncio.run(main())
