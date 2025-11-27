import json
import os

from mcp import ClientSession
from openai import OpenAI

MODEL = "gpt-4o-mini" # OpenAI model to use
MAX_TOKENS = 1000 # Max tokens for response

class OpenAIQueryHandler:
    """Handle OpenAI API interaction and MCP tool execution."""

    # Initialize with ClientSession and OpenAI API key
    def __init__(self, client_session: ClientSession):
        self.client_session = client_session
        if not (api_key := os.getenv("OPENAI_API_KEY")):
            raise RuntimeError(
                "Error: OPENAI_API_KEY environment variable not set",
            )
        self.openai = OpenAI(api_key=api_key)
    
    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available MCP tools."""
        # Get initial model's response and decision on tool calls
        messages = [{"role": "user", "content": query}]
        initial_response = self.openai.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
            tools=await self._get_tools(),
        )

        # Grab the initial message and create empty list
        # for accumulating response parts
        current_message = initial_response.choices[0].message
        result_parts = []

        # Add initial content if present
        if current_message.content:
            result_parts.append(current_message.content)

        # Handle tool usage if present
        if tool_calls := current_message.tool_calls:
            # Accumulate messages for tool execution
            messages.append(
                {
                    "role": "assistant",
                    "content": current_message.content or "",
                    "tool_calls": tool_calls,
                }
            )

            # Execute tools
            for tool_call in tool_calls:
                tool_result = await self._execute_tool(tool_call)
                result_parts.append(tool_result["log"])
                messages.append(tool_result["message"])

            # Get final model's response after tool execution
            final_response = self.openai.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=messages,
            )

            # Append final content if present
            if content := final_response.choices[0].message.content:
                result_parts.append(content)

        # Return the combined response
        return "Assistant: " + "\n".join(result_parts)
    
    async def _get_tools(self) -> list:
        """Get MCP tools formatted for OpenAI."""
        # Fetch available tools from MCP server
        response = await self.client_session.list_tools()

        # Format tools for OpenAI using list comprehension
        # turns tools into JSON ready schema
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "No description",
                    "parameters": getattr(
                        tool,
                        "inputSchema",
                        {"type": "object", "properties": {}},
                    ),
                },
            }
            for tool in response.tools
        ]
    
    async def _execute_tool(self, tool_call) -> dict:
        """Execute an MCP tool call and return formatted result."""

        # Extract tool name and arguments
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments or "{}")

        try:
            # Call the tool via MCP client session
            result = await self.client_session.call_tool(
                tool_name, tool_args,
            )

            # Extract content from result
            content = result.content[0].text if result.content else ""
            
            # Create log entry
            log = f"[Used {tool_name}({tool_args})]"

        # Handle any exceptions during tool execution
        except Exception as e:
            content = f"Error: {e}"
            log = f"[{content}]"

        # Return log and message structure
        # once again, relying on JSON format
        return {
            "log": log,
            "message": {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": content,
            },
        }