/**
 * Configuracao do Jest para os trials do Lab02.
 *
 * O participante roda a suite dezenas de vezes dentro dos 35 minutos, e esse
 * tempo entra direto na variavel dependente principal (RQ1). Por isso:
 *   - `isolatedModules`: o ts-jest so transpila, sem checagem de tipo, e o ciclo
 *     salvar-testar fica curto. A checagem existe a parte, em `npm run typecheck`.
 *   - sem cobertura, sem watch.
 */
/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: "node",
  // `solucoes-referencia` fica fora daqui de proposito: e um diretorio ignorado
  // pelo git, que nao existe na maquina dos outros integrantes, e o Jest aborta
  // se um root listado nao existir. O run_tests.ps1 sobrescreve `roots` com a
  // pasta alvo a cada execucao, entao a validacao das suites contra as solucoes
  // de referencia continua funcionando.
  roots: ["<rootDir>/katas", "<rootDir>/trials"],
  testMatch: ["**/test/**/*.test.ts"],
  transform: {
    "^.+\\.ts$": ["ts-jest", {}],
  },
  // Um kata travado nao pode segurar o cronometro do trial.
  testTimeout: 5000,
  // O relatorio XML e o contrato com o cronometro (Issue S01-B). O diretorio e o
  // nome do arquivo sao sobrescritos por JEST_JUNIT_OUTPUT_DIR / _OUTPUT_NAME em
  // scripts/run_tests.ps1.
  reporters: [
    "default",
    ["jest-junit", { outputDirectory: "reports", outputName: "junit.xml" }],
  ],
};
