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
    "doc.toc.title": "[[icon:toc]] Índice",
    "doc.toc.overview": "Visão Geral",
    "doc.toc.dictionary": "Dicionário de Dados e Termos",
    "doc.toc.pages": "Páginas do Relatório",
    "doc.toc.model": "Modelo de Dados",
    "doc.toc.tables_summary": "Resumo das Tabelas",
    "doc.toc.tables_detail": "Detalhamento das Tabelas",
    "doc.toc.relationships": "Relacionamentos",
    "doc.toc.custom_visuals": "Visuais Personalizados",
    "doc.toc.image_resources": "Recursos de Imagem",

    "doc.section.overview": "[[icon:overview]] Visão Geral",
    "doc.section.dictionary": "[[icon:dictionary]] Dicionário de Dados e Termos",
    "doc.section.glossary_dax": "[[icon:glossary]] Glossário DAX",
    "doc.section.pages": "[[icon:pages]] Páginas do Relatório",
    "doc.section.model": "[[icon:model]] Modelo de Dados",
    "doc.section.er_diagram": "Diagrama de Relacionamentos (ER)",
    "doc.section.relationships_list": "[[icon:link]] Lista de Relacionamentos",
    "doc.section.query_groups": "[[icon:folder-open]] Grupos de Consulta",
    "doc.section.tables_summary": "[[icon:chart]] Resumo das Tabelas",
    "doc.section.tables_in_model": "[[icon:tables]] Tabelas do Modelo",
    "doc.section.tables": "Tabelas",

    # -------------------------------------------------------------------
    # Capa
    # -------------------------------------------------------------------
    "cover.document_title_default": "Documentação Power BI",
    "cover.created_on": "Data de criação",
    "cover.subtitle": "Modelo Semântico e Camada de Relatório",
    "cover.project_updated": "Última atualização do projeto",
    "cover.tables_count": "Tabelas no modelo",
    "cover.measures_count": "Medidas DAX",
    "cover.generated_by": "Gerado por",

    # -------------------------------------------------------------------
    # Sumario executivo (pagina 2)
    # -------------------------------------------------------------------
    "exec.title": "Sumário Executivo",
    "exec.intro": "Visão geral do conteúdo deste documento, pensada para leitura rápida por gestores e stakeholders não-técnicos.",
    "exec.what.title": "O que este modelo entrega",
    "exec.what.body": "Conjunto de {tables} tabelas e {measures} medidas DAX organizadas em {facts} fato(s) e {dims} dimensão(ões), apresentadas em {pages} página(s) de relatório.",
    "exec.what.body_no_dim": "Conjunto de {tables} tabelas e {measures} medidas DAX, apresentadas em {pages} página(s) de relatório.",
    "exec.highlight.tables": "Tabelas",
    "exec.highlight.measures": "Medidas DAX",
    "exec.highlight.relationships": "Relacionamentos",
    "exec.highlight.pages": "Páginas",
    "exec.highlight.last_update": "Atualização do projeto",
    "exec.scope.title": "Escopo da documentação",
    "exec.scope.body": "Este documento abrange o modelo semântico (tabelas, colunas, medidas, relacionamentos, regras Power Query), o glossário de negócio inferido dos metadados, o glossário das funções DAX utilizadas e o catálogo de páginas do relatório com seus filtros.",

    # -------------------------------------------------------------------
    # Tabela de visao geral (cards de contadores)
    # -------------------------------------------------------------------
    "overview.col.tables": "Tabelas",
    "overview.col.measures": "Medidas",
    "overview.col.columns": "Colunas",
    "overview.col.calc_columns": "Calculadas",
    "overview.col.relationships": "Relacionamentos",
    "overview.col.pages": "Páginas",
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
    "dict.subtitle.business": "Termos de Negócio",
    "dict.subtitle.business_desc": "Conceitos do domínio — indicadores, entidades, períodos e atributos que falam a linguagem da área usuária.",
    "dict.subtitle.technical": "Termos Técnicos",
    "dict.subtitle.technical_desc": "Vocabulário interno de transformação — regras Power Query, padrões de etapas e identificadores estruturais.",
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

    # Estatisticas exibidas em cada medida (linha de chips abaixo do nome)
    "measure.stat.lines": "linhas DAX",
    "measure.stat.function": "função",
    "measure.stat.functions": "funções",
    "measure.stat.dependency": "dependência",
    "measure.stat.dependencies": "dependências",
    "measure.stat.table": "tabela referenciada",
    "measure.stat.tables": "tabelas referenciadas",

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

    "table.section.columns": "[[icon:columns]] Colunas",
    "table.section.calc_columns_summary": "Colunas Calculadas (Resumo)",
    "table.section.calc_columns_dax": "Colunas Calculadas - Código DAX",
    "table.section.measures_summary": "Medidas (Resumo)",
    "table.section.measures_dax": "Medidas - Código DAX",
    "table.section.source_data": "[[icon:save]] Fonte de Dados",

    "table.measure.col.name": "Nome",
    "table.measure.col.type": "Tipo",
    "table.measure.col.name_full": "Nome da Medida",

    "table.calc.col.name": "Nome",
    "table.calc.col.type": "Tipo",
    "table.calc.col.format": "Formato",

    "table.status.visible": "[[icon:eye]] Visível",
    "table.status.hidden": "[[icon:lock]] Oculta",
    "table.refresh.yes": "[[icon:check]] Sim",
    "table.refresh.no": "[[icon:x]] Não",
    "table.yes": "Sim",
    "table.no": "Não",

    "table.source.import": "[[icon:import]] Importação",
    "table.source.dax": "[[icon:dax]] DAX",
    "table.source.sql": "[[icon:database]] SQL",
    "table.source.oracle": "[[icon:database]] Oracle",
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
    "rel.legend": "**Como ler o diagrama:**\n\n- `}|` ou `}o` = lado **\"muitos\"** da relação (vários registros)\n- `||` = lado **\"um\"** da relação (registro único)\n- `}|--||` = **Filtro Bidirecional** — ambas as tabelas se filtram mutuamente\n- `}o--||` = **Filtro Único** — só a dimensão filtra a fato (direção padrão)",

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
    "pages.empty_thin_report": "[[icon:warning]] Nenhuma página encontrada localmente. Este projeto pode ser um **relatório remoto** (thin report) onde as páginas ficam armazenadas no serviço Power BI.",
    "pages.col.idx": "#",
    "pages.col.name": "Nome",
    "pages.col.type": "Tipo",
    "pages.col.dimensions": "Dimensões",
    "pages.col.filters": "Filtros",
    "pages.section.filters": "[[icon:filter]] Filtros de Página",
    "pages.filter.col.table": "Tabela",
    "pages.filter.col.column": "Coluna",
    "pages.filter.col.type": "Tipo",
    "pages.filter.col.values": "Valores",

    # Visuais Personalizados + Recursos de Imagem (colunas MD)
    "custom_visuals.col.id": "ID do Visual",
    "image_resources.col.name": "Nome",
    "image_resources.col.type": "Tipo",

    # Inline labels para coluna calculada (cabecalho proprio na descricao DAX)
    "calc_col.label.type": "Tipo",
    "calc_col.label.format": "Formato",

    # -------------------------------------------------------------------
    # Mensagens [AVISO] e log (apenas console; ja em pt-BR)
    # -------------------------------------------------------------------
    "log.dax_not_captured": "// [AVISO] Expressão DAX não capturada durante o parsing",

    # -------------------------------------------------------------------
    # Filenames (sufixo apos o nome do projeto)
    # -------------------------------------------------------------------
    "filename.suffix": "_documentacao",

    # -------------------------------------------------------------------
    # Power Query: templates de descricao inferida (coluna "Descricao")
    # Placeholders: {step} = nome da etapa, {cols} = lista de colunas
    # -------------------------------------------------------------------
    "pq.desc.navigation":   "Etapa `{step}` navega para um objeto específico dentro da origem de dados.",
    "pq.desc.filter":       "Etapa `{step}` mantém apenas os registros que atendem à condição informada.",
    "pq.desc.select_cols":  "Etapa `{step}` mantém somente as colunas: {cols}.",
    "pq.desc.remove_cols":  "Etapa `{step}` remove as colunas: {cols}.",
    "pq.desc.rename":       "Etapa `{step}` padroniza nomes de colunas.",
    "pq.desc.type_cast":    "Etapa `{step}` ajusta os tipos de dados das colunas: {cols}.",
    "pq.desc.calc_column":  "Etapa `{step}` cria uma coluna calculada a partir de regra definida em M.",
    "pq.desc.join":         "Etapa `{step}` combina dados com outra consulta/tabela.",
    "pq.desc.join_keys":    " Chaves ou campos citados: {cols}.",
    "pq.desc.expand":       "Etapa `{step}` expande campos relacionados.",
    "pq.desc.expand_cols":  " Campos expandidos: {cols}.",
    "pq.desc.group":        "Etapa `{step}` resume registros por chaves de análise.",
    "pq.desc.group_cols":   " Campos citados: {cols}.",
    "pq.desc.sort":         "Etapa `{step}` ordena os registros.",
    "pq.desc.sort_cols":    " Campos de ordenação: {cols}.",
    "pq.desc.dedup":        "Etapa `{step}` remove registros duplicados.",
    "pq.desc.dedup_cols":   " Campos considerados: {cols}.",
    "pq.desc.custom":       "Etapa `{step}` não foi classificada automaticamente. Consulte o código M original para detalhe completo.",
    "pq.desc.generic":      "Etapa `{step}` {action}",
    "pq.desc.aux_functions": " Funções auxiliares detectadas: {items}.",
    "pq.desc.more_functions": "; e mais {n} função(ões)",

    # Fallbacks usados na coluna "Regra / Filtro" quando o token de funcao
    # esta ausente (so aparecem em queries menos canonicas).
    "pq.rule.navigation_object":   "Objeto da origem",
    "pq.rule.data_source":         "Fonte de dados",
    "pq.rule.filter":               "Filtro",
    "pq.rule.selected_columns":     "Colunas selecionadas",
    "pq.rule.removed_columns":      "Colunas removidas",
    "pq.rule.rename_columns":       "Renomeação de colunas",
    "pq.rule.type_conversion":      "Conversão de tipos",
    "pq.rule.new_column":           "Nova coluna",
    "pq.rule.calc_column_prefix":   "Coluna calculada: {name}",
    "pq.rule.join_between_queries": "Junção entre consultas",
    "pq.rule.append_queries":       "Anexação de consultas",
    "pq.rule.expanded_fields":      "Campos expandidos",
    "pq.rule.group_aggregate":      "Agrupamento e agregação",
    "pq.rule.rows_to_cols":         "Linhas para colunas",
    "pq.rule.cols_to_rows":         "Colunas para linhas",
    "pq.rule.row_sort":             "Ordenação de linhas",
    "pq.rule.dedup":                "Remoção de duplicidades",
    "pq.rule.replace":              "Substituição",
    "pq.rule.promote_headers":      "Primeira linha como cabeçalho",
    "pq.rule.error_handling":       "Tratamento de erros",
    "pq.rule.row_limit":            "Limite/remoção por posição",
    "pq.rule.transform":            "Transformação",
    "pq.rule.custom_transform":     "Transformação personalizada",

    # Templates do _classificar_etapa_power_query (etapa.descricao usada
    # como fallback quando o linha_regra nao monta sua propria descricao).
    "pq.cls.source":                "Etapa `{step}` conecta ou lê dados de {source}.",
    "pq.cls.filter":                "Etapa `{step}` filtra linhas{detail}.",
    "pq.cls.filter_detail":         " usando a condição `{condition}`",
    "pq.cls.join":                  "Etapa `{step}` combina dados com outra consulta ou tabela.{detail}",
    "pq.cls.join_detail":           " Colunas/chaves citadas: {cols}.",
    "pq.cls.combine":               "Etapa `{step}` empilha/anexa dados de múltiplas consultas ou tabelas.",
    "pq.cls.expand":                "Etapa `{step}` expande colunas vindas de consulta relacionada.{detail}",
    "pq.cls.expand_detail":         " Campos expandidos: {cols}.",
    "pq.cls.remove_cols":           "Etapa `{step}` remove colunas{detail}.",
    "pq.cls.select_cols":           "Etapa `{step}` mantém somente colunas selecionadas{detail}.",
    "pq.cls.rename_cols":           "Etapa `{step}` renomeia colunas{detail}.",
    "pq.cls.type_cast":             "Etapa `{step}` ajusta tipos de dados das colunas{detail}.",
    "pq.cls.add_column":            "Etapa `{step}` cria coluna calculada{detail}.",
    "pq.cls.group":                 "Etapa `{step}` agrupa registros{detail}.",
    "pq.cls.group_detail":          " por {cols}",
    "pq.cls.sort":                  "Etapa `{step}` ordena linhas{detail}.",
    "pq.cls.dedup":                 "Etapa `{step}` remove duplicidades{detail}.",
    "pq.cls.dedup_detail":          " considerando {cols}",
    "pq.cls.replace":               "Etapa `{step}` substitui valores em colunas da tabela.",
    "pq.cls.unpivot":               "Etapa `{step}` transforma colunas em linhas (unpivot).",
    "pq.cls.pivot":                 "Etapa `{step}` transforma valores de linhas em colunas (pivot).",
    "pq.cls.promote_headers":       "Etapa `{step}` promove a primeira linha para cabeçalhos.",
    "pq.cls.row_limit":             "Etapa `{step}` limita ou remove linhas por posição/quantidade.",
    "pq.cls.custom":                "Etapa `{step}` executa transformação personalizada/não classificada.",
    "pq.cls.cols_suffix":           ": {cols}",
    "pq.cls.col_suffix":            " `{col}`",

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

    # -------------------------------------------------------------------
    # Validacao estrutural do PBIP (pre-extracao)
    # -------------------------------------------------------------------
    "validate.header": "Não foi possível documentar o projeto em {project}. Estrutura PBIP incompleta:",
    "validate.missing_model_folder": "Pasta do modelo semântico não encontrada: {folder}",
    "validate.missing_model_tmdl": "Arquivo principal do modelo (model.tmdl) não encontrado: {file}",
    "validate.missing_report_folder": "Pasta do relatório não encontrada: {folder} — a documentação será gerada sem páginas/visuais.",
    "validate.no_tables": "Nenhuma tabela TMDL encontrada no modelo — a documentação será mínima.",
    "validate.hint": "Abra o projeto no Power BI Desktop, salve novamente como PBIP e tente outra vez.",

    # -------------------------------------------------------------------
    # v0.9.3 — Container de medidas
    # -------------------------------------------------------------------
    "table.measures_container": "Container de medidas",
    "table.measures_lower": "medidas",

    # -------------------------------------------------------------------
    # v0.9.0 — Calculation Groups
    # -------------------------------------------------------------------
    "doc.section.calc_groups": "[[icon:calc]] Grupos de Cálculo",
    "calc_groups.intro": "Grupos de cálculo permitem aplicar variações dinâmicas (ex: YTD, YoY, % Total) sobre medidas existentes, sem precisar duplicá-las.",
    "calc_groups.precedence": "Precedência",
    "calc_groups.no_items": "Nenhum item de cálculo definido.",
    "calc_groups.col.name": "Item",
    "calc_groups.col.ordinal": "Ordem",
    "calc_groups.expr": "Expressão DAX",
    "calc_groups.format_string": "Format String dinâmica",

    # -------------------------------------------------------------------
    # v0.9.0 — Perspectives
    # -------------------------------------------------------------------
    "doc.section.perspectives": "[[icon:eye]] Perspectivas",
    "perspectives.intro": "Perspectivas são visões reduzidas do modelo para diferentes audiências. Mostram apenas um subconjunto de tabelas, colunas e medidas — sem restringir acesso aos dados.",
    "perspectives.empty": "Perspectiva vazia (sem tabelas declaradas).",
    "perspectives.whole_table": "tabela inteira",
    "perspectives.col.table": "Tabela",
    "perspectives.col.included": "Incluído",
    "perspectives.col.columns": "Colunas",
    "perspectives.col.measures": "Medidas",
    "perspectives.col.hierarchies": "Hierarquias",
    "perspectives.col_count": "{n} coluna(s)",
    "perspectives.measure_count": "{n} medida(s)",
    "perspectives.hier_count": "{n} hierarquia(s)",

    # -------------------------------------------------------------------
    # v0.9.0 — Security (RLS + OLS)
    # -------------------------------------------------------------------
    "doc.section.security": "[[icon:lock]] Segurança (RLS / OLS)",
    "security.intro": "Roles de segurança definem **quem vê o quê**. RLS (Row-Level Security) filtra linhas por usuário; OLS (Object-Level Security) restringe metadados de colunas.",
    "security.model_permission": "Permissão no modelo",
    "security.members": "Membros",
    "security.no_table_permissions": "Sem restrições por tabela — acesso total.",
    "security.col.table": "Tabela",
    "security.col.rls": "RLS",
    "security.col.ols": "OLS",
    "security.col.column": "Coluna",
    "security.col.permission": "Permissão",
    "security.filter": "Filtro RLS (DAX)",
    "security.column_permissions": "Restrições de colunas (OLS)",
    "security.cols_restricted": "{n} coluna(s) restrita(s)",

    # -------------------------------------------------------------------
    # v0.9.0 — Named Expressions (parametros M + queries compartilhadas)
    # -------------------------------------------------------------------
    "doc.section.named_expressions": "[[icon:wrench]] Parâmetros e Expressões M",
    "named_expressions.intro": "Parâmetros e expressões compartilhadas declarados no nível do modelo. Parâmetros M (`IsParameterQuery=true`) podem ser editados sem alterar o código.",
    "named_expressions.params_heading": "Parâmetros",
    "named_expressions.queries_heading": "Expressões compartilhadas",
    "named_expressions.col.name": "Nome",
    "named_expressions.col.type": "Tipo",
    "named_expressions.col.required": "Obrigatório",
    "named_expressions.col.value": "Valor atual",
    "named_expressions.col.group": "Grupo",
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
    "doc.toc.title": "[[icon:toc]] Table of Contents",
    "doc.toc.overview": "Overview",
    "doc.toc.dictionary": "Data Dictionary and Terms",
    "doc.toc.pages": "Report Pages",
    "doc.toc.model": "Data Model",
    "doc.toc.tables_summary": "Tables Summary",
    "doc.toc.tables_detail": "Tables Detail",
    "doc.toc.relationships": "Relationships",
    "doc.toc.custom_visuals": "Custom Visuals",
    "doc.toc.image_resources": "Image Resources",

    "doc.section.overview": "[[icon:overview]] Overview",
    "doc.section.dictionary": "[[icon:dictionary]] Data Dictionary and Terms",
    "doc.section.glossary_dax": "[[icon:glossary]] DAX Glossary",
    "doc.section.pages": "[[icon:pages]] Report Pages",
    "doc.section.model": "[[icon:model]] Data Model",
    "doc.section.er_diagram": "Relationship Diagram (ER)",
    "doc.section.relationships_list": "[[icon:link]] Relationships List",
    "doc.section.query_groups": "[[icon:folder-open]] Query Groups",
    "doc.section.tables_summary": "[[icon:chart]] Tables Summary",
    "doc.section.tables_in_model": "[[icon:tables]] Model Tables",
    "doc.section.tables": "Tables",

    # -------------------------------------------------------------------
    # Cover
    # -------------------------------------------------------------------
    "cover.document_title_default": "Power BI Documentation",
    "cover.created_on": "Created on",
    "cover.subtitle": "Semantic Model and Report Layer",
    "cover.project_updated": "Last project update",
    "cover.tables_count": "Tables in model",
    "cover.measures_count": "DAX measures",
    "cover.generated_by": "Generated by",

    # -------------------------------------------------------------------
    # Executive summary (page 2)
    # -------------------------------------------------------------------
    "exec.title": "Executive Summary",
    "exec.intro": "High-level overview of this document, designed for quick reading by managers and non-technical stakeholders.",
    "exec.what.title": "What this model delivers",
    "exec.what.body": "A set of {tables} tables and {measures} DAX measures organized into {facts} fact(s) and {dims} dimension(s), presented across {pages} report page(s).",
    "exec.what.body_no_dim": "A set of {tables} tables and {measures} DAX measures, presented across {pages} report page(s).",
    "exec.highlight.tables": "Tables",
    "exec.highlight.measures": "DAX measures",
    "exec.highlight.relationships": "Relationships",
    "exec.highlight.pages": "Pages",
    "exec.highlight.last_update": "Project update",
    "exec.scope.title": "Documentation scope",
    "exec.scope.body": "This document covers the semantic model (tables, columns, measures, relationships, Power Query rules), the business glossary inferred from metadata, the DAX function glossary used, and the report page catalog with filters.",

    # -------------------------------------------------------------------
    # Overview counters table
    # -------------------------------------------------------------------
    "overview.col.tables": "Tables",
    "overview.col.measures": "Measures",
    "overview.col.columns": "Columns",
    "overview.col.calc_columns": "Calculated",
    "overview.col.relationships": "Relationships",
    "overview.col.pages": "Pages",
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
    "dict.subtitle.business": "Business Terms",
    "dict.subtitle.business_desc": "Domain concepts — indicators, entities, periods and attributes spoken in business language.",
    "dict.subtitle.technical": "Technical Terms",
    "dict.subtitle.technical_desc": "Internal transformation vocabulary — Power Query rules, step patterns and structural identifiers.",
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

    "measure.stat.lines": "DAX lines",
    "measure.stat.function": "function",
    "measure.stat.functions": "functions",
    "measure.stat.dependency": "dependency",
    "measure.stat.dependencies": "dependencies",
    "measure.stat.table": "referenced table",
    "measure.stat.tables": "referenced tables",

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

    "table.section.columns": "[[icon:columns]] Columns",
    "table.section.calc_columns_summary": "Calculated Columns (Summary)",
    "table.section.calc_columns_dax": "Calculated Columns - DAX Code",
    "table.section.measures_summary": "Measures (Summary)",
    "table.section.measures_dax": "Measures - DAX Code",
    "table.section.source_data": "[[icon:save]] Data Source",

    "table.measure.col.name": "Name",
    "table.measure.col.type": "Type",
    "table.measure.col.name_full": "Measure Name",

    "table.calc.col.name": "Name",
    "table.calc.col.type": "Type",
    "table.calc.col.format": "Format",

    "table.status.visible": "[[icon:eye]] Visible",
    "table.status.hidden": "[[icon:lock]] Hidden",
    "table.refresh.yes": "[[icon:check]] Yes",
    "table.refresh.no": "[[icon:x]] No",
    "table.yes": "Yes",
    "table.no": "No",

    "table.source.import": "[[icon:import]] Import",
    "table.source.dax": "[[icon:dax]] DAX",
    "table.source.sql": "[[icon:database]] SQL",
    "table.source.oracle": "[[icon:database]] Oracle",
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
    "rel.legend": "**How to read the diagram:**\n\n- `}|` or `}o` = **\"many\"** side of the relationship (multiple records)\n- `||` = **\"one\"** side of the relationship (single record)\n- `}|--||` = **Bidirectional Filter** — both tables filter each other\n- `}o--||` = **Single Filter** — only the dimension filters the fact (default direction)",

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
    "pages.empty_thin_report": "[[icon:warning]] No page found locally. This project may be a **remote report** (thin report) where pages are stored on the Power BI service.",
    "pages.col.idx": "#",
    "pages.col.name": "Name",
    "pages.col.type": "Type",
    "pages.col.dimensions": "Dimensions",
    "pages.col.filters": "Filters",
    "pages.section.filters": "[[icon:filter]] Page Filters",
    "pages.filter.col.table": "Table",
    "pages.filter.col.column": "Column",
    "pages.filter.col.type": "Type",
    "pages.filter.col.values": "Values",

    # Custom Visuals + Image Resources (MD columns)
    "custom_visuals.col.id": "Visual ID",
    "image_resources.col.name": "Name",
    "image_resources.col.type": "Type",

    # Inline labels for calculated column (DAX description header)
    "calc_col.label.type": "Type",
    "calc_col.label.format": "Format",

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
    # Power Query inferred description templates
    # -------------------------------------------------------------------
    "pq.desc.navigation":   "Step `{step}` navigates to a specific object inside the data source.",
    "pq.desc.filter":       "Step `{step}` keeps only the records that match the given condition.",
    "pq.desc.select_cols":  "Step `{step}` keeps only the columns: {cols}.",
    "pq.desc.remove_cols":  "Step `{step}` removes the columns: {cols}.",
    "pq.desc.rename":       "Step `{step}` standardizes column names.",
    "pq.desc.type_cast":    "Step `{step}` adjusts the data types of the columns: {cols}.",
    "pq.desc.calc_column":  "Step `{step}` creates a calculated column from a rule defined in M.",
    "pq.desc.join":         "Step `{step}` combines data with another query/table.",
    "pq.desc.join_keys":    " Keys or fields mentioned: {cols}.",
    "pq.desc.expand":       "Step `{step}` expands related fields.",
    "pq.desc.expand_cols":  " Expanded fields: {cols}.",
    "pq.desc.group":        "Step `{step}` summarizes records by analysis keys.",
    "pq.desc.group_cols":   " Fields mentioned: {cols}.",
    "pq.desc.sort":         "Step `{step}` sorts the records.",
    "pq.desc.sort_cols":    " Sort fields: {cols}.",
    "pq.desc.dedup":        "Step `{step}` removes duplicate records.",
    "pq.desc.dedup_cols":   " Fields considered: {cols}.",
    "pq.desc.custom":       "Step `{step}` could not be automatically classified. See the original M code for full detail.",
    "pq.desc.generic":      "Step `{step}` {action}",
    "pq.desc.aux_functions": " Auxiliary functions detected: {items}.",
    "pq.desc.more_functions": "; and {n} more function(s)",

    # Rule column fallbacks
    "pq.rule.navigation_object":   "Source object",
    "pq.rule.data_source":         "Data source",
    "pq.rule.filter":               "Filter",
    "pq.rule.selected_columns":     "Selected columns",
    "pq.rule.removed_columns":      "Removed columns",
    "pq.rule.rename_columns":       "Column rename",
    "pq.rule.type_conversion":      "Type conversion",
    "pq.rule.new_column":           "New column",
    "pq.rule.calc_column_prefix":   "Calculated column: {name}",
    "pq.rule.join_between_queries": "Join between queries",
    "pq.rule.append_queries":       "Append queries",
    "pq.rule.expanded_fields":      "Expanded fields",
    "pq.rule.group_aggregate":      "Group and aggregate",
    "pq.rule.rows_to_cols":         "Rows to columns",
    "pq.rule.cols_to_rows":         "Columns to rows",
    "pq.rule.row_sort":             "Row sort",
    "pq.rule.dedup":                "Duplicate removal",
    "pq.rule.replace":              "Replace",
    "pq.rule.promote_headers":      "Promote first row as headers",
    "pq.rule.error_handling":       "Error handling",
    "pq.rule.row_limit":            "Row limit/removal by position",
    "pq.rule.transform":            "Transform",
    "pq.rule.custom_transform":     "Custom transform",

    # _classificar_etapa_power_query templates (EN)
    "pq.cls.source":                "Step `{step}` connects to or reads data from {source}.",
    "pq.cls.filter":                "Step `{step}` filters rows{detail}.",
    "pq.cls.filter_detail":         " using the condition `{condition}`",
    "pq.cls.join":                  "Step `{step}` combines data with another query or table.{detail}",
    "pq.cls.join_detail":           " Columns/keys mentioned: {cols}.",
    "pq.cls.combine":               "Step `{step}` stacks/appends data from multiple queries or tables.",
    "pq.cls.expand":                "Step `{step}` expands columns coming from a related query.{detail}",
    "pq.cls.expand_detail":         " Expanded fields: {cols}.",
    "pq.cls.remove_cols":           "Step `{step}` removes columns{detail}.",
    "pq.cls.select_cols":           "Step `{step}` keeps only selected columns{detail}.",
    "pq.cls.rename_cols":           "Step `{step}` renames columns{detail}.",
    "pq.cls.type_cast":             "Step `{step}` casts the data types of columns{detail}.",
    "pq.cls.add_column":            "Step `{step}` creates a calculated column{detail}.",
    "pq.cls.group":                 "Step `{step}` groups records{detail}.",
    "pq.cls.group_detail":          " by {cols}",
    "pq.cls.sort":                  "Step `{step}` sorts rows{detail}.",
    "pq.cls.dedup":                 "Step `{step}` removes duplicates{detail}.",
    "pq.cls.dedup_detail":          " considering {cols}",
    "pq.cls.replace":               "Step `{step}` replaces values in table columns.",
    "pq.cls.unpivot":               "Step `{step}` turns columns into rows (unpivot).",
    "pq.cls.pivot":                 "Step `{step}` turns row values into columns (pivot).",
    "pq.cls.promote_headers":       "Step `{step}` promotes the first row to headers.",
    "pq.cls.row_limit":             "Step `{step}` limits or removes rows by position/count.",
    "pq.cls.custom":                "Step `{step}` runs a custom/unclassified transformation.",
    "pq.cls.cols_suffix":           ": {cols}",
    "pq.cls.col_suffix":            " `{col}`",

    # Power Query function business readings (EN translations).
    # Used in _descricao_catalogo_generica via i18n.t_or; fallback to PT in dataclass.
    # Covers the most user-visible functions in the final client doc.
    "m_func.Table.ReplaceErrorValues.business":      "handles conversion errors without dropping the row.",
    "m_func.Table.RemoveRowsWithErrors.business":    "removes invalid records caused by conversion or calculation.",
    "m_func.Table.SelectRowsWithErrors.business":    "isolates problematic records for review or treatment.",
    "m_func.Table.FillDown.business":                "propagates header/group values to rows below.",
    "m_func.Table.FillUp.business":                  "propagates values from below to records above.",
    "m_func.Table.Distinct.business":                "keeps unique combinations of records.",
    "m_func.Table.RemoveDuplicates.business":        "ensures uniqueness by one or more keys.",
    "m_func.Table.ReplaceValue.business":            "standardizes or corrects values in selected fields.",
    "m_func.Table.Buffer.business":                  "stabilizes the read of one step before further transformations.",
    "m_func.Table.PromoteHeaders.business":          "uses the first row of the file as column names.",
    "m_func.Table.DemoteHeaders.business":           "turns column names into records.",
    "m_func.Text.Clean.business":                    "sanitizes fields imported from files or systems.",
    "m_func.Text.Trim.business":                     "cleans accidental spaces in text fields.",
    "m_func.Text.Replace.business":                  "corrects textual patterns in fields.",
    "m_func.Date.From.business":                     "ensures a date type for time analysis.",
    "m_func.DateTime.From.business":                 "ensures temporal granularity with time.",
    "m_func.try otherwise.business":                 "defines a contingency rule when a transformation fails.",
    "m_func.if then else.business":                  "implements a conditional business rule.",

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

    # -------------------------------------------------------------------
    # PBIP structural validation (pre-extraction)
    # -------------------------------------------------------------------
    "validate.header": "Couldn't document the project at {project}. PBIP structure is incomplete:",
    "validate.missing_model_folder": "Semantic model folder not found: {folder}",
    "validate.missing_model_tmdl": "Main model file (model.tmdl) not found: {file}",
    "validate.missing_report_folder": "Report folder not found: {folder} — documentation will be generated without pages/visuals.",
    "validate.no_tables": "No TMDL tables found in the model — documentation will be minimal.",
    "validate.hint": "Open the project in Power BI Desktop, save it again as PBIP and try again.",

    # -------------------------------------------------------------------
    # v0.9.3 — Measures container
    # -------------------------------------------------------------------
    "table.measures_container": "Measures container",
    "table.measures_lower": "measures",

    # -------------------------------------------------------------------
    # v0.9.0 — Calculation Groups
    # -------------------------------------------------------------------
    "doc.section.calc_groups": "[[icon:calc]] Calculation Groups",
    "calc_groups.intro": "Calculation groups let you apply dynamic variations (e.g. YTD, YoY, % Total) on top of existing measures without duplicating them.",
    "calc_groups.precedence": "Precedence",
    "calc_groups.no_items": "No calculation items defined.",
    "calc_groups.col.name": "Item",
    "calc_groups.col.ordinal": "Order",
    "calc_groups.expr": "DAX expression",
    "calc_groups.format_string": "Dynamic format string",

    # -------------------------------------------------------------------
    # v0.9.0 — Perspectives
    # -------------------------------------------------------------------
    "doc.section.perspectives": "[[icon:eye]] Perspectives",
    "perspectives.intro": "Perspectives are reduced views of the model for different audiences. They expose only a subset of tables, columns and measures — without restricting data access.",
    "perspectives.empty": "Empty perspective (no tables declared).",
    "perspectives.whole_table": "whole table",
    "perspectives.col.table": "Table",
    "perspectives.col.included": "Included",
    "perspectives.col.columns": "Columns",
    "perspectives.col.measures": "Measures",
    "perspectives.col.hierarchies": "Hierarchies",
    "perspectives.col_count": "{n} column(s)",
    "perspectives.measure_count": "{n} measure(s)",
    "perspectives.hier_count": "{n} hierarchy(ies)",

    # -------------------------------------------------------------------
    # v0.9.0 — Security (RLS + OLS)
    # -------------------------------------------------------------------
    "doc.section.security": "[[icon:lock]] Security (RLS / OLS)",
    "security.intro": "Security roles define **who sees what**. RLS (Row-Level Security) filters rows per user; OLS (Object-Level Security) restricts column metadata.",
    "security.model_permission": "Model permission",
    "security.members": "Members",
    "security.no_table_permissions": "No table restrictions — full access.",
    "security.col.table": "Table",
    "security.col.rls": "RLS",
    "security.col.ols": "OLS",
    "security.col.column": "Column",
    "security.col.permission": "Permission",
    "security.filter": "RLS filter (DAX)",
    "security.column_permissions": "Column restrictions (OLS)",
    "security.cols_restricted": "{n} restricted column(s)",

    # -------------------------------------------------------------------
    # v0.9.0 — Named Expressions (M parameters + shared queries)
    # -------------------------------------------------------------------
    "doc.section.named_expressions": "[[icon:wrench]] Parameters and M Expressions",
    "named_expressions.intro": "Parameters and shared expressions declared at the model level. M parameters (`IsParameterQuery=true`) can be edited without changing code.",
    "named_expressions.params_heading": "Parameters",
    "named_expressions.queries_heading": "Shared expressions",
    "named_expressions.col.name": "Name",
    "named_expressions.col.type": "Type",
    "named_expressions.col.required": "Required",
    "named_expressions.col.value": "Current value",
    "named_expressions.col.group": "Group",
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
