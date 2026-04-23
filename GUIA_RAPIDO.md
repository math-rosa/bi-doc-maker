# Guia Rápido - Documentador Power BI

## 🚀 Início Rápido

### Uso via Linha de Comando

```bash
python documentador_pbip.py "C:\Caminho\Para\Projeto"
```

### Uso Programático

```python
from documentador_pbip import DocumentadorPBIP

doc = DocumentadorPBIP("C:/Projeto")
doc.extrair_informacoes()
doc.salvar_documentacao()
```

---

## 📋 Estrutura de Classes

### InfoModelo
```python
doc.info_modelo.cultura              # "pt-BR"
doc.info_modelo.versao_datasource    # "powerBI_V3"
doc.info_modelo.grupos_consulta      # [{'nome': '...', 'ordem': 0}]
```

### InfoTabela
```python
tabela.nome                  # Nome da tabela
tabela.esta_oculta          # True/False
tabela.colunas              # List[InfoColuna]
tabela.medidas              # List[InfoMedida]
tabela.colunas_calculadas   # List[InfoColunaCalculada]
tabela.hierarquias          # List[InfoHierarquia]
tabela.particao             # InfoParticao (fonte de dados)
```

### InfoColuna
```python
coluna.nome              # Nome da coluna
coluna.tipo_dado         # "string", "int64", "decimal", "dateTime"
coluna.formato           # "#,##0.00"
coluna.sumarizacao       # "sum", "none", "count"
coluna.esta_oculta       # True/False
```

### InfoMedida
```python
medida.nome                 # Nome da medida
medida.expressao_dax        # Código DAX completo
medida.formato              # "#,##0.00"
medida.formato_dinamico     # Código DAX para formato (opcional)
```

### InfoRelacionamento
```python
rel.tabela_origem
rel.coluna_origem
rel.tabela_destino
rel.coluna_destino
rel.filtro_bidirecional     # True/False
rel.esta_ativo              # True/False
```

---

## 🔧 Exemplos Práticos

### 1. Listar todas as medidas

```python
doc = DocumentadorPBIP("C:/Projeto")
doc.extrair_informacoes()

for tabela in doc.tabelas:
    if tabela.medidas:
        print(f"\n{tabela.nome}:")
        for medida in tabela.medidas:
            print(f"  - {medida.nome}")
```

### 2. Encontrar medidas complexas

```python
for tabela in doc.tabelas:
    for medida in tabela.medidas:
        if len(medida.expressao_dax) > 200:
            print(f"{tabela.nome}.{medida.nome}")
            print(f"  Tamanho: {len(medida.expressao_dax)} caracteres")
```

### 3. Analisar relacionamentos

```python
doc = DocumentadorPBIP("C:/Projeto")
doc.extrair_informacoes()

# Relacionamentos bidirecionais
bidirecionais = [r for r in doc.relacionamentos if r.filtro_bidirecional]
print(f"Bidirecionais: {len(bidirecionais)}")

# Relacionamentos inativos
inativos = [r for r in doc.relacionamentos if not r.esta_ativo]
print(f"Inativos: {len(inativos)}")
```

### 4. Exportar lista de tabelas para CSV

```python
import csv

doc = DocumentadorPBIP("C:/Projeto")
doc.extrair_informacoes()

with open("tabelas.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Tabela", "Colunas", "Medidas", "Oculta"])
    
    for t in doc.tabelas:
        writer.writerow([
            t.nome,
            len(t.colunas),
            len(t.medidas),
            "Sim" if t.esta_oculta else "Não"
        ])

print("✓ CSV gerado!")
```

### 5. Processar múltiplos projetos

```python
from pathlib import Path

pasta_projetos = Path("C:/Projetos")

for pasta in pasta_projetos.iterdir():
    if pasta.is_dir():
        try:
            doc = DocumentadorPBIP(str(pasta))
            doc.extrair_informacoes()
            doc.salvar_documentacao(f"DOC_{pasta.name}.md")
            print(f"✓ {pasta.name}")
        except:
            print(f"✗ {pasta.name} (pulado)")
```

---

## 📊 Estatísticas Úteis

### Contagem de elementos

```python
doc = DocumentadorPBIP("C:/Projeto")
doc.extrair_informacoes()

print(f"Tabelas: {len(doc.tabelas)}")
print(f"Relacionamentos: {len(doc.relacionamentos)}")
print(f"Páginas: {len(doc.paginas)}")
print(f"Medidas: {sum(len(t.medidas) for t in doc.tabelas)}")
print(f"Colunas: {sum(len(t.colunas) for t in doc.tabelas)}")
```

### Top 5 tabelas por medidas

```python
top_tabelas = sorted(doc.tabelas, key=lambda t: len(t.medidas), reverse=True)[:5]

for i, tabela in enumerate(top_tabelas, 1):
    print(f"{i}. {tabela.nome}: {len(tabela.medidas)} medidas")
```

---

## 🎯 Padrões de Nome

### Convenções Power BI

```python
# Tabelas de Fato
tabelas_fato = [t for t in doc.tabelas if t.nome.startswith('Fato') or t.nome.startswith('F_')]

# Tabelas Dimensão
tabelas_dim = [t for t in doc.tabelas if t.nome.startswith('Dim') or t.nome.startswith('D_')]

# Tabelas de Data (não técnicas)
tabelas_data = [t for t in doc.tabelas if 'Data' in t.nome or 'Date' in t.nome]
```

---

## ⚠️ Dicas Importantes

### 1. Encoding UTF-8
Todos os arquivos são lidos com `encoding='utf-8'`. Não precisa se preocupar com acentos.

### 2. Tabelas Filtradas
As seguintes tabelas são automaticamente ignoradas:
- `LocalDateTable_*`
- `DateTableTemplate_*`

### 3. Expressões Multilinhas
DAX e Power Query M podem ter múltiplas linhas. O parser lida com isso automaticamente.

### 4. Nomes com Espaços
Nomes de tabelas/colunas com espaços são suportados (aparecem entre aspas simples no TMDL).

---

## 🔍 Debug

### Verificar se arquivo foi encontrado

```python
import os
from pathlib import Path

projeto = Path("C:/Projeto")
arquivo_pbip = list(projeto.glob("*.pbip"))

if arquivo_pbip:
    print(f"✓ Encontrado: {arquivo_pbip[0].name}")
else:
    print("✗ Nenhum .pbip encontrado")
```

### Verificar estrutura de pastas

```python
projeto = Path("C:/Projeto")
nome = arquivo_pbip[0].stem

# Verificar pastas esperadas
pasta_semantic = projeto / f"{nome}.SemanticModel"
pasta_report = projeto / f"{nome}.Report"

print(f"SemanticModel: {pasta_semantic.exists()}")
print(f"Report: {pasta_report.exists()}")
```

---

## 📝 Customização

### Modificar formato de saída

Edite o método `gerar_documentacao()` em `documentador_pbip.py`:

```python
def gerar_documentacao(self) -> str:
    md = []
    
    # Seu código customizado aqui
    md.append("# Meu Formato Personalizado")
    
    # ...
    
    return '\n'.join(md)
```

### Adicionar novos filtros

Edite o método `_deve_filtrar_tabela()`:

```python
def _deve_filtrar_tabela(self, nome_tabela: str) -> bool:
    padroes_filtro = [
        r'^LocalDateTable_',
        r'^DateTableTemplate_',
        r'^_Temp',           # Adicionar: filtrar tabelas temporárias
        r'^Staging',         # Adicionar: filtrar staging
    ]
    
    for padrao in padroes_filtro:
        if re.match(padrao, nome_tabela):
            return True
    
    return False
```

---

## 📞 Troubleshooting

### Erro: "Nenhum arquivo .pbip encontrado"
- Verifique se o caminho está correto
- Certifique-se de que está apontando para a **pasta** do projeto, não para o arquivo .pbip

### Erro: encoding
- Os arquivos devem estar em UTF-8
- Se houver erro, verifique o encoding com um editor de texto

### Nenhuma tabela extraída
- Verifique se existe a pasta `<Projeto>.SemanticModel/definition/tables/`
- Certifique-se de que não está filtrando todas as tabelas acidentalmente

### Relacionamentos vazios
- Verifique se existe `relationships.tmdl`
- Alguns modelos podem não ter relacionamentos definidos

---

**Última atualização**: Dezembro 2025
