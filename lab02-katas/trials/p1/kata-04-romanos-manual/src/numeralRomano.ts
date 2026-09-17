/**
 * K4 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function paraDecimal(romano: string): number {
  if (romano.length === 0)
    throw new RangeError("Numeral romano inválido: string vazia") 
  
  const VALUES: Record<string, number> = {
    I: 1,
    V: 5,
    X: 10,
    L: 50,
    C: 100,
    D: 500,
    M: 1000
  }

  const SMALL_SYMBOL = ["I", "X", "C", "M"]
  const BIG_SYMBOL = ["V", "L", "D", ""]

  for (const s of romano){
    if (!(s in VALUES))
      throw new RangeError(`Numeral romano inválido: símbolo "${s}"`)
  }

  let total = 0;
  let index = romano.length - 1;

  for (let c = 0; c <= 3 && index >= 0; c++){
    const small = SMALL_SYMBOL[c]
    const big = BIG_SYMBOL[c]
    const nextSmall = c < 3 ? SMALL_SYMBOL[c +1] : ""

    if (index >= 1 && romano[index - 1] === small && (romano[index] === big || romano[index] === nextSmall)){
      total += VALUES[romano[index]] - VALUES[small]
      index -= 2;
      continue
    }

    let repeats = 0;
    while(index >= 0 && romano[index] === small){
      repeats++;
      if (repeats > 3)
        throw new RangeError(`Numeral romano inválido: "${small}" repetido mais de três vezes`)

      total += VALUES[small]
      index--;
    }

    if(index >= 0 && big !== "" && romano[index] === big){
      total += VALUES[big];
      index--;
    }
  }

  if (index >= 0)
    throw new RangeError(`Numeral romano inválido: "${romano}"`)

  return total
}
