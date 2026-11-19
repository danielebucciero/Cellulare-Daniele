# Ape Cosmetica – scheda per la comunicazione

Promemoria per le sessioni future di Claude: leggi questa scheda e le campagne in `campagne/`
prima di preparare spot, post o testi per l'erboristeria.

## L'attività
- **Ragione sociale:** Ape Cosmetica S.r.l. – società unipersonale (P. IVA 01890410903, REA SS-132720)
- **Insegna:** Erboristeria Ape Cosmetica, a Olbia **dal 1980**. Slogan nel logo: *"Nelle Erbe La Salute"*
  (logo: faro in un cerchio, scritta "ERBORISTERIA – Herbalist shop", file `spot/logo.png`)
- **Negozi a Olbia:**
  - Viale Aldo Moro 215 – tel. 0789 51171 (anche sede legale)
  - Corso Umberto 153 – tel. 0789 25121
- **Orari:** lunedì–sabato 9.00–13.15 e 15.30–19.30 (domenica chiuso)
- **WhatsApp:** +39 393 918 7689 (link `https://wa.me/393939187689`)
- **PEC:** apecosmeticasrl@pec.it

## Canali
- **Sito:** https://apecosmetica.com, fatto con Aruba Supersite. **Non è un e-commerce**: porta il cliente
  in negozio (chiama, WhatsApp, mappa). Pagine: Home, Le nostre offerte, Prodotti sardi, Erbe e tisane,
  Cosmesi naturale, Integratori, Oli essenziali, I nostri marchi, Negozi e orari, Chi siamo, Regali.
- **Instagram:** https://instagram.com/erboristeria.apecosmetica/
- **Facebook:** https://facebook.com/erbosarda/
- Instagram e Facebook non si leggono senza login: per vedere i post chiedere screenshot al titolare.
  **Non chiedere né accettare password.**
- Nell'ambiente cloud "Ape Cosmetica (sito web)" sono già consentiti il sito e i server Aruba che servono a leggerlo.
  Il sito si carica solo con un browser (Playwright) e a volte il server chiude la connessione: riprovare.

## Prodotti e marchi visti
L'Erbolario, Nature's, Bioearth, L'Amande, Erbe di Sardegna, Delicato d'Asina, Natur Unique (Aloe Attiva), Biokap.
Poi oli essenziali e vegetali, integratori, tè e tisane, miele e caramelle, prodotti sardi, make-up naturale,
erbe tintorie e henné, incensi, essenze e diffusori per la casa, lampade di sale.

**Confezioni regalo personalizzate** fatte in negozio: scatola kraft a pois marroni con finestra,
nastro di raso colorato, paglietta colorata, etichetta tonda "Erboristeria Ape Cosmetica" e cartellino verde
"BLACK FRIDAY da € … a € …" scritto a mano. Sul sito (pagina Regali) i prezzi vanno da 19,50 € a 59,00 €.

## Stile grafico usato negli spot
- **Colori:** verde scuro `#264634`, verde `#3E684A`, crema `#F7F1E6`, pois kraft `#D6C4A8`,
  rosso `#C42626` per i bollini, giallo caldo `#FFD278` per gli evidenziati.
- **Font** (in `spot/font/`, licenza SIL OFL): Playfair Display (titoli e prezzi),
  Dancing Script ("Erboristeria", "naturale", "Vieni a trovarci!"), Inter (testi piccoli).
- **Formato:** verticale 1080×1920 per Reel e Storie. Testi tra circa 250 e 1600 px di altezza, così i pulsanti
  di Instagram non li coprono. Video senza audio: la musica si aggiunge da Instagram.
- **Generatore:** `spot/genera_video.py`. Per una nuova campagna basta cambiare foto, prezzi e data (istruzioni in cima al file).

## Regole da rispettare negli annunci
- **Messaggio da dare:** invitare a **venire in negozio**. Le confezioni sono distribuite tra i due negozi
  e quelle mostrate sono solo alcune idee: in negozio ce ne sono tante altre.
  **Non invitare a prenotare** (né su WhatsApp né per telefono): è una scelta del titolare.
  **Non scrivere "pezzo unico"**: non tutte le confezioni lo sono.
- **Prezzi:** copiarli sempre dai cartellini in negozio e ricontrollarli. Nel primo video del Black Friday 2026
  c'erano tre prezzi sbagliati.
- **Sconto in percentuale:** deve essere vero. Si calcola sul prezzo più basso dei 30 giorni precedenti
  (Codice del consumo, art. 17-bis). Se la riduzione cresce durante la stessa promozione, di norma si parte
  dal prezzo pieno iniziale. In caso di dubbio, sentire il commercialista.
- **"Fino al -50%"** si può scrivere solo se c'è davvero almeno un prodotto con quello sconto.
- **Claim:** su cosmetici, tisane e integratori niente promesse terapeutiche ("cura", "guarisce").
  Usare "aiuta", "nutre", "coccola".
- **Foto:** controllare che nei vetri o nelle finestre delle scatole non ci siano riflessi di persone.

## Musica dei Reel
- `spot/musica_natale.py` compone e sintetizza una **musica natalizia originale**, senza diritti di terzi:
  campanelle, arpa, accordi morbidi e sonagli, in Re maggiore a 96 bpm, a circa -14 LUFS.
- `python3 spot/musica_natale.py --monta <video.mp4> <video_con_musica.mp4>` crea la musica della durata
  giusta e la monta nel video.
- In alternativa la musica si aggiunge da Instagram. In quel caso usare il video senza audio, per non sovrapporre due tracce.
