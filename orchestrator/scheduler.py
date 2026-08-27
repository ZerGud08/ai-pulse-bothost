"""Scheduler for orchestrator"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def create_scheduler():
    """Create and return scheduler instance"""
    return AsyncIOScheduler()
