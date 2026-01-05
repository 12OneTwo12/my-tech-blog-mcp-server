"""MCP Server for My Tech Blog - Provides access to personal blog documentation and experiences.

Built with FastMCP for the fastest, most Pythonic MCP server development.
"""

import json
import logging
from datetime import datetime
from typing import Literal, Optional

from fastmcp import FastMCP

from llms_parser import LLMSParser, ParserConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("My Tech Blog")

# Initialize parser with config
config = ParserConfig()
parser = LLMSParser(config=config)

logger.info(f"Initialized parser with URL: {config.llms_url}")


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
async def search_documentation(query: str, top_k: int = 10) -> str:
    """Search for specific topics in documentation and development guidelines.

    Use this when you need to find coding conventions, architectural patterns,
    Git workflows, or development rules. Uses BM25 ranking for relevance.

    Args:
        query: Search query (e.g., 'git convention', 'TDD', 'kubernetes', 'API design')
        top_k: Maximum number of results to return (default: 10)

    Returns:
        Search results with matching documentation sections, ranked by relevance
    """
    results = await parser.search_documentation(query, top_k=top_k)

    if not results:
        return f"No documentation found for query: '{query}'"

    response_parts = [f"# Documentation Search Results for '{query}' (Top {len(results)})\n"]
    for idx, section in enumerate(results, 1):
        response_parts.append(f"\n## {idx}. {section.title}\n")
        if section.url:
            response_parts.append(f"URL: {section.url}\n")
        response_parts.append(section.content)
        response_parts.append("\n---\n")

    return "\n".join(response_parts)


@mcp.tool()
async def search_experience(query: str, top_k: int = 10) -> str:
    """Search for past experiences and real-world problem-solving stories.

    Use this when you need to know how specific technical challenges
    were handled in the past. Uses BM25 ranking for relevance.

    Args:
        query: Search query (e.g., 'kubernetes migration', 'database replication', 'MSA transition')
        top_k: Maximum number of results to return (default: 10)

    Returns:
        Search results with matching tech blog posts and experiences, ranked by relevance
    """
    results = await parser.search_tech_blog(query, top_k=top_k)

    if not results:
        return f"No experiences found for query: '{query}'"

    response_parts = [f"# Experience Search Results for '{query}' (Top {len(results)})\n"]
    for idx, section in enumerate(results, 1):
        response_parts.append(f"\n## {idx}. {section.title}\n")
        if section.url:
            response_parts.append(f"URL: {section.url}\n")
        if section.published_date:
            response_parts.append(f"Published: {section.published_date.strftime('%Y-%m-%d')}\n")
        if section.subcategory:
            response_parts.append(f"Category: {section.subcategory}\n")
        response_parts.append(section.content)
        response_parts.append("\n---\n")

    return "\n".join(response_parts)


@mcp.tool()
async def get_category_posts(
    category: Literal[
        "backend", "infrastructure", "architecture", "culture", "reflection", "trends"
    ],
) -> str:
    """Get all posts from a specific tech blog category.

    Useful for browsing experiences by topic area.

    Args:
        category: Blog category to retrieve

    Returns:
        All posts from the specified category with metadata
    """
    content = await parser.get_content()

    filtered_sections = [
        section
        for section in content.all_sections
        if section.subcategory == category or category in (section.category or "").lower()
    ]

    if not filtered_sections:
        return f"No posts found in category: '{category}'"

    response_parts = [
        f"# Tech Blog Posts - {category.title()} Category ({len(filtered_sections)} posts)\n"
    ]
    for idx, section in enumerate(filtered_sections, 1):
        response_parts.append(f"\n## {idx}. {section.title}\n")
        if section.url:
            response_parts.append(f"URL: {section.url}\n")
        if section.published_date:
            response_parts.append(f"Published: {section.published_date.strftime('%Y-%m-%d')}\n")
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


@mcp.tool()
async def search_all(query: str, top_k: int = 10) -> str:
    """Search across ALL blog content (documentation, tech blog, reflections, trends).

    Most comprehensive search - searches everything with BM25 ranking.

    Args:
        query: Search query
        top_k: Maximum number of results to return (default: 10)

    Returns:
        Ranked search results from all content with relevance scores
    """
    results = await parser.search_all(query, top_k=top_k)

    if not results:
        return f"No results found for query: '{query}'"

    response_parts = [f"# Global Search Results for '{query}' (Top {len(results)})\n"]
    for idx, result in enumerate(results, 1):
        section = result.section
        response_parts.append(f"\n## {idx}. {section.title} [Score: {result.score:.2f}]\n")
        response_parts.append(f"Category: {section.category}")
        if section.subcategory:
            response_parts.append(f" > {section.subcategory}")
        response_parts.append("\n")
        if section.url:
            response_parts.append(f"URL: {section.url}\n")
        if section.published_date:
            response_parts.append(f"Published: {section.published_date.strftime('%Y-%m-%d')}\n")
        if result.matched_terms:
            response_parts.append(f"Matched terms: {', '.join(set(result.matched_terms))}\n")
        response_parts.append(f"\n{section.content}\n")
        response_parts.append("\n---\n")

    return "\n".join(response_parts)


@mcp.tool()
async def get_recent_posts(days: int = 30, category: Optional[str] = None) -> str:
    """Get recent blog posts from the last N days.

    Args:
        days: Number of days to look back (default: 30)
        category: Optional category filter (documentation, tech_blog, reflections, trends)

    Returns:
        Recent posts sorted by date
    """
    from datetime import timedelta

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    posts = await parser.get_posts_by_date(
        start_date=start_date, end_date=end_date, category=category
    )

    if not posts:
        return f"No posts found in the last {days} days"

    response_parts = [f"# Recent Posts (Last {days} Days)\n"]
    if category:
        response_parts[0] = f"# Recent Posts in {category} (Last {days} Days)\n"

    response_parts.append(f"Found {len(posts)} posts\n")

    for idx, section in enumerate(posts, 1):
        response_parts.append(f"\n## {idx}. {section.title}\n")
        if section.published_date:
            response_parts.append(f"Published: {section.published_date.strftime('%Y-%m-%d')}\n")
        if section.subcategory:
            response_parts.append(f"Category: {section.subcategory}\n")
        if section.url:
            response_parts.append(f"URL: {section.url}\n")
        preview = section.content[:300].strip()
        if len(section.content) > 300:
            preview += "..."
        response_parts.append(f"\n{preview}\n")
        response_parts.append("\n---\n")

    return "\n".join(response_parts)


@mcp.tool()
async def health_check() -> str:
    """Check the health status of the MCP server and parser.

    Returns:
        JSON health status including cache state and configuration
    """
    status = await parser.get_health_status()
    return json.dumps(status, indent=2, default=str)


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting My Tech Blog MCP Server...")
    logger.info(f"Serving content from: {config.llms_url}")
    logger.info(f"Cache TTL: {config.cache_ttl_minutes} minutes")
    mcp.run()
