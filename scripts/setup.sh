@' #!/bin/bash echo "AI-Pulse Setup" python -m venv venv source venv/bin/activate pip install -r requirements.txt cp .env.example .env echo "Edit .env file!" '@ | Out-File -FilePath scripts/setup.sh -Encoding UTF8

Write-Host "=" -ForegroundColor Cyan Write-Host "🎉 ALL FILES CREATED SUCCESSFULLY!" -ForegroundColor Green Write-Host "=" -ForegroundColor Cyan Write-Host "" Write-Host "Next steps:" -ForegroundColor Yellow Write-Host "1. Edit .env file with your API keys" -ForegroundColor White Write-Host "2. Install dependencies: pip install -r requirements.txt" -ForegroundColor White Write-Host "3. Test Scout: python agents/scout.py" -ForegroundColor White Write-Host "4. Run: python -m orchestrator.main" -ForegroundColor White


### Шаг 3: Запустите скрипт

```powershell
# Разрешите выполнение скриптов (один раз)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Запустите скрипт
.\create-all-files.ps1