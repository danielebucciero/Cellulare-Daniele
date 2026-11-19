"""Reel verticale (1080x1920) "Scegli la fragranza, noi prepariamo la confezione".

Simula un cliente davanti allo scaffale: l'inquadratura si avvicina alla fila della fragranza, la fila si illumina
e un "tocco" la sceglie; poi compare la confezione regalo che prepariamo con quella fragranza.
Uso:  python3 reel_scelta.py <file_uscita.mp4>    (Pillow + ffmpeg). Salva anche <uscita>_copertina.jpg.
Musica: python3 musica_natale.py --monta <video> <video_con_musica>.
Per riusarlo: cambiare FOTO_DIR, SCAFFALE e SCELTE (zona dello scaffale in pixel, foto della confezione, testi).
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE, "font") + os.sep
FOTO_DIR = os.path.join(BASE, "foto", "2026-11-scaffale-erbolario") + os.sep
LOGO_PATH = os.path.join(BASE, "logo.png")
OUT = sys.argv[1] if len(sys.argv) > 1 else "reel_scelta.mp4"

def pf(w, s): return ImageFont.truetype(FONT + "playfair-display-latin-%d-normal.woff" % w, s)
def ds(s): return ImageFont.truetype(FONT + "dancing-script-latin-700-normal.woff", s)
def it(w, s): return ImageFont.truetype(FONT + "inter-latin-%d-normal.woff" % {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}[w], s)

CREAM, DOT = (247, 241, 230), (214, 196, 168)
GREEN, GREEN2, GDOT = (38, 70, 52), (62, 104, 74), (52, 88, 64)
GREY, LIGHT, YELLOW = (120, 112, 100), (214, 236, 196), (255, 210, 120)

# ---------- contenuti ----------
SCAFFALE = "scaffale.jpg"
SCELTE = [  # vista (x, y, larghezza; altezza = 4/3), fila da illuminare, colore, foto confezione + ritaglio, testi, prezzo
    dict(vista=(20, 0, 800), fila=(55, 20, 740, 285), colore=(170, 140, 220),
         domanda="Ti piace l'Iris?", foto="confezione-iris.jpg", rit=(150, 380, 1350, 1980),
         nome="Confezione Iris", contenuto="bagnoschiuma e crema per il corpo", prezzo="42,90 €"),
    dict(vista=(80, 250, 1150), fila=(120, 395, 1190, 665), colore=(255, 214, 90),
         domanda="Preferisci il Giglio?", foto="confezione-giglio.jpg", rit=(60, 283, 1360, 2016),
         nome="Confezione Giglio", contenuto="bagnocrema, crema per il corpo e profumo 15 ml", prezzo="59,00 €"),
    dict(vista=(737, 680, 760), fila=(975, 1060, 1260, 1310), colore=(255, 170, 150),
         domanda="O i Fiori d'Arancio?", foto="confezione-fiori-arancio.jpg", rit=(130, 350, 1350, 1977),
         nome="Confezione Fiori d'Arancio", contenuto="bagnoschiuma e crema fluida per il corpo", prezzo="41,50 €"),
]
TIMELINE = [("intro", None, 2.9)]
for i in range(len(SCELTE)):
    TIMELINE += [("scaffale", i, 2.7), ("confezione", i, 2.7)]
TIMELINE += [("outro", None, 4.4)]
XF = 0.35

# ---------- utilità ----------
def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_io(t): t = clamp(t); return 3 * t * t - 2 * t * t * t
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
def fade(layer, a):
    if a >= 1: return layer
    l = layer.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * clamp(a)))); return l
def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
def shadow(w, h, r, blur=28):
    p = blur * 3; s = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((p, p + 14, p + w, p + h + 14), r, fill=(40, 30, 20, 110))
    return s.filter(ImageFilter.GaussianBlur(blur)), p
def foto(n): return ImageOps.exif_transpose(Image.open(FOTO_DIR + n)).convert("RGB")

BG_C, BG_G = dots(CREAM, DOT), dots(GREEN, GDOT)
def header(dark):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 112, "Erboristeria", ds(64), LIGHT if dark else GREEN)
    ctext(d, 192, "APE COSMETICA  ·  OLBIA", it("SemiBold", 30), CREAM if dark else GREEN2)
    return L
HEAD_C, HEAD_G = header(False), header(True)

CW, CH = 780, 1040; CX, CY = (W - CW) // 2, 280; RAD = 34
SH, SHP = shadow(CW, CH, RAD); MASK = rmask(CW, CH, RAD)
SCAF = foto(SCAFFALE)
SW, SHH = SCAF.size
FULL = (0, 0, SW)                      # vista intera (3:4)
CONF = [ImageEnhance.Brightness(foto(s["foto"]).crop(s["rit"])).enhance(1.08).resize((CW, CH), Image.LANCZOS) for s in SCELTE]

def card(fr, img):
    fr.alpha_composite(SH, (CX - SHP, CY - SHP)); fr.paste(img, (CX, CY), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((CX, CY, CX + CW, CY + CH), RAD, outline=(255, 255, 255), width=8)

def lerp(a, b, t): return tuple(x + (y - x) * t for x, y in zip(a, b))

def vista_img(v):
    x, y, w = v; h = w * 4 / 3
    return SCAF.crop((int(x), int(y), int(x + w), int(y + h))).resize((CW, CH), Image.BILINEAR), (x, y, w)

def testo(lab, tit, sub, prezzo=None):
    L = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 0, lab, it("Bold", 28), GREEN2)
    ctext(d, 44, tit, pf(700, 80 if len(tit) < 20 else 66), GREEN)
    if sub: ctext(d, 150, sub, it("Regular", 32), GREY)
    if prezzo:
        f = pf(800, 56); w = d.textlength(prezzo, font=f) + 90
        d.rounded_rectangle((W / 2 - w / 2, 206, W / 2 + w / 2, 292), 43, fill=YELLOW)
        ctext(d, 249, prezzo, f, GREEN, anchor="mm")
    return L
T_SCAF = [testo("SCEGLI LA FRAGRANZA", s["domanda"], "dal nostro scaffale L'Erbolario") for s in SCELTE]
T_CONF = [testo("E NOI LA CONFEZIONIAMO", s["nome"], s["contenuto"], s["prezzo"]) for s in SCELTE]
TXT_Y = CY + CH + 40

def render_scaffale(i, t, dur):
    s = SCELTE[i]
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C)
    v0 = FULL if i == 0 else SCELTE[i - 1]["vista"]
    k = ease_io((t - 0.15) / 1.1)
    img, (vx, vy, vw) = vista_img(lerp(v0, s["vista"], k))
    sc = CW / vw
    lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = s["fila"]; rx0, ry0, rx1, ry1 = [(x0 - vx) * sc, (y0 - vy) * sc, (x1 - vx) * sc, (y1 - vy) * sc]
    g = ease((t - 1.15) / 0.35)
    if g > 0:   # oscura il resto e illumina la fila scelta
        dim = Image.new("RGBA", (CW, CH), (20, 20, 20, int(120 * g)))
        hole = Image.new("L", (CW, CH), 0); ImageDraw.Draw(hole).rounded_rectangle((rx0, ry0, rx1, ry1), 18, fill=255)
        dim.putalpha(Image.composite(Image.new("L", (CW, CH), 0), dim.getchannel("A"), hole))
        img = img.convert("RGBA"); img.alpha_composite(dim)
        for wd, al in ((18, 0.25), (10, 0.5), (5, 1.0)):
            d.rounded_rectangle((rx0 - wd, ry0 - wd, rx1 + wd, ry1 + wd), 18 + wd, outline=A(s["colore"], al * g), width=5)
    # il "tocco" del cliente: un cerchio che arriva e fa un'onda
    cx, cy = (rx0 + rx1) / 2, (ry0 + ry1) / 2
    p = ease_io((t - 0.7) / 0.5)
    if 0 < p and t < dur - XF:
        sx, sy = CW * 0.5, CH * 0.95
        fx, fy = sx + (cx - sx) * p, sy + (cy - sy) * p
        r = 34
        d.ellipse((fx - r, fy - r, fx + r, fy + r), fill=(255, 255, 255, 150), outline=(255, 255, 255, 235), width=5)
        w = (t - 1.25) / 0.6
        if 0 < w < 1:
            rr = r + 110 * w
            d.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), outline=(255, 255, 255, int(220 * (1 - w))), width=6)
    img = img.convert("RGBA"); img.alpha_composite(lay)
    card(fr, img.convert("RGB"))
    e = ease((t - 0.3) / 0.5) * clamp((dur - XF - t) / 0.25)
    fr.alpha_composite(fade(T_SCAF[i], e), (0, int(TXT_Y + (1 - ease((t - 0.3) / 0.5)) * 40)))
    return fr.convert("RGB")

def render_conf(i, t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C)
    z = 1.08 - 0.08 * clamp(t / dur); im = CONF[i]
    cw, ch = CW / z, CH / z
    card(fr, im.crop((int((CW - cw) / 2), int((CH - ch) / 2), int((CW + cw) / 2), int((CH + ch) / 2))).resize((CW, CH), Image.BILINEAR))
    e = ease((t - 0.3) / 0.5) * clamp((dur - XF - t) / 0.25)
    fr.alpha_composite(fade(T_CONF[i], e), (0, int(TXT_Y - 6 + (1 - ease((t - 0.3) / 0.5)) * 40)))
    return fr.convert("RGB")

def render_intro(t, dur):
    fr = BG_G.copy(); fr.alpha_composite(HEAD_G)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = [ease((t - 0.2 - k * 0.35) / 0.55) for k in range(4)]
    ctext(d, 520 + (1 - a[0]) * 30, "Scegli tu", ds(130), A(LIGHT, a[0]))
    ctext(d, 700 + (1 - a[1]) * 30, "la fragranza,", pf(900, 120), A((255, 255, 255), a[1]))
    ctext(d, 860 + (1 - a[2]) * 30, "noi prepariamo", pf(700, 84), A((255, 255, 255), a[2]))
    ctext(d, 970 + (1 - a[2]) * 30, "la confezione regalo", pf(700, 84), A(YELLOW, a[2]))
    ctext(d, 1160 + (1 - a[3]) * 30, "con i prodotti L'Erbolario", it("Medium", 42), A(CREAM, a[3]))
    fr.alpha_composite(L)
    return fr.convert("RGB")

_lg = Image.open(LOGO_PATH).convert("RGB").resize((380, 380), Image.LANCZOS)
LOGO = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
ImageDraw.Draw(LOGO).rounded_rectangle((0, 0, 419, 419), 48, fill=(255, 255, 255, 255)); LOGO.paste(_lg, (20, 20))
def render_outro(t, dur):
    fr = BG_G.copy()
    a = [ease((t - k * 0.22) / 0.5) for k in range(5)]
    if a[0] > 0: fr.alpha_composite(fade(LOGO, a[0]), ((W - 420) // 2, int(170 + (1 - a[0]) * 30)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 630 + (1 - a[1]) * 30, "Ti aspettiamo!", ds(120), A(LIGHT, a[1]))
    ctext(d, 820 + (1 - a[2]) * 30, "Scegli la tua fragranza:", it("Medium", 40), A(CREAM, a[2]))
    ctext(d, 874 + (1 - a[2]) * 30, "la confezione la prepariamo noi", pf(700, 58), A((255, 255, 255), a[2]))
    y = 1050 + (1 - a[3]) * 30
    ctext(d, y, "Viale Aldo Moro 215", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 72, "Corso Umberto 153", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 152, "Olbia  ·  lun–sab  9.00–13.15  ·  15.30–19.30", it("Medium", 32), A(CREAM, a[3]))
    ctext(d, 1440 + (1 - a[4]) * 30, "apecosmetica.com", it("SemiBold", 38), A(LIGHT, a[4]))
    fr.alpha_composite(L)
    return fr.convert("RGB")

def frame(k, t):
    kind, i, dur = TIMELINE[k]
    if kind == "scaffale": return render_scaffale(i, t, dur)
    if kind == "confezione": return render_conf(i, t, dur)
    return (render_intro if kind == "intro" else render_outro)(t, dur)

starts, t0 = [], 0.0
for s in TIMELINE: starts.append(t0); t0 += s[2] - XF
TOTAL = t0 + XF
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
cover_t = starts[1] + 1.9
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
