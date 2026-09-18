/**
 * K1 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Não altere a assinatura exportada: a suite de aceitação depende dela.
 */
export function comprimir(valores: number[]): string {
  if (valores.length === 0) return "";

  // Remove duplicatas preservando ordem
  const unicos = [...new Set(valores)];

  // Agrupa em sequências consecutivas
  const grupos: number[][] = [];
  let grupoAtual: number[] = [unicos[0]];

  for (let i = 1; i < unicos.length; i++) {
    const atual = unicos[i];
    const anterior = unicos[i - 1];

    if (atual === anterior + 1) {
      // Continua a sequência
      grupoAtual.push(atual);
    } else {
      // Inicia novo grupo
      grupos.push(grupoAtual);
      grupoAtual = [atual];
    }
  }
  grupos.push(grupoAtual);

  // Formata cada grupo
  const partes = grupos.map((grupo) => {
    if (grupo.length >= 3) {
      return `${grupo[0]}..${grupo[grupo.length - 1]}`;
    } else {
      return grupo.join(",");
    }
  });

  return partes.join(",");
}
