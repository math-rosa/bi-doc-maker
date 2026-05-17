# Winget manifests — BI Doc Maker

Manifestos prontos para submissão ao repositório oficial [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs).

Publicar via winget tem dois ganhos diretos:

- **Bypass do SmartScreen**: instalações via `winget install` não disparam o aviso "Windows protected your PC".
- **Distribuição corporativa**: muitos times de TI bloqueiam instaladores baixados, mas permitem winget.

## Estrutura

```
manifests/m/MathRosa/BIDocMaker/0.9.2/
├── MathRosa.BIDocMaker.yaml              # version manifest
├── MathRosa.BIDocMaker.installer.yaml    # installer + SHA256 + ProductCode
├── MathRosa.BIDocMaker.locale.en-US.yaml # locale padrão (default)
└── MathRosa.BIDocMaker.locale.pt-BR.yaml # locale PT-BR
```

## Como atualizar para uma nova versão

A cada release pública:

1. **Copie a pasta** `0.9.2/` para `<nova-versao>/` (ex: `0.10.0/`).
2. **Em todos os arquivos**, troque `PackageVersion: 0.9.2` por `PackageVersion: <nova-versao>`.
3. **No `installer.yaml`**:
   - Atualize `InstallerUrl` para a URL do novo MSI no GitHub Releases.
   - Atualize `InstallerSha256` (rode `Get-FileHash` no MSI novo).
   - Atualize `ProductCode` se mudou — extraia com:
     ```powershell
     $installer = New-Object -ComObject WindowsInstaller.Installer
     $db = $installer.GetType().InvokeMember("OpenDatabase","InvokeMethod",$null,$installer,@("CAMINHO\AO\MSI", 0))
     $view = $db.GetType().InvokeMember("OpenView","InvokeMethod",$null,$db,@("SELECT Value FROM Property WHERE Property='ProductCode'"))
     $view.GetType().InvokeMember("Execute","InvokeMethod",$null,$view,$null)
     $record = $view.GetType().InvokeMember("Fetch","InvokeMethod",$null,$view,$null)
     $record.GetType().InvokeMember("StringData","GetProperty",$null,$record,1)
     ```
   - Atualize `ReleaseDate`.
4. **Nos `locale.*.yaml`**: atualize `ReleaseNotesUrl` para a tag nova.

## Validar antes de submeter

```powershell
# Instale o winget-create
winget install Microsoft.WingetCreate

# Valide o manifest
wingetcreate validate .\manifests\m\MathRosa\BIDocMaker\0.9.2

# Teste a instalação local sem submeter
winget install --manifest .\manifests\m\MathRosa\BIDocMaker\0.9.2
```

## Como submeter ao repositório oficial

A primeira submissão é **manual** (segue o processo padrão do projeto):

1. **Fork** [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs).
2. **Copie** o conteúdo de `winget/manifests/` para `manifests/` no fork (mantendo a estrutura `m/MathRosa/BIDocMaker/0.9.2/`).
3. **Abra um PR** para `microsoft/winget-pkgs:master` com título `New version: MathRosa.BIDocMaker version 0.9.2`.
4. O bot de validação roda automaticamente. Se passar, um maintainer aprova em **24-72h**.

Submissões posteriores podem usar `wingetcreate submit` para automatizar o PR.

## Depois de aprovado

Usuários poderão instalar com:

```powershell
winget install MathRosa.BIDocMaker
```

Ou via search:

```powershell
winget search "BI Doc Maker"
```
