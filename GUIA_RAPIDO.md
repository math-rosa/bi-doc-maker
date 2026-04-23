# Guia Rápido - Documentador Power BI

Este guia foi feito para que qualquer pessoa, independentemente do nível de conhecimento em programação, consiga rodar e gerar documentações de projetos no Power BI.

---

## 🏁 Passo a Passo Visual

### 1. Requisito Inicial
Você só precisa ter o **Python** instalado na sua máquina.
- Baixe no site oficial: [python.org/downloads](https://www.python.org/downloads/)
- **Dica de Ouro:** Na tela de instalação, lembre-se de marcar a opção **"Add python.exe to PATH"**. Isso é essencial para o Windows conseguir rodar o programa!

### 2. Abrindo a Interface
Após baixar (ou clonar) os arquivos deste projeto, você verá o arquivo principal chamado `documentador_gui.py`. 
Para abrir a interface gráfica:
- Dê um duplo clique em `documentador_gui.py`.
- Se abrir uma tela preta (terminal) e fechar rapidamente sem abrir a tela do aplicativo, clique com o botão direito no arquivo, vá em "Abrir com" e escolha "Python".

### 3. Usando a Interface
1. **Selecionar Pasta:** Ao clicar no botão **"Selecionar Pasta"**, **NÃO** selecione o arquivo `.pbip` diretamente. Escolha a **pasta principal** onde seu projeto está salvo. O programa é inteligente o suficiente para escanear a pasta e procurar se existe algum projeto do Power BI lá dentro.
2. **Projetos Encontrados:** Uma lista aparecerá mostrando os projetos que foram encontrados na pasta. Você pode usar:
   - `Ctrl + Clique` para selecionar projetos alternados.
   - `Shift + Clique` para selecionar um intervalo contínuo de projetos.
   - O botão `Selecionar Todos` para marcar tudo de uma vez.
3. **Gerar Documentação:** Com os projetos selecionados, clique no grande botão azul "GERAR DOCUMENTAÇÃO". Uma barra de carregamento indicará o progresso da extração.
4. **Resultados Prontos!** Um botão verde "Abrir Pasta com Documentação" aparecerá no final. Ao clicar, ele abrirá o local onde os documentos `.md` (Markdown) e `.docx` (Word) foram gerados para você.

---

## 🔧 Referência Técnica (Avançado)
*Abaixo estão informações direcionadas a desenvolvedores querendo estender a solução.*

### Classe Principal `DocumentadorPBIP`
Você pode importar e rodar o extrator direto via código:
```python
from documentador_pbip import DocumentadorPBIP

doc = DocumentadorPBIP("C:/Projetos/Financeiro")
doc.extrair_informacoes()

# Exportando
doc.salvar_documentacao("C:/Saida/doc.md")
doc.salvar_documentacao_docx("C:/Saida/doc.docx")
```

### Acessando os Dados Extraídos
Ao usar a biblioteca no seu código, a variável `doc` possuirá atributos ricos que mapeiam o modelo inteiro:
- `doc.info_modelo`: Metadados do dataset.
- `doc.tabelas`: Uma lista de objetos `InfoTabela` contendo suas colunas, medidas, hierarquias e códigos em Power Query.
- `doc.relacionamentos`: Lista das ligações do modelo com sentido dos filtros e quais colunas se interligam.

### Customizando Filtros (Tabelas Ocultas)
Por padrão, o sistema ignora tabelas nativas de calendário que o Power BI cria "escondido" (ex: `LocalDateTable_`, `DateTableTemplate_`). 

Se desejar ocultar outras tabelas (exemplo: tabelas de parâmetros, staging temporário), você pode adicionar regras no método `_deve_filtrar_tabela` dentro do arquivo `documentador_pbip.py`.
