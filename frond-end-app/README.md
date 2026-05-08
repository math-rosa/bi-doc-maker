# BI Doc Maker (Tauri + Svelte)

App desktop do produto. A interface Tauri chama o core Python empacotado como sidecar.

## Requisitos

- Node.js 18+
- Rust (toolchain estavel)
- Tauri CLI (via npm)

## Rodar em desenvolvimento

```bash
npm install
npm run tauri:dev
```

Antes de abrir o app em desenvolvimento, gere o sidecar em `src-tauri/binaries` usando o script da raiz ou copie um `documentador-core-<triple>.exe` valido para essa pasta.

## Build

```bash
../build-windows.ps1
```

O script da raiz cria o ambiente Python, empacota `documentador_core_cli.py` com PyInstaller e roda o build Tauri.
