"""Main Orchestrator"""
import asyncio
import sys
from datetime import datetime, timedelta  # <-- добавлено

from utils.logger import logger
from agents.scout import ScoutAgent
from agents.curator import CuratorAgent
from agents.editor import EditorAgent
from agents.publisher import PublisherAgent


class Orchestrator:
    def __init__(self):
        self.scout = ScoutAgent()
        self.curator = CuratorAgent()
        self.editor = EditorAgent()
        self.publisher = PublisherAgent()

    async def run_pipeline(self):
        """Обычный пайплайн – публикует 1 лучший пост"""
        try:
            logger.info("=" * 50)
            logger.info("Pipeline started")
            logger.info("=" * 50)

            logger.info("Stage 1/4: Collecting news...")
            raw_news = await self.scout.fetch_all_sources()
            if not raw_news:
                logger.warning("No new data")
                return

            logger.info("Stage 2/4: Filtering...")
            quality_news = self.curator.filter_news(raw_news, min_score=0)
            if not quality_news:
                logger.warning("No quality news")
                return

            logger.info(f"Curator selected {len(quality_news)} news")
            best_news = quality_news[:1]

            logger.info("Stage 3/4: Creating content...")
            posts = await self.editor.process_batch(best_news)
            if not posts:
                logger.warning("No posts generated")
                return

            logger.info("Stage 4/4: Publishing...")
            for post in posts:
                await self.publisher.publish(post)
                await asyncio.sleep(1)

            logger.success(f"Pipeline completed! {len(posts)} post published")

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()

    async def run_daily_digest(self):
        """Ежедневный дайджест – публикует один пост с топ-7 новостей за сутки"""
        try:
            logger.info("=" * 50)
            logger.info("Daily Digest started")
            logger.info("=" * 50)

            logger.info("Stage 1/4: Collecting news...")
            raw_news = await self.scout.fetch_all_sources()
            if not raw_news:
                logger.warning("No news for digest")
                return False  # возвращаем False, чтобы бот знал о неудаче

            # Фильтруем новости за последние 24 часа
            now = datetime.now()
            day_ago = now - timedelta(hours=24)
            recent_news = [n for n in raw_news if n.get('published_at') and n['published_at'] > day_ago]
            if not recent_news:
                logger.warning("No recent news for digest")
                return False

            logger.info(f"Found {len(recent_news)} news from last 24 hours")

            # Скоринг и отбор лучших (без дедупликации – она уже есть в curator)
            scored = []
            for item in recent_news:
                score = self.curator._calculate_score(item)
                item['score'] = score
                scored.append(item)
            scored.sort(key=lambda x: x['score'], reverse=True)
            top_news = scored[:7]

            logger.info("Stage 2/4: Creating digest...")
            content = await self.editor.create_digest(top_news)
            if not content:
                logger.warning("Digest content empty")
                return False

            post = {"content": content, "news": top_news[0] if top_news else {}}
            logger.info("Stage 3/4: Publishing digest...")
            await self.publisher.publish(post)
            logger.success("Daily digest published successfully")
            return True

        except Exception as e:
            logger.error(f"Digest error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def run_weekly_analytics(self):
        """Еженедельная аналитика – публикует один пост с обзором за неделю"""
        try:
            logger.info("=" * 50)
            logger.info("Weekly Analytics started")
            logger.info("=" * 50)

            logger.info("Stage 1/4: Collecting news...")
            raw_news = await self.scout.fetch_all_sources()
            if not raw_news:
                logger.warning("No news for analytics")
                return False

            # Фильтруем новости за последние 7 дней
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            recent_news = [n for n in raw_news if n.get('published_at') and n['published_at'] > week_ago]
            if not recent_news:
                logger.warning("No recent news for analytics")
                return False

            logger.info(f"Found {len(recent_news)} news from last 7 days")

            scored = []
            for item in recent_news:
                score = self.curator._calculate_score(item)
                item['score'] = score
                scored.append(item)
            scored.sort(key=lambda x: x['score'], reverse=True)
            top_news = scored[:10]

            logger.info("Stage 2/4: Creating analytics...")
            content = await self.editor.create_weekly_analytics(top_news)
            if not content:
                logger.warning("Analytics content empty")
                return False

            post = {"content": content, "news": top_news[0] if top_news else {}}
            logger.info("Stage 3/4: Publishing analytics...")
            await self.publisher.publish(post)
            logger.success("Weekly analytics published successfully")
            return True

        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def start(self):
        logger.info("AI-Pulse orchestrator ready")


async def main():
    orchestrator = Orchestrator()
    await orchestrator.run_pipeline()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Goodbye!")
        sys.exit(0)