"""RQ07, RQ08 e dataset de sensibilidade, com uma coleta montada à mão."""
from datetime import datetime, timezone

import pandas as pd
import pytest

from analise import rq07, rq08, sensibilidade_dataset
from pipeline.config import Config, Janela


def _classes(c1, c2):
    return pd.DataFrame({"classe_C1": c1, "classe_C2": c2})


def test_pares_identicos_nao_mudam_e_kappa_um():
    df = _classes(["Elite", "High", "Low", "Medium"], ["Elite", "High", "Low", "Medium"])
    t = rq07.comparar_pares(df, ["C1", "C2"])
    assert t["mudaram_%"].iloc[0] == 0 and t["kappa_ponderado"].iloc[0] == pytest.approx(1.0)
    assert t["interpretacao"].iloc[0] == "quase perfeita"


def test_pares_diferentes_contam_mudancas_e_ponderam_a_distancia():
    perto = rq07.comparar_pares(_classes(["Elite", "High", "Medium", "Low"],
                                         ["High", "High", "Medium", "Low"]), ["C1", "C2"])
    longe = rq07.comparar_pares(_classes(["Elite", "High", "Medium", "Low"],
                                         ["Low", "High", "Medium", "Low"]), ["C1", "C2"])
    assert perto["mudaram_n"].iloc[0] == longe["mudaram_n"].iloc[0] == 1
    assert perto["kappa_ponderado"].iloc[0] > longe["kappa_ponderado"].iloc[0]


def test_sensibilidade_frequencia_conta_mudancas_de_classe():
    df = pd.DataFrame({"freq_release": [0.1, 0.5, 2.0, 8.0], "freq_release_pre": [0.1, 1.5, 2.0, 8.0]})
    t = rq07.sensibilidade_frequencia(df)
    assert t["mudaram_classe_n"].iloc[0] == 1          # só 0,5 (Medium) -> 1,5 (High)
    assert t["mudaram_classe_%"].iloc[0] == pytest.approx(25.0)
    assert t["mediana_release_pre"].iloc[0] >= t["mediana_release"].iloc[0]


@pytest.mark.parametrize("k,esperado", [(-0.1, "pobre"), (0.1, "leve"), (0.3, "razoável"),
                                         (0.5, "moderada"), (0.7, "substancial"), (0.9, "quase perfeita")])
def test_interpretar_kappa_landis_koch(k, esperado):
    assert rq07.interpretar_kappa(k) == esperado


def test_distribuicao_e_tabela_cruzada():
    df = _classes(["Elite", "Elite", "Low"], ["Elite", "High", "Low"])
    d = rq07.distribuicao(df, ["C1", "C2"]).set_index("combinacao")
    assert d.loc["C1", "Elite"] == 2 and d.loc["C2", "High"] == 1
    x = rq07.tabela_cruzada(df, "C1", "C2").set_index("C1 \\ C2")
    assert x.loc["Elite", "High"] == 1 and x.loc["Low", "Low"] == 1


# ---------- dataset de sensibilidade + RQ07/RQ08 ----------
def _coleta():
    def rel(tag, data, ant, pre=False, commits=()):
        return {"tag": tag, "publicada_em": data, "prerelease": pre, "anterior_tag": ant,
                "status_compare": "ok" if ant else "sem_anterior", "total_commits": len(commits),
                "commits": [{"sha": f"s{i}", "data": c[0], "msg": c[1], "merge": False}
                            for i, c in enumerate(commits)]}
    releases = [
        rel("v1.0.0", "2025-10-10T00:00:00Z", None),
        rel("v1.1.0", "2025-11-10T00:00:00Z", "v1.0.0", commits=[("2025-11-01T00:00:00Z", "feat: a")]),
        rel("v1.1.1", "2025-11-12T00:00:00Z", "v1.1.0", commits=[("2025-11-11T00:00:00Z", "fix: b")]),
        rel("v1.2.0-rc1", "2025-12-01T00:00:00Z", None, pre=True),
        rel("v1.2.0", "2025-12-20T00:00:00Z", "v1.1.1", commits=[("2025-12-10T00:00:00Z", "feat: c")]),
    ]
    runs = [{"workflow_id": 1, "conclusao": c, "iniciada_em": t, "atualizada_em": t}
            for c, t in [("success", "2025-11-01T09:00:00Z"), ("failure", "2025-11-01T10:00:00Z"),
                         ("success", "2025-11-01T12:00:00Z")]]
    return {"meta": {"repo": "o/r", "estrelas": 10, "linguagem": "Go", "criado_em": "2020-01-01T00:00:00Z",
                     "default_branch": "main", "contribuidores": 3},
            "releases": releases, "runs": runs, "runs_ignorados": 0, "teto_runs_atingido": False}


def _cfg():
    j = Janela(datetime(2025, 10, 1, tzinfo=timezone.utc), datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc))
    return Config(janela=j, heuristica="v1")


def test_linha_sensibilidade_conta_prerelease_so_nas_variantes_c2():
    l = sensibilidade_dataset.linha_sensibilidade(_coleta(), _cfg())
    assert l["n_prereleases"] == 1
    assert l["freq_release_pre"] > l["freq_release"]
    assert l["cfr_a"] == pytest.approx(1 / 3)       # 1 falha em 1 + 2 sucessos
    for c in ["classe_C1", "classe_C2", "classe_C3", "classe_C4", "classe_C4_v1", "classe_C4_v2", "classe_C4_v3"]:
        assert l[c] in {"Elite", "High", "Medium", "Low"}


def test_rework_rate_conta_releases_corretivas():
    from metricas.heuristica import HEURISTICAS
    from pipeline.adaptadores import releases_de_coleta
    r = sensibilidade_dataset.rework_rate(releases_de_coleta(_coleta()), HEURISTICAS["v1"])
    assert r["n"] == 4                      # a pré-release não conta
    assert r["corretivas"] == 1             # só v1.1.1 (patch com fix)
    assert r["taxa"] == pytest.approx(0.25)
    assert sensibilidade_dataset.rework_rate([], HEURISTICAS["v1"])["taxa"] is None


def test_gerar_escreve_csv_e_rq07_rq08_rodam_sobre_ele(tmp_path):
    from pipeline.estado import RepoStore, ETAPA_FINAL
    import json
    store = RepoStore(str(tmp_path / "estado.sqlite"))
    for i in range(6):
        c = _coleta()
        c["meta"]["repo"] = f"o/r{i}"
        store.adicionar_candidatos([c["meta"]])
        store.salvar_coleta(f"o/r{i}", c)
        store.avancar(f"o/r{i}", ETAPA_FINAL)
    cfg = _cfg()
    cfg.saida_dir = str(tmp_path / "saida")
    df = sensibilidade_dataset.gerar(store, cfg)
    assert len(df) == 6 and (tmp_path / "saida" / "dataset_sensibilidade.csv").exists()
    csv = str(tmp_path / "saida" / "dataset_sensibilidade.csv")
    rq07.main(["--csv", csv, "--saida", str(tmp_path / "a")])
    rq08.main(["--csv", csv, "--saida", str(tmp_path / "a")])
    for nome in ["rq07_pares.csv", "rq07_heuristicas_pares.csv", "rq08_rework.csv",
                 "rq07_frequencia_com_prerelease.csv"]:
        assert (tmp_path / "a" / nome).exists(), nome
    assert rq08.resumo_rework(df)["heuristica"].tolist() == ["v1", "v2", "v3", "v4", "v5"]
