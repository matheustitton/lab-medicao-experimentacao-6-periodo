"""Aplica os dois testes a um conjunto de dados simulado e interpreta o resultado.

Como a simulação define o efeito verdadeiro, a interpretação diz se cada teste acertou.
O fator do exemplo é fixado aqui, sem olhar o resultado.

Uso: python -m lab04.exemplo
"""
from __future__ import annotations

import json

import numpy as np

from lab04.caminhos import JSON_EXEMPLO, JSON_PARAMETROS
from lab04.simulacao import gerar_grupos
from lab04.testes import aplicar_mann_whitney, aplicar_welch

FATOR_EXEMPLO = 0.5  # o bot reduz a mediana do tempo até o merge à metade
ALFA = 0.05


def formatar_numero(valor: float, casas: int = 2) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def formatar_p(p: float) -> str:
    return "p < 0,001" if p < 0.001 else f"p = {formatar_numero(p, 3)}"


def desfecho(p_valor: float, fator: float, alfa: float = ALFA) -> str:
    """Compara a decisão do teste com a verdade da simulação."""
    rejeita = p_valor < alfa
    if fator == 1.0:
        return "erro tipo I" if rejeita else "acerto"
    return "acerto" if rejeita else "erro tipo II"


def interpretar(nome: str, resultado: dict, fator: float, alfa: float = ALFA) -> str:
    p_valor = resultado["p_valor"]
    decisao = "rejeita H₀" if p_valor < alfa else "não rejeita H₀"
    verdade = "H₀ é verdadeira" if fator == 1.0 else f"existe efeito real (k = {formatar_numero(fator, 1)})"
    significado = {
        "acerto": "e a decisão está correta",
        "erro tipo I": "e a decisão é um erro tipo I",
        "erro tipo II": "e a decisão é um erro tipo II: o efeito existe, mas esta amostra não bastou para detectá-lo",
    }[desfecho(p_valor, fator, alfa)]
    return (
        f"{nome}: {formatar_p(p_valor)}, {resultado['nome_efeito']} = {formatar_numero(resultado['efeito'])}. "
        f"Com α = {formatar_numero(alfa)}, o teste {decisao}. "
        f"Na simulação, {verdade}, {significado}."
    )


def executar_exemplo(parametros: dict, fator: float = FATOR_EXEMPLO) -> dict:
    rng = np.random.default_rng(parametros["semente"])
    n = parametros["n_por_grupo"]
    sem_bot, com_bot = gerar_grupos(rng, parametros["mediana_horas"], parametros["sigma_log"], n, n, fator)
    welch = aplicar_welch(sem_bot, com_bot)
    mann_whitney = aplicar_mann_whitney(sem_bot, com_bot)
    return {
        "fator": fator,
        "alfa": ALFA,
        "grupos": {"sem_bot": sem_bot.tolist(), "com_bot": com_bot.tolist()},
        "welch": welch,
        "mann_whitney": mann_whitney,
        "interpretacao": {
            "welch": interpretar("Welch", welch, fator),
            "mann_whitney": interpretar("Mann-Whitney", mann_whitney, fator),
        },
    }


def main() -> dict:
    parametros = json.loads(JSON_PARAMETROS.read_text(encoding="utf-8"))
    exemplo = executar_exemplo(parametros)
    JSON_EXEMPLO.parent.mkdir(parents=True, exist_ok=True)
    JSON_EXEMPLO.write_text(
        json.dumps(exemplo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Exemplo em {JSON_EXEMPLO}")
    return exemplo


if __name__ == "__main__":
    main()
