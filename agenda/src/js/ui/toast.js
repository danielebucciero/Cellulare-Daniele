// Notifica breve in basso, con "Annulla" facoltativo.

let timerNotifica = null;
let annullaCorrente = null;

function notifica(testo, annulla = null) {
  const toast = $("#toast");
  const bottone = $("#toast-undo");
  $("#toast-text").textContent = testo;
  annullaCorrente = annulla;
  bottone.hidden = !annulla;
  toast.hidden = false;
  clearTimeout(timerNotifica);
  timerNotifica = setTimeout(chiudiNotifica, DURATA_NOTIFICA_MS);
}

function chiudiNotifica() {
  $("#toast").hidden = true;
  annullaCorrente = null;
}

function collegaNotifica() {
  $("#toast-undo").addEventListener("click", () => {
    const annulla = annullaCorrente;
    chiudiNotifica();
    annulla?.();
  });
}
