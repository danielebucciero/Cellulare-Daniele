// Archivio nel browser (localStorage): usato quando l'app non gira dentro claude.ai.

function leggiLocale() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function scriviLocale(items) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    return true;
  } catch {
    return false;
  }
}

function creaArchivioLocale({ conEsempi }) {
  let items = leggiLocale();
  if (!Array.isArray(items)) {
    const adesso = Date.now();
    items = conEsempi
      ? IMPEGNI_INIZIALI.map((i) => ({ ...i, id: nuovoId(), fatto: false, creatoIl: adesso, completatoIl: null }))
      : [];
    scriviLocale(items);
  }

  const ascoltatori = new Set();
  const notifica = () => ascoltatori.forEach((cb) => cb(items.slice()));

  function salva(nuovi) {
    items = nuovi;
    scriviLocale(items);
    notifica();
  }

  return {
    modalita: "locale",
    solaLettura: false,

    ascolta(cb) {
      ascoltatori.add(cb);
      cb(items.slice());
      return () => ascoltatori.delete(cb);
    },

    async aggiungi(dati) {
      const id = nuovoId();
      salva([...items, { ...dati, id }]);
      return id;
    },

    async modifica(id, modifiche) {
      salva(items.map((i) => (i.id === id ? { ...i, ...modifiche } : i)));
    },

    async elimina(id) {
      salva(items.filter((i) => i.id !== id));
    },

    async ripristina(item) {
      salva([...items.filter((i) => i.id !== item.id), { ...item }]);
    },
  };
}
