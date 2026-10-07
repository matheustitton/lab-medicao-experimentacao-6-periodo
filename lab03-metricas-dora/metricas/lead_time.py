"""RQ02 - lead time for changes, variantes (a) por release e (b) por commit."""
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .modelos import Release
from .tempo import horas, mediana


def lead_time_release_horas(release: Release) -> Optional[float]:
    """(a) data da release - data do commit mais antigo nela. None se não há commits."""
    if not release.commits:
        return None
    return horas(release.publicada_em - min(c.data for c in release.commits))


def lead_times_commits_horas(release: Release) -> List[float]:
    """(b) um valor por commit: data da release - data do commit."""
    return [horas(release.publicada_em - c.data) for c in release.commits]


@dataclass(frozen=True)
class ResultadoLeadTime:
    a_mediana_h: Optional[float]
    b_mediana_h: Optional[float]
    n_releases_usadas: int
    n_commits: int
    n_sem_anterior: int
    n_indisponiveis: int
    n_sem_commits: int
    n_negativos: int
    n_truncadas: int


def lead_time_repo(releases: Iterable[Release]) -> ResultadoLeadTime:
    por_release: List[float] = []
    por_commit: List[float] = []
    sem_anterior = indisponiveis = sem_commits = truncadas = 0
    for r in releases:
        if r.prerelease:
            continue
        if r.status_compare == "sem_anterior":
            sem_anterior += 1
            continue
        if r.status_compare in ("indisponivel", "nao_coletado"):
            indisponiveis += 1
            continue
        if not r.commits:
            sem_commits += 1
            continue
        if r.status_compare == "truncado":
            truncadas += 1
        por_release.append(lead_time_release_horas(r))
        por_commit.extend(lead_times_commits_horas(r))
    negativos = sum(1 for v in por_commit if v < 0)
    return ResultadoLeadTime(
        a_mediana_h=mediana(por_release),
        b_mediana_h=mediana(por_commit),
        n_releases_usadas=len(por_release),
        n_commits=len(por_commit),
        n_sem_anterior=sem_anterior,
        n_indisponiveis=indisponiveis,
        n_sem_commits=sem_commits,
        n_negativos=negativos,
        n_truncadas=truncadas,
    )
