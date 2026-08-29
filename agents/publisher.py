"""Editor Agent - creates content using Groq API"""
import os
import re
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv
from utils.logger import logger

def clean_llm_response(text: str) -> str:
    """Удаляет технические блоки и HTML-теги, оставляет разделение абзацев"""
    if not text:
        return ""
    # Удаляем <think>...</think>
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Удаляем все остальные HTML-теги, но оставляем переносы
    text = re.sub(r'<[^>]+>', '', text)
    # Заменяем 3 и более переносов на 2 (чтобы избежать слишком больших отступов)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

class EditorAgent:
    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info("Editor initialized (Groq)")

    async def create_short_news(self, news: dict) -> str:
        """Generate short news post (200-400 chars) with HTML formatting and paragraph breaks"""
        prompt = f"""
Ты — опытный редактор Telegram-канала "AI-Pulse". 
Пиши для IT-специалистов, разработчиков и предпринимателей. 
Стиль: дружелюбный, экспертный, без воды, фокус на практическую пользу.

ВАЖНО: Разделяй абзацы пустой строкой (два переноса) для читаемости.
Заголовок всегда в <b>...</b>.
Вывод начинай с 💡 и новой строки.

СОЗДАЙ КОРОТКИЙ ПОСТ (200–400 символов) НА РУССКОМ ЯЗЫКЕ.

НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

СТРУКТУРА ПОСТА:
1. ЗАГОЛОВОК — до 70 символов, в <b>...</b>.
2. 2–3 предложения сути.
3. ПРАКТИЧЕСКИЙ ВЫВОД — начни с 💡 и новой строки.
4. В конце укажи источник (ссылку) и добавь 2–3 хештега.

ПРИМЕР ФОРМАТА (с пустыми строками):
🔥 <b>OpenAI выпустила GPT-4.1 — быстрее и дешевле</b>

Новая модель на 40% быстрее и стоит в 2 раза меньше предыдущей. Уже доступна в API.

💡 Разработчикам: обновите интеграции — это снизит ваши расходы на инфраструктуру.

🔗 Источник: openai.com/blog/gpt-4-1

#OpenAI #GPT4 #AI

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
        """Generate detailed article (800-1500 chars) with HTML formatting and paragraph breaks"""
        prompt = f"""
Ты — главный аналитик канала "AI-Pulse". 
Твоя аудитория — умные, занятые люди, которые хотят быстро понять суть и извлечь пользу.

ВАЖНО: Разделяй абзацы пустой строкой (два переноса) для читаемости.
Заголовок всегда в <b>...</b>.
Вывод начинай с 💡 и новой строки.

СОЗДАЙ РАЗВЁРНУТЫЙ ПОСТ (800–1500 символов) НА РУССКОМ ЯЗЫКЕ.

НОВОСТЬ:
Заголовок: {news.get('title', '')}
Текст: {news.get('summary', '')}
Источник: {news.get('url', '')}

СТРУКТУРА ПОСТА:
1. 🔥 ЗАГОЛОВОК в <b>...</b>.
2. ЛИД — 1–2 предложения.
3. ОСНОВНАЯ ЧАСТЬ (2–3 абзаца, разделённые пустыми строками):
   - Что произошло?
   - Технические детали (если есть).
   - Почему это важно?
4. 💡 ПРАКТИЧЕСКИЙ ВЫВОД (новая строка, начинается с 💡).
5. 🤔 Мнение AI-Pulse.
6. 🔗 Источник.
7. #хештеги.

ПРИМЕР ФОРМАТА (с пустыми строками):
🔥 <b>Google представила Gemini 2.0 — мультимодальную модель нового поколения</b>

Вчера Google анонсировала Gemini 2.0, которая понимает текст, видео и аудио одновременно. Это первый шаг к ИИ-агентам, которые могут действовать в реальном мире.

Модель уже доступна в ограниченном доступе. Ключевые улучшения: улучшенное понимание контекста, мультимодальность и низкая задержка.

Для индустрии это означает переход к более естественному взаимодействию с ИИ.

💡 Для разработчиков открываются новые возможности: создание приложений, которые одновременно работают с текстом, звуком и видео.

🤔 Наш комментарий: Gemini 2.0 — это не просто очередная модель, а смена парадигмы.

🔗 Источник: blog.google/gemini2

#Google #Gemini #AI #Мультимодальность

ОТВЕТЬ ТОЛЬКО ГОТОВЫМ ПОСТОМ, БЕЗ РАССУЖДЕНИЙ.
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
        """Создаёт ежедневный дайджест с чёткой структурой и разделением абзацев"""
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

ВАЖНО: Разделяй смысловые блоки пустой строкой (два переноса) для читаемости.
Используй HTML-теги для жирного (<b>...</b>) в заголовках.

НОВОСТИ ЗА ДЕНЬ (топ-7):
{news_text}

СТРУКТУРА ДАЙДЖЕСТА:
📊 <b>AI-Pulse Daily Digest | {datetime.now().strftime('%d.%m.%Y')}</b>

🔥 Главные события дня:
1. [Краткое описание + ссылка]
2. [Краткое описание + ссылка]
3. [Краткое описание + ссылка]

⚡ Также важно:
• [Новость]
• [Новость]

🛠 Инструменты:
• [Инструмент с описанием] (если есть)

💡 Тренд дня: [1-2 предложения]

📈 Цифра дня: [интересная статистика]

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
        """Создаёт еженедельный аналитический обзор с разделением абзацев"""
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

ВАЖНО: Разделяй смысловые блоки пустой строкой (два переноса) для читаемости.
Используй HTML-теги для жирного (<b>...</b>) в заголовках.

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