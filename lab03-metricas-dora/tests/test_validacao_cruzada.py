"""Validação cruzada por repositório da heurística refinada."""
import numpy as np
import pandas as pd
import pytest

from validacao import validacao_cruzada as vc


def _x():
    # 10 repositórios x 4 releases: patch com correção é positivo, release grande sem correção é negativo
    linhas = []
    for i in range(10):
        linhas += [
            dict(repo=f"r{i}", y=1, patch=1, n=3, ncorr=1, frac=1 / 3, gap=5.0),
            dict(repo=f"r{i}", y=0, patch=0, n=20, ncorr=0, frac=0.0, gap=40.0),
            dict(repo=f"r{i}", y=1, patch=0, n=4, ncorr=3, frac=0.75, gap=10.0),
            dict(repo=f"r{i}", y=0, patch=1, n=9, ncorr=0, frac=0.0, gap=np.inf),
        ]
    return pd.DataFrame(linhas)


def test_regra_aplica_patch_fracao_e_intervalo():
    x = _x()
    assert list(vc.regra(x.iloc[:4], pequena=2, fracao=0.3, gap=2)) == [1, 0, 1, 0]


def test_validar_separacao_perfeita_da_f1_um_dentro_e_fora_da_amostra():
    r = vc.validar(_x(), dobras=5)
    assert r["f1_no_ajuste"] == pytest.approx(1.0)
    assert r["cv_f1"] == pytest.approx(1.0)
    assert r["n"] == 40 and r["dobras"] == 5


def test_f1_zero_quando_nada_acerta():
    assert vc.f1(np.array([1, 1, 0]), np.array([0, 0, 0])) == 0.0
