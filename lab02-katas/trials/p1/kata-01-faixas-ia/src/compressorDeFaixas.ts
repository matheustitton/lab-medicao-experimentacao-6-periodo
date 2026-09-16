/**
 * K1 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function comprimir(valores: number[]): string {
  // Regra 3: como a entrada é não decrescente, basta remover repetições adjacentes.
  const unicos = valores.filter((v, i) => i === 0 || v !== valores[i - 1]);

  const partes: string[] = [];
  let inicio = 0;

  while (inicio < unicos.length) {
    // Avança enquanto o próximo valor for exatamente o atual + 1.
    let fim = inicio;
    while (fim + 1 < unicos.length && unicos[fim + 1] === unicos[fim] + 1) {
      fim++;
    }

    const tamanho = fim - inicio + 1;
    if (tamanho >= 3) {
      // Regra 1: 3 ou mais consecutivos viram "primeiro..ultimo".
      partes.push(`${unicos[inicio]}..${unicos[fim]}`);
    } else {
      // Regra 2: 1 ou 2 valores são escritos um a um.
      for (let k = inicio; k <= fim; k++) {
        partes.push(String(unicos[k]));
      }
    }

    inicio = fim + 1;
  }

  // Regra 4: entrada vazia resulta em "" naturalmente.
  return partes.join(",");
}