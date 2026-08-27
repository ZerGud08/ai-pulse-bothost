import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

def send_test():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": f"@{CHANNEL_USERNAME}",
        "text": "? Тест публикации через бота!",
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    print(response.json())

if __name__ == "__main__":
    send_test()