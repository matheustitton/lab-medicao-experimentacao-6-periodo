# Introdução — hipóteses RQ01 e RQ02 (Pedro)

### RQ01 — Frequência de deploys

**Pergunta:** Qual a frequência de deploys dos repositórios populares que usam CI/CD?

**Hipótese:** Esperamos que a mediana fique entre 1 release por mês e 1 por semana (faixas Medium/High), com poucos repositórios Elite (7 ou mais por semana) e uma cauda longa de projetos muito ativos. O motivo é que publicar uma release no GitHub é um ato deliberado (criar tag, escrever notas), e os repositórios populares costumam ser bibliotecas e ferramentas com versionamento em ciclos de semanas. Projetos com deploy contínuo raramente publicam uma release a cada deploy, então a métrica tende a subestimá-los. O filtro de pelo menos 5 releases em 12 meses também elimina os projetos mais parados.

### RQ02 — Lead time

**Pergunta:** Qual o tempo entre um commit e seu respectivo deploy?

**Hipótese:** Esperamos que a variante (b), por commit, dê valores bem menores que a (a), por release, na grande maioria dos repositórios, com mediana de (b) em dias e de (a) em semanas (faixas Medium/Low). A razão é que uma release reúne todos os commits acumulados desde a anterior: a variante (a) olha só o mais antigo e basta um commit "esquecido" para ela explodir, enquanto a (b) pesa todos os commits e é dominada pelos mais recentes. Também esperamos que repositórios com releases mais frequentes tenham lead time menor, em parte por efeito mecânico (menos tempo para os commits esperarem).
