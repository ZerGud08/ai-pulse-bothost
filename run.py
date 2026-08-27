"""Run script"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_agent(name):
    if name == "scout":
        from agents.scout import ScoutAgent
        scout = ScoutAgent()
        asyncio.run(scout.fetch_all_sources())
    elif name == "curator":
        print("Curator test")
    elif name == "all":
        from orchestrator.main import Orchestrator
        asyncio.run(Orchestrator().start())
    else:
        print("Unknown: " + name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py [scout|curator|all]")
    else:
        run_agent(sys.argv[1])
