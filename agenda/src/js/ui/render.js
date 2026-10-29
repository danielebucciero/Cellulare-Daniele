// Ridisegna intestazione e vista corrente a partire dallo stato.

function render() {
  const riferimento = oggi();
  $("#oggi-label").textContent = dataLunga(riferimento);

  $("#count-prossimi").textContent = state.caricato ? String(daFare().length || "") : "";
  $("#count-completati").textContent = state.caricato ? String(completati().length || "") : "";

  for (const tab of $$(".tab")) {
    if (tab.dataset.view === state.vista) tab.setAttribute("aria-current", "page");
    else tab.removeAttribute("aria-current");
  }

  $("#fab-nuovo").hidden = state.solaLettura;
  $("#main").innerHTML = state.caricato ? VISTE_RENDER[state.vista]() : statoCaricamento();
}

function mostraAvviso(testo) {
  const banner = $("#banner");
  banner.textContent = testo ?? "";
  banner.hidden = !testo;
}
