"""RQ01 a RQ04: descritivas, classes, variantes e censura, com dados sintéticos."""
import pandas as pd
import pytest

from analise import rq01_04
from tests.helpers_analise import df_sintetico


def test_descritivas_tem_uma_linha_por_metrica_e_n_correto():
    df = df_sintetico()
    t = rq01_04.descritivas(df)
    assert list(t["RQ"]) == ["RQ01", "RQ02", "RQ02", "RQ03", "RQ03", "RQ04"]
    assert t.loc[t.RQ == "RQ01", "n"].iloc[0] == 60
    assert t.loc[t.RQ == "RQ04", "n"].iloc[0] == df["recuperacao_h"].notna().sum()
    assert (t["IQR"] == t["Q3"] - t["Q1"]).all()


def test_classes_por_metrica_somam_100_por_cento():
    c = rq01_04.classes_por_metrica(df_sintetico())
    for _, linha in c.iterrows():
        assert linha["Elite %"] + linha["High %"] + linha["Medium %"] + linha["Low %"] == pytest.approx(100)
        assert linha["Elite"] + linha["High"] + linha["Medium"] + linha["Low"] == linha["n"]
    assert "Classe geral (C1)" in set(c["metrica"])


def test_classes_usam_os_cortes_do_enunciado():
    df = pd.DataFrame({
        "freq_deploy_semana": [8.0, 2.0, 0.5, 0.1], "lead_time_a_h": [10, 50, 300, 900],
        "lead_time_b_h": [10, 50, 300, 900], "cfr_ci": [0.1, 0.2, 0.4, 0.6],
        "cfr_entrega": [0.1, 0.2, 0.4, 0.6], "recuperacao_h": [0.5, 5, 50, 500],
        "classe_dora_c1": ["Elite", "High", "Medium", "Low"]})
    c = rq01_04.classes_por_metrica(df).set_index("metrica")
    for nome in ["Frequência de deploy", "Lead time (a)", "CFR (a) CI", "Recuperação"]:
        assert [c.loc[nome, k] for k in ["Elite", "High", "Medium", "Low"]] == [1, 1, 1, 1]


def test_comparar_variantes_lead_e_cfr():
    df = pd.DataFrame({
        "freq_deploy_semana": [6.0, 5, 4, 3, 2, 1],
        "lead_time_a_h": [100.0, 200, 300, 400, 500, 600], "lead_time_b_h": [50.0, 100, 150, 200, 250, 300],
        "cfr_ci": [0.1, 0.0, 0.2, 0.1, 0.3, 0.1], "cfr_entrega": [0.5, 0.0, 0.4, 0.6, 0.7, 0.2]})
    r = rq01_04.comparar_variantes(df)
    assert r["lead_prop_a_maior_b"] == 1.0
    assert r["lead_razao_mediana_a_sobre_b"] == pytest.approx(2.0)
    assert r["lead_spearman_rho"] == pytest.approx(1.0)
    assert r["cfr_entrega_zero_prop"] == pytest.approx(1 / 6)
    assert r["lead_a_vs_freq_rho"] == pytest.approx(-1.0)   # mais deploys, menos espera
    assert r["cfr_ci_zero_prop"] == pytest.approx(1 / 6)


def test_censura_conta_episodios_e_repositorios():
    df = df_sintetico()
    c = rq01_04.censura(df)
    assert c["repos"] == 60
    assert c["repos_sem_episodio"] == 6
    assert c["episodios"] == int(df["n_episodios"].sum())
    assert c["prop_episodios_censurados"] == pytest.approx(c["episodios_censurados"] / c["episodios"])
    assert c["repos_lead_negativo"] == 3
    assert "repos_com_10pct_ou_mais_censurados" in c


def test_main_gera_tabelas_e_figuras(tmp_path):
    csv = tmp_path / "d.csv"
    df_sintetico().to_csv(csv, index=False)
    saida = tmp_path / "out"
    rq01_04.main(["--csv", str(csv), "--saida", str(saida)])
    for nome in ["rq01_04_descritivas.csv", "rq01_04_classificacao.md", "rq02_rq03_variantes.csv",
                 "rq04_censura.csv", "rq01_04_distribuicoes.png", "rq01_04_classe_dora.png"]:
        assert (saida / nome).exists(), nome
