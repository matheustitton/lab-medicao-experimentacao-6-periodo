"""Funções compartilhadas da análise: resumo, tamanhos de efeito, quartis e tabelas."""
import math

import numpy as np
import pandas as pd
import pytest

from analise import comum


def test_resumo_mediana_e_iqr_ignorando_ausentes():
    r = comum.resumo(pd.Series([1, 2, 3, 4, 5, np.nan]))
    assert r["n"] == 5
    assert r["mediana"] == 3
    assert (r["q1"], r["q3"], r["iqr"]) == (2, 4, 2)


def test_resumo_de_serie_vazia():
    r = comum.resumo(pd.Series([np.nan, np.nan]))
    assert r["n"] == 0 and math.isnan(r["mediana"])


def test_epsilon_quadrado():
    assert comum.epsilon_quadrado(9.0, 10) == pytest.approx(1.0)
    assert comum.epsilon_quadrado(4.5, 10) == pytest.approx(0.5)
    assert math.isnan(comum.epsilon_quadrado(1.0, 1))


def test_cliffs_delta_separacao_total_e_sem_efeito():
    assert comum.cliffs_delta([10, 11, 12], [1, 2, 3]) == pytest.approx(1.0)
    assert comum.cliffs_delta([1, 2, 3], [10, 11, 12]) == pytest.approx(-1.0)
    assert comum.cliffs_delta([1, 2, 3], [1, 2, 3]) == pytest.approx(0.0)


@pytest.mark.parametrize("valor,esperado", [
    (0.10, "desprezível"), (0.20, "pequeno"), (0.40, "médio"), (0.60, "grande"), (-0.60, "grande")])
def test_interpretar_delta_romano(valor, esperado):
    assert comum.interpretar_delta(valor) == esperado


@pytest.mark.parametrize("valor,esperado", [
    (0.005, "desprezível"), (0.05, "pequeno"), (0.10, "médio"), (0.20, "grande")])
def test_interpretar_epsilon(valor, esperado):
    assert comum.interpretar_epsilon(valor) == esperado


@pytest.mark.parametrize("valor,esperado", [
    (0.05, "desprezível"), (-0.2, "fraca"), (0.4, "moderada"), (0.8, "forte")])
def test_interpretar_rho(valor, esperado):
    assert comum.interpretar_rho(valor) == esperado


def test_quartis_cria_quatro_grupos_equilibrados():
    g = comum.quartis(pd.Series(range(1, 101)))
    assert sorted(g.unique()) == ["Q1", "Q2", "Q3", "Q4"]
    assert g.value_counts().min() == 25
    assert g.iloc[0] == "Q1" and g.iloc[-1] == "Q4"


def test_quartis_com_empates_colapsa_grupos():
    g = comum.quartis(pd.Series([1] * 30 + [2] * 5 + [3] * 5))
    assert 2 <= g.nunique() <= 4


def test_tabela_md_formata_numeros_e_ausentes():
    t = comum.tabela_md(pd.DataFrame({"a": ["x"], "n": [3], "v": [1.23456], "p": [0.00001], "z": [np.nan]}))
    linhas = t.splitlines()
    assert linhas[0] == "| a | n | v | p | z |"
    assert linhas[2] == "| x | 3 | 1.23 | 1.0e-05 | — |"


def test_salvar_grava_csv_e_md(tmp_path):
    comum.salvar(pd.DataFrame({"a": [1, 2]}), str(tmp_path), "tab")
    assert (tmp_path / "tab.csv").exists() and (tmp_path / "tab.md").exists()


def test_distribuicao_classes_ordem_e_percentual():
    d = comum.distribuicao_classes(pd.Series(["Elite", "Low", "Low", "High"]))
    assert list(d["classe"]) == ["Elite", "High", "Medium", "Low"]
    assert list(d["repositorios"]) == [1, 1, 0, 2]
    assert d["percentual"].sum() == pytest.approx(100)


def test_carregar_le_csv(tmp_path):
    p = tmp_path / "d.csv"
    pd.DataFrame({"a": [1]}).to_csv(p, index=False)
    assert list(comum.carregar(str(p)).columns) == ["a"]
