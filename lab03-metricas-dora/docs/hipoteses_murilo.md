# Introdução — hipóteses RQ03 e RQ04 (Murilo)

### RQ03 — Taxa de falha

**Pergunta:** Qual a taxa de falha das mudanças entregues por esses repositórios?

**Hipótese:** Esperamos que o CFR (a), de CI, tenha mediana entre 10% e 30%, e que o CFR (b), de entrega, seja menor na mediana, com muitos repositórios em 0%. Falhar um pipeline é barato e comum (testes instáveis, dependências quebradas, runs em branches de trabalho), enquanto uma release corretiva em até 7 dias exige esforço e só acontece quando o defeito é percebido e importante. Por isso esperamos também que as duas variantes se correlacionem pouco: elas medem coisas diferentes, falha de pipeline e correção de entrega.

### RQ04 — Tempo de recuperação

**Pergunta:** Qual o tempo de recuperação após uma execução de CI/CD com falha?

**Hipótese:** Esperamos uma distribuição muito assimétrica: a maioria dos episódios resolvida em menos de 24 horas, porque falha na branch principal é visível e os mantenedores corrigem logo, mas com uma cauda longa de workflows secundários (nightly, publicação de documentação) que ficam quebrados por semanas. Por isso a mediana por repositório deve ficar entre algumas horas e poucos dias, e esperamos uma proporção de episódios censurados que não é desprezível em parte dos repositórios.
