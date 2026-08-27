from groq import Groq

# Инициализация клиента
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

completion = client.chat.completions.create(
    model="qwen/qwen3.6-27b",
    messages=[{"role": "user", "content": "Объясни, что такое квантовая запутанность"}],
    temperature=0.7,
)

print(completion.choices[0].message.content)