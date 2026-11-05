import re

import pandas as pd
import pytest

from lab04.dashboard import TITULOS_SECOES, gerar_html, resumir_amostra
from lab04.exemplo import executar_exemplo
from lab04.graficos import simular_estatisticas_h0

PARAMETROS = {
    "mediana_horas": 16.9,
    "sigma_log": 1.64,
    "sigma_log_amostral": 2.77,
    "n_por_grupo": 30,
    "semente": 42,
}


@pytest.fixture(scope="module")
def exemplo():
    return executar_exemplo(PARAMETROS)


@pytest.fixture(scope="module")
def html(exemplo):
    tabela = pd.DataFrame({
        "numero": range(4),
        "grupo": ["sem_bot", "sem_bot", "com_bot", "com_bot"],
        "criado_em": ["2024-08-07T00:00:00Z", "2024-08-17T00:00:00Z", "2024-11-01T00:00:00Z", "2024-11-11T00:00:00Z"],
        "mergeado_em": ["2024-08-08T00:00:00Z"] * 4,
        "horas_ate_merge": [0.5, 200.0, 1.0, 400.0],
        "url": ["u"] * 4,
    })
    return gerar_html(tabela, exemplo, PARAMETROS, simular_estatisticas_h0(PARAMETROS, repeticoes=200))


def test_tem_as_sete_secoes_na_ordem_do_enunciado(html):
    assert re.findall(r"<h2>(.*?)</h2>", html) == TITULOS_SECOES


def test_mostra_g1_e_g2_com_titulo(html):
    # O Plotly escapa acentos e símbolos no JSON, então a busca usa só o trecho em ASCII.
    for titulo in ("Sem bot: real", "Com bot: real", "Welch: estat", "Mann-Whitney: estat"):
        assert titulo in html


def test_links_ficam_no_topo(html):
    topo = html.split("<main>")[0]
    assert "github.com/matheustitton/lab01-repositorios-populares" in topo
    assert "GitHub Projects" in topo
    assert "Dashboard" in topo


def test_interpretacao_do_exemplo_aparece_na_pagina(html, exemplo):
    assert exemplo["interpretacao"]["welch"] in html
    assert exemplo["interpretacao"]["mann_whitney"] in html


def test_secoes_futuras_ficam_marcadas_como_pendentes(html):
    assert html.count('class="pendente"') == 4


def test_html_nao_muda_entre_execucoes(html, exemplo):
    tabela = pd.DataFrame({
        "numero": range(4),
        "grupo": ["sem_bot", "sem_bot", "com_bot", "com_bot"],
        "criado_em": ["2024-08-07T00:00:00Z", "2024-08-17T00:00:00Z", "2024-11-01T00:00:00Z", "2024-11-11T00:00:00Z"],
        "mergeado_em": ["2024-08-08T00:00:00Z"] * 4,
        "horas_ate_merge": [0.5, 200.0, 1.0, 400.0],
        "url": ["u"] * 4,
    })
    assert html == gerar_html(tabela, exemplo, PARAMETROS, simular_estatisticas_h0(PARAMETROS, repeticoes=200))


def test_resumo_da_amostra():
    resumo = resumir_amostra(pd.Series([0.5, 1.0, 3.0, 10.0]).to_numpy())
    assert resumo["n"] == 4
    assert resumo["mediana"] == 2.0
    assert resumo["abaixo_1h"] == 0.25
