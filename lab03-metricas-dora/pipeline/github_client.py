"""Cliente REST do GitHub escrito à mão (o enunciado proíbe bibliotecas como PyGithub).

Cuida de: autenticação, cache em disco, rate limit (X-RateLimit-*), backoff exponencial
em 5xx/erros de rede e paginação pelo cabeçalho Link.
"""
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests

from .cache import Cache, chave_requisicao

BASE_URL = "https://api.github.com"
STATUS_CACHEAVEIS = {200, 204, 404, 409, 451}
RE_LINK = re.compile(r'<([^>]+)>;\s*rel="(\w+)"')
log = logging.getLogger(__name__)


class ErroAPI(Exception):
    def __init__(self, mensagem: str, status: Optional[int] = None):
        super().__init__(mensagem)
        self.status = status


@dataclass
class Resposta:
    status: int
    dados: Any
    links: Dict[str, str] = field(default_factory=dict)


def normalizar(caminho: str, params: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
    """Aceita caminho relativo ou URL absoluta (vinda do Link) e separa path/params."""
    params = dict(params or {})
    if caminho.startswith("http"):
        u = urlparse(caminho)
        caminho = u.path
        params = {**dict(parse_qsl(u.query)), **params}
    return caminho, params


def parse_link(cabecalho: Optional[str]) -> Dict[str, str]:
    return {rel: url for url, rel in RE_LINK.findall(cabecalho or "")}


class ClienteGitHub:
    def __init__(
        self,
        token: Optional[str],
        cache: Cache,
        base_url: str = BASE_URL,
        sessao: Optional[requests.Session] = None,
        max_tentativas: int = 5,
        margem_rate_limit: int = 2,
        dormir: Callable[[float], None] = time.sleep,
        agora: Callable[[], float] = time.time,
        timeout: int = 30,
    ):
        self.cache = cache
        self.base_url = base_url
        self.sessao = sessao or requests.Session()
        self.sessao.headers.update(
            {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        )
        if token:
            self.sessao.headers["Authorization"] = f"Bearer {token}"
        self.max_tentativas = max_tentativas
        self.margem = margem_rate_limit
        self.dormir = dormir
        self.agora = agora
        self.timeout = timeout
        self.n_chamadas_rede = 0

    # ---------------------------------------------------------------- público
    def get(self, caminho: str, params: Optional[Dict[str, Any]] = None,
            reduzir: Optional[Callable[[Any], Any]] = None) -> Resposta:
        """GET com cache. `reduzir` encolhe o JSON antes de gravar (economiza disco)."""
        caminho, params = normalizar(caminho, params)
        chave = chave_requisicao(caminho, params)
        achado = self.cache.obter(chave)
        if achado is not None:
            return Resposta(*achado)
        status, dados, links = self._requisitar(caminho, params)
        if reduzir is not None and status == 200:
            dados = reduzir(dados)
        if status in STATUS_CACHEAVEIS:
            self.cache.salvar(chave, status, dados, links)
        return Resposta(status, dados, links)

    def paginar(self, caminho: str, params: Optional[Dict[str, Any]] = None,
                chave: Optional[str] = None, reduzir: Optional[Callable[[Any], Any]] = None,
                max_paginas: Optional[int] = None) -> Iterator[Any]:
        """Itera item a item seguindo rel="next". `chave` = campo que guarda a lista."""
        params = {"per_page": 100, **(params or {})}
        resp = self.get(caminho, params, reduzir)
        pagina = 1
        while resp.status == 200:
            yield from (resp.dados[chave] if chave else resp.dados)
            proxima = resp.links.get("next")
            if not proxima or (max_paginas and pagina >= max_paginas):
                break
            resp = self.get(proxima, None, reduzir)
            pagina += 1

    def contar(self, caminho: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Conta itens sem baixar tudo: per_page=1 e lê a última página do Link."""
        resp = self.get(caminho, {**(params or {}), "per_page": 1})
        if resp.status != 200:
            return 0
        ultima = resp.links.get("last")
        if ultima:
            return int(dict(parse_qsl(urlparse(ultima).query))["page"])
        return len(resp.dados)

    # --------------------------------------------------------------- interno
    def _backoff(self, tentativa: int) -> None:
        espera = 2 ** tentativa          # 1, 2, 4, 8, 16 s
        log.warning("erro temporário; nova tentativa em %ss", espera)
        self.dormir(espera)

    def _dormir_ate(self, reset: Optional[str], extra: float = 1.0) -> None:
        espera = max(float(reset) - self.agora(), 0) + extra if reset else 60.0
        log.warning("rate limit: aguardando %.0fs", espera)
        self.dormir(espera)

    def _espera_por_limite(self, r) -> Optional[float]:
        """Segundos a esperar se a resposta 403/429 é limite de taxa; None caso contrário."""
        if r.headers.get("Retry-After"):
            return float(r.headers["Retry-After"]) + 1
        if r.headers.get("X-RateLimit-Remaining") == "0":
            return max(float(r.headers.get("X-RateLimit-Reset", 0)) - self.agora(), 0) + 1
        if "rate limit" in (r.text or "").lower():
            return 60.0
        return None

    def _requisitar(self, caminho: str, params: Dict[str, Any]):
        tentativa = 0
        while True:
            try:
                r = self.sessao.get(self.base_url + caminho, params=params, timeout=self.timeout)
            except (requests.ConnectionError, requests.Timeout):
                tentativa += 1
                if tentativa >= self.max_tentativas:
                    raise ErroAPI(f"rede indisponível em {caminho}")
                self._backoff(tentativa - 1)
                continue
            self.n_chamadas_rede += 1
            if r.status_code in (403, 429):
                espera = self._espera_por_limite(r)
                if espera is None:
                    raise ErroAPI(f"{r.status_code} em {caminho}: {r.text[:200]}", r.status_code)
                log.warning("rate limit (%s): aguardando %.0fs", r.status_code, espera)
                self.dormir(espera)
                continue
            if r.status_code >= 500:
                tentativa += 1
                if tentativa >= self.max_tentativas:
                    raise ErroAPI(f"{r.status_code} persistente em {caminho}", r.status_code)
                self._backoff(tentativa - 1)
                continue
            restante = r.headers.get("X-RateLimit-Remaining")
            if restante is not None and int(restante) <= self.margem:
                self._dormir_ate(r.headers.get("X-RateLimit-Reset"))
            if r.status_code not in STATUS_CACHEAVEIS:
                raise ErroAPI(f"{r.status_code} em {caminho}: {r.text[:200]}", r.status_code)
            try:
                dados = r.json() if r.status_code != 204 else []
            except ValueError:
                dados = None
            return r.status_code, dados, parse_link(r.headers.get("Link"))
