/**
 * Configuracao de MEDICAO, nao de estilo.
 *
 * A regra `complexity` do ESLint calcula complexidade ciclomatica de McCabe por
 * funcao. Com o limite em 0, toda funcao viola a regra e portanto aparece no
 * relatorio com o seu valor -- e assim que extraimos a metrica da RQ3.
 *
 * Uso (ver scripts/run_metrics.ps1, Issue S01-C):
 *   npx eslint --config eslint.complexity.config.mjs --no-config-lookup \
 *              --format json <arquivo.ts>
 *
 * Cada mensagem tem a forma:
 *   "Function 'minutosMonitorados' has a complexity of 5. Maximum allowed is 0."
 */
import tsParser from "@typescript-eslint/parser";

export default [
  {
    files: ["**/*.ts"],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: "module",
    },
    rules: {
      complexity: ["warn", 0],
    },
  },
];
