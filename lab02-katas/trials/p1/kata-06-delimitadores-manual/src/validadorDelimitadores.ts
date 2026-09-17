/**
 * K6 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function estaBalanceado(texto: string): boolean {
  const CLOSING_FOR: Record<string, string> = {
    "(": ")",
    "[": "]",
    "{": "}"
  }

  const OPENERS = new Set(["(", "[", "{"])
  const CLOSERS = new Set([")", "]", "}"])

  const stack = []
  let insideLiteral = false;

  for(const char of texto){
    if (char === '"'){
      insideLiteral = !insideLiteral;
      continue
    }

    if (insideLiteral)
      continue;

    if (OPENERS.has(char)){
      stack.push(char)
      continue;
    }

    if(CLOSERS.has(char)){
      const lastOpener =stack.pop()
      if(!lastOpener || CLOSING_FOR[lastOpener] !== char)
        return false;
    }
  }

  return stack.length === 0 && !insideLiteral
}
