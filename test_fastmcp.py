#!/usr/bin/env python3
"""Test FastMCP server components."""

import sys
from pathlib import Path

# Add src to path and change directory context
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import with proper module resolution
import importlib.util
spec = importlib.util.spec_from_file_location("server", src_path / "server.py")
server_module = importlib.util.module_from_spec(spec)

# Create a mock llms_parser module to avoid import issues
import types
llms_parser = types.ModuleType("llms_parser")
sys.modules["server.llms_parser"] = llms_parser

# Now try to load the server
try:
    print("=" * 80)
    print("FastMCP Server - Import Test")
    print("=" * 80)
    print()

    # Try importing directly
    from llms_parser import LLMSParser
    print("✓ LLMSParser imported successfully")

    # Check if FastMCP is available
    from fastmcp import FastMCP
    print("✓ FastMCP imported successfully")

    print()
    print("=" * 80)
    print("✓ All imports successful!")
    print("=" * 80)
    print()
    print("The FastMCP server can be started with:")
    print("  ./venv/bin/python run.py")
    print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
