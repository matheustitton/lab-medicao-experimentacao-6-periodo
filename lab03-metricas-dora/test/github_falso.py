"""GitHub simulado para testes ponta a ponta (3 repositórios: ok, sem Actions, poucas releases)."""
import pandas as pd

from metricas.tempo import parse_data
from pipeline.config import Config, Janela
from tests.helpers import d

JANELA = Janela(d("2025-10-01"), d("2026-09-30T23:59:59"))
RELEASES_OK = [
    ("v0.9.0", "2025-06-01", False, False), ("v1.0.0", "2025-11-01", False, False),
    ("v1.1.0", "2025-12-01", False, False), ("v1.2.0", "2026-01-01", False, False),
    ("v1.2.1", "2026-01-03", False, False), ("v1.3.0", "2026-03-01", False, False),
    ("v1.4.0", "2026-05-01", False, False), ("v1.5.0", "2026-06-01", True, False),   # rascunho
    ("v2.0.0-rc1", "2026-06-02", False, True),
]


def github_falso(caminho, params):
    if caminho == "/search/repositories":
        itens = [{"full_name": n, "stargazers_count": 2000, "language": "Python", "default_branch": "main",
                  "created_at": "2019-01-01T00:00:00Z"} for n in ("a/ok", "b/sem-actions", "c/poucas-releases")]
        return 200, {"total_count": 3, "items": itens}
    repo = caminho.split("/")[2] + "/" + caminho.split("/")[3] if caminho.startswith("/repos/") else ""
    if caminho.endswith("/actions/workflows"):
        return 200, {"total_count": 0 if repo.startswith("b/") else 1}
    if caminho.endswith("/releases"):
        if repo.startswith("c/"):
            return 200, [{"tag_name": "v1", "draft": False, "prerelease": False, "published_at": "2026-01-01T00:00:00Z"}]
        return 200, [{"tag_name": t, "draft": dr, "prerelease": pre, "published_at": q + "T12:00:00Z"}
                     for t, q, dr, pre in RELEASES_OK]
    if "/compare/" in caminho:
        msg = "fix: crash" if caminho.endswith("...v1.2.1") else "feat: algo"
        return 200, {"total_commits": 1, "commits": [
            {"sha": "abc", "commit": {"author": {"date": "2025-10-01T00:00:00Z"}, "message": msg}, "parents": [{}]}]}
    if caminho.endswith("/actions/runs"):
        if params["per_page"] == 1:
            return 200, {"total_count": 60}
        ini = parse_data(params["created"].split("..")[0])
        conclusoes = ["success", "failure", "failure", "success", "success"] if ini.month == 1 else ["success"] * 5 + ["cancelled"]
        runs = []
        for k, c in enumerate(conclusoes):
            t = (ini + pd.Timedelta(hours=k + 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            runs.append({"workflow_id": 7, "conclusion": c, "event": "push", "created_at": t,
                         "run_started_at": t, "updated_at": t})
        return 200, {"total_count": len(runs), "workflow_runs": runs}
    if caminho.endswith("/contributors"):
        return 200, [{}], {"last": "https://api.github.com/x/contributors?per_page=1&anon=true&page=17"}
    raise AssertionError(f"chamada inesperada: {caminho} {params}")


def cfg_teste(tmp_path):
    return Config(janela=JANELA, faixas_estrelas=["1000..2999"], alvo_amostra=10,
                  saida_dir=str(tmp_path / "saida"), heuristica="v1")


