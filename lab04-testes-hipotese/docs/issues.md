# Issues do Lab04 — prontas para colar no GitHub

**Tudo é Sprint 2.** Ordem obrigatória: **Murilo → Pedro → Matheus**. Cada um faz as suas duas issues seguidas, avisa no grupo e não volta a mexer no código depois de passar a vez.

**Como usar:** para cada bloco, clique em *New issue*, copie o **Título** e cole o **Corpo** (o trecho dentro da caixa de código). Defina Assignee e labels e coloque a issue no GitHub Projects (coluna *Todo*). Crie todas antes de começar e anote o número de cada uma: ele substitui o `#ISSUE` nos commits.

| Ordem | Issue | Assignee |
|---|---|---|
| 1 | Situações simuladas e violações de pressuposto (Q3) | Murilo |
| 2 | Testes de hipótese nos dados reais (seção 6) | Murilo |
| 3 | Motor de Monte Carlo: erro tipo I (Q1) e poder (Q2) | Pedro |
| 4 | Tamanho da amostra e rodar.py completo | Pedro |
| 5 | Dashboard completo: G3, G4 e seções 4 a 7 | Matheus |
| 6 | README, documentação e publicação do dashboard | Matheus |
| 7 | Ensaio da apresentação oral | todos |

---

## 1 · Murilo

**Título:** `[S02] Situações simuladas e violações de pressuposto (Q3)`
**Assignee:** Murilo · **Labels:** `sprint-2`, `simulação`

```markdown
## Objetivo
Definir as situações em que os dois testes serão comparados: o cenário-base, três violações de pressuposto do teste paramétrico (Q3) e um contraste favorável ao Welch.

## Tarefas
- [ ] Atualizar `lab04/caminhos.py` com os arquivos de saída novos (simulações, dados reais e tamanho de amostra)
- [ ] Criar `lab04/situacoes.py` com a dataclass `Situacao` e a função `montar_situacoes(parametros)`
- [ ] Cenário-base: lognormal com σ = 1,64 e n = 30 (parâmetros reais)
- [ ] Cauda pesada: σ = 2,77 (desvio-padrão do log real)
- [ ] Outliers: 5% dos PRs levam 20 vezes mais, aplicado nos dois grupos para manter H₀ verdadeira
- [ ] Amostra pequena: n = 10 por grupo
- [ ] Contraste quase simétrico: σ = 0,20
- [ ] Testes em `tests/test_situacoes.py`
- [ ] Documentar a tabela de situações em `docs/cenario.md`

## Critério de pronto
- `python -m pytest` passa (60 testes)
- `python rodar.py --nao-abrir` roda do início ao fim

## Arquivos
`lab04/caminhos.py`, `lab04/situacoes.py`, `tests/test_situacoes.py`, `docs/cenario.md`

## Depende de
Sprint 1 concluída.
```

---

## 2 · Murilo

**Título:** `[S02] Testes de hipótese nos dados reais (seção 6)`
**Assignee:** Murilo · **Labels:** `sprint-2`, `análise`

```markdown
## Objetivo
Aplicar o Welch e o Mann-Whitney aos 60 PRs reais e medir o efeito na unidade do cenário (horas).

## Tarefas
- [ ] Criar `lab04/dados_reais.py`
- [ ] Estatística, p-valor, tamanho do efeito (g de Hedges e rank-bisserial) e magnitude
- [ ] Decisão de cada teste com α = 0,05, bicaudal
- [ ] Médias e medianas por grupo e razão entre as medianas
- [ ] IC bootstrap de 95% para a diferença de médias e de medianas (semente fixa)
- [ ] Gerar `saida/dados_reais.json` com `python -m lab04.dados_reais`
- [ ] Testes em `tests/test_dados_reais.py`

## Critério de pronto
- `python -m pytest` passa (67 testes)
- `python rodar.py --nao-abrir` roda do início ao fim

## Arquivos
`lab04/dados_reais.py`, `saida/dados_reais.json`, `tests/test_dados_reais.py`

## Depende de
Issue 1: "[S02] Situações simuladas e violações de pressuposto (Q3)" (mesmo responsável, logo em seguida).
```

---

## 3 · Pedro

**Título:** `[S02] Motor de Monte Carlo: erro tipo I (Q1) e poder (Q2)`
**Assignee:** Pedro · **Labels:** `sprint-2`, `simulação`

```markdown
## Objetivo
Responder Q1 (erro tipo I) e Q2 (poder) em todas as situações, para α = 0,05 e α = 0,01.

## Tarefas
- [ ] Criar `lab04/simulacoes.py`
- [ ] 10.000 conjuntos de dados por situação e por tamanho de efeito
- [ ] Efeitos: redução da mediana de 0%, 10%, 20%, ..., 70% (8 valores, começando em zero)
- [ ] Contar a proporção de p < α para os dois testes; redução 0% = erro tipo I
- [ ] Semente fixa por (situação, efeito) com `numpy.random.default_rng`
- [ ] Margem do Monte Carlo (±0,43 p.p. para 5% com 10.000 repetições)
- [ ] Gerar `saida/simulacoes_s02.json` com `python -m lab04.simulacoes`
- [ ] Testes em `tests/test_simulacoes.py`

## Critério de pronto
- `python -m pytest` passa (75 testes)
- `python rodar.py --nao-abrir` roda do início ao fim

## Arquivos
`lab04/simulacoes.py`, `saida/simulacoes_s02.json`, `tests/test_simulacoes.py`

## Depende de
Issue 2: "[S02] Testes de hipótese nos dados reais (seção 6)" (passagem de vez: Murilo → Pedro).
```

---

## 4 · Pedro

**Título:** `[S02] Tamanho da amostra e rodar.py completo`
**Assignee:** Pedro · **Labels:** `sprint-2`, `simulação`

```markdown
## Objetivo
Responder às questões de "Para discutir: tamanho da amostra" com o efeito observado nos dados reais, e deixar o `rodar.py` executando tudo.

## Tarefas
- [ ] Criar `lab04/amostra.py`
- [ ] Usar a razão entre as medianas reais (redução de 34%) no cenário-base
- [ ] Poder dos dois testes para n = 30, 50, 75, 100, 150, 200, 300, 400, 600, 800 e 1.000 por grupo
- [ ] Menor n da grade com poder ≥ 80% para cada teste
- [ ] Gerar `saida/tamanho_amostra.json` com `python -m lab04.amostra`
- [ ] Testes em `tests/test_amostra.py`
- [ ] `rodar.py` passa a executar simulações, dados reais e tamanho de amostra

## Critério de pronto
- `python -m pytest` passa (77 testes)
- `python rodar.py --nao-abrir` roda do início ao fim

## Arquivos
`lab04/amostra.py`, `saida/tamanho_amostra.json`, `tests/test_amostra.py`, `rodar.py`

## Depende de
Issue 3: "[S02] Motor de Monte Carlo: erro tipo I (Q1) e poder (Q2)" (mesmo responsável, logo em seguida).
```

---

## 5 · Matheus

**Título:** `[S02] Dashboard completo: G3, G4 e seções 4 a 7`
**Assignee:** Matheus · **Labels:** `sprint-2`, `dashboard`, `gráficos`

```markdown
## Objetivo
Fechar o dashboard com as 7 seções do enunciado, sem nada pendente: G3, G4, dados reais e conclusão.

## Tarefas
- [ ] Criar `lab04/graficos_s02.py` com G3 (erro tipo I por situação, linha em α e faixa do Monte Carlo) e G4 (curvas de poder, um painel por situação, linha de 80%)
- [ ] Botão para trocar α entre 0,05 e 0,01 nos dois gráficos (pergunta 12)
- [ ] Mesma cor de cada teste em todos os gráficos, título, eixos com unidade e legenda
- [ ] Seções 4 e 5 com textos de 2 a 4 frases gerados a partir dos números
- [ ] Seção 6: tabela dos dados reais e subseção sobre tamanho de amostra
- [ ] Seção 7: expectativa × resultado, recomendação, quando ela mudaria e limitações
- [ ] Testes em `tests/test_graficos_s02.py` e `tests/test_dashboard.py`
- [ ] Regenerar `dashboard/index.html` com `python rodar.py --nao-abrir`

## Critério de pronto
- `python -m pytest` passa (83 testes)
- `python rodar.py --nao-abrir` roda do início ao fim

## Arquivos
`lab04/graficos_s02.py`, `tests/test_graficos_s02.py`, `lab04/dashboard.py`, `tests/test_dashboard.py`, `dashboard/index.html`

## Depende de
Issue 4: "[S02] Tamanho da amostra e rodar.py completo" (passagem de vez: Pedro → Matheus).
```

---

## 6 · Matheus

**Título:** `[S02] README, documentação e publicação do dashboard`
**Assignee:** Matheus · **Labels:** `sprint-2`, `documentação`

```markdown
## Objetivo
Deixar o repositório pronto para correção e o dashboard publicado.

## Tarefas
- [ ] `README.md` com o comando único (`python rodar.py`) e a estrutura do código
- [ ] `docs/issues.md`, `docs/divisao_tarefas.md` e `docs/roteiro_apresentacao.md`
- [ ] Ligar o GitHub Pages (Settings → Pages → Deploy from a branch → `main` / root) e testar o link do topo do dashboard

## Critério de pronto
- `python -m pytest` passa (83 testes)
- `python rodar.py --nao-abrir` roda do início ao fim

## Arquivos
`README.md`, `docs/issues.md`, `docs/divisao_tarefas.md`, `docs/roteiro_apresentacao.md`

## Depende de
Issue 5: "[S02] Dashboard completo: G3, G4 e seções 4 a 7" (mesmo responsável, logo em seguida).
```

---

## 7 · Todos

**Título:** `[S02] Ensaio da apresentação oral`
**Assignees:** Murilo, Pedro e Matheus · **Labels:** `sprint-2`, `apresentação`

```markdown
## Objetivo
Responder às 15 perguntas em até 7 minutos, usando o próprio dashboard.

## Divisão (ver docs/roteiro_apresentacao.md)
- Murilo: perguntas 1, 2, 3, 4 e 11
- Matheus: perguntas 5, 6, 7, 10 e 15
- Pedro: perguntas 8, 9, 12, 13 e 14

## Tarefas
- [ ] Cada um ensaia as suas respostas, até 30 s cada
- [ ] Um ensaio completo cronometrado com os três
- [ ] Testar o botão de α = 0,01 no G3 e no G4 (pergunta 12)
- [ ] Deixar uma cópia local do dashboard aberta, caso a internet falhe

## Critério de pronto
- Ensaio completo em até 7 minutos
- Todos conseguem responder qualquer pergunta, não só as suas
```
