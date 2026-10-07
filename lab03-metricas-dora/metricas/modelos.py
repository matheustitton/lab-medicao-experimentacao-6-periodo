"""Tipos de dados usados por todas as métricas."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass(frozen=True)
class Commit:
    sha: str
    data: datetime              # commit.author.date
    mensagem: str = ""          # primeira linha


@dataclass(frozen=True)
class Release:
    tag: str
    publicada_em: datetime
    anterior_tag: Optional[str] = None
    commits: Tuple[Commit, ...] = ()
    # ok | sem_anterior | indisponivel | truncado | nao_coletado
    status_compare: str = "ok"
    prerelease: bool = False


@dataclass(frozen=True)
class Execucao:
    workflow_id: int
    conclusao: Optional[str]
    iniciada_em: datetime       # run_started_at
    atualizada_em: datetime     # updated_at
