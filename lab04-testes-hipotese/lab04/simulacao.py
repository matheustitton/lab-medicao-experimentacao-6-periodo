"""Gerador dos dados simulados: tempo até o merge com distribuição lognormal."""
from __future__ import annotations

import numpy as np


def gerar_grupos(
    rng: np.random.Generator,
    mediana: float,
    sigma: float,
    n_a: int,
    n_b: int,
    fator: float = 1.0,
    repeticoes: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Gera os grupos A (sem bot) e B (com bot), em horas.

    `fator` multiplica a mediana de B: 1.0 significa H0 verdadeira. Com `repeticoes`, cada
    grupo vira uma matriz (repeticoes, n), com um conjunto de dados por linha.
    """
    if mediana <= 0 or sigma <= 0 or fator <= 0:
        raise ValueError("mediana, sigma e fator precisam ser positivos")
    forma_a = n_a if repeticoes is None else (repeticoes, n_a)
    forma_b = n_b if repeticoes is None else (repeticoes, n_b)
    grupo_a = rng.lognormal(np.log(mediana), sigma, size=forma_a)
    grupo_b = rng.lognormal(np.log(mediana * fator), sigma, size=forma_b)
    return grupo_a, grupo_b
