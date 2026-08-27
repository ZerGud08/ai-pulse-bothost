import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

def send_test():
    if not BOT_TOKEN:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не найден в .env")
        return
    if not CHANNEL_USERNAME:
        print("❌ Ошибка: CHANNEL_USERNAME не найден в .env")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": f"@{CHANNEL_USERNAME}",
        "text": "✅ Тестовое сообщение от бота!",
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        result = response.json()
        if result.get("ok"):
            print("✅ Сообщение успешно отправлено в канал!")
        else:
            print("❌ Ошибка:", result)
    except Exception as e:
        print("❌ Исключение:", e)

if __name__ == "__main__":
    send_test()