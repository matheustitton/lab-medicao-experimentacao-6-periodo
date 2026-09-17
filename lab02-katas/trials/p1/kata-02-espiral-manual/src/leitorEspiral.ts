/**
 * K2 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function emEspiral(matriz: number[][]): number[] {
  if (matriz.length === 0) return []

  const boundaries = {
    left: 0,
    right: matriz[0].length -1,
    top:0,
    bottom: matriz.length -1 
  }

  const result = []

  while(boundaries.top <= boundaries.bottom && boundaries.left <= boundaries.right){
    for(let i = boundaries.top; i <= boundaries.bottom; i++){
      result.push(matriz[i][boundaries.left])
    }
    boundaries.left++

    if(boundaries.left <= boundaries.right){
      for(let i = boundaries.left; i <= boundaries.right; i++){
        result.push(matriz[boundaries.bottom][i])
      }
      boundaries.bottom--
    }

    if(boundaries.top <= boundaries.bottom && boundaries.left <= boundaries.right) {
      for(let i = boundaries.bottom; i >= boundaries.top; i--){
        result.push(matriz[i][boundaries.right])
      }
      boundaries.right--
    }

    if(boundaries.left <= boundaries.right && boundaries.top <= boundaries.bottom){
      for(let i = boundaries.right; i >= boundaries.left; i--){
        result.push(matriz[boundaries.top][i])
      }
      boundaries.top++
    }
  }

  return result;
}
