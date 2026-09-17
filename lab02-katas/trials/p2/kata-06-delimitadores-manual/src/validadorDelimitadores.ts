/**
 * K6 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function estaBalanceado(texto: string): boolean {
  const pilha: string[] = [];
  let dentroDeLiteral = false;

  const aberturas = new Set(["(", "[", "{"]);

  const correspondentes: Record<string, string> = {
    ")": "(",
    "]": "[",
    "}": "{",
  };

  for (const caractere of texto) {
    // Aspas alternam entre entrar e sair de um literal
    if (caractere === '"') {
      dentroDeLiteral = !dentroDeLiteral;
      continue;
    }

    // Tudo dentro de uma string é ignorado
    if (dentroDeLiteral) {
      continue;
    }

    // Abertura de delimitador
    if (aberturas.has(caractere)) {
      pilha.push(caractere);
      continue;
    }

    // Fechamento de delimitador
    if (caractere in correspondentes) {
      if (pilha.length === 0) {
        return false;
      }

      const ultimo = pilha.pop();

      if (ultimo !== correspondentes[caractere]) {
        return false;
      }
    }
  }

  // Literal aberto ou delimitador sem fechamento
  if (dentroDeLiteral) {
    return false;
  }

  return pilha.length === 0;
}
