#!/usr/bin/env python
"""Интерактивный бот для канала AI-Pulse"""
import os
import re
import sys
import json
import threading
import asyncio
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
from urllib.parse import urlparse

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from dotenv import load_dotenv
from groq import Groq

# Импорты для планировщика
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from orchestrator.main import Orchestrator

# Загружаем переменные окружения (если есть .env)
load_dotenv()

# --- Получение токенов ---
TOKEN = os.getenv("INTERACTIVE_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TOKEN:
    sys.exit("❌ Ошибка: не найден токен бота (INTERACTIVE_BOT_TOKEN или TELEGRAM_BOT_TOKEN).")
if not GROQ_API_KEY:
    sys.exit("❌ Ошибка: не найден GROQ_API_KEY.")

# Инициализируем клиент Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# Создаём экземпляр оркестратора для публикаций (глобально)
orchestrator = Orchestrator()

# --- HTTP сервер для health check (чтобы Render видел открытый порт) ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

# --- Вспомогательная функция для запросов к Groq ---
async def ask_groq(prompt: str, system_prompt: str = "Ты — полезный AI-ассистент.") -> str:
    try:
        response = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Ошибка при обращении к AI: {str(e)}"

# --- Функция-обёртка для запуска пайплайна с логированием ---
async def run_pipeline_wrapper():
    """Обёртка для запуска пайплайна с обработкой ошибок и логированием"""
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🔄 [{start_time}] Запуск пайплайна публикации...")
    try:
        await orchestrator.run_pipeline()
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ [{end_time}] Пайплайн успешно завершён")
    except Exception as e:
        print(f"❌ Ошибка в пайплайне: {e}")
        import traceback
        traceback.print_exc()

# --- Синхронная обёртка для планировщика ---
def run_pipeline_sync():
    """Синхронная обёртка для запуска асинхронного пайплайна"""
    asyncio.run(run_pipeline_wrapper())

# --- Обработчики команд ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Привет! Я — AI-ассистент канала AI-Pulse.\n\n"
        "Я могу:\n"
        "• 📄 Сделать саммари статьи по ссылке — /summary <url>\n"
        "• 🛠 Подобрать AI-инструменты под вашу задачу — /tools <описание задачи>\n"
        "• 💡 Сгенерировать идеи для проекта или бизнеса — /ideas <тема>\n\n"
        "Просто отправь команду с текстом или ссылкой."
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📌 Доступные команды:\n\n"
        "/start — приветствие\n"
        "/help — эта справка\n"
        "/summary <ссылка> — краткое содержание статьи\n"
        "/tools <запрос> — подбор AI-инструментов\n"
        "/ideas <тема> — генерация идей\n"
        "/publish_now — ручной запуск публикации новостей\n"
        "/show_published — показать последние опубликованные URL\n\n"
        "Примеры:\n"
        "/summary https://openai.com/blog/gpt-4-1\n"
        "/tools хочу сделать чат-бота для поддержки\n"
        "/ideas сервис для автоматического перевода видео"
    )
    await update.message.reply_text(help_text)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите ссылку после команды, например: /summary https://example.com/article")
        return

    url = context.args[0]
    if not urlparse(url).scheme:
        await update.message.reply_text("❌ Непохоже на ссылку. Убедитесь, что начинается с http:// или https://")
        return

    await update.message.reply_text("⏳ Получаю статью и делаю саммари... Это может занять 10–20 секунд.")

    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            await update.message.reply_text("❌ Не удалось загрузить страницу. Проверьте ссылку.")
            return

        raw_text = response.text
        clean_text = re.sub(r'<[^>]+>', ' ', raw_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()[:3000]

        prompt = f"""
Сделай краткое саммари (до 500 символов) этой статьи:

{clean_text}

Выдели главную мысль, ключевые факты и практическую пользу.
"""
        summary_text = await ask_groq(prompt, "Ты — опытный редактор, который умеет кратко излагать суть.")
        await update.message.reply_text(f"📄 **Краткое содержание:**\n\n{summary_text}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обработке: {str(e)}")

async def tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Опишите задачу после команды, например: /tools создать чат-бота на русском")
        return

    user_query = " ".join(context.args)
    await update.message.reply_text("⏳ Ищу подходящие инструменты...")

    prompt = f"""
Пользователь ищет AI-инструменты для задачи: {user_query}

Предложи 3–5 конкретных инструментов (названия + краткое описание), которые лучше всего подходят для этой задачи.
Укажи, какие из них бесплатные, а какие платные.
Ответ напиши на русском, структурированно (списком или с пунктами).
"""
    result = await ask_groq(prompt, "Ты — эксперт по AI-инструментам и сервисам.")
    await update.message.reply_text(f"🛠 **Рекомендуемые инструменты:**\n\n{result}")

async def ideas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите тему после команды, например: /ideas образовательное приложение с AI")
        return

    topic = " ".join(context.args)
    await update.message.reply_text("⏳ Генерирую идеи...")

    prompt = f"""
Сгенерируй 5 креативных идей для проекта или бизнеса на тему: {topic}.
Идеи должны быть реалистичными, с использованием AI-технологий.
Для каждой идеи дай краткое описание (1-2 предложения) и потенциальную аудиторию.
Ответ напиши на русском, структурированно (нумерованный список).
"""
    result = await ask_groq(prompt, "Ты — креативный стратег и предприниматель.")
    await update.message.reply_text(f"💡 **Идеи по теме «{topic}»:**\n\n{result}")

async def publish_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручной запуск пайплайна публикации"""
    await update.message.reply_text("⏳ Запускаю пайплайн публикации новостей...")
    try:
        await run_pipeline_wrapper()
        await update.message.reply_text("✅ Публикация завершена! Проверьте канал.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при публикации: {e}")

async def show_published(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает последние 10 опубликованных URL"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'published_urls.json')
    if not os.path.exists(file_path):
        await update.message.reply_text("❌ Файл с опубликованными URL пока не создан.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = json.load(f)
        if not urls:
            await update.message.reply_text("📭 Список опубликованных URL пуст.")
            return

        # Показываем последние 10 URL
        text = "📋 **Опубликованные URL (последние 10):**\n\n" + "\n".join(urls[-10:])
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при чтении файла: {e}")

# --- Основная функция ---
def main():
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("tools", tools))
    application.add_handler(CommandHandler("ideas", ideas))
    application.add_handler(CommandHandler("publish_now", publish_now))
    application.add_handler(CommandHandler("show_published", show_published))

    # --- Планировщик: публикация каждые 88 минут ---
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_pipeline_sync,
        trigger=IntervalTrigger(minutes=88),
        id="publish_news",
        next_run_time=datetime.now() + timedelta(seconds=15)
    )

    scheduler.start()
    next_run = scheduler.get_job('publish_news').next_run_time
    print(f"✅ Планировщик публикаций запущен (каждые 88 минут)")
    print(f"   Следующий запуск: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")

    # Health check сервер
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"✅ Health check server running on port {port}")

    print("🤖 Бот запущен и ожидает команды...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()