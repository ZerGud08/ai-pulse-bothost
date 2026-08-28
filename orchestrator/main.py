"""Main Orchestrator"""
import asyncio
import sys

from utils.logger import logger
from agents.scout import ScoutAgent
from agents.curator import CuratorAgent
from agents.editor import EditorAgent
from agents.publisher import PublisherAgent


class Orchestrator:
    """Main coordinator"""

    def __init__(self):
        self.scout = ScoutAgent()
        self.curator = CuratorAgent()
        self.editor = EditorAgent()
        self.publisher = PublisherAgent()

    async def run_pipeline(self):
        """Main pipeline"""
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

            # Берем только одну новость для публикации
            best_news = quality_news[:1]  # <-- только одна

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

    async def start(self):
        """Start orchestrator"""
        logger.info("AI-Pulse starting...")
        await self.run_pipeline()
        logger.info("AI-Pulse finished")


async def main():
    orchestrator = Orchestrator()
    await orchestrator.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Goodbye!")
        sys.exit(0)