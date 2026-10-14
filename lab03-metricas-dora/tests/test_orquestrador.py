import pandas as pd

from pipeline.estado import RepoStore
from pipeline.orquestrador import executar
from tests.fakes import ClienteFalso
from tests.github_falso import cfg_teste, github_falso


def rodar(cfg, client, store):
    executar(cfg, client, store, etapa="selecao")
    executar(cfg, client, store, etapa="coleta")


def test_pipeline_coleta_funil_e_retomada(tmp_path):
    cfg, store, client = cfg_teste(tmp_path), RepoStore(":memory:"), ClienteFalso(github_falso)
    rodar(cfg, client, store)
    assert [n for _, n in store.funil()] == [3, 2, 1, 1, 1]
    assert store.descartes() == {"sem_actions": 1, "releases_insuficientes": 1}
    assert [r for r, _ in store.incluidos()] == ["a/ok"]
    coleta = store.coleta_de("a/ok")
    assert coleta["meta"]["contribuidores"] == 17 and len(coleta["runs"]) == 60
    assert coleta["runs_ignorados"] == 11 and coleta["teto_runs_atingido"] is False
    tags = [r["tag"] for r in coleta["releases"]]
    assert tags[0] == "v1.0.0" and "v0.9.0" not in tags and "v1.5.0" not in tags   # fora da janela / rascunho
    assert coleta["releases"][0]["anterior_tag"] == "v0.9.0"                       # anterior fora da janela é mantida
    chamadas = len(client.chamadas)
    rodar(cfg, client, store)              # segunda execução: nada pendente, nenhuma chamada nova
    assert len(client.chamadas) == chamadas


def test_alvo_para_a_coleta_cedo(tmp_path):
    cfg, store = cfg_teste(tmp_path), RepoStore(":memory:")
    cfg.alvo_amostra = 1
    rodar(cfg, ClienteFalso(github_falso), store)
    assert store.contar_incluidos() == 1
