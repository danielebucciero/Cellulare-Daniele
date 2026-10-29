// Avvio: collega eventi, navigazione e archivio.

function vistaDaHash() {
  const nome = location.hash.slice(1);
  return VISTE.includes(nome) ? nome : VISTA_PREDEFINITA;
}

function applicaHash() {
  state.vista = vistaDaHash();
  state.confermaSvuota = false;
  render();
}

function gestisciClick(event) {
  const bersaglio = event.target.closest("[data-action]");
  if (!bersaglio) return;
  const azione = bersaglio.dataset.action;
  const id = bersaglio.dataset.id ?? bersaglio.closest("[data-id]")?.dataset.id;
  const item = id ? trovaImpegno(id) : null;

  switch (azione) {
    case "new":
      apriScheda({ data: bersaglio.dataset.date ?? null });
      break;
    case "edit":
      if (item) apriScheda({ item });
      break;
    case "toggle":
      if (item && !state.solaLettura) cambiaStato(item);
      break;
    case "close-sheet":
      chiudiScheda();
      break;
    case "delete":
      eliminaDaScheda();
      break;
    case "quick-date":
      $("#f-data").value = bersaglio.dataset.date;
      aggiornaScorciatoie();
      break;
    case "week-prev":
      state.lunedi = aggiungiGiorni(state.lunedi, -7);
      render();
      break;
    case "week-next":
      state.lunedi = aggiungiGiorni(state.lunedi, 7);
      render();
      break;
    case "week-today":
      state.lunedi = inizioSettimana(oggi());
      render();
      break;
    case "clear-done":
      if (state.confermaSvuota) svuotaCompletati();
      else {
        state.confermaSvuota = true;
        render();
      }
      break;
  }
}

async function avvia() {
  collegaScheda();
  collegaNotifica();
  document.addEventListener("click", gestisciClick);
  window.addEventListener("hashchange", applicaHash);
  $("#cerca").addEventListener("input", (e) => {
    state.ricerca = e.target.value.trim();
    render();
  });
  // Se l'app resta aperta oltre la mezzanotte, "Oggi" si aggiorna al ritorno.
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) render();
  });

  applicaHash();

  const { archivio, avviso } = await collegaArchivio();
  state.archivio = archivio;
  state.solaLettura = archivio.solaLettura;
  mostraAvviso(avviso);

  archivio.ascolta(
    (items) => {
      state.items = items.map(normalizzaImpegno);
      state.caricato = true;
      render();
    },
    () => mostraAvviso("La sincronizzazione si è interrotta. Ricarica la pagina per riprovare."),
  );
}

avvia();
