"""Parser for llms.txt content from jeongil.dev with advanced search capabilities."""

import asyncio
import logging
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


def _safe_int(env_var: str, default: int) -> int:
    """Safely parse integer from environment variable."""
    try:
        return int(os.getenv(env_var, str(default)))
    except ValueError:
        logger.warning(f"Invalid integer for {env_var}, using default: {default}")
        return default


def _safe_float(env_var: str, default: float) -> float:
    """Safely parse float from environment variable."""
    try:
        return float(os.getenv(env_var, str(default)))
    except ValueError:
        logger.warning(f"Invalid float for {env_var}, using default: {default}")
        return default


@dataclass
class ParserConfig:
    """Configuration for the LLMS parser."""

    base_url: str = field(default_factory=lambda: os.getenv("BLOG_BASE_URL", "https://jeongil.dev"))
    llms_path: str = field(default_factory=lambda: os.getenv("BLOG_LLMS_PATH", "/ko/llms.txt"))
    cache_ttl_minutes: int = field(default_factory=lambda: _safe_int("BLOG_CACHE_TTL_MINUTES", 60))
    http_timeout: float = field(default_factory=lambda: _safe_float("BLOG_HTTP_TIMEOUT", 30.0))
    http_max_retries: int = field(default_factory=lambda: _safe_int("BLOG_HTTP_MAX_RETRIES", 3))
    http_retry_delay: float = field(default_factory=lambda: _safe_float("BLOG_HTTP_RETRY_DELAY", 1.0))

    @property
    def llms_url(self) -> str:
        return f"{self.base_url}{self.llms_path}"


# =============================================================================
# Models
# =============================================================================


class BlogSection(BaseModel):
    """Represents a section in the blog with rich metadata."""

    title: str
    content: str  # Summary from llms.txt
    category: str  # main category: documentation, tech_blog, reflections, trends
    subcategory: Optional[str] = None  # subcategory: backend, infrastructure, etc.
    url: Optional[str] = None  # Human-readable URL (without .md)
    md_url: Optional[str] = None  # Direct URL to .md file for full content
    published_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Combined searchable text."""
        return f"{self.title} {self.content}"


class LLMSContent(BaseModel):
    """Parsed content from llms.txt with metadata."""

    raw_content: str
    documentation: List[BlogSection] = Field(default_factory=list)
    tech_blog: List[BlogSection] = Field(default_factory=list)
    reflections: List[BlogSection] = Field(default_factory=list)
    trends: List[BlogSection] = Field(default_factory=list)
    fetched_at: datetime = Field(default_factory=datetime.now)
    source_url: str = ""

    @property
    def all_sections(self) -> List[BlogSection]:
        """All sections combined for unified search."""
        return self.documentation + self.tech_blog + self.reflections + self.trends


class SearchResult(BaseModel):
    """Search result with relevance score."""

    section: BlogSection
    score: float
    matched_terms: List[str] = Field(default_factory=list)


# =============================================================================
# BM25 Search Engine
# =============================================================================


class BM25SearchEngine:
    """BM25 ranking algorithm implementation for text search.

    BM25 (Best Matching 25) is a ranking function used by search engines
    to estimate the relevance of documents to a given search query.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Args:
            k1: Term frequency saturation parameter (1.2-2.0 typical)
            b: Document length normalization parameter (0.75 typical)
        """
        self.k1 = k1
        self.b = b
        self._documents: List[str] = []
        self._doc_lengths: List[int] = []
        self._avg_doc_length: float = 0
        self._doc_freqs: Dict[str, int] = {}  # term -> number of docs containing term
        self._term_freqs: List[Counter] = []  # per-document term frequencies
        self._indexed = False

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms."""
        # Convert to lowercase and extract words
        text = text.lower()
        # Handle Korean and English
        words = re.findall(r"[\w가-힣]+", text)
        return words

    def index(self, documents: List[str]) -> None:
        """Build the search index from documents."""
        self._documents = documents
        self._term_freqs = []
        self._doc_freqs = Counter()
        self._doc_lengths = []

        for doc in documents:
            tokens = self._tokenize(doc)
            self._doc_lengths.append(len(tokens))

            term_freq = Counter(tokens)
            self._term_freqs.append(term_freq)

            # Update document frequencies (each term counted once per doc)
            for term in set(tokens):
                self._doc_freqs[term] += 1

        self._avg_doc_length = sum(self._doc_lengths) / len(documents) if documents else 0
        self._indexed = True
        logger.debug(f"Indexed {len(documents)} documents with {len(self._doc_freqs)} unique terms")

    def _idf(self, term: str) -> float:
        """Calculate Inverse Document Frequency for a term."""
        n = len(self._documents)
        df = self._doc_freqs.get(term, 0)
        if df == 0:
            return 0
        # BM25 IDF formula
        return math.log((n - df + 0.5) / (df + 0.5) + 1)

    def _score_document(self, query_terms: List[str], doc_idx: int) -> Tuple[float, List[str]]:
        """Calculate BM25 score for a single document."""
        score = 0.0
        matched_terms = []

        doc_length = self._doc_lengths[doc_idx]
        term_freqs = self._term_freqs[doc_idx]

        for term in query_terms:
            if term not in term_freqs:
                continue

            matched_terms.append(term)
            tf = term_freqs[term]
            idf = self._idf(term)

            # BM25 scoring formula (guard against division by zero)
            numerator = tf * (self.k1 + 1)
            if self._avg_doc_length > 0:
                length_norm = doc_length / self._avg_doc_length
            else:
                length_norm = 1.0  # No normalization if avg is 0
            denominator = tf + self.k1 * (1 - self.b + self.b * length_norm)
            score += idf * (numerator / denominator)

        return score, matched_terms

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float, List[str]]]:
        """
        Search for documents matching the query.

        Returns:
            List of (doc_index, score, matched_terms) tuples, sorted by score descending
        """
        if not self._indexed:
            logger.warning("Search called before indexing")
            return []

        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        results = []
        for idx in range(len(self._documents)):
            score, matched = self._score_document(query_terms, idx)
            if score > 0:
                results.append((idx, score, matched))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


# =============================================================================
# Cache with TTL
# =============================================================================


@dataclass
class CacheEntry:
    """Cache entry with expiration."""

    content: LLMSContent
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


# =============================================================================
# HTTP Client with Retry
# =============================================================================


class ResilientHttpClient:
    """HTTP client with retry logic and circuit breaker pattern."""

    def __init__(self, config: ParserConfig):
        self.config = config
        self._consecutive_failures = 0
        self._circuit_open_until: Optional[datetime] = None

    async def get(self, url: str) -> str:
        """Fetch URL with retries and exponential backoff."""
        # Check circuit breaker
        if self._circuit_open_until and datetime.now() < self._circuit_open_until:
            raise ConnectionError(
                f"Circuit breaker open until {self._circuit_open_until}. "
                "Too many consecutive failures."
            )

        last_exception: Optional[Exception] = None

        for attempt in range(self.config.http_max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.config.http_timeout) as client:
                    response = await client.get(url)
                    response.raise_for_status()

                    # Reset failure count on success
                    self._consecutive_failures = 0
                    self._circuit_open_until = None

                    logger.info(f"Successfully fetched {url}")
                    return response.text

            except httpx.HTTPStatusError as e:
                last_exception = e
                logger.warning(
                    f"HTTP error {e.response.status_code} fetching {url} "
                    f"(attempt {attempt + 1}/{self.config.http_max_retries})"
                )
                # Don't retry on 4xx errors (except 429)
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    break

            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_exception = e
                logger.warning(
                    f"Request error fetching {url}: {e} "
                    f"(attempt {attempt + 1}/{self.config.http_max_retries})"
                )

            # Exponential backoff
            if attempt < self.config.http_max_retries - 1:
                delay = self.config.http_retry_delay * (2**attempt)
                logger.debug(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)

        # Track failures for circuit breaker
        self._consecutive_failures += 1
        if self._consecutive_failures >= 5:
            self._circuit_open_until = datetime.now() + timedelta(minutes=5)
            logger.error(f"Circuit breaker opened after {self._consecutive_failures} failures")

        raise ConnectionError(
            f"Failed to fetch {url} after {self.config.http_max_retries} attempts: {last_exception}"
        )


# =============================================================================
# Main Parser
# =============================================================================


class LLMSParser:
    """Parser for fetching and parsing llms.txt content with advanced features.

    Features:
    - BM25 semantic search
    - TTL-based caching
    - Resilient HTTP fetching with retries
    - Rich metadata extraction
    """

    def __init__(self, config: Optional[ParserConfig] = None):
        self.config = config or ParserConfig()
        self._cache: Optional[CacheEntry] = None
        self._http_client = ResilientHttpClient(self.config)
        self._search_engine = BM25SearchEngine()
        self._search_indexed = False

    async def fetch_content(self) -> str:
        """Fetch llms.txt content from the blog with resilient HTTP."""
        return await self._http_client.get(self.config.llms_url)

    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract publication date from text."""
        # Pattern: "Published YYYY-MM-DD" or "YYYY-MM-DD"
        patterns = [
            r"Published\s+(\d{4}-\d{2}-\d{2})",
            r"(\d{4}-\d{2}-\d{2})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return datetime.strptime(match.group(1), "%Y-%m-%d")
                except ValueError:
                    continue
        return None

    def _extract_url(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract URL from markdown link or path.

        Returns:
            Tuple of (human_readable_url, md_url)
        """
        # Pattern: [text](/path/to/article.md)
        match = re.search(r"\[([^\]]+)\]\((/[^)]+)\)", text)
        if match:
            path = match.group(2)
            md_url = f"{self.config.base_url}{path}"  # Full URL to .md file

            # Convert .md path to human-readable URL
            human_path = path
            if human_path.endswith(".md"):
                human_path = human_path.replace("/index.md", "").replace(".md", "")
            human_url = f"{self.config.base_url}{human_path}"

            return human_url, md_url
        return None, None

    def _extract_subcategory(self, section_context: str) -> Optional[str]:
        """Extract subcategory from section context."""
        subcategories = {
            "troubleshooting": "troubleshooting",
            "performance": "performance",
            "optimization": "performance",
            "backend": "backend",
            "infrastructure": "infrastructure",
            "devops": "infrastructure",
            "architecture": "architecture",
            "design": "architecture",
            "culture": "culture",
            "reflection": "reflection",
            "trends": "trends",
        }
        context_lower = section_context.lower()
        for keyword, subcat in subcategories.items():
            if keyword in context_lower:
                return subcat
        return None

    def _parse_sections(self, content: str) -> LLMSContent:
        """Parse llms.txt content into structured sections with metadata."""
        lines = content.split("\n")

        parsed = LLMSContent(
            raw_content=content, source_url=self.config.llms_url, fetched_at=datetime.now()
        )

        current_main_category: Optional[str] = None  # ## level
        current_sub_context: Optional[str] = None  # ### or #### level context
        current_section: Optional[str] = None
        current_content: List[str] = []
        current_url: Optional[str] = None
        current_md_url: Optional[str] = None

        def save_section():
            """Helper to save the current section."""
            nonlocal current_content, current_section, current_url, current_md_url

            if current_section and current_content and current_main_category:
                content_text = "\n".join(current_content).strip()

                # Extract metadata
                pub_date = self._extract_date(content_text)
                if not current_url:
                    current_url, current_md_url = self._extract_url(content_text)
                subcategory = self._extract_subcategory(
                    f"{current_sub_context or ''} {current_section}"
                )

                section = BlogSection(
                    title=current_section,
                    content=content_text,
                    category=current_main_category,
                    subcategory=subcategory,
                    url=current_url,
                    md_url=current_md_url,
                    published_date=pub_date,
                )

                # Add to appropriate list
                if current_main_category == "documentation":
                    parsed.documentation.append(section)
                elif current_main_category == "tech_blog":
                    parsed.tech_blog.append(section)
                elif current_main_category == "reflections":
                    parsed.reflections.append(section)
                elif current_main_category == "trends":
                    parsed.trends.append(section)

                current_content = []
                current_section = None
                current_url = None
                current_md_url = None

        for line in lines:
            line_stripped = line.strip()

            # Detect ## level (main categories)
            if line_stripped.startswith("## "):
                save_section()

                section_title = line_stripped[3:].strip()

                if "Documentation" in section_title:
                    current_main_category = "documentation"
                elif "Tech Blog" in section_title:
                    current_main_category = "tech_blog"
                elif "Reflection" in section_title or "Thoughts" in section_title:
                    current_main_category = "reflections"
                elif "Trends" in section_title:
                    current_main_category = "trends"
                else:
                    current_main_category = None

                current_sub_context = None

            # Detect ### level (subcategories/groups)
            elif line_stripped.startswith("### "):
                save_section()
                current_sub_context = line_stripped[4:].strip()

            # Detect #### level (sub-subcategories)
            elif line_stripped.startswith("#### "):
                save_section()
                sub_context = line_stripped[5:].strip()
                current_sub_context = (
                    f"{current_sub_context} > {sub_context}" if current_sub_context else sub_context
                )

            # Detect list items with links (actual blog posts)
            elif line_stripped.startswith("- ["):
                save_section()

                # Extract title from markdown link
                title_match = re.match(r"- \[([^\]]+)\]", line_stripped)
                if title_match:
                    current_section = title_match.group(1)
                    current_url, current_md_url = self._extract_url(line_stripped)
                    # Rest of the line is content start
                    rest_match = re.search(r"\):\s*(.+)", line_stripped)
                    if rest_match:
                        current_content = [rest_match.group(1)]
                    else:
                        current_content = []

            # Collect content
            else:
                if current_main_category and current_section:
                    current_content.append(line)

        # Save last section
        save_section()

        logger.info(
            f"Parsed {len(parsed.documentation)} docs, "
            f"{len(parsed.tech_blog)} blog posts, "
            f"{len(parsed.reflections)} reflections, "
            f"{len(parsed.trends)} trends"
        )

        return parsed

    def _build_search_index(self, content: LLMSContent) -> None:
        """Build BM25 search index from content."""
        all_sections = content.all_sections
        documents = [section.full_text for section in all_sections]
        self._search_engine.index(documents)
        self._search_indexed = True
        logger.info(f"Built search index with {len(documents)} documents")

    async def get_content(self, force_refresh: bool = False) -> LLMSContent:
        """Get parsed llms.txt content with TTL caching."""
        # Check cache
        if not force_refresh and self._cache and not self._cache.is_expired:
            logger.debug("Returning cached content")
            return self._cache.content

        # Fetch and parse
        try:
            raw_content = await self.fetch_content()
            content = self._parse_sections(raw_content)

            # Update cache
            self._cache = CacheEntry(
                content=content,
                expires_at=datetime.now() + timedelta(minutes=self.config.cache_ttl_minutes),
            )

            # Rebuild search index
            self._build_search_index(content)

            return content

        except Exception as e:
            logger.error(f"Failed to fetch content: {e}")
            # Return stale cache if available
            if self._cache:
                logger.warning("Returning stale cached content due to fetch failure")
                return self._cache.content
            raise

    async def search_all(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search across all sections using BM25 ranking."""
        content = await self.get_content()

        if not self._search_indexed:
            self._build_search_index(content)

        all_sections = content.all_sections
        results = self._search_engine.search(query, top_k)

        return [
            SearchResult(section=all_sections[idx], score=score, matched_terms=matched)
            for idx, score, matched in results
        ]

    async def search_documentation(self, query: str, top_k: int = 10) -> List[BlogSection]:
        """Search for content in documentation sections."""
        results = await self.search_all(query, top_k=50)  # Get more, then filter

        filtered = [r.section for r in results if r.section.category == "documentation"]
        return filtered[:top_k]

    async def search_tech_blog(self, query: str, top_k: int = 10) -> List[BlogSection]:
        """Search for content in tech blog sections."""
        results = await self.search_all(query, top_k=50)

        filtered = [r.section for r in results if r.section.category == "tech_blog"]
        return filtered[:top_k]

    async def get_documentation_summary(self) -> str:
        """Get a summary of all documentation sections."""
        content = await self.get_content()

        if not content.documentation:
            return "No documentation sections found."

        summary_parts = ["# Documentation Summary\n"]
        for section in content.documentation:
            summary_parts.append(f"## {section.title}")
            if section.url:
                summary_parts.append(f"URL: {section.url}")
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
            meta_parts = []
            if section.published_date:
                meta_parts.append(f"Published: {section.published_date.strftime('%Y-%m-%d')}")
            if section.subcategory:
                meta_parts.append(f"Category: {section.subcategory}")
            if section.url:
                meta_parts.append(f"URL: {section.url}")
            if meta_parts:
                summary_parts.append(" | ".join(meta_parts))
            preview = section.content[:200].strip()
            if len(section.content) > 200:
                preview += "..."
            summary_parts.append(preview)
            summary_parts.append("")

        return "\n".join(summary_parts)

    async def get_posts_by_date(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
    ) -> List[BlogSection]:
        """Get posts filtered by date range and optionally category."""
        content = await self.get_content()

        sections = (
            content.all_sections
            if not category
            else [s for s in content.all_sections if s.category == category]
        )

        # Filter by date (only include posts WITH dates when date filtering is requested)
        filtered = []
        for section in sections:
            # If date filters are specified, only include posts with dates
            if start_date or end_date:
                if not section.published_date:
                    continue  # Skip posts without dates when filtering by date
                if start_date and section.published_date < start_date:
                    continue
                if end_date and section.published_date > end_date:
                    continue
            filtered.append(section)

        # Sort by date descending
        filtered.sort(key=lambda s: s.published_date or datetime.min, reverse=True)

        return filtered

    async def get_health_status(self) -> Dict:
        """Get health status of the parser."""
        return {
            "status": "healthy",
            "cache_valid": self._cache is not None and not self._cache.is_expired,
            "cache_expires_at": self._cache.expires_at.isoformat() if self._cache else None,
            "search_indexed": self._search_indexed,
            "source_url": self.config.llms_url,
            "config": {
                "cache_ttl_minutes": self.config.cache_ttl_minutes,
                "http_timeout": self.config.http_timeout,
                "http_max_retries": self.config.http_max_retries,
            },
        }

    async def fetch_post_content(self, section: BlogSection) -> str:
        """Fetch full content of a blog post from its .md URL.

        Args:
            section: BlogSection with md_url

        Returns:
            Full markdown content of the post
        """
        if not section.md_url:
            raise ValueError(f"No md_url available for section: {section.title}")

        logger.info(f"Fetching full content from: {section.md_url}")
        return await self._http_client.get(section.md_url)

    async def get_post_by_title(self, title: str) -> Optional[BlogSection]:
        """Find a post by its title (partial match supported).

        Args:
            title: Title to search for (case-insensitive partial match)

        Returns:
            Matching BlogSection or None
        """
        content = await self.get_content()
        title_lower = title.lower()

        for section in content.all_sections:
            if title_lower in section.title.lower():
                return section

        return None

    async def get_full_post_content(self, title: str) -> Optional[str]:
        """Get full content of a post by title.

        Args:
            title: Title to search for (partial match supported)

        Returns:
            Full markdown content or None if not found
        """
        section = await self.get_post_by_title(title)
        if not section:
            return None

        if not section.md_url:
            return f"# {section.title}\n\n{section.content}\n\n(Full content URL not available)"

        try:
            return await self.fetch_post_content(section)
        except Exception as e:
            logger.error(f"Failed to fetch full content for {section.title}: {e}")
            return f"# {section.title}\n\n{section.content}\n\n(Failed to fetch full content: {e})"
