"""RQ03 (a) - change failure rate por workflow runs (proxy de CI)."""
from dataclasses import dataclass
from typing import Iterable, Optional

from .modelos import Execucao

SUCESSO = {"success"}
FALHA = {"failure", "timed_out", "startup_failure"}


def classificar_conclusao(conclusao: Optional[str]) -> Optional[str]:
    """'sucesso' | 'falha' | None (ignorar: cancelled, skipped, vazio...)."""
    if conclusao in SUCESSO:
        return "sucesso"
    if conclusao in FALHA:
        return "falha"
    return None


@dataclass(frozen=True)
class ResultadoCFRCI:
    falhas: int
    sucessos: int
    ignoradas: int
    taxa: Optional[float]


def cfr_ci(execucoes: Iterable[Execucao]) -> ResultadoCFRCI:
    falhas = sucessos = ignoradas = 0
    for e in execucoes:
        c = classificar_conclusao(e.conclusao)
        if c == "falha":
            falhas += 1
        elif c == "sucesso":
            sucessos += 1
        else:
            ignoradas += 1
    total = falhas + sucessos
    return ResultadoCFRCI(falhas, sucessos, ignoradas, falhas / total if total else None)
