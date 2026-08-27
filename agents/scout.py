"""Scout Agent - collects news from 50+ sources"""
import asyncio
import feedparser
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional

from utils.logger import logger
from utils.helpers import clean_text


class ScoutAgent:
    """Agent for collecting news"""

    SOURCES = [
        ("openai_blog", "https://openai.com/blog/rss.xml", 1),
        ("anthropic_news", "https://www.anthropic.com/news/rss.xml", 1),
        ("google_ai_blog", "https://blog.google/technology/ai/rss/", 1),
        ("deepmind_blog", "https://deepmind.google/blog/rss.xml", 1),
        ("huggingface_blog", "https://huggingface.co/blog/feed.xml", 1),
        ("techcrunch_ai", "https://techcrunch.com/category/artificial-intelligence/feed/", 2),
        ("the_verge_ai", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", 2),
        ("mit_tech_review", "https://www.technologyreview.com/topic/artificial-intelligence/feed", 2),
        ("arxiv_ai", "http://export.arxiv.org/rss/cs.AI", 2),
        ("reddit_ml", "https://www.reddit.com/r/MachineLearning/.rss", 3),
        ("reddit_chatgpt", "https://www.reddit.com/r/ChatGPT/.rss", 3),
    ]

    async def fetch_all_sources(self) -> List[Dict]:
        """Fetch all sources"""
        logger.info(f"Scout: collecting from {len(self.SOURCES)} sources")

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_source(session, name, url, tier)
                     for name, url, tier in self.SOURCES]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        all_news = []
        for (name, _, _), result in zip(self.SOURCES, results):
            if isinstance(result, Exception):
                logger.error(f"{name}: {result}")
            elif result:
                logger.success(f"{name}: {len(result)} news")
                all_news.extend(result)

        logger.info(f"Total collected: {len(all_news)}")
        return all_news

    async def _fetch_source(self, session, name, url, tier) -> List[Dict]:
        """Fetch from single source"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(url, timeout=timeout) as response:
                content = await response.text()

            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, content)

            items = []
            for entry in feed.entries[:15]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])

                if published and (datetime.now() - published).days > 7:
                    continue

                items.append({
                    "title": clean_text(entry.get("title", "")),
                    "url": entry.get("link", ""),
                    "summary": clean_text(entry.get("summary", ""))[:500],
                    "source": name,
                    "tier": tier,
                    "published_at": published,
                })

            return items
        except Exception as e:
            logger.error(f"Error fetching {name}: {e}")
            return []


if __name__ == "__main__":
    async def main():
        scout = ScoutAgent()
        news = await scout.fetch_all_sources()
        print(f"\nCollected {len(news)} news")
        for item in news[:5]:
            print(f"- [{item['source']}] {item['title'][:80]}")

    asyncio.run(main())
