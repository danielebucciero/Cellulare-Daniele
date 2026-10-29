// Azioni sugli impegni: ognuna scrive nell'archivio e avvisa con una notifica.

const MESSAGGI_ERRORE = {
  quota_exceeded: "L'archivio è pieno: elimina qualche impegno completato e riprova.",
  invalid_argument: "Non hai i permessi per modificare questa agenda.",
  revoked: "L'accesso all'agenda è cambiato: ricarica la pagina.",
};

async function esegui(operazione, messaggio, annulla = null) {
  try {
    await operazione();
    if (messaggio) notifica(messaggio, annulla);
    return true;
  } catch (err) {
    if (err?.code === "invalid_argument" && state.archivio.modalita === "db") {
      state.solaLettura = true;
      render();
    }
    notifica(MESSAGGI_ERRORE[err?.code] ?? "Salvataggio non riuscito. Controlla la connessione e riprova.");
    return false;
  }
}

async function cambiaStato(item) {
  const fatto = !item.fatto;
  const prima = { fatto: item.fatto, completatoIl: item.completatoIl };
  await esegui(
    () => state.archivio.modifica(item.id, { fatto, completatoIl: fatto ? Date.now() : null }),
    fatto ? "Fatto! Spostato nei completati" : "Rimesso tra le cose da fare",
    () => esegui(() => state.archivio.modifica(item.id, prima)),
  );
}

async function eliminaImpegno(item) {
  await esegui(
    () => state.archivio.elimina(item.id),
    "Impegno eliminato",
    () => esegui(() => state.archivio.ripristina(item), "Impegno ripristinato"),
  );
}

async function svuotaCompletati() {
  const daEliminare = completati();
  state.confermaSvuota = false;
  await esegui(
    () => Promise.all(daEliminare.map((i) => state.archivio.elimina(i.id))),
    daEliminare.length === 1 ? "1 impegno eliminato" : `${daEliminare.length} impegni eliminati`,
    () => esegui(() => Promise.all(daEliminare.map((i) => state.archivio.ripristina(i))), "Impegni ripristinati"),
  );
}
