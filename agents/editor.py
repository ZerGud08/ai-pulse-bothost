"""Editor Agent - creates content using Groq API"""
import os
import re
from datetime import datetime, timedelta
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
        """Generate short news post (200-400 chars) with HTML formatting"""
        prompt = f"""
Ты — опытный редактор Telegram-канала "AI-Pulse". 
Пиши для IT-специалистов, разработчиков и предпринимателей. 
Стиль: дружелюбный, экспертный, без воды, фокус на практическую пользу.

СОЗДАЙ КОРОТКИЙ ПОСТ (200–400 символов) НА РУССКОМ ЯЗЫКЕ.

НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

СТРУКТУРА ПОСТА:
1. ЗАГОЛОВОК — до 70 символов, цепляющий, передаёт суть. 
   ОБЯЗАТЕЛЬНО используй HTML-тег <b>...</b> для жирного выделения.
2. 2–3 предложения сути.
3. ПРАКТИЧЕСКИЙ ВЫВОД — начни с 💡 и новой строки.
4. В конце укажи источник (ссылку) и добавь 2–3 хештега.

ПРИМЕР ПРАВИЛЬНОГО ФОРМАТА:
🔥 <b>OpenAI выпустила GPT-4.1 — быстрее и дешевле</b>

Новая модель на 40% быстрее и стоит в 2 раза меньше предыдущей. Уже доступна в API.

💡 Разработчикам: обновите интеграции — это снизит ваши расходы на инфраструктуру.

🔗 Источник: openai.com/blog/gpt-4-1

#OpenAI #GPT4 #AI

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ, БЕЗ РАССУЖДЕНИЙ. 
ЗАГОЛОВОК ОБЯЗАТЕЛЬНО В <b>.
ВЫВОД ОБЯЗАТЕЛЬНО НАЧИНАЙ С 💡 И НОВОЙ СТРОКИ.
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
        """Generate detailed article (800-1500 chars) with HTML formatting"""
        prompt = f"""
Ты — главный аналитик канала "AI-Pulse". 
Твоя аудитория — умные, занятые люди, которые хотят быстро понять суть и извлечь пользу.

СОЗДАЙ РАЗВЁРНУТЫЙ ПОСТ (800–1500 символов) НА РУССКОМ ЯЗЫКЕ.

НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

СТРУКТУРА ПОСТА:
1. 🔥 ЗАГОЛОВОК — до 80 символов, цепляющий, отражающий главную мысль.
   ОБЯЗАТЕЛЬНО используй HTML-тег <b>...</b> для жирного выделения.
2. ЛИД — 1–2 предложения о том, что произошло и почему это важно прямо сейчас.
3. ОСНОВНАЯ ЧАСТЬ:
   - Что именно анонсировано / случилось? (ключевые факты, цифры, даты)
   - Технические детали (если есть) — но не перегружай, только самое важное.
   - Почему это событие значимо для индустрии?
4. 💡 ПРАКТИЧЕСКИЙ ВЫВОД — начни с 💡 и новой строки. Как это можно применить? Для кого это актуально?
5. 🤔 Мнение AI-Pulse — краткий аналитический комментарий.
6. 🔗 Источник — ссылка.
7. #хештеги (3–5).

ПРИМЕР ПРАВИЛЬНОГО ФОРМАТА:
🔥 <b>Google представила Gemini 2.0 — мультимодальную модель нового поколения</b>

Вчера Google анонсировала Gemini 2.0, которая понимает текст, видео и аудио одновременно. Это первый шаг к ИИ-агентам, которые могут действовать в реальном мире.

Модель уже доступна в ограниченном доступе. Ключевые улучшения: ...
Технически это стало возможным благодаря ...
Для индустрии это означает ...

💡 Для разработчиков открываются новые возможности: ...
Предприниматели могут использовать для ...

🤔 Наш комментарий: Gemini 2.0 — это не просто очередная модель, а смена парадигмы. ...

🔗 Источник: blog.google/gemini2

#Google #Gemini #AI #Мультимодальность

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ, БЕЗ РАССУЖДЕНИЙ.
ЗАГОЛОВОК ОБЯЗАТЕЛЬНО В <b>.
ВЫВОД ОБЯЗАТЕЛЬНО НАЧИНАЙ С 💡 И НОВОЙ СТРОКИ.
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
        """Создаёт ежедневный дайджест с чёткой структурой"""
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

НОВОСТИ ЗА ДЕНЬ (топ-7):
{news_text}

СТРУКТУРА ДАЙДЖЕСТА:
1. ЗАГОЛОВОК: 📊 AI-Pulse Daily Digest | {datetime.now().strftime('%d.%m.%Y')}
2. 🔥 Главные события дня: (3 пункта с кратким описанием и ссылкой)
3. ⚡ Также важно: (2–3 кратких пункта)
4. 🛠 Инструменты: (1–2 инструмента с описанием, если есть в новостях)
5. 💡 Тренд дня: (1–2 предложения о главном тренде)
6. 📈 Цифра дня: (интересная статистика)

ИСПОЛЬЗУЙ HTML-ТЕГИ ДЛЯ ЖИРНОГО (<b>...</b>) В ЗАГОЛОВКАХ.
ЭМОДЗИ ДОЛЖНЫ БЫТЬ В НАЧАЛЕ КАЖДОГО БЛОКА.

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ.
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

СТРУКТУРА ОБЗОРА:
🎯 <b>AI-Тренды недели ({datetime.now().strftime('%d.%m')} – {(datetime.now() + timedelta(days=7)).strftime('%d.%m')})</b>

📈 Главный тренд: [название и описание в 2-3 предложения]

🔥 Что произошло:
1. [Событие] — [значимость]
2. [Событие] — [значимость]
3. [Событие] — [значимость]

💼 Бизнес-импакт: [как это влияет на индустрию]

👨‍💻 Для разработчиков: [что нужно знать]

🔮 Прогноз на следующую неделю: [1-2 предложения]

ИСПОЛЬЗУЙ HTML-ТЕГИ ДЛЯ ЖИРНОГО (<b>...</b>) В ЗАГОЛОВКАХ.

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ.
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
        """Обрабатывает список новостей, генерируя посты"""
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
                content = f"<b>{title}</b>\n\n{summary}\n\n💡 {title}\n\n🔗 {url}\n\n#AI #Нейросети"
                logger.warning(f"Used fallback for article: {title}")

            posts.append({
                "news": news,
                "content": content,
                "format": format_type,
            })
        logger.info(f"Editor: created {len(posts)} posts")
        return posts