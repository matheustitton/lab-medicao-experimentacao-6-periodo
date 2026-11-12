"""Aplica os dois testes aos dados reais (seção 6 do dashboard).

Além da estatística, do p-valor e do tamanho do efeito, mede o efeito na unidade do cenário
(horas) com intervalo de confiança bootstrap, para discutir a importância prática.

Uso: python -m lab04.dados_reais
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from lab04.caminhos import CSV_REAIS, JSON_DADOS_REAIS, JSON_PARAMETROS
from lab04.exemplo import ALFA
from lab04.testes import aplicar_mann_whitney, aplicar_welch

REPETICOES_BOOTSTRAP = 10_000
# Limiares usuais: Cohen (1988) para o g e Kerby (2014) para a rank-bisserial.
LIMIARES_G = ((0.2, "desprezível"), (0.5, "pequeno"), (0.8, "médio"))
LIMIARES_RANK = ((0.1, "desprezível"), (0.3, "pequeno"), (0.5, "médio"))


def magnitude(efeito: float, limiares: tuple[tuple[float, str], ...]) -> str:
    for limite, rotulo in limiares:
        if abs(efeito) < limite:
            return rotulo
    return "grande"


def ic_bootstrap(
    a: np.ndarray, b: np.ndarray, estatistica, rng: np.random.Generator, repeticoes: int = REPETICOES_BOOTSTRAP
) -> tuple[float, float]:
    """IC de 95% por percentis para estatistica(b) - estatistica(a), reamostrando cada grupo."""
    amostras_a = rng.choice(a, size=(repeticoes, len(a)), replace=True)
    amostras_b = rng.choice(b, size=(repeticoes, len(b)), replace=True)
    diferencas = estatistica(amostras_b, axis=1) - estatistica(amostras_a, axis=1)
    baixo, alto = np.percentile(diferencas, [2.5, 97.5])
    return float(baixo), float(alto)


def analisar(tabela: pd.DataFrame, semente: int) -> dict:
    """Grupo A = sem bot e grupo B = com bot, como na simulação."""
    a = tabela.loc[tabela["grupo"] == "sem_bot", "horas_ate_merge"].to_numpy()
    b = tabela.loc[tabela["grupo"] == "com_bot", "horas_ate_merge"].to_numpy()
    rng = np.random.default_rng(semente + 2)
    welch = aplicar_welch(a, b)
    mann_whitney = aplicar_mann_whitney(a, b)
    welch["magnitude"] = magnitude(welch["efeito"], LIMIARES_G)
    mann_whitney["magnitude"] = magnitude(mann_whitney["efeito"], LIMIARES_RANK)
    for resultado in (welch, mann_whitney):
        resultado["rejeita"] = bool(resultado["p_valor"] < ALFA)
    return {
        "alfa": ALFA,
        "n": {"sem_bot": len(a), "com_bot": len(b)},
        "media": {"sem_bot": float(np.mean(a)), "com_bot": float(np.mean(b))},
        "mediana": {"sem_bot": float(np.median(a)), "com_bot": float(np.median(b))},
        "razao_medianas": float(np.median(b) / np.median(a)),
        "ic_diferenca_medias": ic_bootstrap(a, b, np.mean, rng),
        "ic_diferenca_medianas": ic_bootstrap(a, b, np.median, rng),
        "welch": welch,
        "mann_whitney": mann_whitney,
    }


def main() -> dict:
    parametros = json.loads(JSON_PARAMETROS.read_text(encoding="utf-8"))
    resultado = analisar(pd.read_csv(CSV_REAIS), parametros["semente"])
    JSON_DADOS_REAIS.parent.mkdir(parents=True, exist_ok=True)
    JSON_DADOS_REAIS.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Dados reais em {JSON_DADOS_REAIS}: Welch p = {resultado['welch']['p_valor']:.3f}, "
          f"Mann-Whitney p = {resultado['mann_whitney']['p_valor']:.3f}")
    return resultado


if __name__ == "__main__":
    main()
