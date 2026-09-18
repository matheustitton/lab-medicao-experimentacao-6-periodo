/**
 * K2 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Não altere a assinatura exportada: a suite de aceitação depende dela.
 */
export function emEspiral(matriz: number[][]): number[] {
  if (matriz.length === 0) return [];

  const resultado: number[] = [];
  let top = 0;
  let bottom = matriz.length - 1;
  let left = 0;
  let right = matriz[0].length - 1;

  while (top <= bottom && left <= right) {
    // 1. Descer a primeira coluna (left) de top a bottom
    for (let row = top; row <= bottom; row++) {
      resultado.push(matriz[row][left]);
    }
    left++;

    // 2. Avançar pela última linha (bottom) de left a right
    if (top <= bottom) {
      for (let col = left; col <= right; col++) {
        resultado.push(matriz[bottom][col]);
      }
      bottom--;
    }

    // 3. Subir a última coluna (right) de bottom a top
    if (left <= right) {
      for (let row = bottom; row >= top; row--) {
        resultado.push(matriz[row][right]);
      }
      right--;
    }

    // 4. Voltar pela primeira linha (top) de right a left
    if (top <= bottom) {
      for (let col = right; col >= left; col--) {
        resultado.push(matriz[top][col]);
      }
      top++;
    }
  }

  return resultado;
}
