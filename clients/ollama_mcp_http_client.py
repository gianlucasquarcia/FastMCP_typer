"""Bridge between a local Ollama model and this project's FastMCP server (HTTP transport).

Connects to an already-running FastMCP server over streamable-http (mirroring
`mcp_http_client.py`), exposes its tools and resources to an Ollama model, and
forwards tool calls and requested resource reads to the MCP server.

Usage:
    uv run mcp_server.py run --transport streamable-http --port 8000  # in one terminal
    uv run clients/ollama_mcp_http_client.py "What time is it?"       # in another

Requires a running Ollama daemon (``ollama serve``) with a tool-calling
capable model already pulled, e.g. ``ollama pull llama3.1``.
"""

import asyncio
import json
import sys
from typing import Any

import ollama
from fastmcp import Client
from fastmcp.exceptions import ToolError
from mcp.shared.exceptions import MCPError
from mcp_types import Resource, ResourceTemplate
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


def to_ollama_resource_tool(
    resources: list[Resource], templates: list[ResourceTemplate]
) -> dict:
    """Expose MCP resource reads as an Ollama function call."""
    resource_details = [
        {
            "uri": str(resource.uri),
            "name": resource.name,
            "description": resource.description or "",
        }
        for resource in resources
    ]
    template_details = [
        {
            "uri_template": template.uri_template,
            "name": template.name,
            "description": template.description or "",
        }
        for template in templates
    ]
    description = (
        "Read a resource exposed by the MCP server. Use a URI from the resource "
        "catalog, or construct a URI that matches a resource template. "
        f"Resources: {json.dumps(resource_details)}. "
        f"Resource templates: {json.dumps(template_details)}."
    )
    return {
        "type": "function",
        "function": {
            "name": "read_mcp_resource",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": "The MCP resource URI to read.",
                    }
                },
                "required": ["uri"],
            },
        },
    }


def normalize_tool_arguments(input_schema: dict | None, arguments: dict) -> dict:
    """Coerce stringified array/object arguments back to their JSON types.

    Local Ollama models occasionally emit array- or object-typed tool
    arguments as their JSON-encoded string form (e.g. ``"[1, 2, 3]"``
    instead of ``[1, 2, 3]``). Parse those back to native Python values so
    the MCP server's argument validation does not reject the call.
    """
    if not input_schema:
        return arguments

    properties = input_schema.get("properties", {})
    normalized = dict(arguments)
    for key, value in arguments.items():
        if not isinstance(value, str):
            continue
        expected_type = properties.get(key, {}).get("type")
        if expected_type not in ("array", "object"):
            continue
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(parsed, (list, dict)):
            normalized[key] = parsed
    return normalized


def resource_content_to_text(resource_contents: list[Any]) -> str:
    """Serialize text and binary MCP resource content for an Ollama tool result."""
    contents = []
    for content in resource_contents:
        if hasattr(content, "text"):
            contents.append(
                {
                    "uri": str(content.uri),
                    "mime_type": content.mime_type,
                    "text": content.text,
                }
            )
        else:
            contents.append(
                {
                    "uri": str(content.uri),
                    "mime_type": content.mime_type,
                    "blob": content.blob,
                }
            )
    return json.dumps(contents)


async def run(prompt: str) -> None:
    mcp_client = Client(SERVER_URL)

    async with mcp_client:
        tools_result, resources_result, templates_result = await asyncio.gather(
            mcp_client.list_tools(),
            mcp_client.list_resources(),
            mcp_client.list_resource_templates(),
        )
        # tools = tools_result.tools
        ollama_tools = [to_ollama_tool(tool) for tool in tools_result]
        ollama_tools.append(to_ollama_resource_tool(resources_result, templates_result))
        input_schemas_by_name = {tool.name: tool.input_schema for tool in tools_result}

        messages = [
            {
                "role": "system",
                "content": (
                    "You can read MCP resources with the read_mcp_resource tool when "
                    "their catalog metadata is relevant to the user's request."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        response = ollama.chat(
            model=LOCAL_OLLAMA_MODEL, messages=messages, tools=ollama_tools
        )
        messages.append(response.message)

        while response.message.tool_calls:
            for call in response.message.tool_calls:
                print(
                    f"-> calling tool '{call.function.name}' with {call.function.arguments}"
                )
                try:
                    if call.function.name == "read_mcp_resource":
                        resource_result = await mcp_client.read_resource(
                            str(call.function.arguments["uri"])
                        )
                        content = resource_content_to_text(resource_result)
                    else:
                        call_arguments = normalize_tool_arguments(
                            input_schemas_by_name.get(call.function.name),
                            dict(call.function.arguments),
                        )
                        result = await mcp_client.call_tool(
                            call.function.name, call_arguments
                        )
                        content = str(result.structured_content)
                except (ToolError, MCPError) as error:
                    content = f"Error calling '{call.function.name}': {error}"
                    print(content)
                messages.append(
                    {
                        "role": "tool",
                        "content": content,
                        "tool_name": call.function.name,
                    }
                )

            response = ollama.chat(
                model=LOCAL_OLLAMA_MODEL, messages=messages, tools=ollama_tools
            )
            messages.append(response.message)

        print(response.message.content)


if __name__ == "__main__":
    user_prompt = (
        " ".join(sys.argv[1:])
        or "What time is it? Where are you? Say hello. Then Sort this list of numbers: 5, 2, 9, 1, 5, 6."
    )
    asyncio.run(run(user_prompt))
