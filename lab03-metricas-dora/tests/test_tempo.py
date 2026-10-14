from datetime import timedelta, timezone

import pytest

from metricas.tempo import horas, mediana, parse_data


def test_parse_data_converte_para_utc():
    assert parse_data("2025-03-15T10:00:00Z").tzinfo == timezone.utc
    assert parse_data("2025-03-15T10:00:00-03:00").hour == 13          # convertido para UTC
    assert parse_data("2025-03-15T10:00:00").tzinfo == timezone.utc    # sem fuso = UTC


def test_horas_e_mediana():
    assert horas(timedelta(days=1, hours=12)) == 36
    assert mediana([3, 1, 2]) == 2 and mediana([1, 2, 3, 4]) == 2.5
    assert mediana([]) is None
