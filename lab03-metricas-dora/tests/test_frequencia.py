import pytest

from metricas.frequencia import frequencia_deploys
from tests.helpers import d, release


def test_frequencia_releases_por_semana():
    rels = [release(f"v{i}", "2025-02-01") for i in range(52)] + [release("rc", "2025-02-01", pre=True)]
    f = frequencia_deploys(rels, d("2025-01-01"), d("2025-12-31"))
    assert f == pytest.approx(52 / (364 / 7))      # pré-release não conta


def test_frequencia_ignora_fora_da_janela_e_valida_janela():
    rels = [release("a", "2024-12-31"), release("b", "2025-06-01")]
    assert frequencia_deploys(rels, d("2025-01-01"), d("2025-01-08")) == 0
    assert frequencia_deploys(rels, d("2025-01-01"), d("2025-12-31")) > 0
    with pytest.raises(ValueError):
        frequencia_deploys(rels, d("2025-02-01"), d("2025-01-01"))
