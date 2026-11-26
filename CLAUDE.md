# Istruzioni per Claude

Scrivi sempre in italiano. Il repository contiene tre aree di lavoro del titolare di Ape Cosmetica S.r.l.
(erboristeria a Olbia). Capisci dall'inizio della richiesta di quale area si tratta e leggi prima la sua scheda:

| Area | Parole d'inizio tipiche | Leggi prima |
|---|---|---|
| **Pubblicità e social** | "Social:", post, Reel, video, Instagram, Facebook, sito, sponsorizzata | `ape-cosmetica/README.md`, `ape-cosmetica/campagne/`, skill `pubblicita-e-social` |
| **Magazzino e gestione** | "Magazzino:", scorte, ordini, fornitori, inventario | `magazzino/README.md` |
| **Consultazione contabile** | "Contabilità:", fisco, scadenze, F24, personale, lavoro | `contabilita/README.md` e, per il lavoro, l'osservatorio qui sotto |

Se la richiesta non è chiara, chiedi a quale area appartiene. Non mescolare le aree nello stesso file.

## Osservatorio sulla consulenza del lavoro

I file nella radice (`digest/`, `scadenzario.md`, `temi.md`, `fonti.md`, `templates/`, `note/`) sono un osservatorio
sulla consulenza del lavoro in Italia.

## Generazione del digest giornaliero

Quando ti viene chiesto di generare il digest:

1. Leggi `temi.md`, `fonti.md` e gli ultimi 5 digest in `digest/` (per non ripetere notizie già riportate).
2. Cerca sul web le novità pubblicate dall'ultimo digest (di norma le ultime 24 ore; il lunedì copri il fine settimana).
   Fai più ricerche in parallelo, una per area di `temi.md`, privilegiando le fonti ufficiali di `fonti.md`.
   Il lunedì cerca anche la rassegna "Le Novità Normative della Settimana" del Consiglio nazionale dei Consulenti
   del Lavoro e le sentenze della Corte costituzionale e della Cassazione in materia di lavoro, per recuperare novità
   sfuggite nei giorni precedenti.
3. Includi solo novità concrete e datate: norme pubblicate in Gazzetta Ufficiale, decreti, circolari e messaggi
   INPS/INAIL/INL/Agenzia delle Entrate, interpelli, rinnovi o accordi CCNL, sentenze rilevanti, scadenze imminenti.
   Escludi opinioni, notizie non verificabili e duplicati.
4. Per ogni novità indica: titolo, data, fonte con link, sintesi in 2–4 righe, impatto pratico per il consulente
   (chi riguarda, cosa fare, da quando).
5. Aggiungi la sezione "Scadenze dei prossimi 7 giorni" usando `scadenzario.md` e le eventuali proroghe trovate.
6. Salva il file in `digest/AAAA/AAAA-MM-GG.md` seguendo `templates/digest.md`.
   Se non ci sono novità rilevanti, crea comunque il file scrivendolo esplicitamente.
7. Aggiorna `digest/INDICE.md` aggiungendo in cima una riga: `- [AAAA-MM-GG](AAAA/AAAA-MM-GG.md) — N novità: titoli brevi`.
8. Fai commit con messaggio `Digest AAAA-MM-GG` e push sul branch `main`.

## Cartelle `ape-cosmetica/`, `magazzino/`, `contabilita/`

Sono separate dall'osservatorio: le istruzioni sul digest non si applicano a queste cartelle.

## Regole

- Non inventare numeri di circolari, date o importi: se non sei sicuro, scrivi "da verificare" e cita la fonte.
- Distingui chiaramente norme in vigore, norme approvate ma non ancora pubblicate e semplici proposte.
- Se trovi una nuova scadenza ricorrente o una proroga stabile, aggiorna anche `scadenzario.md`.
