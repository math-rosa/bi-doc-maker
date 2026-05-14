param(
    [string]$VenvDir = ".product-venv",
    [switch]$Force
)

# rebuild-pyinstaller.ps1
#
# Rebuilda o bootloader do PyInstaller a partir do codigo-fonte e instala
# essa versao customizada no venv do produto (.product-venv).
#
# Por que? O bootloader stock do PyInstaller (binario compilado distribuido
# via pip) tem um padrao de bytes que ficou conhecido por antivirus heuristicos
# (Avast, Trend Micro, McAfee, Kaspersky). Eles assumem PyInstaller = malware
# Python disfarcado e flagam.
#
# Buildar localmente produz um bootloader com hash diferente, que nao bate
# com nenhuma assinatura heuristica conhecida. Reduz drasticamente alertas
# em scans de AV.
#
# Pre-requisitos:
#   - Visual Studio Build Tools (compilador C/C++ MSVC)
#   - git
#   - .product-venv ja criado (rode .\build-windows.ps1 antes)
#
# Uso:
#   .\rebuild-pyinstaller.ps1            # primeira execucao
#   .\rebuild-pyinstaller.ps1 -Force     # forca novo clone + rebuild
#
# Depois disso, todo .\build-windows.ps1 vai usar o PyInstaller customizado.

$ErrorActionPreference = "Stop"

function Assert-LastExitCode {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step falhou (codigo $LASTEXITCODE)."
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $Root "$VenvDir\Scripts\python.exe"
$SrcDir = Join-Path $Root ".pyinstaller-src"

if (-not (Test-Path $VenvPython)) {
    throw "Ambiente $VenvDir nao encontrado em $Root. Rode .\build-windows.ps1 primeiro."
}

$Git = Get-Command git -ErrorAction SilentlyContinue
if (-not $Git) {
    throw "git nao encontrado no PATH. Instale Git for Windows."
}

if ($Force -and (Test-Path $SrcDir)) {
    Write-Host "==> Removendo .pyinstaller-src/ (-Force)"
    Remove-Item -Recurse -Force $SrcDir
}

if (-not (Test-Path $SrcDir)) {
    Write-Host "==> Clonando PyInstaller upstream em $SrcDir"
    & git clone --depth 1 https://github.com/pyinstaller/pyinstaller.git $SrcDir
    Assert-LastExitCode "git clone do PyInstaller"
}

Write-Host "==> Buildando bootloader localmente"
Write-Host "    (requer Visual Studio Build Tools com C++ instalado)"
Push-Location (Join-Path $SrcDir "bootloader")
try {
    & $VenvPython ./waf all
    Assert-LastExitCode "Build do bootloader (verifique se VS Build Tools esta instalado)"
}
finally {
    Pop-Location
}

Write-Host "==> Removendo PyInstaller pip-instalado do venv"
& $VenvPython -m pip uninstall -y pyinstaller | Out-Null

Write-Host "==> Instalando PyInstaller customizado a partir de $SrcDir"
& $VenvPython -m pip install --no-deps $SrcDir
Assert-LastExitCode "pip install do PyInstaller customizado"

Write-Host ""
Write-Host "==> Pronto."
Write-Host "    O bootloader rebuildado fica em:"
Write-Host "    $SrcDir\PyInstaller\bootloader\Windows-64bit-intel\run.exe"
Write-Host ""
Write-Host "    Hash diferente do bootloader stock = bypass de assinaturas"
Write-Host "    heuristicas de AV. Rode .\build-windows.ps1 normalmente."
