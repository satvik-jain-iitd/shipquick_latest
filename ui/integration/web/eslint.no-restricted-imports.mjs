// Story #133 (ADR-012, rule 38): the web library is @astryxdesign/core, used directly at a pinned exact version.
// This ESLint flat-config fragment refuses another UI kit's import in app code, so every screen is built
// from the one library. Template only: copy it into the child's eslint.config.* (a protected path there,
// scripts/protected_paths.txt) and spread it into the project's own config array. ShipQuick CI does not run
// ESLint for a child; the child's own lint job does.
//
//   import { noOtherUiKits } from "./eslint.no-restricted-imports.mjs";
//   export default [...yourConfig, noOtherUiKits];
export const noOtherUiKits = {
  files: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
  rules: {
    "no-restricted-imports": [
      "error",
      {
        patterns: [
          {
            group: [
              "@mui/*",
              "@chakra-ui/*",
              "antd",
              "antd/*",
              "@ant-design/*",
              "@mantine/*",
              "@radix-ui/*",
              "@headlessui/*",
              "react-bootstrap",
              "react-bootstrap/*",
              "@material/*",
              "@shoelace-style/*",
              "primereact",
              "primereact/*",
            ],
            message:
              "Library first (rule 38): build the screen from @astryxdesign/core. Nothing fits? File a component-request and stop; no stand-in.",
          },
        ],
      },
    ],
  },
};
