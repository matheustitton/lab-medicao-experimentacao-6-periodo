"""Fixtures do pytest: dados pequenos montados à mão, com resultado conhecido do enunciado (seção 5)."""
import pytest

from tests.helpers import commit, d, execucao, release


@pytest.fixture
def janela_fim():
    return d("2025-12-31")


@pytest.fixture
def release_v11():
    """Exemplo da RQ02: v1.1 publicada em 15/03 com commits de 02/03, 10/03 e 14/03."""
    return release("v1.1", "2025-03-15", "v1.0",
                   [commit("2025-03-02"), commit("2025-03-10"), commit("2025-03-14")])


@pytest.fixture
def historia_cfr():
    """Exemplo da RQ03(b): v2.3.0 falha (v2.3.1 com fix em 2 dias); v2.4.0 não falha."""
    return [
        release("v2.3.0", "2025-05-10", None, [commit("2025-05-01", "feat: x")]),
        release("v2.3.1", "2025-05-12", "v2.3.0", [commit("2025-05-11", "fix: crash ao abrir arquivo")]),
        release("v2.4.0", "2025-06-01", "v2.3.1", [commit("2025-05-20", "feat: y")]),
        release("v2.5.0", "2025-06-20", "v2.4.0", [commit("2025-06-10", "feat: z")]),
    ]


@pytest.fixture
def runs_episodio():
    """Exemplo da RQ04: sucesso 09:00, falhas 10:00 e 10:30, sucesso 11:15 (termina 11:20) = 1h20."""
    return [
        execucao(1, "success", "2025-05-01T09:00", "2025-05-01T09:05"),
        execucao(1, "failure", "2025-05-01T10:00", "2025-05-01T10:05"),
        execucao(1, "failure", "2025-05-01T10:30", "2025-05-01T10:35"),
        execucao(1, "success", "2025-05-01T11:15", "2025-05-01T11:20"),
    ]


@pytest.fixture
def runs_censurado():
    return [execucao(1, "success", "2025-12-01"), execucao(1, "failure", "2025-12-30")]
