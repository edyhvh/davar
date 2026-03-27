import { defineConfig } from "eslint/config";
import expoConfig from "eslint-config-expo/flat.js";
// https://docs.expo.dev/guides/using-eslint/

export default defineConfig([
  expoConfig,
  {
    settings: {
      "import/resolver": {
        node: {
          extensions: [".js", ".jsx", ".ts", ".tsx"],
        },
        typescript: {
          alwaysTryTypes: true,
          project: "./tsconfig.json",
        },
      },
    },
  },
  {
    ignores: ["dist/*"],
  },
]);
