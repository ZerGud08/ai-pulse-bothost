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
from apscheduler.triggers.cron import CronTrigger
from orchestrator.main import Orchestrator

# Загружаем переменные окружения
load_dotenv()

# --- Получение токенов и ID ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("INTERACTIVE_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "ai_pulse_ai")

if not TOKEN:
    sys.exit("❌ Ошибка: не найден токен бота.")
if not GROQ_API_KEY:
    sys.exit("❌ Ошибка: не найден GROQ_API_KEY.")
if not ADMIN_USER_ID:
    sys.exit("❌ Ошибка: не задан ADMIN_USER_ID (ваш Telegram ID).")

groq_client = Groq(api_key=GROQ_API_KEY)
orchestrator = Orchestrator()

# --- HTTP сервер для health check ---
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

# --- Функция для отправки уведомлений администратору (без parse_mode) ---
async def send_error_notification(error_text: str, context: str = ""):
    """Отправляет сообщение об ошибке администратору"""
    if not ADMIN_USER_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        message = f"⚠️ Ошибка в пайплайне\n\n{error_text}"
        if context:
            message += f"\n\nКонтекст: {context}"
        data = {
            "chat_id": ADMIN_USER_ID,
            "text": message,
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ Уведомление об ошибке отправлено администратору.")
        else:
            print(f"❌ Не удалось отправить уведомление: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления: {e}")

# --- Функции-обёртки для пайплайнов с уведомлениями ---
async def run_pipeline_wrapper():
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🔄 [{start_time}] Запуск обычного пайплайна...")
    try:
        await orchestrator.run_pipeline()
        print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Пайплайн завершён")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка в пайплайне: {error_msg}")
        import traceback
        traceback.print_exc()
        await send_error_notification(error_msg, "run_pipeline")
        return False

async def run_daily_digest_wrapper():
    print("🔄 Запуск ежедневного дайджеста...")
    try:
        result = await orchestrator.run_daily_digest()
        if result:
            print("✅ Дайджест успешно опубликован")
        else:
            print("❌ Дайджест не опубликован (нет новостей или ошибка)")
            await send_error_notification("Дайджест не опубликован (нет новостей или ошибка)", "daily_digest")
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка в дайджесте: {error_msg}")
        import traceback
        traceback.print_exc()
        await send_error_notification(error_msg, "daily_digest")
        return False

async def run_weekly_analytics_wrapper():
    print("🔄 Запуск еженедельной аналитики...")
    try:
        result = await orchestrator.run_weekly_analytics()
        if result:
            print("✅ Аналитика успешно опубликована")
        else:
            print("❌ Аналитика не опубликована (нет новостей или ошибка)")
            await send_error_notification("Аналитика не опубликована (нет новостей или ошибка)", "weekly_analytics")
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка в аналитике: {error_msg}")
        import traceback
        traceback.print_exc()
        await send_error_notification(error_msg, "weekly_analytics")
        return False

def run_pipeline_sync():
    asyncio.run(run_pipeline_wrapper())

def run_daily_digest_sync():
    asyncio.run(run_daily_digest_wrapper())

def run_weekly_analytics_sync():
    asyncio.run(run_weekly_analytics_wrapper())

# --- Обработчики команд бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Привет! Я — AI-ассистент канала AI-Pulse.\n\n"
        "Я могу:\n"
        "• 📄 /summary <url> — саммари статьи\n"
        "• 🛠 /tools <запрос> — подбор AI-инструментов\n"
        "• 💡 /ideas <тема> — генерация идей\n"
        "• 📰 /publish_now — ручная публикация новости\n"
        "• 📊 /daily_digest — ручной запуск дайджеста\n"
        "• 📈 /weekly_analytics — ручной запуск аналитики\n"
        "• 📋 /show_published — показать опубликованные URL\n"
        "• 📊 /stats — статистика канала\n"
        "• 💾 /export_published — получить файл с опубликованными URL"
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
        "/publish_now — ручной запуск публикации новости\n"
        "/daily_digest — ручной запуск ежедневного дайджеста\n"
        "/weekly_analytics — ручной запуск еженедельной аналитики\n"
        "/show_published — показать последние опубликованные URL\n"
        "/stats — статистика канала (подписчики, количество постов)\n"
        "/export_published — скачать файл с опубликованными URL"
    )
    await update.message.reply_text(help_text)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите ссылку после команды.")
        return
    url = context.args[0]
    if not urlparse(url).scheme:
        await update.message.reply_text("❌ Непохоже на ссылку.")
        return

    await update.message.reply_text("⏳ Получаю статью и делаю саммари...")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            await update.message.reply_text("❌ Не удалось загрузить страницу.")
            return
        raw_text = response.text
        clean_text = re.sub(r'<[^>]+>', ' ', raw_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()[:3000]
        prompt = f"Сделай краткое саммари (до 500 символов) этой статьи:\n\n{clean_text}\n\nВыдели главную мысль."
        summary_text = await ask_groq(prompt, "Ты — опытный редактор.")
        await update.message.reply_text(f"📄 Краткое содержание:\n\n{summary_text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Опишите задачу.")
        return
    query = " ".join(context.args)
    await update.message.reply_text("⏳ Ищу инструменты...")
    prompt = f"Предложи 3–5 AI-инструментов для задачи: {query}. Укажи, какие бесплатные, какие платные. Ответ на русском."
    result = await ask_groq(prompt, "Ты — эксперт по AI-инструментам.")
    await update.message.reply_text(f"🛠 Инструменты:\n\n{result}")

async def ideas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите тему.")
        return
    topic = " ".join(context.args)
    await update.message.reply_text("⏳ Генерирую идеи...")
    prompt = f"Сгенерируй 5 креативных идей для проекта на тему: {topic}. Описание и аудитория. Ответ на русском."
    result = await ask_groq(prompt, "Ты — креативный стратег.")
    await update.message.reply_text(f"💡 Идеи:\n\n{result}")

async def publish_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Запускаю публикацию новости...")
    success = await run_pipeline_wrapper()
    if success:
        await update.message.reply_text("✅ Публикация завершена! Проверьте канал.")
    else:
        await update.message.reply_text("❌ Публикация не удалась. Проверьте логи.")

async def daily_digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую ежедневный дайджест...")
    success = await run_daily_digest_wrapper()
    if success:
        await update.message.reply_text("✅ Дайджест опубликован!")
    else:
        await update.message.reply_text("❌ Дайджест не удалось опубликовать (нет новостей или ошибка).")

async def weekly_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую еженедельную аналитику...")
    success = await run_weekly_analytics_wrapper()
    if success:
        await update.message.reply_text("✅ Аналитика опубликована!")
    else:
        await update.message.reply_text("❌ Аналитика не удалась (нет новостей или ошибка).")

async def show_published(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'published_urls.json')
    if not os.path.exists(file_path):
        await update.message.reply_text("❌ Файл с опубликованными URL не найден.")
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = json.load(f)
        if not urls:
            await update.message.reply_text("📭 Список пуст.")
            return
        text = "📋 Опубликованные URL (последние 10):\n\n" + "\n".join(urls[-10:])
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def export_published(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет файл published_urls.json администратору"""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Эта команда доступна только администратору.")
        return
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'published_urls.json')
    if not os.path.exists(file_path):
        await update.message.reply_text("❌ Файл не найден.")
        return
    try:
        with open(file_path, 'rb') as f:
            await update.message.reply_document(document=f, filename='published_urls.json')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при отправке файла: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику канала (подписчики и количество постов)"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getChat"
        data = {"chat_id": f"@{CHANNEL_USERNAME}"}
        response = requests.post(url, data=data)
        result = response.json()
        if not result.get("ok"):
            await update.message.reply_text("❌ Не удалось получить статистику канала.")
            return

        chat_info = result.get("result", {})
        member_count = chat_info.get("member_count", "неизвестно")
        title = chat_info.get("title", "AI-Pulse")

        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'published_urls.json')
        posts_count = 0
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls = json.load(f)
                    posts_count = len(urls)
            except:
                posts_count = 0

        text = (
            f"📊 Статистика канала\n\n"
            f"📌 Название: {title}\n"
            f"👥 Подписчиков: {member_count}\n"
            f"📰 Опубликовано постов: {posts_count}\n"
            f"🔗 Ссылка: https://t.me/{CHANNEL_USERNAME}"
        )
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении статистики: {str(e)}")

# --- Основная функция ---
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("tools", tools))
    application.add_handler(CommandHandler("ideas", ideas))
    application.add_handler(CommandHandler("publish_now", publish_now))
    application.add_handler(CommandHandler("daily_digest", daily_digest))
    application.add_handler(CommandHandler("weekly_analytics", weekly_analytics))
    application.add_handler(CommandHandler("show_published", show_published))
    application.add_handler(CommandHandler("export_published", export_published))
    application.add_handler(CommandHandler("stats", stats))

    # --- Планировщик ---
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_pipeline_sync,
        trigger=IntervalTrigger(minutes=88),
        id="publish_news",
        replace_existing=True,
        next_run_time=datetime.now() + timedelta(seconds=15)
    )

    scheduler.add_job(
        run_daily_digest_sync,
        trigger=CronTrigger(hour=6, minute=0, timezone='Europe/Moscow'),
        id="daily_digest",
        replace_existing=True
    )

    scheduler.add_job(
        run_weekly_analytics_sync,
        trigger=CronTrigger(day_of_week='fri', hour=15, minute=0, timezone='Europe/Moscow'),
        id="weekly_analytics",
        replace_existing=True
    )

    scheduler.start()
    print("✅ Планировщик запущен:")
    print("   - Новости: каждые 88 минут")
    print("   - Дайджест: ежедневно в 9:00 МСК")
    print("   - Аналитика: по пятницам в 18:00 МСК")

    # Health check сервер
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"✅ Health check server running on port {port}")

    print("🤖 Бот запущен и ожидает команды...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()