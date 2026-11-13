'# Lab04 — Testes de hipótese por dentro: t de Welch × Mann-Whitney

Laboratório de Experimentação de Software · Engenharia de Software PUC Minas · prof. Danilo Maia
Grupo: Matheus Ferreira Titton, Murilo Andrade Machado e Pedro Henrique Barbosa Montandon de Araújo

**Pergunta:** adotar um bot de revisão (CodeRabbit) muda o tempo até o merge dos PRs?
Par escolhido: **P1, t de Welch × Mann-Whitney**. Cenário completo em [`docs/cenario.md`](docs/cenario.md),
origem dos dados em [`dados/FONTE.md`](dados/FONTE.md).

- Dashboard publicado: https://matheustitton.github.io/lab01-repositorios-populares/lab04-testes-hipotese/dashboard/
- GitHub Projects: https://github.com/users/matheustitton/projects/2

## Como rodar (um único comando)

```bash
pip install -r requirements.txt
python rodar.py
```

O `rodar.py` faz tudo, sem acessar a rede e com semente fixa (`numpy.random.default_rng`, semente 42):

1. estima os parâmetros da simulação a partir de `dados/prs_reais.csv` → `dados/parametros_simulacao.json`
2. aplica os dois testes a um conjunto simulado (S01) → `saida/exemplo_s01.json`
3. roda Q1, Q2 e Q3: 10.000 conjuntos por situação e por tamanho de efeito (S02) → `saida/simulacoes_s02.json`
4. aplica os testes aos dados reais → `saida/dados_reais.json`
5. estima o poder com o n real e o n necessário para 80% → `saida/tamanho_amostra.json`
6. monta `dashboard/index.html` e abre no navegador (`--nao-abrir` só gera o arquivo)

Leva cerca de 10 segundos. Rodar de novo gera exatamente os mesmos arquivos.

Testes automatizados: `python -m pytest`.

A coleta dos dados reais foi feita uma única vez com `python -m lab04.coleta` e o CSV ficou congelado no repositório.

## Estrutura

| Arquivo | O que faz | Sprint |
|---|---|---|
| `lab04/coleta.py` | coleta os PRs reais pela API do GitHub | S01 |
| `lab04/parametros.py` | mediana e σ da lognormal a partir dos dados reais | S01 |
| `lab04/simulacao.py` | gerador lognormal dos dois grupos | S01 |
| `lab04/testes.py` | Welch e Mann-Whitney, com tamanho de efeito | S01 |
| `lab04/exemplo.py` | os dois testes em um conjunto simulado, com interpretação | S01 |
| `lab04/graficos.py` | G1 e G2 | S01 |
| `lab04/situacoes.py` | cenário-base, três violações de pressuposto e um contraste | S02 |
| `lab04/simulacoes.py` | Monte Carlo do erro tipo I e do poder, com α = 0,05 e 0,01 | S02 |
| `lab04/graficos_s02.py` | G3 e G4, com botão para trocar α | S02 |
| `lab04/dados_reais.py` | testes nos dados reais, efeito em horas e IC bootstrap | S02 |
| `lab04/amostra.py` | poder com n = 30 e n necessário para 80% | S02 |
| `lab04/dashboard.py` | página HTML com as 7 seções do enunciado | todas |

## Publicação

O dashboard é um HTML estático. Para publicar no GitHub Pages: **Settings → Pages → Deploy from a branch → `main` / root**.
O link acima passa a funcionar depois do primeiro deploy.
