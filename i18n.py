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
}


# ===========================================================================
# Catalogo en-US (placeholders por enquanto; tradutor preenche na Fase 4)
# ===========================================================================
# IMPORTANTE: enquanto vazio, o fallback usa pt-BR. Para nao quebrar nada
# durante a Fase 1, deixamos completamente vazio. Fase 4 preenche com a
# traducao cuidadosa de cada chave.

_EN_US: Dict[str, str] = {
    # Phase 4 -- preencher com traducoes manuais cuidadosas.
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
