"""Cache de respostas da API em SQLite: permite retomar a coleta sem repetir chamadas."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode


def chave_requisicao(caminho: str, params: Optional[Dict[str, Any]] = None) -> str:
    return caminho + "?" + urlencode(sorted((params or {}).items()))


class Cache:
    def __init__(self, caminho: str = "data/cache.sqlite"):
        if caminho != ":memory:":
            os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
        self.con = sqlite3.connect(caminho, timeout=30)
        self.con.execute(
            "CREATE TABLE IF NOT EXISTS respostas ("
            "chave TEXT PRIMARY KEY, status INTEGER NOT NULL, corpo TEXT NOT NULL, "
            "links TEXT NOT NULL, criado_em TEXT NOT NULL)"
        )
        self.con.commit()

    def obter(self, chave: str) -> Optional[Tuple[int, Any, Dict[str, str]]]:
        linha = self.con.execute(
            "SELECT status, corpo, links FROM respostas WHERE chave = ?", (chave,)
        ).fetchone()
        if linha is None:
            return None
        return linha[0], json.loads(linha[1]), json.loads(linha[2])

    def salvar(self, chave: str, status: int, dados: Any, links: Dict[str, str]) -> None:
        self.con.execute(
            "INSERT OR REPLACE INTO respostas VALUES (?, ?, ?, ?, ?)",
            (chave, status, json.dumps(dados), json.dumps(links),
             datetime.now(timezone.utc).isoformat()),
        )
        self.con.commit()

    def total(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM respostas").fetchone()[0]
