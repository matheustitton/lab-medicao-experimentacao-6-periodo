import { estaBalanceado } from "../src/validadorDelimitadores";

/** Suite de aceitacao da K6 - NAO EDITAR. */
describe("delimitadores balanceados com literais", () => {
  it("texto vazio e valido", () => {
    expect(estaBalanceado("")).toBe(true);
  });

  it("par simples", () => {
    expect(estaBalanceado("()")).toBe(true);
  });

  it("os tres tipos aninhados", () => {
    expect(estaBalanceado("([{}])")).toBe(true);
  });

  it("delimitadores em sequencia, sem aninhamento", () => {
    expect(estaBalanceado("()[]{}")).toBe(true);
  });

  it("ordem de fechamento errada e invalida", () => {
    expect(estaBalanceado("([)]")).toBe(false);
  });

  it("abre e nao fecha e invalido", () => {
    expect(estaBalanceado("(")).toBe(false);
  });

  it("fecha antes de abrir e invalido", () => {
    expect(estaBalanceado(")(")).toBe(false);
  });

  it("caracteres fora do alfabeto de delimitadores sao ignorados", () => {
    expect(estaBalanceado("se (a > b) { troca(a, b); }")).toBe(true);
  });

  it("delimitador dentro de literal nao conta", () => {
    expect(estaBalanceado('("[")')).toBe(true);
  });

  it("literal pode conter um desbalanceamento inteiro", () => {
    expect(estaBalanceado('x = "([{" ;')).toBe(true);
  });

  it("aspa aberta e nunca fechada invalida o texto", () => {
    expect(estaBalanceado('(")')).toBe(false);
  });

  it("literais consecutivos alternam entrada e saida", () => {
    // O primeiro par de aspas esconde o "(", o segundo esconde o ")".
    // Fora dos literais sobra apenas o par [] , que esta balanceado.
    expect(estaBalanceado('["(" a ")"]')).toBe(true);
  });
});
