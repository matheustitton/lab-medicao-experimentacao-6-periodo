# analise/ - Passo 4 (analise de resultados) e Passo 6 (dashboard)

Scripts Python da S03. A coleta (`scripts/*.ps1`) nao depende de nada daqui: ela roda so com
Node. Esta pasta le os CSVs que a coleta produziu e devolve testes estatisticos e figuras.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r analise\requirements.txt
```

## Pipeline

Rodar nesta ordem - cada script consome a saida do anterior:

```powershell
.\scripts\run_metrics.ps1 -Todos        # (Node) metricas estaticas dos 18 trials
python analise\consolidar_dados.py      # dataset canonico + auditoria
python analise\rq1_rq2.py               # RQ1 (tempo) e RQ2 (defeitos)
python analise\rq3.py                   # RQ3 (complexidade, duplicacao, LOC)
python analise\dashboard.py             # figuras do relatorio
python analise\montar_relatorio.py      # docs/relatorio-final.md
```

| Script | Frente na S03 | Entrada | Saida |
|---|---|---|---|
| `comum.py` | compartilhado | - | caminhos, constantes, CSV, descritiva, tamanhos de efeito |
| `consolidar_dados.py` | RQ1/RQ2 | `data/trials.csv` | `data/trials_consolidado.csv`, `docs/resultados/00-consolidacao.md` |
| `rq1_rq2.py` | RQ1/RQ2 | `data/trials_consolidado.csv` | `data/resultados_rq1_rq2.csv`, `docs/resultados/rq1-rq2.md` |
| `rq3.py` | RQ3 | `data/metrics.csv` | `data/metrics_consolidado.csv`, `data/resultados_rq3.csv`, `data/descritivas_rq3.csv`, `docs/resultados/rq3.md` |
| `dashboard.py` | dashboard | CSVs dos dois anteriores (nao recalcula) | `docs/figuras/fig01..fig06-*.png` + resumo das 3 RQs no console |
| `montar_relatorio.py` | relatorio | `docs/relatorio/NN-*.md` | `docs/relatorio-final.md` |

## Convencoes que nao sao negociaveis

**Mediana e IQR, nunca media e desvio-padrao.** N pequeno, distribuicao assimetrica e valores
censurados - media aqui engana. Vale para tabela e para grafico.

**Todo p-valor sai com tamanho de efeito.** Cliff's delta para amostras independentes,
rank-biserial para o pareado. "Significativo" sem magnitude nao informa nada com este N.

**O plano estatistico nao muda depois de ver os dados.** Ele esta em
`docs/desenho-experimento.md` e foi fixado antes da coleta. Se um teste nao couber (variancia
zero, poucos pares), o script reporta "nao aplicavel" com a razao - nao troca de teste.

**Nenhum numero e digitado a mao.** Todo valor do relatorio sai de um CSV gerado por script.
Se um numero do texto divergir do CSV, o relatorio perdeu a reprodutibilidade.

**CSV em UTF-8 sem BOM e com ponto decimal.** Escrito sempre por `comum.escrever_csv`, lido
sempre por `comum.ler_csv` (que tolera o BOM que o PowerShell grava). Nao abra os CSVs no
Excel: ele grava BOM e, em locale pt-BR, troca o ponto pela virgula - o que quebra a leitura
em silencio.

## Por que os dois testes

O plano usa **Wilcoxon pareado por kata** como principal e **Mann-Whitney U** como secundario.
Parear por integrante e impossivel neste desenho: ninguem resolve a mesma kata nos dois
tratamentos, entao o bloco e a kata.

Consequencia pratica que apareceu nos dados reais: como duas katas receberam um so tratamento,
sobram 4 pares - e com 4 pares o menor p-valor que o teste exato unicaudal produz e 0,0625,
acima de alfa. O `p_minimo_wilcoxon()` calcula esse limite e os scripts avisam quando ele passa
de alfa, justamente para que "nao rejeita H0" nao seja lido como "nao ha efeito".
