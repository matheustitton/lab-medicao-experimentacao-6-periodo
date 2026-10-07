import numpy as np
import pandas as pd
import pytest

from validacao.concordancia import (analisar, carregar_rotulos, concordancia_bruta, consenso_maioria,
                                    interpretar_kappa, kappa_fleiss)


def fleiss_manual(rotulos):
    cats = sorted({r for l in rotulos for r in l})
    N, n = len(rotulos), len(rotulos[0])
    cont = np.array([[l.count(c) for c in cats] for l in rotulos])
    p_i = ((cont ** 2).sum(axis=1) - n) / (n * (n - 1))
    p_j = cont.sum(axis=0) / (N * n)
    pe = (p_j ** 2).sum()
    return (p_i.mean() - pe) / (1 - pe)


def test_kappa_fleiss_confere_com_formula_manual():
    dados = [["sim", "sim", "nao"], ["nao", "nao", "nao"], ["sim", "sim", "sim"], ["nao", "sim", "nao"],
             ["sim", "nao", "nao"], ["sim", "sim", "sim"], ["nao", "nao", "sim"], ["nao", "nao", "nao"]]
    assert kappa_fleiss(dados) == pytest.approx(fleiss_manual(dados))
    assert concordancia_bruta(dados) == 4 / 8


def test_kappa_extremos():
    assert kappa_fleiss([["a", "a", "a"], ["b", "b", "b"], ["a", "a", "a"]]) == pytest.approx(1.0)
    assert np.isnan(kappa_fleiss([["a", "a", "a"], ["a", "a", "a"]]))        # sem variação


@pytest.mark.parametrize("k,txt", [(-0.1, "pobre"), (0.1, "leve"), (0.3, "razoável"), (0.5, "moderada"),
                                   (0.7, "substancial"), (0.85, "quase perfeita"), (1.0, "quase perfeita")])
def test_interpretacao_landis_koch(k, txt):
    assert interpretar_kappa(k) == txt
    assert "indefinido" in interpretar_kappa(float("nan"))


def test_consenso_por_maioria_e_empate_1_1_1():
    assert consenso_maioria(["sim", "sim", "nao"]) == "sim"
    assert consenso_maioria(["a", "b", "c"]) is None


def escrever_rotulos(pasta, avaliadores, repos_vals, rel_vals):
    for nome, rv, lv in zip(avaliadores, repos_vals, rel_vals):
        pd.DataFrame({"repo": ["o/a", "o/b"], "url_repo": ["", ""], "tipo_projeto": rv[0],
                      "releases_entregas_reais": rv[1]}).to_csv(pasta / f"rotulos_{nome}_repos.csv", index=False)
        pd.DataFrame({"repo": ["o/a", "o/a"], "tag": ["v1", "v2"], "url_release": ["", ""],
                      "url_comparacao": ["", ""], "corretiva": lv}).to_csv(pasta / f"rotulos_{nome}_releases.csv", index=False)


def test_carregar_rotulos_e_analise_com_desempate(tmp_path):
    av = ["m", "p", "u"]
    escrever_rotulos(
        tmp_path, av,
        repos_vals=[(["cli", "outro"], ["sim", "nao"]), (["cli", "outro"], ["sim", "incerto"]), (["cli", "cli"], ["sim", "sim"])],
        rel_vals=[["sim", "nao"], ["sim", "sim"], ["nao", "nao"]])
    longo = pd.concat([carregar_rotulos(str(tmp_path), av, n) for n in ("repos", "releases")])
    assert set(longo["chave"]) == {"o/a", "o/b", "o/a@v1", "o/a@v2"}
    kappas, consenso, pendentes = analisar(longo, av)
    assert set(kappas["dimensao"]) == {"tipo_projeto", "releases_entregas_reais", "corretiva"}
    assert len(pendentes) == 1 and pendentes.iloc[0]["chave"] == "o/b" and pendentes.iloc[0]["dimensao"] == "releases_entregas_reais"
    des = pd.DataFrame([{"nivel": "repos", "chave": "o/b", "dimensao": "releases_entregas_reais", "rotulo_final": "nao"}])
    _, consenso2, pendentes2 = analisar(longo, av, des)
    assert pendentes2.empty and len(consenso2) == len(consenso) + 1


def test_rotulo_vazio_ou_invalido_e_rejeitado(tmp_path):
    av = ["m"]
    escrever_rotulos(tmp_path, av, [(["cli", ""], ["sim", "talvez"])], [["sim", "nao"]])
    with pytest.raises(ValueError, match="vazios ou inválidos"):
        carregar_rotulos(str(tmp_path), av, "repos")
