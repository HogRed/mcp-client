import sys
from contextlib import AsyncExitStack
from typing import Any, Awaitable, Callable, ClassVar
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_client import chat
from mcp_client.handlers import OpenAIQueryHandler

class MCPClient:
    """MCP client to interact with MCP server.

    Usage:
        async with MCPClient(server_path) as client:
            # Call client methods here...
    """

    client_session: ClassVar[ClientSession]

    def __init__(self, server_path: str):
        ''' Initialize MCPClient with the server path.
            Also, sets up an AsyncExitStack for resource management.'''
        self.server_path = server_path
        self.exit_stack = AsyncExitStack()

    async def __aenter__(self) -> "MCPClient":
        ''' Save the class type and establish a connection to the MCP server.
            Store the client session in a class variable for shared access.'''
        cls = type(self)
        cls.client_session = await self._connect_to_server()
        return self

    async def __aexit__(self, *_) -> None:
        ''' Method that will be called once the context is exited.
            Closes the exit stack to clean up resources.'''
        await self.exit_stack.aclose()

    async def _connect_to_server(self) -> ClientSession:
        '''Establish a stdio connection to the MCP server script.

        On Windows we invoke the Python interpreter directly.
        Returns an initialized ClientSession or raises RuntimeError with details.
        '''
        server_path = Path(self.server_path).resolve()
        if not server_path.exists():
            raise RuntimeError(f"Server script not found: {server_path}")

        # Build platform-appropriate command.
        if sys.platform == "win32":
            command = sys.executable # Use Python executable directly on Windows
            args = [str(server_path)] # Pass server script as argument
        else:
            # On POSIX we can still just exec Python directly; avoids shell.
            command = sys.executable
            args = [str(server_path)]

        try:
            # Establish stdio client connection.
            # passes the command and args to start the server process
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(
                    server=StdioServerParameters(
                        command=command,
                        args=args,
                        env=None,
                    )
                )
            )
            # Create and initialize the ClientSession.
            client_session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await client_session.initialize() # Ensure the session is initialized
            return client_session # Return the initialized session
        except Exception as e:  # if no connection could be made
            raise RuntimeError(f"Failed to connect to server: {e}") from e

    async def list_all_members(self) -> None:
        """List all available tools, prompts, and resources."""
        print("MCP Server Members")
        print("=" * 50)

        # Define sections to list
        sections = {
            "tools": self.client_session.list_tools,
            "prompts": self.client_session.list_prompts,
            "resources": self.client_session.list_resources,
        }
        # Iterate and list each section
        for section, listing_method in sections.items():
            await self._list_section(section, listing_method)

        print("\n" + "=" * 50)

    async def _list_section(self, section: str, list_method: Callable[[], Awaitable[Any]]) -> None:
        '''Take a section name and list_method object and dynamically call the 
            method and retrieve the members or items in the section. 
            Then, print the section title, the number of items, and the 
            details for each one, including its name and description.'''
        try:
            items = getattr(await list_method(), section)
            if items:
                print(f"\n{section.upper()} ({len(items)}):")
                print("-" * 30)
                # Print each item's name and description
                for item in items:
                    description = item.description or "No description"
                    print(f" > {item.name} - {description}")
            else:
                # No items found in this section
                print(f"\n{section.upper()}: None available")
        except Exception as e: # handle errors gracefully
            print(f"\n{section.upper()}: Error - {e}")

    async def run_chat(self) -> None:
        """Start interactive chat with MCP server using OpenAI."""
       
        try:
            handler = OpenAIQueryHandler(self.client_session)
            await chat.run_chat(handler)

        # Handle connection errors gracefully
        except RuntimeError as e:
            print(e)