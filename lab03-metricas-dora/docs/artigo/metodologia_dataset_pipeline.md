# Metodologia — dataset e pipeline (Murilo)

Rascunho para o artigo. Cubra: arquitetura do pipeline (cliente, cache/retomada, rate limit, backoff),
como cada variante das métricas foi calculada, o dataset final (n de repositórios, colunas, ver
`docs/DICIONARIO_DADOS.md`), tratamento de censura e das limitações da API (teto de 1.000 runs, 404 no compare).
