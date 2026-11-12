# Roteiro da apresentação (7 minutos, 15 perguntas)

**Regras:** respostas curtas (até 30 s, umas 60 a 70 palavras), sempre com o dashboard aberto na seção indicada. Cada um responde 5 perguntas, mas qualquer um pode ser chamado para qualquer pergunta: todos devem ler o roteiro inteiro.

| Quem | Perguntas | Seções do dashboard |
|---|---|---|
| **Murilo** | 1, 2, 3, 4, 11 | 1, 2, 4/5 |
| **Matheus** | 5, 6, 7, 10, 15 | 3, 5, 7 |
| **Pedro** | 8, 9, 12, 13, 14 | 4, 5, 6, 7 |

## Antes de começar (2 min antes)
- Abrir o dashboard publicado (ou rodar `python rodar.py`) **e** deixar uma cópia local aberta, caso a internet falhe (o Plotly vem da CDN; sem internet os gráficos não aparecem).
- Zoom do navegador em ~110%, botões de α do G3 e do G4 em **α = 0,05**.
- Abertura (Murilo, 10 s): "Somos Murilo, Matheus e Pedro. Comparamos o t de Welch e o Mann-Whitney para saber se um bot de revisão muda o tempo até o merge."

---

## Murilo

**1. Qual é o cenário e o que H₀ e H₁ afirmam?** · *Seção 1*
> Queremos saber se adotar o CodeRabbit, um bot que revisa PRs, muda o tempo até o merge no repositório formbricks. H₀ diz que o tempo até o merge tem a mesma distribuição com e sem bot. H₁ diz que as distribuições são diferentes. Cada teste lê isso do seu jeito: o Welch pergunta se as médias são iguais, e o Mann-Whitney pergunta se um grupo tende a ter valores maiores que o outro.

**2. O teste é unicaudal ou bicaudal? Por quê?** · *Seção 1*
> Bicaudal. O bot pode acelerar o merge, porque adianta a revisão, mas também pode atrasar, porque os comentários dele geram retrabalho. Decidimos isso antes de ver os dados. Na prática, os 5% de α ficam divididos: 2,5% em cada ponta da distribuição, como aparece no G2.

**3. Como os dados reais foram coletados e o que mostraram sobre a forma da distribuição?** · *Seção 2, G1 + tabela*
> Pela API de busca do GitHub: 30 PRs mergeados antes do bot, até 18/08/2024, e 30 depois, a partir de 01/11/2024. Excluímos a transição, em que o bot comentava só em parte dos PRs, e o Hacktoberfest. Medimos as horas entre abrir e mergear. Os dados são muito assimétricos: sem bot, a média é 65 h e a mediana 16,9 h, quase 4 vezes menor. O mais longo levou 470 h, e 20% saíram em menos de uma hora.

**4. Como os dados reais ajudaram a escolher os parâmetros da simulação?** · *Seção 2, texto abaixo do G1*
> Usamos uma lognormal, porque os tempos são positivos e assimétricos. A mediana veio direto do grupo sem bot: 16,9 h. O σ = 1,64 é o que reproduz a razão real entre média e mediana. O desvio-padrão do log real, 2,77, daria uma média teórica de centenas de horas, muito acima dos 65 h reais, então ele virou o cenário de cauda pesada. E n = 30, igual ao real.

**11. Que violação de pressuposto simularam, e por que afeta mais um teste?** · *Seção 5, G4 (painéis) ou seção 4, G3*
> Três: cauda pesada, com σ = 2,77; outliers, com 5% dos PRs levando 20 vezes mais; e amostra pequena, com 10 PRs por grupo. Todas afetam mais o Welch, porque ele usa média e variância em horas: um único PR gigante muda as duas. O Mann-Whitney só usa a ordem: o maior PR é só "o maior", tanto faz se levou 100 h ou 4.000 h. Na cauda pesada o poder do Welch quase não sai de 5%.

## Matheus

**5. O que cada teste compara de fato?** · *Seção 3*
> O Welch compara médias: pega a diferença entre as médias dos dois grupos e divide pelo erro-padrão, sem supor que as variâncias sejam iguais. O Mann-Whitney compara postos: junta os 60 PRs, ordena do mais rápido ao mais lento e conta quantas vezes um PR sem bot fica acima de um PR com bot. Por isso ele responde se um grupo tende a ser mais lento, não se as médias diferem.

**6. No G2, o que é a distribuição da estatística sob H₀ e por que a região de rejeição fica onde fica?** · *Seção 3, G2*
> É como a estatística se comportaria se o bot não fizesse diferença: uma t com cerca de 48 graus de liberdade no Welch e uma normal padrão no Mann-Whitney. A região de rejeição fica nas duas pontas, além de ±2,01 e ±1,96, porque o teste é bicaudal e são os valores que só aparecem 5% das vezes sob H₀. O histograma cinza é a simulação: no Welch ele não acompanha a curva, e isso já antecipa o problema.

**7. O que significa o p-valor do exemplo do G2, e o que ele não significa?** · *Seção 3, área colorida do G2 e tabela do exemplo*
> No exemplo, o Mann-Whitney deu p = 0,070: se H₀ fosse verdadeira, uma estatística tão extrema ou mais apareceria em 7% dos conjuntos. É a área colorida. Ele não é a probabilidade de H₀ ser verdadeira, nem a chance de o bot não funcionar, nem mede o tamanho do efeito. Inclusive, nesse exemplo o efeito existia, porque nós simulamos um bot que corta a mediana pela metade, e os dois testes erraram: erro tipo II.

**10. No G4, qual teste tem mais poder? A diferença muda com o tamanho do efeito?** · *Seção 5, G4*
> O Mann-Whitney, em todas as situações assimétricas, e a distância cresce com o efeito. No cenário-base, com a mediana cortada pela metade, ele detecta 35% das vezes, contra 14% do Welch. A vantagem só muda de lado no contraste quase simétrico, e por pouco: com 10% de redução, 50% do Welch contra 49% do Mann-Whitney. Nenhum dos dois chega a 80% com n = 30 nas situações realistas.

**15. Qual teste recomendam, quando mudariam e qual a principal limitação?** · *Seção 7*
> Recomendamos o Mann-Whitney para o tempo até o merge: ele mantém o erro tipo I perto de 5% e tem mais poder em todas as situações realistas. Mudaríamos para o Welch se a pergunta fosse sobre a média, por exemplo o total de horas que a equipe espera, ou se os dados fossem quase simétricos. A principal limitação é que o estudo real é antes e depois, sem grupo de controle, e com só 30 PRs por grupo.

## Pedro

**8. No cenário, o que seria um erro tipo I e um erro tipo II? Qual é mais grave?** · *Seção 4 (sem gráfico específico)*
> Erro tipo I é concluir que o bot muda o tempo de merge quando ele não muda. Erro tipo II é o bot mudar o tempo e a gente não detectar. Para nós o tipo I é mais grave: ele leva a equipe a manter ou a recomendar uma ferramenta paga por um efeito que não existe. Mas o tipo II é o mais provável aqui, porque com 30 PRs o poder é baixo.

**9. No G3, algum teste se afastou de 5%? Ficou liberal ou conservador, e por quê?** · *Seção 4, G3*
> O Welch, em todas as situações assimétricas, sempre para baixo: 2,7% no cenário-base e só 1,0% na cauda pesada. Ou seja, conservador. Um PR muito longo entra ao mesmo tempo na diferença de médias e no erro-padrão, então o t quase nunca fica grande. O Mann-Whitney ficou entre 4,3% e 4,9%, dentro da faixa do acaso, exceto com n = 10, em que ficou levemente abaixo.

**12. Com α = 0,01 em vez de 0,05, o que mudaria no G3 e no G4?** · *Seção 4 e 5: **clicar no botão α = 0,01** nos dois gráficos*
> [clicar] No G3, a linha de referência desce para 1%, e o Mann-Whitney acompanha, perto de 1%; o Welch vai para quase zero. No G4, todas as curvas caem: no cenário-base, com a mediana pela metade, o poder do Mann-Whitney vai de 35% para 15%, e o do Welch de 14% para 2%. Erramos menos alarmes falsos, mas deixamos passar mais efeitos reais. [voltar para α = 0,05]

**13. A simulação confirmou o que o grupo esperava?** · *Seção 7, primeiro e segundo parágrafos*
> Confirmou. Esperávamos o Mann-Whitney com mais poder e o Welch conservador, e foi isso, só que mais forte: o Welch ficou entre 1% e 2,7% de erro tipo I. O que não esperávamos estava nos dados reais: as médias com e sem bot são praticamente iguais, 65 h, mas a mediana caiu 34%. É um caso real em que os dois testes medem coisas diferentes.

**14. Nos dados reais, os testes chegaram à mesma conclusão? O efeito tem importância prática?** · *Seção 6, tabela + "Para discutir"*
> Sim, nenhum rejeitou H₀: p = 0,99 no Welch e 0,64 no Mann-Whitney, com efeitos desprezíveis. A mediana caiu de 16,9 h para 11,2 h, mas o intervalo de confiança vai de 36 h mais rápido a 27 h mais lento, então não dá para afirmar importância prática. E isso não prova que o bot não funciona: com 30 PRs, o Mann-Whitney detectaria esse efeito só 15% das vezes. Precisaríamos de 200 a 300 PRs por grupo.

---

## Se o professor perguntar além do roteiro
- **Por que 10.000 repetições?** A margem de erro da proporção fica em ±0,43 ponto percentual (a faixa cinza do G3).
- **Por que não usar o σ amostral no cenário-base?** Geraria médias de centenas de horas, 10 vezes a cauda real, e prejudicaria o Welch artificialmente.
- **Reprodutibilidade:** semente 42 em tudo; `python rodar.py` gera os mesmos arquivos byte a byte.
- **O não paramétrico sempre ganha?** Não: no contraste quase simétrico, o Welch empata ou ganha por pouco.

## Cronometragem sugerida
15 respostas × ~25 s ≈ 6 min 15 s + abertura e transições ≈ 7 min. Se estourar, encurte primeiro as perguntas 3 e 11 (são as mais longas).
