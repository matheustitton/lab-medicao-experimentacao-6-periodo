/**
 * K1 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function comprimir(valores: number[]): string {
  if (valores.length === 0) return "";

  const unicos = [...new Set(valores)];
  const resultado: string[] = [];

  let inicio = unicos[0];
  let fim = inicio;

  for (let i = 1; i <= unicos.length; i++) {
    const atual = unicos[i];

    if (atual === fim + 1) {
      fim = atual;
      continue;
    }

    if (fim - inicio >= 2) {
      resultado.push(`${inicio}..${fim}`);
    } else if (fim === inicio) {
      resultado.push(`${inicio}`);
    } else {
      resultado.push(`${inicio}`, `${fim}`);
    }

    inicio = atual;
    fim = atual;
  }

  return resultado.join(",");
}
