import pandas as pd
import pytest

from pipeline.estado import RepoStore
from validacao.avaliacao_heuristica import avaliar, metricas_classificacao


def test_precisao_recall_f1_exemplo_do_enunciado():
    y_true = [1] * 30 + [0] * 10 + [1] * 20 + [0] * 40      # consenso: 50 corretivas
    y_pred = [1] * 30 + [1] * 10 + [0] * 20 + [0] * 40      # heurística marcou 40, acertou 30
    m = metricas_classificacao(y_true, y_pred)
    assert m["precisao"] == pytest.approx(0.75) and m["recall"] == pytest.approx(0.60)
    assert m["f1"] == pytest.approx(2 / 3, abs=1e-3)


def test_avaliar_heuristicas_contra_consenso():
    s = RepoStore(":memory:")
    s.adicionar_candidatos([{"repo": "o/r"}])
    s.salvar_coleta("o/r", {"releases": [
        {"tag": "v1.0.0", "publicada_em": "2026-01-01T00:00:00Z", "prerelease": False, "anterior_tag": None,
         "status_compare": "sem_anterior", "commits": []},
        {"tag": "v1.0.1", "publicada_em": "2026-01-02T00:00:00Z", "prerelease": False, "anterior_tag": "v1.0.0",
         "status_compare": "ok", "commits": [{"sha": "a", "data": "2026-01-01T12:00:00Z", "msg": "fix: bug"}]},
        {"tag": "v1.1.0", "publicada_em": "2026-02-01T00:00:00Z", "prerelease": False, "anterior_tag": "v1.0.1",
         "status_compare": "ok", "commits": [{"sha": "b", "data": "2026-01-20T00:00:00Z", "msg": "feat: nova"}]}]})
    consenso = pd.DataFrame({"chave": ["o/r@v1.0.0", "o/r@v1.0.1", "o/r@v1.1.0", "o/r@inexistente"],
                             "consenso": ["nao", "sim", "nao", "sim"]})
    t = avaliar(consenso, s).set_index("versao")
    assert t.loc["v1", "f1"] == 1.0 and bool(t.loc["v1", "meta_f1_ok"]) and t.loc["v1", "n"] == 3
