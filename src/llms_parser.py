"""Parser for llms.txt content from jeongil.dev."""

import httpx
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BlogSection(BaseModel):
    """Represents a section in the blog."""

    title: str
    content: str
    category: str
    url: Optional[str] = None


class LLMSContent(BaseModel):
    """Parsed content from llms.txt."""

    raw_content: str
    documentation: List[BlogSection] = Field(default_factory=list)
    tech_blog: List[BlogSection] = Field(default_factory=list)
    reflections: List[BlogSection] = Field(default_factory=list)
    trends: List[BlogSection] = Field(default_factory=list)


class LLMSParser:
    """Parser for fetching and parsing llms.txt content."""

    def __init__(self, base_url: str = "https://jeongil.dev"):
        self.base_url = base_url
        self.llms_url = f"{base_url}/ko/llms.txt"
        self._cache: Optional[LLMSContent] = None

    async def fetch_content(self) -> str:
        """Fetch llms.txt content from the blog."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.llms_url)
            response.raise_for_status()
            return response.text

    def _parse_sections(self, content: str) -> LLMSContent:
        """Parse llms.txt content into structured sections."""
        lines = content.split('\n')

        parsed = LLMSContent(raw_content=content)
        current_main_category = None  # ## level (Documentation, Tech Blog)
        current_section = None  # ### level
        current_content = []

        for line in lines:
            line_stripped = line.strip()

            # Detect ## level (main categories)
            if line_stripped.startswith('## '):
                # Save previous section
                if current_section and current_content and current_main_category:
                    self._add_section(
                        parsed,
                        current_main_category,
                        current_section,
                        '\n'.join(current_content)
                    )
                    current_content = []
                    current_section = None

                # Determine main category
                section_title = line_stripped[3:].strip()

                if 'Documentation' in section_title:
                    current_main_category = 'documentation'
                elif 'Tech Blog' in section_title:
                    current_main_category = 'tech_blog'
                elif 'Reflection' in section_title or 'Thoughts' in section_title:
                    current_main_category = 'reflections'
                elif 'Trends' in section_title:
                    current_main_category = 'trends'
                else:
                    current_main_category = None

            # Detect ### level (subsections)
            elif line_stripped.startswith('### '):
                # Save previous subsection
                if current_section and current_content and current_main_category:
                    self._add_section(
                        parsed,
                        current_main_category,
                        current_section,
                        '\n'.join(current_content)
                    )
                    current_content = []

                current_section = line_stripped[4:].strip()

            # Collect content
            else:
                if current_main_category and current_section:
                    current_content.append(line)

        # Save last section
        if current_section and current_content and current_main_category:
            self._add_section(
                parsed,
                current_main_category,
                current_section,
                '\n'.join(current_content)
            )

        return parsed

    def _add_section(
        self,
        parsed: LLMSContent,
        category: Optional[str],
        title: str,
        content: str
    ):
        """Add a section to the appropriate category."""
        if not category:
            return

        section = BlogSection(
            title=title,
            content=content.strip(),
            category=category
        )

        if category == 'documentation':
            parsed.documentation.append(section)
        elif category == 'tech_blog':
            parsed.tech_blog.append(section)
        elif category == 'reflections':
            parsed.reflections.append(section)
        elif category == 'trends':
            parsed.trends.append(section)

    async def get_content(self, force_refresh: bool = False) -> LLMSContent:
        """Get parsed llms.txt content with caching."""
        if self._cache is None or force_refresh:
            raw_content = await self.fetch_content()
            self._cache = self._parse_sections(raw_content)

        return self._cache

    async def search_documentation(self, query: str) -> List[BlogSection]:
        """Search for content in documentation sections."""
        content = await self.get_content()
        query_lower = query.lower()

        return [
            section for section in content.documentation
            if query_lower in section.title.lower() or query_lower in section.content.lower()
        ]

    async def search_tech_blog(self, query: str) -> List[BlogSection]:
        """Search for content in tech blog sections."""
        content = await self.get_content()
        query_lower = query.lower()

        return [
            section for section in content.tech_blog
            if query_lower in section.title.lower() or query_lower in section.content.lower()
        ]

    async def get_documentation_summary(self) -> str:
        """Get a summary of all documentation sections."""
        content = await self.get_content()

        if not content.documentation:
            return "No documentation sections found."

        summary_parts = ["# Documentation Summary\n"]
        for section in content.documentation:
            summary_parts.append(f"## {section.title}")
            # Get first 200 characters as preview
            preview = section.content[:200].strip()
            if len(section.content) > 200:
                preview += "..."
            summary_parts.append(preview)
            summary_parts.append("")

        return "\n".join(summary_parts)

    async def get_tech_blog_summary(self) -> str:
        """Get a summary of all tech blog sections."""
        content = await self.get_content()

        if not content.tech_blog:
            return "No tech blog sections found."

        summary_parts = ["# Tech Blog Summary\n"]
        for section in content.tech_blog:
            summary_parts.append(f"## {section.title}")
            # Get first 200 characters as preview
            preview = section.content[:200].strip()
            if len(section.content) > 200:
                preview += "..."
            summary_parts.append(preview)
            summary_parts.append("")

        return "\n".join(summary_parts)
