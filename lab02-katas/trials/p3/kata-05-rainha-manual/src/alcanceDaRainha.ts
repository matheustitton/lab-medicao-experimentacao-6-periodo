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
  const bloqueadasValidas = new Set<string>();

  for (const [bl, bc] of bloqueadas) {
    if(bl < 0 || bl >= linhas || bc < 0 || bc >= colunas) continue;

    if (bl === rainha[0] && bc === rainha[1]) continue;

    bloqueadasValidas.add(JSON.stringify([bl, bc]));
  }

  const [rl, rc] = rainha;

  const direcoes: [number, number][] = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1],
    [-1, -1],
    [-1, 1],
    [1, -1],
    [1, 1]
  ];

  let total = 0;

  for (const [dL, dC] of direcoes) {
    let l = rl + dL;
    let c = rc + dC;

    while (l >= 0 && l < linhas && c >= 0 && c < colunas) {
      const key = JSON.stringify([l, c]);
      if(bloqueadasValidas.has(key)) break;
      total++;
      l += dL;
      c += dC;
    }
  }

  return total;
}
