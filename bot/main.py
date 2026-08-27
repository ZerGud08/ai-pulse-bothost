#!/usr/bin/env python
"""Интерактивный бот для канала AI-Pulse"""
import os
import re
import sys
import asyncio
import requests
from urllib.parse import urlparse

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from dotenv import load_dotenv
from groq import Groq

# Загружаем переменные из .env (если файл существует)
load_dotenv()

# --- ОТЛАДОЧНЫЙ ВЫВОД (убедимся, что переменные видны) ---
print("=== DEBUG: Переменные окружения ===")
# Выводим только ключи, чтобы не светить значениями
env_keys = list(os.environ.keys())
print(f"Доступные ключи: {env_keys}")

# Проверяем наличие наших ключей
token_env = os.getenv("INTERACTIVE_BOT_TOKEN")
token_env2 = os.getenv("TELEGRAM_BOT_TOKEN")
groq_env = os.getenv("GROQ_API_KEY")
print(f"INTERACTIVE_BOT_TOKEN: {'НАЙДЕН' if token_env else 'ОТСУТСТВУЕТ'}")
print(f"TELEGRAM_BOT_TOKEN: {'НАЙДЕН' if token_env2 else 'ОТСУТСТВУЕТ'}")
print(f"GROQ_API_KEY: {'НАЙДЕН' if groq_env else 'ОТСУТСТВУЕТ'}")
print("=== КОНЕЦ ОТЛАДКИ ===\n")

# --- Получение токена бота ---
# Пробуем взять из INTERACTIVE_BOT_TOKEN, если нет — из TELEGRAM_BOT_TOKEN
TOKEN = token_env or token_env2
if not TOKEN:
    print("❌ Ошибка: не найден токен бота ни в INTERACTIVE_BOT_TOKEN, ни в TELEGRAM_BOT_TOKEN.")
    print("Убедитесь, что переменные окружения установлены на Render.")
    sys.exit(1)

GROQ_API_KEY = groq_env
if not GROQ_API_KEY:
    print("❌ Ошибка: не найден GROQ_API_KEY.")
    sys.exit(1)

# Инициализируем Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# ---- Вспомогательные функции для работы с Groq ----

async def ask_groq(prompt: str, system_prompt: str = "Ты — полезный AI-ассистент.") -> str:
    """Отправляет запрос к Groq и возвращает ответ"""
    try:
        response = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",  # можно заменить на другую доступную модель
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

# ---- Обработчики команд ----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
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
    """Список команд"""
    help_text = (
        "📌 Доступные команды:\n\n"
        "/start — приветствие\n"
        "/help — эта справка\n"
        "/summary <ссылка> — краткое содержание статьи\n"
        "/tools <запрос> — подбор AI-инструментов\n"
        "/ideas <тема> — генерация идей\n\n"
        "Примеры:\n"
        "/summary https://openai.com/blog/gpt-4-1\n"
        "/tools хочу сделать чат-бота для поддержки\n"
        "/ideas сервис для автоматического перевода видео"
    )
    await update.message.reply_text(help_text)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /summary — делает саммари по ссылке"""
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
    """Обработчик /tools — подбор AI-инструментов"""
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
    """Обработчик /ideas — генерация идей"""
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

# ---- Запуск бота ----

def main():
    """Точка входа"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("tools", tools))
    application.add_handler(CommandHandler("ideas", ideas))

    print("🤖 Бот запущен и ожидает команды...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()