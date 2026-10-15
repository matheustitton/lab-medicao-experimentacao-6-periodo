# Protocolo de validação manual (amostra-ouro)

1. **Sorteio** — `python -m validacao.amostra`: 60 repositórios com `df.sample(n=60, random_state=42)` sobre os
   repositórios da amostra final (os mesmos do `dataset_dora.csv`, lidos de `data/estado.sqlite`); para cada um, 5 releases principais (com release anterior) sorteadas com
   `random.Random(f"{semente}:{repo}")`. Mesma semente = mesma amostra.
2. **Rotulagem independente** — cada integrante preenche a própria planilha, sem consultar os demais e
   **sem ver a saída da heurística** (as planilhas não a contêm):
   * `tipo_projeto`: `biblioteca_framework | aplicacao_servico | cli | outro`
   * `releases_entregas_reais`: `sim | nao | incerto`
   * `corretiva` (por release): `sim | nao` — lendo release notes e a lista de commits (`url_comparacao`).
3. **Concordância** — `python -m validacao.concordancia`: kappa de Fleiss por dimensão (interpretação de
   Landis & Koch) e concordância bruta. Kappa baixo é um achado: o critério é ambíguo; discutir no artigo.
4. **Consenso e desempate** — maioria simples (2 de 3). Casos 1-1-1 vão para `rotulos/consenso_pendentes.csv`
   e são decididos **em reunião dos três**; a decisão é registrada em `rotulos/desempate_reuniao.csv`
   (colunas `nivel,chave,dimensao,rotulo_final`) e entra no `consenso.csv` na próxima execução.
5. **Heurística** — `python -m validacao.avaliacao_heuristica`: precisão, recall e F1 de cada versão
   registrada em `metricas/heuristica.py`, contra o consenso. Se F1 < 0,70: refinar, reavaliar e anotar a
   versão e o F1 em `docs/HISTORICO_HEURISTICA.md`.
6. Depois de escolher a versão final, ajustar `heuristica:` no `config.yaml` e regerar o dataset
   (`python -m pipeline --etapa dataset`).
