import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Ключ загружен: {api_key[:10]}...{api_key[-4:] if api_key else 'НЕТ КЛЮЧА!'}")

client = Groq(api_key=api_key)
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": "Привет! Напиши одно слово."}],
    max_tokens=10
)
print("✅ Ответ:", response.choices[0].message.content)