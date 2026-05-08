@echo off
chcp 65001 > nul
title Setup - BI Doc Maker

echo ===================================================
echo     Configuracao do Ambiente - BI Doc Maker
echo ===================================================
echo.

:: Verifica se o Python está instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] O Python nao foi encontrado neste computador!
    echo Por favor, instale o Python antes de continuar.
    echo.
    pause
    exit /b 1
)

:: Cria ambiente virtual
IF NOT EXIST "venv" (
    echo [1/3] Criando ambiente virtual (venv)...
    python -m venv venv
) ELSE (
    echo [1/3] Ambiente virtual (venv) ja existe.
)

:: Ativa o ambiente
echo [2/3] Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Instala pip e dependencias
echo [3/3] Instalando dependencias do requirements.txt...
python -m pip install --upgrade pip -q
pip install -r requirements.txt

echo.
echo [SUCESSO] Configuracao concluida com sucesso!
echo Voce ja pode usar a CLI Python ou gerar o app com build-windows.ps1.
echo.
pause
