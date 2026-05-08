# BI Doc Maker

BI Doc Maker gera documentacao de projetos Power BI salvos como `.pbip`.

O produto atual tem duas camadas:

- App desktop Windows feito com Tauri + Svelte.
- Core Python reutilizado como sidecar para analisar o PBIP e exportar arquivos.

## Formatos gerados

- Markdown (`.md`)
- Word (`.docx`)
- HTML imprimivel para salvar como PDF pelo navegador
- PNG do diagrama de relacionamentos, tambem embutido no DOCX quando Word for gerado

Os arquivos sao salvos em uma subpasta `Doc_BI` dentro da pasta de saida escolhida.

## App Windows

Para gerar o instalador Windows:

```powershell
.\build-windows.ps1
```

O script:

- cria/atualiza o ambiente Python `.product-venv`;
- instala as dependencias do `requirements.txt`;
- empacota `documentador_core_cli.py` com PyInstaller;
- copia o sidecar para o padrao do Tauri;
- roda o build do app desktop.

Os instaladores ficam em:

```text
frond-end-app\src-tauri\target\release\bundle\
```

## Rodar o Front-end em Desenvolvimento

```powershell
cd frond-end-app
npm install
npm run tauri:dev
```

Antes de abrir em desenvolvimento, gere o sidecar com `.\build-windows.ps1` ou copie um `documentador-core-<triple>.exe` valido para `frond-end-app\src-tauri\binaries`.

## CLI do Core Python

Tambem e possivel testar o core diretamente:

```powershell
.\dist\documentador-core.exe export --project "C:\caminho\ProjetoPBIP" --output-dir "C:\saida" --formats md,docx,html --json
```

Durante o desenvolvimento, usando Python:

```powershell
python documentador_core_cli.py export --project "C:\caminho\ProjetoPBIP" --output-dir "C:\saida" --formats md,docx,html --json
```

## Dependencias Principais

- Python 3
- `python-docx`
- `Markdown`
- `Pillow`
- Node.js 18+
- Rust toolchain
- Tauri v1

## O que e documentado

- Tabelas, colunas e colunas calculadas
- Medidas e expressoes DAX
- Relacionamentos
- Hierarquias
- Paginas do relatorio
- Fontes e consultas Power Query quando disponiveis

## Observacao

O PDF automatico com Chromium foi removido para reduzir o tamanho do produto. O app gera HTML imprimivel e abre no navegador padrao para o usuario salvar como PDF.
