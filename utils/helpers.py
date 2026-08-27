def clean_text(text):
    """Очистка текста от HTML-тегов и лишних пробелов"""
    import re
    text = re.sub(r'<[^>]+>', '', text)  # удаляем HTML
    text = re.sub(r'\s+', ' ', text).strip()
    return text