# Metodologia — pipeline e dataset

> Texto da seção 2 do artigo (parte do pipeline), com os números reais.

## 2.11 Pipeline

O pipeline é executado por um único comando (`python -m pipeline --config config.yaml`); o token do GitHub vem da variável de ambiente `GITHUB_TOKEN` e nunca é commitado. Ele tem quatro camadas:

- **Cliente HTTP:** escrito pelo grupo sobre `requests`. Segue o cabeçalho `Link` (`rel="next"`) para paginar, lê `X-RateLimit-Remaining` e `X-RateLimit-Reset` e espera automaticamente quando a cota está acabando ou o servidor responde 403/429 por limite de taxa. Erros 5xx e de rede são repetidos com *backoff* exponencial (1 s, 2 s, 4 s, 8 s) até 5 tentativas.
- **Cache e retomada:** cada resposta é gravada em SQLite (chave = caminho + parâmetros). Um segundo banco guarda a etapa alcançada por cada repositório e o motivo de descarte. Interromper e rodar de novo continua de onde parou, sem repetir chamadas.
- **Coletores:** releases (com a release anterior de cada uma), commits entre releases (`compare` paginado de 100 em 100) e workflow runs.
- **Métricas:** funções puras, sem acesso à rede, testadas com pytest (196 testes; cobertura de 100% do módulo de métricas, mínimo exigido de 80%), executadas a cada push pelo GitHub Actions do próprio repositório.

## 2.12 Limites da API e como foram tratados

| Limite | Tratamento |
|---|---|
| Busca devolve no máximo 1.000 resultados | consultas fatiadas por faixas de estrelas |
| `compare` devolve no máximo 250 commits sem paginação | paginação até 30 páginas; releases com mais commits ficam marcadas como `truncado` e entram no dataset com essa marca |
| Workflow runs: no máximo 1.000 resultados por consulta com filtros | janela dividida por mês e, se algum intervalo atinge o teto, dividida ao meio recursivamente; se ainda assim atinge o teto, a coluna `teto_runs_atingido` fica verdadeira |
| `compare` retorna 404/422 (tag removida ou reescrita) | a release é marcada `indisponivel` e fica fora do lead time, contada em `n_releases_indisponiveis` |
| Lista de contribuidores recusada em repositórios muito grandes | `contribuidores` fica vazio |

## 2.13 Tratamento de casos de borda

- Release sem release anterior (primeira da história): fora do lead time (`n_releases_sem_anterior`).
- Release sem commits novos: fora do lead time (`n_releases_sem_commits`).
- Commit com data posterior à release (efeito de *rebase* ou *squash*): mantido nos cálculos e contado em `n_lead_negativos`.
- Falha sem sucesso anterior no mesmo workflow: não inicia episódio.
- Execuções `cancelled` e similares: ignoradas e não encerram episódios.
- Episódio de falha nunca recuperado na janela: censurado; reportamos `n_episodios_censurados` e `prop_episodios_censurados`.

## 2.14 Dataset final

O arquivo `data/saida/dataset_dora.csv` tem uma linha por repositório e 37 colunas, com todas as variantes de RQ01 a RQ04, os contadores de censura e de exclusão e a classe DORA da combinação C1. O dicionário de dados (nome, tipo, unidade e fórmula ou origem de cada coluna) está em `docs/DICIONARIO_DADOS.md` e em `data/saida/dicionario_dados.csv`, gerado da mesma fonte que as colunas do CSV, o que impede que os dois divirjam.

A amostra final tem **270 repositórios** (o mínimo exigido era 300; ver ameaças à validade), de 25 linguagens (TypeScript 73, Python 46, Go 38, Rust 25, JavaScript 19), com mediana de 15.705 estrelas (IQR 4.816 a 36.418), 168 contribuidores (IQR 64 a 466) e 6,6 anos de idade (2.394 dias). Os 270 repositórios somam 13.664 releases publicadas, 1.046.247 commits comparados e cerca de 800 mil workflow runs válidos. Pré-releases (4.119 em 98 repositórios) ficam fora da definição principal. Do total de releases, 58 são a primeira da história (sem release anterior), 12 tiveram o `compare` indisponível e 1.659 (12%) não trouxeram commits novos; todas ficam fora do lead time. Em 22 repositórios existe commit com data posterior à release (`n_lead_negativos`), efeito de *rebase* ou *squash*; eles foram mantidos.

## 2.15 Reprodutibilidade

Com a mesma janela, a mesma semente (42) e o mesmo cache, a seleção e as métricas são determinísticas. Sem o cache, repetir a coleta pode produzir números ligeiramente diferentes, porque repositórios recebem estrelas, releases e runs ao longo do tempo; por isso o cache e o dataset final são versionados ou arquivados junto com o artigo.
