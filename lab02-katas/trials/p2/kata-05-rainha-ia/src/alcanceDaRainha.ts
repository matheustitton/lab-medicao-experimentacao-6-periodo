/**
 * K5 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function casasAlcancaveis(
  linhas: number,
  colunas: number,
  rainha: [number, number],
  bloqueadas: [number, number][],
): number {
  const [linhaRainha, colunaRainha] = rainha;

  const bloqueios = new Set<string>();

  for (const [linha, coluna] of bloqueadas) {
    if (
      linha >= 0 &&
      linha < linhas &&
      coluna >= 0 &&
      coluna < colunas &&
      !(linha === linhaRainha && coluna === colunaRainha)
    ) {
      bloqueios.add(`${linha},${coluna}`);
    }
  }

  const direcoes: [number, number][] = [
    [-1, 0],  // cima
    [1, 0],   // baixo
    [0, -1],  // esquerda
    [0, 1],   // direita
    [-1, -1], // diagonal superior esquerda
    [-1, 1],  // diagonal superior direita
    [1, -1],  // diagonal inferior esquerda
    [1, 1],   // diagonal inferior direita
  ];

  let resultado = 0;

  for (const [deltaLinha, deltaColuna] of direcoes) {
    let linha = linhaRainha + deltaLinha;
    let coluna = colunaRainha + deltaColuna;

    while (
      linha >= 0 &&
      linha < linhas &&
      coluna >= 0 &&
      coluna < colunas
    ) {
      if (bloqueios.has(`${linha},${coluna}`)) {
        break;
      }

      resultado++;

      linha += deltaLinha;
      coluna += deltaColuna;
    }
  }

  return resultado;
}