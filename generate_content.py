from anthropic import Anthropic, ResponseChoice

# Замените 'ВАШ_API_КЛЮЧ' на ваш фактический API ключ
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Anthropic(api_key=api_key)

def create_content(title, summary):
    prompt = f'Название статьи: {title}\n\nТекст статьи: {summary}'
    response = client.completion(prompt=prompt)
    return response.text

# Пример использования
title = 'Искусственный интеллект в медицине'
summary = 'Развитие искусственного интеллекта приводит к значимым изменениям в медицине.'
content = create_content(title, summary)
print(content)

