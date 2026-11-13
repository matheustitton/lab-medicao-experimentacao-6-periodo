import json

import pandas as pd

from lab04.interativo import dados_prs, html_simulador, payload, textos_explorador
from lab04.simulacoes import executar_simulacoes

PARAMETROS = {"mediana_horas": 16.9, "sigma_log": 1.64, "sigma_log_amostral": 2.77, "n_por_grupo": 30, "semente": 42}


def tabela():
    return pd.DataFrame({
        "numero": [1, 2, 3, 4],
        "grupo": ["sem_bot", "sem_bot", "com_bot", "com_bot"],
        "horas_ate_merge": [0.5, 200.0, 1.0, 400.0],
        "url": ["u1", "u2", "u3", "u4"],
    })


def test_postos_vao_de_1_a_n_e_o_maior_pr_e_identificado():
    prs = dados_prs(tabela(), 42)
    postos = prs["grupos"]["sem_bot"]["postos"] + prs["grupos"]["com_bot"]["postos"]
    assert sorted(postos) == [1.0, 2.0, 3.0, 4.0]
    assert prs["maior"] == {"numero": 4, "horas": 400.0, "grupo": "com_bot"}
    assert prs["grupos"]["com_bot"]["media"] == 200.5


def test_jitter_e_reproduzivel():
    assert dados_prs(tabela(), 42) == dados_prs(tabela(), 42)


def test_textos_citam_o_maior_pr():
    textos = textos_explorador(dados_prs(tabela(), 42))
    assert "#4" in textos["horas"] and "posto 4" in textos["postos"]


def test_payload_e_json_valido_e_seguro_dentro_de_script():
    simulacoes = executar_simulacoes(PARAMETROS, repeticoes=100)
    texto = payload(dados_prs(tabela(), 42), simulacoes)
    assert "</" not in texto
    dados = json.loads(texto)
    assert len(dados["simulacoes"]["situacoes"]) == len(simulacoes["situacoes"])


def test_simulador_tem_um_botao_por_situacao_e_por_alfa():
    simulacoes = executar_simulacoes(PARAMETROS, repeticoes=100)
    html = html_simulador(simulacoes)
    assert html.count('role="radio"') == len(simulacoes["situacoes"]) + len(simulacoes["alfas"])
    assert 'type="range"' in html
