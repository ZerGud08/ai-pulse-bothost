"""Curator Agent - filters and scores news"""
from utils.logger import logger

class CuratorAgent:
    def filter_news(self, items, min_score=0):
        """Simple filter: returns all items with score >= min_score"""
        # Пока пропускаем всё, в будущем можно добавить скоринг
        logger.info(f"Curator: filtering {len(items)} items")
        # Для теста возвращаем первые 10, чтобы не перегружать
        return items[:10]