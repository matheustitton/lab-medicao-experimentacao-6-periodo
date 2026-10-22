# Discussão

> Texto da seção 4 do artigo: hipóteses (escritas antes de ver os dados, em `docs/hipoteses_*.md`) contra os resultados.

## 4.1 Hipóteses contra resultados

| RQ | O que esperávamos | O que encontramos | Veredito |
|---|---|---|---|
| RQ01 | mediana entre 1/mês e 1/semana; poucos Elite | 0,38 releases/semana (Medium); 3 Elite (1,1%) | confirmada |
| RQ02 | (b) bem menor que (a); (a) em semanas, (b) em dias; mais releases, menos espera | (a) 9,8 dias e (b) 8,9 dias, ambos Medium; (a) > (b) em só 63% dos repositórios; ρ com a frequência de −0,59 e −0,50 | parcial |
| RQ03 | CFR (a) entre 10% e 30%; CFR (b) menor que o (a), com muitos zeros; variantes pouco correlacionadas | CFR (a) 5,3%; CFR (b) 40,0% e maior que o (a) em 78% dos repositórios; só 14% dos repositórios com CFR (b) zero; ρ = 0,24 | só a última confirmada |
| RQ04 | assimétrica, mediana de horas a poucos dias; censura não desprezível | mediana de 3,2 horas, cauda longa; censura de 0,7% dos episódios (7% dos repositórios com 10% ou mais) | parcial |
| RQ05 | ρ(a) perto de zero; ρ(b) positivo, fraco a moderado, em parte mecânico | ρ(a) = 0,25 (fraco); ρ(b) = 0,73 (forte) | direção certa, intensidade subestimada |
| RQ06 | contribuidores e tipo do projeto importam para a frequência; estrelas não; poucos testes sobrevivem a Holm, com efeitos de pequenos a médios | 9 de 30 sobrevivem; contribuidores e idade importam para o lead time, não para a frequência; estrelas e tipo não; efeitos médios a grandes | parcial |
| RQ07 | classificação muda bastante (≥ 40% entre C1 e a combinação com tags); κ < 0,6; C1 e C2 parecidas; ordem relativa robusta, faixas não | 19% a 45% mudam; κ de 0,37 a 0,76; C1 × C2 é o par **mais** diferente; ρ de 0,53 a 0,82 | parcial |

## 4.2 O que surpreendeu e por quê

**O CFR (a) é baixo e o CFR (b) é alto.** Esperávamos o contrário, porque uma falha de pipeline é barata e uma release corretiva é cara. O CFR (a) tem mediana de 5%, ou seja, o CI do branch principal desses repositórios quase sempre passa. O CFR (b) tem mediana de 40% porque a heurística é frouxa (precisão de 0,60) e porque o critério de 7 dias é fácil de cumprir para quem publica seguido: basta uma release de patch com um commit de correção logo depois. (Explicações que não testamos: o CI do branch principal falha pouco porque os testes já rodaram nos pull requests, e releases de patch curtas são comuns nesses projetos.) Por isso o CFR (b) é, na prática, um indicador do ritmo de releases mais do que de falhas, e é a razão da correlação forte com a frequência na RQ05. **Não** concluímos que esses projetos falham 40% das vezes.

**Velocidade e estabilidade andam juntas?** Os dados não confirmam o DORA, mas também não permitem a conclusão oposta. Com o CFR (a), a relação é fraca e positiva (ρ = 0,25): repositórios que publicam mais também falham um pouco mais no CI. Os repositórios jovens, que são os mais frequentes, têm CFR (b) muito maior (0,74 contra 0,23 nos mais velhos), o que reforça o efeito mecânico. Uma interpretação, que estes dados não testam, é que o DORA mede equipes de uma organização, enquanto aqui cada repositório é um projeto de código aberto em que a frequência de releases reflete o estilo de versionamento (por exemplo, publicar uma versão a cada correção) mais do que uma prática de entrega contínua.

**A idade importa mais do que a popularidade.** Os fatores mais associados ao desempenho foram a idade (efeito grande em quatro métricas) e o número de contribuidores (lead time), e não as estrelas nem a linguagem. Repositórios jovens publicam mais (0,81 releases/semana) e esperam menos (27 horas de lead time (a) contra 733 nos mais velhos). Parte disso é um artefato de medição: um repositório com menos de um ano não pode ter commits com mais de um ano. Excluindo os 40 repositórios com menos de um ano, a associação diminui, mas permanece: ρ = −0,34 com a frequência e +0,38 com o lead time (a). Repositórios com mais contribuidores também têm lead time maior (693 contra 93 horas), mas não separamos o efeito do número de contribuidores do efeito da idade, porque os fatores foram testados um de cada vez.

**A definição operacional muda a resposta.** A mudança de categoria entre definições chega a 45% dos repositórios (C1 × C2), e o par mais diferente envolve a variante do CFR e as pré-releases. O que mais pesa é a variante do CFR: as combinações com o CFR (a) (C1 e C3) têm 21 e 23 repositórios Elite, e as com o CFR (b) (C2 e C4) têm 4 e 2. Trocar só o lead time de (a) para (b) muda 19% das classificações, e trocar só o CFR de (a) para (b) muda 36%. A **ordem relativa** dos repositórios é mais estável (ρ de 0,53 a 0,82), então rankings são mais confiáveis do que a faixa absoluta Elite/High/Medium/Low. A RQ01 é robusta à inclusão de pré-releases (a mediana passa de 0,38 para 0,46 por semana e só 8% dos repositórios mudam de faixa de frequência). A RQ05, por outro lado, depende da variante do CFR, e as classificações da RQ07 dependem das definições.

## 4.3 Ameaças à validade

**De construto.** Release não é deploy: projetos com entrega contínua publicam releases raramente, e projetos que versionam muito (por exemplo, uma release por correção) parecem rápidos. O CFR (a) mede falha de pipeline, e não falha em produção. O CFR (b) depende da heurística de release corretiva, cuja F1 é de 0,704 na amostra-ouro e de 0,697 por validação cruzada, com precisão de 0,60; ele deve ser lido como limite superior. A dimensão "as releases são entregas reais" teve kappa de 0,12 por desbalanceamento (58 de 60 repositórios "sim"), então não validamos que releases representam entregas para os projetos que não foram rotulados. O lead time usa `commit.author.date`, que *rebases* e *squash merges* distorcem (22 repositórios com commits posteriores à release); 12% das releases (1.659) não trouxeram commits e ficam fora do lead time.

**Interna.** A idade limita o lead time dos repositórios jovens e confunde a associação com a frequência e o CFR (b); mostramos o resultado sem os 40 repositórios com menos de um ano, mas não ajustamos por regressão. Contribuidores, idade e frequência estão correlacionados entre si, então os testes por fator (um de cada vez) não separam seus efeitos.

**Externa.** A amostra tem 270 repositórios, abaixo dos 300 exigidos, porque a coleta parou antes de atingir o alvo. Foram examinados 1.391 dos 8.499 candidatos, em ordem pseudoaleatória, e os repositórios sorteados são os que passaram nos três filtros (Actions, 5 ou mais releases, 50 ou mais runs); descartamos 592 por terem poucas releases (43% dos examinados), que são justamente projetos com baixa frequência de entrega. Os candidatos vêm da busca por estrelas (mais de 1.000), então os resultados valem para projetos populares de código aberto no GitHub e não para equipes corporativas. A janela de 12 meses é única, e a coleta foi feita em 14 e 15 de outubro de 2026.

**De conclusão.** O RQ06 faz 30 testes; usamos Holm, mas o tipo do projeto tem 60 repositórios em 4 grupos (um com 6), com baixo poder estatístico. Os grupos de linguagem variam de 16 a 73 repositórios (mais "Outras", com 53). As diferenças em RQ06 são associações, não causas. Não corrigimos a precisão da heurística ao estimar o CFR (b). A tag como unidade de entrega, parte da RQ07, não foi coletada.

## 4.4 Replicação cruzada

A ser preenchida na entrega final, depois de executar o pipeline de outro grupo (seção 9 do enunciado).
