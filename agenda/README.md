# Agenda di Daniele

Agenda personale pensata per il telefono, nata dal documento *Agenda settimanale di Daniele*.

**App online (claude.ai):** https://claude.ai/artifact/PuR6hzuDr9YFwqGV38jzjG
I dati stanno nel database dell'artifact e si sincronizzano tra telefono e computer.

## Cosa fa

- **Prossimi**: il prossimo impegno in evidenza e gli impegni da fare raggruppati in
  *In ritardo*, *Oggi*, *Domani*, *Questa settimana*, *Settimana prossima* e *Più avanti*.
- **Settimana**: da lunedì a domenica, con le frecce per spostarsi e «+ Aggiungi» sui giorni liberi.
- **Completati**: lo storico di ciò che hai spuntato, con la data di completamento.
  Puoi rimettere un impegno tra le cose da fare o svuotare l'elenco.
- Aggiunta e modifica da una scheda in basso: cosa, giorno, ora facoltativa, categoria e note.
  Ci sono le scorciatoie *Oggi*, *Domani*, *Lunedì prossimo* e *Tra una settimana*.
- Si può annullare dopo aver spuntato, eliminato o svuotato i completati.
- Ricerca su titolo, note e categoria. Tema chiaro e scuro automatici.

## Struttura

```
agenda/
├── build.mjs              unisce i moduli in dist/
├── src/
│   ├── index.html         struttura della pagina (segnaposto per CSS e JS)
│   ├── css/
│   │   ├── tokens.css     colori, caratteri, misure (tema chiaro e scuro)
│   │   ├── base.css       reset ed elementi di base
│   │   ├── layout.css     intestazione, schede, pulsante «Nuovo»
│   │   └── components.css impegni, gruppi, settimana, scheda, notifiche
│   └── js/
│       ├── constants.js   categorie, viste, chiavi
│       ├── seed.js        impegni iniziali (solo per la versione locale)
│       ├── util/          date (fuso locale) e aiuti DOM
│       ├── model.js       normalizzazione, validazione, ordinamento, gruppi
│       ├── store/         archivio: database claude.ai o localStorage
│       ├── state.js       stato dell'interfaccia
│       ├── ui/            componenti, viste, render, scheda, notifiche
│       ├── actions.js     spunta, elimina, svuota (con annulla)
│       └── main.js        avvio, eventi, navigazione con #prossimi/#settimana/#completati
├── test/model.test.mjs    test della logica di date e modello
└── dist/
    ├── agenda.html        versione pubblicata su claude.ai
    └── index.html         versione da aprire nel browser (dati in localStorage)
```

L'archivio ha un'interfaccia unica (`ascolta`, `aggiungi`, `modifica`, `elimina`, `ripristina`).
Su claude.ai usa il database dell'artifact. Aperta fuori da claude.ai usa `localStorage` del
browser e parte con gli impegni del documento originale.

## Comandi

Serve Node.js 18 o superiore, senza dipendenze da installare.

```sh
cd agenda
npm test        # test della logica
npm run build   # rigenera dist/agenda.html e dist/index.html
```

Dopo una modifica in `src/`, ricostruisci e ripubblica `dist/agenda.html` sullo stesso artifact.
