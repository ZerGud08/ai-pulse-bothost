import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("INTERACTIVE_BOT_TOKEN")

# Замените на ваш Telegram ID (можно узнать у @userinfobot)
YOUR_USER_ID = 946283881  # <-- ВСТАВЬТЕ СВОЙ ID

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {
    "chat_id": YOUR_USER_ID,
    "text": "Привет! Это тест от бота."
}
response = requests.post(url, data=data)
print(response.status_code)
print(response.json())