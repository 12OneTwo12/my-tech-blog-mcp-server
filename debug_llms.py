#!/usr/bin/env python3
"""Debug script to check llms.txt structure."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from llms_parser import LLMSParser


async def debug():
    """Debug llms.txt structure."""
    parser = LLMSParser()

    raw = await parser.fetch_content()

    print("=" * 80)
    print("RAW CONTENT")
    print("=" * 80)
    print(raw[:1000])
    print("\n...")
    print("\n" + "=" * 80)
    print("HEADERS FOUND")
    print("=" * 80)

    for line in raw.split('\n')[:50]:
        if line.strip().startswith('#'):
            print(line)


if __name__ == "__main__":
    asyncio.run(debug())
