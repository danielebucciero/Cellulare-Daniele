#!/usr/bin/env python3
"""Genera costs.csv / spostamenti.csv / riepilogo.md per il viaggio in Islanda
e verifica che i numeri coincidano con itinerario.md.

Uso: python3 calcola_viaggio.py
"""
import csv
import re
import sys
from collections import OrderedDict
from pathlib import Path

DIR = Path(__file__).resolve().parent

# --- Parametri -------------------------------------------------------------
CAMBIO = 142.0  # ISK per 1 EUR
FONTE_CAMBIO = ("https://www.dove-e-quando.it/soldi/islanda/reykjavik/ "
                "(141,6 al 23/08/2026) e https://www.profee.com/it/currency-exchange/eur-isk")
BUDGET_PP = 1500.0
CONSUMO_L_100KM = 6.5          # stima Dacia Duster 4x4 diesel, inverno
PREZZO_DIESEL = 315            # ISK/L, ottobre 2026
FONTE_DIESEL = "https://dailyfuels.com/iceland/ (diesel 315 ISK/L, ott. 2026)"
TASSA_KM = 6.95                # ISK/km, in vigore dal 1/1/2026
FONTE_TASSA_KM = "https://www.dollar.is/iceland-travel-guide/driving-in-iceland/icelands-new-kilometer-tax-2026-a-complete-guide/"

GIORNI = OrderedDict([
    (1, "2027-03-27"), (2, "2027-03-28"), (3, "2027-03-29"), (4, "2027-03-30"),
    (5, "2027-03-31"), (6, "2027-04-01"), (7, "2027-04-02"), (8, "2027-04-03"),
    (9, "2027-04-04"),
])

# --- Tratte in auto: (giorno, partenza, arrivo, km, minuti, strade da controllare)
TRATTE = [
    (1, "Aeroporto KEF (ritiro auto)", "Reykjanesbær (Bónus)", 5, 10, "—"),
    (1, "Reykjanesbær", "Borgarnes", 115, 90,
     "Strada 41 e Ring Road 1; galleria Hvalfjarðargöng (gratuita); vento forte a Kjalarnes"),
    (2, "Borgarnes", "Hvammstangi", 128, 100,
     "Passo Holtavörðuheiði (407 m) sulla 1: neve e chiusure frequenti"),
    (2, "Hvammstangi", "Hvítserkur", 30, 45,
     "Strada 711 sterrata, servizio invernale ridotto: controllare umferdin.is"),
    (2, "Hvítserkur", "Blönduós (via Borgarvirki)", 60, 60,
     "Strade 711/716 sterrate, poi Ring Road 1"),
    (2, "Blönduós", "Bólstaðarhlíð", 28, 20, "Ring Road 1"),
    (3, "Bólstaðarhlíð", "Varmahlíð", 30, 25, "Passo Vatnsskarð sulla 1"),
    (3, "Varmahlíð", "Akureyri", 95, 75,
     "Passo Öxnadalsheiði (540 m): neve, ghiaccio, chiusure con bufera"),
    (3, "Akureyri", "Goðafoss", 35, 30,
     "Galleria a pedaggio Vaðlaheiðargöng oppure passo Víkurskarð (gratuito, spesso chiuso)"),
    (3, "Goðafoss", "Reykjahlíð (Mývatn)", 50, 40, "Ring Road 1, tratti ghiacciati"),
    (4, "Reykjahlíð", "Hverir (Námafjall)", 7, 10, "Passo Námaskarð sulla 1"),
    (4, "Hverir", "Dettifoss ovest", 50, 45,
     "Strada 862: servizio invernale solo da metà marzo e può chiudere all'improvviso; la 864 (lato est) è senza servizio invernale"),
    (4, "Dettifoss ovest", "Möðrudalur (Fjallakaffi)", 67, 55,
     "Altipiano Möðrudalsöræfi (~600 m) sulla 1: tra i tratti più esposti dell'isola"),
    (4, "Möðrudalur", "Stuðlagil ovest (Grund)", 75, 60,
     "Strada 923 Jökuldalsvegur: ultimo tratto sterrato, verificare servizio invernale"),
    (4, "Stuðlagil ovest", "Egilsstaðir", 70, 55, "Strada 923 e Ring Road 1"),
    (5, "Egilsstaðir", "Fáskrúðsfjörður", 50, 45,
     "Passo Fagradalur (strada 92); galleria Fáskrúðsfjarðargöng. NON usare la 939 Öxi: senza servizio invernale"),
    (5, "Fáskrúðsfjörður", "Djúpivogur", 105, 85, "Strada costiera 96/1 dei fiordi orientali, cadute massi"),
    (5, "Djúpivogur", "Stokksnes", 90, 70, "Ring Road 1, Hvalnesskriður (frane); galleria Almannaskarð"),
    (5, "Stokksnes", "Höfn", 15, 15, "Breve tratto sterrato verso il Viking Café"),
    (6, "Höfn", "Jökulsárlón", 80, 60, "Ring Road 1, vento laterale"),
    (6, "Jökulsárlón", "Diamond Beach", 1, 5, "—"),
    (6, "Diamond Beach", "Fjallsárlón", 11, 10, "—"),
    (6, "Fjallsárlón", "Múlagljúfur (parcheggio)", 14, 20, "Ultimi 2 km sterrati e sconnessi, senza segnaletica"),
    (6, "Múlagljúfur", "Skaftafell", 25, 20, "Ring Road 1, raffiche al Skeiðarársandur"),
    (6, "Skaftafell", "Kirkjubæjarklaustur", 70, 55, "Ring Road 1, ponti a corsia unica"),
    (7, "Kirkjubæjarklaustur", "Vík", 72, 55,
     "Mýrdalssandur: tempeste di vento e sabbia, chiusure della 1 frequenti"),
    (7, "Vík", "Reynisfjara", 10, 15, "Strada 215"),
    (7, "Reynisfjara", "Dyrhólaey", 12, 15, "Strada 218: tratto ripido e sterrato verso il faro, può essere chiuso"),
    (7, "Dyrhólaey", "Skógafoss", 30, 25, "Ring Road 1"),
    (7, "Skógafoss", "Seljalandsfoss", 30, 25, "Ring Road 1, raffiche sotto l'Eyjafjallajökull"),
    (7, "Seljalandsfoss", "Hella", 40, 30, "Ring Road 1"),
    (8, "Hella", "Kerið", 50, 40, "Ring Road 1 e strada 35"),
    (8, "Kerið", "Faxi", 45, 35, "Strada 35"),
    (8, "Faxi", "Geysir", 20, 15, "Strada 35"),
    (8, "Geysir", "Gullfoss", 10, 10, "Strada 35"),
    (8, "Gullfoss", "Þingvellir", 70, 60, "Strade 35/37/365 (Lyngdalsheiði): ghiaccio"),
    (8, "Þingvellir", "Reykjavík", 45, 45, "Strada 36 Mosfellsheiði: chiusure con bufera"),
    (9, "Reykjavík", "Blue Lagoon", 50, 45,
     "Strade 41 e 43: attività vulcanica a Reykjanes/Grindavík, controllare chiusure su safetravel.is"),
    (9, "Blue Lagoon", "Aeroporto KEF (riconsegna auto)", 22, 25, "Strada 43/41"),
]

# --- Costi -----------------------------------------------------------------
# (giorno, categoria, descrizione, importo, valuta, fonte, stima?, ristorante?)
# valuta: "ISK" o "EUR"; l'importo è sempre per DUE persone.
U_KAYAK_MXP = "https://www.kayak.it/voli/Milano-Aeroporto-Malpensa-MXP/Reykjavik-Keflavik-KEF"
U_MOMONDO_OLB = "https://www.momondo.it/volo/olbia/aeroporto-di-milano-malpensa-mxp"
U_CAR = "https://www.kayak.it/Autonoleggi-economici-Keflavik.5406.cars.ksp"
U_CAR2 = "https://www.discovercars.com/it/suv/keflafik-airport-kef_1787"
U_FOOD = "https://guidetoiceland.is/travel-info/food-prices-in-iceland"
U_ISNET = "https://isnet.is/iceland/food/"
U_PARK = "https://happycampers.is/driving-in-iceland-parking-fees-and-road-tolls/"
U_GOCAMP = "https://www.gocampers.is/guides/money/parking-fees-iceland/"

COSTI = [
    # Voli (andata)
    (1, "volo", "Olbia → Milano Malpensa, 2 biglietti solo andata, bagaglio a mano", 120, "EUR", U_MOMONDO_OLB, True, False),
    (1, "volo", "Olbia → Malpensa, 1 bagaglio da stiva condiviso", 35, "EUR", U_MOMONDO_OLB, True, False),
    (1, "volo", "Malpensa → Keflavík (easyJet/Wizz Air), 2 biglietti solo andata", 300, "EUR", U_KAYAK_MXP, True, False),
    (1, "volo", "Malpensa → Keflavík, 1 bagaglio da stiva 23 kg condiviso", 45, "EUR", U_KAYAK_MXP, True, False),
    # Auto
    (1, "auto", "Noleggio Dacia Duster 4x4 o simile, 8 giorni (27/3–4/4), periodo pasquale", 440, "EUR", U_CAR + " ; " + U_CAR2, True, False),
    (1, "auto", "Assicurazione SCDW + ghiaia/pietrisco (GP), 8 giorni", 144, "EUR", U_CAR2, True, False),
    (3, "auto", "Pedaggio galleria Vaðlaheiðargöng (Akureyri → Goðafoss), pagamento online", 1800, "ISK", "https://veggjald.is (da verificare)", True, False),
    # Alloggi (prezzo per notte, camera doppia)
    (1, "alloggio", "Setrið Guesthouse, Borgarnes (cucina in comune)", 17500, "ISK", "https://www.priceline.com/hotel-deals/en-us/P5000084841/H101442706/setrid-guesthouse.ssp", True, False),
    (2, "alloggio", "Bólstaðarhlíð Guesthouse – appartamento (con cucina)", 19500, "ISK", "https://www.hotels.com/ho891702144/bolsta-arhli-guesthouse-blonduos-iceland/", True, False),
    (3, "alloggio", "Eldá Guesthouse, Reykjahlíð – Mývatn (bagno in comune)", 20000, "ISK", "https://www.kayak.com/Myvatn-Hotels-Elda-Guesthouse.2313389.ksp", True, False),
    (4, "alloggio", "Lyngás Guesthouse, Egilsstaðir (cucina in comune)", 16500, "ISK", "https://www.priceline.com/hotel-deals/en-us/P5000372856/H48867404/lyngas-guesthouse.ssp", True, False),
    (5, "alloggio", "Höfn Guesthouse, Hafnarbraut 21 – Höfn", 14000, "ISK", "https://www.kayak.com/Hofn-Hotels-Hoefn-Guesthouse.2604228.ksp", True, False),
    (6, "alloggio", "Landbrot Guesthouse, Kirkjubæjarklaustur (angolo cottura in camera)", 18500, "ISK", "https://www.hotels.com/es/ho1189421632/", True, False),
    (7, "alloggio", "Welcome Riverside Guesthouse, Hella (cucina in comune)", 15000, "ISK", "https://kayak.ie/Hella-Hotels-Welcome-Riverside-Guesthouse.2846257.ksp", True, False),
    (8, "alloggio", "Reykjavik Peace Center Guesthouse (cucina)", 16000, "ISK", "https://www.kayak.com/Reykjavik-Hotels-Reykjavik-Peace-Center---Guesthouse.363676.ksp", True, False),
    # Cibo (per due persone)
    (1, "cibo", "Spesa grande al Bónus di Reykjanesbær (scorte per Pasqua: 28–29/3 negozi chiusi)", 18000, "ISK", U_FOOD, True, False),
    (2, "cibo", "Pranzo alla stazione N1 Staðarskáli (zuppa/hot dog), aperta a Pasqua", 5000, "ISK", U_ISNET, True, True),
    (3, "cibo", "Rifornimento spesa ad Akureyri (verificare apertura Lunedì dell'Angelo)", 8000, "ISK", U_FOOD, True, False),
    (3, "cibo", "Cena a Daddi's Pizza, Reykjahlíð", 7500, "ISK", U_ISNET, True, True),
    (4, "cibo", "Zuppa di carne a Fjallakaffi, Möðrudalur (2 porzioni)", 5800, "ISK", U_ISNET, True, True),
    (4, "cibo", "Spesa al Bónus di Egilsstaðir", 7000, "ISK", U_FOOD, True, False),
    (5, "cibo", "Spesa per pranzo al sacco + colazioni", 4000, "ISK", U_FOOD, True, False),
    (5, "cibo", "Panini all'aragosta (humar) a Höfn, 2 porzioni", 7000, "ISK", U_ISNET, True, True),
    (6, "cibo", "Zuppa al caffè di Jökulsárlón (2 porzioni)", 5000, "ISK", U_ISNET, True, True),
    (6, "cibo", "Spesa al Kjarval di Kirkjubæjarklaustur", 6000, "ISK", U_FOOD, True, False),
    (7, "cibo", "Spesa alla Krónan di Vík", 6000, "ISK", U_FOOD, True, False),
    (7, "cibo", "Pranzo a Vík (hamburger, 2 porzioni)", 7600, "ISK", U_ISNET, True, True),
    (8, "cibo", "Spesa per pranzo al sacco", 4000, "ISK", U_FOOD, True, False),
    (8, "cibo", "Cena a Reykjavík: zuppa di agnello a volontà, Icelandic Street Food (2×2.290)", 4580, "ISK", "https://www.machupicchu.org/reykjavik-budget-guide-2026-complete-cost-breakdown.htm", True, True),
    (9, "cibo", "Spuntino in aeroporto KEF (2 persone)", 5000, "ISK", U_ISNET, True, True),
    # Attività
    (5, "attività", "Ingresso Stokksnes / Vestrahorn al Viking Café (2×1.100)", 2200, "ISK", "https://www.hertz.is/iceland-attractions/stokksnes/", False, False),
    (8, "attività", "Ingresso cratere Kerið (2×700)", 1400, "ISK", "https://en.wikipedia.org/wiki/Keri%C3%B0", False, False),
    (9, "attività", "Blue Lagoon, biglietto Comfort (2×13.500; tariffa 2026 13.000, 2027 stimata)", 27000, "ISK", "https://www.bluelagoon.com/travel-professionals/BL-ratecard2026", True, False),
    # Parcheggi (per auto)
    (4, "parcheggio", "Hverir / Námafjall", 1000, "ISK", U_GOCAMP, True, False),
    (4, "parcheggio", "Dettifoss ovest (fonti discordanti: gratuito o 1.000)", 1000, "ISK", "https://www.holdurcarrental.is/travel-inspiration/your-guide-to-visiting-dettifoss-waterfall-by-car-icelands-thundering-wonder-awaits", True, False),
    (4, "parcheggio", "Stuðlagil ovest (Parka o terminale)", 1000, "ISK", U_GOCAMP, False, False),
    (6, "parcheggio", "Jökulsárlón", 1000, "ISK", U_PARK, False, False),
    (6, "parcheggio", "Diamond Beach", 1000, "ISK", U_PARK, True, False),
    (6, "parcheggio", "Fjallsárlón", 1000, "ISK", U_PARK, True, False),
    (7, "parcheggio", "Reynisfjara (750–1.000 secondo il parcheggio)", 1000, "ISK", U_PARK, False, False),
    (7, "parcheggio", "Skógafoss", 1000, "ISK", U_PARK, False, False),
    (7, "parcheggio", "Seljalandsfoss (checkit.is)", 1000, "ISK", "https://www.locationscout.net/articles/81-iceland-update-2026-new-road-fees-parking-costs-and-digital-border-controls", False, False),
    (8, "parcheggio", "Þingvellir (1.000 nel 2025, 1.200 stimato)", 1200, "ISK", "https://www.locationscout.net/articles/81-iceland-update-2026-new-road-fees-parking-costs-and-digital-border-controls", True, False),
    (8, "parcheggio", "Sosta a pagamento a Reykjavík (sera + mattina)", 1500, "ISK", "https://www.camperrentaliceland.com/blog/driving/parking-iceland", True, False),
    # Voli (ritorno)
    (9, "volo", "Keflavík → Milano Malpensa, 2 biglietti solo andata", 300, "EUR", U_KAYAK_MXP, True, False),
    (9, "volo", "Keflavík → Malpensa, 1 bagaglio da stiva condiviso", 45, "EUR", U_KAYAK_MXP, True, False),
    (9, "volo", "Milano Malpensa → Olbia, 2 biglietti solo andata", 120, "EUR", U_MOMONDO_OLB, True, False),
    (9, "volo", "Malpensa → Olbia, 1 bagaglio da stiva condiviso", 35, "EUR", U_MOMONDO_OLB, True, False),
]

CATEGORIE = ["volo", "auto", "carburante", "tassa chilometrica", "parcheggio", "alloggio", "cibo", "attività"]


def km_giorno(g):
    return sum(t[3] for t in TRATTE if t[0] == g)


def min_giorno(g):
    return sum(t[4] for t in TRATTE if t[0] == g)


def fmt_durata(m):
    return f"{m // 60} h {m % 60:02d} min"


def costruisci_righe():
    righe = []
    for g, cat, desc, imp, val, fonte, stima, rist in COSTI:
        if val == "EUR":
            eur = float(imp)
            isk = round(eur * CAMBIO)
        else:
            isk = int(imp)
            eur = isk / CAMBIO
        righe.append(dict(giorno=g, cat=cat, desc=desc, isk=isk, eur=eur, fonte=fonte, stima=stima, rist=rist))
    # Carburante: quota giornaliera in base ai km
    for g in GIORNI:
        km = km_giorno(g)
        litri = km * CONSUMO_L_100KM / 100
        isk = round(litri * PREZZO_DIESEL)
        righe.append(dict(giorno=g, cat="carburante",
                          desc=f"Gasolio per {km} km ({litri:.1f} L a {CONSUMO_L_100KM} L/100 km)",
                          isk=isk, eur=isk / CAMBIO, fonte=FONTE_DIESEL, stima=True, rist=False))
    # Tassa chilometrica: addebitata dal noleggiatore alla riconsegna
    km_tot = sum(t[3] for t in TRATTE)
    isk = round(km_tot * TASSA_KM)
    righe.append(dict(giorno=9, cat="tassa chilometrica",
                      desc=f"Kílómetragjald {TASSA_KM} ISK/km × {km_tot} km, addebitata alla riconsegna",
                      isk=isk, eur=isk / CAMBIO, fonte=FONTE_TASSA_KM, stima=False, rist=False))
    righe.sort(key=lambda r: (r["giorno"], CATEGORIE.index(r["cat"])))
    return righe


def scrivi_costi(righe):
    tot_cat = OrderedDict((c, [0, 0.0]) for c in CATEGORIE)
    with open(DIR / "costi.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["giorno", "data", "categoria", "descrizione", "costo_isk",
                    "costo_eur_2_persone", "costo_eur_a_persona", "fonte"])
        for r in righe:
            fonte = r["fonte"] + (" [STIMA]" if r["stima"] else "")
            w.writerow([r["giorno"], GIORNI[r["giorno"]], r["cat"], r["desc"], r["isk"],
                        f"{r['eur']:.2f}", f"{r['eur'] / 2:.2f}", fonte])
            tot_cat[r["cat"]][0] += r["isk"]
            tot_cat[r["cat"]][1] += r["eur"]
        for c, (isk, eur) in tot_cat.items():
            w.writerow(["", "", c, f"TOTALE {c}", isk, f"{eur:.2f}", f"{eur / 2:.2f}", ""])
        tot_isk = sum(v[0] for v in tot_cat.values())
        tot_eur = sum(v[1] for v in tot_cat.values())
        w.writerow(["", "", "TOTALE", "TOTALE GENERALE", tot_isk, f"{tot_eur:.2f}", f"{tot_eur / 2:.2f}",
                    f"Cambio 1 EUR = {CAMBIO:.0f} ISK: {FONTE_CAMBIO}"])
    return tot_cat, tot_isk, tot_eur


def scrivi_spostamenti():
    with open(DIR / "spostamenti.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["giorno", "data", "partenza", "arrivo", "km", "durata_stimata", "strade_da_controllare"])
        for g, p, a, km, m, note in TRATTE:
            w.writerow([g, GIORNI[g], p, a, km, fmt_durata(m), note])
        tot_km = sum(t[3] for t in TRATTE)
        tot_m = sum(t[4] for t in TRATTE)
        w.writerow(["", "", "TOTALE", "", tot_km, fmt_durata(tot_m), ""])
    return tot_km, tot_m


def eur(x):
    s = f"{x:,.0f}".replace(",", ".")
    return f"{s} €"


def isk(x):
    return f"{x:,.0f}".replace(",", ".") + " ISK"


def scrivi_riepilogo(righe, tot_cat, tot_isk, tot_eur, tot_km):
    pp = tot_eur / 2
    diff = pp - BUDGET_PP
    # Risparmi possibili (per persona)
    rist = sum(r["eur"] for r in righe if r["rist"])
    risp_cibo = (rist - sum(r["isk"] for r in righe if r["rist"]) * 0.35 / CAMBIO) / 2  # spesa al supermercato ≈ 35% del costo al ristorante
    risp_alloggi = tot_cat["alloggio"][1] * 0.20 / 2
    blue = next(r for r in righe if r["desc"].startswith("Blue Lagoon"))
    risp_blue = (blue["isk"] - 2 * 1700) / CAMBIO / 2  # piscina comunale ≈ 1.700 ISK a testa (stima)
    risp_tot = risp_cibo + risp_alloggi + risp_blue

    righe_cat = "\n".join(
        f"| {c} | {isk(v[0])} | {eur(v[1])} | {eur(v[1] / 2)} |" for c, v in tot_cat.items())
    esito = (f"**Il budget è superato di circa {eur(diff)} a persona** ({eur(pp)} contro {eur(BUDGET_PP)})."
             if diff > 0 else f"**Il budget è rispettato**: avanzano circa {eur(-diff)} a persona.")
    testo = f"""# Riepilogo costi – Islanda in auto, 27 marzo – 4 aprile 2027

*File generato da `calcola_viaggio.py`: non modificare a mano i numeri, rilancia lo script.*

- **Viaggiatori:** 2 adulti, partenza da Olbia
- **Cambio usato:** 1 € = {CAMBIO:.0f} ISK. Valori più recenti trovati: 141,6 ISK al 23/08/2026 e 143,2 ISK al 24/07/2026. Fonti: {FONTE_CAMBIO}
- **Chilometri in auto:** {tot_km} km, con tassa chilometrica a {str(TASSA_KM).replace(".", ",")} ISK/km
- **Avvertenza:** quasi tutte le cifre sono **stime** basate su prezzi del 2026, perché a ottobre 2026 non sono ancora in vendita voli, auto e camere per la Pasqua 2027. In `costi.csv` le stime sono segnate con [STIMA] nella colonna fonte.

## Totali per categoria

| Categoria | ISK | € per 2 persone | € a persona |
|---|---:|---:|---:|
{righe_cat}
| **TOTALE** | **{isk(tot_isk)}** | **{eur(tot_eur)}** | **{eur(pp)}** |

## Confronto con il budget

- Budget: {eur(BUDGET_PP)} a persona, cioè {eur(BUDGET_PP * 2)} in due
- Costo stimato: {eur(pp)} a persona, cioè {eur(tot_eur)} in due
- {esito}

Le voci che pesano di più sono gli alloggi (Pasqua e camere doppie in zone con poca offerta), i voli con due tratte separate e il cibo. Quest'ultimo resta alto anche cucinando quasi sempre: in Islanda la spesa costa circa il 44% in più della media UE ([Guide to Iceland, ottobre 2026]({U_FOOD})).

Non sono compresi: un'eventuale notte a Milano se al ritorno non c'è una coincidenza serale per Olbia (circa 90–120 € a camera, stima), le escursioni facoltative (grotta di ghiaccio, Mývatn Nature Baths), i ramponcini (circa 20–30 € al paio in Italia), souvenir e alcolici.

## 3 modi per risparmiare

1. **Cucinare tutti i pasti e saltare i locali (risparmio ≈ {eur(risp_cibo)} a persona).** Tutti gli alloggi scelti hanno una cucina. Puoi sostituire i pasti fuori ({eur(rist)} in due) con spesa da Bónus o Krónan, che costa circa un terzo: panini e thermos di zuppa per pranzo, pasta e pesce surgelato per cena. Porta da casa caffè, condimenti e snack, nei limiti del bagaglio.
2. **Prendere camere con bagno in comune o ostelli HI con camera privata (risparmio ≈ {eur(risp_alloggi)} a persona, circa −20% sugli alloggi).** Conviene soprattutto a Borgarnes (Borgarnes HI Hostel), Höfn e Reykjavík. Prenota appena aprono le date di Pasqua 2027 con tariffa cancellabile, poi ricontrolla i prezzi a gennaio. L'Eldá resta com'è, perché l'hai chiesto tu.
3. **Sostituire la Blue Lagoon con una piscina termale pubblica (risparmio ≈ {eur(risp_blue)} a persona).** Le piscine comunali di Reykjavík, come Sundhöllin o Vesturbæjarlaug, costano circa 1.700 ISK a testa (stima) e hanno vasche calde e hot pot. Se la Blue Lagoon resta irrinunciabile, prenota la fascia delle 7–9 del mattino, la più economica.

**Con tutte e tre le misure** risparmi circa {eur(risp_tot)} a persona e scendi intorno a **{eur(pp - risp_tot)} a persona**.{" Per rientrare del tutto nei 1.500 € resta da limare il volo: prenota MXP–KEF appena esce l'orario estivo 2027 (le tariffe minime sono intorno ai 65 € a tratta) oppure sposta il viaggio di una settimana, fuori dal periodo pasquale." if pp - risp_tot > BUDGET_PP else ""}
"""
    (DIR / "riepilogo.md").write_text(testo, encoding="utf-8")
    return pp, risp_tot


def verifica_itinerario(righe):
    """Controlla che km, durate e prezzi degli alloggi in itinerario.md coincidano con i dati."""
    path = DIR / "itinerario.md"
    if not path.exists():
        return ["itinerario.md mancante"]
    testo = path.read_text(encoding="utf-8")
    errori = []
    blocchi = re.split(r"^## Giorno (\d+)", testo, flags=re.M)
    trovati = {int(blocchi[i]): blocchi[i + 1] for i in range(1, len(blocchi), 2)}
    for g in GIORNI:
        b = trovati.get(g)
        if b is None:
            errori.append(f"Giorno {g} assente in itinerario.md")
            continue
        m = re.search(r"\*\*Guida:\*\* ([\d.]+) km · (\d+) h (\d+) min", b)
        if not m:
            errori.append(f"Giorno {g}: riga 'Guida' non trovata")
        else:
            km = int(m.group(1).replace(".", ""))
            minuti = int(m.group(2)) * 60 + int(m.group(3))
            if km != km_giorno(g):
                errori.append(f"Giorno {g}: km itinerario {km} ≠ spostamenti {km_giorno(g)}")
            if minuti != min_giorno(g):
                errori.append(f"Giorno {g}: durata itinerario {minuti} ≠ spostamenti {min_giorno(g)}")
            if minuti > 240:
                errori.append(f"Giorno {g}: {minuti} min di guida, oltre le 4 ore")
        allog = [r for r in righe if r["giorno"] == g and r["cat"] == "alloggio"]
        for r in allog:
            prezzo = f"{r['isk']:,}".replace(",", ".") + " ISK/notte"
            if prezzo not in b:
                errori.append(f"Giorno {g}: prezzo alloggio '{prezzo}' non presente in itinerario.md")
    return errori


def main():
    righe = costruisci_righe()
    tot_cat, tot_isk, tot_eur = scrivi_costi(righe)
    tot_km, tot_m = scrivi_spostamenti()
    pp, risp = scrivi_riepilogo(righe, tot_cat, tot_isk, tot_eur, tot_km)

    # Controlli incrociati tra i file generati
    errori = verifica_itinerario(righe)
    with open(DIR / "costi.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    dettaglio = [r for r in rows if r["giorno"]]
    somma = sum(int(r["costo_isk"]) for r in dettaglio)
    gen = next(r for r in rows if r["descrizione"] == "TOTALE GENERALE")
    if somma != int(gen["costo_isk"]):
        errori.append(f"costi.csv: somma righe {somma} ≠ totale generale {gen['costo_isk']}")
    with open(DIR / "spostamenti.csv", encoding="utf-8") as f:
        sp = [r for r in csv.DictReader(f) if r["giorno"]]
    if sum(int(r["km"]) for r in sp) != tot_km:
        errori.append("spostamenti.csv: somma km incoerente")
    tassa = next(r for r in dettaglio if r["categoria"] == "tassa chilometrica")
    if str(tot_km) not in tassa["descrizione"]:
        errori.append("tassa chilometrica calcolata su km diversi da spostamenti.csv")
    if f"{pp:,.0f}".replace(",", ".") not in (DIR / "riepilogo.md").read_text(encoding="utf-8"):
        errori.append("riepilogo.md: totale a persona non coerente")

    print(f"Km totali: {tot_km} ({fmt_durata(tot_m)} di guida)")
    for c, (i, e) in tot_cat.items():
        print(f"  {c:20s} {i:>9,} ISK  {e:>9.2f} €  ({e / 2:.2f} €/persona)")
    print(f"TOTALE: {tot_isk:,} ISK = {tot_eur:.2f} € (2 pers.) = {pp:.2f} €/persona; risparmio possibile {risp:.2f} €/persona")
    if errori:
        print("\nERRORI:")
        for e in errori:
            print(" -", e)
        sys.exit(1)
    print("Controlli incrociati: OK")


if __name__ == "__main__":
    main()
