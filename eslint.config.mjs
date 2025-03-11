import globals from "globals";
import pluginVue from 'eslint-plugin-vue';
import pluginJs from "@eslint/js";
import typescriptEslint from 'typescript-eslint';


export default typescriptEslint.config(
  {ignores: ["./public/", "./rust/", "./node_modules/", '**/*.d.ts', './reports/', './lib/lines/', '**/*.js']},
  {
    extends: [
      pluginJs.configs.recommended,
      ...typescriptEslint.configs.recommended,
      ...pluginVue.configs['flat/recommended'],
    ],
    files: ["**/*.{ts,vue}"],
    languageOptions: {
      sourceType: 'module',
      globals: globals.browser,
      parserOptions: {
        parser: typescriptEslint.parser,
      },
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "vue/multi-word-component-names": "off",
    }
  },
);
