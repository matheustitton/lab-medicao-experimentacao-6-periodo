"""Utilidades de tempo e estatística simples usadas pelas métricas."""
import statistics
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional


def parse_data(texto: str) -> datetime:
    """ISO 8601 (com 'Z') -> datetime com fuso UTC."""
    dt = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def horas(delta: timedelta) -> float:
    return delta.total_seconds() / 3600


def mediana(valores: Iterable[float]) -> Optional[float]:
    valores = list(valores)
    return statistics.median(valores) if valores else None
