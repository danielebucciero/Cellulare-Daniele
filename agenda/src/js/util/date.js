// Date come chiavi "AAAA-MM-GG" nel fuso orario locale: niente sorprese con l'ora legale.

const pad2 = (n) => String(n).padStart(2, "0");

function chiaveData(date) {
  return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

function daChiave(chiave) {
  const [y, m, d] = chiave.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function isChiaveValida(chiave) {
  if (typeof chiave !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(chiave)) return false;
  return chiaveData(daChiave(chiave)) === chiave;
}

const oggi = () => chiaveData(new Date());

function aggiungiGiorni(chiave, giorni) {
  const d = daChiave(chiave);
  d.setDate(d.getDate() + giorni);
  return chiaveData(d);
}

/** Giorni da `a` a `b` (positivo se `b` è dopo). */
function giorniTra(a, b) {
  return Math.round((daChiave(b) - daChiave(a)) / 86400000);
}

/** Lunedì della settimana che contiene `chiave`. */
function inizioSettimana(chiave) {
  const d = daChiave(chiave);
  const giornoIso = (d.getDay() + 6) % 7; // lunedì = 0
  d.setDate(d.getDate() - giornoIso);
  return chiaveData(d);
}

function formatta(chiave, opzioni) {
  return new Intl.DateTimeFormat("it-IT", opzioni).format(daChiave(chiave));
}

const giornoBreve = (k) => formatta(k, { weekday: "short" }).replace(".", "").toUpperCase();
const meseBreve = (k) => formatta(k, { month: "short" }).replace(".", "");
const numeroGiorno = (k) => daChiave(k).getDate();
const dataLunga = (k) => formatta(k, { weekday: "long", day: "numeric", month: "long" });
const dataMedia = (k) => formatta(k, { weekday: "short", day: "numeric", month: "short" });

/** "Oggi", "Domani", "Tra 5 giorni", "3 giorni fa"… */
function distanzaRelativa(chiave, riferimento = oggi()) {
  const diff = giorniTra(riferimento, chiave);
  if (diff === 0) return "Oggi";
  if (diff === 1) return "Domani";
  if (diff === -1) return "Ieri";
  if (diff > 1) return `Tra ${diff} giorni`;
  return `${-diff} giorni fa`;
}

/** "26 ott – 1 nov 2026" */
function intervalloSettimana(lunedi) {
  const domenica = aggiungiGiorni(lunedi, 6);
  const stessoMese = daChiave(lunedi).getMonth() === daChiave(domenica).getMonth();
  const inizio = stessoMese ? String(numeroGiorno(lunedi)) : `${numeroGiorno(lunedi)} ${meseBreve(lunedi)}`;
  const fine = formatta(domenica, { day: "numeric", month: "short", year: "numeric" }).replace(".", "");
  return `${inizio} – ${fine}`;
}

function formattaIstante(ms) {
  return new Intl.DateTimeFormat("it-IT", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(ms));
}
