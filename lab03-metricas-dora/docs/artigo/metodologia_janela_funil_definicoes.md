# Metodologia — fonte de dados, janela, funil de seleção e definições operacionais

> Texto da seção 2 do artigo (SBC, máx. 10 páginas no total), com os números da coleta real (`data/saida/funil_selecao.md`).

## 2.1 Fonte de dados

Todos os dados vêm da API REST do GitHub, acessada por um cliente HTTP escrito pelo grupo (sem bibliotecas prontas de acesso à API). Foram usados os endpoints de busca de repositórios, workflows, releases, comparação de commits (`compare`), workflow runs e contribuidores. A coleta foi executada em 14 e 15 de outubro de 2026 com token autenticado, e todas as respostas ficam em um cache local, o que torna a coleta retomável e auditável.

## 2.2 Janela de observação

A janela tem 12 meses, de 1º de outubro de 2025 a 30 de setembro de 2026 (UTC), fixada pelo professor. Só entram nos cálculos releases publicadas e workflow runs criados dentro dela. A primeira release da janela pode ter como release anterior uma publicada antes do início; isso é permitido apenas para obter os commits que ela inclui.

## 2.3 Seleção dos repositórios e funil

**Candidatos.** A Search API devolve no máximo 1.000 resultados por consulta. Para contornar esse limite, a busca foi fatiada em faixas de estrelas (`stars:1000..1199`, `1200..1499`, ..., `>=50000`), sempre com `fork:false archived:false`. Os resultados das faixas foram unidos sem duplicatas. Os candidatos são repositórios com mais de 1.000 estrelas.

**Ordem de processamento.** Os candidatos foram processados em ordem pseudoaleatória reprodutível (ordenação por hash SHA-256 de `semente:repositório`, com semente 42), até atingir o alvo da amostra. Isso evita que a amostra seja dominada pelos repositórios mais estrelados, mas a amostra continua restrita aos candidatos devolvidos pela busca (veja a ameaça de validade externa).

**Filtros, na ordem:**
1. o repositório usa GitHub Actions (`total_count > 0` em `/actions/workflows`);
2. tem pelo menos 5 releases principais publicadas na janela (rascunhos e pré-releases não contam);
3. tem pelo menos 50 workflow runs válidos (`success` ou falha, ver 2.4) no default branch, evento `push`, dentro da janela.

**Funil.** A tabela abaixo é gerada automaticamente pelo pipeline (`data/saida/funil_selecao.md`).

A busca devolveu **8.499 candidatos**. O pipeline os processa em ordem pseudoaleatória e parou ao chegar a **270 repositórios na amostra final**, depois de examinar **1.391** candidatos (os outros 7.108 não foram examinados). O alvo de 350 não foi alcançado e o mínimo de 300 do enunciado também não; as análises usam os 270 repositórios disponíveis (ver ameaças à validade). Como os candidatos foram examinados em ordem aleatória, as taxas de passagem abaixo estimam o que aconteceria com os 8.499.

| Etapa | Repositórios |
|---|---|
| candidatos devolvidos pela busca (≥ 1.000 estrelas) | 8.499 |
| examinados antes de a coleta parar | 1.391 |
| usam GitHub Actions | 941 |
| ≥ 5 releases na janela | 349 |
| ≥ 50 workflow runs válidos (amostra final) | 270 |

| Motivo de descarte (entre os 1.391 examinados) | Repositórios |
|---|---|
| não usam GitHub Actions (`sem_actions`) | 450 |
| menos de 5 releases na janela (`releases_insuficientes`) | 592 |
| menos de 50 workflow runs válidos (`runs_insuficientes`) | 78 |
| em processamento quando a coleta parou | 1 |

Entre os examinados, 68% usam Actions (941 de 1.391); entre os que usam, 37% têm releases suficientes (349 de 941); entre esses, 77% têm runs suficientes (270 de 349).

## 2.4 Definições operacionais

| Conceito | Definição adotada |
|---|---|
| Deploy | release publicada (`draft = false`, `prerelease = false`) |
| Branch | apenas o `default_branch` do repositório |
| Data de um commit | `commit.author.date` |
| Execuções de CI | workflow runs com `event = push` no default branch |
| Sucesso | `conclusion = success` |
| Falha | `failure`, `timed_out`, `startup_failure` |
| Ignorado | `cancelled`, `skipped`, `neutral`, `action_required`, `stale` ou vazio; não entra em nenhum cálculo, mas é contado (`n_runs_ignorados`) |
| Censura | medições cujo evento final não ocorre na janela são mantidas e contadas, nunca descartadas |

**Métricas e variantes calculadas nesta etapa** (todas no mesmo dataset, uma linha por repositório):

- **Frequência de deploy (RQ01):** releases na janela ÷ 52,1 semanas.
- **Lead time (RQ02):** variante (a), por release: data da release menos o commit mais antigo incluído nela; variante (b), por commit: um valor por commit. Em ambas, a mediana do repositório é calculada sobre as releases (a) ou sobre todos os commits (b). A primeira release da história é ignorada.
- **CFR (RQ03):** variante (a), por CI: falhas ÷ (falhas + sucessos); variante (b), por entrega: releases seguidas, em até 7 dias, por uma release corretiva ÷ releases avaliadas. As releases dos últimos 7 dias da janela ficam fora do denominador (censura).
- **Tempo de recuperação (RQ04):** por workflow, um episódio começa na primeira falha após um sucesso e termina no próximo sucesso do mesmo workflow; tempo = `updated_at` do sucesso menos `run_started_at` da falha. Reportamos a mediana dos episódios concluídos e, separadamente, a mediana que inclui os censurados como limite inferior.
- **Classificação DORA (RQ07, combinação C1):** cada métrica recebe 4 (Elite), 3 (High), 2 (Medium) ou 1 (Low) pelos cortes da disciplina; a classe geral é a mediana dos pontos, arredondada para baixo. Métricas sem valor ficam fora da mediana.

As combinações da RQ07 (C1 a C4) estão descritas na seção de resultados e usam o arquivo `data/saida/dataset_sensibilidade.csv`. A coleta **não baixou as tags** do GitHub, então a combinação com tags como unidade de entrega do exemplo do enunciado não pôde ser calculada.

## 2.5 Estatística descritiva

Em todas as RQs reportamos mediana e intervalo interquartil (IQR), e não média e desvio-padrão, porque as distribuições dessas métricas são muito assimétricas.
