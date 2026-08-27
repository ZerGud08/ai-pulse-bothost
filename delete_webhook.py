import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("INTERACTIVE_BOT_TOKEN")
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
response = requests.post(url)
print(response.json())