"""Situações simuladas na Sprint 2: o cenário-base, três violações de pressuposto (Q3) e um contraste.

Em todas, H0 é verdadeira quando o fator é 1: os dois grupos saem da mesma distribuição.
O efeito é sempre multiplicativo (o bot multiplica o tempo do grupo B por `fator`).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lab04.simulacao import gerar_grupos

# Um PR "esquecido" fica aberto 20 vezes mais que o normal.
MULTIPLICADOR_OUTLIER = 20.0
PROPORCAO_OUTLIERS = 0.05
N_PEQUENO = 10
# Contraste: σ pequeno deixa a lognormal quase simétrica, o terreno do teste paramétrico.
SIGMA_QUASE_SIMETRICO = 0.2


@dataclass(frozen=True)
class Situacao:
    chave: str
    rotulo: str
    descricao: str
    sigma: float
    n: int
    proporcao_outliers: float = 0.0

    @property
    def viola_pressupostos(self) -> bool:
        return self.chave not in ("base", "quase_simetrico")


def contaminar_com_outliers(
    rng: np.random.Generator, horas: np.ndarray, proporcao: float, multiplicador: float = MULTIPLICADOR_OUTLIER
) -> np.ndarray:
    """Multiplica uma fração sorteada dos PRs, como PRs esquecidos abertos por semanas."""
    if not 0 <= proporcao < 1:
        raise ValueError("a proporção de outliers precisa estar em [0, 1)")
    if proporcao == 0:
        return horas
    sorteio = rng.random(horas.shape) < proporcao
    return np.where(sorteio, horas * multiplicador, horas)


def gerar(
    rng: np.random.Generator, parametros: dict, situacao: Situacao, fator: float, repeticoes: int
) -> tuple[np.ndarray, np.ndarray]:
    """Matrizes (repeticoes, n) dos grupos sem bot e com bot na situação pedida."""
    a, b = gerar_grupos(rng, parametros["mediana_horas"], situacao.sigma, situacao.n, situacao.n, fator, repeticoes)
    a = contaminar_com_outliers(rng, a, situacao.proporcao_outliers)
    b = contaminar_com_outliers(rng, b, situacao.proporcao_outliers)
    return a, b


def montar_situacoes(parametros: dict) -> list[Situacao]:
    """As cinco situações, com σ e n tirados dos dados reais (dados/parametros_simulacao.json)."""
    sigma, sigma_amostral, n = parametros["sigma_log"], parametros["sigma_log_amostral"], parametros["n_por_grupo"]
    fmt = lambda valor: f"{valor:.2f}".replace(".", ",")  # noqa: E731
    return [
        Situacao(
            "base", "Cenário-base",
            f"Lognormal com σ = {fmt(sigma)} e n = {n} por grupo, como nos dados reais.",
            sigma, n,
        ),
        Situacao(
            "cauda_pesada", "Cauda pesada",
            f"σ = {fmt(sigma_amostral)} (desvio-padrão do log real): poucos PRs enormes dominam a média.",
            sigma_amostral, n,
        ),
        Situacao(
            "outliers", "Outliers",
            f"Cenário-base, mas {PROPORCAO_OUTLIERS:.0%} dos PRs ficam esquecidos e levam "
            f"{MULTIPLICADOR_OUTLIER:.0f} vezes mais.",
            sigma, n, PROPORCAO_OUTLIERS,
        ),
        Situacao(
            "amostra_pequena", "Amostra pequena",
            f"Cenário-base com só n = {N_PEQUENO} PRs por grupo.",
            sigma, N_PEQUENO,
        ),
        Situacao(
            "quase_simetrico", "Quase simétrico (contraste)",
            f"σ = {fmt(SIGMA_QUASE_SIMETRICO)} e n = {n}: dados quase normais, a situação mais favorável ao Welch. "
            "Não é o cenário real, serve para ver se a vantagem muda de lado.",
            SIGMA_QUASE_SIMETRICO, n,
        ),
    ]
