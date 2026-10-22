"""RQ05: correlação de Spearman entre frequência de deploy e CFR."""
import numpy as np
import pandas as pd
import pytest

from analise import rq05
from tests.helpers_analise import df_sintetico


def test_spearman_perfeita_e_inversa():
    df = pd.DataFrame({"freq_deploy_semana": [1.0, 2, 3, 4, 5], "cfr_ci": [0.5, 0.4, 0.3, 0.2, 0.1],
                       "cfr_entrega": [0.1, 0.2, 0.3, 0.4, 0.5]})
    t = rq05.correlacoes(df).set_index("variante")
    assert t.loc["CFR (a) CI", "rho"] == pytest.approx(-1.0)
    assert t.loc["CFR (b) entrega", "rho"] == pytest.approx(1.0)
    assert t.loc["CFR (a) CI", "sentido"] == "negativa"
    assert (t["n"] == 5).all()


def test_correlacoes_ignoram_ausentes():
    df = pd.DataFrame({"freq_deploy_semana": [1.0, 2, 3, 4], "cfr_ci": [0.1, np.nan, 0.3, 0.4],
                       "cfr_entrega": [0.1, 0.2, 0.3, 0.4]})
    assert rq05.correlacoes(df).set_index("variante").loc["CFR (a) CI", "n"] == 3


def test_correlacoes_por_heuristica():
    sens = pd.DataFrame({"freq_release": [1.0, 2, 3, 4], "cfr_b_v1": [0.1, 0.2, 0.3, 0.4],
                         "cfr_b_v2": [0.4, 0.3, 0.2, 0.1], "cfr_b_pre_v1": [0, 0, 0, 0]})
    t = rq05.correlacoes_heuristicas(sens).set_index("heuristica")
    assert list(t.index) == ["v1", "v2"]
    assert t.loc["v1", "rho"] == pytest.approx(1.0) and t.loc["v2", "rho"] == pytest.approx(-1.0)


def test_rq05_main(tmp_path):
    csv = tmp_path / "d.csv"
    df_sintetico().to_csv(csv, index=False)
    rq05.main(["--csv", str(csv), "--saida", str(tmp_path), "--sens", str(tmp_path / "nao_existe.csv")])
    assert (tmp_path / "rq05_spearman.csv").exists() and (tmp_path / "rq05_dispersao.png").exists()
