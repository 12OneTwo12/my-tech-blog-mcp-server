#!/usr/bin/env python3
"""Test script to verify llms.txt connection and parsing."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llms_parser import LLMSParser


async def test_connection():
    """Test connection to jeongil.dev and parsing."""
    print("=" * 60)
    print("My Tech Blog MCP Server - Connection Test")
    print("=" * 60)
    print()

    parser = LLMSParser()

    try:
        # Test 1: Fetch content
        print("1. llms.txt 콘텐츠 가져오기...")
        raw_content = await parser.fetch_content()
        print(f"   ✓ 성공: {len(raw_content)} 문자 수신")
        print()

        # Test 2: Parse content
        print("2. 콘텐츠 파싱...")
        content = await parser.get_content()
        print(f"   ✓ Documentation 섹션: {len(content.documentation)}개")
        print(f"   ✓ Tech Blog 섹션: {len(content.tech_blog)}개")
        print(f"   ✓ Reflections 섹션: {len(content.reflections)}개")
        print(f"   ✓ Trends 섹션: {len(content.trends)}개")
        print()

        # Test 3: Show documentation sections
        if content.documentation:
            print("3. Documentation 섹션 목록:")
            for i, section in enumerate(content.documentation[:5], 1):
                print(f"   {i}. {section.title}")
            if len(content.documentation) > 5:
                print(f"   ... 외 {len(content.documentation) - 5}개")
            print()

        # Test 4: Show tech blog sections
        if content.tech_blog:
            print("4. Tech Blog 섹션 목록:")
            for i, section in enumerate(content.tech_blog[:5], 1):
                print(f"   {i}. {section.title}")
            if len(content.tech_blog) > 5:
                print(f"   ... 외 {len(content.tech_blog) - 5}개")
            print()

        # Test 5: Search test
        print("5. 검색 기능 테스트 (query: 'git')...")
        results = await parser.search_documentation("git")
        print(f"   ✓ {len(results)}개의 결과 발견")
        if results:
            print(f"   첫 번째 결과: {results[0].title}")
        print()

        print("=" * 60)
        print("✓ 모든 테스트 통과!")
        print("=" * 60)
        print()
        print("MCP 서버가 정상적으로 작동할 준비가 되었습니다.")
        print("Claude Desktop에서 사용할 수 있습니다.")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ 테스트 실패")
        print("=" * 60)
        print(f"오류: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_connection())
