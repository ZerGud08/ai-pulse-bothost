"""Publisher Agent - publishes to Telegram via Bot API"""
import os
import requests
from dotenv import load_dotenv
from utils.logger import logger

class PublisherAgent:
    """Agent for publishing posts to Telegram channel via bot"""

    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.channel_username = os.getenv("CHANNEL_USERNAME", "ai_pulse_ai")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        logger.info("Publisher initialized (bot)")

    async def publish(self, post: dict) -> bool:
        content = post.get("content", "")
        if not content:
            logger.error("Empty content, nothing to publish")
            return False

        chat_id = f"@{self.channel_username}"
        if not await self._send_message(chat_id, content):
            logger.warning(f"Failed to send to @{self.channel_username}, trying with channel ID...")
            # Если хотите использовать числовой ID, раскомментируйте и укажите свой
            # chat_id = -1001234567890
            # return await self._send_message(chat_id, content)
            return False
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
            # Используем json= для корректной передачи вложенных объектов
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