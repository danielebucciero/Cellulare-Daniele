// Sceglie l'archivio: database di claude.ai se disponibile, altrimenti il browser.

async function collegaArchivio() {
  const claude = window.claude;
  if (!claude?.use) {
    return { archivio: creaArchivioLocale({ conEsempi: true }), avviso: null };
  }

  let db = null;
  try {
    db = await claude.use("db");
  } catch {
    db = null;
  }
  if (!db) {
    return {
      archivio: creaArchivioLocale({ conEsempi: false }),
      avviso: "Non riesco a raggiungere l'archivio online: le modifiche restano solo su questo dispositivo.",
    };
  }

  let solaLettura = false;
  try {
    const user = await claude.use("user");
    solaLettura = user ? (await user.can("data.write")) === false : false;
  } catch {
    solaLettura = false;
  }

  return {
    archivio: creaArchivioDb(db, solaLettura),
    avviso: solaLettura ? "Puoi consultare questa agenda ma non modificarla." : null,
  };
}
