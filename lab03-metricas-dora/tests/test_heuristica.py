import pytest

from metricas.heuristica import (HEURISTICAS, eh_patch_bump, n_commits_correcao,
                                 obter_heuristica, parse_versao, v1, v2, v3)
from tests.helpers import commit, release


def test_parse_versao():
    assert parse_versao("v2.3.1") == (2, 3, 1)
    assert parse_versao("release-1.2") == (1, 2, 0)
    assert parse_versao("pkg@4.0.0-rc.1") == (4, 0, 0)
    assert parse_versao("nightly") is None and parse_versao(None) is None


def test_patch_bump():
    assert eh_patch_bump(release("v2.3.1", "2025-01-01", "v2.3.0"))
    assert not eh_patch_bump(release("v2.4.0", "2025-01-01", "v2.3.1"))
    assert not eh_patch_bump(release("v2.3.0", "2025-01-01", None))
    assert not eh_patch_bump(release("nightly", "2025-01-01", "v2.3.0"))


@pytest.mark.parametrize("msg,esperado", [
    ("fix: crash ao abrir", 1), ("Fixes #12", 1), ("revert da feature", 1), ("HOTFIX urgente", 1),
    ("add prefix handling", 0), ("affixed label", 0), ("feat: novo botão", 0),
])
def test_palavras_de_correcao(msg, esperado):
    assert n_commits_correcao(release("v1", "2025-01-01", commits=[commit("2025-01-01", msg)])) == esperado


def test_versoes_da_heuristica():
    patch_fix = release("v1.0.1", "2025-01-02", "v1.0.0", [commit("2025-01-01", "fix: bug")])
    patch_feat = release("v1.0.1", "2025-01-02", "v1.0.0",
                         [commit("2025-01-01", f"feat: {i}") for i in range(8)])
    minor_fix = release("v1.1.0", "2025-01-02", "v1.0.0", [commit("2025-01-01", "fix: a"), commit("2025-01-01", "fix: b")])
    minor_feat = release("v1.1.0", "2025-01-02", "v1.0.0", [commit("2025-01-01", "feat: a")])
    assert v1(patch_fix) and v1(patch_feat) and v1(minor_fix) and not v1(minor_feat)
    assert v2(patch_fix) and not v2(patch_feat) and not v2(minor_fix)
    assert v3(patch_fix) and not v3(patch_feat) and v3(minor_fix) and not v3(minor_feat)
    assert v3(release("v1.0.1", "2025-01-02", "v1.0.0", []))      # patch sem commits coletados


def test_registro_de_heuristicas():
    assert {"v1", "v2", "v3"} <= set(HEURISTICAS) and obter_heuristica("v2") is v2
    with pytest.raises(ValueError):
        obter_heuristica("v99")


# ---------- v4 e v5 (refinadas contra a amostra-ouro) ----------
def _rel(tag, ant, msgs, dia="2025-06-10", ant_dia=None):
    from datetime import datetime, timezone
    from metricas.modelos import Commit, Release
    pub = datetime.fromisoformat(dia + "T00:00:00+00:00")
    anterior = datetime.fromisoformat(ant_dia + "T00:00:00+00:00") if ant_dia else None
    return Release(tag=tag, publicada_em=pub, anterior_tag=ant,
                   commits=tuple(Commit(f"s{i}", pub, m) for i, m in enumerate(msgs)),
                   anterior_publicada_em=anterior)


def test_v4_patch_com_correcao_e_corretiva():
    from metricas.heuristica import v4
    assert v4(_rel("v1.0.1", "v1.0.0", ["fix: crash ao abrir"]))


def test_v4_patch_pequeno_sem_correcao_e_corretiva_mas_patch_grande_nao():
    from metricas.heuristica import v4
    assert v4(_rel("v1.0.1", "v1.0.0", ["bump version"]))
    assert not v4(_rel("v1.0.1", "v1.0.0", ["feat: a", "feat: b", "feat: c", "feat: d"]))


def test_v4_ignora_merge_e_correcao_de_dependencia():
    from metricas.heuristica import n_correcao_util, v4
    r = _rel("v1.1.0", "v1.0.0", ["Merge pull request #1 fix: algo", "fix(deps): bump lodash",
                                   "feat: a", "feat: b"])
    assert n_correcao_util(r) == 0
    assert not v4(r)


def test_v4_release_grande_so_com_fracao_alta_de_correcao():
    from metricas.heuristica import v4
    assert v4(_rel("v2.0.0", "v1.0.0", ["fix: a", "fix: b", "feat: c", "feat: d"]))   # 50%
    assert not v4(_rel("v2.0.0", "v1.0.0", ["fix: a"] + [f"feat: {i}" for i in range(9)]))   # 10%


def test_v5_acrescenta_correcao_logo_apos_a_release_anterior():
    from metricas.heuristica import v4, v5
    feats = [f"feat: {i}" for i in range(9)]
    rapida = _rel("v2.1.0", "v2.0.0", ["fix: a"] + feats, dia="2025-06-11", ant_dia="2025-06-10")
    lenta = _rel("v2.1.0", "v2.0.0", ["fix: a"] + feats, dia="2025-08-11", ant_dia="2025-06-10")
    assert not v4(rapida) and v5(rapida)
    assert not v5(lenta)


def test_v5_sem_data_da_anterior_cai_na_v4():
    from metricas.heuristica import v4, v5
    r = _rel("v2.1.0", "v2.0.0", ["fix: a"] + [f"feat: {i}" for i in range(9)])
    assert v5(r) == v4(r) is False


def test_adaptador_preenche_a_data_da_release_anterior():
    from pipeline.adaptadores import releases_de_coleta
    coleta = {"releases": [
        {"tag": "v1", "publicada_em": "2025-01-01T00:00:00Z", "prerelease": False, "anterior_tag": None,
         "status_compare": "sem_anterior", "commits": []},
        {"tag": "v2", "publicada_em": "2025-01-05T00:00:00Z", "prerelease": False, "anterior_tag": "v1",
         "status_compare": "ok", "commits": []}]}
    rs = releases_de_coleta(coleta)
    assert rs[0].anterior_publicada_em is None
    assert rs[1].anterior_publicada_em == rs[0].publicada_em
