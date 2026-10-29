// Archivio nel database dell'artifact su claude.ai: si sincronizza tra telefono e computer.

function creaArchivioDb(db, solaLettura) {
  const collezione = db.collection(COLLEZIONE);

  return {
    modalita: "db",
    solaLettura,

    ascolta(cb, onErrore) {
      return collezione.onSnapshot(
        (snap) => cb(snap.docs.map((d) => ({ ...d.data(), id: d.id }))),
        onErrore,
      );
    },

    async aggiungi(dati) {
      const ref = collezione.doc(nuovoId());
      await ref.set(dati);
      return ref.id;
    },

    modifica: (id, modifiche) => collezione.doc(id).update(modifiche),

    elimina: (id) => collezione.doc(id).delete(),

    ripristina(item) {
      const { id, ...dati } = item;
      return collezione.doc(id).set(dati);
    },
  };
}
