# -*- coding: utf-8 -*-
"""
icons.py - Sistema de icones SVG minimalistas para documentacao HTML.

Substituicao para emojis (que dao aspecto "vibe coding" e tem encoding
fragil entre Windows/cp1252 e Linux/utf-8). Os SVGs sao monocromaticos,
herdam a cor do texto via `currentColor` e tem tamanho controlado por
font-size (1em). Visual: inspirado em Lucide/Tabler, traco fino.

Uso:
    1. No markdown/i18n, escreva `[[icon:database]]` (token ASCII puro).
    2. No pipeline HTML, chame `substituir_icones_em_html(html)` antes
       de salvar. O token vira `<svg class="icon">...</svg>` inline.
    3. Em MD/DOCX, chame `remover_tokens_icone(texto)` para limpar o
       placeholder (DOCX nao renderiza SVG inline da mesma forma).
"""
from __future__ import annotations

import re
from typing import Dict


# Cada SVG eh um path 24x24 viewBox, stroke="currentColor" stroke-width="1.75".
# Tudo `fill="none"` para visual de linha fina (estilo Lucide).
# IMPORTANTE: o `viewBox` precisa ser 24x24 — todos os paths foram desenhados
# para essa grade. Mexer no viewBox quebra o alinhamento.
_BASE_SVG = (
    '<svg class="icon" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" focusable="false">{paths}</svg>'
)


# Paths SVG por nome de icone. Todos minimalistas, monocromaticos.
_ICON_PATHS: Dict[str, str] = {
    # ---------- Estrutura / navegacao ----------
    "toc": (
        '<line x1="8" y1="6" x2="20" y2="6"/>'
        '<line x1="8" y1="12" x2="20" y2="12"/>'
        '<line x1="8" y1="18" x2="20" y2="18"/>'
        '<circle cx="4" cy="6" r="1"/>'
        '<circle cx="4" cy="12" r="1"/>'
        '<circle cx="4" cy="18" r="1"/>'
    ),
    "overview": (  # grafico em alta
        '<polyline points="3,17 9,11 13,15 21,7"/>'
        '<polyline points="14,7 21,7 21,14"/>'
    ),
    "dictionary": (  # livro aberto
        '<path d="M4 5a2 2 0 0 1 2-2h5v16H6a2 2 0 0 0-2 2V5z"/>'
        '<path d="M20 5a2 2 0 0 0-2-2h-5v16h5a2 2 0 0 1 2 2V5z"/>'
    ),
    "glossary": (  # regua/format
        '<path d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>'
        '<line x1="3" y1="9" x2="21" y2="9"/>'
        '<line x1="9" y1="9" x2="9" y2="12"/>'
        '<line x1="15" y1="9" x2="15" y2="12"/>'
        '<line x1="3" y1="15" x2="21" y2="15"/>'
        '<line x1="9" y1="15" x2="9" y2="18"/>'
        '<line x1="15" y1="15" x2="15" y2="18"/>'
    ),
    "pages": (  # documento
        '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>'
        '<polyline points="14,3 14,9 20,9"/>'
    ),
    "model": (  # diagrama de blocos conectados
        '<rect x="3" y="4" width="6" height="6" rx="1"/>'
        '<rect x="15" y="4" width="6" height="6" rx="1"/>'
        '<rect x="9" y="14" width="6" height="6" rx="1"/>'
        '<line x1="6" y1="10" x2="11" y2="14"/>'
        '<line x1="18" y1="10" x2="13" y2="14"/>'
    ),
    "link": (  # corrente
        '<path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.5 1.5"/>'
        '<path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.5-1.5"/>'
    ),
    "folder": (  # pasta
        '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>'
    ),
    "folder-open": (
        '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1H3V7z"/>'
        '<path d="M3 9h18l-2 8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/>'
    ),
    "table": (  # tabela
        '<rect x="3" y="4" width="18" height="16" rx="1"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
        '<line x1="3" y1="16" x2="21" y2="16"/>'
        '<line x1="9" y1="4" x2="9" y2="20"/>'
        '<line x1="15" y1="4" x2="15" y2="20"/>'
    ),
    "tables": (  # multiplas tabelas (resumo)
        '<rect x="2" y="6" width="14" height="12" rx="1"/>'
        '<rect x="8" y="3" width="14" height="12" rx="1" fill="#ffffff"/>'
        '<line x1="2" y1="11" x2="16" y2="11"/>'
        '<line x1="9" y1="6" x2="9" y2="18"/>'
    ),
    "columns": (  # 3 colunas verticais
        '<rect x="4" y="4" width="4" height="16" rx="1"/>'
        '<rect x="10" y="4" width="4" height="16" rx="1"/>'
        '<rect x="16" y="4" width="4" height="16" rx="1"/>'
    ),
    "measure": (  # sigma (estilizado)
        '<polyline points="6,4 18,4 12,12 18,20 6,20"/>'
    ),
    "calc": (  # calculadora
        '<rect x="5" y="3" width="14" height="18" rx="2"/>'
        '<line x1="9" y1="7" x2="15" y2="7"/>'
        '<line x1="9" y1="12" x2="9.01" y2="12"/>'
        '<line x1="12" y1="12" x2="12.01" y2="12"/>'
        '<line x1="15" y1="12" x2="15.01" y2="12"/>'
        '<line x1="9" y1="16" x2="9.01" y2="16"/>'
        '<line x1="12" y1="16" x2="12.01" y2="16"/>'
        '<line x1="15" y1="16" x2="15.01" y2="16"/>'
    ),
    "hash": (  # # para colunas numero
        '<line x1="4" y1="9" x2="20" y2="9"/>'
        '<line x1="4" y1="15" x2="20" y2="15"/>'
        '<line x1="10" y1="3" x2="8" y2="21"/>'
        '<line x1="16" y1="3" x2="14" y2="21"/>'
    ),
    "page": (  # documento simples
        '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>'
        '<polyline points="14,3 14,9 20,9"/>'
    ),
    "database": (
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5v6c0 1.7 4 3 9 3s9-1.3 9-3V5"/>'
        '<path d="M3 11v6c0 1.7 4 3 9 3s9-1.3 9-3v-6"/>'
    ),
    "save": (  # disquete (fonte)
        '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
        '<polyline points="17,21 17,13 7,13 7,21"/>'
        '<polyline points="7,3 7,8 15,8"/>'
    ),
    "code": (  # < / >
        '<polyline points="16,18 22,12 16,6"/>'
        '<polyline points="8,6 2,12 8,18"/>'
    ),
    "dax": (  # f(x)
        '<path d="M4 7c0-2 1-3 3-3"/>'
        '<line x1="3" y1="11" x2="9" y2="11"/>'
        '<path d="M12 7l8 10"/>'
        '<path d="M20 7l-8 10"/>'
    ),
    "import": (  # download/import
        '<path d="M12 3v12"/>'
        '<polyline points="7,10 12,15 17,10"/>'
        '<path d="M5 21h14"/>'
    ),
    "search": (
        '<circle cx="11" cy="11" r="7"/>'
        '<line x1="21" y1="21" x2="16" y2="16"/>'
    ),
    "filter": (
        '<polygon points="3,4 21,4 14,12 14,20 10,20 10,12"/>'
    ),
    "lock": (
        '<rect x="5" y="11" width="14" height="10" rx="2"/>'
        '<path d="M8 11V7a4 4 0 0 1 8 0v4"/>'
    ),
    "eye": (
        '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "wrench": (
        '<path d="M14.7 6.3a4 4 0 0 0 5 5L21 13l-8 8a2 2 0 1 1-3-3l8-8 1.7-1.7z"/>'
    ),
    "settings": (  # engrenagem (alt para parametros)
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'
    ),
    "scroll": (  # pergaminho
        '<path d="M5 4h11a3 3 0 0 1 3 3v10a3 3 0 0 0 3 3"/>'
        '<path d="M19 20H6a3 3 0 0 1-3-3V6a2 2 0 0 1 2-2"/>'
        '<line x1="8" y1="9" x2="14" y2="9"/>'
        '<line x1="8" y1="13" x2="14" y2="13"/>'
    ),
    "shuffle": (  # hierarquia / rotas
        '<polyline points="16,3 21,3 21,8"/>'
        '<line x1="21" y1="3" x2="14" y2="10"/>'
        '<polyline points="21,16 21,21 16,21"/>'
        '<line x1="21" y1="21" x2="14" y2="14"/>'
        '<line x1="3" y1="3" x2="10" y2="10"/>'
        '<line x1="3" y1="21" x2="10" y2="14"/>'
    ),
    "package": (  # caixa (container de medidas)
        '<path d="M12 2 3 6.5v11L12 22l9-4.5v-11z"/>'
        '<line x1="12" y1="22" x2="12" y2="11"/>'
        '<polyline points="3,6.5 12,11 21,6.5"/>'
    ),
    "check": (
        '<polyline points="5,12 10,17 19,7"/>'
    ),
    "x": (
        '<line x1="6" y1="6" x2="18" y2="18"/>'
        '<line x1="6" y1="18" x2="18" y2="6"/>'
    ),
    "circle-filled": (  # ponto solido (item visivel)
        '<circle cx="12" cy="12" r="6" fill="currentColor"/>'
    ),
    "circle-outline": (  # circulo vazio (item nao oculto/neutro)
        '<circle cx="12" cy="12" r="6"/>'
    ),
    "warning": (
        '<path d="M12 3 2 21h20L12 3z"/>'
        '<line x1="12" y1="10" x2="12" y2="14"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
    ),
    "info": (
        '<circle cx="12" cy="12" r="9"/>'
        '<line x1="12" y1="11" x2="12" y2="16"/>'
        '<line x1="12" y1="8" x2="12.01" y2="8"/>'
    ),
    "calendar": (
        '<rect x="3" y="5" width="18" height="16" rx="2"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
        '<line x1="8" y1="3" x2="8" y2="7"/>'
        '<line x1="16" y1="3" x2="16" y2="7"/>'
    ),
    "user": (
        '<circle cx="12" cy="8" r="4"/>'
        '<path d="M4 21a8 8 0 0 1 16 0"/>'
    ),
    "tag": (
        '<path d="M20 12 12 4H4v8l8 8 8-8z"/>'
        '<circle cx="8" cy="8" r="1.2" fill="currentColor"/>'
    ),
    "grid": (  # cards / overview
        '<rect x="3" y="3" width="7" height="7" rx="1"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1"/>'
    ),
    "chart": (  # bar chart
        '<line x1="6" y1="20" x2="6" y2="10"/>'
        '<line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="18" y1="20" x2="18" y2="14"/>'
        '<line x1="3" y1="20" x2="21" y2="20"/>'
    ),
    "moon": (  # toggle dark mode
        '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>'
    ),
    "sun": (  # toggle light mode
        '<circle cx="12" cy="12" r="4"/>'
        '<line x1="12" y1="2" x2="12" y2="5"/>'
        '<line x1="12" y1="19" x2="12" y2="22"/>'
        '<line x1="2" y1="12" x2="5" y2="12"/>'
        '<line x1="19" y1="12" x2="22" y2="12"/>'
        '<line x1="4.9" y1="4.9" x2="7" y2="7"/>'
        '<line x1="17" y1="17" x2="19.1" y2="19.1"/>'
        '<line x1="4.9" y1="19.1" x2="7" y2="17"/>'
        '<line x1="17" y1="7" x2="19.1" y2="4.9"/>'
    ),
    "print": (
        '<polyline points="6,9 6,3 18,3 18,9"/>'
        '<rect x="4" y="9" width="16" height="9" rx="1"/>'
        '<rect x="7" y="14" width="10" height="7"/>'
    ),
}


# Aliases — varios nomes apontando para o mesmo SVG, para
# uso semantico claro no codigo.
_ALIASES: Dict[str, str] = {
    "params": "wrench",
    "calc_groups": "calc",
    "hidden": "circle-filled",
    "visible": "circle-outline",
    "yes": "check",
    "no": "x",
    "sql": "database",
    "oracle": "database",
    "source": "save",
    "card-tables": "tables",
    "card-measures": "measure",
    "card-columns": "columns",
    "card-calc": "calc",
    "card-relations": "link",
    "card-pages": "page",
}


def _resolver_path(nome: str) -> str:
    nome = nome.lower().strip()
    if nome in _ALIASES:
        nome = _ALIASES[nome]
    return _ICON_PATHS.get(nome, "")


def render_icon(nome: str, css_class: str = "icon") -> str:
    """Renderiza um SVG inline para o icone solicitado.

    Se o nome nao existir, retorna string vazia (fail-safe — nunca quebra a
    pagina por causa de um icone faltando)."""
    paths = _resolver_path(nome)
    if not paths:
        return ""
    svg = _BASE_SVG.format(paths=paths)
    if css_class != "icon":
        svg = svg.replace('class="icon"', f'class="{css_class}"', 1)
    return svg


# Regex que casa [[icon:NOME]] — nome aceita letras, numeros, hifen.
_TOKEN_RE = re.compile(r"\[\[icon:([a-z0-9\-]+)\]\]", re.IGNORECASE)


def substituir_icones_em_html(html: str) -> str:
    """Substitui todos os tokens [[icon:NOME]] por <svg> inline.

    Tokens desconhecidos sao removidos (string vazia). Usar APOS o markdown
    -> html converter, porque o token e ASCII puro e nao interfere no parser."""
    def _repl(match: re.Match) -> str:
        return render_icon(match.group(1))
    return _TOKEN_RE.sub(_repl, html)


def remover_tokens_icone(texto: str) -> str:
    """Remove os tokens [[icon:NOME]] do texto (usar em DOCX/MD onde SVG
    inline nao se aplica)."""
    return _TOKEN_RE.sub("", texto)


def envolver_com_icone(token_nome: str, texto: str) -> str:
    """Atalho para gerar `[[icon:NOME]] texto` (com espaco)."""
    return f"[[icon:{token_nome}]] {texto}"


# CSS minimo recomendado para os icones inline:
#
#   .icon {
#     width: 1em;
#     height: 1em;
#     vertical-align: -0.15em;
#     margin-right: 0.4em;
#     display: inline-block;
#   }
#   h1 .icon, h2 .icon, h3 .icon { opacity: 0.7; }
#
# O `currentColor` nos paths faz o SVG herdar a cor do h1/h2/parent.
