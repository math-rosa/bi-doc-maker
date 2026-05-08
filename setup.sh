#!/bin/bash

echo -e "\e[36mIniciando configuracao do ambiente para o BI Doc Maker...\e[0m"
python3 -m venv venv

echo -e "\e[36mAtivando ambiente virtual...\e[0m"
source venv/bin/activate

echo -e "\e[36mInstalando dependencias do requirements.txt...\e[0m"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo -e "\e[32mConfiguracao concluida com sucesso!\e[0m"
echo -e "\e[33mPara usar a CLI Python, rode:\e[0m"
echo "source venv/bin/activate"
echo "python documentador_core_cli.py export --project /caminho/ProjetoPBIP --output-dir /caminho/saida --formats md,docx,html --json"
