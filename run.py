#!/usr/bin/env python3
"""Entry point for running the MCP server with FastMCP."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from server import mcp

if __name__ == "__main__":
    mcp.run()
