# Osservatorio Consulenza del Lavoro

Progetto personale per restare aggiornati su normativa, prassi e novità in materia di
consulenza del lavoro. Un'attività pianificata di Claude Code genera ogni mattina
(lun–ven) un digest delle novità e lo salva in `digest/`.

## Struttura

| Percorso | Contenuto |
|---|---|
| `CLAUDE.md` | Istruzioni per la generazione del digest (lette dall'attività pianificata) |
| `fonti.md` | Fonti ufficiali e specializzate da monitorare |
| `temi.md` | Aree di interesse e parole chiave |
| `scadenzario.md` | Scadenze ricorrenti di adempimenti lavoro/paghe |
| `digest/AAAA/AAAA-MM-GG.md` | Digest giornalieri |
| `templates/digest.md` | Formato del digest |
| `note/` | Approfondimenti personali (facoltativo) |

## Come usarlo

- **Leggere le novità**: apri l'ultimo file in `digest/`.
- **Cambiare i temi o le fonti**: modifica `temi.md` / `fonti.md`; il digest successivo ne terrà conto.
- **Approfondire**: chiedi a Claude, ad esempio, "approfondisci la circolare INPS citata nel digest di oggi".

> I digest sono generati automaticamente da fonti web: verifica sempre il testo ufficiale
> (Gazzetta Ufficiale, circolari, messaggi) prima di applicarlo a casi concreti.
