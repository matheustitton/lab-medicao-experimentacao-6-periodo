"""Comando único do Lab04: python rodar.py

Parte do CSV congelado, sem acessar a rede: estima os parâmetros, aplica os testes ao
exemplo simulado, monta o dashboard e o abre no navegador.
"""
from __future__ import annotations

import argparse
import webbrowser

from lab04 import dashboard, exemplo, parametros


def main() -> None:
    leitor = argparse.ArgumentParser(description=__doc__)
    leitor.add_argument("--nao-abrir", action="store_true", help="só gera o dashboard, sem abrir o navegador")
    argumentos = leitor.parse_args()

    parametros.main()
    exemplo.main()
    caminho = dashboard.main()
    if not argumentos.nao_abrir:
        webbrowser.open(caminho.as_uri())


if __name__ == "__main__":
    main()
