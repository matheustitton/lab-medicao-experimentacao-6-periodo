"""Classificação DORA (Elite/High/Medium/Low) com os cortes fixos da disciplina."""
import math
import statistics
from dataclasses import dataclass
from typing import Dict, Optional

PONTOS = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1}
NOME_POR_PONTO = {v: k for k, v in PONTOS.items()}
UMA_POR_MES_EM_SEMANAS = 12 / (365 / 7)   # ≈ 0,23 release/semana


def classificar_frequencia(por_semana: Optional[float]) -> Optional[str]:
    if por_semana is None:
        return None
    if por_semana >= 7:
        return "Elite"
    if por_semana >= 1:
        return "High"
    if por_semana >= UMA_POR_MES_EM_SEMANAS:
        return "Medium"
    return "Low"


def classificar_lead_time(horas: Optional[float]) -> Optional[str]:
    if horas is None:
        return None
    if horas < 24:
        return "Elite"
    if horas < 7 * 24:
        return "High"
    if horas < 30 * 24:
        return "Medium"
    return "Low"


def classificar_cfr(taxa: Optional[float]) -> Optional[str]:
    if taxa is None:
        return None
    if taxa <= 0.15:
        return "Elite"
    if taxa <= 0.30:
        return "High"
    if taxa <= 0.45:
        return "Medium"
    return "Low"


def classificar_recuperacao(horas: Optional[float]) -> Optional[str]:
    if horas is None:
        return None
    if horas < 1:
        return "Elite"
    if horas < 24:
        return "High"
    if horas < 7 * 24:
        return "Medium"
    return "Low"


@dataclass(frozen=True)
class ClasseRepositorio:
    por_metrica: Dict[str, Optional[str]]
    n_metricas: int
    geral: Optional[str]


def classificar_repositorio(freq, lead_h, cfr, recuperacao_h) -> ClasseRepositorio:
    """Pontos 4/3/2/1 por métrica; geral = mediana arredondada para baixo.
    Métricas sem valor (None) ficam de fora da mediana."""
    por_metrica = {
        "frequencia": classificar_frequencia(freq),
        "lead_time": classificar_lead_time(lead_h),
        "cfr": classificar_cfr(cfr),
        "recuperacao": classificar_recuperacao(recuperacao_h),
    }
    pontos = [PONTOS[c] for c in por_metrica.values() if c is not None]
    geral = NOME_POR_PONTO[math.floor(statistics.median(pontos))] if pontos else None
    return ClasseRepositorio(por_metrica, len(pontos), geral)
