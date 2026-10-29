// Le tre viste: Prossimi, Settimana, Completati. Ognuna restituisce l'HTML del <main>.

function vistaProssimi() {
  const riferimento = oggi();
  const tutti = daFare();
  if (tutti.length === 0) {
    return statoVuoto("Nessun impegno in programma", "Tocca «Nuovo» per aggiungere il primo.");
  }

  const items = visibili(tutti);
  const gruppi = raggruppaProssimi(items, riferimento);
  const inRitardo = tutti.filter((i) => i.data < riferimento).length;
  const perOggi = tutti.filter((i) => i.data === riferimento).length;
  const finoADomenica = aggiungiGiorni(inizioSettimana(riferimento), 6);
  const settimana = tutti.filter((i) => i.data >= riferimento && i.data <= finoADomenica).length;
  const prossimo = [...tutti].filter((i) => i.data >= riferimento).sort(confrontaImpegni)[0];

  const riepilogo = state.ricerca
    ? ""
    : `
    <section class="summary" aria-label="Riepilogo">
      ${
        prossimo
          ? `<button class="summary__next" type="button" data-action="edit" data-id="${esc(prossimo.id)}">
              <span class="summary__eyebrow">Prossimo impegno</span>
              <span class="summary__title">${esc(prossimo.titolo)}</span>
              <span class="summary__when"><strong>${esc(distanzaRelativa(prossimo.data, riferimento))}</strong>
                · ${esc(dataLunga(prossimo.data))}${prossimo.ora ? ` · ore ${esc(prossimo.ora)}` : ""}</span>
            </button>`
          : `<p class="summary__title">Nessun impegno nei prossimi giorni</p>`
      }
      <div class="stats">
        <span class="stat"><b>${tutti.length}</b> da fare</span>
        <span class="stat"><b>${perOggi}</b> oggi</span>
        <span class="stat"><b>${settimana}</b> entro domenica</span>
        ${inRitardo ? `<span class="stat stat--danger"><b>${inRitardo}</b> in ritardo</span>` : ""}
      </div>
    </section>`;

  if (gruppi.length === 0) return riepilogo + nessunRisultato();

  const sezioni = gruppi
    .map(
      (g) => `
      <section class="group group--${g.id}" aria-labelledby="g-${g.id}">
        <div class="group__head">
          <h2 class="group__title" id="g-${g.id}">${esc(g.titolo)}${g.sottotitolo ? ` <small>${esc(g.sottotitolo)}</small>` : ""}</h2>
          <span class="group__count">${g.items.length}</span>
        </div>
        <ul class="list">${g.items.map((i) => rigaImpegno(i, { riferimento })).join("")}</ul>
      </section>`,
    )
    .join("");

  return riepilogo + sezioni;
}

function vistaSettimana() {
  const riferimento = oggi();
  const giorni = Array.from({ length: 7 }, (_, n) => aggiungiGiorni(state.lunedi, n));
  const items = visibili(state.items);
  const settimanaCorrente = state.lunedi === inizioSettimana(riferimento);

  const righe = giorni
    .map((giorno) => {
      const delGiorno = items.filter((i) => i.data === giorno).sort(confrontaImpegni);
      const contenuto = delGiorno.length
        ? `<ul class="day__items">${delGiorno
            .map((i) =>
              rigaImpegno(i, {
                conGiorno: false,
                meta: [chipCategoria(i.categoria), i.ora ? `<span class="item__time">${esc(i.ora)}</span>` : ""].join(""),
              }),
            )
            .join("")}</ul>`
        : state.solaLettura
          ? `<span class="day__add" aria-disabled="true">Libero</span>`
          : `<button class="day__add" type="button" data-action="new" data-date="${giorno}">+ Aggiungi</button>`;
      return `<li class="day" aria-label="${esc(dataLunga(giorno))}">${piastrellaGiorno(giorno, riferimento, { segnaRitardo: false })}${contenuto}</li>`;
    })
    .join("");

  return `
    <section class="group" aria-labelledby="week-label">
      <div class="weeknav">
        <button class="icon-btn" type="button" data-action="week-prev" aria-label="Settimana precedente">${ICONA_PRIMA}</button>
        <h2 class="weeknav__label" id="week-label">${esc(intervalloSettimana(state.lunedi))}</h2>
        ${settimanaCorrente ? "" : `<button class="btn btn--ghost btn--small" type="button" data-action="week-today">Oggi</button>`}
        <button class="icon-btn" type="button" data-action="week-next" aria-label="Settimana successiva">${ICONA_DOPO}</button>
      </div>
      <ol class="days">${righe}</ol>
    </section>`;
}

function vistaCompletati() {
  const tutti = completati();
  if (tutti.length === 0) {
    return statoVuoto("Nessun impegno completato", "Quando spunti un impegno lo ritrovi qui.");
  }
  const items = visibili(tutti).sort((a, b) => (b.completatoIl ?? 0) - (a.completatoIl ?? 0));
  if (items.length === 0) return nessunRisultato();

  const strumenti = state.solaLettura
    ? ""
    : `<div class="completed-tools">
        <button class="btn btn--danger btn--small" type="button" data-action="clear-done"
          data-armed="${state.confermaSvuota}">${state.confermaSvuota ? `Conferma: elimina ${tutti.length}` : "Svuota completati"}</button>
      </div>`;

  const righe = items
    .map((i) =>
      rigaImpegno(i, {
        riferimento: "0000-00-00", // già fatti: nessuna data va segnata in ritardo
        meta: [
          chipCategoria(i.categoria),
          `<span>${esc(dataMedia(i.data))}</span>`,
          i.completatoIl ? `<span>fatto il ${esc(formattaIstante(i.completatoIl))}</span>` : "",
        ].join(""),
      }),
    )
    .join("");

  return `
    <section class="group" aria-labelledby="g-done">
      <div class="group__head">
        <h2 class="group__title" id="g-done">Completati</h2>
        <span class="group__count">${items.length}</span>
      </div>
      ${strumenti}
      <ul class="list">${righe}</ul>
    </section>`;
}

const VISTE_RENDER = {
  prossimi: vistaProssimi,
  settimana: vistaSettimana,
  completati: vistaCompletati,
};
