"""
Documentador de Projetos Power BI (.pbip)

Script para gerar documentação automática em Markdown de projetos Power BI Desktop.
Extrai informações do modelo semântico e relatório.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple


# ============================================================================
# DATACLASSES - Estruturas de Dados
# ============================================================================

@dataclass
class InfoColuna:
    """Informações de uma coluna regular de tabela"""
    nome: str
    tipo_dado: str = "string"
    formato: Optional[str] = None
    sumarizacao: str = "none"
    coluna_fonte: Optional[str] = None
    esta_oculta: bool = False
    categoria_dados: Optional[str] = None


@dataclass
class InfoColunaCalculada:
    """Informações de uma coluna calculada (com DAX)"""
    nome: str
    expressao_dax: str
    tipo_dado: str = "string"
    formato: Optional[str] = None
    sumarizacao: str = "none"


@dataclass
class InfoMedida:
    """Informações de uma medida DAX"""
    nome: str
    expressao_dax: str
    formato: Optional[str] = None
    formato_dinamico: Optional[str] = None


@dataclass
class InfoHierarquia:
    """Informações de uma hierarquia"""
    nome: str
    niveis: List[str] = field(default_factory=list)


@dataclass
class InfoParticao:
    """Informações da partição (fonte de dados)"""
    nome: str
    modo: str = "import"
    grupo_consulta: Optional[str] = None
    codigo_fonte: str = ""


@dataclass
class InfoTabela:
    """Informações completas de uma tabela"""
    nome: str
    esta_oculta: bool = False
    excluida_refresh: bool = False
    colunas: List[InfoColuna] = field(default_factory=list)
    medidas: List[InfoMedida] = field(default_factory=list)
    colunas_calculadas: List[InfoColunaCalculada] = field(default_factory=list)
    hierarquias: List[InfoHierarquia] = field(default_factory=list)
    particao: Optional[InfoParticao] = None


@dataclass
class InfoRelacionamento:
    """Informações de um relacionamento entre tabelas"""
    id: str
    tabela_origem: str
    coluna_origem: str
    tabela_destino: str
    coluna_destino: str
    filtro_bidirecional: bool = False
    esta_ativo: bool = True
    comportamento_data: Optional[str] = None


@dataclass
class InfoModelo:
    """Informações gerais do modelo semântico"""
    cultura: str = "pt-BR"
    versao_datasource: str = ""
    grupos_consulta: List[Dict] = field(default_factory=list)
    tabelas_referenciadas: List[str] = field(default_factory=list)
    annotations: Dict = field(default_factory=dict)


@dataclass
class InfoVisual:
    """Informações de um visual na página"""
    tipo: str
    titulo: Optional[str] = None
    nome: str = ""  # ID interno ou nome do container


@dataclass
class InfoPagina:
    """Informações de uma página do relatório"""
    id: str
    nome_exibicao: str
    largura: int = 1280
    altura: int = 720
    opcao_exibicao: str = "FitToPage"
    tipo: str = "Normal"
    filtros: Optional[List[Dict]] = None
    visuais: List[InfoVisual] = field(default_factory=list)


# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def limpar_nome(nome: str) -> str:
    """Remove aspas simples do nome se existirem"""
    return nome.strip().strip("'\"")


def arquivo_existe(caminho: str) -> bool:
    """Verifica se arquivo existe"""
    return os.path.isfile(caminho)


def obter_com_fallback(dicionario: dict, chave: str, padrao=None):
    """Obtém valor do dicionário ou retorna padrão"""
    return dicionario.get(chave, padrao)


# ============================================================================
# PARSING - JSON
# ============================================================================

def parse_json(caminho: str) -> dict:
    """
    Lê e parseia arquivo JSON.
    Retorna dict vazio se arquivo não existir ou houver erro.
    """
    if not arquivo_existe(caminho):
        return {}
    
    try:
        with open(caminho, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler JSON {caminho}: {e}")
        return {}


# ============================================================================
# PARSING - TMDL
# ============================================================================

def extrair_expressao_multilinhas(linhas: List[str], indice_inicio: int) -> Tuple[str, int]:
    """
    Extrai expressões DAX/M que podem ocupar múltiplas linhas.
    
    Returns:
        (expressao, indice_final)
    """
    expressao_partes = []
    i = indice_inicio
    
    # Verifica se começa com ```
    linha_atual = linhas[i].strip()
    
    if linha_atual.endswith('```'):
        # Expressão multilinha delimitada
        i += 1
        while i < len(linhas):
            linha = linhas[i].rstrip()
            if linha.strip() == '```':
                i += 1
                break
            expressao_partes.append(linha)
            i += 1
    else:
        # Expressão inline (na mesma linha)
        # Pega tudo após o =
        if '=' in linha_atual:
            expressao_partes.append(linha_atual.split('=', 1)[1].strip())
            i += 1
    
    return '\n'.join(expressao_partes), i


def parse_tmdl_relationships(caminho: str) -> List[InfoRelacionamento]:
    """
    Parseia arquivo relationships.tmdl
    """
    if not arquivo_existe(caminho):
        return []
    
    relacionamentos = []
    
    try:
        with open(caminho, 'r', encoding='utf-8-sig') as f:
            linhas = f.readlines()
        
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            
            # Detecta início de relacionamento
            match = re.match(r'^relationship\s+(.+)$', linha)
            if match:
                rel_id = match.group(1).strip()
                rel_info = {
                    'id': rel_id,
                    'fromTable': None,
                    'fromColumn': None,
                    'toTable': None,
                    'toColumn': None,
                    'crossFilteringBehavior': 'singleDirection',
                    'isActive': True,
                    'joinOnDateBehavior': None
                }
                
                # Lê propriedades do relacionamento
                i += 1
                while i < len(linhas):
                    linha_prop = linhas[i].strip()
                    
                    # Fim do bloco de relacionamento
                    if linha_prop and not linha_prop.startswith(('fromColumn', 'toColumn', 'crossFilteringBehavior', 'isActive', 'joinOnDateBehavior')):
                        break
                    
                    # fromColumn ou toColumn
                    match_col = re.match(r'^(fromColumn|toColumn):\s*(.+)\.(.+)$', linha_prop)
                    if match_col:
                        tipo = match_col.group(1)
                        tabela = limpar_nome(match_col.group(2))
                        coluna = limpar_nome(match_col.group(3))
                        
                        if tipo == 'fromColumn':
                            rel_info['fromTable'] = tabela
                            rel_info['fromColumn'] = coluna
                        else:
                            rel_info['toTable'] = tabela
                            rel_info['toColumn'] = coluna
                    
                    # Outras propriedades
                    match_prop = re.match(r'^(\w+):\s*(.+)$', linha_prop)
                    if match_prop:
                        prop_nome = match_prop.group(1)
                        prop_valor = match_prop.group(2).strip()
                        
                        if prop_nome == 'crossFilteringBehavior':
                            rel_info['crossFilteringBehavior'] = prop_valor
                        elif prop_nome == 'isActive':
                            rel_info['isActive'] = prop_valor.lower() != 'false'
                        elif prop_nome == 'joinOnDateBehavior':
                            rel_info['joinOnDateBehavior'] = prop_valor
                    
                    i += 1
                
                # Cria objeto InfoRelacionamento
                if rel_info['fromTable'] and rel_info['toTable']:
                    relacionamento = InfoRelacionamento(
                        id=rel_info['id'],
                        tabela_origem=rel_info['fromTable'],
                        coluna_origem=rel_info['fromColumn'],
                        tabela_destino=rel_info['toTable'],
                        coluna_destino=rel_info['toColumn'],
                        filtro_bidirecional=(rel_info['crossFilteringBehavior'] == 'bothDirections'),
                        esta_ativo=rel_info['isActive'],
                        comportamento_data=rel_info['joinOnDateBehavior']
                    )
                    relacionamentos.append(relacionamento)
                
                continue
            
            i += 1
    
    except Exception as e:
        print(f"Erro ao parsear relationships.tmdl: {e}")
    
    return relacionamentos


def parse_tmdl_model(caminho: str) -> InfoModelo:
    """
    Parseia arquivo model.tmdl
    """
    info = InfoModelo()
    
    if not arquivo_existe(caminho):
        return info
    
    try:
        with open(caminho, 'r', encoding='utf-8-sig') as f:
            linhas = f.readlines()
        
        grupo_atual = None
        
        for linha in linhas:
            linha_strip = linha.strip()
            
            # Cultura
            if linha_strip.startswith('culture:'):
                info.cultura = linha_strip.split(':', 1)[1].strip()
            
            # Versão datasource
            elif linha_strip.startswith('defaultPowerBIDataSourceVersion:'):
                info.versao_datasource = linha_strip.split(':', 1)[1].strip()
            
            # Query group
            elif 'queryGroup' in linha_strip:
                match = re.search(r"queryGroup\s+['\"](.+?)['\"]", linha_strip)
                if match:
                    grupo_atual = {'nome': match.group(1), 'ordem': 0}
            
            # Ordem do grupo
            elif grupo_atual and 'PBI_QueryGroupOrder' in linha_strip:
                match = re.search(r'=\s*(\d+)', linha_strip)
                if match:
                    grupo_atual['ordem'] = int(match.group(1))
                    info.grupos_consulta.append(grupo_atual)
                    grupo_atual = None
            
            # Referências de tabela
            elif linha_strip.startswith('ref table'):
                match = re.search(r"ref table\s+['\"](.+?)['\"]", linha_strip)
                if match:
                    info.tabelas_referenciadas.append(match.group(1))
            
            # Annotations
            elif linha_strip.startswith('annotation'):
                match = re.match(r'annotation\s+(\S+)\s*=\s*(.+)$', linha_strip)
                if match:
                    info.annotations[match.group(1)] = match.group(2)
    
    except Exception as e:
        print(f"Erro ao parsear model.tmdl: {e}")
    
    return info


def parse_tmdl_table(caminho: str) -> Optional[InfoTabela]:
    """
    Parseia arquivo .tmdl de uma tabela.
    DEFENSIVO: Retorna None em qualquer erro, nunca falha.
    """
    if not arquivo_existe(caminho):
        return None
    
    try:
        with open(caminho, 'r', encoding='utf-8-sig') as f:
            linhas = f.readlines()
    except Exception as e:
        print(f"  [AVISO] Erro ao ler {caminho}: {e}")
        return None
    
    # Validação básica
    if not linhas:
        return None
    
    # Extrai nome da tabela
    nome_tabela = None
    try:
        for linha in linhas[:min(10, len(linhas))]:  # Procura nas primeiras linhas
            match = re.match(r"^table\s+['\"]?(.+?)['\"]?\s*$", linha.strip())
            if match:
                nome_tabela = limpar_nome(match.group(1))
                break
    except Exception:
        pass
    
    if not nome_tabela:
        return None
    
    tabela = InfoTabela(nome=nome_tabela)
    
    # Parse linha por linha
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        
        # Tabela oculta
        if linha == 'isHidden':
            tabela.esta_oculta = True
        
        # Excluída de refresh
        elif linha == 'excludeFromModelRefresh':
            tabela.excluida_refresh = True
        
        # Coluna regular ou calculada
        elif linha.startswith('column '):
            # Tenta capturar nome entre aspas primeiro
            match_quoted = re.match(r"^column\s+['\"](.+?)['\"]\s*(?:=\s*(.+))?$", linha)
            # Se não tiver aspas, captura até o = (se houver) ou até o fim
            match_unquoted = re.match(r"^column\s+(\S+)\s*(?:=\s*(.+))?$", linha)
            
            match = match_quoted or match_unquoted
            if match:
                nome_col = limpar_nome(match.group(1))
                expressao = match.group(2)
                
                if expressao:
                    # Coluna calculada
                    if expressao.strip() == '```':
                        # Expressão multilinha
                        expressao_completa, i = extrair_expressao_multilinhas(linhas, i)
                    else:
                        expressao_completa = expressao.strip()
                        i += 1
                    
                    col_calc = InfoColunaCalculada(nome=nome_col, expressao_dax=expressao_completa)
                    
                    # Lê propriedades da coluna calculada
                    while i < len(linhas):
                        linha_prop = linhas[i].strip()
                        if not linha_prop.startswith(('dataType', 'formatString', 'summarizeBy', 'lineageTag', 'annotation',
                                                     'changedProperty')):
                            break
                        
                        if linha_prop.startswith('dataType:'):
                            col_calc.tipo_dado = linha_prop.split(':', 1)[1].strip()
                        elif linha_prop.startswith('formatString:'):
                            col_calc.formato = linha_prop.split(':', 1)[1].strip()
                        elif linha_prop.startswith('summarizeBy:'):
                            col_calc.sumarizacao = linha_prop.split(':', 1)[1].strip()
                        
                        i += 1
                    
                    tabela.colunas_calculadas.append(col_calc)
                    continue
                
                else:
                    # Coluna regular
                    coluna = InfoColuna(nome=nome_col)
                    i += 1
                    
                    # Lê propriedades da coluna
                    while i < len(linhas):
                        linha_prop = linhas[i].strip()
                        
                        if not linha_prop.startswith(('dataType', 'formatString', 'summarizeBy', 'sourceColumn', 
                                                     'isHidden', 'dataCategory', 'lineageTag', 'annotation',
                                                     'changedProperty', 'variation')):
                            break
                        
                        # Bloco variation: pula todas as sub-linhas indentadas
                        if linha_prop.startswith('variation'):
                            i += 1
                            while i < len(linhas):
                                sub_linha = linhas[i]
                                # Sub-propriedades são indentadas com tabs/espaços extras
                                if sub_linha.strip() and not sub_linha.startswith('\t\t\t') and not sub_linha.startswith('            '):
                                    break
                                i += 1
                            continue

                        
                        if linha_prop.startswith('dataType:'):
                            coluna.tipo_dado = linha_prop.split(':', 1)[1].strip()
                        elif linha_prop.startswith('formatString:'):
                            coluna.formato = linha_prop.split(':', 1)[1].strip()
                        elif linha_prop.startswith('summarizeBy:'):
                            coluna.sumarizacao = linha_prop.split(':', 1)[1].strip()
                        elif linha_prop.startswith('sourceColumn:'):
                            coluna.coluna_fonte = linha_prop.split(':', 1)[1].strip()
                        elif linha_prop == 'isHidden':
                            coluna.esta_oculta = True
                        elif linha_prop.startswith('dataCategory:'):
                            coluna.categoria_dados = linha_prop.split(':', 1)[1].strip()
                        
                        i += 1
                    
                    tabela.colunas.append(coluna)
                    continue
        
        # Medida
        elif linha.startswith('measure '):
            # Tenta capturar nome entre aspas primeiro (com ou sem =)
            match_quoted = re.match(r"^measure\s+['\"](.+?)['\"]\s*=?", linha)
            # Se não tiver aspas, captura até o = (se houver) ou fim da linha
            match_unquoted = re.match(r"^measure\s+(\S+)\s*=?", linha)
            
            match = match_quoted or match_unquoted
            if match:
                nome_medida = limpar_nome(match.group(1))
                
                # Extrai expressão - verifica se tem = na linha
                if '=' in linha:
                    # Tem = na mesma linha
                    partes_split = linha.split('=', 1)
                    if len(partes_split) > 1 and partes_split[1].strip():
                        # Tem conteúdo após o =
                        if linha.rstrip().endswith('```'):
                            expressao, i = extrair_expressao_multilinhas(linhas, i)
                        else:
                            # Expressão inline
                            expressao = partes_split[1].strip()
                            i += 1
                    else:
                        # Tem = mas nada depois - expressão na próxima linha
                        i += 1
                        expressao = ""
                        # Pula linhas vazias
                        while i < len(linhas) and not linhas[i].strip():
                            i += 1
                        if i < len(linhas):
                            proxima = linhas[i].strip()
                            if proxima and not proxima.startswith(('formatString', 'lineageTag', 'annotation')):
                                # A próxima linha é a expressão
                                if proxima == '```' or proxima.startswith('```'):
                                    expressao, i = extrair_expressao_multilinhas(linhas, i)
                                else:
                                    # Expressão DAX multilinha SEM delimitadores ```
                                    # Continua lendo até encontrar propriedade ou nova entidade
                                    linhas_dax = []
                                    while i < len(linhas):
                                        linha_atual = linhas[i]
                                        linha_strip = linha_atual.strip()
                                        
                                        # Para se encontrar uma propriedade TMDL ou nova entidade
                                        if linha_strip and (
                                            linha_strip.startswith(('formatString:', 'formatStringDefinition', 'lineageTag', 'annotation', 'changedProperty')) or
                                            linha_strip.startswith(('measure ', 'column ', 'hierarchy ', 'partition ', 'expression'))
                                        ):
                                            break
                                        
                                        # Adiciona a linha (mantém indentação original do DAX)
                                        linhas_dax.append(linha_atual.rstrip())
                                        i += 1
                                    
                                    # Junta as linhas e remove indentação comum
                                    expressao = '\n'.join(linhas_dax).strip()
                else:
                    # Não tem = na mesma linha - verifica próxima
                    i += 1
                    expressao = ""
                    if i < len(linhas):
                        proxima = linhas[i].strip()
                        # Medida sem expressão (apenas declarada)
                        if not proxima or proxima.startswith(('changedProperty', 'formatString', 'lineageTag', 'annotation',
                                                              'measure ', 'column ', 'hierarchy ', 'partition ')):
                            pass  # expressão fica vazia
                        elif proxima.startswith('='):
                            if '```' in proxima:
                                expressao, i = extrair_expressao_multilinhas(linhas, i)
                            else:
                                expressao = proxima.split('=', 1)[1].strip() if '=' in proxima else ""
                                i += 1
                        elif proxima == '```':
                            expressao, i = extrair_expressao_multilinhas(linhas, i)
                
                medida = InfoMedida(nome=nome_medida, expressao_dax=expressao)
                
                # Lê propriedades da medida
                while i < len(linhas):
                    linha_prop = linhas[i].strip()
                    
                    if not linha_prop.startswith(('formatString:', 'formatStringDefinition', 'lineageTag', 'annotation',
                                                 'changedProperty')):
                        break
                    
                    if linha_prop.startswith('formatString:'):
                        medida.formato = linha_prop.split(':', 1)[1].strip()
                    elif linha_prop.startswith('formatStringDefinition'):
                        # Formato dinâmico
                        if linha_prop.endswith('```'):
                            formato_din, i = extrair_expressao_multilinhas(linhas, i)
                            medida.formato_dinamico = formato_din
                            continue
                    
                    i += 1
                
                tabela.medidas.append(medida)
            else:
                # DEBUG: Se não conseguiu fazer match, mostra a linha
                print(f"  [DEBUG] Falha ao parsear medida: {linha[:80]}")
            continue
        
        # Hierarquia
        elif linha.startswith('hierarchy '):
            match = re.match(r"^hierarchy\s+['\"]?(.+?)['\"]?$", linha)
            if match:
                nome_hier = limpar_nome(match.group(1))
                hierarquia = InfoHierarquia(nome=nome_hier)
                i += 1
                
                # Lê níveis
                while i < len(linhas):
                    linha_prop = linhas[i].strip()
                    
                    if linha_prop.startswith('level '):
                        match_nivel = re.match(r"^level\s+['\"]?(.+?)['\"]?$", linha_prop)
                        if match_nivel:
                            hierarquia.niveis.append(limpar_nome(match_nivel.group(1)))
                    elif not linha_prop.startswith(('lineageTag', 'column:')):
                        break
                    
                    i += 1
                
                tabela.hierarquias.append(hierarquia)
                continue
        
        # Partição
        elif linha.startswith('partition '):
            match = re.match(r"^partition\s+['\"]?(.+?)['\"]?\s*=\s*(\w+)", linha)
            if match:
                nome_part = limpar_nome(match.group(1))
                tipo_part = match.group(2)
                
                particao = InfoParticao(nome=nome_part)
                i += 1
                
                # Lê propriedades
                while i < len(linhas):
                    linha_prop = linhas[i].strip()
                    linha_raw = linhas[i]  # Mantém indentação original
                    
                    if linha_prop.startswith('mode:'):
                        particao.modo = linha_prop.split(':', 1)[1].strip()
                    elif linha_prop.startswith('queryGroup:'):
                        particao.grupo_consulta = limpar_nome(linha_prop.split(':', 1)[1].strip())
                    elif linha_prop.startswith('source') or linha_prop.startswith('expression'):
                        # Código fonte M ou DAX
                        if '```' in linha_prop:
                            # Com delimitadores ```
                            codigo, i = extrair_expressao_multilinhas(linhas, i)
                            particao.codigo_fonte = codigo
                            break
                        elif '=' in linha_prop:
                            # source = ou source = código
                            partes = linha_prop.split('=', 1)
                            resto = partes[1].strip() if len(partes) > 1 else ""
                            
                            if resto:
                                # Código inline após =
                                particao.codigo_fonte = resto
                                i += 1
                            else:
                                # Código nas próximas linhas (indentado)
                                i += 1
                                linhas_codigo = []
                                
                                # Pega todas as linhas indentadas até próxima propriedade
                                while i < len(linhas):
                                    linha_cod = linhas[i]
                                    linha_cod_strip = linha_cod.strip()
                                    
                                    # Para se encontrar linha não indentada (nova propriedade)
                                    # ou linha de annotation/outra seção
                                    if linha_cod_strip and not linha_cod.startswith('\t') and not linha_cod.startswith('    '):
                                        break
                                    if linha_cod_strip.startswith('annotation ') or linha_cod_strip.startswith('lineageTag'):
                                        break
                                    
                                    linhas_codigo.append(linha_cod.rstrip())
                                    i += 1
                                
                                particao.codigo_fonte = '\n'.join(linhas_codigo).strip()
                            break
                        else:
                            i += 1
                            break
                    elif not linha_prop.startswith(('lineageTag', 'annotation')):
                        break
                    
                    i += 1
                
                tabela.particao = particao
                continue
        
        i += 1
    
    return tabela


# ============================================================================
# CLASSE PRINCIPAL
# ============================================================================

class DocumentadorPBIP:
    """
    Classe principal para documentar projetos Power BI (.pbip)
    """
    
    def __init__(self, caminho_projeto: str):
        """
        Inicializa o documentador
        
        Args:
            caminho_projeto: Caminho para a pasta do projeto (que contém o .pbip)
        """
        self.caminho_projeto = Path(caminho_projeto)
        self.nome_projeto = None
        self.info_modelo = InfoModelo()
        self.tabelas: List[InfoTabela] = []
        self.relacionamentos: List[InfoRelacionamento] = []
        self.paginas: List[InfoPagina] = []
        self.info_report = {}
        self.total_visuais = 0
        self.visuais_personalizados = []
        self.recursos_imagem = []
        
        # Layout do projeto: 'novo' (Model/, Report/) ou 'antigo' ({nome}.SemanticModel/definition/)
        self.layout = None
        
        # Encontra o projeto e detecta o layout
        self._encontrar_pbip()
    
    def _encontrar_pbip(self):
        """Encontra o projeto Power BI na pasta e detecta o layout"""
        
        # === Layout NOVO: pasta Model/ diretamente na raiz ===
        pasta_model = self.caminho_projeto / "Model"
        if pasta_model.is_dir():
            self.layout = 'novo'
            # Nome do projeto: arquivo .pbip, nome da pasta, ou stem da pasta
            arquivos_pbip = [p for p in self.caminho_projeto.glob("*.pbip") if p.is_file()]
            if arquivos_pbip:
                self.nome_projeto = arquivos_pbip[0].stem
            else:
                # Usa o nome da pasta (remove .pbip do nome se existir)
                nome_pasta = self.caminho_projeto.name
                if nome_pasta.lower().endswith('.pbip'):
                    self.nome_projeto = self.caminho_projeto.stem
                else:
                    self.nome_projeto = nome_pasta
            print(f"[OK] Projeto encontrado (layout novo): {self.nome_projeto}")
            return
        
        # === Layout ANTIGO: {nome}.SemanticModel/definition/ ===
        self.layout = 'antigo'
        
        # Padrão 1: Arquivo .pbip dentro da pasta
        arquivos_pbip = [p for p in self.caminho_projeto.glob("*.pbip") if p.is_file()]
        if arquivos_pbip:
            self.nome_projeto = arquivos_pbip[0].stem
            print(f"[OK] Projeto encontrado: {self.nome_projeto}")
            return
        
        # Padrão 2: Detecta pelo subdiretório *.SemanticModel
        semantic_dirs = list(self.caminho_projeto.glob("*.SemanticModel"))
        if semantic_dirs:
            self.nome_projeto = semantic_dirs[0].name.replace(".SemanticModel", "")
            print(f"[OK] Projeto encontrado (via SemanticModel): {self.nome_projeto}")
            return
        
        # Padrão 3: O nome da própria pasta termina com .pbip
        if self.caminho_projeto.suffix.lower() == '.pbip':
            nome_base = self.caminho_projeto.stem
            semantic_check = self.caminho_projeto / f"{nome_base}.SemanticModel"
            if semantic_check.exists():
                self.nome_projeto = nome_base
                print(f"[OK] Projeto encontrado (pasta .pbip): {self.nome_projeto}")
                return
            for item in self.caminho_projeto.iterdir():
                if item.is_dir() and item.name.endswith(".SemanticModel"):
                    self.nome_projeto = item.name.replace(".SemanticModel", "")
                    print(f"[OK] Projeto encontrado (pasta .pbip, SemanticModel): {self.nome_projeto}")
                    return
        
        raise FileNotFoundError(
            f"Nenhum projeto Power BI encontrado em {self.caminho_projeto}\n"
            f"Verifique se a pasta contém Model/ ou {'{nome}'}.SemanticModel/"
        )
    
    def _deve_filtrar_tabela(self, nome_tabela: str) -> bool:
        """Verifica se a tabela deve ser filtrada (tabelas técnicas)"""
        padroes_filtro = [
            r'^LocalDateTable_',
            r'^DateTableTemplate_',
        ]
        
        for padrao in padroes_filtro:
            if re.match(padrao, nome_tabela):
                return True
        
        return False
    
    def extrair_informacoes(self):
        """Extrai todas as informações do projeto"""
        print("\nExtraindo informações do modelo semântico...")
        self._extrair_modelo()
        
        print("Extraindo tabelas...")
        self._extrair_tabelas()
        
        print("Extraindo relacionamentos...")
        self._extrair_relacionamentos()
        
        print("Extraindo páginas do relatório...")
        self._extrair_paginas()
        
        print("Extraindo informações do relatório...")
        self._extrair_info_report()
        
        # Totaliza visuais a partir das páginas processadas
        self.total_visuais = sum(len(p.visuais) for p in self.paginas)
        
        print("[OK] Extração concluída!\n")
    
    def _obter_pasta_modelo(self) -> Path:
        """Retorna o caminho da pasta do modelo conforme o layout"""
        if self.layout == 'novo':
            return self.caminho_projeto / "Model"
        else:
            return self.caminho_projeto / f"{self.nome_projeto}.SemanticModel" / "definition"
    
    def _obter_pasta_report(self) -> Path:
        """Retorna o caminho da pasta do relatório conforme o layout"""
        if self.layout == 'novo':
            return self.caminho_projeto / "Report"
        else:
            return self.caminho_projeto / f"{self.nome_projeto}.Report" / "definition"
    
    def _extrair_modelo(self):
        """Extrai informações do modelo"""
        caminho_model = self._obter_pasta_modelo() / "model.tmdl"
        self.info_modelo = parse_tmdl_model(str(caminho_model))
    
    def _extrair_tabelas(self):
        """Extrai informações de todas as tabelas"""
        try:
            pasta_tables = self._obter_pasta_modelo() / "tables"
            
            if not pasta_tables.exists():
                print("  [AVISO] Pasta de tabelas não encontrada")
                return
            
            arquivos_tmdl = list(pasta_tables.glob("*.tmdl"))
            print(f"  Encontradas {len(arquivos_tmdl)} tabelas")
            
            for arquivo in arquivos_tmdl:
                try:
                    tabela = parse_tmdl_table(str(arquivo))
                    
                    if tabela:
                        # Filtra tabelas técnicas
                        if self._deve_filtrar_tabela(tabela.nome):
                            print(f"  [X] Ignorando tabela técnica: {tabela.nome}")
                            continue
                        
                        self.tabelas.append(tabela)
                        print(f"  [OK] {tabela.nome} ({len(tabela.colunas)} colunas, {len(tabela.medidas)} medidas)")
                except Exception as e:
                    print(f"  [AVISO] Erro ao processar {arquivo.name}: {e}")
                    continue
        except Exception as e:
            print(f"  [ERRO] Falha ao extrair tabelas: {e}")
    
    def _extrair_relacionamentos(self):
        """Extrai relacionamentos entre tabelas"""
        try:
            caminho_rel = self._obter_pasta_modelo() / "relationships.tmdl"
            self.relacionamentos = parse_tmdl_relationships(str(caminho_rel))
            print(f"  Encontrados {len(self.relacionamentos)} relacionamentos")
        except Exception as e:
            print(f"  [AVISO] Erro ao extrair relacionamentos: {e}")
            self.relacionamentos = []
    
    def _extrair_paginas(self):
        """Extrai informações das páginas do relatório"""
        try:
            pasta_report = self._obter_pasta_report()
            
            if self.layout == 'novo':
                # Layout novo: Report/sections/*/section.json
                pasta_sections = pasta_report / "sections"
                if not pasta_sections.exists():
                    print("  [AVISO] Pasta de seções não encontrada")
                    return
                
                for secao_dir in sorted(pasta_sections.iterdir()):
                    if not secao_dir.is_dir():
                        continue
                    try:
                        caminho_section = secao_dir / "section.json"
                        section_data = parse_json(str(caminho_section))
                        
                        if section_data:
                            # displayOption pode ser int (0, 1) ou string
                            display_opt = section_data.get('displayOption', 'FitToPage')
                            if isinstance(display_opt, int):
                                display_opt = {0: 'FitToPage', 1: 'FitToPage', 2: 'FitToWidth'}.get(display_opt, str(display_opt))
                            
                            pagina = InfoPagina(
                                id=section_data.get('name', secao_dir.name),
                                nome_exibicao=section_data.get('displayName', secao_dir.name),
                                largura=section_data.get('width', 1280),
                                altura=section_data.get('height', 720),
                                opcao_exibicao=display_opt,
                                tipo='Drillthrough' if section_data.get('pageBinding') else 'Normal',
                                filtros=section_data.get('filterConfig', {}).get('filters') if section_data.get('filterConfig') else None
                            )
                            
                            # Extrair visuais desta página
                            self._extrair_visuais_pagina(pagina, secao_dir)
                            
                            self.paginas.append(pagina)
                            print(f"  [OK] {pagina.nome_exibicao} ({pagina.tipo}) - {len(pagina.visuais)} visuais")
                    except Exception as e:
                        print(f"  [AVISO] Erro ao processar seção {secao_dir.name}: {e}")
                        continue
            else:
                # Layout antigo: {nome}.Report/definition/pages/pages.json
                pasta_pages = pasta_report / "pages"
                if not pasta_pages.exists():
                    print("  [AVISO] Pasta de páginas não encontrada")
                    return
                
                caminho_pages_json = pasta_pages / "pages.json"
                pages_data = parse_json(str(caminho_pages_json))
                page_order = pages_data.get('pageOrder', [])
                
                for page_id in page_order:
                    try:
                        pasta_pagina = pasta_pages / page_id
                        caminho_page_json = pasta_pagina / "page.json"
                        page_data = parse_json(str(caminho_page_json))
                        
                        if page_data:
                            pagina = InfoPagina(
                                id=page_id,
                                nome_exibicao=page_data.get('displayName', page_id),
                                largura=page_data.get('width', 1280),
                                altura=page_data.get('height', 720),
                                opcao_exibicao=page_data.get('displayOption', 'FitToPage'),
                                tipo='Drillthrough' if page_data.get('pageBinding') else 'Normal',
                                filtros=page_data.get('filterConfig', {}).get('filters') if page_data.get('filterConfig') else None
                            )
                            
                            # Extrair visuais desta página
                            self._extrair_visuais_pagina(pagina, pasta_pagina)
                            
                            self.paginas.append(pagina)
                            print(f"  [OK] {pagina.nome_exibicao} ({pagina.tipo}) - {len(pagina.visuais)} visuais")
                    except Exception as e:
                        print(f"  [AVISO] Erro ao processar página {page_id}: {e}")
                        continue
        except Exception as e:
            print(f"  [AVISO] Erro ao extrair páginas: {e}")
    
    def _extrair_visuais_pagina(self, pagina: InfoPagina, diretorio_pagina: Path):
        """Extrai detalhes dos visuais de uma página"""
        pasta_visuais = diretorio_pagina / "visualContainers"
        if not pasta_visuais.exists():
            return
        
        for visual_dir in pasta_visuais.iterdir():
            if not visual_dir.is_dir():
                continue
            
            caminho_config = visual_dir / "config.json"
            if not caminho_config.exists():
                continue
            
            try:
                config = parse_json(str(caminho_config))
                if not config:
                    continue
                
                # Tipo do visual
                tipo_visual = "Unknown"
                if 'singleVisual' in config:
                    tipo_visual = config['singleVisual'].get('visualType', 'Unknown')
                elif 'visualGroup' in config:
                    tipo_visual = 'Group'
                
                # Título do visual
                titulo = None
                
                # Tenta extrair título de vcObjects (comum)
                vc_objects = config.get('singleVisual', {}).get('vcObjects', {})
                if not vc_objects:
                    # Tenta no nível layout/config (ás vezes acontece)
                    vc_objects = config.get('vcObjects', {})

                if vc_objects:
                    title_obj = vc_objects.get('title', [])
                    if title_obj and isinstance(title_obj, list):
                        props = title_obj[0].get('properties', {})
                        text_prop = props.get('text', {})
                        # Estrutura complexa: text -> expr -> Literal -> Value
                        try:
                            titulo = text_prop.get('expr', {}).get('Literal', {}).get('Value', None)
                        except:
                            pass
                
                # Se não achou, tenta em objects.general
                if not titulo:
                    objects = config.get('singleVisual', {}).get('objects', {})
                    general = objects.get('general', [])
                    if general and isinstance(general, list):
                        try:
                            # A estrutura pode variar muito aqui, é uma tentativa genérica
                            props = general[0].get('properties', {})
                            titulo = props.get('title', None)
                        except:
                            pass
                
                # Limpa o título (remove aspas e sufixo D/L se houver)
                if titulo:
                    titulo = titulo.strip("'\"")
                    if titulo.endswith('D') or titulo.endswith('L'): # Sufixos comuns em expressões literals
                         # Verifica se é só sufixo numérico/literal ou parte do texto
                         # Na verdade, literais de string em JSON do PBI geralmente são "'Texto'"
                         # Se for expression, pode ter sufixo. Vamos assumir que se veio de Literal.Value é string pura ou com aspas
                         pass
                
                pagina.visuais.append(InfoVisual(
                    tipo=tipo_visual,
                    titulo=titulo if titulo else "-",
                    nome=visual_dir.name
                ))
            except Exception as e:
                # Ignora visual se der erro no parse, mas loga
                # print(f"Erro visual {visual_dir.name}: {e}")
                pass

    def _extrair_info_report(self):
        """Extrai informações do relatório"""
        try:
            caminho_report = self._obter_pasta_report() / "report.json"
            self.info_report = parse_json(str(caminho_report))
            
            # Extrai visuais personalizados (com segurança)
            if self.info_report:
                self.visuais_personalizados = self.info_report.get('publicCustomVisuals', [])
                
                # Extrai recursos de imagem
                resource_packages = self.info_report.get('resourcePackages', [])
                if isinstance(resource_packages, list):
                    for package in resource_packages:
                        # Layout novo: items dentro de resourcePackage
                        # Layout antigo: items direto no package
                        inner = package.get('resourcePackage', package)
                        items = inner.get('items', [])
                        if isinstance(items, list):
                            for item in items:
                                item_type = item.get('type', '')
                                # type pode ser string 'Image' ou int 100
                                if item_type == 'Image' or item_type == 100:
                                    self.recursos_imagem.append({
                                        'nome': item.get('name', 'sem_nome'),
                                        'tipo': 'Image'
                                    })
        except Exception as e:
            print(f"  [AVISO] Erro ao extrair informações do relatório: {e}")
    
    def _formatar_codigo_fonte(self, codigo: str) -> str:
        """Formata código fonte para melhor legibilidade"""
        if not codigo:
            return codigo
        # Substitui #(lf) por quebras de linha reais
        codigo = codigo.replace('#(lf)', '\n')
        # Remove indentação excessiva inicial
        linhas = codigo.split('\n')
        if linhas:
            # Encontra indentação mínima (ignorando linhas vazias)
            min_indent = float('inf')
            for linha in linhas:
                if linha.strip():
                    espacos = len(linha) - len(linha.lstrip())
                    min_indent = min(min_indent, espacos)
            
            if min_indent < float('inf') and min_indent > 0:
                linhas = [linha[min_indent:] if len(linha) >= min_indent else linha for linha in linhas]
            
            codigo = '\n'.join(linhas)
        return codigo.strip()
    
    def gerar_documentacao(self) -> str:
        """
        Gera a documentação em Markdown
        
        Returns:
            String com o conteúdo Markdown
        """
        md = []
        
        # Contadores para estatísticas
        total_colunas = sum(len(t.colunas) for t in self.tabelas)
        total_medidas = sum(len(t.medidas) for t in self.tabelas)
        total_calc = sum(len(t.colunas_calculadas) for t in self.tabelas)
        
        # ========================================================================
        # CABEÇALHO PRINCIPAL
        # ========================================================================
        md.append(f"# 📊 Documentação do Modelo Power BI")
        md.append(f"")
        md.append(f"> **Projeto**: `{self.nome_projeto}`")
        md.append(f"> ")
        md.append(f"> **Gerado em**: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        md.append(f"")
        md.append(f"---")
        md.append(f"")
        
        # ========================================================================
        # CARDS DE ESTATÍSTICAS
        # ========================================================================
        md.append(f"## 📈 Visão Geral")
        md.append(f"")
        md.append(f"| 📁 Tabelas | 📐 Medidas | 🔢 Colunas | 🧮 Calculadas | 🔗 Relacionamentos | 📄 Páginas | 📊 Visuais |")
        md.append(f"|:----------:|:----------:|:----------:|:-------------:|:-----------------:|:----------:|:----------:|")
        md.append(f"| **{len(self.tabelas)}** | **{total_medidas}** | **{total_colunas}** | **{total_calc}** | **{len(self.relacionamentos)}** | **{len(self.paginas)}** | **{self.total_visuais}** |")
        md.append(f"")
        md.append(f"---")
        md.append(f"")
        
        # ========================================================================
        # ÍNDICE (Table of Contents)
        # ========================================================================
        md.append(f"## 📑 Índice")
        md.append(f"")
        md.append(f"1. [Visão Geral](#-visão-geral)")
        md.append(f"2. [Modelo de Dados](#-modelo-de-dados)")
        md.append(f"3. [Resumo das Tabelas](#-resumo-das-tabelas)")
        md.append(f"4. [Detalhamento das Tabelas](#-detalhamento-das-tabelas)")
        
        # Lista de tabelas no índice
        for idx, tabela in enumerate(self.tabelas, 1):
            nome_safe = tabela.nome.lower().replace(' ', '-').replace('_', '-')
            md.append(f"   - {idx}. [{tabela.nome}](#{idx}-{nome_safe})")
        
        md.append(f"5. [Relacionamentos](#-relacionamentos)")
        md.append(f"6. [Páginas do Relatório](#-páginas-do-relatório)")
        
        if self.visuais_personalizados:
            md.append(f"7. [Visuais Personalizados](#-visuais-personalizados)")
        
        md.append(f"8. [Detalhamento dos Visuais](#-detalhamento-dos-visuais)")
        md.append(f"9. [Recursos de Imagem](#-recursos-de-imagem)")
        
        md.append(f"")
        md.append(f"---")
        md.append(f"")
        
        # ========================================================================
        # MODELO DE DADOS
        # ========================================================================
        md.append(f"## 🗂️ Modelo de Dados")
        md.append(f"")

        
        # Diagrama de Relacionamentos (Mermaid)
        if self.tabelas or self.relacionamentos:
            md.append(f"### Diagrama de Relacionamentos (ER)")
            md.append(f"")
            md.append(f"```mermaid")
            md.append(f"erDiagram")
            
            # Função auxiliar para limpar nomes e evitar erros de sintaxe no Mermaid
            def limpar_nome_mermaid(nome: str) -> str:
                # Substitui qualquer caractere que não seja letra, número ou underscore por _
                resultado = re.sub(r'[^a-zA-Z0-9_]', '_', str(nome))
                # Mermaid não aceita nomes que começam com número
                if resultado and resultado[0].isdigit():
                    resultado = "T_" + resultado
                return resultado

            # Adiciona definição das tabelas e colunas no diagrama
            for tabela in self.tabelas:
                # Omitir tabelas de calendário automáticas
                if 'LocalDateTable' in tabela.nome or 'DateTableTemplate' in tabela.nome:
                    continue
                nome_tab = limpar_nome_mermaid(tabela.nome)
                md.append(f"    {nome_tab} {{")
                # Limite de colunas para o diagrama não ficar gigantesco (Top 10)
                for col in tabela.colunas[:10]:
                    tipo = limpar_nome_mermaid(col.tipo_dado or "string")
                    nome_col = limpar_nome_mermaid(col.nome)
                    md.append(f"        {tipo} {nome_col}")
                if len(tabela.colunas) > 10:
                    md.append(f"        string outras_colunas_ocultas")
                md.append(f"    }}")
            
            # Adiciona as ligações (relacionamentos)
            for rel in self.relacionamentos:
                if 'LocalDateTable' in rel.tabela_destino or 'DateTableTemplate' in rel.tabela_destino:
                    continue
                tabela_origem = limpar_nome_mermaid(rel.tabela_origem)
                tabela_destino = limpar_nome_mermaid(rel.tabela_destino)
                coluna_origem = rel.coluna_origem.replace("'", "")
                
                # }|--|| = muitos-para-um (bidirecional)  |  }o--|| = muitos-para-um (unidirecional)
                tipo_rel = "}|--||" if rel.filtro_bidirecional else "}o--||"
                md.append("    " + tabela_origem + " " + tipo_rel + " " + tabela_destino + ' : "' + coluna_origem + '"')
            
            md.append("```")
            md.append("")
            md.append("*Legenda: `}|--||` = Filtro Bidirecional | `}o--||` = Filtro Único*")
            md.append("")
        # Relacionamentos (Tabela)
        if self.relacionamentos:
            md.append(f"")
            md.append(f"### 🔗 Lista de Relacionamentos")
            md.append(f"")
            md.append(f"*Total: {len(self.relacionamentos)} relacionamentos*")
            md.append(f"")
            md.append(f"| Origem | → | Destino | Bidirecional | Ativo |")
            md.append(f"|--------|---|---------|--------------|-------|")
            
            for rel in self.relacionamentos:
                origem = f"{rel.tabela_origem}.{rel.coluna_origem}"
                destino = f"{rel.tabela_destino}.{rel.coluna_destino}"
                bidirecional = "Sim" if rel.filtro_bidirecional else "Não"
                ativo = "Sim" if rel.esta_ativo else "Não"
                md.append(f"| {origem} | → | {destino} | {bidirecional} | {ativo} |")
            
            md.append(f"")
        
        # Grupos de Consulta
        if self.info_modelo.grupos_consulta:
            md.append(f"### Grupos de Consulta")
            md.append(f"")
            md.append(f"| Nome | Ordem |")
            md.append(f"|:-----|:-----:|")
            
            for grupo in sorted(self.info_modelo.grupos_consulta, key=lambda x: x['ordem']):
                md.append(f"| {grupo['nome']} | {grupo['ordem']} |")
            
            md.append(f"")
        
        md.append(f"---")
        md.append(f"")
        # ========================================================================
        # RESUMO DAS TABELAS
        # ========================================================================
        md.append(f"---")
        md.append(f"")
        md.append(f"## 📊 Resumo das Tabelas")
        md.append(f"")
        md.append(f"*Visão geral de {len(self.tabelas)} tabelas no modelo*")
        md.append(f"")
        md.append(f"| # | Tabela | Colunas | Medidas | Colunas Calc. | Fonte |")
        md.append(f"|---|--------|---------|---------|---------------|-------|")
        
        for idx, tabela in enumerate(self.tabelas, 1):
            num_colunas = len(tabela.colunas)
            num_medidas = len(tabela.medidas)
            num_calc = len(tabela.colunas_calculadas)
            fonte = "DAX" if tabela.particao and "DAX" in tabela.particao.codigo_fonte.upper() else "Importação"
            if tabela.particao and tabela.particao.grupo_consulta:
                fonte = tabela.particao.grupo_consulta
            md.append(f"| {idx} | **{tabela.nome}** | {num_colunas} | {num_medidas} | {num_calc} | {fonte} |")
        
        md.append(f"")
        
        # Totais
        total_colunas = sum(len(t.colunas) for t in self.tabelas)
        total_medidas = sum(len(t.medidas) for t in self.tabelas)
        total_calc = sum(len(t.colunas_calculadas) for t in self.tabelas)
        md.append(f"**Totais**: {total_colunas} colunas | {total_medidas} medidas | {total_calc} colunas calculadas")
        md.append(f"")
        
        # Tabelas
        if self.tabelas:
            md.append(f"---")
            md.append(f"")
            md.append(f"## 📁 Tabelas do Modelo")
            md.append(f"")
            md.append(f"*Total de tabelas documentadas: {len(self.tabelas)}*")
            md.append(f"")
        else:
            md.append(f"---")
            md.append(f"")
            md.append(f"## Tabelas")
            md.append(f"")
            md.append(f"*Nenhuma tabela encontrada no projeto.*")
            md.append(f"")
        
        for idx, tabela in enumerate(self.tabelas, 1):
            # Separador entre tabelas (exceto antes da primeira)
            if idx > 1:
                md.append(f"---")
                md.append(f"")
            
            md.append(f"### {idx}. {tabela.nome}")
            md.append(f"")
            
            # Card de metadados com badges
            status_badge = "🔴 Oculta" if tabela.esta_oculta else "🟢 Visível"
            refresh_badge = "❌ Não" if tabela.excluida_refresh else "✅ Sim"
            
            # Determina tipo de fonte
            fonte_tipo = "📥 Importação"
            if tabela.particao:
                if tabela.particao.grupo_consulta:
                    fonte_tipo = f"🗃️ {tabela.particao.grupo_consulta}"
                elif "DAX" in tabela.particao.codigo_fonte.upper()[:50] if tabela.particao.codigo_fonte else False:
                    fonte_tipo = "📝 DAX"
                elif "Oracle" in tabela.particao.codigo_fonte if tabela.particao.codigo_fonte else False:
                    fonte_tipo = "🔷 Oracle"
            
            md.append(f"| Status | Atualização | Colunas | Medidas | Fonte |")
            md.append(f"|:------:|:-----------:|:-------:|:-------:|:-----:|")
            md.append(f"| {status_badge} | {refresh_badge} | {len(tabela.colunas)} | {len(tabela.medidas)} | {fonte_tipo} |")
            md.append(f"")
            
            # Colunas
            if tabela.colunas:
                md.append(f"#### 📋 Colunas")
                md.append(f"")
                md.append(f"| Nome | Tipo | Sumarização | Oculta |")
                md.append(f"|:-----|:----:|:-----------:|:------:|")
                
                for coluna in tabela.colunas:
                    oculta = "🔴" if coluna.esta_oculta else "⚪"
                    md.append(f"| `{coluna.nome}` | `{coluna.tipo_dado}` | {coluna.sumarizacao} | {oculta} |")
                
                md.append(f"")
            
            # Colunas Calculadas - Resumo
            if tabela.colunas_calculadas:
                md.append(f"#### Colunas Calculadas (Resumo)")
                md.append(f"")
                md.append(f"| Nome | Tipo | Formato |")
                md.append(f"|------|------|---------|")
                
                for coluna in tabela.colunas_calculadas:
                    tipo = coluna.tipo_dado or "string"
                    formato = coluna.formato or "-"
                    md.append(f"| {coluna.nome} | {tipo} | {formato} |")
                
                md.append(f"")
                
                # Colunas Calculadas - Código DAX Completo
                md.append(f"#### Colunas Calculadas - Código DAX")
                md.append(f"")
                
                for coluna in tabela.colunas_calculadas:
                    md.append(f"##### {coluna.nome}")
                    md.append(f"")
                    info_parts = []
                    if coluna.tipo_dado:
                        info_parts.append(f"**Tipo**: `{coluna.tipo_dado}`")
                    if coluna.formato:
                        info_parts.append(f"**Formato**: `{coluna.formato}`")
                    if info_parts:
                        md.append(" | ".join(info_parts))
                        md.append(f"")
                    md.append(f"```dax")
                    # Verifica se a expressão DAX está vazia ou None
                    if coluna.expressao_dax and str(coluna.expressao_dax).strip():
                        md.append(str(coluna.expressao_dax).strip())
                    else:
                        md.append("// [AVISO] Expressão DAX não capturada durante o parsing")
                    md.append(f"```")
                    md.append(f"")
                
                md.append(f"")
            
            # Medidas - Resumo
            if tabela.medidas:
                md.append(f"#### Medidas (Resumo)")
                md.append(f"")
                md.append(f"| Nome | Formato |")
                md.append(f"|------|---------|")
                
                for medida in tabela.medidas:
                    formato = medida.formato or "-"
                    md.append(f"| {medida.nome} | {formato} |")
                
                md.append(f"")
                
                # Medidas - Código DAX Completo
                md.append(f"#### Medidas - Código DAX")
                md.append(f"")
                
                for medida in tabela.medidas:
                    md.append(f"##### {medida.nome}")
                    md.append(f"")
                    if medida.formato:
                        md.append(f"**Formato**: `{medida.formato}`")
                        md.append(f"")
                    md.append(f"```dax")
                    # Verifica se a expressão DAX está vazia ou None
                    if medida.expressao_dax and str(medida.expressao_dax).strip():
                        md.append(str(medida.expressao_dax).strip())
                    else:
                        md.append("// [AVISO] Expressão DAX não capturada durante o parsing")
                    md.append(f"```")
                    md.append(f"")
                
                md.append(f"")
            
            # Hierarquias
            if tabela.hierarquias:
                md.append(f"#### 🔀 Hierarquias")
                md.append(f"")
                for hier in tabela.hierarquias:
                    niveis_str = " → ".join(hier.niveis)
                    md.append(f"- **{hier.nome}**: {niveis_str}")
                md.append(f"")
            
            # Fonte de Dados
            if tabela.particao and tabela.particao.codigo_fonte:
                md.append(f"#### 💾 Fonte de Dados")
                md.append(f"")
                
                # Badges para modo e grupo
                modo_badge = f"`{tabela.particao.modo}`"
                grupo_badge = f"`{tabela.particao.grupo_consulta}`" if tabela.particao.grupo_consulta else ""
                
                if grupo_badge:
                    md.append(f"**Modo**: {modo_badge} | **Grupo**: {grupo_badge}")
                else:
                    md.append(f"**Modo**: {modo_badge}")
                md.append(f"")
                
                # Código fonte formatado
                codigo_formatado = self._formatar_codigo_fonte(tabela.particao.codigo_fonte)
                md.append(f"```powerquery")
                md.append(codigo_formatado)
                md.append(f"```")
                md.append(f"")
        
        # Páginas do Relatório (sempre exibe, mesmo quando 0)
        md.append(f"---")
        md.append(f"")
        md.append(f"## 📄 Páginas do Relatório")
        md.append(f"")
        md.append(f"**Total de páginas: {len(self.paginas)}**")
        md.append(f"")
        if self.paginas:
            md.append(f"| # | Nome | Tipo | Dimensões |")
            md.append(f"|---|------|------|-----------|")
            
            for i, pagina in enumerate(self.paginas, 1):
                dimensoes = f"{pagina.largura} x {pagina.altura}"
                md.append(f"| {i} | {pagina.nome_exibicao} | {pagina.tipo} | {dimensoes} |")
            
            md.append(f"")
        else:
            md.append(f"> ⚠️ Nenhuma página encontrada localmente. Este projeto pode ser um **relatório remoto** (thin report) onde as páginas ficam armazenadas no serviço Power BI.")            
            md.append(f"")
        
        # Detalhamento dos Visuais (Página a Página)
        md.append(f"---")
        md.append(f"")
        md.append(f"## 🎨 Detalhamento dos Visuais")
        md.append(f"")
        md.append(f"*Lista de visuais por página do relatório*")
        md.append(f"")
        
        for pagina in self.paginas:
            md.append(f"### {pagina.nome_exibicao}")
            md.append(f"")
            if pagina.visuais:
                md.append(f"| Tipo | Título |")
                md.append(f"|------|--------|")
                for visual in pagina.visuais:
                    md.append(f"| `{visual.tipo}` | {visual.titulo} |")
            else:
                md.append(f"*Nenhum visual detectado nesta página.*")
            md.append(f"")
        
        # Visuais Personalizados
        if self.visuais_personalizados:
            md.append(f"---")
            md.append(f"")
            md.append(f"## Visuais Personalizados")
            md.append(f"")
            md.append(f"| ID do Visual |")
            md.append(f"|--------------|")
            
            for visual in self.visuais_personalizados:
                md.append(f"| {visual} |")
            
            md.append(f"")
        
        # Recursos de Imagem
        if self.recursos_imagem:
            md.append(f"---")
            md.append(f"")
            md.append(f"## Recursos de Imagem")
            md.append(f"")
            md.append(f"| Nome | Tipo |")
            md.append(f"|------|------|")
            
            for recurso in self.recursos_imagem:
                md.append(f"| {recurso['nome']} | {recurso['tipo']} |")
            
            md.append(f"")
        
        return '\n'.join(md)
    
    def salvar_documentacao(self, caminho_saida: Optional[str] = None):
        """
        Salva a documentação em arquivo
        
        Args:
            caminho_saida: Caminho para salvar. Se None, salva na pasta do projeto
        """
        if caminho_saida is None:
            caminho_saida = self.caminho_projeto / f"{self.nome_projeto}_documentacao.md"
        
        markdown = self.gerar_documentacao()
        
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"[OK] Documentação MD salva em: {caminho_saida}")
        return caminho_saida
    
    def salvar_documentacao_docx(self, caminho_saida: Optional[str] = None):
        """
        Salva a documentação em formato Word (.docx) com formatação profissional
        
        Args:
            caminho_saida: Caminho para salvar. Se None, salva na pasta do projeto
        """
        try:
            from docx import Document
            from docx.shared import Inches, Pt, Cm, RGBColor, Emu
            from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
            from docx.enum.table import WD_TABLE_ALIGNMENT
            from docx.enum.section import WD_ORIENT
            from docx.oxml.ns import qn, nsdecls
            from docx.oxml import parse_xml
        except ImportError:
            print("[ERRO] Pacote 'python-docx' não instalado. Execute: pip install python-docx")
            return None
        
        if caminho_saida is None:
            caminho_saida = self.caminho_projeto / f"{self.nome_projeto}_documentacao.docx"
        
        doc = Document()
        
        # ====================================================================
        # CORES E CONSTANTES
        # ====================================================================
        AZUL_PRI = RGBColor(0x00, 0x3D, 0x6B)    # Azul escuro primário
        AZUL_SEC = RGBColor(0x00, 0x6D, 0xAA)    # Azul médio
        AZUL_CLR = RGBColor(0xD6, 0xE8, 0xF5)    # Azul claro fundo
        CINZA_TX = RGBColor(0x44, 0x44, 0x44)     # Texto principal
        CINZA_LT = RGBColor(0x77, 0x77, 0x77)     # Texto secundário
        BRANCO   = RGBColor(0xFF, 0xFF, 0xFF)
        
        HEX_AZUL_PRI = "003D6B"
        HEX_AZUL_SEC = "006DAA"
        HEX_AZUL_CLR = "D6E8F5"
        HEX_CINZA_BG = "F7F8FA"
        HEX_CODE_BG  = "F0F2F5"
        HEX_CODE_BRD = "006DAA"
        
        # ====================================================================
        # CONFIGURAÇÃO DA PÁGINA
        # ====================================================================
        section = doc.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)
        
        # ====================================================================
        # ESTILOS GLOBAIS
        # ====================================================================
        style_normal = doc.styles['Normal']
        style_normal.font.name = 'Calibri'
        style_normal.font.size = Pt(10)
        style_normal.font.color.rgb = CINZA_TX
        style_normal.paragraph_format.space_after = Pt(4)
        style_normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        
        # Estilos de heading
        for lvl in range(1, 5):
            style_h = doc.styles[f'Heading {lvl}']
            style_h.font.name = 'Calibri'
            style_h.font.color.rgb = AZUL_PRI
            style_h.font.bold = True
            if lvl == 1:
                style_h.font.size = Pt(18)
                style_h.paragraph_format.space_before = Pt(12)
                style_h.paragraph_format.space_after = Pt(6)
            elif lvl == 2:
                style_h.font.size = Pt(14)
                style_h.paragraph_format.space_before = Pt(10)
                style_h.paragraph_format.space_after = Pt(4)
            elif lvl == 3:
                style_h.font.size = Pt(12)
                style_h.font.color.rgb = AZUL_SEC
                style_h.paragraph_format.space_before = Pt(6)
                style_h.paragraph_format.space_after = Pt(2)
            else:
                style_h.font.size = Pt(11)
                style_h.font.color.rgb = AZUL_SEC
        
        # ====================================================================
        # FUNÇÕES AUXILIARES
        # ====================================================================
        def _add_separator():
            """Adiciona linha separadora sutil"""
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            # Borda inferior como separador
            pPr = p._p.get_or_add_pPr()
            pBdr = parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:bottom w:val="single" w:sz="4" w:space="1" w:color="{HEX_AZUL_CLR}"/>'
                f'</w:pBdr>'
            )
            pPr.append(pBdr)
            return p
        
        def _add_table(headers, rows, compact=False):
            """Cria tabela profissional com estilo refinado"""
            table = doc.add_table(rows=1 + len(rows), cols=len(headers))
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Remove bordas padrão e aplica estilo customizado
            tbl = table._tbl
            tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>') 
            # Bordas suaves da tabela
            borders = parse_xml(
                f'<w:tblBorders {nsdecls("w")}>'
                f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
                f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
                f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
                f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
                f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E5EB"/>'
                f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E0E5EB"/>'
                f'</w:tblBorders>'
            )
            tblPr.append(borders)
            
            font_size = Pt(8) if compact else Pt(9)
            
            # Cabeçalho
            for i, header in enumerate(headers):
                cell = table.rows[0].cells[i]
                cell.text = ''
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(header)
                run.bold = True
                run.font.size = font_size
                run.font.name = 'Calibri'
                run.font.color.rgb = BRANCO
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{HEX_AZUL_PRI}"/>')
                cell._tc.get_or_add_tcPr().append(shading)
            
            # Dados
            for r_idx, row_data in enumerate(rows):
                for c_idx, cell_text in enumerate(row_data):
                    cell = table.rows[r_idx + 1].cells[c_idx]
                    cell.text = ''
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    run = p.add_run(str(cell_text))
                    run.font.size = font_size
                    run.font.name = 'Calibri'
                    run.font.color.rgb = CINZA_TX
                    # Fundo alternado
                    if r_idx % 2 == 0:
                        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{HEX_CINZA_BG}"/>')
                        cell._tc.get_or_add_tcPr().append(shading)
            
            doc.add_paragraph("").paragraph_format.space_after = Pt(2)
            return table
        
        def _add_code_block(code, language=""):
            """Adiciona bloco de código com borda lateral azul e fundo cinza"""
            # Label da linguagem (se fornecida)
            if language:
                p_lang = doc.add_paragraph()
                p_lang.paragraph_format.space_after = Pt(0)
                p_lang.paragraph_format.space_before = Pt(6)
                run_lang = p_lang.add_run(f"  {language.upper()}")
                run_lang.font.size = Pt(7)
                run_lang.font.name = 'Calibri'
                run_lang.font.color.rgb = AZUL_SEC
                run_lang.bold = True
            
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2) if language else Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.left_indent = Cm(0.3)
            
            # Fundo cinza + borda lateral azul
            pPr = p._p.get_or_add_pPr()
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{HEX_CODE_BG}"/>')
            pPr.append(shading)
            pBdr = parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:left w:val="single" w:sz="18" w:space="6" w:color="{HEX_CODE_BRD}"/>'
                f'  <w:top w:val="single" w:sz="2" w:space="2" w:color="D0D5DD"/>'
                f'  <w:bottom w:val="single" w:sz="2" w:space="2" w:color="D0D5DD"/>'
                f'  <w:right w:val="single" w:sz="2" w:space="2" w:color="D0D5DD"/>'
                f'</w:pBdr>'
            )
            pPr.append(pBdr)
            
            run = p.add_run(code)
            run.font.name = 'Consolas'
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(0x1E, 0x1E, 0x2E)
            return p
        
        def _add_info_box(text, tipo="info"):
            """Adiciona caixa informativa colorida"""
            cores = {
                "info":    (HEX_AZUL_CLR, HEX_AZUL_SEC, AZUL_PRI),
                "warning": ("FFF3CD",      "FFC107",     RGBColor(0x85, 0x6D, 0x00)),
                "success": ("D4EDDA",      "28A745",     RGBColor(0x15, 0x57, 0x24)),
            }
            bg, brd, txt_cor = cores.get(tipo, cores["info"])
            
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.left_indent = Cm(0.5)
            
            pPr = p._p.get_or_add_pPr()
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{bg}"/>')
            pPr.append(shading)
            pBdr = parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:left w:val="single" w:sz="24" w:space="8" w:color="{brd}"/>'
                f'</w:pBdr>'
            )
            pPr.append(pBdr)
            
            run = p.add_run(text)
            run.font.size = Pt(9)
            run.font.name = 'Calibri'
            run.font.color.rgb = txt_cor
            return p
        
        def _add_stat_card(label, value, emoji=""):
            """Retorna lista [label, valor] para card de estatística"""
            return [f"{emoji} {label}" if emoji else label, str(value)]
        
        # ====================================================================
        # CONTADORES
        # ====================================================================
        total_colunas = sum(len(t.colunas) for t in self.tabelas)
        total_medidas = sum(len(t.medidas) for t in self.tabelas)
        total_calc = sum(len(t.colunas_calculadas) for t in self.tabelas)
        
        # ====================================================================
        # CAPA
        # ====================================================================
        # Espaçamento superior
        for _ in range(3):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
        
        # Barra decorativa superior
        p_barra = doc.add_paragraph()
        p_barra.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p_barra._p.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'  <w:top w:val="single" w:sz="48" w:space="1" w:color="{HEX_AZUL_PRI}"/>'
            f'</w:pBdr>'
        )
        pPr.append(pBdr)
        
        # Título único
        p_titulo = doc.add_paragraph()
        p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_titulo.paragraph_format.space_before = Pt(30)
        p_titulo.paragraph_format.space_after = Pt(10)
        run = p_titulo.add_run(f"Documentação do Projeto Power BI:")
        run.font.size = Pt(22)
        run.font.name = 'Calibri Light'
        run.font.color.rgb = AZUL_SEC
        
        # Nome do projeto
        p_proj = doc.add_paragraph()
        p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_proj.paragraph_format.space_after = Pt(10)
        run = p_proj.add_run(self.nome_projeto)
        run.font.size = Pt(28)
        run.font.name = 'Calibri'
        run.font.color.rgb = AZUL_PRI
        run.bold = True
        
        # Barra decorativa inferior
        p_barra2 = doc.add_paragraph()
        p_barra2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr2 = p_barra2._p.get_or_add_pPr()
        pBdr2 = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'  <w:bottom w:val="single" w:sz="24" w:space="1" w:color="{HEX_AZUL_SEC}"/>'
            f'</w:pBdr>'
        )
        pPr2.append(pBdr2)
        
        # Espaçamento
        doc.add_paragraph("").paragraph_format.space_after = Pt(30)
        
        # Estatísticas resumidas na capa
        info_capa = [
            ("Tabelas", str(len(self.tabelas))),
            ("Medidas DAX", str(total_medidas)),
            ("Colunas", str(total_colunas)),
            ("Relacionamentos", str(len(self.relacionamentos))),
        ]
        
        tbl_info = doc.add_table(rows=len(info_capa), cols=2)
        tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r_idx, (label, valor) in enumerate(info_capa):
            cell_l = tbl_info.rows[r_idx].cells[0]
            cell_l.text = ''
            p = cell_l.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = p.add_run(label + "  ")
            run.font.size = Pt(11)
            run.font.color.rgb = CINZA_LT
            run.font.name = 'Calibri'
            
            cell_v = tbl_info.rows[r_idx].cells[1]
            cell_v.text = ''
            p = cell_v.paragraphs[0]
            run = p.add_run("  " + valor)
            run.font.size = Pt(11)
            run.font.color.rgb = AZUL_PRI
            run.font.name = 'Calibri'
            run.bold = True
        
        # Quebra de página após capa
        doc.add_page_break()
        
        # ====================================================================
        # SUMÁRIO (Table of Contents) 
        # ====================================================================
        h_toc = doc.add_heading("Sumário", level=1)
        
        # Insere campo TOC do Word (atualizado ao abrir o documento)
        p_toc = doc.add_paragraph()
        run_toc = p_toc.add_run()
        fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        run_toc._r.append(fldChar1)
        run_toc2 = p_toc.add_run()
        instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText>')
        run_toc2._r.append(instrText)
        run_toc3 = p_toc.add_run()
        fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
        run_toc3._r.append(fldChar2)
        run_toc4 = p_toc.add_run("(Clique com botão direito e selecione \"Atualizar campo\" para gerar o sumário)")
        run_toc4.font.size = Pt(9)
        run_toc4.font.color.rgb = CINZA_LT
        run_toc4.italic = True
        run_toc5 = p_toc.add_run()
        fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run_toc5._r.append(fldChar3)
        
        doc.add_page_break()
        
        # ====================================================================
        # CABEÇALHO E RODAPÉ
        # ====================================================================
        header = section.header
        header.is_linked_to_previous = False
        p_header = header.paragraphs[0]
        p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        run_h = p_header.add_run(f"{self.nome_projeto}")
        run_h.font.size = Pt(8)
        run_h.font.color.rgb = CINZA_LT
        run_h.font.name = 'Calibri'
        p_header.add_run("  |  ").font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
        run_h2 = p_header.add_run("Documentação Power BI")
        run_h2.font.size = Pt(8)
        run_h2.font.color.rgb = AZUL_SEC
        run_h2.font.name = 'Calibri'
        
        # Borda inferior no cabeçalho
        pPr_h = p_header._p.get_or_add_pPr()
        pBdr_h = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'  <w:bottom w:val="single" w:sz="6" w:space="4" w:color="{HEX_AZUL_CLR}"/>'
            f'</w:pBdr>'
        )
        pPr_h.append(pBdr_h)
        
        # Rodapé com numeração
        footer = section.footer
        footer.is_linked_to_previous = False
        p_footer = footer.paragraphs[0]
        p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Borda superior no rodapé
        pPr_f = p_footer._p.get_or_add_pPr()
        pBdr_f = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'  <w:top w:val="single" w:sz="6" w:space="4" w:color="{HEX_AZUL_CLR}"/>'
            f'</w:pBdr>'
        )
        pPr_f.append(pBdr_f)
        
        run_f1 = p_footer.add_run("Página ")
        run_f1.font.size = Pt(8)
        run_f1.font.color.rgb = CINZA_LT
        run_f1.font.name = 'Calibri'
        
        # Campo de número de página
        fldChar_pg1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        run_pg = p_footer.add_run()
        run_pg._r.append(fldChar_pg1)
        instrPg = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
        run_pg2 = p_footer.add_run()
        run_pg2._r.append(instrPg)
        fldChar_pg2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run_pg3 = p_footer.add_run()
        run_pg3._r.append(fldChar_pg2)
        
        run_f2 = p_footer.add_run(" de ")
        run_f2.font.size = Pt(8)
        run_f2.font.color.rgb = CINZA_LT
        
        # Campo total de páginas
        fldChar_np1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        run_np = p_footer.add_run()
        run_np._r.append(fldChar_np1)
        instrNp = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> NUMPAGES </w:instrText>')
        run_np2 = p_footer.add_run()
        run_np2._r.append(instrNp)
        fldChar_np2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run_np3 = p_footer.add_run()
        run_np3._r.append(fldChar_np2)
        
        # ====================================================================
        # VISÃO GERAL
        # ====================================================================
        doc.add_heading("Visão Geral", level=1)
        
        # Cards de estatísticas em tabela 3x3 (ajustado para incluir visuais)
        stats_table = doc.add_table(rows=3, cols=3)
        stats_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        stats_data = [
            ("Tabelas", len(self.tabelas)),
            ("Medidas", total_medidas),
            ("Colunas", total_colunas),
            ("Calculadas", total_calc),
            ("Relacionamentos", len(self.relacionamentos)),
            ("Páginas", len(self.paginas)),
            ("Visuais", self.total_visuais),
        ]
        
        for idx, (label, value) in enumerate(stats_data):
            row = idx // 3
            col = idx % 3
            cell = stats_table.rows[row].cells[col]
            cell.text = ''
            
            # Fundo azul claro
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{HEX_AZUL_CLR}"/>')
            cell._tc.get_or_add_tcPr().append(shading)
            
            # Valor grande
            p_val = cell.paragraphs[0]
            p_val.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_val.paragraph_format.space_before = Pt(8)
            p_val.paragraph_format.space_after = Pt(2)
            run_val = p_val.add_run(str(value))
            run_val.font.size = Pt(22)
            run_val.font.name = 'Calibri Light'
            run_val.font.color.rgb = AZUL_PRI
            run_val.bold = True
            
            # Label abaixo
            p_lbl = cell.add_paragraph()
            p_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_lbl.paragraph_format.space_before = Pt(0)
            p_lbl.paragraph_format.space_after = Pt(8)
            run_lbl = p_lbl.add_run(label)
            run_lbl.font.size = Pt(9)
            run_lbl.font.name = 'Calibri'
            run_lbl.font.color.rgb = AZUL_SEC
        
        _add_separator()
        
        # ====================================================================
        # MODELO DE DADOS
        # ====================================================================
        doc.add_heading("Modelo de Dados", level=1)
        doc.add_heading("Configuração", level=2)
        
        config_data = [
            ["Cultura", self.info_modelo.cultura or "—"],
            ["Versão", self.info_modelo.versao_datasource or "—"],
            ["Tabelas", str(len(self.tabelas))],
            ["Relacionamentos", str(len(self.relacionamentos))],
        ]
        _add_table(["Propriedade", "Valor"], config_data)
        
        # Grupos de Consulta
        if self.info_modelo.grupos_consulta:
            doc.add_heading("Grupos de Consulta", level=2)
            rows_gq = [[g['nome'], str(g['ordem'])] for g in sorted(self.info_modelo.grupos_consulta, key=lambda x: x['ordem'])]
            _add_table(["Nome", "Ordem"], rows_gq)
        
        # ====================================================================
        # RESUMO DAS TABELAS
        # ====================================================================
        doc.add_page_break()
        doc.add_heading("Resumo das Tabelas", level=1)
        
        p = doc.add_paragraph()
        run = p.add_run(f"O modelo contém {len(self.tabelas)} tabelas com {total_colunas} colunas, "
                        f"{total_medidas} medidas e {total_calc} colunas calculadas.")
        run.italic = True
        run.font.color.rgb = CINZA_LT
        
        rows_resumo = []
        for idx, tabela in enumerate(self.tabelas, 1):
            fonte = "Importação"
            if tabela.particao:
                if tabela.particao.grupo_consulta:
                    fonte = tabela.particao.grupo_consulta
                elif tabela.particao.codigo_fonte and "DAX" in tabela.particao.codigo_fonte.upper()[:50]:
                    fonte = "DAX"
            rows_resumo.append([
                str(idx), tabela.nome,
                str(len(tabela.colunas)), str(len(tabela.medidas)),
                str(len(tabela.colunas_calculadas)), fonte
            ])
        
        _add_table(
            ["#", "Tabela", "Colunas", "Medidas", "Col. Calc.", "Fonte"],
            rows_resumo
        )
        
        _add_separator()
        
        # ====================================================================
        # DETALHAMENTO DAS TABELAS
        # ====================================================================
        doc.add_page_break()
        doc.add_heading("Detalhamento das Tabelas", level=1)
        
        for idx, tabela in enumerate(self.tabelas, 1):
            # Separador entre tabelas (exceto a primeira)
            if idx > 1:
                p_sep = doc.add_paragraph()
                p_sep.paragraph_format.space_before = Pt(12)
                p_sep.paragraph_format.space_after = Pt(12)
                run_sep = p_sep.add_run("─" * 40)
                run_sep.font.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)
                run_sep.font.size = Pt(8)
                p_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_heading(f"{idx}. {tabela.nome}", level=2)
            
            # Card de metadados
            status = "Visível" if not tabela.esta_oculta else "Oculta"
            refresh = "Sim" if not tabela.excluida_refresh else "Não"
            fonte_tipo = "Importação"
            if tabela.particao:
                if tabela.particao.grupo_consulta:
                    fonte_tipo = tabela.particao.grupo_consulta
                elif tabela.particao.codigo_fonte and "DAX" in tabela.particao.codigo_fonte.upper()[:50]:
                    fonte_tipo = "DAX"
            
            _add_table(
                ["Status", "Atualização", "Colunas", "Medidas", "Fonte"],
                [[status, refresh, str(len(tabela.colunas)), str(len(tabela.medidas)), fonte_tipo]]
            )
            
            # Colunas
            if tabela.colunas:
                h = doc.add_heading("Colunas", level=3)
                h.paragraph_format.space_before = Pt(8)
                rows_col = []
                for col in tabela.colunas:
                    oculta = "Sim" if col.esta_oculta else "Não"
                    rows_col.append([col.nome, col.tipo_dado, col.sumarizacao, oculta])
                _add_table(["Nome", "Tipo", "Sumarização", "Oculta"], rows_col, compact=True)
            
            # Colunas Calculadas
            if tabela.colunas_calculadas:
                h = doc.add_heading("Colunas Calculadas", level=3)
                h.paragraph_format.space_before = Pt(8)
                for coluna in tabela.colunas_calculadas:
                    p = doc.add_paragraph()
                    p.paragraph_format.space_after = Pt(2)
                    run = p.add_run(f"▸ {coluna.nome}")
                    run.bold = True
                    run.font.size = Pt(10)
                    run.font.color.rgb = AZUL_PRI
                    if coluna.tipo_dado:
                        p.add_run(f"  ({coluna.tipo_dado})").font.color.rgb = CINZA_LT
                    expr = coluna.expressao_dax.strip() if coluna.expressao_dax else "// Expressão não capturada"
                    _add_code_block(expr, "DAX")
            
            # Medidas
            if tabela.medidas:
                h = doc.add_heading("Medidas DAX", level=3)
                h.paragraph_format.space_before = Pt(8)
                
                # Tabela resumo
                rows_med = [[m.nome, m.formato or "—"] for m in tabela.medidas]
                _add_table(["Nome da Medida", "Formato de Exibição"], rows_med, compact=True)
                
                # Código de cada medida
                h_cod = doc.add_heading("Código das Medidas", level=4)
                h_cod.paragraph_format.space_before = Pt(6)
                
                for medida in tabela.medidas:
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(2)
                    run = p.add_run(f"▸ {medida.nome}")
                    run.bold = True
                    run.font.size = Pt(10)
                    run.font.color.rgb = AZUL_PRI
                    
                    if medida.formato:
                        r_l = p.add_run("  |  Fmt: ")
                        r_l.font.size = Pt(8)
                        r_l.font.color.rgb = CINZA_LT
                        r_v = p.add_run(medida.formato)
                        r_v.font.size = Pt(8)
                        r_v.font.name = 'Consolas'
                        r_v.font.color.rgb = CINZA_TX
                    
                    expr = medida.expressao_dax.strip() if medida.expressao_dax else "// Expressão não capturada"
                    _add_code_block(expr, "DAX")
            
            # Hierarquias
            if tabela.hierarquias:
                h = doc.add_heading("Hierarquias", level=3)
                h.paragraph_format.space_before = Pt(8)
                for hier in tabela.hierarquias:
                    niveis_str = " → ".join(hier.niveis)
                    p = doc.add_paragraph()
                    run = p.add_run(f"  {hier.nome}: ")
                    run.bold = True
                    run.font.color.rgb = AZUL_PRI
                    p.add_run(niveis_str).font.color.rgb = CINZA_TX
            
            # Fonte de Dados
            if tabela.particao and tabela.particao.codigo_fonte:
                h = doc.add_heading("Fonte de Dados", level=3)
                h.paragraph_format.space_before = Pt(8)
                
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                r_m = p.add_run("Modo: ")
                r_m.bold = True
                r_m.font.color.rgb = CINZA_LT
                r_v = p.add_run(tabela.particao.modo)
                r_v.font.color.rgb = CINZA_TX
                if tabela.particao.grupo_consulta:
                    p.add_run("  │  ").font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
                    r_g = p.add_run("Grupo: ")
                    r_g.bold = True
                    r_g.font.color.rgb = CINZA_LT
                    p.add_run(tabela.particao.grupo_consulta).font.color.rgb = CINZA_TX
                
                codigo_formatado = self._formatar_codigo_fonte(tabela.particao.codigo_fonte)
                lang = "Power Query M" if "let" in codigo_formatado[:20].lower() else "DAX"
                _add_code_block(codigo_formatado, lang)
        
        # ====================================================================
        # RELACIONAMENTOS
        # ====================================================================
        if self.relacionamentos:
            doc.add_page_break()
            doc.add_heading("Relacionamentos", level=1)
            
            _add_info_box(
                f"O modelo possui {len(self.relacionamentos)} relacionamentos entre tabelas.",
                "info"
            )
            
            rows_rel = []
            for rel in self.relacionamentos:
                origem = f"{rel.tabela_origem}.{rel.coluna_origem}"
                destino = f"{rel.tabela_destino}.{rel.coluna_destino}"
                bidi = "Sim" if rel.filtro_bidirecional else "Não"
                ativo = "Sim" if rel.esta_ativo else "Não"
                rows_rel.append([origem, "→", destino, bidi, ativo])
            
            _add_table(
                ["Origem", "", "Destino", "Bidirecional", "Ativo"],
                rows_rel, compact=True
            )
        
        # ====================================================================
        # PÁGINAS DO RELATÓRIO
        # ====================================================================
        doc.add_heading("Páginas do Relatório", level=1)
        
        if self.paginas:
            _add_info_box(f"O relatório contém {len(self.paginas)} página(s).", "success")
            rows_pag = []
            for i, pagina in enumerate(self.paginas, 1):
                dimensoes = f"{pagina.largura} × {pagina.altura}"
                rows_pag.append([str(i), pagina.nome_exibicao, pagina.tipo, dimensoes])
            _add_table(["#", "Nome da Página", "Tipo", "Dimensões"], rows_pag)
        else:
            _add_info_box(
                "Nenhuma página encontrada localmente. Este projeto pode ser um "
                "relatório remoto (thin report) onde as páginas ficam armazenadas "
                "no serviço Power BI.",
                "warning"
            )
            
        # ====================================================================
        # DETALHAMENTO DOS VISUAIS
        # ====================================================================
        doc.add_page_break()
        doc.add_heading("Detalhamento dos Visuais", level=1)
        
        for pagina in self.paginas:
            p_pag = doc.add_paragraph()
            p_pag.paragraph_format.space_before = Pt(12)
            run = p_pag.add_run(f"Página: {pagina.nome_exibicao}")
            run.bold = True
            run.font.size = Pt(12)
            run.font.color.rgb = AZUL_PRI
            
            if pagina.visuais:
                 rows_vis = [[v.tipo, v.titulo] for v in pagina.visuais]
                 _add_table(["Tipo", "Título"], rows_vis, compact=True)
            else:
                 p = doc.add_paragraph("Nenhum visual encontrado.")
                 p.paragraph_format.left_indent = Cm(0.5)
                 p.paragraph_format.space_after = Pt(12)
        
        # ====================================================================
        # VISUAIS PERSONALIZADOS
        # ====================================================================
        if self.visuais_personalizados:
            doc.add_heading("Visuais Personalizados", level=1)
            rows_vis = [[v] for v in self.visuais_personalizados]
            _add_table(["ID do Visual"], rows_vis)
        
        # ====================================================================
        # RECURSOS DE IMAGEM
        # ====================================================================
        if self.recursos_imagem:
            doc.add_heading("Recursos de Imagem", level=1)
            rows_img = [[r['nome'], r['tipo']] for r in self.recursos_imagem]
            _add_table(["Nome", "Tipo"], rows_img)
        
        # ====================================================================
        # SALVAR
        # ====================================================================
        doc.save(str(caminho_saida))
        print(f"[OK] Documentação DOCX salva em: {caminho_saida}")
        return caminho_saida


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python documentador_pbip.py <caminho_para_projeto>")
        print("Exemplo: python documentador_pbip.py C:/Projetos/MeuDashboard")
        sys.exit(1)
    
    caminho_projeto = sys.argv[1]
    
    try:
        # Criar documentador
        print("=" * 60)
        print("DOCUMENTADOR DE PROJETOS POWER BI (.pbip)")
        print("=" * 60)
        
        doc = DocumentadorPBIP(caminho_projeto)
        
        # Extrair informações
        doc.extrair_informacoes()
        
        # Gerar e salvar documentação
        print("Gerando documentação...")
        caminho_doc = doc.salvar_documentacao()
        
        print("\n" + "=" * 60)
        print("[OK] CONCLUIDO!")
        print("=" * 60)
        print(f"\nResumo:")
        print(f"  - Tabelas: {len(doc.tabelas)}")
        print(f"  - Relacionamentos: {len(doc.relacionamentos)}")
        print(f"  - Paginas: {len(doc.paginas)}")
        print(f"  - Documentacao: {caminho_doc}")
        
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
