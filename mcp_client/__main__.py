import asyncio

from mcp_client.cli import parse_args
from mcp_client.mcp_client import MCPClient

async def main() -> None:
    """Run the MCP client with the specified options."""
    args = parse_args() # Parse command line arguments
    # Check if the server script exists at the specified path
    if not args.server_path.exists():
        print(f"Error: Server script '{args.server_path}' not found")
        return
    # if path exists, create MCPClient and interact with server
    try:
        async with MCPClient(str(args.server_path)) as client:
            
            # checks whether the user provided the --members option 
            if args.members:
                await client.list_all_members()
            
            # checks whether the user provided the --chat option
            elif args.chat:
                await client.run_chat()

    except RuntimeError as e: # catch connection errors
        print(e)

def cli_main():
    """Entry point for the mcp-client CLI app.
       Needed because setuptools build system 
       can't handle async functions"""
    
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())