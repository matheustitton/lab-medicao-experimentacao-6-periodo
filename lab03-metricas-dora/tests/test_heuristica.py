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
    assert set(HEURISTICAS) == {"v1", "v2", "v3"} and obter_heuristica("v2") is v2
    with pytest.raises(ValueError):
        obter_heuristica("v99")
