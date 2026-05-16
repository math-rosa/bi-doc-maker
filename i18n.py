"""Internacionalizacao do BI Doc Maker.

Estrategia: cataloga as strings em dois dicts (pt_BR e en_US) no proprio
modulo (evita complicacao com data files no PyInstaller). Cada chave usa
o padrao "secao.nome" para facilitar grep e organizacao.

API:
    set_locale("pt") | set_locale("en")  - troca idioma global
    t("chave")                           - retorna string traduzida
    t("chave", n=5, nome="X")            - com placeholders {n}/{nome}

Fallback: se a chave nao existir em en_US, retorna pt_BR. Se nao existir
em nenhum, retorna "[?chave]" para facilitar identificar bugs.

Para adicionar novo idioma: criar novo dict (ex: _ES_ES) e tratar em
set_locale + escolha em _catalog().
"""
from __future__ import annotations

from typing import Any, Dict


# ===========================================================================
# Catalogo pt-BR (idioma de referencia)
# ===========================================================================

_PT_BR: Dict[str, str] = {
    # -------------------------------------------------------------------
    # Cabecalhos principais do documento (Markdown ## headings)
    # -------------------------------------------------------------------
    "doc.toc.title": "📑 Índice",
    "doc.toc.overview": "Visão Geral",
    "doc.toc.dictionary": "Dicionário de Dados e Termos",
    "doc.toc.pages": "Páginas do Relatório",
    "doc.toc.model": "Modelo de Dados",
    "doc.toc.tables_summary": "Resumo das Tabelas",
    "doc.toc.tables_detail": "Detalhamento das Tabelas",
    "doc.toc.relationships": "Relacionamentos",
    "doc.toc.custom_visuals": "Visuais Personalizados",
    "doc.toc.image_resources": "Recursos de Imagem",

    "doc.section.overview": "📈 Visão Geral",
    "doc.section.dictionary": "Dicionário de Dados e Termos",
    "doc.section.glossary_dax": "📐 Glossário DAX",
    "doc.section.pages": "📄 Páginas do Relatório",
    "doc.section.model": "🗂️ Modelo de Dados",
    "doc.section.er_diagram": "Diagrama de Relacionamentos (ER)",
    "doc.section.relationships_list": "🔗 Lista de Relacionamentos",
    "doc.section.query_groups": "📂 Grupos de Consulta",
    "doc.section.tables_summary": "📊 Resumo das Tabelas",
    "doc.section.tables_in_model": "📁 Tabelas do Modelo",
    "doc.section.tables": "Tabelas",

    # -------------------------------------------------------------------
    # Capa
    # -------------------------------------------------------------------
    "cover.document_title_default": "Documentação Power BI",
    "cover.created_on": "Data de Criação",

    # -------------------------------------------------------------------
    # Tabela de visao geral (cards de contadores)
    # -------------------------------------------------------------------
    "overview.col.tables": "📁 Tabelas",
    "overview.col.measures": "📐 Medidas",
    "overview.col.columns": "🔢 Colunas",
    "overview.col.calc_columns": "🧮 Calculadas",
    "overview.col.relationships": "🔗 Relacionamentos",
    "overview.col.pages": "📄 Páginas",
    "overview.dimensional_label": "**Modelo dimensional**",

    # Plurais para modelo dimensional
    "overview.dim.fact_one": "fato",
    "overview.dim.fact_many": "fatos",
    "overview.dim.dim_one": "dimensão",
    "overview.dim.dim_many": "dimensões",
    "overview.dim.aux_one": "auxiliar",
    "overview.dim.aux_many": "auxiliares",

    # -------------------------------------------------------------------
    # Dicionario de termos
    # -------------------------------------------------------------------
    "dict.intro": "Leitura offline inferida a partir dos metadados do PBIP. O dicionário não usa dados reais das tabelas e deve ser validado com a área de negócio.",
    "dict.col.term": "Termo",
    "dict.col.frequency": "Ocorrências",
    "dict.col.category": "Categoria",
    "dict.col.sources": "Onde aparece",
    "dict.col.examples": "Exemplos",

    # Categorias do dicionario
    "dict.cat.indicator": "Indicador",
    "dict.cat.entity": "Entidade",
    "dict.cat.time": "Tempo",
    "dict.cat.attribute": "Atributo",
    "dict.cat.identifier": "Identificador",
    "dict.cat.technical_rule": "Regra Técnica",
    "dict.cat.filter": "Filtro",
    "dict.cat.page_visual": "Página/Visual",
    "dict.cat.general": "Termo Geral",
    "dict.cat.other": "Outro",

    # -------------------------------------------------------------------
    # Glossario DAX
    # -------------------------------------------------------------------
    "glossary_dax.intro": "Funções DAX usadas em medidas, colunas calculadas e tabelas deste projeto. Cada medida individual abaixo lista apenas os nomes das funções — a descrição completa fica aqui.",
    "glossary_dax.col.function": "Função",
    "glossary_dax.col.category": "Categoria",
    "glossary_dax.col.description": "Descrição",
    "glossary_dax.col.business_reading": "Leitura de negócio",

    "leitura_dax.functions_used": "**Funções DAX usadas**",

    # -------------------------------------------------------------------
    # Linhagem de medidas
    # -------------------------------------------------------------------
    "linhagem.measures_referenced": "**Medidas referenciadas**",

    # -------------------------------------------------------------------
    # Power Query
    # -------------------------------------------------------------------
    "pq.business_rule_inferred": "Regra de Negócio Inferida",
    "pq.intro": "Leitura offline inferida a partir das etapas do Power Query M. Para compreensão completa da regra, consulte o código M original exibido abaixo.",
    "pq.intro_with_observations": "Comentários `BI_DOC` são tratados como documentação oficial e aparecem antes da inferência automática.",
    "pq.documented_observations": "**Observações Documentadas**",
    "pq.summary_label": "**Esta tabela aplica**",
    "pq.rules_title": "**Regras de Negócio e Filtros — Power Query**",
    "pq.col.step": "Etapa",
    "pq.col.rule_or_filter": "Regra / Filtro",
    "pq.col.description": "Descrição",

    # Rotulos para observacoes documentadas
    "pq.obs.general": "Geral",
    "pq.obs.source": "Origem",
    "pq.obs.rule": "Regra",
    "pq.obs.observation": "Observação",

    # -------------------------------------------------------------------
    # Tabelas (detalhamento por tabela)
    # -------------------------------------------------------------------
    "table.col.status": "Status",
    "table.col.refresh": "Atualização",
    "table.col.columns": "Colunas",
    "table.col.measures": "Medidas",
    "table.col.source": "Fonte",

    "table.col.name": "Nome",
    "table.col.type": "Tipo",
    "table.col.summarization": "Sumarização",
    "table.col.hidden": "Oculta",

    "table.section.columns": "📋 Colunas",
    "table.section.calc_columns_summary": "Colunas Calculadas (Resumo)",
    "table.section.calc_columns_dax": "Colunas Calculadas - Código DAX",
    "table.section.measures_summary": "Medidas (Resumo)",
    "table.section.measures_dax": "Medidas - Código DAX",
    "table.section.source_data": "💾 Fonte de Dados",

    "table.measure.col.name": "Nome",
    "table.measure.col.type": "Tipo",
    "table.measure.col.name_full": "Nome da Medida",

    "table.calc.col.name": "Nome",
    "table.calc.col.type": "Tipo",
    "table.calc.col.format": "Formato",

    "table.status.visible": "🟢 Visível",
    "table.status.hidden": "🔴 Oculta",
    "table.refresh.yes": "✅ Sim",
    "table.refresh.no": "❌ Não",
    "table.yes": "Sim",
    "table.no": "Não",

    "table.source.import": "📥 Importação",
    "table.source.dax": "📝 DAX",
    "table.source.sql": "🗃️ SQL",
    "table.source.oracle": "🔷 Oracle",
    "table.source.mode_label": "**Modo**",
    "table.source.group_label": "**Grupo**",
    "table.source.code_m": "**Código fonte (Power Query M)**",
    "table.source.code_dax": "**Código fonte (DAX)**",

    # -------------------------------------------------------------------
    # Tipos inferidos de medida
    # -------------------------------------------------------------------
    "measure.type.percentage": "Percentual",
    "measure.type.count": "Contagem",
    "measure.type.currency": "Moeda",
    "measure.type.average": "Média",
    "measure.type.sum": "Soma",
    "measure.type.minmax": "Extremo",
    "measure.type.numeric": "Numérico",

    # -------------------------------------------------------------------
    # Relacionamentos
    # -------------------------------------------------------------------
    "rel.total_label": "*Total: {n} relacionamentos*",
    "rel.col.from": "Origem",
    "rel.col.arrow": "→",
    "rel.col.to": "Destino",
    "rel.col.bidirectional": "Bidirecional",
    "rel.col.active": "Ativo",
    "rel.legend": "*Legenda: `}|--||` = Filtro Bidirecional | `}o--||` = Filtro Único*",

    # -------------------------------------------------------------------
    # Resumo das tabelas
    # -------------------------------------------------------------------
    "tables_summary.intro": "*Visão geral de {n} tabelas no modelo*",
    "tables_summary.col.idx": "#",
    "tables_summary.col.table": "Tabela",
    "tables_summary.col.columns": "Colunas",
    "tables_summary.col.measures": "Medidas",
    "tables_summary.col.calc_columns": "Colunas Calc.",
    "tables_summary.col.source": "Fonte",
    "tables_summary.totals": "**Totais**: {cols} colunas | {meds} medidas | {calc} colunas calculadas",
    "tables_summary.doc_count": "*Total de tabelas documentadas: {n}*",
    "tables_summary.empty": "*Nenhuma tabela encontrada no projeto.*",

    # -------------------------------------------------------------------
    # Paginas / report
    # -------------------------------------------------------------------
    "pages.total": "**Total de páginas: {n}**",
    "pages.empty_thin_report": "⚠️ Nenhuma página encontrada localmente. Este projeto pode ser um **relatório remoto** (thin report) onde as páginas ficam armazenadas no serviço Power BI.",

    # -------------------------------------------------------------------
    # Mensagens [AVISO] e log (apenas console; ja em pt-BR)
    # -------------------------------------------------------------------
    "log.dax_not_captured": "// [AVISO] Expressão DAX não capturada durante o parsing",

    # -------------------------------------------------------------------
    # Filenames (sufixo apos o nome do projeto)
    # -------------------------------------------------------------------
    "filename.suffix": "_documentacao",

    # -------------------------------------------------------------------
    # DOCX-especificas (espelham strings do MD com pequenas variacoes)
    # -------------------------------------------------------------------
    "docx.toc.title": "Sumário",
    "docx.section.overview": "Visão Geral",
    "docx.section.dictionary": "Dicionário de Dados e Termos",
    "docx.section.pages": "Páginas do Relatório",
    "docx.section.page_filters": "Filtros de Página",
    "docx.section.model": "Modelo de Dados",
    "docx.section.relationships_list": "Lista de Relacionamentos",
    "docx.section.query_groups": "Grupos de Consulta",
    "docx.section.tables_summary": "Resumo das Tabelas",
    "docx.section.tables_detail": "Detalhamento das Tabelas",
    "docx.section.columns": "Colunas",
    "docx.section.calc_columns": "Colunas Calculadas",
    "docx.section.measures_dax": "Medidas DAX",
    "docx.section.measures_code": "Código das Medidas",
    "docx.section.hierarchies": "Hierarquias",
    "docx.section.source_data": "Fonte de Dados",
    "docx.section.custom_visuals": "Visuais Personalizados",
    "docx.section.image_resources": "Recursos de Imagem",
    "docx.section.business_rule_inferred": "Regra de Negócio Inferida",
    "docx.section.pq_rules": "Regras de Negócio e Filtros — Power Query",

    # Stats cards e info da capa
    "docx.stat.tables": "Tabelas",
    "docx.stat.measures": "Medidas",
    "docx.stat.measures_dax": "Medidas DAX",
    "docx.stat.columns": "Colunas",
    "docx.stat.calc_columns": "Calculadas",
    "docx.stat.relationships": "Relacionamentos",
    "docx.stat.pages": "Páginas",
    "docx.stat.dimensional_label": "Modelo dimensional",

    # Colunas de tabelas DOCX
    "docx.tcol.term": "Termo",
    "docx.tcol.frequency": "Ocorrências",
    "docx.tcol.category": "Categoria",
    "docx.tcol.sources": "Onde aparece",
    "docx.tcol.examples": "Exemplos",
    "docx.tcol.idx": "#",
    "docx.tcol.page_name": "Nome da Página",
    "docx.tcol.page_type": "Tipo",
    "docx.tcol.dimensions": "Dimensões",
    "docx.tcol.filters": "Filtros",
    "docx.tcol.table": "Tabela",
    "docx.tcol.column": "Coluna",
    "docx.tcol.type": "Tipo",
    "docx.tcol.values": "Valores",
    "docx.tcol.gq_name": "Nome",
    "docx.tcol.gq_order": "Ordem",
    "docx.tcol.col_name": "Nome",
    "docx.tcol.col_type": "Tipo",
    "docx.tcol.summarization": "Sumarização",
    "docx.tcol.hidden": "Oculta",
    "docx.tcol.measure_name": "Nome da Medida",
    "docx.tcol.measure_type": "Tipo",
    "docx.tcol.visual_id": "ID do Visual",
    "docx.tcol.img_name": "Nome",
    "docx.tcol.img_type": "Tipo",
    "docx.tcol.step": "Etapa",
    "docx.tcol.rule_or_filter": "Regra / Filtro",
    "docx.tcol.description": "Descrição",
    "docx.tcol.rel_from": "Origem",
    "docx.tcol.rel_arrow": "→",
    "docx.tcol.rel_to": "Destino",
    "docx.tcol.rel_bidirectional": "Bidirecional",
    "docx.tcol.rel_active": "Ativo",

    # Labels reusados em valores de celulas
    "docx.value.yes": "Sim",
    "docx.value.no": "Não",
    "docx.value.visible": "Visível",
    "docx.value.hidden_label": "Oculta",
    "docx.value.refresh_yes": "Sim",
    "docx.value.refresh_no": "Não",

    # Mensagens de info boxes
    "docx.info.dict_intro": "Leitura offline inferida a partir dos metadados do PBIP. O dicionário não usa dados reais das tabelas e deve ser validado com a área de negócio.",
    "docx.info.pages_count": "O relatório contém {n} página(s).",
    "docx.info.pages_empty_thin_report": "Nenhuma página encontrada localmente. Este projeto pode ser um relatório remoto (thin report) onde as páginas ficam armazenadas no serviço Power BI.",
    "docx.info.rel_count": "O modelo possui {n} relacionamentos entre tabelas.",
    "docx.info.pq_intro": "Leitura offline inferida a partir das etapas do Power Query M. Para compreensão completa da regra, consulte o código M original exibido abaixo.",
    "docx.info.pq_observations_intro": "Comentários `BI_DOC` são tratados como documentação oficial e aparecem antes da inferência automática.",

    # Etapa "Esta tabela aplica" no DOCX (espelha o MD)
    "docx.pq.summary_label": "Esta tabela aplica",
    "docx.pq.documented_observations": "Observações Documentadas",

    # Card de metadados da tabela individual (DOCX)
    "docx.tcard.status": "Status",
    "docx.tcard.refresh": "Atualização",
    "docx.tcard.columns": "Colunas",
    "docx.tcard.measures": "Medidas",
    "docx.tcard.source": "Fonte",
    "docx.tcard.source_import": "Importação",
    "docx.tcard.source_dax": "DAX",
    "docx.tcard.status_visible": "Visível",
    "docx.tcard.status_hidden": "Oculta",

    # Lista de Relacionamentos DOCX (tabela)
    "docx.rel.col.from": "Origem",
    "docx.rel.col.to": "Destino",
    "docx.rel.col.from_table": "Tabela de Origem",
    "docx.rel.col.from_column": "Coluna de Origem",
    "docx.rel.col.to_table": "Tabela de Destino",
    "docx.rel.col.to_column": "Coluna de Destino",
    "docx.rel.col.bidirectional": "Bidirecional",
    "docx.rel.col.active": "Ativo",
}


# ===========================================================================
# Catalogo en-US (placeholders por enquanto; tradutor preenche na Fase 4)
# ===========================================================================
# IMPORTANTE: enquanto vazio, o fallback usa pt-BR. Para nao quebrar nada
# durante a Fase 1, deixamos completamente vazio. Fase 4 preenche com a
# traducao cuidadosa de cada chave.

_EN_US: Dict[str, str] = {
    # -------------------------------------------------------------------
    # Document headings (Markdown ## headings)
    # -------------------------------------------------------------------
    "doc.toc.title": "📑 Table of Contents",
    "doc.toc.overview": "Overview",
    "doc.toc.dictionary": "Data Dictionary and Terms",
    "doc.toc.pages": "Report Pages",
    "doc.toc.model": "Data Model",
    "doc.toc.tables_summary": "Tables Summary",
    "doc.toc.tables_detail": "Tables Detail",
    "doc.toc.relationships": "Relationships",
    "doc.toc.custom_visuals": "Custom Visuals",
    "doc.toc.image_resources": "Image Resources",

    "doc.section.overview": "📈 Overview",
    "doc.section.dictionary": "Data Dictionary and Terms",
    "doc.section.glossary_dax": "📐 DAX Glossary",
    "doc.section.pages": "📄 Report Pages",
    "doc.section.model": "🗂️ Data Model",
    "doc.section.er_diagram": "Relationship Diagram (ER)",
    "doc.section.relationships_list": "🔗 Relationships List",
    "doc.section.query_groups": "📂 Query Groups",
    "doc.section.tables_summary": "📊 Tables Summary",
    "doc.section.tables_in_model": "📁 Model Tables",
    "doc.section.tables": "Tables",

    # -------------------------------------------------------------------
    # Cover
    # -------------------------------------------------------------------
    "cover.document_title_default": "Power BI Documentation",
    "cover.created_on": "Created on",

    # -------------------------------------------------------------------
    # Overview counters table
    # -------------------------------------------------------------------
    "overview.col.tables": "📁 Tables",
    "overview.col.measures": "📐 Measures",
    "overview.col.columns": "🔢 Columns",
    "overview.col.calc_columns": "🧮 Calculated",
    "overview.col.relationships": "🔗 Relationships",
    "overview.col.pages": "📄 Pages",
    "overview.dimensional_label": "**Dimensional model**",

    # Plurals for dimensional model summary
    "overview.dim.fact_one": "fact",
    "overview.dim.fact_many": "facts",
    "overview.dim.dim_one": "dimension",
    "overview.dim.dim_many": "dimensions",
    "overview.dim.aux_one": "auxiliary",
    "overview.dim.aux_many": "auxiliaries",

    # -------------------------------------------------------------------
    # Data dictionary
    # -------------------------------------------------------------------
    "dict.intro": "Offline reading inferred from PBIP metadata. The dictionary does not use real table data and should be validated with the business area.",
    "dict.col.term": "Term",
    "dict.col.frequency": "Occurrences",
    "dict.col.category": "Category",
    "dict.col.sources": "Where it appears",
    "dict.col.examples": "Examples",

    # Dictionary categories
    "dict.cat.indicator": "Indicator",
    "dict.cat.entity": "Entity",
    "dict.cat.time": "Time",
    "dict.cat.attribute": "Attribute",
    "dict.cat.identifier": "Identifier",
    "dict.cat.technical_rule": "Technical Rule",
    "dict.cat.filter": "Filter",
    "dict.cat.page_visual": "Page/Visual",
    "dict.cat.general": "General Term",
    "dict.cat.other": "Other",

    # -------------------------------------------------------------------
    # DAX glossary
    # -------------------------------------------------------------------
    "glossary_dax.intro": "DAX functions used in measures, calculated columns and tables of this project. Each measure below lists only function names — the full description lives here.",
    "glossary_dax.col.function": "Function",
    "glossary_dax.col.category": "Category",
    "glossary_dax.col.description": "Description",
    "glossary_dax.col.business_reading": "Business reading",

    "leitura_dax.functions_used": "**DAX functions used**",

    # -------------------------------------------------------------------
    # Measure lineage
    # -------------------------------------------------------------------
    "linhagem.measures_referenced": "**Referenced measures**",

    # -------------------------------------------------------------------
    # Power Query
    # -------------------------------------------------------------------
    "pq.business_rule_inferred": "Inferred Business Rule",
    "pq.intro": "Offline reading inferred from Power Query M steps. For full understanding of the rule, see the original M code shown below.",
    "pq.intro_with_observations": "`BI_DOC` comments are treated as official documentation and appear before the automatic inference.",
    "pq.documented_observations": "**Documented Observations**",
    "pq.summary_label": "**This table applies**",
    "pq.rules_title": "**Business Rules and Filters — Power Query**",
    "pq.col.step": "Step",
    "pq.col.rule_or_filter": "Rule / Filter",
    "pq.col.description": "Description",

    # Documented observation labels
    "pq.obs.general": "General",
    "pq.obs.source": "Source",
    "pq.obs.rule": "Rule",
    "pq.obs.observation": "Observation",

    # -------------------------------------------------------------------
    # Tables (per-table detail)
    # -------------------------------------------------------------------
    "table.col.status": "Status",
    "table.col.refresh": "Refresh",
    "table.col.columns": "Columns",
    "table.col.measures": "Measures",
    "table.col.source": "Source",

    "table.col.name": "Name",
    "table.col.type": "Type",
    "table.col.summarization": "Summarization",
    "table.col.hidden": "Hidden",

    "table.section.columns": "📋 Columns",
    "table.section.calc_columns_summary": "Calculated Columns (Summary)",
    "table.section.calc_columns_dax": "Calculated Columns - DAX Code",
    "table.section.measures_summary": "Measures (Summary)",
    "table.section.measures_dax": "Measures - DAX Code",
    "table.section.source_data": "💾 Data Source",

    "table.measure.col.name": "Name",
    "table.measure.col.type": "Type",
    "table.measure.col.name_full": "Measure Name",

    "table.calc.col.name": "Name",
    "table.calc.col.type": "Type",
    "table.calc.col.format": "Format",

    "table.status.visible": "🟢 Visible",
    "table.status.hidden": "🔴 Hidden",
    "table.refresh.yes": "✅ Yes",
    "table.refresh.no": "❌ No",
    "table.yes": "Yes",
    "table.no": "No",

    "table.source.import": "📥 Import",
    "table.source.dax": "📝 DAX",
    "table.source.sql": "🗃️ SQL",
    "table.source.oracle": "🔷 Oracle",
    "table.source.mode_label": "**Mode**",
    "table.source.group_label": "**Group**",
    "table.source.code_m": "**Source code (Power Query M)**",
    "table.source.code_dax": "**Source code (DAX)**",

    # -------------------------------------------------------------------
    # Inferred measure types
    # -------------------------------------------------------------------
    "measure.type.percentage": "Percentage",
    "measure.type.count": "Count",
    "measure.type.currency": "Currency",
    "measure.type.average": "Average",
    "measure.type.sum": "Sum",
    "measure.type.minmax": "Min/Max",
    "measure.type.numeric": "Numeric",

    # -------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------
    "rel.total_label": "*Total: {n} relationships*",
    "rel.col.from": "Source",
    "rel.col.arrow": "→",
    "rel.col.to": "Target",
    "rel.col.bidirectional": "Bidirectional",
    "rel.col.active": "Active",
    "rel.legend": "*Legend: `}|--||` = Bidirectional Filter | `}o--||` = Single Filter*",

    # -------------------------------------------------------------------
    # Tables summary
    # -------------------------------------------------------------------
    "tables_summary.intro": "*Overview of {n} tables in the model*",
    "tables_summary.col.idx": "#",
    "tables_summary.col.table": "Table",
    "tables_summary.col.columns": "Columns",
    "tables_summary.col.measures": "Measures",
    "tables_summary.col.calc_columns": "Calc. Columns",
    "tables_summary.col.source": "Source",
    "tables_summary.totals": "**Totals**: {cols} columns | {meds} measures | {calc} calculated columns",
    "tables_summary.doc_count": "*Total documented tables: {n}*",
    "tables_summary.empty": "*No table found in the project.*",

    # -------------------------------------------------------------------
    # Pages / report
    # -------------------------------------------------------------------
    "pages.total": "**Total pages: {n}**",
    "pages.empty_thin_report": "⚠️ No page found locally. This project may be a **remote report** (thin report) where pages are stored on the Power BI service.",

    # -------------------------------------------------------------------
    # Log messages
    # -------------------------------------------------------------------
    "log.dax_not_captured": "// [WARNING] DAX expression not captured during parsing",

    # -------------------------------------------------------------------
    # Filenames
    # -------------------------------------------------------------------
    "filename.suffix": "_documentation",

    # -------------------------------------------------------------------
    # DOCX-specific (mirror of MD with formatting variations)
    # -------------------------------------------------------------------
    "docx.toc.title": "Table of Contents",
    "docx.section.overview": "Overview",
    "docx.section.dictionary": "Data Dictionary and Terms",
    "docx.section.pages": "Report Pages",
    "docx.section.page_filters": "Page Filters",
    "docx.section.model": "Data Model",
    "docx.section.relationships_list": "Relationships List",
    "docx.section.query_groups": "Query Groups",
    "docx.section.tables_summary": "Tables Summary",
    "docx.section.tables_detail": "Tables Detail",
    "docx.section.columns": "Columns",
    "docx.section.calc_columns": "Calculated Columns",
    "docx.section.measures_dax": "DAX Measures",
    "docx.section.measures_code": "Measure Code",
    "docx.section.hierarchies": "Hierarchies",
    "docx.section.source_data": "Data Source",
    "docx.section.custom_visuals": "Custom Visuals",
    "docx.section.image_resources": "Image Resources",
    "docx.section.business_rule_inferred": "Inferred Business Rule",
    "docx.section.pq_rules": "Business Rules and Filters — Power Query",

    # Stats cards and cover info
    "docx.stat.tables": "Tables",
    "docx.stat.measures": "Measures",
    "docx.stat.measures_dax": "DAX Measures",
    "docx.stat.columns": "Columns",
    "docx.stat.calc_columns": "Calculated",
    "docx.stat.relationships": "Relationships",
    "docx.stat.pages": "Pages",
    "docx.stat.dimensional_label": "Dimensional model",

    # DOCX table columns
    "docx.tcol.term": "Term",
    "docx.tcol.frequency": "Occurrences",
    "docx.tcol.category": "Category",
    "docx.tcol.sources": "Where it appears",
    "docx.tcol.examples": "Examples",
    "docx.tcol.idx": "#",
    "docx.tcol.page_name": "Page Name",
    "docx.tcol.page_type": "Type",
    "docx.tcol.dimensions": "Dimensions",
    "docx.tcol.filters": "Filters",
    "docx.tcol.table": "Table",
    "docx.tcol.column": "Column",
    "docx.tcol.type": "Type",
    "docx.tcol.values": "Values",
    "docx.tcol.gq_name": "Name",
    "docx.tcol.gq_order": "Order",
    "docx.tcol.col_name": "Name",
    "docx.tcol.col_type": "Type",
    "docx.tcol.summarization": "Summarization",
    "docx.tcol.hidden": "Hidden",
    "docx.tcol.measure_name": "Measure Name",
    "docx.tcol.measure_type": "Type",
    "docx.tcol.visual_id": "Visual ID",
    "docx.tcol.img_name": "Name",
    "docx.tcol.img_type": "Type",
    "docx.tcol.step": "Step",
    "docx.tcol.rule_or_filter": "Rule / Filter",
    "docx.tcol.description": "Description",
    "docx.tcol.rel_from": "Source",
    "docx.tcol.rel_arrow": "→",
    "docx.tcol.rel_to": "Target",
    "docx.tcol.rel_bidirectional": "Bidirectional",
    "docx.tcol.rel_active": "Active",

    # DOCX cell values
    "docx.value.yes": "Yes",
    "docx.value.no": "No",
    "docx.value.visible": "Visible",
    "docx.value.hidden_label": "Hidden",
    "docx.value.refresh_yes": "Yes",
    "docx.value.refresh_no": "No",

    # DOCX info box messages
    "docx.info.dict_intro": "Offline reading inferred from PBIP metadata. The dictionary does not use real table data and should be validated with the business area.",
    "docx.info.pages_count": "The report contains {n} page(s).",
    "docx.info.pages_empty_thin_report": "No page found locally. This project may be a remote report (thin report) where pages are stored on the Power BI service.",
    "docx.info.rel_count": "The model has {n} relationships between tables.",
    "docx.info.pq_intro": "Offline reading inferred from Power Query M steps. For full understanding of the rule, see the original M code shown below.",
    "docx.info.pq_observations_intro": "`BI_DOC` comments are treated as official documentation and appear before the automatic inference.",

    "docx.pq.summary_label": "This table applies",
    "docx.pq.documented_observations": "Documented Observations",

    # Relationships list (DOCX)
    "docx.rel.col.from": "Source",
    "docx.rel.col.to": "Target",
    "docx.rel.col.from_table": "Source Table",
    "docx.rel.col.from_column": "Source Column",
    "docx.rel.col.to_table": "Target Table",
    "docx.rel.col.to_column": "Target Column",
    "docx.rel.col.bidirectional": "Bidirectional",
    "docx.rel.col.active": "Active",

    # Table metadata card (DOCX)
    "docx.tcard.status": "Status",
    "docx.tcard.refresh": "Refresh",
    "docx.tcard.columns": "Columns",
    "docx.tcard.measures": "Measures",
    "docx.tcard.source": "Source",
    "docx.tcard.source_import": "Import",
    "docx.tcard.source_dax": "DAX",
    "docx.tcard.status_visible": "Visible",
    "docx.tcard.status_hidden": "Hidden",

    # Tables summary intro paragraph (DOCX)
    "docx.tables_summary_intro": "The model has {n} tables with {cols} columns, {meds} measures and {calc} calculated columns.",

    # -------------------------------------------------------------------
    # DAX category labels (used in glossary table + leitura compacta)
    # -------------------------------------------------------------------
    "dax.cat.contexto_filtro": "Context and filters",
    "dax.cat.agregacao": "Aggregations and iterators",
    "dax.cat.relacionamento": "Relationships",
    "dax.cat.tempo": "Time intelligence",
    "dax.cat.logica": "Logic and handling",
    "dax.cat.texto": "Text and formatting",
    "dax.cat.tabela": "Table functions",

    # -------------------------------------------------------------------
    # DAX function glossary -- descricao + leitura_negocio por funcao.
    # Chave: dax.<NOME_LOWER>.desc / dax.<NOME_LOWER>.business
    # PT-BR vem do DAX_FUNCTION_CATALOG (sem chave aqui = fallback dataclass).
    # -------------------------------------------------------------------

    # Context and filters
    "dax.calculate.desc": "Evaluates an expression in a modified filter context.",
    "dax.calculate.business": "recomputes the metric by applying specific filter rules.",
    "dax.calculatetable.desc": "Evaluates a table in a modified filter context.",
    "dax.calculatetable.business": "produces an intermediate table with specific filters applied.",
    "dax.filter.desc": "Returns a table filtered by an expression.",
    "dax.filter.business": "applies a row-by-row rule to narrow down data.",
    "dax.all.desc": "Removes filters from a table or column.",
    "dax.all.business": "computes the indicator ignoring the currently selected filters.",
    "dax.allexcept.desc": "Removes all filters except the ones specified.",
    "dax.allexcept.business": "keeps only the relevant dimensions for the calculation.",
    "dax.allselected.desc": "Considers the externally selected filters.",
    "dax.allselected.business": "computes respecting the broader visual selection.",
    "dax.removefilters.desc": "Removes filters from columns or tables.",
    "dax.removefilters.business": "clears filters to obtain a comparison baseline.",
    "dax.keepfilters.desc": "Preserves existing filters while adding new ones.",
    "dax.keepfilters.business": "refines the context without overwriting selections.",
    "dax.values.desc": "Returns distinct values visible in the current context.",
    "dax.values.business": "gets the set of values available in the current context.",
    "dax.selectedvalue.desc": "Returns a single selected value, or an alternative.",
    "dax.selectedvalue.business": "reads a unique selection made by the user or context.",
    "dax.hasonevalue.desc": "Tests if exactly one value is visible.",
    "dax.hasonevalue.business": "checks whether the cell shows a single value before computing.",
    "dax.hasonefilter.desc": "Tests if exactly one filter is applied.",
    "dax.hasonefilter.business": "checks whether a single filter is active before computing.",
    "dax.lookupvalue.desc": "Looks up a value by key/value pairs.",
    "dax.lookupvalue.business": "retrieves an attribute when the rule needs an explicit match.",

    # Aggregations and iterators
    "dax.sum.desc": "Sums a numeric column.",
    "dax.sum.business": "calculates a direct total of a field.",
    "dax.sumx.desc": "Iterates a table and sums an expression.",
    "dax.sumx.business": "calculates a total row by row before summing.",
    "dax.average.desc": "Returns the arithmetic mean.",
    "dax.average.business": "calculates the average value of a metric.",
    "dax.averagex.desc": "Iterates a table and averages an expression.",
    "dax.averagex.business": "calculates an average row by row over a derived expression.",
    "dax.count.desc": "Counts non-blank rows.",
    "dax.count.business": "measures how many records contribute to the indicator.",
    "dax.counta.desc": "Counts non-blank cells, including text.",
    "dax.counta.business": "measures how many filled records exist.",
    "dax.countrows.desc": "Counts table rows.",
    "dax.countrows.business": "measures the total number of records.",
    "dax.distinctcount.desc": "Counts distinct values.",
    "dax.distinctcount.business": "measures the unique count of entities or keys.",
    "dax.min.desc": "Returns the smallest value.",
    "dax.min.business": "identifies the minimum value in the context.",
    "dax.minx.desc": "Iterates a table and returns the minimum expression value.",
    "dax.minx.business": "identifies the minimum of a derived expression.",
    "dax.max.desc": "Returns the largest value.",
    "dax.max.business": "identifies the maximum value in the context.",
    "dax.maxx.desc": "Iterates a table and returns the maximum expression value.",
    "dax.maxx.business": "identifies the maximum of a derived expression.",
    "dax.medianx.desc": "Iterates a table and returns the median.",
    "dax.medianx.business": "summarizes the central tendency of a metric.",
    "dax.rankx.desc": "Returns the rank of an item within a list.",
    "dax.rankx.business": "ranks entities by a chosen metric.",
    "dax.topn.desc": "Returns the top N rows of a table by an expression.",
    "dax.topn.business": "isolates the most relevant items by a ranking metric.",

    # Relationships
    "dax.related.desc": "Returns a related value from another table.",
    "dax.related.business": "joins attributes between related tables.",
    "dax.relatedtable.desc": "Returns the related table.",
    "dax.relatedtable.business": "accesses related records to aggregate or filter.",
    "dax.userelationship.desc": "Activates an inactive relationship for the calculation.",
    "dax.userelationship.business": "uses an alternative relationship path for a specific metric.",
    "dax.crossfilter.desc": "Changes the filter direction of a relationship.",
    "dax.crossfilter.business": "adjusts how dimensions filter facts for a specific rule.",
    "dax.treatas.desc": "Treats a table as if it filtered another column.",
    "dax.treatas.business": "applies a virtual filter across tables without a real relationship.",

    # Time intelligence
    "dax.totalytd.desc": "Returns the year-to-date total.",
    "dax.totalytd.business": "calculates the year-to-date accumulated indicator.",
    "dax.totalqtd.desc": "Returns the quarter-to-date total.",
    "dax.totalqtd.business": "calculates the quarter-to-date accumulated indicator.",
    "dax.totalmtd.desc": "Returns the month-to-date total.",
    "dax.totalmtd.business": "calculates the month-to-date accumulated indicator.",
    "dax.dateadd.desc": "Shifts dates by an interval.",
    "dax.dateadd.business": "compares periods shifted in time.",
    "dax.datediff.desc": "Returns the difference between two dates.",
    "dax.datediff.business": "calculates duration between events.",
    "dax.sameperiodlastyear.desc": "Returns the same period in the previous year.",
    "dax.sameperiodlastyear.business": "enables year-over-year comparison.",
    "dax.parallelperiod.desc": "Returns a parallel period from the calendar.",
    "dax.parallelperiod.business": "compares an indicator across equivalent periods.",
    "dax.previousmonth.desc": "Returns the previous month.",
    "dax.previousmonth.business": "compares the indicator to the previous month.",
    "dax.previousyear.desc": "Returns the previous year.",
    "dax.previousyear.business": "compares the indicator to the previous year.",
    "dax.nextmonth.desc": "Returns the next month.",
    "dax.nextmonth.business": "looks at the next-month value.",
    "dax.year.desc": "Extracts the year from a date.",
    "dax.year.business": "groups or compares results by year.",
    "dax.month.desc": "Extracts the month from a date.",
    "dax.month.business": "groups or compares results by month.",
    "dax.day.desc": "Extracts the day from a date.",
    "dax.day.business": "groups or compares results by day.",
    "dax.quarter.desc": "Extracts the quarter from a date.",
    "dax.quarter.business": "groups or compares results by quarter.",
    "dax.weekday.desc": "Returns the weekday from a date.",
    "dax.weekday.business": "groups or compares results by weekday.",
    "dax.weeknum.desc": "Returns the week number.",
    "dax.weeknum.business": "groups or compares results by week.",
    "dax.today.desc": "Returns today's date.",
    "dax.today.business": "uses the refresh date as a reference in the rule.",
    "dax.now.desc": "Returns the current date and time.",
    "dax.now.business": "uses the current moment as a reference in the rule.",
    "dax.eomonth.desc": "Returns the last day of the month.",
    "dax.eomonth.business": "creates a month-end reference for monthly indicators.",
    "dax.edate.desc": "Returns a date shifted by N months.",
    "dax.edate.business": "creates dates relative to a reference (deadlines, due dates).",
    "dax.calendar.desc": "Generates a calendar table.",
    "dax.calendar.business": "builds a custom date dimension.",
    "dax.calendarauto.desc": "Generates an automatic calendar from the model.",
    "dax.calendarauto.business": "builds a date dimension covering all dates used in the model.",

    # Logic and handling
    "dax.if.desc": "Applies a simple conditional rule.",
    "dax.if.business": "returns a result based on a business condition.",
    "dax.switch.desc": "Selects a result among multiple cases.",
    "dax.switch.business": "models classification or multi-scenario rules.",
    "dax.iferror.desc": "Returns an alternative value when the expression fails.",
    "dax.iferror.business": "handles errors silently with a safe value.",
    "dax.isblank.desc": "Tests for a blank value.",
    "dax.isblank.business": "handles missing values in the calculation.",
    "dax.iserror.desc": "Tests for an error value.",
    "dax.iserror.business": "handles error scenarios silently in the calculation.",
    "dax.isfiltered.desc": "Tests whether a column is being filtered.",
    "dax.isfiltered.business": "branches the calculation based on whether a filter is active.",
    "dax.iscrossfiltered.desc": "Tests whether a column is cross-filtered.",
    "dax.iscrossfiltered.business": "branches the calculation based on indirect filter activity.",
    "dax.blank.desc": "Returns a blank value.",
    "dax.blank.business": "omits a result when the rule should hide it.",
    "dax.divide.desc": "Divides with safe handling for error/zero division.",
    "dax.divide.business": "calculates a ratio or percentage with a safe fallback.",
    "dax.coalesce.desc": "Returns the first non-blank value.",
    "dax.coalesce.business": "picks a fallback value across candidates.",

    # Text and formatting
    "dax.format.desc": "Formats a value as text.",
    "dax.format.business": "controls textual presentation of a number, date, or measure.",
    "dax.concatenate.desc": "Concatenates two strings.",
    "dax.concatenate.business": "joins fields to build labels or composite keys.",
    "dax.concatenatex.desc": "Iterates a table and concatenates an expression.",
    "dax.concatenatex.business": "builds a list of values from related records.",
    "dax.upper.desc": "Converts text to uppercase.",
    "dax.upper.business": "standardizes text case for comparison.",
    "dax.lower.desc": "Converts text to lowercase.",
    "dax.lower.business": "standardizes text case for comparison.",
    "dax.left.desc": "Returns the first N characters of a text.",
    "dax.left.business": "extracts the leading portion of a code or text.",
    "dax.right.desc": "Returns the last N characters of a text.",
    "dax.right.business": "extracts the trailing portion of a code or text.",
    "dax.mid.desc": "Returns a slice of a text.",
    "dax.mid.business": "extracts a section of a text by position.",
    "dax.len.desc": "Returns the length of a text.",
    "dax.len.business": "validates or classifies based on text size.",
    "dax.substitute.desc": "Replaces occurrences of a substring.",
    "dax.substitute.business": "normalizes textual patterns within a field.",
    "dax.trim.desc": "Removes extra whitespace.",
    "dax.trim.business": "cleans accidental spaces in text fields.",

    # Table functions
    "dax.addcolumns.desc": "Adds calculated columns to a table.",
    "dax.addcolumns.business": "enriches a virtual table with auxiliary metrics.",
    "dax.selectcolumns.desc": "Returns selected columns of a table.",
    "dax.selectcolumns.business": "projects a custom view of a table.",
    "dax.summarize.desc": "Groups rows and aggregates results.",
    "dax.summarize.business": "summarizes data by analysis keys.",
    "dax.summarizecolumns.desc": "Groups and aggregates in an optimized way.",
    "dax.summarizecolumns.business": "produces summary tables for analytical exploration.",
    "dax.generate.desc": "Combines rows of two tables.",
    "dax.generate.business": "produces a virtual table joining records.",
    "dax.generateall.desc": "Generates a combined table preserving uncombined rows.",
    "dax.generateall.business": "produces a virtual table preserving records without a match.",
    "dax.generateseries.desc": "Generates a sequence of values.",
    "dax.generateseries.business": "produces a numeric sequence for iteration.",
    "dax.row.desc": "Returns a single-row table.",
    "dax.row.business": "produces a single-row virtual table.",
    "dax.union.desc": "Combines rows from multiple tables.",
    "dax.union.business": "consolidates virtual tables vertically.",
    "dax.intersect.desc": "Returns rows present in two tables.",
    "dax.intersect.business": "filters records that appear in both sources.",
    "dax.except.desc": "Returns rows that appear in the first but not the second.",
    "dax.except.business": "isolates records that exist only in one source.",
    "dax.crossjoin.desc": "Returns the Cartesian product of tables.",
    "dax.crossjoin.business": "creates all combinations across virtual tables.",
    "dax.naturalleftouterjoin.desc": "Returns an outer join based on column names.",
    "dax.naturalleftouterjoin.business": "joins virtual tables by shared columns.",
    "dax.naturalinnerjoin.desc": "Returns an inner join based on column names.",
    "dax.naturalinnerjoin.business": "joins virtual tables keeping only matching records.",
}


# ===========================================================================
# Estado global e helpers
# ===========================================================================

_LOCALE = "pt_BR"  # default; pode ser alterado via CLI --lang ou set_locale()


def set_locale(code: str) -> None:
    """Define o locale ativo.

    Aceita "pt", "pt_BR", "pt-BR", "en", "en_US", "en-US" (case-insensitive).
    Qualquer outro valor cai em pt_BR.
    """
    global _LOCALE
    code_norm = (code or "").lower().replace("-", "_")
    if code_norm in ("en", "en_us"):
        _LOCALE = "en_US"
    else:
        _LOCALE = "pt_BR"


def get_locale() -> str:
    """Retorna o codigo do locale ativo ('pt_BR' ou 'en_US')."""
    return _LOCALE


def _catalog() -> Dict[str, str]:
    return _EN_US if _LOCALE == "en_US" else _PT_BR


def t(key: str, **kwargs: Any) -> str:
    """Retorna a string traduzida para a chave, com placeholders opcionais.

    Fallback chain: locale ativo -> pt_BR -> "[?key]".
    """
    catalog = _catalog()
    template = catalog.get(key)
    if template is None and _LOCALE != "pt_BR":
        template = _PT_BR.get(key)
    if template is None:
        return f"[?{key}]"
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return template
    return template


def t_or(key: str, default: str, **kwargs: Any) -> str:
    """Como t(), mas usa `default` (em vez de '[?key]') quando a chave nao existe.

    Util para catalogos que ja tem versao pt-BR inline em outro lugar (ex.:
    DAX_FUNCTION_CATALOG) e queremos so sobrepor com EN quando disponivel.
    """
    catalog = _catalog()
    template = catalog.get(key)
    if template is None:
        return default.format(**kwargs) if kwargs else default
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return template
    return template
