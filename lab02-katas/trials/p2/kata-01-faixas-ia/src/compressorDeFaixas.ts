export function comprimir(valores: number[]): string {
  if (valores.length === 0) {
    return "";
  }

  const unicos = [...new Set(valores)];

  const resultado: string[] = [];

  let inicio = unicos[0];
  let anterior = unicos[0];

  for (let i = 1; i <= unicos.length; i++) {
    const atual = unicos[i];

    if (atual === anterior + 1) {
      anterior = atual;
      continue;
    }

    const tamanho = anterior - inicio + 1;

    if (tamanho >= 3) {
      resultado.push(`${inicio}..${anterior}`);
    } else if (tamanho === 2) {
      resultado.push(`${inicio}`, `${anterior}`);
    } else {
      resultado.push(`${inicio}`);
    }

    inicio = atual;
    anterior = atual;
  }

  return resultado.join(",");
}