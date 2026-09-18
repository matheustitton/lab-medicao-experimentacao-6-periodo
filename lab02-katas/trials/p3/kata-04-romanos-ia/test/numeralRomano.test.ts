import { paraDecimal } from "../src/numeralRomano";

/** Suite de aceitacao da K4 - NAO EDITAR. */
describe("numeral romano com validacao", () => {
  it("simbolo unico", () => {
    expect(paraDecimal("I")).toBe(1);
  });

  it("repeticao aditiva ate tres vezes", () => {
    expect(paraDecimal("III")).toBe(3);
  });

  it("par subtrativo simples", () => {
    expect(paraDecimal("IV")).toBe(4);
  });

  it("aditivo depois de simbolo maior", () => {
    expect(paraDecimal("XIV")).toBe(14);
  });

  it("numeral longo com dois pares subtrativos", () => {
    expect(paraDecimal("MCMXCIV")).toBe(1994);
  });

  it("maior numeral representavel", () => {
    expect(paraDecimal("MMMCMXCIX")).toBe(3999);
  });

  it("quatro repeticoes seguidas sao invalidas", () => {
    expect(() => paraDecimal("IIII")).toThrow(RangeError);
  });

  it("V, L e D nunca se repetem, mesmo separados", () => {
    expect(() => paraDecimal("VIV")).toThrow(RangeError);
  });

  it("subtracao fora da lista permitida e invalida", () => {
    expect(() => paraDecimal("IL")).toThrow(RangeError);
  });

  it("simbolo fora do alfabeto romano e invalido", () => {
    expect(() => paraDecimal("abc")).toThrow(RangeError);
  });

  it("string vazia e invalida", () => {
    expect(() => paraDecimal("")).toThrow(RangeError);
  });

  it("depois de par subtrativo so pode vir simbolo menor", () => {
    expect(() => paraDecimal("IXI")).toThrow(RangeError);
  });
});
