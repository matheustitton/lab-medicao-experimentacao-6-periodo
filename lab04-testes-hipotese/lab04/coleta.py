"""Coleta única dos PRs reais: gera dados/prs_reais.csv pela API de busca do GitHub.

O CSV fica congelado no repositório, e o resto do laboratório não acessa a rede.
Critérios e justificativa das janelas: dados/FONTE.md.

Uso: python -m lab04.coleta
"""
from __future__ import annotations

import os
import time
from datetime import datetime

import pandas as pd
import requests

from lab04.caminhos import CSV_REAIS

REPOSITORIO = "formbricks/formbricks"
BOT_REVISAO = "coderabbitai[bot]"
N_POR_GRUPO = 30
# Último dia antes do primeiro comentário do bot (1º comentário: 19/08/2024).
FIM_SEM_BOT = "2024-08-18"
# Cobertura do bot ~100% e fora do Hacktoberfest (outubro).
INICIO_COM_BOT = "2024-11-01"

URL_BUSCA = "https://api.github.com/search/issues"
COLUNAS = ["numero", "grupo", "criado_em", "mergeado_em", "horas_ate_merge", "url"]


def horas_ate_merge(criado_em: str, mergeado_em: str) -> float:
    """Horas entre a abertura e o merge, a partir de timestamps ISO 8601 do GitHub."""
    inicio = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
    fim = datetime.fromisoformat(mergeado_em.replace("Z", "+00:00"))
    return (fim - inicio).total_seconds() / 3600


def eh_autor_bot(item: dict) -> bool:
    usuario = item["user"]
    return usuario.get("type") == "Bot" or usuario["login"].endswith("[bot]")


def montar_linhas(itens: list[dict], grupo: str, limite: int = N_POR_GRUPO) -> list[dict]:
    """Converte itens da busca em linhas do CSV, sem autores bot e sem PRs não mergeados."""
    linhas = []
    for item in itens:
        mergeado_em = item.get("pull_request", {}).get("merged_at")
        if mergeado_em is None or eh_autor_bot(item):
            continue
        linhas.append({
            "numero": item["number"],
            "grupo": grupo,
            "criado_em": item["created_at"],
            "mergeado_em": mergeado_em,
            "horas_ate_merge": round(horas_ate_merge(item["created_at"], mergeado_em), 4),
            "url": item["html_url"],
        })
        if len(linhas) == limite:
            break
    return linhas


def consultas() -> dict[str, tuple[str, str]]:
    """Consulta e ordem de cada grupo: os PRs mais próximos do fim ou do início da janela."""
    base = f"repo:{REPOSITORIO} is:pr is:merged"
    return {
        "sem_bot": (f"{base} created:<={FIM_SEM_BOT} -commenter:{BOT_REVISAO}", "desc"),
        "com_bot": (f"{base} created:>={INICIO_COM_BOT} commenter:{BOT_REVISAO}", "asc"),
    }


def buscar(consulta: str, ordem: str) -> list[dict]:
    cabecalhos = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    parametros = {"q": consulta, "sort": "created", "order": ordem, "per_page": 100}
    resposta = requests.get(URL_BUSCA, params=parametros, headers=cabecalhos, timeout=30)
    resposta.raise_for_status()
    return resposta.json()["items"]


def coletar() -> pd.DataFrame:
    linhas: list[dict] = []
    for grupo, (consulta, ordem) in consultas().items():
        linhas += montar_linhas(buscar(consulta, ordem), grupo)
        time.sleep(7)  # a busca sem token aceita 10 chamadas por minuto
    return pd.DataFrame(linhas, columns=COLUNAS)


def main() -> None:
    tabela = coletar()
    CSV_REAIS.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(CSV_REAIS, index=False, lineterminator="\n")
    print(f"{len(tabela)} PRs em {CSV_REAIS}")
    print(tabela.groupby("grupo")["horas_ate_merge"].describe().round(1))


if __name__ == "__main__":
    main()
