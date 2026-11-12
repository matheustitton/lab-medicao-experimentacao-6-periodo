# Divisão de tarefas do Lab04 (Sprint 2)

Tudo é entregue na Sprint 2, em uma única passada: **Murilo → Pedro → Matheus**. Cada um só começa quando o anterior fez o `git push` e fechou as suas issues, e ninguém volta a mexer depois de passar a vez. Cada commit deixa `python -m pytest` passando e cita o número da issue (`#ISSUE`). As issues prontas para colar estão em `docs/issues.md`.

## 1. Situações simuladas e violações de pressuposto (Q3) — **Murilo**

| Commit | Arquivos |
|---|---|
| `feat(lab04): caminhos dos novos arquivos de saída #ISSUE` | `lab04/caminhos.py` |
| `feat(lab04): situações simuladas com violações de pressuposto #ISSUE` | `lab04/situacoes.py` |
| `test(lab04): testes das situações e dos outliers #ISSUE` | `tests/test_situacoes.py` |
| `docs(lab04): tabela de situações no cenário #ISSUE` | `docs/cenario.md` |

## 2. Testes de hipótese nos dados reais (seção 6) — **Murilo**

| Commit | Arquivos |
|---|---|
| `feat(lab04): testes aplicados aos dados reais #ISSUE` | `lab04/dados_reais.py`, `saida/dados_reais.json` |
| `test(lab04): testes da análise dos dados reais #ISSUE` | `tests/test_dados_reais.py` |

## 3. Motor de Monte Carlo: erro tipo I (Q1) e poder (Q2) — **Pedro**

| Commit | Arquivos |
|---|---|
| `feat(lab04): simulação de erro tipo I e poder #ISSUE` | `lab04/simulacoes.py`, `saida/simulacoes_s02.json` |
| `test(lab04): testes do motor de simulação #ISSUE` | `tests/test_simulacoes.py` |

## 4. Tamanho da amostra e rodar.py completo — **Pedro**

| Commit | Arquivos |
|---|---|
| `feat(lab04): estudo de tamanho de amostra #ISSUE` | `lab04/amostra.py`, `saida/tamanho_amostra.json` |
| `test(lab04): testes do estudo de tamanho de amostra #ISSUE` | `tests/test_amostra.py` |
| `chore(lab04): rodar.py executa todas as etapas #ISSUE` | `rodar.py` |

## 5. Dashboard completo: G3, G4 e seções 4 a 7 — **Matheus**

| Commit | Arquivos |
|---|---|
| `feat(lab04): gráficos G3 e G4 com botão de α #ISSUE` | `lab04/graficos_s02.py` |
| `test(lab04): testes do G3 e do G4 #ISSUE` | `tests/test_graficos_s02.py` |
| `feat(lab04): dashboard com as sete seções completas #ISSUE` | `lab04/dashboard.py`, `tests/test_dashboard.py`, `dashboard/index.html` |

## 6. README, documentação e publicação do dashboard — **Matheus**

| Commit | Arquivos |
|---|---|
| `docs(lab04): README com comando único e estrutura #ISSUE` | `README.md` |
| `docs(lab04): issues, divisão de tarefas e roteiro da apresentação #ISSUE` | `docs/issues.md`, `docs/divisao_tarefas.md`, `docs/roteiro_apresentacao.md` |

## Checklist do GitHub Projects (vale desconto de até 10%)
- [ ] Toda issue com Assignee, e cartão movido para *In Progress* quando começar e *Done* quando fechar.
- [ ] No máximo uma issue *In Progress* por pessoa (WIP).
- [ ] Todo commit com `#número` da issue.
