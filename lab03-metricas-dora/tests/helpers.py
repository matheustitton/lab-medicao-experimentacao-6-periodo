"""Construtores de dados de teste (dependem só de metricas)."""
from datetime import datetime

from metricas.modelos import Commit, Execucao, Release
from metricas.tempo import parse_data


def d(texto: str) -> datetime:
    """d('2025-03-15') ou d('2025-03-15T10:30')."""
    return parse_data(texto if "T" in texto else texto + "T00:00:00Z")


def release(tag, quando, anterior=None, commits=(), status="ok", pre=False) -> Release:
    return Release(tag, d(quando), anterior, tuple(commits), status, pre)


def commit(quando, msg="feat: algo", sha="x") -> Commit:
    return Commit(sha, d(quando), msg)


def execucao(wf, conclusao, inicio, fim=None) -> Execucao:
    return Execucao(wf, conclusao, d(inicio), d(fim or inicio))
