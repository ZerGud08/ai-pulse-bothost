$content = @'
# AI-Pulse

> AI-Driven Telegram Channel about AI & Technology

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database
psql -U postgres -c "CREATE DATABASE ai_pulse;"
psql -U postgres -d ai_pulse -f database/migrations/001_initial.sql

# Run
python -m orchestrator.main
