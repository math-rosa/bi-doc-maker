@echo off
chcp 65001 > nul
title Iniciar Documentador Power BI

echo ===================================================
echo     Documentador de Projetos Power BI (.pbip)
echo ===================================================
echo.

:: Verifica se o Python está instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] O Python nao foi encontrado neste computador!
    echo Por favor, instale o Python 3.10 ou superior antes de continuar.
    echo Baixe em: https://www.python.org/downloads/
    echo IMPORTANTE: Lembre-se de marcar a caixa "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

:: Verifica/Cria o ambiente virtual
IF NOT EXIST "venv" (
    echo [INFO] Primeira execucao detectada. Configurando ambiente isolado...
    echo [INFO] Isso pode levar um ou dois minutos. Por favor, aguarde.
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)

:: Ativa o ambiente virtual
call venv\Scripts\activate

:: Atualiza o pip silenciosamente
python -m pip install --upgrade pip -q

:: Instala as dependencias
echo [INFO] Verificando bibliotecas (python-docx, playwright, etc)...
pip install -r requirements.txt -q
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao instalar as bibliotecas Python.
    pause
    exit /b 1
)

:: Verifica/Instala o Chromium para o Playwright
echo [INFO] Verificando navegador embutido para renderizar PDFs/Imagens...
playwright install chromium
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao instalar o navegador embutido (Playwright).
    pause
    exit /b 1
)

echo.
echo [SUCESSO] Tudo pronto! Iniciando a interface...
echo (Esta janela preta precisa ficar aberta enquanto voce usa o programa)
echo.

:: Inicia a GUI
python documentador_gui.py

:: Desativa o venv apos fechar a interface
deactivate
