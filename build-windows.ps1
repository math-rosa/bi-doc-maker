param(
    [switch]$SkipNpmInstall
)

$ErrorActionPreference = "Stop"

function Assert-LastExitCode {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step falhou (codigo $LASTEXITCODE)."
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $Root ".product-venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$TauriDir = Join-Path $Root "frond-end-app"
$SidecarName = "documentador-core"
$BinariesDir = Join-Path $TauriDir "src-tauri\binaries"

function Invoke-SystemPython {
    param([string[]]$Arguments)

    $PyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($PyLauncher) {
        & py -3 @Arguments
        return
    }

    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) {
        & python @Arguments
        return
    }

    throw "Python nao encontrado. Instale Python 3 e deixe-o disponivel no PATH ou via py launcher."
}

function Get-RustHostTriple {
    $Rustc = Get-Command rustc -ErrorAction SilentlyContinue
    if (-not $Rustc) {
        return "x86_64-pc-windows-msvc"
    }

    $HostLine = & rustc -Vv | Select-String "host:" | Select-Object -First 1
    if (-not $HostLine) {
        return "x86_64-pc-windows-msvc"
    }

    return (($HostLine.Line -split "\s+")[1]).Trim()
}

Write-Host "==> Criando ambiente Python de produto"
Invoke-SystemPython @("-m", "venv", $VenvDir)
Assert-LastExitCode "Criacao do ambiente Python (venv)"

Write-Host "==> Instalando dependencias Python"
& $VenvPython -m pip install --upgrade pip
Assert-LastExitCode "Upgrade do pip"
& $VenvPython -m pip install -r (Join-Path $Root "requirements.txt") pyinstaller
Assert-LastExitCode "Instalacao de dependencias Python"

Write-Host "==> Gerando sidecar Python com PyInstaller"
& $VenvPython -m PyInstaller `
    --clean `
    --noconfirm `
    --onefile `
    --noupx `
    --name $SidecarName `
    --exclude-module playwright `
    --collect-all markdown `
    --collect-all docx `
    (Join-Path $Root "documentador_core_cli.py")
Assert-LastExitCode "PyInstaller"

$Triple = Get-RustHostTriple
$DistExe = Join-Path $Root "dist\$SidecarName.exe"
$SidecarExe = Join-Path $BinariesDir "$SidecarName-$Triple.exe"

if (-not (Test-Path $DistExe)) {
    throw "PyInstaller nao gerou $DistExe"
}

Write-Host "==> Copiando sidecar para $SidecarExe"
New-Item -ItemType Directory -Force $BinariesDir | Out-Null
Copy-Item -Force $DistExe $SidecarExe

Push-Location $TauriDir
try {
    if (-not $SkipNpmInstall) {
        Write-Host "==> Instalando dependencias Node"
        npm.cmd ci
        Assert-LastExitCode "npm ci"
    }

    Write-Host "==> Gerando instalador Tauri"
    npm.cmd run tauri:build
    Assert-LastExitCode "npm run tauri:build"
}
finally {
    Pop-Location
}

Write-Host "==> Build Windows concluido"
