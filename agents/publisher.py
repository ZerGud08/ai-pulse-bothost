"""Publisher Agent - publishes to Telegram via Bot API and tracks published URLs"""
import os
import json
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
        logger.info("Publisher initialized (bot)")

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

    def _add_published_url(self, url):
        if not url:
            return
        urls = self._load_published_urls()
        if url not in urls:
            urls.append(url)
            self._save_published_urls(urls)
            logger.info(f"Publisher: URL сохранён как опубликованный: {url}")

    async def publish(self, post: dict) -> bool:
        content = post.get("content", "")
        if not content:
            logger.error("Empty content, nothing to publish")
            return False

        chat_id = f"@{self.channel_username}"
        if not await self._send_message(chat_id, content):
            logger.warning(f"Failed to send to @{self.channel_username}, trying with channel ID...")
            return False

        # После успешной публикации сохраняем URL новости
        news = post.get("news", {})
        url = news.get("url")
        if url:
            self._add_published_url(url)
        return True

    async def _send_message(self, chat_id: str, content: str) -> bool:
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
                logger.success(f"Published to {chat_id}: {content[:80]}...")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False
        except Exception as e:
            logger.error(f"Failed to publish: {e}")
            return False