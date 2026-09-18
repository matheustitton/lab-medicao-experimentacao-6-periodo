/**
 * K4 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Não altere a assinatura exportada: a suite de aceitação depende dela.
 */
export function paraDecimal(romano: string): number {
  // Valores dos símbolos
  const valores: Record<string, number> = {
    I: 1,
    V: 5,
    X: 10,
    L: 50,
    C: 100,
    D: 500,
    M: 1000,
  };

  const simbolos = new Set(['I', 'V', 'X', 'L', 'C', 'D', 'M']);
  const subtrativoPermitido = new Set(['IV', 'IX', 'XL', 'XC', 'CD', 'CM']);

  // 1. Validar vazio
  if (romano.length === 0) {
    throw new RangeError('String vazia');
  }

  // 2. Validar caracteres (apenas I, V, X, L, C, D, M em maiúsculas)
  for (const char of romano) {
    if (!simbolos.has(char)) {
      throw new RangeError(`Caractere inválido: ${char}`);
    }
  }

  // 3. Validar máximo 3 repetições de I, X, C, M
  for (const char of ['I', 'X', 'C', 'M']) {
    if (romano.includes(char + char + char + char)) {
      throw new RangeError(`Repetição não permitida: ${char}${char}${char}${char}`);
    }
  }

  // 4. Validar que V, L, D não se repetem
  for (const char of ['V', 'L', 'D']) {
    let count = 0;
    for (const c of romano) {
      if (c === char) count++;
      if (count > 1) {
        throw new RangeError(`${char} repetido`);
      }
    }
  }

  // 5. Validar subtrações permitidas
  for (let i = 0; i < romano.length - 1; i++) {
    const par = romano[i] + romano[i + 1];
    const val1 = valores[romano[i]];
    const val2 = valores[romano[i + 1]];

    if (val1 < val2) {
      // É uma subtração
      if (!subtrativoPermitido.has(par)) {
        throw new RangeError(`Subtração não permitida: ${par}`);
      }
    }
  }

  // 6. Validar ordem e regras após subtração
  let i = 0;
  let ultimoValor = Infinity;
  let ultimoSubtrativoVal = Infinity;

  while (i < romano.length) {
    // Verificar se é um par subtrativo
    if (i < romano.length - 1) {
      const par = romano[i] + romano[i + 1];
      if (subtrativoPermitido.has(par)) {
        const val1 = valores[romano[i]];
        const val2 = valores[romano[i + 1]];
        const resultado = val2 - val1;

        // O par subtrativo deve estar em ordem decrescente em relação ao anterior
        if (resultado > ultimoValor) {
          throw new RangeError('Ordem inválida após subtração');
        }

        ultimoValor = resultado;
        ultimoSubtrativoVal = val1; // O menor valor do par
        i += 2;
        continue;
      }
    }

    const val = valores[romano[i]];

    // Após um par subtrativo, só pode vir símbolo com valor menor
    if (val >= ultimoSubtrativoVal && ultimoSubtrativoVal !== Infinity) {
      throw new RangeError('Ordem inválida após subtração');
    }

    // Ordem decrescente
    if (val > ultimoValor) {
      throw new RangeError('Ordem inválida');
    }

    ultimoValor = val;
    i++;
  }

  // 7. Converter para decimal
  let total = 0;
  i = 0;
  while (i < romano.length) {
    if (i < romano.length - 1) {
      const par = romano[i] + romano[i + 1];
      if (subtrativoPermitido.has(par)) {
        total += valores[romano[i + 1]] - valores[romano[i]];
        i += 2;
        continue;
      }
    }
    total += valores[romano[i]];
    i++;
  }

  return total;
}
