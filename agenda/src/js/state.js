// Stato dell'interfaccia. Gli impegni arrivano dall'archivio; il resto è locale alla vista.

const state = {
  archivio: null,
  items: [],
  caricato: false,
  solaLettura: false,
  vista: VISTA_PREDEFINITA,
  lunedi: inizioSettimana(oggi()),
  ricerca: "",
  confermaSvuota: false,
};

const daFare = () => state.items.filter((i) => !i.fatto);
const completati = () => state.items.filter((i) => i.fatto);
const visibili = (items) => items.filter((i) => corrispondeRicerca(i, state.ricerca));
const trovaImpegno = (id) => state.items.find((i) => i.id === id);
