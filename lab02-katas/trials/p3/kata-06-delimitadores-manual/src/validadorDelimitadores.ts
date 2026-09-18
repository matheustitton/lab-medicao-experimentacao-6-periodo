/**
 * K6 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function estaBalanceado(texto: string): boolean {
  const pilha: string[] = [];
  let dentroDeQuota = false;

  const pares: Record<string, string> = {
    ')': '(',
    ']': '[',
    '}': '{' 
  };

  for (const char of texto) {
    if (char === '"') {
      dentroDeQuota = !dentroDeQuota;
    } else if (!dentroDeQuota) {
      if (char === '(' || char === '[' || char === '{') {
        pilha.push(char);
      } else if (char === ')' || char === ']' || char === '}') {
        if (pilha.length === 0) {
          return false;
        }
        const aberto = pilha.pop()!;
        const esperado = pares[char];
        if(aberto !== esperado) {
          return false
        }
      }
    }
  }

  if(dentroDeQuota) {
    return false;
  }

  return pilha.length === 0;
}
