"""Estado de cada repositório (candidato -> ... -> amostra final) e funil de seleção."""
import hashlib
import json
import os
import sqlite3
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

ETAPAS = [
    "candidatos (busca por estrelas)",
    "usam GitHub Actions",
    "≥ 5 releases na janela",
    "≥ 50 workflow runs válidos",
    "amostra final (coleta completa)",
]
ETAPA_FINAL = len(ETAPAS) - 1


class RepoStore:
    def __init__(self, caminho: str = "data/estado.sqlite"):
        if caminho != ":memory:":
            os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
        self.con = sqlite3.connect(caminho, timeout=30)
        self.con.execute(
            "CREATE TABLE IF NOT EXISTS repos ("
            "repo TEXT PRIMARY KEY, meta TEXT NOT NULL, etapa INTEGER NOT NULL DEFAULT 0, "
            "motivo TEXT, coleta TEXT)"
        )
        self.con.commit()

    def adicionar_candidatos(self, metas: List[Dict[str, Any]]) -> int:
        antes = self.total()
        self.con.executemany(
            "INSERT OR IGNORE INTO repos (repo, meta) VALUES (?, ?)",
            [(m["repo"], json.dumps(m)) for m in metas],
        )
        self.con.commit()
        return self.total() - antes

    def total(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM repos").fetchone()[0]

    def pendentes(self, semente: int) -> List[Dict[str, Any]]:
        """Candidatos ainda sem decisão, em ordem pseudoaleatória reprodutível."""
        linhas = self.con.execute(
            "SELECT repo, meta FROM repos WHERE motivo IS NULL AND etapa < ?", (ETAPA_FINAL,)
        ).fetchall()
        linhas.sort(key=lambda l: hashlib.sha256(f"{semente}:{l[0]}".encode()).hexdigest())
        return [json.loads(m) for _, m in linhas]

    def avancar(self, repo: str, etapa: int) -> None:
        self.con.execute("UPDATE repos SET etapa = ? WHERE repo = ?", (etapa, repo))
        self.con.commit()

    def descartar(self, repo: str, motivo: str) -> None:
        self.con.execute("UPDATE repos SET motivo = ? WHERE repo = ?", (motivo, repo))
        self.con.commit()

    def salvar_coleta(self, repo: str, coleta: Dict[str, Any]) -> None:
        self.con.execute(
            "UPDATE repos SET coleta = ?, etapa = ? WHERE repo = ?",
            (json.dumps(coleta), ETAPA_FINAL, repo),
        )
        self.con.commit()

    def contar_incluidos(self) -> int:
        return self.con.execute(
            "SELECT COUNT(*) FROM repos WHERE etapa = ? AND motivo IS NULL", (ETAPA_FINAL,)
        ).fetchone()[0]

    def incluidos(self) -> List[Tuple[str, Dict[str, Any]]]:
        linhas = self.con.execute(
            "SELECT repo, coleta FROM repos WHERE etapa = ? AND motivo IS NULL ORDER BY repo",
            (ETAPA_FINAL,),
        ).fetchall()
        return [(r, json.loads(c)) for r, c in linhas]

    def coleta_de(self, repo: str) -> Optional[Dict[str, Any]]:
        linha = self.con.execute("SELECT coleta FROM repos WHERE repo = ?", (repo,)).fetchone()
        return json.loads(linha[0]) if linha and linha[0] else None

    # ------------------------------------------------------------------ funil
    def funil(self) -> List[Tuple[str, int]]:
        """Quantos repositórios chegaram a cada etapa (os descartados contam até onde passaram)."""
        etapas = [r[0] for r in self.con.execute("SELECT etapa FROM repos")]
        return [(nome, sum(1 for e in etapas if e >= i)) for i, nome in enumerate(ETAPAS)]

    def descartes(self) -> Dict[str, int]:
        c = Counter(r[0] for r in self.con.execute(
            "SELECT motivo FROM repos WHERE motivo IS NOT NULL"))
        return dict(c)


def funil_markdown(store: RepoStore) -> str:
    linhas = ["| Etapa | Repositórios |", "|---|---|"]
    linhas += [f"| {nome} | {n} |" for nome, n in store.funil()]
    desc = store.descartes()
    if desc:
        linhas += ["", "| Motivo de descarte | Repositórios |", "|---|---|"]
        linhas += [f"| {m} | {n} |" for m, n in sorted(desc.items())]
    return "\n".join(linhas)
