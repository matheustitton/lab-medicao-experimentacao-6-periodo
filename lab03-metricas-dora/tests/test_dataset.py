import pandas as pd

from pipeline.dataset import gerar_dataset, linha_dataset
from pipeline.dicionario import COLUNAS, DICIONARIO, markdown
from pipeline.estado import RepoStore
from pipeline.orquestrador import executar
from tests.fakes import ClienteFalso
from tests.github_falso import JANELA, cfg_teste, github_falso


def test_dataset_ponta_a_ponta(tmp_path):
    cfg, store = cfg_teste(tmp_path), RepoStore(":memory:")
    executar(cfg, ClienteFalso(github_falso), store, etapa="todas")
    df = pd.read_csv(tmp_path / "saida" / "dataset_dora.csv")
    assert list(df.columns) == COLUNAS and len(df) == 1
    linha = df.iloc[0]
    assert linha["n_releases"] == 6 and linha["contribuidores"] == 17
    assert linha["n_runs_falha"] == 2 and linha["n_runs_sucesso"] == 58 and linha["n_runs_ignorados"] == 11
    assert linha["n_episodios"] == 1 and linha["n_episodios_censurados"] == 0
    assert linha["n_releases_falha"] == 1 and linha["n_releases_avaliadas"] == 6   # v1.2.0 foi seguida por v1.2.1 (fix)
    assert (tmp_path / "saida" / "funil_selecao.md").exists()
    assert (tmp_path / "saida" / "dicionario_dados.csv").exists()


def coleta_minima():
    return {
        "meta": {"repo": "o/r", "estrelas": 1500, "linguagem": None, "criado_em": "2020-10-01T00:00:00Z",
                 "default_branch": "main", "contribuidores": None},
        "releases": [
            {"tag": "v1.0.0", "publicada_em": "2026-01-01T00:00:00Z", "prerelease": False, "anterior_tag": None,
             "status_compare": "sem_anterior", "total_commits": 0, "commits": []},
            {"tag": "v1.1.0", "publicada_em": "2026-01-10T00:00:00Z", "prerelease": False, "anterior_tag": "v1.0.0",
             "status_compare": "ok", "total_commits": 1,
             "commits": [{"sha": "a", "data": "2026-01-09T00:00:00Z", "msg": "feat", "merge": False}]}],
        "runs": [{"workflow_id": 1, "conclusao": "success", "iniciada_em": "2026-01-01T00:00:00Z",
                  "atualizada_em": "2026-01-01T00:05:00Z"}],
        "runs_ignorados": 3, "teto_runs_atingido": False,
    }


def test_linha_dataset_tem_exatamente_as_colunas_do_dicionario():
    linha = linha_dataset(coleta_minima(), JANELA)
    assert list(linha) == COLUNAS
    assert linha["lead_time_a_h"] == 24 and linha["cfr_ci"] == 0.0 and linha["recuperacao_h"] is None
    assert linha["n_releases_sem_anterior"] == 1 and linha["classe_dora_c1"] in {"Elite", "High", "Medium", "Low"}


def test_dicionario_completo_e_sem_duplicatas():
    assert len(COLUNAS) == len(set(COLUNAS)) and all(len(l) == 5 and all(l) for l in DICIONARIO)
    texto = markdown()
    assert all(f"`{c}`" in texto for c in COLUNAS)


def test_gerar_dataset_vazio_mantem_cabecalho(tmp_path):
    df = gerar_dataset(RepoStore(":memory:"), cfg_teste(tmp_path))
    assert list(df.columns) == COLUNAS and df.empty
