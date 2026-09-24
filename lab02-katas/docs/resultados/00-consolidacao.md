# S03 - Consolidacao do dataset (auditoria)

Gerado por `analise/consolidar_dados.py`. Nao editar a mao: rode o script de novo.

## 1. Deduplicacao

- linhas no log bruto (`data/trials.csv`): **21**
- trials distintos apos deduplicar: **18**
- linhas descartadas: **3** (mantida sempre a execucao mais recente)

| trial_id | inicio descartado | tempo (s) | motivo |
|---|---|---|---|
| `p1-kata-01-faixas-ia` | 2026-09-14T21:38:04 | 4 | execucao anterior do mesmo trial_id (superada por uma mais recente) |
| `p1-kata-02-espiral-manual` | 2026-09-14T22:00:21 | 4 | execucao anterior do mesmo trial_id (superada por uma mais recente) |
| `p2-kata-01-faixas-ia` | 2026-09-16T19:08:05 | 7 | execucao anterior do mesmo trial_id (superada por uma mais recente) |

As linhas acima ficam versionadas em `data/trials_descartados.csv` - descarte sem
registro seria manipulacao de dado, ainda que involuntaria.

## 2. Validacao contra o desenho

Todas as checagens passaram: 18 trials, 3 integrantes x 6 katas, 9 IA / 9 MANUAL.

## 3. Cobertura por kata - o n real do Wilcoxon

| kata | trials IA | trials MANUAL | forma par? |
|---|---|---|---|
| kata-01-faixas | 3 | 0 | **NAO** |
| kata-02-espiral | 1 | 2 | sim |
| kata-03-duracao | 2 | 1 | sim |
| kata-04-romanos | 1 | 2 | sim |
| kata-05-rainha | 2 | 1 | sim |
| kata-06-delimitadores | 0 | 3 | **NAO** |

**Pares completos: 4 de 6.**

O plano de analise previa n = 6 pares. Com 4, o menor p-valor que o Wilcoxon
exato unicaudal pode produzir e **0,0625** - acima de alfa = 0.05. Nessa configuracao o teste pareado NAO PODE rejeitar H0, por maior que seja o efeito.
O Mann-Whitney sobre os 18 trials individuais passa a ser o teste com poder, e o
Wilcoxon entra como evidencia de direcao consistente entre blocos.

## 4. Aderencia ao contrabalanceamento planejado

Trials fora do quadrado latino de `docs/desenho-experimento.md`: **8** de 18.

| trial | planejado | executado |
|---|---|---|
| `p2 / kata-01-faixas` | MANUAL | IA |
| `p2 / kata-02-espiral` | IA | MANUAL |
| `p2 / kata-03-duracao` | MANUAL | IA |
| `p2 / kata-04-romanos` | IA | MANUAL |
| `p2 / kata-05-rainha` | MANUAL | IA |
| `p2 / kata-06-delimitadores` | IA | MANUAL |
| `p3 / kata-01-faixas` | MANUAL | IA |
| `p3 / kata-05-rainha` | IA | MANUAL |

Desvio de execucao, nao erro de digitacao: e a causa direta das katas sem par da
secao 3. Entra no relatorio final como ameaca a validade (item novo), com o efeito
que teve sobre o n do teste pareado.

## 5. Trials com tempo curto demais para ser cronometragem

Limiar: 30 s (o `run_trial.ps1` so reavalia a suite a cada 5 s).
Trials marcados: **3**.

| trial_id | tratamento | tempo (s) |
|---|---|---|
| `p2-kata-01-faixas-ia` | IA | 6 |
| `p2-kata-03-duracao-ia` | IA | 5 |
| `p2-kata-05-rainha-ia` | IA | 6 |

Um verde em poucos segundos significa que o codigo ja estava escrito quando o
cronometro comecou - o tempo registrado mede a execucao do Jest, nao a resolucao
da kata. **Nenhum destes e descartado**: eles entram na analise de sensibilidade
do `analise/rq1_rq2.py`, que refaz os testes sem eles e mostra se a conclusao muda.

