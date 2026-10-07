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


HEURISTICAS: Dict[str, Callable[[Release], bool]] = {"v1": v1, "v2": v2, "v3": v3}


def obter_heuristica(nome: str) -> Callable[[Release], bool]:
    try:
        return HEURISTICAS[nome]
    except KeyError:
        raise ValueError(f"heurística desconhecida: {nome}. Disponíveis: {sorted(HEURISTICAS)}")
