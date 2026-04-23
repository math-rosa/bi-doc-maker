# Documentador de Projetos Power BI (.pbip)

Uma ferramenta simples e visual para gerar documentação automática (em formato Word e Markdown) de projetos do Power BI Desktop. Se você quer economizar horas escrevendo a documentação do seu modelo de dados, este aplicativo faz isso para você em poucos segundos!

## 🚀 Como começar (Para Leigos)

### 1. Pré-requisitos (O que você precisa instalar)
Para rodar este aplicativo, você só precisa do **Python** instalado no seu computador.
1. Acesse o site oficial do Python: [python.org/downloads](https://www.python.org/downloads/)
2. Baixe a versão mais recente para Windows.
3. **MUITO IMPORTANTE:** Durante a instalação do Python, **marque a caixa "Add Python.exe to PATH"** (Adicionar Python ao PATH) antes de clicar em Install.

*Não é necessário instalar nenhum outro pacote ou dependência de terceiros! O programa usa apenas os recursos nativos.*

### 2. Baixando o Projeto
1. Clique no botão verde **Code** no topo desta página do GitHub e selecione **Download ZIP**.
2. Extraia o arquivo ZIP em uma pasta de sua preferência no seu computador.

### 3. Como usar o Aplicativo
1. Abra a pasta onde você extraiu os arquivos.
2. Dê um duplo clique no arquivo **`documentador_gui.py`**.
   *(Se não abrir com duplo clique, abra o prompt de comando (CMD), navegue até a pasta do projeto e digite `python documentador_gui.py`)*
3. Uma interface moderna e limpa será aberta.
4. Clique em **"Selecionar Pasta"** e escolha a pasta que contém os seus projetos do Power BI salvos como `.pbip`.
5. O aplicativo irá analisar as pastas e listar todos os projetos que encontrou.
6. Selecione os projetos que deseja documentar e clique em **"GERAR DOCUMENTAÇÃO"**.
7. Pronto! Os arquivos de documentação (`.md` e `.docx`) serão salvos na pasta raiz que você selecionou e um botão aparecerá para você abrir a pasta e ver os resultados.

---

## 🤓 Modo Avançado (Para Programadores)

### Uso via Linha de Comando (CLI)

Você também pode pular a interface gráfica e gerar direto pelo terminal:

```bash
python documentador_pbip.py "C:\Caminho\Para\MeuProjeto"
```

### Uso Programático (Criando seus próprios scripts)

```python
from documentador_pbip import DocumentadorPBIP

# 1. Informar a pasta do projeto
doc = DocumentadorPBIP("C:/Caminho/Para/Projeto")

# 2. Extrair informações
doc.extrair_informacoes()

# 3. Salvar (Markdown e Word)
doc.salvar_documentacao("meu_projeto.md")
doc.salvar_documentacao_docx("meu_projeto.docx")
```

## 📋 O que é documentado automaticamente?

O aplicativo analisa os arquivos TMDL do seu projeto Power BI e documenta de forma inteligente:
- **Tabelas** (Visíveis e ocultas)
- **Colunas e Colunas Calculadas** (Tipo de dado, sumarização, ocultação)
- **Medidas e Códigos DAX** (Expressões formatadas)
- **Relacionamentos** entre tabelas (Diretividade, status ativo/inativo)
- **Hierarquias**
- **Códigos em Power Query** (Linguagem M da fonte de dados)

## 📁 Como salvar seu projeto no Power BI
O formato tradicional do Power BI é o `.pbix`. Para usar este documentador, você precisa salvar seu relatório no formato de **Projeto do Power BI (`.pbip`)**.
1. No Power BI Desktop, vá em *Arquivo > Salvar Como*.
2. Escolha o tipo **Power BI Project (*.pbip)**.
3. Escolha uma pasta vazia e salve. É essa pasta que você vai selecionar no aplicativo!

---
**Desenvolvido para facilitar a vida de analistas de dados!** 🚀
