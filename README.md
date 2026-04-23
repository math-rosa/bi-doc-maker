# Documentador de Projetos Power BI (.pbip)

Script Python para gerar documentação automática em Markdown de projetos Power BI Desktop no formato `.pbip`.

## 📋 Características

- ✅ **Parsing de arquivos TMDL** - Parser customizado para Tabular Model Definition Language
- ✅ **Extração completa do modelo semântico**:
  - Tabelas (visíveis e ocultas)
  - Colunas (regulares e calculadas)
  - Medidas DAX
  - Hierarquias
  - Relacionamentos
  - Código fonte Power Query (M)
- ✅ **Informações do relatório**:
  - Páginas (nome, tipo, dimensões)
  - Visuais personalizados
  - Recursos e imagens
- ✅ **Geração de Markdown formatado** - Documentação completa e organizada
- ✅ **Filtro de tabelas técnicas** - Remove automaticamente tabelas LocalDateTable
- ✅ **Suporte UTF-8** - Caracteres especiais e acentuação

## 🚀 Uso

### Modo Básico

```bash
python documentador_pbip.py <caminho_para_projeto>
```

**Exemplo:**

```bash
python documentador_pbip.py "C:\Projetos\MeuDashboard"
```

### Programático

```python
from documentador_pbip import DocumentadorPBIP

# Criar documentador
doc = DocumentadorPBIP("C:/Caminho/Para/Projeto")

# Extrair informações
doc.extrair_informacoes()

# Gerar documentação
markdown = doc.gerar_documentacao()

# Salvar
doc.salvar_documentacao()
# ou especificar caminho:
# doc.salvar_documentacao("minha_documentacao.md")

print("Documentação gerada com sucesso!")
```

## 📁 Estrutura Esperada do Projeto

O script espera encontrar a seguinte estrutura:

```
MeuProjeto/
├── MeuProjeto.pbip
├── MeuProjeto.SemanticModel/
│   ├── definition/
│   │   ├── model.tmdl
│   │   ├── relationships.tmdl
│   │   └── tables/
│   │       ├── Tabela1.tmdl
│   │       └── Tabela2.tmdl
│   └── diagramLayout.json
└── MeuProjeto.Report/
    └── definition/
        ├── report.json
        └── pages/
            ├── pages.json
            └── page_id/
                └── page.json
```

## 📄 Saída Gerada

O script gera um arquivo Markdown contendo:

### 1. Informações do Modelo
- Cultura/idioma
- Versão do DataSource
- Grupos de consulta (se existirem)

### 2. Tabelas
Para cada tabela:
- Nome e status (visível/oculta)
- **Colunas** com tipo, sumarização
- **Colunas calculadas** com expressões DAX
- **Medidas** com expressões DAX e formatação
- **Hierarquias** com níveis
- **Fonte de dados** (código Power Query/M)

### 3. Relacionamentos
- Tabela origem → Tabela destino
- Colunas envolvidas
- Filtro bidirecional
- Status (ativo/inativo)

### 4. Páginas do Relatório
- Nome
- Tipo (Normal/Drillthrough)
- Dimensões

### 5. Recursos Extras
- Visuais personalizados
- Imagens e recursos estáticos

## 🔧 Requisitos

- **Python 3.7+**
- **Bibliotecas padrão apenas** (sem dependências externas)

```python
import os
import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
```

## 💡 Exemplos de Uso

### Exemplo 1: Documentar projeto único

```bash
python documentador_pbip.py "C:\Users\joao\Documents\Vendas_Dashboard"
```

Saída: `Vendas_Dashboard_documentacao.md` na mesma pasta

### Exemplo 2: Processar múltiplos projetos

```python
from documentador_pbip import DocumentadorPBIP
from pathlib import Path

projetos = [
    "C:/Projetos/Vendas",
    "C:/Projetos/Marketing",
    "C:/Projetos/Financeiro"
]

for projeto in projetos:
    print(f"\n{'='*60}")
    print(f"Processando: {projeto}")
    print('='*60)
    
    doc = DocumentadorPBIP(projeto)
    doc.extrair_informacoes()
    doc.salvar_documentacao()
```

### Exemplo 3: Filtrar apenas tabelas específicas

```python
doc = DocumentadorPBIP("C:/Projeto")
doc.extrair_informacoes()

# Filtrar apenas tabelas de fato (não dimensões)
tabelas_fato = [t for t in doc.tabelas if 'Fato' in t.nome]

for tabela in tabelas_fato:
    print(f"{tabela.nome}: {len(tabela.medidas)} medidas")
```

## 🛠️ Características Técnicas

### Parser TMDL

O script inclui um parser customizado para TMDL (Tabular Model Definition Language), que:

- ✅ Identifica blocos por indentação
- ✅ Extrai expressões multilinhas (DAX e Power Query)
- ✅ Processa nomes com espaços e caracteres especiais
- ✅ Lida com annotations e metadata

### Tratamento de Erros

- Arquivos ausentes retornam estruturas vazias (não erros)
- Seções opcionais são omitidas se não existirem
- Encoding UTF-8 garantido

### Filtros Automáticos

Tabelas técnicas são automaticamente filtradas:
- `LocalDateTable_*` - Tabelas de data automáticas
- `DateTableTemplate_*` - Templates de data

## 📊 Exemplo de Saída

```markdown
# Documentação do Dashboard Power BI

**Nome do Projeto**: Vendas_Dashboard
**Data de Geração**: 09/12/2025 19:30:00

---

## Informações do Modelo

| Propriedade | Valor |
|------------|-------|
| Cultura | pt-BR |
| Versão DataSource | powerBI_V3 |

---

## Tabelas

### Fato_Vendas

**Status**: Visível
**Atualização Automática**: Sim

#### Colunas

| Nome | Tipo | Sumarização | Oculta |
|------|------|-------------|--------|
| DataVenda | dateTime | none | Não |
| ValorVenda | decimal | sum | Não |

#### Medidas

| Nome | Expressão DAX | Formato |
|------|---------------|---------|
| Total Vendas | `SUM(Fato_Vendas[ValorVenda])` | #,##0.00 |
| Média Vendas | `AVERAGE(Fato_Vendas[ValorVenda])` | #,##0.00 |

...
```

## ⚠️ Limitações Conhecidas

1. **Visuais**: Não extrai configurações detalhadas de visuais individuais (apenas lista visuais personalizados)
2. **Bookmarks**: Não processa bookmarks
3. **RLS**: Não extrai regras Row-Level Security
4. **Drillthrough**: Lista páginas drillthrough mas não extrai parâmetros detalhados

## 🤝 Contribuindo

Este é um script standalone. Sugestões de melhorias:

- [ ] Adicionar extração de bookmarks
- [ ] Processar configurações RLS
- [ ] Extrair parâmetros de drillthrough
- [ ] Gerar diagrama de relacionamentos (Mermaid)
- [ ] Exportar também em HTML

## 📝 Notas

- O script **não modifica** nenhum arquivo do projeto Power BI
- A leitura é **somente leitura**
- Funciona com projetos `.pbip` (Power BI Desktop formato de projeto)
- **Não funciona** com arquivos `.pbix` (formato legado binário)

## 📞 Suporte

Para questões sobre o formato `.pbip` e TMDL, consulte:
- [Documentação oficial Power BI](https://learn.microsoft.com/power-bi/)
- [TMDL Reference](https://learn.microsoft.com/analysis-services/tmdl/tmdl-overview)

---

**Desenvolvido para documentação automática de projetos Power BI** 🚀
