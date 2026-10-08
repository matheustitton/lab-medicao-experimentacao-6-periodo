"""RQ04 - tempo de recuperação após falha de CI, por episódio e por workflow."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

from .cfr import classificar_conclusao
from .modelos import Execucao
from .tempo import horas, mediana


@dataclass(frozen=True)
class Episodio:
    workflow_id: int
    inicio: datetime
    fim: Optional[datetime]      # None = censurado (nunca recuperou na janela)


@dataclass(frozen=True)
class ResultadoRecuperacao:
    n_episodios: int
    n_censurados: int
    prop_censurados: Optional[float]
    mediana_h: Optional[float]               # só episódios concluídos
    mediana_h_com_censura: Optional[float]   # censurados entram como limite inferior


def episodios(execucoes: Iterable[Execucao]) -> List[Episodio]:
    """Episódio: primeira falha APÓS um sucesso até o próximo sucesso do mesmo workflow.
    Execuções ignoradas (cancelled etc.) não quebram nem encerram episódios."""
    por_workflow = defaultdict(list)
    for e in execucoes:
        por_workflow[e.workflow_id].append(e)
    saida: List[Episodio] = []
    for wid, runs in por_workflow.items():
        runs.sort(key=lambda e: (e.iniciada_em, e.atualizada_em))
        viu_sucesso = False
        inicio: Optional[datetime] = None
        for e in runs:
            c = classificar_conclusao(e.conclusao)
            if c is None:
                continue
            if c == "falha":
                if viu_sucesso and inicio is None:
                    inicio = e.iniciada_em
            else:
                viu_sucesso = True
                if inicio is not None:
                    saida.append(Episodio(wid, inicio, e.atualizada_em))
                    inicio = None
        if inicio is not None:
            saida.append(Episodio(wid, inicio, None))
    return saida


def tempo_recuperacao(execucoes: Iterable[Execucao], janela_fim: datetime) -> ResultadoRecuperacao:
    eps = episodios(execucoes)
    concluidos = [horas(e.fim - e.inicio) for e in eps if e.fim is not None]
    censurados = [horas(janela_fim - e.inicio) for e in eps if e.fim is None]
    n = len(eps)
    return ResultadoRecuperacao(
        n_episodios=n,
        n_censurados=len(censurados),
        prop_censurados=len(censurados) / n if n else None,
        mediana_h=mediana(concluidos),
        mediana_h_com_censura=mediana(concluidos + censurados),
    )
