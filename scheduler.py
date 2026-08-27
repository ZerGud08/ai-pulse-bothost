from apscheduler.schedulers.blocking import BlockingScheduler
from orchestrator.main import Orchestrator
import asyncio
from utils.logger import logger

scheduler = BlockingScheduler()

async def job():
    orchestrator = Orchestrator()
    await orchestrator.start()

def run_job():
    asyncio.run(job())

# Запуск каждые 3 часа
scheduler.add_job(run_job, 'interval', hours=3, id='ai_pulse_job')

logger.info("🚀 Планировщик запущен. Будет публиковать новости каждые 3 часа.")
scheduler.start()