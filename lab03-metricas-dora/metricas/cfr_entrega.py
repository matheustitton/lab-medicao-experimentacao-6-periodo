"""RQ03 (b) - change failure rate por releases (proxy de entrega)."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Iterable, Optional

from .modelos import Release


@dataclass(frozen=True)
class ResultadoCFREntrega:
    avaliadas: int
    falhas: int
    censuradas: int
    taxa: Optional[float]


def cfr_entrega(
    releases: Iterable[Release],
    janela_fim: datetime,
    eh_corretiva: Callable[[Release], bool],
    dias: int = 7,
) -> ResultadoCFREntrega:
    """Release R falha se alguma release corretiva sai em até `dias` dias depois dela.
    Releases dos últimos `dias` dias da janela são censuradas (fora do denominador)."""
    principais = sorted((r for r in releases if not r.prerelease), key=lambda r: r.publicada_em)
    avaliadas = falhas = censuradas = 0
    for i, r in enumerate(principais):
        if r.publicada_em > janela_fim - timedelta(days=dias):
            censuradas += 1
            continue
        avaliadas += 1
        limite = r.publicada_em + timedelta(days=dias)
        seguintes = (s for s in principais[i + 1:] if s.publicada_em <= limite)
        if any(eh_corretiva(s) for s in seguintes):
            falhas += 1
    return ResultadoCFREntrega(avaliadas, falhas, censuradas, falhas / avaliadas if avaliadas else None)
