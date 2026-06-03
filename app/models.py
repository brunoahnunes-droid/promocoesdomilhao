from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl


class Categoria(str, Enum):
    ELETRONICOS = "eletronicos"
    SEGURANCA = "seguranca"
    VIAGENS = "viagens"
    CRUZEIROS = "cruzeiros"


class Oferta(BaseModel):
    titulo: str
    preco_atual: float
    preco_original: Optional[float] = None
    desconto_pct: Optional[float] = None
    loja: str
    url: str
    imagem: Optional[str] = None
    categoria: Categoria
    score_ico: Optional[float] = None
