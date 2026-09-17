import { formatar } from "../src/duracaoLegivel";

/** Suite de aceitacao da K3 - NAO EDITAR. */
describe("duracao legivel", () => {
  it("zero segundos e o instante atual", () => {
    expect(formatar(0)).toBe("agora");
  });

  it("um segundo no singular", () => {
    expect(formatar(1)).toBe("1 segundo");
  });

  it("segundos no plural", () => {
    expect(formatar(45)).toBe("45 segundos");
  });

  it("um minuto exato nao mostra segundos", () => {
    expect(formatar(60)).toBe("1 minuto");
  });

  it("dois itens sao unidos por ' e '", () => {
    expect(formatar(62)).toBe("1 minuto e 2 segundos");
  });

  it("uma hora exata", () => {
    expect(formatar(3600)).toBe("1 hora");
  });

  it("tres itens usam virgula e depois ' e '", () => {
    expect(formatar(3662)).toBe("1 hora, 1 minuto e 2 segundos");
  });

  it("um dia exato", () => {
    expect(formatar(86400)).toBe("1 dia");
  });

  it("uma semana exata", () => {
    expect(formatar(604800)).toBe("1 semana");
  });

  it("as cinco unidades juntas", () => {
    expect(formatar(694861)).toBe("1 semana, 1 dia, 1 hora, 1 minuto e 1 segundo");
  });

  it("unidades intermediarias zeradas sao omitidas", () => {
    expect(formatar(604801)).toBe("1 semana e 1 segundo");
  });

  it("duracao negativa e rejeitada", () => {
    expect(() => formatar(-1)).toThrow(RangeError);
  });
});
