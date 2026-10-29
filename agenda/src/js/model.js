// Modello di un impegno: normalizzazione, validazione, ordinamento e raggruppamento.

/** Porta un documento qualsiasi (anche scritto a mano) nella forma attesa. */
function normalizzaImpegno(raw) {
  const categoria = CATEGORIA_PER_ID[raw.categoria] ? raw.categoria : CATEGORIA_PREDEFINITA;
  return {
    id: String(raw.id),
    titolo: String(raw.titolo ?? "").trim() || "Senza titolo",
    data: isChiaveValida(raw.data) ? raw.data : oggi(),
    ora: /^\d{2}:\d{2}$/.test(raw.ora ?? "") ? raw.ora : "",
    categoria,
    note: String(raw.note ?? ""),
    fatto: Boolean(raw.fatto),
    creatoIl: Number(raw.creatoIl) || 0,
    completatoIl: Number(raw.completatoIl) || null,
  };
}

/** Controlla i campi del modulo. Restituisce i valori puliti e gli errori per campo. */
function validaImpegno(input) {
  const valori = {
    titolo: String(input.titolo ?? "").trim(),
    data: String(input.data ?? ""),
    ora: String(input.ora ?? ""),
    categoria: CATEGORIA_PER_ID[input.categoria] ? input.categoria : CATEGORIA_PREDEFINITA,
    note: String(input.note ?? "").trim(),
  };
  const errori = {};
  if (!valori.titolo) errori.titolo = "Scrivi cosa devi fare.";
  if (!isChiaveValida(valori.data)) errori.data = "Scegli il giorno dell'impegno.";
  if (valori.ora && !/^\d{2}:\d{2}$/.test(valori.ora)) valori.ora = "";
  return { valori, errori, valido: Object.keys(errori).length === 0 };
}

/** Per giorno, poi gli impegni senza ora prima di quelli con l'ora, poi per titolo. */
function confrontaImpegni(a, b) {
  if (a.data !== b.data) return a.data < b.data ? -1 : 1;
  if (a.ora !== b.ora) {
    if (!a.ora) return -1;
    if (!b.ora) return 1;
    return a.ora < b.ora ? -1 : 1;
  }
  return a.titolo.localeCompare(b.titolo, "it");
}

function corrispondeRicerca(item, query) {
  if (!query) return true;
  const testo = `${item.titolo} ${item.note} ${CATEGORIA_PER_ID[item.categoria].label}`.toLowerCase();
  return query
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((parola) => testo.includes(parola));
}

/** Divide gli impegni da fare in fasce temporali, nell'ordine in cui si leggono. */
function raggruppaProssimi(items, riferimento = oggi()) {
  const domani = aggiungiGiorni(riferimento, 1);
  const fineSettimana = aggiungiGiorni(inizioSettimana(riferimento), 6);
  const fineProssima = aggiungiGiorni(fineSettimana, 7);

  const gruppi = [
    { id: "ritardo", titolo: "In ritardo", items: [] },
    { id: "oggi", titolo: "Oggi", sottotitolo: dataLunga(riferimento), items: [] },
    { id: "domani", titolo: "Domani", sottotitolo: dataLunga(domani), items: [] },
    { id: "settimana", titolo: "Questa settimana", items: [] },
    { id: "prossima", titolo: "Settimana prossima", items: [] },
    { id: "dopo", titolo: "Più avanti", items: [] },
  ];
  const perId = Object.fromEntries(gruppi.map((g) => [g.id, g]));

  for (const item of [...items].sort(confrontaImpegni)) {
    let gruppo;
    if (item.data < riferimento) gruppo = "ritardo";
    else if (item.data === riferimento) gruppo = "oggi";
    else if (item.data === domani) gruppo = "domani";
    else if (item.data <= fineSettimana) gruppo = "settimana";
    else if (item.data <= fineProssima) gruppo = "prossima";
    else gruppo = "dopo";
    perId[gruppo].items.push(item);
  }
  return gruppi.filter((g) => g.items.length > 0);
}
