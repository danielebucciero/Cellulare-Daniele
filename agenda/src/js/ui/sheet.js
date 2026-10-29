// Scheda per creare o modificare un impegno.

let idInModifica = null;
let focusPrecedente = null;

function preparaCategorie() {
  $("#f-categorie").innerHTML = CATEGORIE.map(
    (c) => `
    <label class="cat-${c.id}">
      <input type="radio" name="categoria" id="f-cat-${c.id}" value="${c.id}">
      <span>${esc(c.label)}</span>
    </label>`,
  ).join("");
}

function scorciatoieData() {
  const riferimento = oggi();
  const lunediProssimo = aggiungiGiorni(inizioSettimana(riferimento), 7);
  return [
    { label: "Oggi", data: riferimento },
    { label: "Domani", data: aggiungiGiorni(riferimento, 1) },
    { label: "Lunedì prossimo", data: lunediProssimo },
    { label: "Tra una settimana", data: aggiungiGiorni(riferimento, 7) },
  ];
}

function aggiornaScorciatoie() {
  const scelta = $("#f-data").value;
  $("#quick-dates").innerHTML = scorciatoieData()
    .map(
      (s) =>
        `<button type="button" data-action="quick-date" data-date="${s.data}" aria-pressed="${s.data === scelta}">${esc(s.label)}</button>`,
    )
    .join("");
}

function mostraErrori(errori) {
  for (const campo of ["titolo", "data"]) {
    const el = $(`#err-${campo}`);
    el.textContent = errori[campo] ?? "";
    el.hidden = !errori[campo];
    $(`#f-${campo}`).setAttribute("aria-invalid", errori[campo] ? "true" : "false");
  }
}

function apriScheda({ item = null, data = null } = {}) {
  if (state.solaLettura) return;
  idInModifica = item?.id ?? null;
  focusPrecedente = document.activeElement;

  $("#sheet-title").textContent = item ? "Modifica impegno" : "Nuovo impegno";
  $("#f-titolo").value = item?.titolo ?? "";
  $("#f-data").value = item?.data ?? data ?? oggi();
  $("#f-ora").value = item?.ora ?? "";
  $("#f-note").value = item?.note ?? "";
  $(`#f-cat-${item?.categoria ?? CATEGORIA_PREDEFINITA}`).checked = true;

  const elimina = $("#btn-elimina");
  elimina.hidden = !item;
  disarmaElimina();

  mostraErrori({});
  aggiornaScorciatoie();
  $("#sheet").hidden = false;
  $("#f-titolo").focus();
}

function chiudiScheda() {
  $("#sheet").hidden = true;
  idInModifica = null;
  focusPrecedente?.focus?.();
}

function disarmaElimina() {
  const elimina = $("#btn-elimina");
  elimina.dataset.armed = "false";
  elimina.textContent = "Elimina";
}

function leggiModulo() {
  const form = $("#form-impegno");
  return {
    titolo: form.titolo.value,
    data: form.data.value,
    ora: form.ora.value,
    categoria: form.categoria.value,
    note: form.note.value,
  };
}

async function salvaScheda(event) {
  event.preventDefault();
  const { valori, errori, valido } = validaImpegno(leggiModulo());
  mostraErrori(errori);
  if (!valido) {
    $(errori.titolo ? "#f-titolo" : "#f-data").focus();
    return;
  }

  const id = idInModifica;
  chiudiScheda();
  if (id) {
    await esegui(() => state.archivio.modifica(id, valori), "Modifiche salvate");
  } else {
    await esegui(
      () => state.archivio.aggiungi({ ...valori, fatto: false, creatoIl: Date.now(), completatoIl: null }),
      `Aggiunto per ${distanzaRelativa(valori.data).toLowerCase()}`,
    );
  }
}

async function eliminaDaScheda() {
  const bottone = $("#btn-elimina");
  if (bottone.dataset.armed !== "true") {
    bottone.dataset.armed = "true";
    bottone.textContent = "Conferma eliminazione";
    return;
  }
  const item = trovaImpegno(idInModifica);
  chiudiScheda();
  if (item) await eliminaImpegno(item);
}

function collegaScheda() {
  preparaCategorie();
  $("#form-impegno").addEventListener("submit", salvaScheda);
  $("#f-data").addEventListener("input", aggiornaScorciatoie);
  $("#sheet").addEventListener("click", (e) => {
    if (e.target.id === "sheet") chiudiScheda();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !$("#sheet").hidden) chiudiScheda();
  });
}
