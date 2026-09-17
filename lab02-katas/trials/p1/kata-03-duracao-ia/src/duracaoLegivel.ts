/**
 * K3 do Lab02. Implementação conforme o ENUNCIADO.md.
 * Não altera a assinatura exportada: a suite de aceitação depende dela.
 */
export function formatar(segundos: number): string {
  if (segundos < 0) {
    throw new RangeError("segundos não pode ser negativo");
  }

  if (segundos === 0) {
    return "agora";
  }

  const unidades: [string, string, number][] = [
    ["semana", "semanas", 604800],
    ["dia", "dias", 86400],
    ["hora", "horas", 3600],
    ["minuto", "minutos", 60],
    ["segundo", "segundos", 1],
  ];

  const partes: string[] = [];
  let resto = segundos;

  for (const [singular, plural, valorUnidade] of unidades) {
    const quantidade = Math.floor(resto / valorUnidade);
    resto %= valorUnidade;

    if (quantidade > 0) {
      const nome = quantidade === 1 ? singular : plural;
      partes.push(`${quantidade} ${nome}`);
    }
  }

  if (partes.length === 1) {
    return partes[0];
  }

  const ultima = partes[partes.length - 1];
  const anteriores = partes.slice(0, -1);

  return `${anteriores.join(", ")} e ${ultima}`;
}