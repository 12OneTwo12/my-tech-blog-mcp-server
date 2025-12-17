"""MCP Server for My Tech Blog - Provides access to personal blog documentation and experiences.

Built with FastMCP for the fastest, most Pythonic MCP server development.
"""

import logging
from typing import Literal

from fastmcp import FastMCP

from llms_parser import LLMSParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("My Tech Blog")

# Initialize parser
parser = LLMSParser()


# ============================================================================
# RESOURCES - Read-only data access
# ============================================================================


@mcp.resource("blog://llms-txt")
async def get_full_llms_txt() -> str:
    """Complete llms.txt content from jeongil.dev.

    Includes all documentation, tech blog posts, and experiences
    from the personal development blog.
    """
    content = await parser.get_content()
    return content.raw_content


@mcp.resource("blog://documentation")
async def get_documentation() -> str:
    """Development guidelines and conventions.

    Contains coding conventions, Git workflows, architecture principles,
    API design patterns, testing strategies, and infrastructure rules.
    """
    content = await parser.get_content()

    if not content.documentation:
        return "No documentation sections available."

    sections = []
    for section in content.documentation:
        sections.append(f"# {section.title}\n\n{section.content}\n")
    return "\n---\n\n".join(sections)


@mcp.resource("blog://tech-blog")
async def get_tech_blog() -> str:
    """Real-world tech experiences and blog posts.

    Contains experiences in Backend development, Infrastructure & DevOps,
    Architecture & Design, and Development Culture.
    """
    content = await parser.get_content()

    if not content.tech_blog:
        return "No tech blog posts available."

    sections = []
    for section in content.tech_blog:
        sections.append(f"# {section.title}\n\n{section.content}\n")
    return "\n---\n\n".join(sections)


@mcp.resource("blog://documentation/summary")
async def get_documentation_summary() -> str:
    """Quick overview of all available documentation sections.

    Provides a summary of development guidelines and rules
    without the full content.
    """
    return await parser.get_documentation_summary()


@mcp.resource("blog://tech-blog/summary")
async def get_tech_blog_summary() -> str:
    """Quick overview of all tech blog posts and experiences.

    Provides a summary of past experiences and learning
    without the full content.
    """
    return await parser.get_tech_blog_summary()


# ============================================================================
# TOOLS - Executable functions
# ============================================================================


@mcp.tool()
async def search_documentation(query: str) -> str:
    """Search for specific topics in documentation and development guidelines.

    Use this when you need to find coding conventions, architectural patterns,
    Git workflows, or development rules.

    Args:
        query: Search query (e.g., 'git convention', 'TDD', 'kubernetes', 'API design')

    Returns:
        Search results with matching documentation sections
    """
    results = await parser.search_documentation(query)

    if not results:
        return f"No documentation found for query: '{query}'"

    response_parts = [f"# Documentation Search Results for '{query}'\n"]
    for section in results:
        response_parts.append(f"\n## {section.title}\n")
        response_parts.append(section.content)
        response_parts.append("\n---\n")

    return "\n".join(response_parts)


@mcp.tool()
async def search_experience(query: str) -> str:
    """Search for past experiences and real-world problem-solving stories.

    Use this when you need to know how specific technical challenges
    were handled in the past.

    Args:
        query: Search query (e.g., 'kubernetes migration', 'database replication', 'MSA transition')

    Returns:
        Search results with matching tech blog posts and experiences
    """
    results = await parser.search_tech_blog(query)

    if not results:
        return f"No experiences found for query: '{query}'"

    response_parts = [f"# Experience Search Results for '{query}'\n"]
    for section in results:
        response_parts.append(f"\n## {section.title}\n")
        response_parts.append(section.content)
        response_parts.append("\n---\n")

    return "\n".join(response_parts)


@mcp.tool()
async def get_category_posts(
    category: Literal["backend", "infrastructure", "architecture", "culture"]
) -> str:
    """Get all posts from a specific tech blog category.

    Useful for browsing experiences by topic area.

    Args:
        category: Blog category to retrieve (backend, infrastructure, architecture, or culture)

    Returns:
        All posts from the specified category
    """
    content = await parser.get_content()

    # Filter by category
    filtered_sections = [
        section for section in content.tech_blog
        if category in section.category.lower() or category in section.title.lower()
    ]

    if not filtered_sections:
        return f"No posts found in category: '{category}'"

    response_parts = [f"# Tech Blog Posts - {category.title()} Category\n"]
    for section in filtered_sections:
        response_parts.append(f"\n## {section.title}\n")
        response_parts.append(section.content)
        response_parts.append("\n---\n")

    return "\n".join(response_parts)


@mcp.tool()
async def refresh_content() -> str:
    """Force refresh the cached blog content from jeongil.dev.

    Use this if you suspect the content might be outdated and want
    to fetch the latest version from the blog.

    Returns:
        Confirmation message
    """
    await parser.get_content(force_refresh=True)
    return "Blog content successfully refreshed from jeongil.dev"


# ============================================================================
# PROMPTS - Reusable templates
# ============================================================================


@mcp.prompt()
def check_past_experience(topic: str) -> str:
    """Check if a similar problem was encountered before.

    Searches tech blog for relevant experiences and summarizes key learnings.

    Args:
        topic: The technical topic or problem to search for
               (e.g., 'kubernetes deployment', 'database optimization')
    """
    return f"""I'm working on: {topic}

Have I encountered a similar problem before? Please search my tech blog for related experiences and summarize:
1. What similar challenges did I face?
2. How did I solve them?
3. What lessons did I learn that might apply now?

Use the search_experience tool to find relevant posts."""


@mcp.prompt()
def get_development_guideline(guideline_type: str) -> str:
    """Retrieve specific development guidelines and conventions.

    Searches documentation for rules and best practices.

    Args:
        guideline_type: Type of guideline to retrieve
                       (e.g., 'git convention', 'API design', 'testing strategy', 'database rules')
    """
    return f"""I need to check our development guidelines for: {guideline_type}

Please retrieve the relevant guidelines from our documentation and provide:
1. The specific rules or conventions
2. Any examples or best practices mentioned
3. Related guidelines that might also apply

Use the search_documentation tool to find the information."""


@mcp.prompt()
def review_architecture_decision(architecture_topic: str) -> str:
    """Review past architectural decisions and patterns.

    Useful when making similar architecture decisions.

    Args:
        architecture_topic: Architecture topic
                           (e.g., 'MSA transition', 'infrastructure design', 'system architecture')
    """
    return f"""I'm making an architecture decision about: {architecture_topic}

Please help me review past architectural decisions and experiences:
1. Search documentation for architectural principles and patterns
2. Search tech blog for related implementation experiences
3. Summarize key learnings and considerations

Use both search_documentation and search_experience tools."""


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting My Tech Blog MCP Server...")
    logger.info("Serving content from: https://jeongil.dev/ko/llms.txt")
    mcp.run()
