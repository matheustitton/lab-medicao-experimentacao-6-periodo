# Lab03 — Mineração de métricas DORA

Pipeline reprodutível que calcula as métricas DORA (frequência de deploy, lead time, taxa de falha e
tempo de recuperação) a partir de repositórios open-source reais que usam GitHub Actions.
Grupo: Matheus, Pedro e Murilo — Laboratório de Experimentação de Software (PUC Minas).

## Como rodar (um único comando)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GITHUB_TOKEN=<seu token>          # nunca commite o token
# 1. ajuste as datas da janela em config.yaml (fixadas pelo professor)
python -m pipeline --config config.yaml  # seleção -> coleta -> dataset
```

Interrompeu (Ctrl+C, rate limit, queda de rede)? **Rode o mesmo comando de novo**: o cache
(`data/cache.sqlite`) e o estado de cada repositório (`data/estado.sqlite`) fazem a coleta continuar
de onde parou, sem repetir chamadas.

Etapas isoladas: `--etapa selecao | coleta | dataset` e `--limite N` (para testes rápidos, ex.: `--limite 3`).

## Saídas (`data/saida/`)

| Arquivo | Conteúdo |
|---|---|
| `dataset_dora.csv` | uma linha por repositório, todas as variantes das métricas |
| `dicionario_dados.csv` / `docs/DICIONARIO_DADOS.md` | nome, tipo, unidade e fórmula de cada coluna |
| `funil_selecao.md` | repositórios restantes em cada etapa e motivos de descarte |
| `dataset_sensibilidade.csv` | métricas sob várias definições (combinações C1 a C4 da RQ07 e versões v1 a v5 da heurística) |
| `kappa_fleiss.csv`, `avaliacao_heuristica.csv`, `validacao_cruzada_heuristica.csv` | resultados da validação manual |
| `analise/` | tabelas (`.csv` e `.md`) e figuras (`.png`) das RQ01 a RQ08 |

## Validação manual (Sprint 02)

```bash
python -m validacao.amostra --config config.yaml              # sorteia 60 repos (semente 42) e gera as planilhas
# cada integrante preenche, SEM combinar, rotulos/rotulos_<nome>_repos.csv e _releases.csv
python -m validacao.concordancia --config config.yaml         # kappa de Fleiss + consenso (maioria)
python -m validacao.avaliacao_heuristica --config config.yaml # precisão/recall/F1 de cada versão da heurística
```
Protocolo completo em `docs/PROTOCOLO_VALIDACAO.md`.

## Análise estatística (Sprint 03)

Cada análise é um módulo reexecutável a partir dos CSVs (não precisa de token nem de rede):

```bash
python -m pipeline --etapa dataset                 # gera data/saida/dataset_dora.csv a partir de data/estado.sqlite
python -m analise.sensibilidade_dataset            # gera data/saida/dataset_sensibilidade.csv
python -m analise.rq01_04                          # RQ01 a RQ04, classificação DORA (C1), variantes e censura
python -m analise.rq05                             # Spearman frequência x CFR (a e b)
python -m analise.rq06                             # Kruskal-Wallis, epsilon², Holm, Cliff's delta, robustez da idade
python -m analise.rq07                             # sensibilidade: % que muda de categoria e kappa ponderado
python -m analise.rq08                             # bônus: rework rate
python -m validacao.validacao_cruzada              # F1 da heurística fora da amostra (5 dobras por repositório)
```

Resultados e discussão em `docs/artigo/resultados_rq01_04.md`, `resultados_rq05_08.md` e `discussao.md`.

## Testes

```bash
pytest --cov=metricas --cov-report=term-missing   # cobertura mínima exigida: 80% (CI falha abaixo disso)
```

## Estrutura

```
pipeline/    coleta e orquestração (cliente da API, cache, seleção, releases, runs, dataset)
metricas/    funções puras de cálculo (lead time, CFR, recuperação, classificação) — sem rede
validacao/   amostra-ouro, kappa de Fleiss, avaliação e validação cruzada da heurística
analise/     estatística das RQ01 a RQ08 (Spearman, Kruskal-Wallis, Holm, kappa ponderado)
tests/       pytest com fixtures dos exemplos do enunciado
docs/        dicionário de dados, protocolo de validação, histórico da heurística, rascunhos do artigo
```

## Decisões de método (resumo)

* Cliente HTTP próprio (`requests`); nenhuma biblioteca de acesso à API do GitHub.
* Candidatos vêm da Search API fatiada por estrelas (limite de 1.000 por consulta) e são processados em
  ordem pseudoaleatória reprodutível (`semente` no config) até atingir `alvo_amostra`.
* Runs: só `event=push` no default branch; janela fatiada por mês e subdividida quando um intervalo chega
  ao teto de 1.000 resultados da API (`teto_runs_atingido` sinaliza o que não foi possível subdividir).
* Lead time com datas negativas (rebase/squash) não é alterado: é contado em `n_lead_negativos`.
* Episódio de falha só começa na primeira falha **após um sucesso**; episódios sem recuperação são
  censurados e reportados (`prop_episodios_censurados`), não descartados.
