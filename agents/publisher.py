"""Publisher Agent - publishes to Telegram via Bot API with alternating image styles"""
import os
import json
import random
import requests
from dotenv import load_dotenv
from utils.logger import logger

class PublisherAgent:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.channel_username = os.getenv("CHANNEL_USERNAME", "ai_pulse_ai")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.published_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'published_urls.json')
        self.counter_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'style_counter.json')
        logger.info(f"Publisher: файл опубликованных URL: {self.published_file}")

        self.color_palettes = [
            "neon blue and purple", "warm orange and gold", "cool teal and cyan",
            "vibrant magenta and yellow", "electric green and blue", "deep red and black",
            "pastel pink and lavender", "metallic silver and blue"
        ]
        self.art_styles = [
            "futuristic digital art", "cyberpunk style", "minimalist tech illustration",
            "abstract geometric", "sci-fi concept art", "glowing neon lines",
            "modern flat design", "3D rendering with glowing effects"
        ]
        self.artists = [
            "inspired by Syd Mead", "inspired by Beeple", "inspired by Zaha Hadid",
            "in the style of Bauhaus", "inspired by cyberpunk aesthetics"
        ]

    def _load_published_urls(self):
        if os.path.exists(self.published_file):
            try:
                with open(self.published_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_published_urls(self, urls):
        os.makedirs(os.path.dirname(self.published_file), exist_ok=True)
        with open(self.published_file, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=2)
        logger.info(f"Publisher: сохранено {len(urls)} URL в файл")

    def _add_published_url(self, url):
        if not url:
            return
        urls = self._load_published_urls()
        if url not in urls:
            urls.append(url)
            self._save_published_urls(urls)
            logger.info(f"Publisher: URL сохранён: {url}")

    def _get_style_counter(self):
        if os.path.exists(self.counter_file):
            try:
                with open(self.counter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('counter', 0)
            except:
                return 0
        return 0

    def _save_style_counter(self, counter):
        os.makedirs(os.path.dirname(self.counter_file), exist_ok=True)
        with open(self.counter_file, 'w', encoding='utf-8') as f:
            json.dump({'counter': counter}, f, ensure_ascii=False, indent=2)
        logger.info(f"Publisher: счётчик стилей обновлён: {counter}")

    def _generate_image_prompt(self, news_title: str, news_summary: str) -> str:
        title_part = news_title[:40].strip()
        summary_part = news_summary[:50].strip()
        if len(summary_part) < 10:
            summary_part = "technology concept"

        color = random.choice(self.color_palettes)
        style = random.choice(self.art_styles)
        artist = random.choice(self.artists)

        prompt = (
            f"Abstract illustration, {style}, {color}, "
            f"representing '{title_part}' concept, "
            f"featuring {summary_part}, {artist}, "
            f"futuristic, high detail, 4k, no text"
        )
        logger.info(f"Сгенерирован промпт для картинки: {prompt[:120]}...")
        return prompt

    async def publish(self, post: dict) -> bool:
        content = post.get("content", "")
        if not content:
            logger.error("Empty content, nothing to publish")
            return False

        news = post.get("news", {})
        title = news.get('title', '')
        summary = news.get('summary', '')

        counter = self._get_style_counter()
        use_ai_image = (counter % 2 == 1)
        logger.info(f"Стиль публикации: {'AI-картинка' if use_ai_image else 'превью из статьи'} (счётчик={counter})")

        chat_id = f"@{self.channel_username}"

        if use_ai_image:
            try:
                image_prompt = self._generate_image_prompt(title, summary)
                encoded_prompt = image_prompt.replace(' ', '%20')
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=512&nologo=true&seed={random.randint(1000, 9999)}"
                logger.info(f"Запрос картинки (seed): {image_url[:120]}...")

                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    files = {'photo': ('cover.jpg', response.content)}
                    data = {
                        'chat_id': chat_id,
                        'caption': content,
                        'parse_mode': 'HTML',
                        'disable_web_page_preview': True
                    }
                    result = requests.post(f"{self.base_url}/sendPhoto", files=files, data=data)
                    result_json = result.json()
                    if result_json.get('ok'):
                        logger.success(f"Published with AI image to {chat_id}: {content[:80]}...")
                        if news.get('url'):
                            self._add_published_url(news['url'])
                        self._save_style_counter(counter + 1)
                        return True
                    else:
                        logger.error(f"Error sending photo: {result_json}")
                        return await self._send_text_message(chat_id, content, news)
                else:
                    logger.error(f"Pollinations.ai error: {response.status_code}")
                    return await self._send_text_message(chat_id, content, news)
            except Exception as e:
                logger.error(f"Exception during AI image generation: {e}")
                return await self._send_text_message(chat_id, content, news)
        else:
            success = await self._send_text_message(chat_id, content, news)
            if success:
                self._save_style_counter(counter + 1)
            return success

    async def _send_text_message(self, chat_id: str, content: str, news: dict) -> bool:
        try:
            data = {
                "chat_id": chat_id,
                "text": content,
                "parse_mode": "HTML",
                "link_preview_options": {
                    "prefer_large_media": True,
                    "prefer_small_media": False,
                    "show_above_text": False
                }
            }
            response = requests.post(f"{self.base_url}/sendMessage", json=data, timeout=30)
            result = response.json()
            if result.get("ok"):
                logger.success(f"Published text to {chat_id}: {content[:80]}...")
                if news.get('url'):
                    self._add_published_url(news['url'])
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            return False