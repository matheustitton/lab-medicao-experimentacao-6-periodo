# Introdução — hipóteses RQ05, RQ06 e RQ07 (Matheus)

### RQ05 — Frequência × taxa de falha

**Pergunta:** Repositórios com maior frequência de deploy apresentam maior ou menor taxa de falha?

**Hipótese:** Esperamos uma correlação de Spearman perto de zero (ou levemente negativa) entre frequência e CFR (a): projetos que publicam com frequência tendem a ter CI mais maduro, mas isso não deve ser uma regra forte. Para o CFR (b) esperamos uma correlação positiva fraca ou moderada, em parte mecânica: quanto mais releases, maior a chance de alguma delas ser corretiva e cair dentro dos 7 dias seguintes. Portanto não esperamos confirmar a tese do DORA de que velocidade e estabilidade andam juntas; esperamos ausência de trade-off claro, e não uma relação inversa forte.

### RQ06 — Características dos repositórios

**Pergunta:** Quais características dos repositórios estão associadas a um melhor desempenho DORA?

**Hipótese:** Esperamos que o número de contribuidores esteja associado a maior frequência de deploy (mais gente, mais releases), e que o tipo do projeto importe: aplicações, serviços e ferramentas CLI devem publicar com mais frequência que bibliotecas e frameworks, que costumam agrupar mudanças em versões semânticas. Esperamos pouca ou nenhuma associação com popularidade (estrelas), e diferenças de linguagem ligadas a convenções de cada ecossistema. Depois da correção de Holm esperamos que só uma minoria dos testes continue significativa, com tamanhos de efeito pequenos a médios.

### RQ07 — Sensibilidade à definição

**Pergunta:** O quanto a classificação DORA de um repositório depende da definição operacional escolhida?

**Hipótese:** Esperamos que a classificação DORA dependa bastante da definição escolhida: pelo menos 40% dos repositórios devem mudar de categoria entre C1 e C3 (usar tags em vez de releases altera muito a frequência) e o kappa ponderado deve ficar abaixo de 0,6. Esperamos que C1 e C2 sejam mais parecidas entre si, já que pré-releases são raras, embora a troca das variantes de lead time e CFR já mude parte dos repositórios. Em resumo, a ordem relativa dos repositórios (quem é mais ou menos frequente) deve ser robusta, mas as faixas absolutas Elite/High/Medium/Low não.
