"""RQ06: Kruskal-Wallis, tamanhos de efeito, Holm e robustez da idade."""
import pandas as pd
import pytest

from analise import rq06
from tests.helpers_analise import df_sintetico


def test_agrupar_linguagem_junta_pequenas_em_outras():
    s = pd.Series(["Python"] * 20 + ["Go"] * 16 + ["Zig"] * 2 + [None])
    g = rq06.agrupar_linguagem(s, minimo=15)
    assert set(g.unique()) == {"Python", "Go", "Outras"}
    assert (g == "Outras").sum() == 3


def test_kruskal_detecta_diferenca_clara():
    df = pd.DataFrame({"y": list(range(10)) + list(range(100, 110)) + list(range(200, 210))})
    grupo = pd.Series(["a"] * 10 + ["b"] * 10 + ["c"] * 10)
    r = rq06.kruskal(df.rename(columns={"y": "m"}), grupo, "m")
    assert r["teste"] == "Kruskal-Wallis" and r["grupos"] == 3
    assert r["p_valor"] < 0.001 and r["efeito"] > 0.8


def test_kruskal_com_dois_grupos_usa_mann_whitney_e_cliff():
    df = pd.DataFrame({"m": [1, 2, 3, 4, 10, 11, 12, 13]})
    r = rq06.kruskal(df, pd.Series(["a"] * 4 + ["b"] * 4), "m")
    assert r["teste"] == "Mann-Whitney" and r["tipo_efeito"] == "Cliff δ"
    assert r["efeito"] == pytest.approx(-1.0)


def test_kruskal_sem_grupos_suficientes_devolve_none():
    assert rq06.kruskal(pd.DataFrame({"m": [1, 2, 3]}), pd.Series(["a", "a", "a"]), "m") is None


def test_testes_principais_aplicam_holm_e_nao_diminuem_p():
    t = rq06.testes_principais(df_sintetico(120))
    assert len(t) == 4 * 6
    assert (t["p_holm"] >= t["p_valor"] - 1e-12).all()
    assert t["p_holm"].max() <= 1.0
    assert set(t["fator"]) == {"linguagem", "popularidade (estrelas)", "contribuidores", "idade do repositório"}


def test_extremos_q4_contra_q1():
    t = rq06.extremos(df_sintetico(120))
    assert set(t["fator"]) == {"popularidade (estrelas)", "contribuidores", "idade do repositório"}
    assert t["cliff_delta_Q4_vs_Q1"].between(-1, 1).all()


def test_tipo_do_projeto_entra_quando_a_coluna_existe():
    df = df_sintetico()
    df["tipo_projeto"] = ["biblioteca_framework", "cli"] * 30
    assert "tipo do projeto" in rq06.fatores(df)
    assert "tipo do projeto" not in rq06.fatores(df_sintetico())


def test_robustez_idade_filtra_repositorios_jovens():
    df = df_sintetico(80)
    df.loc[:9, "idade_dias"] = 100            # 10 repositórios jovens
    t = rq06.robustez_idade(df, corte_dias=365)
    assert len(t) == 6
    assert (t["n (todos)"] >= t["n (idade >= 365 dias)"]).all()
    assert t["n (idade >= 365 dias)"].max() <= 70


def test_anexar_tipo_projeto_junta_so_os_repos_rotulados():
    df = df_sintetico(6)
    consenso = pd.DataFrame({"nivel": ["repos", "repos", "releases"],
                             "chave": ["org/r0", "org/r1", "org/r0@v1"],
                             "dimensao": ["tipo_projeto", "tipo_projeto", "corretiva"],
                             "consenso": ["cli", "biblioteca_framework", "sim"]})
    r = rq06.anexar_tipo_projeto(df, consenso)
    assert r["tipo_projeto"].notna().sum() == 2
    assert r.loc[r.repo == "org/r0", "tipo_projeto"].iloc[0] == "cli"
    assert len(r) == 6


def test_rq06_main(tmp_path):
    csv = tmp_path / "d.csv"
    df_sintetico(120).to_csv(csv, index=False)
    rq06.main(["--csv", str(csv), "--saida", str(tmp_path)])
    for nome in ["rq06_testes.csv", "rq06_extremos_q4_q1.csv", "rq06_medianas_por_grupo.csv", "rq06_robustez_idade.csv",
                 "rq06_contribuidores_frequencia.png"]:
        assert (tmp_path / nome).exists(), nome
