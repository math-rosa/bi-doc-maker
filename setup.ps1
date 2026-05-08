Write-Host "Iniciando configuracao do ambiente para o BI Doc Maker..." -ForegroundColor Cyan
python -m venv venv

Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

Write-Host "Instalando dependencias do requirements.txt..." -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Configuracao concluida com sucesso!" -ForegroundColor Green
Write-Host "Para usar a CLI Python, rode:" -ForegroundColor Yellow
Write-Host ".\venv\Scripts\Activate.ps1"
Write-Host "python documentador_core_cli.py export --project `"C:\caminho\ProjetoPBIP`" --output-dir `"C:\saida`" --formats md,docx,html --json"
