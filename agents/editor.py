"""Editor Agent - creates content using Groq API"""
import os
import re
from datetime import datetime, timedelta  # <-- добавлено
from groq import Groq
from dotenv import load_dotenv
from utils.logger import logger

def clean_llm_response(text: str) -> str:
    """Удаляет технические блоки и HTML-теги"""
    if not text:
        return ""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

class EditorAgent:
    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info("Editor initialized (Groq)")

    async def create_short_news(self, news: dict) -> str:
        # (код без изменений – ваш существующий метод)
        prompt = f"""
Ты — опытный редактор Telegram-канала "AI-Pulse", который пишет для IT-специалистов, разработчиков и предпринимателей. Твой стиль — дружелюбный, но экспертный, без воды, с фокусом на практическую пользу.

Напиши короткий пост (200–400 символов) на русском языке на основе этой новости.

НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

ТВОЯ ЗАДАЧА:
1. Придумай цепляющий заголовок (до 70 символов). Используй HTML-тег <b>...</b> для жирного выделения.
2. В 2–3 предложениях объясни суть.
3. Добавь практический вывод.
4. В конце укажи источник и 2–3 хештега.

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ, БЕЗ РАССУЖДЕНИЙ.
"""
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        raw = response.choices[0].message.content
        return clean_llm_response(raw)

    async def create_article(self, news: dict) -> str:
        # (код без изменений – ваш существующий метод)
        prompt = f"""
Ты — главный аналитик канала "AI-Pulse". Напиши развёрнутый пост (800–1500 символов) на русском языке на основе этой новости.

НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

СТРУКТУРА:
1. 🔥 Заголовок в <b>жирном</b> стиле.
2. Лид — 1–2 предложения о сути.
3. Основная часть: детали, почему это важно.
4. 💡 Практический раздел — как применить.
5. 🤔 Мнение AI-Pulse — краткий аналитический комментарий.
6. 🔗 Источник.
7. #хештеги.

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ.
"""
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1200,
        )
        raw = response.choices[0].message.content
        return clean_llm_response(raw)

    async def create_digest(self, news_list: list) -> str:
        """Создаёт ежедневный дайджест из списка новостей"""
        if not news_list:
            return ""
        news_text = ""
        for i, news in enumerate(news_list[:7], 1):
            title = news.get('title', 'Без заголовка')
            url = news.get('url', '')
            summary = news.get('summary', '')[:150]
            news_text += f"{i}. {title}\n   {summary}...\n   {url}\n\n"

        prompt = f"""
Ты — главный редактор канала "AI-Pulse". Создай ежедневный дайджест на русском языке.

ВОТ НОВОСТИ ЗА ДЕНЬ (топ-7):
{news_text}

ФОРМАТ:
📊 AI-Pulse Daily Digest | {datetime.now().strftime('%d.%m.%Y')}

🔥 Главные события дня:
1. [Краткое описание + ссылка]
2. [Краткое описание + ссылка]
3. [Краткое описание + ссылка]

⚡ Также важно:
• [Новость]
• [Новость]

🛠 Инструменты:
• [Инструмент с описанием] (если есть)

💡 Тренд дня: [1-2 предложения о главном тренде]

📈 Цифра дня: [интересная статистика]

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ, БЕЗ РАССУЖДЕНИЙ. ИСПОЛЬЗУЙ HTML-ТЕГИ ДЛЯ ЖИРНОГО.
"""
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content
        return clean_llm_response(raw)

    async def create_weekly_analytics(self, news_list: list) -> str:
        """Создаёт еженедельный аналитический обзор"""
        if not news_list:
            return ""
        news_text = ""
        for i, news in enumerate(news_list[:10], 1):
            title = news.get('title', 'Без заголовка')
            url = news.get('url', '')
            summary = news.get('summary', '')[:150]
            news_text += f"{i}. {title}\n   {summary}...\n   {url}\n\n"

        prompt = f"""
Ты — главный аналитик канала "AI-Pulse". Подготовь еженедельный обзор трендов на русском языке.

НОВОСТИ ЗА НЕДЕЛЮ (топ-10):
{news_text}

СТРУКТУРА:
🎯 AI-Тренды недели ({datetime.now().strftime('%d.%m')} – {(datetime.now() + timedelta(days=7)).strftime('%d.%m')})

📈 Главный тренд: [название и описание в 2-3 предложения]

🔥 Что произошло:
1. [Событие] — [значимость]
2. [Событие] — [значимость]
3. [Событие] — [значимость]

💼 Бизнес-импакт: [как это влияет на индустрию]

👨‍💻 Для разработчиков: [что нужно знать]

🔮 Прогноз на следующую неделю: [1-2 предложения]

Объём: 1000–1500 символов. Стиль — экспертный, но доступный. Используй HTML-теги.
"""
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1500,
        )
        raw = response.choices[0].message.content
        return clean_llm_response(raw)

    async def process_batch(self, news_list: list) -> list:
        """Обрабатывает список новостей, генерируя посты (используется для обычной публикации)"""
        posts = []
        for news in news_list:
            score = news.get("score", 0)
            if score >= 80:
                content = await self.create_article(news)
                format_type = "article"
            else:
                content = await self.create_short_news(news)
                format_type = "news"

            if not content or content.strip() == "":
                title = news.get('title', 'Новость')
                summary = news.get('summary', '')[:300]
                url = news.get('url', '')
                content = f"<b>{title}</b>\n\n{summary}\n\n🔗 {url}\n\n#AI #Нейросети"
                logger.warning(f"Used fallback for article: {title}")

            posts.append({
                "news": news,
                "content": content,
                "format": format_type,
            })
        logger.info(f"Editor: created {len(posts)} posts")
        return posts