"""Leitura do config.yaml e objetos de configuração compartilhados."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

import yaml


@dataclass(frozen=True)
class Janela:
    inicio: datetime
    fim: datetime

    def contem(self, dt: datetime) -> bool:
        return self.inicio <= dt <= self.fim

    @property
    def semanas(self) -> float:
        return (self.fim - self.inicio).total_seconds() / (7 * 86400)


@dataclass
class Config:
    janela: Janela
    alvo_amostra: int = 100
    min_releases: int = 5
    min_runs: int = 50
    semente: int = 42
    faixas_estrelas: List[str] = field(default_factory=list)
    caminho_cache: str = "data/cache.sqlite"
    caminho_estado: str = "data/estado.sqlite"
    saida_dir: str = "data/saida"
    rotulos_dir: str = "rotulos"
    max_paginas_busca: int = 10
    max_paginas_releases: int = 10
    max_paginas_compare: int = 30
    janela_corretiva_dias: int = 7
    heuristica: str = "v1"
    amostra_ouro_n: int = 60
    releases_por_repo_ouro: int = 5
    avaliadores: List[str] = field(default_factory=lambda: ["matheus", "pedro", "murilo"])


def _data(texto: str, fim_do_dia: bool = False) -> datetime:
    d = datetime.strptime(texto, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return d.replace(hour=23, minute=59, second=59) if fim_do_dia else d


def carregar_config(caminho: str = "config.yaml") -> Config:
    with open(caminho, encoding="utf-8") as f:
        bruto = yaml.safe_load(f)
    j = bruto.pop("janela")
    janela = Janela(_data(j["inicio"]), _data(j["fim"], fim_do_dia=True))
    return Config(janela=janela, **bruto)
