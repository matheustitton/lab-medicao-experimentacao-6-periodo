/**
 * K3 do Lab02. Implemente conforme o ENUNCIADO.md.
 * Nao altere a assinatura exportada: a suite de aceitacao depende dela.
 */
export function formatar(segundos: number): string {
  if (segundos < 0) {
    throw new RangeError("A duração não pode ser negativa.");
  }

  if (segundos === 0) {
    return "agora";
  }

  const unidades = [
    { nome: "semana", valor: 604800 },
    { nome: "dia", valor: 86400 },
    { nome: "hora", valor: 3600 },
    { nome: "minuto", valor: 60 },
    { nome: "segundo", valor: 1 },
  ];

  const partes: string[] = [];
  let restante = segundos;

  for (const unidade of unidades) {
    const quantidade = Math.floor(restante / unidade.valor);

    if (quantidade > 0) {
      const nome =
        quantidade === 1
          ? unidade.nome
          : `${unidade.nome}s`;

      partes.push(`${quantidade} ${nome}`);

      restante %= unidade.valor;
    }
  }

  if (partes.length === 1) {
    return partes[0];
  }

  if (partes.length === 2) {
    return `${partes[0]} e ${partes[1]}`;
  }

  return `${partes.slice(0, -1).join(", ")} e ${partes[partes.length - 1]}`;

}
