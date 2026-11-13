import re

import pandas as pd
import pytest

from lab04.amostra import estudar
from lab04.dados_reais import analisar
from lab04.dashboard import TITULOS_SECOES, gerar_html, resumir_amostra
from lab04.exemplo import executar_exemplo
from lab04.graficos import simular_estatisticas_h0
from lab04.simulacoes import executar_simulacoes

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


def montar_tabela():
    return pd.DataFrame({
        "numero": range(6),
        "grupo": ["sem_bot"] * 3 + ["com_bot"] * 3,
        "criado_em": ["2024-08-07T00:00:00Z", "2024-08-12T00:00:00Z", "2024-08-17T00:00:00Z",
                      "2024-11-01T00:00:00Z", "2024-11-05T00:00:00Z", "2024-11-11T00:00:00Z"],
        "mergeado_em": ["2024-08-08T00:00:00Z"] * 6,
        "horas_ate_merge": [0.5, 20.0, 200.0, 1.0, 10.0, 400.0],
        "url": ["u"] * 6,
    })


def montar_html(exemplo):
    tabela = montar_tabela()
    reais = analisar(tabela, PARAMETROS["semente"])
    return gerar_html(
        tabela, exemplo, PARAMETROS, simular_estatisticas_h0(PARAMETROS, repeticoes=200),
        executar_simulacoes(PARAMETROS, repeticoes=200), reais,
        estudar(PARAMETROS, reais, tamanhos=(30, 60), repeticoes=200),
    )


@pytest.fixture(scope="module")
def html(exemplo):
    return montar_html(exemplo)


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


def test_nenhuma_secao_fica_pendente(html):
    assert "pendente" not in html.lower()
    assert "Sprint 2" in html.split("<main>")[0]


def test_mostra_g3_e_g4(html):
    assert 'id="g3"' in html and 'id="g4"' in html


def test_secoes_finais_tem_tabela_e_recomendacao(html):
    secao_6 = html.split('id="secao-6"')[1].split("</section>")[0]
    secao_7 = html.split('id="secao-7"')[1].split("</section>")[0]
    assert "<table>" in secao_6 and "p-valor" in secao_6
    assert "Recomendação" in secao_7 and "Limitações" in secao_7


def test_html_nao_muda_entre_execucoes(html, exemplo):
    assert html == montar_html(exemplo)


def test_resumo_da_amostra():
    resumo = resumir_amostra(pd.Series([0.5, 1.0, 3.0, 10.0]).to_numpy())
    assert resumo["n"] == 4
    assert resumo["mediana"] == 2.0
    assert resumo["abaixo_1h"] == 0.25


def test_tem_trilha_explorador_simulador_e_grafico_de_amostra(html):
    assert 'class="trilha"' in html
    assert 'id="grafico-explorador"' in html and 'id="simulador"' in html and 'id="g-amostra"' in html
    assert '<script src="plotly.min.js"></script>' in html
    assert html.count('class="tese"') == len(TITULOS_SECOES)
