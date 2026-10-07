import pandas as pd

from pipeline.estado import RepoStore
from validacao.amostra import gerar_planilhas, sortear_releases, sortear_repos


def store_com(repos):
    s = RepoStore(":memory:")
    s.adicionar_candidatos([{"repo": r} for r in repos])
    for r in repos:
        s.salvar_coleta(r, {"releases": [
            {"tag": f"v{i}", "publicada_em": f"2026-0{i}-01T00:00:00Z", "prerelease": False,
             "anterior_tag": f"v{i-1}" if i > 1 else None} for i in range(1, 9)]
            + [{"tag": "rc", "publicada_em": "2026-05-05T00:00:00Z", "prerelease": True, "anterior_tag": None}]})
    return s


def test_sorteio_e_planilhas_reprodutiveis_e_sem_vazar_heuristica(tmp_path):
    repos = [f"o/r{i}" for i in range(30)]
    df = pd.DataFrame({"repo": repos})
    assert sortear_repos(df, 10, 42) == sortear_repos(df, 10, 42) and sortear_repos(df, 10, 42) != sortear_repos(df, 10, 7)
    s = store_com(repos)
    r1 = sortear_releases(s.coleta_de("o/r1"), 5, 42, "o/r1")
    assert r1 == sortear_releases(s.coleta_de("o/r1"), 5, 42, "o/r1") and len(r1) == 5
    assert all(not r["prerelease"] and r["anterior_tag"] for r in r1)
    gerar_planilhas(s, df, ["m", "p", "u"], 10, 5, 42, str(tmp_path))
    a = pd.read_csv(tmp_path / "rotulos_m_releases.csv")
    assert len(a) == 50 and a["corretiva"].isna().all()
    assert "heuristica" not in " ".join(a.columns).lower()
    assert a["url_comparacao"].str.contains("/compare/").all()
    assert len(pd.read_csv(tmp_path / "rotulos_p_repos.csv")) == 10
