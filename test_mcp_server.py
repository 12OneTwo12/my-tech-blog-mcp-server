#!/usr/bin/env python3
"""
MCP 서버 로컬 테스트 스크립트

FastMCP의 테스트 클라이언트를 사용하여 서버가 정상 작동하는지 검증합니다.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from server import mcp


async def test_server():
    """Test MCP server components."""
    print("=" * 80)
    print("MCP Server - Local Test")
    print("=" * 80)
    print()

    # Test 1: Server metadata
    print("1. Server Metadata")
    print(f"   Name: {mcp.name}")
    print()

    # Test 2: List resources
    print("2. Testing Resources")
    try:
        # FastMCP servers expose resources through _resources
        resource_count = len(mcp._resources)
        print(f"   ✓ Found {resource_count} resources")
        for uri, func in mcp._resources.items():
            print(f"     - {uri}")
        print()
    except Exception as e:
        print(f"   ✗ Error listing resources: {e}")
        print()

    # Test 3: List tools
    print("3. Testing Tools")
    try:
        tool_count = len(mcp._tools)
        print(f"   ✓ Found {tool_count} tools")
        for name, func in mcp._tools.items():
            print(f"     - {name}()")
        print()
    except Exception as e:
        print(f"   ✗ Error listing tools: {e}")
        print()

    # Test 4: List prompts
    print("4. Testing Prompts")
    try:
        prompt_count = len(mcp._prompts)
        print(f"   ✓ Found {prompt_count} prompts")
        for name, func in mcp._prompts.items():
            print(f"     - {name}")
        print()
    except Exception as e:
        print(f"   ✗ Error listing prompts: {e}")
        print()

    # Test 5: Test a resource
    print("5. Testing Resource Access (blog://llms-txt)")
    try:
        from llms_parser import LLMSParser
        parser = LLMSParser()
        content = await parser.get_content()
        print(f"   ✓ Successfully fetched content ({len(content.raw_content)} chars)")
        print(f"   ✓ Documentation sections: {len(content.documentation)}")
        print(f"   ✓ Tech Blog sections: {len(content.tech_blog)}")
        print()
    except Exception as e:
        print(f"   ✗ Error accessing resource: {e}")
        import traceback
        traceback.print_exc()
        print()

    # Test 6: Test a tool
    print("6. Testing Tool (search_documentation)")
    try:
        from llms_parser import LLMSParser
        parser = LLMSParser()
        results = await parser.search_documentation("git")
        print(f"   ✓ Search returned {len(results)} results")
        if results:
            print(f"   ✓ First result: {results[0].title}")
        print()
    except Exception as e:
        print(f"   ✗ Error testing tool: {e}")
        import traceback
        traceback.print_exc()
        print()

    print("=" * 80)
    print("✓ Local test completed!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Start the server: ./venv/bin/python run.py")
    print("2. Use MCP Inspector: npx @modelcontextprotocol/inspector")
    print("3. Or configure Claude Desktop with the server")
    print()


if __name__ == "__main__":
    asyncio.run(test_server())
