# Istruzioni per Claude

Questo repository è un osservatorio sulla consulenza del lavoro in Italia. Scrivi sempre in italiano.

## Generazione del digest giornaliero

Quando ti viene chiesto di generare il digest:

1. Leggi `temi.md`, `fonti.md` e gli ultimi 5 digest in `digest/` (per non ripetere notizie già riportate).
2. Cerca sul web le novità pubblicate dall'ultimo digest (di norma le ultime 24 ore; il lunedì copri il fine settimana).
   Fai più ricerche in parallelo, una per area di `temi.md`, privilegiando le fonti ufficiali di `fonti.md`.
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

## Regole

- Non inventare numeri di circolari, date o importi: se non sei sicuro, scrivi "da verificare" e cita la fonte.
- Distingui chiaramente norme in vigore, norme approvate ma non ancora pubblicate e semplici proposte.
- Se trovi una nuova scadenza ricorrente o una proroga stabile, aggiorna anche `scadenzario.md`.
