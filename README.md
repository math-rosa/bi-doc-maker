# BI Doc Maker

BI Doc Maker é um aplicativo desktop Windows para gerar documentação técnica e executiva de projetos Power BI salvos no formato `.pbip`.

O produto combina uma interface Tauri + Svelte com um core Python empacotado como sidecar. Toda a análise é feita localmente: o app lê os metadados do PBIP, interpreta o modelo e gera arquivos prontos para entrega, auditoria, governança ou passagem de conhecimento.

## Recursos

- Análise local de projetos Power BI `.pbip`.
- Exportação para Markdown (`.md`), Word (`.docx`) e HTML imprimível.
- HTML aberto no navegador padrão para o usuário salvar como PDF.
- Documentação DOCX com visual padronizado, capa, sumário, tabelas refinadas e blocos de código com destaque de sintaxe.
- Personalização da documentação com título, logo da empresa e cores.
- Regra de negócio inferida a partir de etapas Power Query M.
- Comentários especiais `BI_DOC` no Power Query tratados como documentação oficial.
- Leitura técnica offline para expressões DAX.
- Dicionário de dados e termos inferido a partir dos metadados do PBIP.
- Diagrama Mermaid nos formatos Markdown e HTML.
- Lista tabular de relacionamentos no Word.
- Interface com modo claro e escuro.
- Saída organizada automaticamente em uma pasta `Doc_BI`.
- Produto Windows sem exigir Python instalado na máquina do cliente.

## Como Usar

1. Abra o BI Doc Maker.
2. Selecione a pasta do projeto Power BI `.pbip`.
3. Selecione a pasta de saída.
4. Marque os formatos desejados: Markdown, Word e/ou HTML / Salvar PDF.
5. Opcionalmente, personalize título, logo e cores da documentação.
6. Clique em **Gerar documentação**.

Os arquivos são salvos em:

```text
<pasta-de-saida>\Doc_BI\
```

Quando o formato HTML for selecionado, o app abre o arquivo no navegador padrão. A partir dele, use a impressão do navegador para salvar como PDF.

## Arquivos Gerados

- `<Projeto>_documentacao.md`
- `<Projeto>_documentacao.docx`
- `<Projeto>_documentacao.html`

O produto não gera PNG do diagrama. Markdown e HTML mantêm o diagrama Mermaid; o DOCX documenta relacionamentos por tabela.

## O Que É Documentado

- Páginas do relatório.
- Tabelas, colunas, colunas calculadas e hierarquias.
- Medidas e expressões DAX.
- Leitura técnica DAX por categoria, como filtros, agregações, relacionamentos, tempo e lógica.
- Consultas Power Query M, com regra de negócio inferida e código original como evidência técnica.
- Relacionamentos do modelo.
- Dicionário de dados e termos recorrentes.
- Recursos de imagem encontrados no projeto.

## Comentários BI_DOC

Você pode enriquecer a documentação diretamente no Power Query M com comentários especiais:

```powerquery
// BI_DOC: regra geral da consulta
// BI_DOC_ORIGEM: descrição da origem oficial
// BI_DOC_REGRA: regra de negócio validada
// BI_DOC_OBSERVACAO: observação relevante
```

Esses comentários aparecem acima da inferência automática e ajudam a separar regra validada de leitura heurística.

## Site Institucional

O repositório também inclui um site estático em `website/`, criado com Vite, HTML, CSS e JavaScript puro.

Comandos principais:

```powershell
cd website
npm install
npm run dev
npm run build
npm run preview
```

O build do site fica em `website\dist\` e não é versionado no Git.

## Tecnologias Usadas

- **Python 3**: core de análise do PBIP e geração dos documentos.
- **python-docx**: criação e formatação do arquivo Word.
- **Python-Markdown**: apoio na geração de Markdown/HTML.
- **PyInstaller**: empacotamento do core Python como executável sidecar.
- **Tauri v1.5**: shell desktop Windows, integração com o sidecar e empacotamento do app.
- **Rust**: camada nativa usada pelo Tauri.
- **Svelte 4**: interface desktop.
- **TypeScript**: tipagem da interface.
- **Vite**: build do app e do site institucional.
- **Node.js 18+**: ambiente de build front-end.
- **Mermaid**: diagrama ER nos formatos Markdown e HTML.
- **Power BI PBIP / TMDL / PBIR**: formatos e metadados analisados localmente.

## Requisitos Para Desenvolvimento

- Windows x64.
- Python 3 disponível no PATH ou pelo launcher `py`.
- Node.js 18+.
- Rust toolchain estável.
- Git.

O script de build empacota o que o produto precisa. O usuário final não precisa instalar Python ou Node.js.

## Build do Produto Windows

Na raiz do projeto:

```powershell
.\build-windows.ps1
```

O script executa:

- criação/atualização do ambiente `.product-venv`;
- instalação das dependências Python;
- empacotamento do sidecar `documentador-core.exe` com PyInstaller;
- cópia do sidecar para `frond-end-app\src-tauri\binaries`;
- build do aplicativo Tauri.

Os instaladores ficam em:

```text
frond-end-app\src-tauri\target\release\bundle\
```

Para reaproveitar dependências Node já instaladas:

```powershell
.\build-windows.ps1 -SkipNpmInstall
```

## Desenvolvimento do App

Instale dependências do front-end:

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

## Testar o Core Python

Com o executável empacotado:

```powershell
.\dist\documentador-core.exe export --project "C:\caminho\ProjetoPBIP" --output-dir "C:\saida" --formats "md,docx,html" --json
```

Durante o desenvolvimento:

```powershell
.\.product-venv\Scripts\python.exe documentador_core_cli.py export --project "C:\caminho\ProjetoPBIP" --output-dir "C:\saida" --formats "md,docx,html" --json
```

Também existe o comando de diagnóstico:

```powershell
.\.product-venv\Scripts\python.exe documentador_core_cli.py analyze --project "C:\caminho\ProjetoPBIP" --json
```

No PowerShell, mantenha `--formats "md,docx,html"` entre aspas.

## Validação Recomendada

```powershell
.\.product-venv\Scripts\python.exe -m py_compile documentador_pbip.py documentador_core_cli.py
cd frond-end-app
npm.cmd run build
cd src-tauri
cargo check
cd ..\..\website
npm.cmd run build
```

## Estrutura Principal

```text
.
├─ documentador_pbip.py              # Core de análise e geração
├─ documentador_core_cli.py          # CLI usada como sidecar
├─ build-windows.ps1                 # Build oficial Windows
├─ assets/                           # Logo padrão
├─ frond-end-app/                    # App Tauri + Svelte
└─ website/                          # Site institucional
```

## Publicação

Este repositório contém o código-fonte do produto e do site. Artefatos gerados, instaladores, ambientes virtuais, `node_modules`, `target`, `dist` e builds locais não são versionados.

Para gerar uma versão instalável, rode:

```powershell
.\build-windows.ps1
```

Depois publique manualmente os artefatos gerados em `frond-end-app\src-tauri\target\release\bundle\`, se desejar criar uma release.

## Agradecimentos Open Source

BI Doc Maker existe em cima de uma base forte de projetos open source:

- [Tauri](https://tauri.app/) pelo runtime desktop leve e empacotamento nativo.
- [Svelte](https://svelte.dev/) pela camada de interface.
- [Vite](https://vitejs.dev/) pelo build rápido do app e do site.
- [Rust](https://www.rust-lang.org/) pela camada nativa usada pelo Tauri.
- [Python](https://www.python.org/) pelo core de análise e geração.
- [PyInstaller](https://pyinstaller.org/) pelo empacotamento do sidecar Python.
- [python-docx](https://python-docx.readthedocs.io/) pela geração dos documentos Word.
- [Python-Markdown](https://python-markdown.github.io/) pelo suporte a Markdown e HTML.
- [Mermaid](https://mermaid.js.org/) pelos diagramas ER em Markdown/HTML.

## Licença

Distribuído sob a licença MIT. Consulte `LICENSE`.
