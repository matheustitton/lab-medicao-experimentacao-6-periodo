"""Tamanho da amostra (seção 6 do enunciado, "para discutir").

Usa o efeito observado nos dados reais (razão entre as medianas) e o cenário-base da simulação
para responder: (1) qual era o poder de cada teste com o n coletado e (2) quantos PRs por
grupo seriam necessários para chegar a 80% de poder.

Uso: python -m lab04.amostra
"""
from __future__ import annotations

import json

import numpy as np

from lab04.caminhos import JSON_AMOSTRA, JSON_DADOS_REAIS, JSON_PARAMETROS
from lab04.exemplo import ALFA
from lab04.simulacao import gerar_grupos
from lab04.simulacoes import TESTES, p_valores

REPETICOES = 4_000
TAMANHOS = (30, 50, 75, 100, 150, 200, 300, 400, 600, 800, 1000)
PODER_ALVO = 0.8


def poder(parametros: dict, fator: float, n: int, rng: np.random.Generator, repeticoes: int = REPETICOES) -> dict:
    a, b = gerar_grupos(rng, parametros["mediana_horas"], parametros["sigma_log"], n, n, fator, repeticoes)
    return {teste: float(np.mean(p < ALFA)) for teste, p in p_valores(a, b).items()}


def curva_por_tamanho(parametros: dict, fator: float, tamanhos: tuple[int, ...] = TAMANHOS,
                      repeticoes: int = REPETICOES) -> dict[str, list[float]]:
    curva: dict[str, list[float]] = {teste: [] for teste in TESTES}
    for i, n in enumerate(tamanhos):
        rng = np.random.default_rng([parametros["semente"], 300, i])
        for teste, valor in poder(parametros, fator, n, rng, repeticoes).items():
            curva[teste].append(valor)
    return curva


def primeiro_n_com_poder(tamanhos: tuple[int, ...], poderes: list[float], alvo: float = PODER_ALVO) -> int | None:
    """Menor n da grade com poder >= alvo, ou None se nenhum chega lá."""
    for n, valor in zip(tamanhos, poderes):
        if valor >= alvo:
            return n
    return None


def estudar(parametros: dict, dados_reais: dict, tamanhos: tuple[int, ...] = TAMANHOS,
            repeticoes: int = REPETICOES) -> dict:
    fator = dados_reais["razao_medianas"]
    curva = curva_por_tamanho(parametros, fator, tamanhos, repeticoes)
    return {
        "fator_observado": fator,
        "reducao_observada": 1 - fator,
        "alfa": ALFA,
        "poder_alvo": PODER_ALVO,
        "repeticoes": repeticoes,
        "tamanhos": list(tamanhos),
        "poder": curva,
        "poder_com_n_real": {teste: valores[0] for teste, valores in curva.items()},
        "n_para_alvo": {teste: primeiro_n_com_poder(tamanhos, valores) for teste, valores in curva.items()},
    }


def main() -> dict:
    parametros = json.loads(JSON_PARAMETROS.read_text(encoding="utf-8"))
    dados_reais = json.loads(JSON_DADOS_REAIS.read_text(encoding="utf-8"))
    resultado = estudar(parametros, dados_reais)
    JSON_AMOSTRA.write_text(json.dumps(resultado, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Tamanho de amostra em {JSON_AMOSTRA}: n para 80% = {resultado['n_para_alvo']}")
    return resultado


if __name__ == "__main__":
    main()
