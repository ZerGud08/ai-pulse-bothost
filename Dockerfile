@' FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt . RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/processed data/published logs

CMD ["python", "-m", "orchestrator.main"] '@ | Out-File -FilePath Dockerfile -Encoding UTF8