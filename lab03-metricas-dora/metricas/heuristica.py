"""Heurísticas automáticas para identificar release corretiva (RQ03 b).

Cada versão recebe uma Release (com anterior_tag e commits) e devolve True/False.
Novas versões entram no dicionário HEURISTICAS; a avaliação contra a amostra-ouro
(validacao.avaliacao_heuristica) calcula precisão/recall/F1 de todas elas.
"""
import re
from typing import Callable, Dict, Optional, Tuple

from .modelos import Release

RE_VERSAO = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?")
RE_CORRECAO = re.compile(r"\b(revert|hotfix|fix(?:es|ed)?)\b", re.IGNORECASE)


def parse_versao(tag: Optional[str]) -> Optional[Tuple[int, int, int]]:
    if not tag:
        return None
    m = RE_VERSAO.search(tag)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)


def eh_patch_bump(release: Release) -> bool:
    """Mesma MAJOR.MINOR da release anterior e PATCH maior (2.3.0 -> 2.3.1)."""
    atual, anterior = parse_versao(release.tag), parse_versao(release.anterior_tag)
    if not atual or not anterior:
        return False
    return atual[:2] == anterior[:2] and atual[2] > anterior[2]


def n_commits_correcao(release: Release) -> int:
    return sum(1 for c in release.commits if RE_CORRECAO.search(c.mensagem or ""))


def v1(release: Release) -> bool:
    """Baseline do enunciado: bump de patch OU commit com revert/hotfix/fix."""
    return eh_patch_bump(release) or n_commits_correcao(release) > 0


def v2(release: Release) -> bool:
    """Conservadora: bump de patch E ao menos um commit de correção."""
    return eh_patch_bump(release) and n_commits_correcao(release) > 0


def v3(release: Release) -> bool:
    """Patch pequeno ou com correção; minor/major só se a maioria dos commits for correção."""
    n, corr = len(release.commits), n_commits_correcao(release)
    if eh_patch_bump(release):
        return n == 0 or corr > 0 or n <= 5
    return n > 0 and corr / n >= 0.5


# --- v4 e v5: refinadas contra o consenso da amostra-ouro (ver docs/HISTORICO_HEURISTICA.md) ---
RE_CORRECAO_FORTE = re.compile(r"\b(revert|hotfix|bugfix|fix(?:es|ed)?|regression|crash)\b", re.IGNORECASE)
RE_RUIDO_DEPENDENCIA = re.compile(r"\b(bump|deps|dependabot|dependenc)", re.IGNORECASE)
PEQUENA = 2            # releases com até 2 commits úteis
FRACAO_CORRECAO = 0.3  # ou com >= 30% de commits de correção
GAP_DIAS = 2           # v5: correção que sai até 2 dias depois da release anterior


def _commits_uteis(release: Release):
    """Ignora commits de merge: eles repetem o conteúdo da branch mesclada."""
    return [c for c in release.commits if not (c.mensagem or "").lower().startswith("merge")]


def n_correcao_util(release: Release) -> int:
    """Commits de correção que não são só atualização de dependência (fix(deps), bump...)."""
    return sum(1 for c in _commits_uteis(release)
               if RE_CORRECAO_FORTE.search(c.mensagem or "") and not RE_RUIDO_DEPENDENCIA.search(c.mensagem or ""))


def v4(release: Release) -> bool:
    """Patch com correção (ou muito pequeno), ou release em que >= 30% dos commits corrigem algo.
    Ignora merges e commits de dependência. F1 na amostra-ouro: ver HISTORICO_HEURISTICA."""
    n, corr = len(_commits_uteis(release)), n_correcao_util(release)
    patch_corretivo = eh_patch_bump(release) and (corr >= 1 or n <= PEQUENA)
    return patch_corretivo or (n >= 1 and corr / n >= FRACAO_CORRECAO)


def v5(release: Release) -> bool:
    """v4 + correção que sai logo (<= 2 dias) depois da release anterior."""
    if v4(release):
        return True
    if release.anterior_publicada_em is None or n_correcao_util(release) < 1:
        return False
    return (release.publicada_em - release.anterior_publicada_em).total_seconds() <= GAP_DIAS * 86400


HEURISTICAS: Dict[str, Callable[[Release], bool]] = {"v1": v1, "v2": v2, "v3": v3, "v4": v4, "v5": v5}


def obter_heuristica(nome: str) -> Callable[[Release], bool]:
    try:
        return HEURISTICAS[nome]
    except KeyError:
        raise ValueError(f"heurística desconhecida: {nome}. Disponíveis: {sorted(HEURISTICAS)}")
