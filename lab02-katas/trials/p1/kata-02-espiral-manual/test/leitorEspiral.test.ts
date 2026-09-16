import { emEspiral } from "../src/leitorEspiral";

/** Suite de aceitacao da K2 - NAO EDITAR. */
describe("leitura em espiral anti-horaria", () => {
  it("matriz vazia produz array vazio", () => {
    expect(emEspiral([])).toEqual([]);
  });

  it("matriz 1x1 produz o unico elemento", () => {
    expect(emEspiral([[7]])).toEqual([7]);
  });

  it("matriz 2x2", () => {
    expect(emEspiral([[1, 2], [3, 4]])).toEqual([1, 3, 4, 2]);
  });

  it("matriz 3x3 termina no centro", () => {
    const m = [
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9],
    ];
    expect(emEspiral(m)).toEqual([1, 4, 7, 8, 9, 6, 3, 2, 5]);
  });

  it("matriz de uma linha vira varredura simples", () => {
    expect(emEspiral([[1, 2, 3, 4]])).toEqual([1, 2, 3, 4]);
  });

  it("matriz de uma coluna vira varredura simples", () => {
    expect(emEspiral([[1], [2], [3], [4]])).toEqual([1, 2, 3, 4]);
  });

  it("matriz retangular mais larga que alta (2x4)", () => {
    const m = [
      [1, 2, 3, 4],
      [5, 6, 7, 8],
    ];
    expect(emEspiral(m)).toEqual([1, 5, 6, 7, 8, 4, 3, 2]);
  });

  it("matriz retangular mais alta que larga (4x2)", () => {
    const m = [
      [1, 2],
      [3, 4],
      [5, 6],
      [7, 8],
    ];
    expect(emEspiral(m)).toEqual([1, 3, 5, 7, 8, 6, 4, 2]);
  });

  it("matriz 4x4 com anel interno completo", () => {
    const m = [
      [1, 2, 3, 4],
      [5, 6, 7, 8],
      [9, 10, 11, 12],
      [13, 14, 15, 16],
    ];
    expect(emEspiral(m)).toEqual([1, 5, 9, 13, 14, 15, 16, 12, 8, 4, 3, 2, 6, 10, 11, 7]);
  });

  it("matriz 3x4 com anel interno de uma linha", () => {
    const m = [
      [1, 2, 3, 4],
      [5, 6, 7, 8],
      [9, 10, 11, 12],
    ];
    expect(emEspiral(m)).toEqual([1, 5, 9, 10, 11, 12, 8, 4, 3, 2, 6, 7]);
  });

  it("matriz 5x3 com anel interno de uma coluna", () => {
    const m = [
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9],
      [10, 11, 12],
      [13, 14, 15],
    ];
    expect(emEspiral(m)).toEqual([1, 4, 7, 10, 13, 14, 15, 12, 9, 6, 3, 2, 5, 8, 11]);
  });

  it("valores repetidos e negativos nao alteram a ordem do percurso", () => {
    const m = [
      [-1, 0, -1],
      [5, -3, 5],
    ];
    expect(emEspiral(m)).toEqual([-1, 5, -3, 5, -1, 0]);
  });
});
