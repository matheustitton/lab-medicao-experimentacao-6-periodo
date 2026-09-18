import { casasAlcancaveis } from "../src/alcanceDaRainha";

/** Suite de aceitacao da K5 - NAO EDITAR. */
describe("alcance da rainha com obstaculos", () => {
  it("tabuleiro 1x1 nao tem para onde mover", () => {
    expect(casasAlcancaveis(1, 1, [0, 0], [])).toBe(0);
  });

  it("centro de um 3x3 livre alcanca todas as outras casas", () => {
    expect(casasAlcancaveis(3, 3, [1, 1], [])).toBe(8);
  });

  it("canto de um 3x3 livre", () => {
    expect(casasAlcancaveis(3, 3, [0, 0], [])).toBe(6);
  });

  it("tabuleiro de uma linha vira movimento so na horizontal", () => {
    expect(casasAlcancaveis(1, 5, [0, 0], [])).toBe(4);
  });

  it("tabuleiro de uma coluna vira movimento so na vertical", () => {
    expect(casasAlcancaveis(5, 1, [2, 0], [])).toBe(4);
  });

  it("uma pedra remove a casa dela do alcance", () => {
    expect(casasAlcancaveis(3, 3, [1, 1], [[0, 0]])).toBe(7);
  });

  it("a pedra bloqueia tambem tudo o que esta atras dela", () => {
    // 5x5, rainha em [2,2]: sem pedras alcanca 16 casas.
    // A pedra em [2,3] corta [2,3] e [2,4]: sobram 14.
    expect(casasAlcancaveis(5, 5, [2, 2], [[2, 3]])).toBe(14);
  });

  it("pedra distante corta so o que vem depois dela", () => {
    // 5x5, rainha em [2,0]: pedra em [2,3] corta [2,3] e [2,4].
    expect(casasAlcancaveis(5, 5, [2, 0], [[2, 3]])).toBe(
      casasAlcancaveis(5, 5, [2, 0], []) - 2,
    );
  });

  it("pedras repetidas na lista nao mudam o resultado", () => {
    expect(casasAlcancaveis(3, 3, [1, 1], [[0, 0], [0, 0], [0, 0]])).toBe(7);
  });

  it("pedra na casa da propria rainha e ignorada", () => {
    expect(casasAlcancaveis(3, 3, [1, 1], [[1, 1]])).toBe(8);
  });

  it("pedra fora do tabuleiro e ignorada", () => {
    expect(casasAlcancaveis(3, 3, [1, 1], [[9, 9], [-1, 0]])).toBe(8);
  });

  it("rainha cercada por pedras nao alcanca nada", () => {
    const cerco: [number, number][] = [
      [0, 0], [0, 1], [0, 2],
      [1, 0], [1, 2],
      [2, 0], [2, 1], [2, 2],
    ];
    expect(casasAlcancaveis(3, 3, [1, 1], cerco)).toBe(0);
  });
});
