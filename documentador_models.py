from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple


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
    descricao: Optional[str] = None

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
    descricao: Optional[str] = None
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

