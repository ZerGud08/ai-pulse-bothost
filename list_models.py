import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Запрашиваем список всех доступных моделей
models = client.models.list()

print("Доступные модели:")
for model in models.data:
    print(f"- {model.id}")