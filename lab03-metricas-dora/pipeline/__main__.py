"""Uso: GITHUB_TOKEN=... python -m pipeline --config config.yaml"""
import argparse
import logging
import os
import sys

from .cache import Cache
from .config import carregar_config
from .estado import RepoStore
from .github_client import ClienteGitHub
from .orquestrador import executar


def main() -> int:
    ap = argparse.ArgumentParser(prog="pipeline", description="Mineração de métricas DORA")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--etapa", choices=["todas", "selecao", "coleta", "dataset"], default="todas")
    ap.add_argument("--limite", type=int, help="sobrescreve alvo_amostra do config")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    token = os.environ.get("GITHUB_TOKEN")
    if not token and args.etapa != "dataset":
        print("Defina a variável de ambiente GITHUB_TOKEN (nunca commite o token).", file=sys.stderr)
        return 1
    cfg = carregar_config(args.config)
    client = ClienteGitHub(token, Cache(cfg.caminho_cache))
    executar(cfg, client, RepoStore(cfg.caminho_estado), args.etapa, args.limite)
    return 0


if __name__ == "__main__":
    sys.exit(main())
