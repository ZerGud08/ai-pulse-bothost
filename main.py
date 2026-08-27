#!/usr/bin/env python
"""
Главный файл для Bothost — запускает интерактивного бота.
"""
import sys
import os

# Добавляем текущую папку в путь, чтобы находились все модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем функцию запуска бота из bot/main.py
from bot.main import main as bot_main

if __name__ == "__main__":
    bot_main()