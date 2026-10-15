"""Fluxo completo da validação manual pelos comandos reais: amostra -> rótulos -> kappa -> F1."""
import sys

import pandas as pd
import pytest

from pipeline.estado import RepoStore
from validacao import amostra, avaliacao_heuristica, concordancia

REPOS = [f"o/r{i}" for i in range(6)]
AVALIADORES = ["matheus", "pedro", "murilo"]


def coleta_repo():
    """5 releases principais com anterior; v1.0.1 e v1.2.1 são correções reais."""
    def rel(tag, mes, dia, anterior, msg):
        return {"tag": tag, "publicada_em": f"2026-{mes:02d}-{dia:02d}T12:00:00Z", "prerelease": False,
                "anterior_tag": anterior, "status_compare": "ok", "total_commits": 1,
                "commits": [{"sha": tag, "data": f"2026-{mes:02d}-{dia:02d}T00:00:00Z", "msg": msg}]}
    return {"releases": [
        rel("v1.0.0", 1, 10, "v0.9.0", "feat: a"), rel("v1.0.1", 1, 12, "v1.0.0", "fix: crash"),
        rel("v1.1.0", 3, 1, "v1.0.1", "feat: b"), rel("v1.2.0", 5, 1, "v1.1.0", "feat: c"),
        rel("v1.2.1", 5, 3, "v1.2.0", "fix: regressao"), rel("v1.3.0", 7, 1, "v1.2.1", "feat: d")]}


@pytest.fixture
def ambiente(tmp_path):
    saida, rotulos = tmp_path / "saida", tmp_path / "rotulos"
    saida.mkdir()
    store = RepoStore(str(tmp_path / "estado.sqlite"))
    store.adicionar_candidatos([{"repo": r} for r in REPOS])
    for r in REPOS:
        store.salvar_coleta(r, coleta_repo())
    cfg = tmp_path / "config.yaml"
    cfg.write_text(f"""
janela: {{inicio: "2026-01-01", fim: "2026-12-31"}}
caminho_estado: {tmp_path / 'estado.sqlite'}
saida_dir: {saida}
rotulos_dir: {rotulos}
amostra_ouro_n: 4
releases_por_repo_ouro: 3
""", encoding="utf-8")
    return cfg, saida, rotulos


def rodar(monkeypatch, modulo, cfg):
    monkeypatch.setattr(sys, "argv", ["x", "--config", str(cfg)])
    modulo.main()


def preencher(rotulos, divergir_tipo):
    corretivas = {"v1.0.1", "v1.2.1"}
    for nome in AVALIADORES:
        repos = pd.read_csv(rotulos / f"rotulos_{nome}_repos.csv", dtype=str)
        repos["tipo_projeto"] = "biblioteca_framework"
        repos["releases_entregas_reais"] = "sim"
        if divergir_tipo:       # 1º repositório: cada avaliador escolhe um tipo diferente (1-1-1)
            repos.loc[0, "tipo_projeto"] = {"matheus": "cli", "pedro": "outro", "murilo": "aplicacao_servico"}[nome]
        repos.to_csv(rotulos / f"rotulos_{nome}_repos.csv", index=False)
        rels = pd.read_csv(rotulos / f"rotulos_{nome}_releases.csv", dtype=str)
        rels["corretiva"] = rels["tag"].map(lambda t: "sim" if t in corretivas else "nao")
        rels.to_csv(rotulos / f"rotulos_{nome}_releases.csv", index=False)


def test_fluxo_completo_planilhas_kappa_desempate_e_f1(monkeypatch, ambiente):
    cfg, saida, rotulos = ambiente
    rodar(monkeypatch, amostra, cfg)
    assert len(pd.read_csv(rotulos / "rotulos_matheus_repos.csv")) == 4
    assert len(pd.read_csv(rotulos / "amostra_ouro_releases.csv")) == 4 * 3

    preencher(rotulos, divergir_tipo=True)
    rodar(monkeypatch, concordancia, cfg)
    kappas = pd.read_csv(saida / "kappa_fleiss.csv")
    assert set(kappas["dimensao"]) == {"tipo_projeto", "releases_entregas_reais", "corretiva"}
    pendentes = pd.read_csv(rotulos / "consenso_pendentes.csv")
    assert len(pendentes) == 1 and pendentes.iloc[0]["dimensao"] == "tipo_projeto"

    pd.DataFrame([{"nivel": "repos", "chave": pendentes.iloc[0]["chave"], "dimensao": "tipo_projeto",
                   "rotulo_final": "cli"}]).to_csv(rotulos / "desempate_reuniao.csv", index=False)
    rodar(monkeypatch, concordancia, cfg)
    assert pd.read_csv(rotulos / "consenso_pendentes.csv").empty
    assert len(pd.read_csv(rotulos / "consenso.csv")) == 4 + 4 + 12     # 2 dimensões de repo + corretiva

    rodar(monkeypatch, avaliacao_heuristica, cfg)
    t = pd.read_csv(saida / "avaliacao_heuristica.csv").set_index("versao")
    assert list(t.index)[:3] == ["v1", "v2", "v3"] and (t["n"] == 12).all()
    assert t.loc["v1", "f1"] == 1.0           # fix: => corretiva; o resto são feat e minor bumps


def test_rotulos_incompletos_travam_o_kappa(monkeypatch, ambiente):
    cfg, _, rotulos = ambiente
    rodar(monkeypatch, amostra, cfg)          # planilhas vazias
    with pytest.raises(ValueError, match="vazios ou inválidos"):
        rodar(monkeypatch, concordancia, cfg)
