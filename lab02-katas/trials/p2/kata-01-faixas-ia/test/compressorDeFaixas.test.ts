import { comprimir } from "../src/compressorDeFaixas";

/** Suite de aceitacao da K1 - NAO EDITAR. */
describe("compressor de faixas", () => {
  it("entrada vazia produz string vazia", () => {
    expect(comprimir([])).toBe("");
  });

  it("um unico valor e escrito sozinho", () => {
    expect(comprimir([7])).toBe("7");
  });

  it("valores isolados sao separados por virgula", () => {
    expect(comprimir([1, 4, 9])).toBe("1,4,9");
  });

  it("tres consecutivos viram faixa", () => {
    expect(comprimir([1, 2, 3])).toBe("1..3");
  });

  it("dois consecutivos nao viram faixa", () => {
    expect(comprimir([5, 6])).toBe("5,6");
  });

  it("faixas e valores isolados se misturam na mesma saida", () => {
    expect(comprimir([1, 2, 3, 4, 7, 9, 10, 11])).toBe("1..4,7,9..11");
  });

  it("valores repetidos sao colapsados em um so", () => {
    expect(comprimir([3, 3, 3])).toBe("3");
  });

  it("repeticao no meio de uma sequencia nao quebra a faixa", () => {
    expect(comprimir([1, 2, 2, 3, 4])).toBe("1..4");
  });

  it("faixa inteiramente negativa", () => {
    expect(comprimir([-9, -8, -7])).toBe("-9..-7");
  });

  it("faixa que atravessa o zero", () => {
    expect(comprimir([-2, -1, 0, 1, 2])).toBe("-2..2");
  });

  it("entrada inteira e uma unica faixa", () => {
    expect(comprimir([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])).toBe("10..20");
  });

  it("duas faixas separadas por um buraco de um valor", () => {
    expect(comprimir([1, 2, 3, 5, 6, 7])).toBe("1..3,5..7");
  });
});
