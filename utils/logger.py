import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ai-pulse")

# Добавляем метод success для удобства
def success(self, msg):
    self.info(f"✅ {msg}")
logger.success = success.__get__(logger)