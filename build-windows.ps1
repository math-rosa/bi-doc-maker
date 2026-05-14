param(
    [switch]$SkipNpmInstall,
    # Opcional: thumbprint SHA1 do certificado Authenticode no Windows Cert Store.
    # Se informado, assina o sidecar Python E o MSI final via signtool.
    # Requer Windows SDK instalado (signtool.exe no PATH).
    [string]$CertificateThumbprint = "",
    # URL do servidor de timestamp RFC 3161 (gratuitos: sectigo, digicert, globalsign).
    [string]$TimestampUrl = "http://timestamp.sectigo.com"
)

$ErrorActionPreference = "Stop"

function Assert-LastExitCode {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step falhou (codigo $LASTEXITCODE)."
    }
}

function Invoke-Signtool {
    param(
        [string]$Path,
        [string]$Thumbprint,
        [string]$TsaUrl,
        [string]$Description
    )

    if ([string]::IsNullOrWhiteSpace($Thumbprint)) {
        return
    }

    $signtool = Get-Command signtool -ErrorAction SilentlyContinue
    if (-not $signtool) {
        throw "signtool.exe nao encontrado no PATH. Instale Windows SDK ou adicione signtool ao PATH."
    }

    Write-Host "==> Assinando $Description ($Path)"
    & signtool sign /sha1 $Thumbprint /fd sha256 /tr $TsaUrl /td sha256 /d "BI Doc Maker" $Path
    Assert-LastExitCode "Assinatura de $Description"
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $Root ".product-venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$TauriDir = Join-Path $Root "frond-end-app"
$SidecarName = "documentador-core"
$BinariesDir = Join-Path $TauriDir "src-tauri\binaries"
$VersionInfo = Join-Path $Root "version-info.txt"

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
$PyInstallerArgs = @(
    "-m", "PyInstaller",
    "--clean",
    "--noconfirm",
    "--onefile",
    "--noupx",
    "--name", $SidecarName,
    "--exclude-module", "playwright",
    "--collect-all", "markdown",
    "--collect-all", "docx"
)

if (Test-Path $VersionInfo) {
    Write-Host "    (usando metadados de $VersionInfo)"
    $PyInstallerArgs += @("--version-file", $VersionInfo)
}
else {
    Write-Host "    [AVISO] version-info.txt nao encontrado; sidecar saira sem metadados"
}

$PyInstallerArgs += (Join-Path $Root "documentador_core_cli.py")
& $VenvPython @PyInstallerArgs
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

Invoke-Signtool -Path $SidecarExe -Thumbprint $CertificateThumbprint -TsaUrl $TimestampUrl -Description "sidecar Python"

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

if (-not [string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
    $MsiDir = Join-Path $TauriDir "src-tauri\target\release\bundle\msi"
    $MsiFiles = Get-ChildItem -Path $MsiDir -Filter "*.msi" -ErrorAction SilentlyContinue
    foreach ($msi in $MsiFiles) {
        Invoke-Signtool -Path $msi.FullName -Thumbprint $CertificateThumbprint -TsaUrl $TimestampUrl -Description "MSI"
    }
}

Write-Host "==> Build Windows concluido"
if ([string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
    Write-Host "    [INFO] Build sem assinatura. Para assinar, rode com -CertificateThumbprint <SHA1>"
}
