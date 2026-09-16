export function emEspiral(matriz: number[][]): number[] {
  if (matriz.length === 0 || matriz[0].length === 0) {
    return [];
  }

  const resultado: number[] = [];

  let topo = 0;
  let base = matriz.length - 1;
  let esquerda = 0;
  let direita = matriz[0].length - 1;

  while (topo <= base && esquerda <= direita) {
    // Desce pela primeira coluna
    for (let linha = topo; linha <= base; linha++) {
      resultado.push(matriz[linha][esquerda]);
    }
    esquerda++;

    // Vai para a direita pela última linha
    if (topo <= base && esquerda <= direita) {
      for (let coluna = esquerda; coluna <= direita; coluna++) {
        resultado.push(matriz[base][coluna]);
      }
      base--;
    }

    // Sobe pela última coluna
    if (esquerda <= direita && topo <= base) {
      for (let linha = base; linha >= topo; linha--) {
        resultado.push(matriz[linha][direita]);
      }
      direita--;
    }

    // Vai para a esquerda pela primeira linha
    if (topo <= base && esquerda <= direita) {
      for (let coluna = direita; coluna >= esquerda; coluna--) {
        resultado.push(matriz[topo][coluna]);
      }
      topo++;
    }
  }
  return resultado;
}