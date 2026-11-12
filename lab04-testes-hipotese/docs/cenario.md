# Cenário do Lab04: par P1, t de Welch × Mann-Whitney

## Pergunta

Adotar um bot de revisão (CodeRabbit) muda o tempo até o merge dos PRs?

## Hipóteses

- **H₀:** o tempo até o merge tem a mesma distribuição com e sem bot.
- **H₁:** as distribuições diferem.

Cada teste olha H₀ de um jeito:

| Teste | O que compara | H₀ específica |
|---|---|---|
| t de Welch | médias, em horas, sem supor variâncias iguais | μ_sem_bot = μ_com_bot |
| Mann-Whitney | postos das observações | P(X > Y) = P(Y > X) |

**O teste é bicaudal** porque o bot pode acelerar a revisão, mas também pode atrasar o merge ao gerar retrabalho. Não havia razão para descartar uma das direções antes de ver os dados.

## Como os dados simulados são gerados

Os dois grupos seguem uma lognormal com o mesmo σ. O grupo com bot tem a mediana multiplicada por um fator `k`:

```
sem_bot ~ Lognormal(ln(mediana), σ)
com_bot ~ Lognormal(ln(mediana · k), σ)
```

`k = 1` significa H₀ verdadeira. `k ≠ 1` significa que existe efeito, de tamanho conhecido.

Os parâmetros vêm do grupo `sem_bot` dos dados reais, a situação anterior a qualquer efeito (`dados/parametros_simulacao.json`):

| Parâmetro | Valor | Origem |
|---|---|---|
| Mediana | 16,92 h | mediana real |
| σ do cenário-base | 1,64 | σ que reproduz a razão média/mediana real, pois média/mediana = exp(σ²/2) |
| σ amostral | 2,77 | desvio-padrão do log real, reservado para o cenário de cauda pesada da Q3 (S02) |
| n por grupo | 30 | tamanho da amostra real |

### Por que não usar o σ amostral no cenário-base

O desvio-padrão do log é inflado pelos PRs mergeados em minutos, como mostram os resumos por amostra de 30:

| Medida | Real (`sem_bot`) | Simulado, σ = 1,64 | Simulado, σ = 2,77 |
|---|---:|---:|---:|
| Média (h) | 65,0 | 55,0 | 307,0 |
| Desvio-padrão (h) | 110,6 | 98,7 | 887,7 |
| Máximo (h) | 470,1 | 453,5 | 4.313,4 |
| PRs com menos de 1 h | 20% | 4% | 15% |

Os valores simulados são a mediana de 20.000 amostras de 30 PRs (o percentual usa todas as observações). Com σ = 2,77, a cauda direita fica cerca de 10 vezes maior que a real, o que prejudicaria o Welch artificialmente, já que ele usa a escala em horas.

**Limitação:** com σ = 1,64, a lognormal não reproduz o excesso de PRs muito rápidos. Uma única lognormal não consegue acertar as duas caudas ao mesmo tempo. Priorizamos a cauda direita, que é a que afeta a média e a variância do Welch. O Mann-Whitney depende só da ordem dos dados e é sensível a σ de outro jeito, por isso a S02 repete a simulação com os dois valores.

## Situações simuladas na S02 (Q1, Q2 e Q3)

Cada situação roda 10.000 conjuntos para cada redução da mediana (0%, 10%, ..., 70%; `k = 1 − redução`), com α = 0,05 e 0,01. A redução 0% é o erro tipo I (Q1); as demais formam a curva de poder (Q2).

| Situação | σ | n por grupo | O que viola |
|---|---:|---:|---|
| Cenário-base | 1,64 | 30 | nada além da assimetria real |
| Cauda pesada | 2,77 | 30 | normalidade: poucos PRs enormes dominam média e variância |
| Outliers | 1,64 | 30 | 5% dos PRs "esquecidos" levam 20 vezes mais |
| Amostra pequena | 1,64 | 10 | o teorema central do limite ainda não ajuda o Welch |
| Quase simétrico (contraste) | 0,20 | 30 | nenhuma: é a situação mais favorável ao Welch |

O contraste não é o cenário real. Ele existe para mostrar em que condição a vantagem do Mann-Whitney deixaria de existir.

## Expectativa antes de simular

**Esperamos que o Mann-Whitney tenha mais poder que o Welch.** Os tempos são muito assimétricos, e poucos PRs longos inflam a variância que entra no denominador da estatística t, reduzindo a chance de detectar o efeito. O Mann-Whitney usa postos, então o maior PR da amostra tem o mesmo peso, seja de 100 h ou de 470 h.

Quanto ao erro tipo I, esperamos o Mann-Whitney perto de 5%, pois os dois grupos têm a mesma distribuição sob H₀. Esperamos o Welch abaixo de 5% (conservador) com n = 30, pela mesma inflação da variância.

Esta expectativa foi escrita antes das simulações da S02 e será comparada ao resultado na seção 7 do dashboard.
