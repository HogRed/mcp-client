# MCP Client

A minimal, cross-platform Python client for the Model Context Protocol (MCP). It can start a local MCP server over stdio, list available members (tools/prompts/resources), and run a simple chat flow powered by OpenAI.

## Features
- Start a local MCP server script via stdio (Windows/macOS/Linux)
- List server members: tools, prompts, and resources
- Chat mode that can call MCP tools using OpenAI
- Clean CLI interface via `python -m mcp_client` or the `mcp-client` console script

## Requirements
- Python 3.10+
- `mcp>=1.22.0`
- `openai>=2.8.1`
- An OpenAI API key (`OPENAI_API_KEY`)

## Install
Using `uv` (recommended):

```powershell
# From the project root
uv pip install .
```

Or with `pip`:

```powershell
pip install .
```

## Quick Start
Set your OpenAI API key, then run the client against the included server:

```powershell
# Set for current PowerShell session
$env:OPENAI_API_KEY = "sk-..."

# List members
uv run python -m mcp_client mcp_server/mcp_server.py --members

# Chat mode (calls tools when appropriate)
uv run python -m mcp_client mcp_server/mcp_server.py --chat
```

Alternatively, after installing the package, use the console script (if on PATH):

```powershell
mcp-client mcp_server/mcp_server.py --members
mcp-client mcp_server/mcp_server.py --chat
```

## Windows Notes
- PowerShell activation for a local venv: ` .\\.venv\\Scripts\\Activate.ps1 `
- You do not need to activate a venv when using `uv run`—it manages the environment automatically.

## CLI
The CLI supports:

- `--members`: Print tools, prompts, and resources exposed by the server
- `--chat`: Start a simple chat loop that may call MCP tools

Examples:

```powershell
# Show help (module form)
uv run python -m mcp_client --help

# With console script (after install)
mcp-client --help
```

## Project Structure

```
main.py
pyproject.toml
mcp_client/
	__init__.py
	__main__.py
    chat.py
	cli.py
	handlers.py
	mcp_client.py
mcp_server/
	mcp_server.py
```

- `mcp_server/mcp_server.py`: Example MCP server (FastMCP) running on stdio
- `mcp_client/mcp_client.py`: Client that starts the server and opens an MCP session
- `mcp_client/chat.py`: Hanldes chat loop for application
- `mcp_client/cli.py`: Parses CLI arguments
- `mcp_client/handlers.py`: Chat handler integrating OpenAI and MCP tools
- `mcp_client/__main__.py`: CLI entry (module form)
- `pyproject.toml`: Package metadata and console script mapping

## Configuration
- `OPENAI_API_KEY` must be set. Options:
	- Session-only: `$env:OPENAI_API_KEY = "sk-..."`
	- Persist for your user: `[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-...', 'User')` (restart terminal)

## Development
Run locally without installing:

```powershell
# Members
uv run python -m mcp_client mcp_server/mcp_server.py --members

# Chat
uv run python -m mcp_client mcp_server/mcp_server.py --chat
```

Optional venv activation in PowerShell:

```powershell
.\\.venv\\Scripts\\Activate.ps1
# work with python/pip
deactivate
```

## Notes
- This client avoids POSIX shell dependencies and uses `sys.executable` to start the server script for cross-platform compatibility.
- If you rely on newer typing features (e.g., `typing.Self`), use Python 3.11+ or add `typing-extensions`.

## Citation
This project takes the base code from [Build a Python MCP Client to Test Servers From Your Terminal](https://realpython.com/python-mcp-client/?utm_source=notification_summary&utm_medium=email&utm_campaign=2025-11-19). Modifications were made and extra comments added to help facilitate learning and to remove dependency on POSIX shell.