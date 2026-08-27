# ============================================
# AI-PULSE AUTOMATIC FILE CREATOR
# ============================================

Write-Host "🤖 AI-Pulse: Создание всех файлов..." -ForegroundColor Cyan

# 1. .gitignore
@'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
.venv/

# Environment variables
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Logs
logs/
*.log

# Data
data/raw/*
data/processed/*
data/published/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/published/.gitkeep

# Database
*.db
*.sqlite3

# Session files
*.session
*.session-journal

# Secrets
secrets/
*.pem
*.key

# Coverage
.coverage
htmlcov/
.pytest_cache/
.tox/

# Docker
.docker/

# Temporary
tmp/
temp/
*.tmp
'@ | Out-File -FilePath .gitignore -Encoding UTF8

# 2. .env.example
@'
# TELEGRAM
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@ai_pulse_ai

# DATABASE
DATABASE_URL=postgresql://ai_pulse:password@localhost:5432/ai_pulse
REDIS_URL=redis://localhost:6379/0

# AI SERVICES (Groq - Free)
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Google Gemini (Free)
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-1.5-flash

# OpenAI (Optional)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo-preview

# Reddit API
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=ai-pulse-bot/1.0

# Application
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=True

# Schedule
SCOUT_INTERVAL_HOURS=2
DAILY_DIGEST_HOUR=9
WEEKLY_ANALYTICS_DAY=fri
WEEKLY_ANALYTICS_HOUR=18

# Content
MIN_SCORE_FOR_PUBLICATION=60
MAX_POSTS_PER_DAY=5
LANGUAGE=ru
'@ | Out-File -FilePath .env.example -Encoding UTF8

# 3. requirements.txt
@'
# AI-PULSE DEPENDENCIES
aiohttp==3.9.1
python-telegram-bot==20.7
telethon==1.34.0
groq==0.4.2
google-generativeai==0.3.2
openai==1.10.0
huggingface-hub==0.20.3
sentence-transformers==2.2.2
feedparser==6.0.10
beautifulsoup4==4.12.2
requests==2.31.0
praw==7.7.1
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
redis==5.0.1
apscheduler==3.10.4
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
loguru==0.7.2
pytest==7.4.4
pytest-asyncio==0.21.2
'@ | Out-File -FilePath requirements.txt -Encoding UTF8

# 4. README.md
@'
# AI-Pulse

> AI-Driven Telegram Channel about AI & Technology

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Initialize database
psql -U postgres -c "CREATE DATABASE ai_pulse;"
psql -U postgres -d ai_pulse -f database/migrations/001_initial.sql

# Run
python -m orchestrator.main
