"""Estima os parâmetros da simulação a partir dos dados reais.

Uso: python -m lab04.parametros
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from lab04.caminhos import CSV_REAIS, JSON_PARAMETROS

SEMENTE = 42
# PR mergeado em segundos: piso de 1 minuto para o log não explodir.
PISO_HORAS = 1 / 60


def sigma_log_amostral(horas: np.ndarray) -> float:
    """Desvio-padrão amostral do log do tempo: inflado pelos PRs mergeados em minutos."""
    return float(np.std(np.log(np.maximum(horas, PISO_HORAS)), ddof=1))


def sigma_por_media_mediana(horas: np.ndarray) -> float:
    """σ da lognormal que reproduz a média e a mediana: média/mediana = exp(σ²/2)."""
    media, mediana = float(np.mean(horas)), float(np.median(horas))
    if media <= mediana:
        raise ValueError("a amostra não tem assimetria à direita (média <= mediana)")
    return float(np.sqrt(2 * np.log(media / mediana)))


def estimar_parametros(tabela: pd.DataFrame) -> dict:
    """A referência é o grupo sem bot: é a situação de H0 antes de qualquer efeito.

    O cenário-base usa o σ que reproduz a cauda direita real, a parte que pesa no Welch.
    O σ amostral geraria médias de ~300 h contra 65 h reais; fica para o cenário de cauda
    pesada da Q3.
    """
    referencia = tabela.loc[tabela["grupo"] == "sem_bot", "horas_ate_merge"].to_numpy()
    return {
        "mediana_horas": round(float(np.median(referencia)), 4),
        "sigma_log": round(sigma_por_media_mediana(referencia), 4),
        "sigma_log_amostral": round(sigma_log_amostral(referencia), 4),
        "n_por_grupo": int(tabela.groupby("grupo").size().min()),
        "semente": SEMENTE,
    }


def main() -> dict:
    parametros = estimar_parametros(pd.read_csv(CSV_REAIS))
    JSON_PARAMETROS.write_text(json.dumps(parametros, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Parametros em {JSON_PARAMETROS}: {parametros}")
    return parametros


if __name__ == "__main__":
    main()
