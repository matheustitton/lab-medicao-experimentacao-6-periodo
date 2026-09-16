/**
 * K5 do Lab02. Implementação conforme o ENUNCIADO.md.
 * Não altera a assinatura exportada: a suite de aceitação depende dela.
 */
export function casasAlcancaveis(
  linhas: number,
  colunas: number,
  rainha: [number, number],
  bloqueadas: [number, number][],
): number {
  const bloqueadasSet = new Set<string>();
  for (const [l, c] of bloqueadas) {
    if (l >= 0 && l < linhas && c >= 0 && c < colunas) {
      bloqueadasSet.add(`${l},${c}`);
    }
  }

  const [rLinha, rColuna] = rainha;
  bloqueadasSet.delete(`${rLinha},${rColuna}`);

  const direcoes = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1],
    [-1, -1],
    [-1, 1],
    [1, -1],
    [1, 1],
  ];

  let total = 0;

  for (const [dLinha, dColuna] of direcoes) {
    let linha = rLinha + dLinha;
    let coluna = rColuna + dColuna;

    while (
      linha >= 0 &&
      linha < linhas &&
      coluna >= 0 &&
      coluna < colunas &&
      !bloqueadasSet.has(`${linha},${coluna}`)
    ) {
      total++;
      linha += dLinha;
      coluna += dColuna;
    }
  }

  return total;
}