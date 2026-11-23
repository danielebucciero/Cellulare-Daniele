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
OUT = sys.argv[1] if len(sys.argv) > 1 else "reel_prodotto.mp4"

# ---------- contenuti ----------
FOTO = os.path.join(BASE, "foto", "2026-11-iris-bianco", "confezione-iris-bianco.jpg")
MARCA, NOME, SOTTO = "L'ERBOLARIO", "Iris Bianco", "confezione regalo · BagnoCrema + Sapone"
INTERA = (100, 520, 1440, 2016)            # confezione intera
DETTAGLI = [((320, 690, 760, 1400), "BagnoCrema", "con estratto e acqua distillata di Iris Bianco · 300 ml"),
            ((720, 620, 1160, 1480), "Sapone Profumato", "con estratto di Iris Bianco · 125 g")]
PREZZO_VECCHIO, PREZZO_NUOVO, BOLLINO = "24,50", "17,00", "-30%"
FINE = "fino a sabato 28 novembre"

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
        ctext(d, 44, "BagnoCrema + Sapone", pf(700, 70), GREEN)
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

TIMELINE = [("intro", None, 3.0)] + [("det", i, 2.6) for i in range(len(DETTAGLI))] + [("prezzo", None, 3.4), ("outro", None, 4.4)]
XF = 0.35
def frame(k, t):
    kind, i, dur = TIMELINE[k]
    if kind == "det": return render_det(i, t, dur)
    return {"intro": render_intro, "prezzo": render_prezzo, "outro": render_outro}[kind](t, dur)
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
