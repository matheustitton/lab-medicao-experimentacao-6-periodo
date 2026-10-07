"""RQ01 - deployment frequency (releases por semana)."""
from datetime import datetime
from typing import Iterable

from .modelos import Release


def frequencia_deploys(releases: Iterable[Release], inicio: datetime, fim: datetime) -> float:
    semanas = (fim - inicio).total_seconds() / (7 * 86400)
    if semanas <= 0:
        raise ValueError("janela inválida")
    n = sum(1 for r in releases if not r.prerelease and inicio <= r.publicada_em <= fim)
    return n / semanas
