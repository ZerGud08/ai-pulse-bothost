"""Editor Agent - creates content using Groq API"""
import os
from groq import Groq
from dotenv import load_dotenv
from utils.logger import logger

class EditorAgent:
    """Agent for content creation using LLM"""

    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info("Editor initialized (Groq)")

    async def create_short_news(self, news: dict) -> str:
        """Generate short news post (200-400 chars)"""
        prompt = f"""
Ты — редактор Telegram-канала про AI "AI-Pulse".
Создай короткий пост-новость (200-400 символов) на русском языке.

ИСХОДНАЯ НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

ТРЕБОВАНИЯ:
1. Начни с эмодзи и жирного заголовка (до 70 символов) – используй HTML-тег <b>...</b>
2. 2-3 предложения сути
3. Практический вывод для разработчиков
4. Источник в конце со ссылкой
5. 2-3 хештега

ФОРМАТ (пример):
🔥 <b>Заголовок</b>

Текст новости в 2-3 предложения.

💡 Практический вывод.

🔗 Источник: ссылка

#AI #Нейросети #Технологии
"""
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content

    async def create_article(self, news: dict) -> str:
        """Generate detailed article (800-1500 chars)"""
        prompt = f"""
Ты — эксперт-аналитик канала "AI-Pulse".
Создай развёрнутый пост (800-1500 символов) на русском языке.

ИСХОДНАЯ НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

СТРУКТУРА:
1. 🔥 Заголовок в <b>жирном</b> стиле (до 80 символов)
2. Лид — 1-2 предложения о ЧТО произошло
3. Основная часть:
   - Что именно анонсировано/произошло
   - Ключевые технические детали
   - Почему это важно
4. 💡 Практический раздел — как это можно использовать
5. 🤔 Мнение AI-Pulse — краткий аналитический комментарий
6. 🔗 Источник
7. #хештеги

ТРЕБОВАНИЯ:
- Пиши живым языком, не как робот
- Используй конкретные цифры и факты
- Добавь 1-2 уместных эмодзи
- Избегай канцелярита
- Пиши от первого лица команды AI-Pulse
"""
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1200,
        )
        return response.choices[0].message.content

    async def process_batch(self, news_list: list) -> list:
        """Process batch of news, generate posts"""
        posts = []
        for news in news_list:
            score = news.get("score", 0)
            if score >= 80:
                content = await self.create_article(news)
                format_type = "article"
            else:
                content = await self.create_short_news(news)
                format_type = "news"

            posts.append({
                "news": news,
                "content": content,
                "format": format_type,
            })
        logger.info(f"Editor: created {len(posts)} posts")
        return posts