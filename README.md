# BI Doc Maker

BI Doc Maker e um aplicativo desktop para gerar documentacao tecnica de projetos Power BI salvos no formato `.pbip`.

O produto combina uma interface Windows feita com Tauri + Svelte e um core Python empacotado como sidecar. O Python analisa a estrutura do projeto PBIP e gera arquivos prontos para entrega, auditoria, governanca ou passagem de conhecimento.

## Recursos

- Analise de projetos Power BI `.pbip`.
- Exportacao para Markdown (`.md`), Word (`.docx`) e HTML imprimivel.
- HTML aberto no navegador padrao para o usuario salvar como PDF.
- PNG do diagrama de relacionamentos gerado com Graphviz e inserido no DOCX.
- Personalizacao da documentacao com titulo, logo e cores da empresa.
- Interface com modo claro e escuro.
- Saida organizada automaticamente em uma pasta `Doc_BI`.
- Produto Windows sem exigir Python instalado na maquina do cliente.

## Como usar o app

1. Abra o BI Doc Maker.
2. Selecione a pasta do projeto Power BI `.pbip`.
3. Selecione a pasta de saida.
4. Marque os formatos desejados: Markdown, Word e/ou HTML / Salvar PDF.
5. Opcionalmente, personalize titulo, logo e cores da documentacao.
6. Clique em **Gerar documentacao**.

Os arquivos serao salvos em:

```text
<pasta-de-saida>\Doc_BI\
```

Quando o formato HTML for selecionado, o app abre o arquivo no navegador padrao. A partir dele, use a impressao do navegador para salvar como PDF.

## Arquivos gerados

- `<Projeto>_documentacao.md`
- `<Projeto>_documentacao.docx`
- `<Projeto>_documentacao.html`
- `<Projeto>_diagrama_relacionamentos.png`

O PNG do diagrama tambem e usado dentro do DOCX quando o formato Word e gerado.

## O que e documentado

- Tabelas, colunas e colunas calculadas.
- Medidas e expressoes DAX.
- Relacionamentos do modelo.
- Hierarquias.
- Paginas do relatorio.
- Fontes e consultas Power Query quando disponiveis.
- Recursos de imagem encontrados no projeto.

## Tecnologias usadas

- **Python 3**: core de analise do PBIP e geracao dos documentos.
- **python-docx**: criacao do arquivo Word.
- **Python-Markdown**: conversao e apoio na documentacao em Markdown/HTML.
- **Graphviz**: renderizacao do PNG do diagrama de relacionamentos.
- **PyInstaller**: empacotamento do core Python como executavel sidecar.
- **Tauri v1.5**: shell desktop Windows, integracao com o sidecar e empacotamento do app.
- **Rust**: camada nativa do Tauri e comandos para chamar o sidecar.
- **Svelte 4**: interface do usuario.
- **TypeScript**: tipagem da interface.
- **Vite**: build do front-end.
- **Node.js 18+**: ambiente de build do front-end.
- **Power BI PBIP**: formato de projeto analisado pelo app.

## Requisitos para desenvolvimento

- Windows x64.
- Python 3 disponivel no PATH ou pelo launcher `py`.
- Node.js 18+.
- Rust toolchain estavel.
- Git.

O script de build baixa o Graphviz portatil e empacota tudo que o produto precisa. O usuario final nao precisa instalar Python, Graphviz ou Node.js.

## Build do produto Windows

Na raiz do projeto:

```powershell
.\build-windows.ps1
```

O script executa:

- criacao/atualizacao do ambiente `.product-venv`;
- instalacao das dependencias Python;
- download do Graphviz portatil;
- empacotamento do sidecar `documentador-core.exe` com PyInstaller;
- copia do sidecar para `frond-end-app\src-tauri\binaries`;
- build do aplicativo Tauri.

Os instaladores ficam em:

```text
frond-end-app\src-tauri\target\release\bundle\
```

Para reaproveitar dependencias Node ja instaladas:

```powershell
.\build-windows.ps1 -SkipNpmInstall
```

## Desenvolvimento do app

Instale dependencias do front-end:

```powershell
cd frond-end-app
npm install
```

Antes de abrir o Tauri em desenvolvimento, gere o sidecar uma vez pela raiz:

```powershell
cd ..
.\build-windows.ps1 -SkipNpmInstall
```

Depois rode:

```powershell
cd frond-end-app
npm run tauri:dev
```

## Testar o core Python

Com o executavel empacotado:

```powershell
.\dist\documentador-core.exe export --project "C:\caminho\ProjetoPBIP" --output-dir "C:\saida" --formats md,docx,html --json
```

Durante o desenvolvimento:

```powershell
.\.product-venv\Scripts\python.exe documentador_core_cli.py export --project "C:\caminho\ProjetoPBIP" --output-dir "C:\saida" --formats md,docx,html --json
```

Tambem existe o comando de diagnostico:

```powershell
.\.product-venv\Scripts\python.exe documentador_core_cli.py analyze --project "C:\caminho\ProjetoPBIP" --json
```

## Validacao recomendada

```powershell
.\.product-venv\Scripts\python.exe -m py_compile documentador_pbip.py documentador_core_cli.py
cd frond-end-app
npm.cmd run build
cd src-tauri
cargo check
```

## Publicacao

Este repositorio contem o codigo-fonte do produto. Os instaladores e pacotes binarios nao sao versionados no Git.

Para gerar uma versao instalavel, rode:

```powershell
.\build-windows.ps1
```

Depois publique manualmente os artefatos gerados em `frond-end-app\src-tauri\target\release\bundle\`, se desejar criar uma release.

## Agradecimentos open source

BI Doc Maker existe em cima de uma base forte de projetos open source:

- [Tauri](https://tauri.app/) pelo runtime desktop leve e empacotamento nativo.
- [Graphviz](https://graphviz.org/) pelo layout do diagrama de relacionamentos.
- [Svelte](https://svelte.dev/) pela camada de interface.
- [Vite](https://vitejs.dev/) pelo build rapido do front-end.
- [Rust](https://www.rust-lang.org/) pela camada nativa usada pelo Tauri.
- [Python](https://www.python.org/) pelo core de analise e geracao.
- [PyInstaller](https://pyinstaller.org/) pelo empacotamento do sidecar Python.
- [python-docx](https://python-docx.readthedocs.io/) pela geracao dos documentos Word.
- [Python-Markdown](https://python-markdown.github.io/) pelo suporte a Markdown e HTML.

## Licenca

Distribuido sob a licenca MIT. Consulte `LICENSE`.
