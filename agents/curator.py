"""Curator Agent - filters and scores news with deduplication"""
import json
import os
from datetime import datetime, timedelta
from utils.logger import logger

class CuratorAgent:
    def __init__(self):
        self.published_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'published_urls.json')

    def _load_published_urls(self):
        """Загружает список уже опубликованных URL из файла"""
        if os.path.exists(self.published_file):
            try:
                with open(self.published_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_published_urls(self, urls):
        """Сохраняет список опубликованных URL в файл"""
        os.makedirs(os.path.dirname(self.published_file), exist_ok=True)
        with open(self.published_file, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=2)

    def filter_news(self, items, min_score=60):
        """
        Оценивает новости, отфильтровывает уже опубликованные,
        и возвращает только новые, отсортированные по рейтингу.
        """
        # Загружаем уже опубликованные URL
        published_urls = self._load_published_urls()
        published_set = set(published_urls)
        logger.info(f"Curator: загружено {len(published_set)} уже опубликованных URL")

        # Фильтруем новости, убирая те, что уже опубликованы
        new_items = []
        for item in items:
            url = item.get('url', '')
            if url and url in published_set:
                continue
            # Если URL отсутствует или новый, добавляем
            new_items.append(item)

        logger.info(f"Curator: после исключения дубликатов осталось {len(new_items)} новостей")

        # Скоринг и отбор (используем существующий метод)
        scored = []
        for item in new_items:
            score = self._calculate_score(item)
            item['score'] = score
            if score >= min_score:
                scored.append(item)

        scored.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"Curator: отобрано {len(scored)} качественных новостей (min_score={min_score})")
        return scored[:10]  # Возвращаем топ-10

    def _calculate_score(self, item):
        # (код скоринга остаётся без изменений, как в вашей предыдущей версии)
        score = 0
        published = item.get('published_at')
        if published:
            age_hours = (datetime.now() - published).total_seconds() / 3600
            if age_hours < 3:
                score += 25
            elif age_hours < 12:
                score += 20
            elif age_hours < 24:
                score += 15
            elif age_hours < 48:
                score += 10
            else:
                score += 5
        else:
            score += 10

        tier = item.get('tier', 3)
        if tier == 1:
            score += 20
        elif tier == 2:
            score += 15
        else:
            score += 10

        text = (item.get('title', '') + ' ' + item.get('summary', '')).lower()
        ai_keywords = [
            'gpt', 'claude', 'llm', 'openai', 'anthropic', 'gemini', 'deepmind',
            'neural', 'machine learning', 'deep learning', 'ai model',
            'нейросеть', 'искусственный интеллект', 'машинное обучение',
            'transformers', 'diffusion', 'stable diffusion', 'midjourney',
            'агент', 'агенты', 'agent', 'agents', 'автономный'
        ]
        keyword_count = sum(1 for kw in ai_keywords if kw in text)
        score += min(keyword_count * 5, 30)

        practical_keywords = [
            'tutorial', 'guide', 'how to', 'launch', 'release', 'announces',
            'гайд', 'инструкция', 'запуск', 'релиз', 'обзор', 'пример',
            'кейс', 'case', 'best practices', 'рекомендации'
        ]
        practical_count = sum(1 for kw in practical_keywords if kw in text)
        score += min(practical_count * 5, 15)

        viral_signals = ['breaking', 'first', 'new', 'exclusive', '重磅', 'first look']
        if any(signal in text for signal in viral_signals):
            score += 10

        return min(score, 100)

    def add_published_url(self, url):
        """Добавляет URL в список опубликованных и сохраняет файл"""
        urls = self._load_published_urls()
        if url not in urls:
            urls.append(url)
            self._save_published_urls(urls)
            logger.info(f"Curator: добавлен URL в опубликованные: {url}")