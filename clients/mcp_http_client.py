import asyncio
import json

from fastmcp import Client


async def call_tool(name: str):
    mcp_client = Client("http://localhost:8000/mcp")

    async with mcp_client:
        result = await mcp_client.call_tool("time", {"name": name})
        print(json.dumps(result.structured_content, indent=4))

        long_result = await mcp_client.call_tool("long_running_greet", {"name": name})
        print(json.dumps(long_result.structured_content, indent=4))


if __name__ == "__main__":
    asyncio.run(call_tool("Ford"))
