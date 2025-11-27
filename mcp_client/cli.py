import argparse # for command line argument parsing
import pathlib # for filesystem path handling

def parse_args():
    """Parse command line arguments and return parsed args."""
    parser = argparse.ArgumentParser(description="A minimal MCP client")
    parser.add_argument(
        "server_path", # positional argument for server script path
        type=pathlib.Path, # converts the user-provided path string into a Path object
        help="path to the MCP server script", # e.g., ./mcp_server/mcp_server.py
    )
    # Mutually exclusive group for listing members
    group = parser.add_mutually_exclusive_group(required=True)
    # Add --members flag to list server members
    group.add_argument(
        "--members",
        action="store_true", # stored Boolean value indicating if flag is present
        help="list the MCP server's tools, prompts, and resources", # help text
    )

    group.add_argument(
        # Add --chat flag to start AI-powered chat
        "--chat",
        action="store_true",
        help="start an AI-powered chat with MCP server integration",
    )

    return parser.parse_args()