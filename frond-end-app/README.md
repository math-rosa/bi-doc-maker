# BI Doc Maker Desktop App

Esta pasta contém a interface desktop do BI Doc Maker, feita com Tauri v1.5, Svelte 4, TypeScript e Vite.

O app não analisa PBIP diretamente no front-end. Ele chama o sidecar Python `documentador-core`, que fica em `src-tauri/binaries` durante o desenvolvimento e é empacotado junto com o instalador no build final.

## Requisitos

- Node.js 18+.
- Rust toolchain estável.
- Dependências Node instaladas com `npm install`.
- Sidecar Python gerado pelo script `..\build-windows.ps1`.

## Desenvolvimento

Na raiz do projeto, gere o sidecar:

```powershell
.\build-windows.ps1 -SkipNpmInstall
```

Depois, nesta pasta:

```powershell
npm install
npm run tauri:dev
```

O Tauri abre a interface local e chama o executável:

```text
src-tauri\binaries\documentador-core-<triple>.exe
```

## Build

Use sempre o script da raiz:

```powershell
..\build-windows.ps1
```

Ele instala dependências, empacota o core Python com PyInstaller e executa `npm run tauri:build`.

## Scripts

- `npm run dev`: inicia apenas o Vite.
- `npm run build`: gera o front-end estático.
- `npm run tauri:dev`: abre o app Tauri em desenvolvimento.
- `npm run tauri:build`: gera o build Tauri, normalmente chamado pelo script da raiz.

## Fluxo da Interface

1. Selecionar o projeto PBIP.
2. Selecionar a pasta de saída.
3. Configurar título, logo e cores da documentação.
4. Escolher Markdown, Word e/ou HTML / Salvar PDF.
5. Gerar a documentação.

Após a exportação, a interface mostra uma confirmação simples e o botão **Abrir pasta**.

## Tecnologias

- Tauri v1.5
- Rust
- Svelte 4
- TypeScript
- Vite
- Node.js
- Sidecar Python empacotado com PyInstaller
