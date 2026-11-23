"""Reel verticale (1080x1920) per promuovere UN prodotto/confezione nel Black Friday, da una sola foto.

Scene: apertura con la foto (scritte visibili dal primo fotogramma) -> dettagli (zoom su ritagli della foto)
-> prezzo con bollino -> finale con logo e indirizzi.
Uso:  python3 reel_prodotto.py <uscita.mp4>   (Pillow + ffmpeg). Salva anche <uscita>_copertina.jpg.
Musica: python3 musica_natale.py --monta <video> <video_con_musica>.
Per un altro prodotto: cambiare FOTO, NOME, DETTAGLI (ritagli x0,y0,x1,y1 + testi) e i prezzi.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE, "font") + os.sep

# ---------- contenuti ----------
FOTO = os.path.join(BASE, "foto", "2026-11-iris-bianco", "confezione-iris-bianco.jpg")
MARCA, NOME, SOTTO = "L'ERBOLARIO", "Iris Bianco", "confezione regalo · BagnoCrema + Sapone"
INTERA = (100, 520, 1440, 2016)            # confezione intera
DETTAGLI = [((320, 690, 760, 1400), "BagnoCrema", "con estratto e acqua distillata di Iris Bianco · 300 ml"),
            ((720, 620, 1160, 1480), "Sapone Profumato", "con estratto di Iris Bianco · 125 g")]
PREZZO_VECCHIO, PREZZO_NUOVO, BOLLINO = "24,50", "17,00", "-30%"
FINE = "fino a sabato 28 novembre"
# scatola chiusa (tagliato il bordo in basso dove si vedevano le scarpe)
CHIUSA = (os.path.join(BASE, "foto", "2026-11-iris-bianco", "scatola-chiusa.jpg"), (0, 300, 1512, 1680))
TITOLO_PREZZO = "BagnoCrema + Sapone"
CON_CHIUSA = True

# ---------- altre confezioni (uso: python3 reel_prodotto.py <nome> <uscita.mp4>) ----------
_F = lambda n: os.path.join(BASE, "foto", "2026-11-black-friday-confezioni", n)
ALTRE = {
    "karite": dict(FOTO=_F("karite.jpg"), MARCA="L'ERBOLARIO", NOME="Karité",
        SOTTO="confezione regalo · BagnoCrema + BurroPuro", INTERA=(0, 200, 1512, 1800),
        DETTAGLI=[((290, 630, 720, 1360), "BagnoCrema Nutriente", "Karité · 300 ml"),
                  ((730, 280, 1270, 1410), "BurroPuro di Karité", "per corpo, viso e capelli · 120 ml")],
        PREZZO_VECCHIO="44,90", PREZZO_NUOVO="31,40", BOLLINO="-30%", TITOLO_PREZZO="BagnoCrema + BurroPuro"),
    "bacche": dict(FOTO=_F("bacche-fiori-legni.jpg"), MARCA="L'ERBOLARIO", NOME="Bacche Fiori Legni",
        SOTTO="confezione regalo · Profumo + Crema corpo", INTERA=(213, 178, 2135, 2230),
        DETTAGLI=[((468, 759, 1168, 1506), "Profumo", "Bacche Fiori Legni · 100 ml"),
                  ((1233, 486, 1643, 1589), "Crema Fluida per il Corpo", "con estratti di Biancospino, Fiori d'Arancio e Legno di Cedro")],
        PREZZO_VECCHIO="72,90", PREZZO_NUOVO="51,00", BOLLINO="-30%", TITOLO_PREZZO="Profumo + Crema corpo"),
    "aloe": dict(FOTO=_F("aloe-attiva.jpg"), MARCA="NATUR UNIQUE", NOME="Aloe Attiva",
        SOTTO="confezione regalo · crema fluida + crema gel viso", INTERA=(110, 0, 2116, 2362),
        DETTAGLI=[((160, 738, 849, 2386), "Crema Fluida", "Aloe Attiva · viso, mani e corpo"),
                  ((1033, 1156, 1599, 2017), "Face Cream Sphere", "Aloe Attiva · crema gel viso")],
        PREZZO_VECCHIO="71,80", PREZZO_NUOVO="57,50", BOLLINO="-20%", TITOLO_PREZZO="Crema fluida + crema gel viso"),
}
if len(sys.argv) > 2 and sys.argv[1] in ALTRE:
    globals().update(ALTRE[sys.argv[1]]); CON_CHIUSA = False; OUT = sys.argv[2]
else:
    OUT = sys.argv[1] if len(sys.argv) > 1 else "reel_prodotto.mp4"

def pf(w, s): return ImageFont.truetype(FONT + "playfair-display-latin-%d-normal.woff" % w, s)
def ds(s): return ImageFont.truetype(FONT + "dancing-script-latin-700-normal.woff", s)
def it(w, s): return ImageFont.truetype(FONT + "inter-latin-%d-normal.woff" % {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}[w], s)
CREAM, DOT = (247, 241, 230), (214, 196, 168)
GREEN, GREEN2, GDOT = (38, 70, 52), (62, 104, 74), (52, 88, 64)
GREY, LIGHT, YELLOW, RED = (120, 112, 100), (214, 236, 196), (255, 210, 120), (196, 38, 38)

def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def dots(color, dot, step=64, r=6):
    im = Image.new("RGB", (W, H), color); d = ImageDraw.Draw(im)
    for j, y in enumerate(range(-step, H + step, step)):
        off = step // 2 if j % 2 else 0
        for x in range(-step, W + step, step):
            d.ellipse((x + off - r, y - r, x + off + r, y + r), fill=dot)
    return im.convert("RGBA")
def ctext(d, y, text, font, fill, anchor="ma"): d.text((W // 2, y), text, font=font, fill=fill, anchor=anchor)
def A(c, a): return c + (int(255 * clamp(a)),)
def fade(l, a):
    if a >= 1: return l
    l = l.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * clamp(a)))); return l
def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
def shadow(w, h, r, blur=28):
    p = blur * 3; s = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((p, p + 14, p + w, p + h + 14), r, fill=(40, 30, 20, 110))
    return s.filter(ImageFilter.GaussianBlur(blur)), p

SRC = ImageEnhance.Brightness(ImageOps.exif_transpose(Image.open(FOTO)).convert("RGB")).enhance(1.06)
BG_C, BG_G = dots(CREAM, DOT), dots(GREEN, GDOT)
CW, CH = 780, 1040; CX, CY = (W - CW) // 2, 300; RAD = 34
SH, SHP = shadow(CW, CH, RAD); MASK = rmask(CW, CH, RAD)

def fit(box):
    """Ritaglio in proporzione 3:4 attorno al riquadro dato (centrato)."""
    x0, y0, x1, y1 = box; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = x1 - x0, y1 - y0
    if w / h > 3 / 4: h = w * 4 / 3
    else: w = h * 3 / 4
    x0 = max(0, min(SRC.size[0] - w, cx - w / 2)); y0 = max(0, min(SRC.size[1] - h, cy - h / 2))
    return (x0, y0, w, h)
def zoom(box, k, z0=1.0, z1=1.08):
    x0, y0, w, h = fit(box); z = z0 + (z1 - z0) * k; cw, ch = w / z, h / z
    x0 += (w - cw) / 2; y0 += (h - ch) / 2
    return SRC.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((CW, CH), Image.BILINEAR)
def card(fr, img, y=CY):
    fr.alpha_composite(SH, (CX - SHP, y - SHP)); fr.paste(img, (CX, y), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((CX, y, CX + CW, y + CH), RAD, outline=(255, 255, 255), width=8)

def header(dark):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 98, "Erboristeria", ds(76), LIGHT if dark else GREEN)
    ctext(d, 192, "APE COSMETICA  ·  OLBIA", it("Bold", 36), CREAM if dark else GREEN2)
    return L
HEAD_C, HEAD_G = header(False), header(True)

def badge(txt, s=250):
    B = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(B)
    d.ellipse((6, 6, s - 6, s - 6), fill=RED); d.ellipse((18, 18, s - 18, s - 18), outline=(255, 255, 255), width=3)
    d.text((s // 2, s // 2 - 6), txt, font=pf(900, 80), fill=(255, 255, 255), anchor="mm")
    d.text((s // 2, s // 2 + 56), "BLACK FRIDAY", font=it("Bold", 18), fill=(255, 235, 235), anchor="mm")
    return B
BADGE = badge(BOLLINO)
def put_badge(fr, t, t0, y=CY):
    e = ease_back((t - t0) / 0.45)
    if t > t0 and e > 0.02:
        sz = max(1, int(250 * e)); b = BADGE.resize((sz, sz), Image.BICUBIC).rotate(-12, expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(b, (CX + CW - 30 - b.size[0] // 2, y + 30 - b.size[1] // 2))

def prezzi(d, y):
    fo, fn = pf(500, 60), pf(900, 140)
    old, new = "€ " + PREZZO_VECCHIO, "€ " + PREZZO_NUOVO
    wo, wn = d.textlength(old, font=fo), d.textlength(new, font=fn); x0 = (W - (wo + 44 + wn)) / 2
    d.text((x0, y), old, font=fo, fill=GREY, anchor="ls"); d.line((x0 - 6, y - 22, x0 + wo + 6, y - 22), fill=RED, width=6)
    d.text((x0 + wo + 44, y), new, font=fn, fill=GREEN, anchor="ls")

# ---------- scene ----------
def render_intro(t, dur):           # scritte già visibili al primo fotogramma (copertina automatica)
    fr = BG_G.copy(); fr.alpha_composite(HEAD_G)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((W // 2 - 230, 262, W // 2 + 230, 330), 34, fill=(20, 20, 20, 255))
    ctext(d, 296, "BLACK FRIDAY", it("Bold", 38), (255, 255, 255, 255), anchor="mm")
    fr.alpha_composite(L)
    img = zoom(INTERA, clamp(t / dur)); y = 380
    w2, h2 = 700, 933; x2 = (W - w2) // 2
    s2, p2 = shadow(w2, h2, RAD); fr.alpha_composite(s2, (x2 - p2, y - p2))
    fr.paste(img.resize((w2, h2), Image.BILINEAR), (x2, y), rmask(w2, h2, RAD))
    ImageDraw.Draw(fr).rounded_rectangle((x2, y, x2 + w2, y + h2), RAD, outline=(255, 255, 255), width=8)
    b = BADGE.rotate(-12, expand=True, resample=Image.BICUBIC); fr.alpha_composite(b, (x2 + w2 - 40 - b.size[0] // 2, y + 20 - b.size[1] // 2))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 1350, MARCA, it("Bold", 34), CREAM + (255,))
    ctext(d, 1395, NOME, pf(900, 118), (255, 255, 255, 255))
    ctext(d, 1540, SOTTO, it("Medium", 36), LIGHT + (255,))
    d.rounded_rectangle((W // 2 - 330, 1620, W // 2 + 330, 1740), 60, fill=YELLOW + (255,))
    ctext(d, 1680, "a soli € " + PREZZO_NUOVO, pf(800, 64), GREEN + (255,), anchor="mm")
    fr.alpha_composite(L)
    return fr.convert("RGB")

def det_text(tit, sub):
    L = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 0, "NELLA CONFEZIONE", it("Bold", 30), GREEN2)
    ctext(d, 46, tit, pf(700, 84), GREEN)
    ctext(d, 160, sub, it("Regular", 32), GREY)
    return L
DET_TXT = [det_text(t, s) for _, t, s in DETTAGLI]
def render_det(i, t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C); card(fr, zoom(DETTAGLI[i][0], clamp(t / dur)))
    e = ease((t - 0.3) / 0.5) * clamp((dur - XF - t) / 0.25)
    if e > 0: fr.alpha_composite(fade(DET_TXT[i], e), (0, int(CY + CH + 46 + (1 - ease((t - 0.3) / 0.5)) * 40)))
    return fr.convert("RGB")

def render_prezzo(t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C); card(fr, zoom(INTERA, clamp(t / dur), 1.06, 1.0))
    put_badge(fr, t, 0.4)
    e = ease((t - 0.3) / 0.5) * clamp((dur - XF - t) / 0.25)
    if e > 0:
        L = Image.new("RGBA", (W, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        ctext(d, 0, MARCA + " · " + NOME.upper(), it("Bold", 30), GREEN2)
        ctext(d, 44, TITOLO_PREZZO, pf(700, 70 if len(TITOLO_PREZZO) < 24 else 58), GREEN)
        prezzi(d, 280); ctext(d, 304, "solo " + FINE, it("Medium", 32), RED)
        fr.alpha_composite(fade(L, e), (0, int(CY + CH + 40 + (1 - ease((t - 0.3) / 0.5)) * 40)))
    return fr.convert("RGB")

_lg = Image.open(os.path.join(BASE, "logo.png")).convert("RGB").resize((380, 380), Image.LANCZOS)
LOGO = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
ImageDraw.Draw(LOGO).rounded_rectangle((0, 0, 419, 419), 48, fill=(255, 255, 255, 255)); LOGO.paste(_lg, (20, 20))
def render_outro(t, dur):
    fr = BG_G.copy(); a = [ease((t - k * 0.22) / 0.5) for k in range(5)]
    if a[0] > 0: fr.alpha_composite(fade(LOGO, a[0]), ((W - 420) // 2, int(170 + (1 - a[0]) * 30)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 630 + (1 - a[1]) * 30, "Ti aspettiamo!", ds(120), A(LIGHT, a[1]))
    y = 810 + (1 - a[2]) * 30
    d.rounded_rectangle((140, y, W - 140, y + 140), 26, fill=A(YELLOW, a[2]))
    ctext(d, y + 24, "BLACK FRIDAY", it("Bold", 32), A(GREEN, a[2]))
    ctext(d, y + 66, "dal 21 al 28 novembre", pf(700, 48), A(GREEN, a[2]))
    y = 1010 + (1 - a[3]) * 30
    ctext(d, y, "Viale Aldo Moro 215", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 72, "Corso Umberto 153", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 152, "Olbia  ·  lun–sab  9.00–13.15  ·  15.30–19.30", it("Medium", 32), A(CREAM, a[3]))
    ctext(d, 1300 + (1 - a[4]) * 30, "fino a esaurimento scorte", it("Medium", 34), A(LIGHT, a[4]))
    fr.alpha_composite(L); return fr.convert("RGB")

# scatola intera e centrata: la foto della scatola (fiocco compreso) sta tutta nella card;
# sopra e sotto c'è la stessa foto ingrandita e sfocata, così la card resta piena
_full = ImageEnhance.Brightness(ImageOps.exif_transpose(Image.open(CHIUSA[0])).convert("RGB")).enhance(1.05)
_box = _full.crop((0, 320, 1430, 1660))                        # scatola con il fiocco, senza scarpe
# centra la SCATOLA ROSSA (centro a x 816, y 990 nella foto originale) nel mezzo della card
_cw0, _ch0 = int(CW * 1.08), int(CH * 1.08)
_s = (_cw0 / 2) / 816
_bw, _bh = int(_box.size[0] * _s), int(_box.size[1] * _s)
_fg = _box.resize((_bw, _bh), Image.LANCZOS)
_bg = _full.crop((300, 500, 1212, 1716)).resize((int(CW * 1.08), int(CH * 1.08)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
_bg = ImageEnhance.Brightness(_bg).enhance(0.8)
_bg.paste(_fg, (int(_cw0 / 2 - 816 * _s), int(_ch0 / 2 - (990 - 320) * _s)))
CHIUSA_IMG = _bg
def render_chiusa(t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C)
    z = 1.08 - 0.08 * clamp(t / dur); iw, ih = CHIUSA_IMG.size; cw, ch = CW * 1.08 / z, CH * 1.08 / z
    card(fr, CHIUSA_IMG.crop((int((iw - cw) / 2), int((ih - ch) / 2), int((iw + cw) / 2), int((ih + ch) / 2))).resize((CW, CH), Image.BILINEAR))
    e = ease((t - 0.3) / 0.5) * clamp((dur - XF - t) / 0.25)
    if e > 0:
        L = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        ctext(d, 0, "IL TOCCO FINALE", it("Bold", 30), GREEN2)
        ctext(d, 46, "Pronta da regalare", pf(700, 84), GREEN)
        ctext(d, 160, "nella scatola L'Erbolario, chiusa con il fiocco", it("Regular", 32), GREY)
        fr.alpha_composite(fade(L, e), (0, int(CY + CH + 46 + (1 - ease((t - 0.3) / 0.5)) * 40)))
    return fr.convert("RGB")
# ---------- busta: la scatola scende nella busta, si chiude con l'etichetta del negozio, consegna ----------
_bd = os.path.join(BASE, "foto", "2026-11-iris-bianco")
BUSTA = ImageEnhance.Brightness(ImageOps.exif_transpose(Image.open(os.path.join(_bd, "busta-erbolario.jpg"))).convert("RGB")).enhance(1.05).resize((CW, CH), Image.LANCZOS)
SC = CW / 1512
CUT = int(560 * SC)                       # bordo della busta: sotto questa linea c'è il davanti
BUSTA_FRONT = BUSTA.crop((0, CUT, CW, CH))
_ch2 = ImageOps.exif_transpose(Image.open(CHIUSA[0])).convert("RGB").crop((200, 330, 1400, 1530))
BOX = _ch2.resize((330, 330), Image.LANCZOS).convert("RGBA"); BOX.putalpha(rmask(330, 330, 14))
_et = ImageOps.exif_transpose(Image.open(os.path.join(_bd, "etichetta-negozio.jpg"))).convert("RGB").crop((455, 1120, 1135, 1500))
_et = ImageEnhance.Color(ImageEnhance.Brightness(_et).enhance(1.18)).enhance(0.7)
ETI = _et.resize((360, int(360 * _et.size[1] / _et.size[0])), Image.LANCZOS).convert("RGBA"); ETI.putalpha(rmask(*ETI.size, 10))
def render_busta(t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C)
    exit_k = ease((t - (dur - 0.9)) / 0.6)            # alla fine la busta "parte" verso destra: consegnata
    ox = int(exit_k * 160)
    C = BUSTA.copy().convert("RGBA")
    p = clamp((t - 0.2) / 1.3); y = int(-360 + (CUT + 120 + 360) * (p * p))  # la scatola cade nella busta
    C.alpha_composite(BOX, ((CW - 330) // 2, y))
    C.paste(BUSTA_FRONT, (0, CUT))                    # il davanti della busta copre la scatola
    e = ease((t - 1.7) / 0.35)
    if e > 0:                                         # etichetta del negozio "timbrata" sul bordo
        sc = 1.6 - 0.6 * e; w, h = int(ETI.size[0] * sc), int(ETI.size[1] * sc)
        et = fade(ETI.resize((w, h), Image.BICUBIC), e)
        C.alpha_composite(et, ((CW - w) // 2, CUT - h // 2 + 10))
    fr.alpha_composite(SH, (CX - SHP + ox, CY - SHP)); fr.paste(C.convert("RGB"), (CX + ox, CY), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((CX + ox, CY, CX + CW + ox, CY + CH), RAD, outline=(255, 255, 255), width=8)
    L = Image.new("RGBA", (W, 320), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a1, a2 = ease((t - 0.3) / 0.5), ease((t - 2.1) / 0.5)
    ctext(d, 0, "E POI…", it("Bold", 30), A(GREEN2, a1))
    ctext(d, 46, "nella busta, chiusa con il nostro sigillo", pf(700, 46), A(GREEN, a1))
    ctext(d, 140, "pronta da consegnare 🎁".replace(" 🎁", ""), pf(900, 84), A(RED, a2))
    ctext(d, 250, "a soli € " + PREZZO_NUOVO + " invece di € " + PREZZO_VECCHIO, it("SemiBold", 36), A(GREY, a2))
    fr.alpha_composite(fade(L, clamp((dur - t) / 0.3)), (0, CY + CH + 40))
    return fr.convert("RGB")

TIMELINE = [("intro", None, 3.0)] + [("det", i, 2.6) for i in range(len(DETTAGLI))] + [("prezzo", None, 3.4)] + ([("chiusa", None, 2.6)] if CON_CHIUSA else []) + ([("busta", None, 4.2)] if "--busta" in sys.argv else []) + [("outro", None, 4.4)]
XF = 0.35
def frame(k, t):
    kind, i, dur = TIMELINE[k]
    if kind == "det": return render_det(i, t, dur)
    return {"intro": render_intro, "prezzo": render_prezzo, "chiusa": render_chiusa, "busta": render_busta, "outro": render_outro}[kind](t, dur)
starts, t0 = [], 0.0
for s in TIMELINE: starts.append(t0); t0 += s[2] - XF
TOTAL = t0 + XF
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
render_intro(0.0, TIMELINE[0][2]).save(OUT.replace(".mp4", "_copertina.jpg"), quality=92)
for n in range(int(TOTAL * FPS)):
    t = n / FPS
    act = [k for k in range(len(TIMELINE)) if starts[k] <= t < starts[k] + TIMELINE[k][2]]
    if len(act) == 1: img = frame(act[0], t - starts[act[0]])
    else:
        a, b = act[0], act[-1]
        img = Image.blend(frame(a, t - starts[a]), frame(b, t - starts[b]), ease((t - starts[b]) / XF))
    ff.stdin.write(img.tobytes())
ff.stdin.close(); ff.wait()
print("durata", round(TOTAL, 2), "s")
