"""Cores do laboratório: cada teste tem uma cor fixa, em todos os gráficos.

Pares validados para daltonismo e contraste. O aqua fica abaixo de 3:1 sobre a superfície,
por isso o G1 tem uma tabela com os mesmos dados ao lado.
"""
from __future__ import annotations

COR_WELCH = "#2a78d6"
COR_MANN_WHITNEY = "#eb6834"
COR_REAL = "#6250d6"
COR_SIMULADO = "#1baf7a"

SUPERFICIE = "#fcfcfb"
FUNDO_PAGINA = "#f9f9f7"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_FRACA = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"


def com_opacidade(cor: str, opacidade: float) -> str:
    vermelho, verde, azul = (int(cor[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({vermelho},{verde},{azul},{opacidade})"
