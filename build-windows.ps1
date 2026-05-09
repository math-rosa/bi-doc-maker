param(
    [switch]$SkipNpmInstall
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $Root ".product-venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$TauriDir = Join-Path $Root "frond-end-app"
$SidecarName = "documentador-core"
$BinariesDir = Join-Path $TauriDir "src-tauri\binaries"
$ToolsDir = Join-Path $Root ".product-tools"
$GraphvizVersion = "14.1.5"
$GraphvizDir = Join-Path $ToolsDir "graphviz"
$GraphvizDot = Join-Path $GraphvizDir "bin\dot.exe"
$GraphvizZip = Join-Path $ToolsDir "graphviz-$GraphvizVersion-win64.zip"
$GraphvizUrl = "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/$GraphvizVersion/windows_10_cmake_Release_Graphviz-$GraphvizVersion-win64.zip"

function Invoke-SystemPython {
    param([string[]]$Arguments)

    $PyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($PyLauncher) {
        & py -3 @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Python launcher falhou com codigo $LASTEXITCODE."
        }
        return
    }

    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) {
        & python @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Python falhou com codigo $LASTEXITCODE."
        }
        return
    }

    throw "Python nao encontrado. Instale Python 3 e deixe-o disponivel no PATH ou via py launcher."
}

function Invoke-NativeCommand {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Comando falhou com codigo $LASTEXITCODE`: $FilePath $($Arguments -join ' ')"
    }
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

function Remove-WorkspaceDirectory {
    param([string]$Path)

    $RootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd([char]'\', [char]'/')
    $TargetFull = [System.IO.Path]::GetFullPath($Path).TrimEnd([char]'\', [char]'/')
    $IsWorkspacePath = $TargetFull.Equals($RootFull, [System.StringComparison]::OrdinalIgnoreCase) -or
        $TargetFull.StartsWith($RootFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase) -or
        $TargetFull.StartsWith($RootFull + [System.IO.Path]::AltDirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)

    if (-not $IsWorkspacePath) {
        throw "Recusando remover pasta fora do workspace: $TargetFull"
    }

    if (Test-Path -LiteralPath $TargetFull) {
        Remove-Item -LiteralPath $TargetFull -Recurse -Force
    }
}

function Ensure-Graphviz {
    if (Test-Path -LiteralPath $GraphvizDot) {
        Write-Host "==> Graphviz ja disponivel em $GraphvizDot"
        return
    }

    Write-Host "==> Baixando Graphviz $GraphvizVersion"
    New-Item -ItemType Directory -Force $ToolsDir | Out-Null

    if (-not (Test-Path -LiteralPath $GraphvizZip)) {
        Invoke-WebRequest -UseBasicParsing -Uri $GraphvizUrl -OutFile $GraphvizZip
    }

    $ExtractDir = Join-Path $ToolsDir "graphviz-extract"
    Remove-WorkspaceDirectory $ExtractDir
    New-Item -ItemType Directory -Force $ExtractDir | Out-Null
    Expand-Archive -LiteralPath $GraphvizZip -DestinationPath $ExtractDir -Force

    $DotExe = Get-ChildItem -LiteralPath $ExtractDir -Recurse -Filter "dot.exe" | Select-Object -First 1
    if (-not $DotExe) {
        throw "dot.exe nao encontrado no pacote Graphviz baixado."
    }

    $FoundGraphvizRoot = Split-Path -Parent (Split-Path -Parent $DotExe.FullName)
    Remove-WorkspaceDirectory $GraphvizDir
    New-Item -ItemType Directory -Force $GraphvizDir | Out-Null
    Get-ChildItem -LiteralPath $FoundGraphvizRoot -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $GraphvizDir -Recurse -Force
    }
    Remove-WorkspaceDirectory $ExtractDir

    if (-not (Test-Path -LiteralPath $GraphvizDot)) {
        throw "Graphviz foi extraido, mas $GraphvizDot nao existe."
    }
}

Write-Host "==> Criando ambiente Python de produto"
Invoke-SystemPython @("-m", "venv", $VenvDir)

Write-Host "==> Instalando dependencias Python"
Invoke-NativeCommand $VenvPython @("-m", "pip", "install", "--upgrade", "pip")
Invoke-NativeCommand $VenvPython @("-m", "pip", "install", "-r", (Join-Path $Root "requirements.txt"), "pyinstaller")

Ensure-Graphviz

Write-Host "==> Gerando sidecar Python com PyInstaller"
Invoke-NativeCommand $VenvPython @(
    "-m", "PyInstaller",
    "--clean",
    "--noconfirm",
    "--onefile",
    "--name", $SidecarName,
    "--exclude-module", "playwright",
    "--add-data", "$Root\assets\bi-doc-maker-logo.png;assets",
    "--add-data", "$GraphvizDir;graphviz",
    "--collect-all", "markdown",
    "--collect-all", "docx",
    (Join-Path $Root "documentador_core_cli.py")
)

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
        Invoke-NativeCommand "npm.cmd" @("ci")
    }

    Write-Host "==> Gerando instalador Tauri"
    Invoke-NativeCommand "npm.cmd" @("run", "tauri:build")
}
finally {
    Pop-Location
}

Write-Host "==> Build Windows concluido"
