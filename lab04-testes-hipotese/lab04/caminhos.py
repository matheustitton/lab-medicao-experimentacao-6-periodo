"""Caminhos do laboratório, relativos à raiz da pasta do Lab04."""
from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
SAIDA = RAIZ / "saida"
DASHBOARD = RAIZ / "dashboard"

CSV_REAIS = DADOS / "prs_reais.csv"
JSON_PARAMETROS = DADOS / "parametros_simulacao.json"
JSON_EXEMPLO = SAIDA / "exemplo_s01.json"
JSON_SIMULACOES = SAIDA / "simulacoes_s02.json"
JSON_DADOS_REAIS = SAIDA / "dados_reais.json"
JSON_AMOSTRA = SAIDA / "tamanho_amostra.json"
