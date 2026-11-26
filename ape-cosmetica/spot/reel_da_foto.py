"""Reel verticale (1080x1920) costruito da UNA sola foto del negozio: mostra i dettagli uno alla volta.

Uso:  python3 reel_da_foto.py <file_uscita.mp4>
Richiede: Python 3 con Pillow, ffmpeg. Salva anche <file_uscita>_copertina.jpg.
Per riusarlo con un'altra foto: cambiare FOTO_PATH, la lista SCENE (ritagli quadrati x, y, lato in pixel
della foto + testi) e i testi di apertura, lista e finale.
Stile e regole: vedi ../README.md (niente prenotazioni, niente "pezzo unico", niente claim sulla salute).
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE, "font") + os.sep
FOTO_PATH = os.path.join(BASE, "foto", "2026-11-angolo-tisane", "angolo-tisane.jpg")
LOGO_PATH = os.path.join(BASE, "logo.png")
OUT = sys.argv[1] if len(sys.argv) > 1 else "reel.mp4"

def pf(w, s): return ImageFont.truetype(FONT + "playfair-display-latin-%d-normal.woff" % w, s)
def ds(s): return ImageFont.truetype(FONT + "dancing-script-latin-700-normal.woff", s)
def it(w, s): return ImageFont.truetype(FONT + "inter-latin-%d-normal.woff" % {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}[w], s)

CREAM, DOT = (247, 241, 230), (214, 196, 168)
GREEN, GREEN2, DGREEN_DOT = (38, 70, 52), (62, 104, 74), (52, 88, 64)
GREY, LIGHT, YELLOW = (120, 112, 100), (214, 236, 196), (255, 210, 120)

# ---------- contenuti ----------
INTRO = ("Le serate si allungano,", "la tazza si scalda")
SCENE = [  # (x, y, lato) del ritaglio quadrato nella foto, etichetta, titolo, sottotitolo
    ((430, 820, 760), "IL NOSTRO ANGOLO TISANE", "Infusi di frutta", "confezionati da noi, con il fiocco"),
    ((812, 100, 700), "IN NEGOZIO TROVI ANCHE", "Yogi Tea", "tanti gusti per ogni momento"),
    ((0, 250, 700), "PER I PIÙ GOLOSI", "Cioccolato Leone", "e i calendari dell'Avvento"),
    ((0, 680, 620), "IDEE REGALO", "Cofanetti di tisane", "pronti da mettere sotto l'albero"),
]
GUSTI = ["Frutti di bosco", "Limone e Zenzero", "Ciliegia selvatica", "Melagrana e Arancia",
         "Rosa Canina e Lamponi", "Rosa e Fico", "Mela e Cannella"]
PREZZO = "100 g  ·  6,00 €"
# ordine: intro, scena 0, lista gusti, scene 1..3, finale
TIMELINE = [("intro", None, 3.2), ("foto", 0, 2.8), ("gusti", None, 3.8), ("foto", 1, 2.5),
            ("foto", 2, 2.5), ("foto", 3, 2.5), ("outro", None, 4.6)]
XF = 0.35

# ---------- utilità ----------
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def dots_bg(color, dot, step=64, r=6):
    im = Image.new("RGB", (W, H), color); d = ImageDraw.Draw(im)
    for j, y in enumerate(range(-step, H + step, step)):
        off = step // 2 if j % 2 else 0
        for x in range(-step, W + step, step):
            d.ellipse((x + off - r, y - r, x + off + r, y + r), fill=dot)
    return im
def ctext(d, y, text, font, fill, anchor="ma"): d.text((W // 2, y), text, font=font, fill=fill, anchor=anchor)
def A(c, a): return c + (int(255 * max(0, min(1, a))),)
def fade(layer, a):
    if a >= 1: return layer
    l = layer.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * a))); return l
def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
def shadow(w, h, r, blur=28):
    pad = blur * 3; s = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((pad, pad + 14, pad + w, pad + h + 14), r, fill=(40, 30, 20, 110))
    return s.filter(ImageFilter.GaussianBlur(blur)), pad

FOTO = ImageOps.exif_transpose(Image.open(FOTO_PATH)).convert("RGB")
BG_CREAM = dots_bg(CREAM, DOT).convert("RGBA")
BG_GREEN = dots_bg(GREEN, DGREEN_DOT).convert("RGBA")

def header(dark=False):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 112, "Erboristeria", ds(64), LIGHT if dark else GREEN)
    ctext(d, 192, "APE COSMETICA  ·  OLBIA", it("SemiBold", 30), CREAM if dark else GREEN2)
    return L
HEAD_CREAM, HEAD_GREEN = header(), header(True)

# ---------- scene con foto ----------
CARD = 860; CX, CY = (W - CARD) // 2, 300; RAD = 36
SH, SHP = shadow(CARD, CARD, RAD); MASK = rounded_mask(CARD, CARD, RAD)
def kenburns(box, k, zoom=0.10, card=(CARD, CARD)):
    x, y, s = box; z = 1 + zoom * (1 - k)          # parte stretto e si allarga piano
    cs = s / z; ox = x + (s - cs) / 2; oy = y + (s - cs) / 2
    asp = card[1] / card[0]
    return FOTO.crop((int(ox), int(oy), int(ox + cs), int(oy + cs * asp))).resize(card, Image.BILINEAR)

def testo_scena(lab, tit, sub):
    L = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 0, lab, it("SemiBold", 30), GREEN2)
    ctext(d, 44, tit, pf(700, 92), GREEN)
    ctext(d, 164, sub, it("Regular", 36), GREY)
    return L
TESTI = [testo_scena(*s[1:]) for s in SCENE]

def render_foto(i, t, dur):
    fr = BG_CREAM.copy()
    fr.alpha_composite(SH, (CX - SHP, CY - SHP))
    fr.paste(kenburns(SCENE[i][0], t / dur), (CX, CY), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((CX, CY, CX + CARD, CY + CARD), RAD, outline=(255, 255, 255), width=8)
    fr.alpha_composite(HEAD_CREAM)
    fo = max(0.0, min(1.0, (dur - XF - t) / 0.25))
    e = ease((t - 0.35) / 0.5)
    if e * fo > 0:
        fr.alpha_composite(fade(TESTI[i], e * fo), (0, int(CY + CARD + 60 + (1 - e) * 50)))
    return fr.convert("RGB")

# ---------- apertura: foto intera ----------
IW, IH = 860, 1146
ISH, ISHP = shadow(IW, IH, RAD); IMASK = rounded_mask(IW, IH, RAD)
def render_intro(t, dur):
    fr = BG_GREEN.copy()
    k = t / dur; z = 1.0 + 0.08 * k
    w0, h0 = FOTO.size; cw, ch = w0 / z, h0 / z
    ph = FOTO.crop((int((w0 - cw) / 2), int((h0 - ch) / 2), int((w0 + cw) / 2), int((h0 + ch) / 2))).resize((IW, IH), Image.BILINEAR)
    x, y = (W - IW) // 2, 300
    fr.alpha_composite(ISH, (x - ISHP, y - ISHP)); fr.paste(ph, (x, y), IMASK)
    ImageDraw.Draw(fr).rounded_rectangle((x, y, x + IW, y + IH), RAD, outline=(255, 255, 255), width=8)
    fr.alpha_composite(HEAD_GREEN)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a1, a2 = ease((t - 0.3) / 0.6), ease((t - 0.9) / 0.6)
    ctext(d, 1478 + (1 - a1) * 30, INTRO[0], pf(700, 70), A((255, 255, 255), a1))
    ctext(d, 1560 + (1 - a2) * 30, INTRO[1], ds(96), A(YELLOW, a2))
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- lista gusti ----------
def render_gusti(t, dur):
    fr = BG_GREEN.copy(); fr.alpha_composite(HEAD_GREEN)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    fo = max(0.0, min(1.0, (dur - XF - t) / 0.25))
    a0 = ease((t - 0.3) / 0.5) * fo
    ctext(d, 330 + (1 - a0) * 30, "7 gusti da scegliere", ds(104), A(LIGHT, a0))
    for n, g in enumerate(GUSTI):
        a = ease((t - 0.6 - n * 0.17) / 0.45) * fo
        y = 540 + n * 116 + (1 - a) * 30
        ctext(d, y, g, pf(600, 64), A((255, 255, 255), a))
        if n < len(GUSTI) - 1:
            d.ellipse((W // 2 - 5, y + 92, W // 2 + 5, y + 102), fill=A(YELLOW, a))
    ap = ease((t - 1.9) / 0.5) * fo
    y = 1400 + (1 - ap) * 30
    d.rounded_rectangle((250, y, W - 250, y + 120), 60, fill=A(YELLOW, ap))
    ctext(d, y + 60, PREZZO, pf(800, 60), A(GREEN, ap), anchor="mm")
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- finale ----------
_lg = Image.open(LOGO_PATH).convert("RGB").resize((380, 380), Image.LANCZOS)
LOGO = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
ImageDraw.Draw(LOGO).rounded_rectangle((0, 0, 419, 419), 48, fill=(255, 255, 255, 255)); LOGO.paste(_lg, (20, 20))
def render_outro(t, dur):
    fr = BG_GREEN.copy()
    a = [ease((t - k * 0.22) / 0.5) for k in range(5)]
    if a[0] > 0: fr.alpha_composite(fade(LOGO, a[0]), ((W - 420) // 2, int(170 + (1 - a[0]) * 30)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 630 + (1 - a[1]) * 30, "Ti aspettiamo!", ds(120), A(LIGHT, a[1]))
    ctext(d, 820 + (1 - a[2]) * 30, "Passa in negozio e scegli", it("Medium", 40), A(CREAM, a[2]))
    ctext(d, 874 + (1 - a[2]) * 30, "il tuo profumo preferito", pf(700, 62), A((255, 255, 255), a[2]))
    y = 1050 + (1 - a[3]) * 30
    ctext(d, y, "Viale Aldo Moro 215", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 72, "Corso Umberto 153", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 152, "Olbia  ·  lun–sab  9.00–13.15  ·  15.30–19.30", it("Medium", 32), A(CREAM, a[3]))
    ctext(d, 1440 + (1 - a[4]) * 30, "apecosmetica.com", it("SemiBold", 38), A(LIGHT, a[4]))
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- montaggio ----------
def frame(k, t):
    kind, i, dur = TIMELINE[k]
    return {"intro": lambda: render_intro(t, dur), "gusti": lambda: render_gusti(t, dur),
            "outro": lambda: render_outro(t, dur), "foto": lambda: render_foto(i, t, dur)}[kind]()

starts, t0 = [], 0.0
for s in TIMELINE: starts.append(t0); t0 += s[2] - XF
TOTAL = t0 + XF
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
cover_t = starts[0] + 2.4
for n in range(int(TOTAL * FPS)):
    t = n / FPS
    act = [k for k in range(len(TIMELINE)) if starts[k] <= t < starts[k] + TIMELINE[k][2]]
    if len(act) == 1: img = frame(act[0], t - starts[act[0]])
    else:
        a, b = act[0], act[-1]
        img = Image.blend(frame(a, t - starts[a]), frame(b, t - starts[b]), ease((t - starts[b]) / XF))
    if abs(t - cover_t) < 0.5 / FPS: img.save(OUT.replace(".mp4", "_copertina.jpg"), quality=92)
    ff.stdin.write(img.tobytes())
ff.stdin.close(); ff.wait()
print("durata", round(TOTAL, 2), "s")
