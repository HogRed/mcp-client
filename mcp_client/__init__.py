"""mcp_server.mcp_client package.

Public API for interacting with an MCP server via the `MCPClient` class.

Typical usage:
    from mcp_server.mcp_client import MCPClient
    async with MCPClient(server_path) as client:
        ...

This module re-exports the primary client class and defines a simple factory
for convenience. Adjust `__all__` as the public surface grows.
"""

from .mcp_client import MCPClient

__all__ = ["MCPClient", "create_client"]

__version__ = "0.1.0"


def create_client(server_path: str) -> MCPClient:
    """Return a new `MCPClient` instance.

    This small helper provides a semantic factory in case you later want to
    inject configuration, logging, or dependency management.
    """
    return MCPClient(server_path)
