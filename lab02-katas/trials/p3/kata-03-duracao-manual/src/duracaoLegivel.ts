/**
 * K3 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */

interface Unidade {
  readonly segundos: number;
  readonly singular: string;
  readonly plural: string;
}

const UNIDADES: Unidade[] = [
  {segundos: 604800, singular: "semana", plural: "semanas"},
  {segundos: 86400, singular: "dia", plural: "dias"},
  {segundos: 3600, singular: "hora", plural: "horas"},
  {segundos: 60, singular: "minuto", plural: "minutos"},
  {segundos: 1, singular: "segundo", plural: "segundos"}
]

function decompor(total: number): string[]{
  let restante = total;
  const partes: string[] = [];

  for (const unidade of UNIDADES) {
    const quantidade = Math.floor(restante / unidade.segundos);
    restante -= quantidade * unidade.segundos;

    if (quantidade > 0) {
      const nome = quantidade === 1 ? unidade.singular : unidade.plural;
      partes.push(`${quantidade} ${nome}`);
    }
  }

  return partes;
}

function juntar(partes: string[]): string {
  if(partes.length === 1) {
    return partes[0];
  }
  const inicio = partes.slice(0, -1). join(", ");
  return `${inicio} e ${partes[partes.length - 1]}`;
}

export function formatar(segundos: number): string {
  if (!(segundos >= 0)) {
    throw new RangeError(`duração negativa: ${segundos}`);
  }
  if (segundos === 0) {
    return "agora";
  }
  return juntar(decompor(segundos));
}