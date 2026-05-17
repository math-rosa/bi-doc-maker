# BI Doc Maker

> 🇺🇸 [English version](README.en.md)

BI Doc Maker é um aplicativo desktop Windows para gerar documentação técnica e executiva de projetos Power BI salvos no formato `.pbip`.

O produto combina uma interface Tauri + Svelte com um core Python empacotado como sidecar. Toda a análise é feita localmente: o app lê os metadados do PBIP, interpreta o modelo e gera arquivos prontos para entrega, auditoria, governança ou passagem de conhecimento.

## Visao Geral do Projeto

- Core Python em `documentador_pbip.py` para ler PBIP e gerar a documentação.
- CLI em `documentador_core_cli.py` que expõe o core via JSON e vira sidecar do app.
- App desktop em `frond-end-app/` (Tauri + Svelte) para fluxo de uso e interface.
- Build Windows em `build-windows.ps1` (PyInstaller + Tauri).
- Site institucional em `website/` com exemplo de documento em PDF.

## Recursos

- Análise local de projetos Power BI `.pbip` (modelo, DAX, Power Query M, relacionamentos, calculation groups, perspectivas e RLS/OLS).
- **Modo lote**: selecione uma pasta-pai, o app varre subpastas e lista todos os PBIPs encontrados — escolha quais documentar de uma vez só.
- **Busca/filtro** na lista de projetos por nome ou caminho (essencial quando há muitos PBIPs).
- **Status em tempo real** durante a geração em lote: cada projeto mostra OK ou erro com tooltip explicando a falha.
- Exportação para Markdown (`.md`), Word (`.docx`) e HTML imprimível.
- HTML aberto no navegador padrão para o usuário salvar como PDF.
- Documentação DOCX com visual padronizado, capa, sumário, tabelas refinadas e blocos de código com destaque de sintaxe.
- Personalização da documentação com título, logo da empresa e cores.
- Pasta de saída configurável (em **Mais Opções**); em lote, todos compartilham uma única pasta.
- Regra de negócio inferida a partir de etapas Power Query M.
- Comentários especiais `BI_DOC` no Power Query tratados como documentação oficial.
- Leitura técnica offline para expressões DAX.
- Dicionário de dados e termos inferido a partir dos metadados do PBIP.
- Diagrama Mermaid nos formatos Markdown e HTML.
- Lista tabular de relacionamentos no Word.
- Interface modernizada com modo claro/escuro, foco visível e tecla Escape para fechar diálogos.
- Saída organizada automaticamente em uma pasta `Doc_BI`.
- Produto Windows sem exigir Python instalado na máquina do cliente.

## Como Usar

1. Abra o BI Doc Maker.
2. Selecione uma pasta. O app **varre subpastas** procurando projetos Power BI e lista todos os PBIPs encontrados.
3. Marque os projetos para os quais deseja gerar documentação (use *Marcar todos* / *Limpar* quando houver vários).
4. (Opcional) Em **Mais Opções**, escolha a pasta de saída, os formatos desejados, título, logo e cores. Sem configurar, a documentação de cada projeto é salva dentro do próprio projeto.
5. Clique em **Gerar Documentação**. O processamento percorre os projetos selecionados um a um, mostrando status (OK / ERRO) ao lado de cada item.

Os arquivos são salvos em:

```text
<pasta-de-saida>\Doc_BI\
```

Regras de saída:

- **Lote (2 ou mais projetos)**: todos compartilham uma única pasta `Doc_BI`. Sem configurar, é a própria pasta selecionada (raiz da varredura). Configurando em **Mais Opções → Pasta de saída**, vai para a pasta escolhida. Os arquivos ficam nomeados como `<Projeto>_documentacao.{md,docx,html}`.
- **Único projeto**: usa a pasta de saída se configurada, senão a pasta do próprio projeto.

Se selecionar apenas um projeto e o formato HTML estiver marcado, ele abre automaticamente no navegador ao terminar — a partir dele, use a impressão do navegador para salvar como PDF.

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
- **Grupos de Cálculo** (Calculation Groups) — itens, precedência e format string dinâmica.
- **Perspectivas** — agrupamentos lógicos de tabelas, colunas e medidas por audiência.
- **Segurança RLS / OLS** — roles, filtros DAX por tabela, permissões de coluna e membros.
- **Parâmetros M e expressões compartilhadas** — separados automaticamente, com tipo e valor.
- Dicionário de dados e termos recorrentes.
- Recursos de imagem encontrados no projeto.

> Cada uma das seções acima só aparece na documentação quando o PBIP realmente contém o recurso — projetos simples geram documentos limpos, sem placeholders vazios.

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
O PDF exibido no mockup fica em `website/public/documentacao-power-bi-corporate-spend.pdf`.
O deploy do site é feito via GitHub Pages pelo workflow `.github/workflows/pages.yml`.

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

Para dev local rápido (pula o rebuild do bootloader PyInstaller, que exige Visual Studio Build Tools):

```powershell
.\build-windows.ps1 -FastBuild
```

> ⚠️ Releases públicas **nunca** devem usar `-FastBuild` — o bootloader stock do PyInstaller é flagrado por vários antivírus heurísticos. O rebuild local muda o hash e elimina essa falsa detecção.

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

## Antivírus e Windows SmartScreen

O BI Doc Maker é distribuído **sem certificado Authenticode** (assinatura digital paga). Como o sidecar Python é empacotado via PyInstaller — tecnologia usada também por programas maliciosos — alguns antivírus podem mostrar alertas durante a instalação ou execução. **O app é seguro** e roda 100% local (não envia dados para lugar nenhum).

### O que esperar

1. **Windows SmartScreen** no primeiro `.exe`: clique em *Mais informações* → *Executar mesmo assim*.
2. **Avast / McAfee / Kaspersky / Trend Micro**: podem flagrar o `documentador-core.exe` (o sidecar Python). Adicione exceção ou submeta como falso positivo ao seu fornecedor.

### Como verificar integridade do download

Toda release no GitHub publica o **SHA256** do `.msi` nas notas. Confira com:

```powershell
Get-FileHash ".\BI Doc Maker_X.Y.Z_x64_en-US.msi" -Algorithm SHA256
```

O hash da sua cópia local deve bater com o publicado na release.

### Para mantenedores: reduzindo falsos positivos

O `build-windows.ps1` já aplica várias mitigações automaticamente:

- `--noupx`: evita o packer UPX (binários UPX-compressed são fortemente flagrados).
- `--version-file version-info.txt`: embute metadata Windows (CompanyName, FileDescription, etc.) — executáveis sem metadata são considerados suspeitos.
- `Assert-LastExitCode`: falha rápida em qualquer step quebrado, evitando entregar binário corrompido.
- **Rebuild automático do bootloader PyInstaller** (executado por padrão pelo `build-windows.ps1`): o bootloader stock distribuído via pip tem hash conhecido por AVs heurísticos. Rebuildando local, o hash muda e o binário deixa de bater com essas assinaturas. Requer Visual Studio Build Tools — se ausente, o build segue com aviso. Para pular o rebuild em dev local, use `-FastBuild`.

#### Submeter como falso positivo aos antivírus principais

Após cada release pública, submeta os dois `.exe` (`documentador-core.exe` e `BI Doc Maker.exe`) aos portais oficiais:

| Vendor | Portal | Tempo médio |
| --- | --- | --- |
| **Microsoft Defender** | [microsoft.com/wdsi/filesubmission](https://www.microsoft.com/wdsi/filesubmission) | 3-7 dias |
| **Avast / AVG** | [avast.com/false-positive-file-form](https://www.avast.com/false-positive-file-form.php) | 1-3 dias |
| **McAfee** | [mcafee.com/.../contact-research](https://www.mcafee.com/enterprise/en-us/threat-center/contact-research.html) | 5-14 dias |
| **Kaspersky** | [kaspersky.com/false-positive](https://www.kaspersky.com/false-positive) | 3-7 dias |
| **Trend Micro** | [success.trendmicro.com/.../1059565](https://success.trendmicro.com/dcx/s/solution/1059565) | 3-10 dias |

Termômetro: suba o `.exe` no [VirusTotal](https://www.virustotal.com) e veja quantos engines flagam antes e depois das submissões.

**Microsoft Defender (passo a passo)**, por ter o maior alcance:

1. Acesse [microsoft.com/wdsi/filesubmission](https://www.microsoft.com/wdsi/filesubmission) e faça login com conta Microsoft.
2. Em **Submission type**, escolha **Software developer**.
3. Faça upload do `documentador-core.exe` (extraído do MSI ou do ZIP portátil).
4. Em **Detection name**, deixe em branco se você não souber qual detecção foi disparada (o Defender descobre).
5. Em **Definition update version**, deixe em branco.
6. Em **Additional information**, descreva: "BI Doc Maker é um app open source para documentar projetos Power BI PBIP. Código em [github.com/math-rosa/bi-doc-maker](https://github.com/math-rosa/bi-doc-maker). PyInstaller é usado apenas para empacotar o sidecar Python — não há código malicioso. Solicito reclassificação como clean."
7. Marque **I believe this file should not be detected as malware**.
8. Submeta. Você recebe email com o resultado em 3-7 dias úteis.
9. Repita o upload com `BI Doc Maker.exe` (instalado em `Program Files`).

#### Distribuir via winget (bypass do SmartScreen)

Instalações via `winget install` **não disparam SmartScreen** porque o instalador vem assinado pelo Microsoft Store. Manifestos prontos ficam em [`winget/`](winget/). Veja [`winget/README.md`](winget/README.md) para o processo de submissão a `microsoft/winget-pkgs`.

Após aprovação, usuários instalam com:

```powershell
winget install MathRosa.BIDocMaker
```

Para assinar o sidecar e o MSI com certificado Authenticode (quando disponível):

```powershell
.\build-windows.ps1 -CertificateThumbprint <SHA1-DO-CERT>
```

O script chama `signtool` em ambos os binários (sidecar + MSI) com timestamp RFC 3161. A integração com Tauri também pode ser configurada via `tauri.conf.json.bundle.windows.certificateThumbprint`.

**Roadmap**: a partir de uma versão futura, todos os artefatos serão assinados com EV (Extended Validation) Authenticode, eliminando o SmartScreen e a maior parte dos alertas de AV.

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
├─ frond-end-app/                    # App Tauri + Svelte (logo SVG em src/assets/)
└─ website/                          # Site institucional
```

## Publicação

Este repositório contém o código-fonte do produto e do site. Artefatos gerados, instaladores, ambientes virtuais, `node_modules`, `target`, `dist` e builds locais não são versionados.

O site é publicado automaticamente no GitHub Pages ao fazer push na `main`.

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
