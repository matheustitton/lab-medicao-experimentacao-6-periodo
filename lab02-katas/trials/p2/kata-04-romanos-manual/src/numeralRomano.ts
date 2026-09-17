/**
 * K4 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function paraDecimal(romano: string): number {
  if (romano.length === 0) {
    throw new RangeError("Numeral romando inválido.");
  }

  const valores: Record<string, number> = {
    I: 1,
    V: 5,
    X: 10,
    L: 50,
    C: 100,
    D: 500,
    M: 1000,
  };

  for (const simbolo of romano) {
    if (!(simbolo in valores)) {
      throw new RangeError("Numeral romano invalido.");
    }
  }

  for (const simbolo of ["V", "L", "D"]) {
    if (romano.split(simbolo).length - 1 > 1) {
      throw new RangeError("Numeral romano inválido.");
    }
  }

  if (/(I{4,}|X{4,}|C{4,}|M{4,})/.test(romano)) {
    throw new RangeError("Numeral romano inválido.");
  }

  const subtracoesPermitidas = new Set(["IV", "IX", "XL", "XC", "CD", "CM"]);

  let resultado = 0;
  let i = 0;

  while (i < romano.length) {
    const atual = romano[i];
    const proximo = romano[i + 1];

    if (proximo !== undefined && valores[atual] < valores[proximo]) {
      const par = atual + proximo;
      if (!subtracoesPermitidas.has(par)) {
        throw new RangeError("Numeral romano inválido.");
      }

      resultado += valores[proximo] - valores[atual];

      i += 2;
    } else {
      resultado += valores[atual];
      i++;
    }
  }

  // Validação estrutural adicional:
  // o numeral deve corresponder à forma romana canônica.
  const milhares = ["", "M", "MM", "MMM"];
  const centenas = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"];
  const dezenas = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"];
  const unidades = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"];

  if (resultado < 1 || resultado > 3999) {
    throw new RangeError("Numeral romano inválido.");
  }

  const canonico =
    milhares[Math.floor(resultado / 1000)] +
    centenas[Math.floor((resultado % 1000) / 100)] +
    dezenas[Math.floor((resultado % 100) / 10)] +
    unidades[resultado % 10];

  if (romano !== canonico) {
    throw new RangeError("Numeral romano inválido.");
  }

  return resultado;
}
