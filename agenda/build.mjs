// Unisce CSS e JS di src/ in due file pronti all'uso:
//   dist/agenda.html  frammento da pubblicare come artifact su claude.ai
//   dist/index.html   documento completo da aprire nel browser
// Uso: node build.mjs

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const src = (p) => join(root, "src", p);
const read = (p) => readFileSync(src(p), "utf8");

// L'ordine conta: ogni file usa solo ciò che è definito nei precedenti.
export const STYLES = ["css/tokens.css", "css/base.css", "css/layout.css", "css/components.css"];
export const SCRIPTS = [
  "js/constants.js",
  "js/seed.js",
  "js/util/dom.js",
  "js/util/date.js",
  "js/model.js",
  "js/store/local-store.js",
  "js/store/db-store.js",
  "js/store/index.js",
  "js/state.js",
  "js/ui/components.js",
  "js/ui/views.js",
  "js/ui/render.js",
  "js/ui/toast.js",
  "js/ui/sheet.js",
  "js/actions.js",
  "js/main.js",
];

const banner = (file) => `/* ---- ${file} ---- */`;
const styles = STYLES.map((f) => `${banner(f)}\n${read(f)}`).join("\n");
// Un solo scope privato: i moduli condividono le dichiarazioni senza toccare window.
const scripts = `(() => {\n"use strict";\n${SCRIPTS.map((f) => `${banner(f)}\n${read(f)}`).join("\n")}\n})();`;

const fragment = read("index.html")
  .replace("/*@STYLES*/", () => styles)
  .replace("/*@SCRIPTS*/", () => scripts);

const document = `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
</head>
<body>
${fragment}
</body>
</html>
`;

mkdirSync(join(root, "dist"), { recursive: true });
writeFileSync(join(root, "dist", "agenda.html"), fragment);
writeFileSync(join(root, "dist", "index.html"), document);
console.log(`Creati dist/agenda.html e dist/index.html (${Math.round(fragment.length / 1024)} KB)`);
