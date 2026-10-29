// Pezzi di HTML riutilizzati dalle viste.

/** `segnaRitardo`: i giorni passati in rosso (per gli impegni non fatti), altrimenti attenuati. */
function piastrellaGiorno(chiave, riferimento, { segnaRitardo = true } = {}) {
  const classi = ["tile"];
  if (chiave === riferimento) classi.push("tile--today");
  else if (chiave < riferimento) classi.push(segnaRitardo ? "tile--late" : "tile--past");
  return `
    <span class="${classi.join(" ")}" aria-hidden="true">
      <span class="tile__wd">${esc(giornoBreve(chiave))}</span>
      <span class="tile__num">${numeroGiorno(chiave)}</span>
      <span class="tile__mon">${esc(meseBreve(chiave))}</span>
    </span>`;
}

function chipCategoria(id) {
  return `<span class="chip cat-${esc(id)}">${esc(CATEGORIA_PER_ID[id].label)}</span>`;
}

function pulsanteSpunta(item) {
  const azione = item.fatto ? "Segna come da fare" : "Segna come fatto";
  return `
    <button class="check" type="button" data-action="toggle" aria-pressed="${item.fatto}"
      aria-label="${azione}: ${esc(item.titolo)}" ${state.solaLettura ? "disabled" : ""}>${ICONA_SPUNTA}</button>`;
}

/**
 * Una riga d'impegno.
 * `conGiorno` mostra la piastrella con la data; `meta` sostituisce la riga informativa.
 */
function rigaImpegno(item, { conGiorno = true, riferimento = oggi(), meta } = {}) {
  const info =
    meta ??
    [
      chipCategoria(item.categoria),
      item.ora ? `<span class="item__time">${esc(item.ora)}</span>` : "",
      conGiorno ? `<span>${esc(distanzaRelativa(item.data, riferimento))}</span>` : "",
    ].join("");

  return `
    <li class="item cat-${esc(item.categoria)}${item.fatto ? " is-done" : ""}" data-id="${esc(item.id)}">
      ${conGiorno ? piastrellaGiorno(item.data, riferimento) : ""}
      <button class="item__body" type="button" data-action="edit">
        <span class="item__title">${esc(item.titolo)}</span>
        <span class="item__meta">${info}</span>
        ${item.note ? `<span class="item__note">${esc(item.note)}</span>` : ""}
      </button>
      ${pulsanteSpunta(item)}
    </li>`;
}

function statoVuoto(titolo, testo) {
  return `<div class="empty"><strong>${esc(titolo)}</strong><span>${esc(testo)}</span></div>`;
}

function statoCaricamento() {
  return statoVuoto("Carico l'agenda…", "Un attimo, sto leggendo i tuoi impegni.");
}

function nessunRisultato() {
  return statoVuoto("Nessun risultato", `Nessun impegno contiene «${state.ricerca}».`);
}
