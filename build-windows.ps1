param(
    [switch]$SkipNpmInstall,
    # Opcional: thumbprint SHA1 do certificado Authenticode no Windows Cert Store.
    # Se informado, assina o sidecar Python E o MSI final via signtool.
    # Requer Windows SDK instalado (signtool.exe no PATH).
    [string]$CertificateThumbprint = "",
    # URL do servidor de timestamp RFC 3161 (gratuitos: sectigo, digicert, globalsign).
    [string]$TimestampUrl = "http://timestamp.sectigo.com",
    # Pula a geração do ZIP portatil (so MSI).
    [switch]$SkipPortable
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

    # Sanity check: version-info.txt deve bater com tauri.conf.json. Drift
    # silencioso (ja aconteceu na v0.9.0) faz o sidecar.exe sair com versao
    # antiga embutida, confundindo telemetria e atenuando o argumento
    # anti-falso-positivo de antivirus ("metadata coerente = menos suspeito").
    $TauriConfPath = Join-Path $TauriDir "src-tauri\tauri.conf.json"
    if (Test-Path $TauriConfPath) {
        try {
            $TauriVersion = (Get-Content $TauriConfPath -Raw | ConvertFrom-Json).package.version
            $InfoText = Get-Content $VersionInfo -Raw
            if ($InfoText -notmatch [regex]::Escape("u'$TauriVersion'")) {
                throw "version-info.txt nao bate com tauri.conf.json (esperado '$TauriVersion'). Atualize filevers/prodvers/FileVersion/ProductVersion."
            }
        }
        catch [System.Management.Automation.RuntimeException] {
            throw
        }
        catch {
            Write-Host "    [AVISO] Nao foi possivel validar versao em $VersionInfo : $_"
        }
    }
}
else {
    Write-Host "    [AVISO] version-info.txt nao encontrado; sidecar saira sem metadados"
}

$PyInstallerArgs += (Join-Path $Root "documentador_core_cli.py")
# Workaround: PowerShell 5.1 com $ErrorActionPreference=Stop trata stderr
# de native commands como erro. PyInstaller 6+ emite INFO no stderr.
# Roda com EAP=Continue para suportar isso, depois verifica exit code.
$PrevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    & $VenvPython @PyInstallerArgs
}
finally {
    $ErrorActionPreference = $PrevEAP
}
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
    $PrevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        if (-not $SkipNpmInstall) {
            Write-Host "==> Instalando dependencias Node"
            # Usamos `npm install` em vez de `npm ci` porque `ci` apaga
            # node_modules antes de reinstalar — isso falha com EPERM quando
            # binarios nativos (.node) estao com handle aberto por Defender/
            # OneDrive. `install` faz unlink incremental (mais tolerante a lock).
            npm.cmd install
            $NpmCiCode = $LASTEXITCODE
        }
        else {
            $NpmCiCode = 0
        }

        Write-Host "==> Gerando instalador Tauri"
        npm.cmd run tauri:build
        $TauriBuildCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PrevEAP
    }

    if ($NpmCiCode -ne 0) { throw "npm install falhou (codigo $NpmCiCode)." }
    if ($TauriBuildCode -ne 0) { throw "npm run tauri:build falhou (codigo $TauriBuildCode)." }
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

# ============================================================
# Target portatil: ZIP com tudo necessario, sem instalacao
# ============================================================
if (-not $SkipPortable) {
    Write-Host "==> Gerando ZIP portatil"

    # Versao vem do tauri.conf.json (fonte de verdade do bundle)
    $TauriConfPath = Join-Path $TauriDir "src-tauri\tauri.conf.json"
    $TauriConf = Get-Content $TauriConfPath -Raw | ConvertFrom-Json
    $AppVersion = $TauriConf.package.version

    $ReleaseDir = Join-Path $TauriDir "src-tauri\target\release"
    $AppExeSource = Join-Path $ReleaseDir "BI Doc Maker.exe"
    $SidecarReleaseSource = Join-Path $ReleaseDir "$SidecarName.exe"

    if (-not (Test-Path $AppExeSource)) {
        throw "App principal nao encontrado em $AppExeSource"
    }
    if (-not (Test-Path $SidecarReleaseSource)) {
        throw "Sidecar nao encontrado em $SidecarReleaseSource (esperado depois do tauri:build)"
    }

    $PortableName = "BI-Doc-Maker-$AppVersion-portable-x64"
    $DistDir = Join-Path $Root "dist"
    $PortableStageDir = Join-Path $DistDir $PortableName
    $PortableZip = Join-Path $DistDir "$PortableName.zip"

    # Limpa staging e zip previos
    if (Test-Path $PortableStageDir) { Remove-Item -Recurse -Force $PortableStageDir }
    if (Test-Path $PortableZip) { Remove-Item -Force $PortableZip }

    Write-Host "    Estruturando em $PortableStageDir"
    New-Item -ItemType Directory -Force $PortableStageDir | Out-Null

    Copy-Item -Force $AppExeSource         (Join-Path $PortableStageDir "BI Doc Maker.exe")
    Copy-Item -Force $SidecarReleaseSource (Join-Path $PortableStageDir "documentador-core.exe")

    $LicensePath = Join-Path $Root "LICENSE"
    if (Test-Path $LicensePath) {
        Copy-Item -Force $LicensePath (Join-Path $PortableStageDir "LICENSE.txt")
    }

    $ReadmeText = @"
BI Doc Maker $AppVersion - Versao Portatil

----- Como usar -----

1. Mantenha os arquivos desta pasta JUNTOS. Nao mova so o .exe.
2. De duplo clique em "BI Doc Maker.exe" para abrir o app.

Nada e instalado no sistema. Para usar em outra maquina, basta copiar
a pasta inteira. As configuracoes (tema, formatos, branding) ficam
salvas em %APPDATA%\BI Doc Maker.

----- Requisitos -----

* Windows 10 (build 17763+) ou Windows 11
* Microsoft Edge WebView2 Runtime (ja vem pre-instalado no Windows 11
  e no Windows 10 atualizado desde maio/2022).

Se ao abrir aparecer erro sobre WebView2 faltando, instale o
"Evergreen Standalone Installer" em:
https://developer.microsoft.com/microsoft-edge/webview2/

----- Suporte -----

Site:    https://math-rosa.github.io/bi-doc-maker/
Codigo:  https://github.com/math-rosa/bi-doc-maker
Issues:  https://github.com/math-rosa/bi-doc-maker/issues
Licenca: MIT (veja LICENSE.txt)
"@
    $ReadmeText | Out-File -Encoding UTF8 -FilePath (Join-Path $PortableStageDir "LEIA-ME.txt")

    # Assina as copias portateis se houver certificado
    if (-not [string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
        Invoke-Signtool -Path (Join-Path $PortableStageDir "BI Doc Maker.exe") -Thumbprint $CertificateThumbprint -TsaUrl $TimestampUrl -Description "app portatil"
        Invoke-Signtool -Path (Join-Path $PortableStageDir "documentador-core.exe") -Thumbprint $CertificateThumbprint -TsaUrl $TimestampUrl -Description "sidecar portatil"
    }

    Write-Host "    Compactando para $PortableZip"
    Compress-Archive -Path "$PortableStageDir\*" -DestinationPath $PortableZip -CompressionLevel Optimal

    # Limpa staging dir (o zip ja foi gerado)
    Remove-Item -Recurse -Force $PortableStageDir

    $ZipSize = [math]::Round((Get-Item $PortableZip).Length / 1MB, 2)
    Write-Host "==> ZIP portatil pronto ($ZipSize MB)"
}

Write-Host "==> Build Windows concluido"
if ([string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
    Write-Host "    [INFO] Build sem assinatura. Para assinar, rode com -CertificateThumbprint <SHA1>"
}
if ($SkipPortable) {
    Write-Host "    [INFO] ZIP portatil pulado (-SkipPortable)"
}
