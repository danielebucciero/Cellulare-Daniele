// Test della logica pura (date e modello). Uso: npm test
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "src");
const files = ["js/constants.js", "js/util/dom.js", "js/util/date.js", "js/model.js"];
const code = files.map((f) => readFileSync(join(root, f), "utf8")).join("\n");
const exportsList = "({ giorniTra, inizioSettimana, aggiungiGiorni, distanzaRelativa, intervalloSettimana, isChiaveValida, validaImpegno, confrontaImpegni, raggruppaProssimi, normalizzaImpegno, corrispondeRicerca })";
const m = vm.runInNewContext(`${code}\n${exportsList}`, { Intl, crypto: globalThis.crypto });

const imp = (id, data, ora = "", extra = {}) => normalizza({ id, titolo: id, data, ora, ...extra });
const normalizza = (raw) => m.normalizzaImpegno(raw);

test("date: settimana da lunedì e differenze di giorni", () => {
  assert.equal(m.inizioSettimana("2026-10-29"), "2026-10-26"); // giovedì → lunedì
  assert.equal(m.inizioSettimana("2026-11-01"), "2026-10-26"); // domenica → lunedì precedente
  assert.equal(m.giorniTra("2026-10-24", "2026-10-26"), 2); // attraversa il cambio dell'ora legale
  assert.equal(m.aggiungiGiorni("2026-10-31", 1), "2026-11-01");
  assert.equal(m.intervalloSettimana("2026-10-26"), "26 ott – 1 nov 2026");
});

test("date: etichette relative", () => {
  assert.equal(m.distanzaRelativa("2026-10-29", "2026-10-29"), "Oggi");
  assert.equal(m.distanzaRelativa("2026-10-30", "2026-10-29"), "Domani");
  assert.equal(m.distanzaRelativa("2026-11-10", "2026-10-29"), "Tra 12 giorni");
  assert.equal(m.distanzaRelativa("2026-10-26", "2026-10-29"), "3 giorni fa");
});

test("validazione: titolo e data obbligatori", () => {
  const vuoto = m.validaImpegno({ titolo: "  ", data: "2026-02-30" });
  assert.equal(vuoto.valido, false);
  assert.ok(vuoto.errori.titolo && vuoto.errori.data);
  const ok = m.validaImpegno({ titolo: " Udienza ", data: "2026-11-03", categoria: "inventata" });
  assert.equal(ok.valido, true);
  assert.equal(ok.valori.titolo, "Udienza");
  assert.equal(ok.valori.categoria, "altro");
});

test("ordinamento: per giorno, poi senza ora, poi per ora", () => {
  const items = [imp("b", "2026-11-02", "11:00"), imp("c", "2026-11-02"), imp("a", "2026-10-30", "09:00")];
  assert.equal([...items].sort(m.confrontaImpegni).map((i) => i.id).join(), "a,c,b");
});

test("raggruppamento della vista Prossimi (oggi giovedì 29 ottobre)", () => {
  const items = [
    imp("ritardo", "2026-10-27"),
    imp("domani", "2026-10-30"),
    imp("domenica", "2026-11-01"),
    imp("lunedi", "2026-11-02", "11:00"),
    imp("dieci", "2026-11-10"),
  ];
  const gruppi = m.raggruppaProssimi(items, "2026-10-29");
  // JSON: gli array creati nel contesto vm hanno un prototipo diverso.
  assert.deepEqual(
    JSON.parse(JSON.stringify(gruppi.map((g) => [g.id, g.items.map((i) => i.id)]))),
    [
      ["ritardo", ["ritardo"]],
      ["domani", ["domani"]],
      ["settimana", ["domenica"]],
      ["prossima", ["lunedi"]],
      ["dopo", ["dieci"]],
    ],
  );
});

test("ricerca: tutte le parole, senza distinguere maiuscole", () => {
  const item = imp("x", "2026-11-10", "", { titolo: "Chiamare la dott.ssa Mulas", categoria: "legale" });
  assert.equal(m.corrispondeRicerca(item, "mulas"), true);
  assert.equal(m.corrispondeRicerca(item, "legale chiamare"), true);
  assert.equal(m.corrispondeRicerca(item, "revisione"), false);
});
