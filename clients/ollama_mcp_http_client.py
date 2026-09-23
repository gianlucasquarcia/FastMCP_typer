"""Bridge between a local Ollama model and this project's FastMCP server (HTTP transport).

Connects to an already-running FastMCP server over streamable-http (mirroring
`mcp_http_client.py`), exposes its tools to an Ollama model via the standard
OpenAI-style `tools` chat parameter, and executes any tool calls the model
requests by forwarding them to the MCP server.

Usage:
    uv run mcp_server.py run --transport streamable-http --port 8000  # in one terminal
    uv run clients/ollama_mcp_http_client.py "What time is it?"       # in another

Requires a running Ollama daemon (``ollama serve``) with a tool-calling
capable model already pulled, e.g. ``ollama pull llama3.1``.
"""

import asyncio
import sys

import ollama
from fastmcp import Client
from mcp_types import Tool as MCPTool

SERVER_URL = "http://localhost:8000/mcp"
LOCAL_OLLAMA_MODEL = "llama3.1"  # Ollama model to use for tool calls


def to_ollama_tool(tool: MCPTool) -> dict:
    """Convert an MCP tool definition into the tool schema Ollama expects."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


async def run(prompt: str) -> None:
    mcp_client = Client(SERVER_URL)

    async with mcp_client:
        tools = await mcp_client.list_tools()
        ollama_tools = [to_ollama_tool(tool) for tool in tools]

        messages = [{"role": "user", "content": prompt}]

        response = ollama.chat(
            model=LOCAL_OLLAMA_MODEL, messages=messages, tools=ollama_tools
        )
        messages.append(response.message)

        while response.message.tool_calls:
            for call in response.message.tool_calls:
                print(
                    f"-> calling tool '{call.function.name}' with {call.function.arguments}"
                )
                result = await mcp_client.call_tool(
                    call.function.name, dict(call.function.arguments)
                )
                messages.append(
                    {
                        "role": "tool",
                        "content": str(result.structured_content),
                        "tool_name": call.function.name,
                    }
                )

            response = ollama.chat(
                model=LOCAL_OLLAMA_MODEL, messages=messages, tools=ollama_tools
            )
            messages.append(response.message)

        print(response.message.content)


if __name__ == "__main__":
    user_prompt = " ".join(sys.argv[1:]) or "What time is it?"
    asyncio.run(run(user_prompt))
