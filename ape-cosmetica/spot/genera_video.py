"""Genera lo spot verticale (1080x1920, Reel/Storie) per Erboristeria Ape Cosmetica.

Uso:  python3 genera_video.py <file_uscita.mp4>
Richiede: Python 3 con Pillow, ffmpeg.
Per una nuova campagna: cambiare FOTO, la lista P (foto, marca, nome, contenuto,
prezzi presi dai cartellini, bollino) e la data in FINE_PROMO.
Viene salvata anche la copertina <file_uscita>_copertina.jpg.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FOTO = os.path.join(BASE, "foto", "2026-black-friday") + os.sep
FONT = os.path.join(BASE, "font") + os.sep
LOGO_PATH = os.path.join(BASE, "logo.png")
FINE_PROMO = "sabato 28 novembre"

PF = FONT + "playfair-display-latin-%d-normal.woff"
DS = FONT + "dancing-script-latin-700-normal.woff"
INTER_PESI = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}

def pf(w, s): return ImageFont.truetype(PF % w, s)
def ds(s): return ImageFont.truetype(DS, s)
def it(w, s): return ImageFont.truetype(FONT + "inter-latin-%d-normal.woff" % INTER_PESI[w], s)

CREAM = (247, 241, 230)
KRAFT_DOT = (214, 196, 168)
GREEN = (38, 70, 52)
GREEN2 = (62, 104, 74)
RED = (196, 38, 38)
GREY = (120, 112, 100)
GOLD = (200, 160, 80)

OUT = sys.argv[1] if len(sys.argv) > 1 else "spot.mp4"

# ---------- prodotti (prezzi dai cartellini in negozio) ----------
P = [
    dict(img="mirto-calendula.jpg", y0=0, side=2380, brand="ERBE DI SARDEGNA",
         name="Mirto & Calendula", sub="crema mirto · sapone calendula · gommose",
         old="31,00", new="21,50", badge="-30%"),
    dict(img="karite-erbolario.jpg", y0=250, brand="L'ERBOLARIO",
         name="Karité", sub="bagnocrema · crema mani nutriente",
         old="24,90", new="17,40", badge="-30%"),
    dict(img="lamande.jpg", y0=20, brand="L'AMANDE",
         name="Mandorle Dolci", sub="crema mani · sapone mentuccia · ialù labbra",
         old="26,50", new="18,50", badge="-30%"),
    dict(img="latte-asina.jpg", y0=60, brand="DELICATO D'ASINA",
         name="Latte d'Asina", sub="struccante solido · doccia scrub · sacchetto sisal",
         old="26,40", new="21,10", badge="-20%"),
    dict(img="corbezzolo.jpg", y0=300, brand="ERBE DI SARDEGNA",
         name="Corbezzolo", sub="bagnodoccia · crema corpo e mani",
         old="29,00", new="23,20", badge="-20%"),
    dict(img="vaniglia-bianca.jpg", y0=0, brand="NATURE'S",
         name="Vaniglia Bianca", sub="eau de toilette · crema corpo",
         old="52,00", new="36,50", badge=None),
]

def dots_bg(color=CREAM, dot=KRAFT_DOT, step=64, r=6, alpha=None):
    im = Image.new("RGB", (W, H), color)
    d = ImageDraw.Draw(im)
    for j, y in enumerate(range(-step, H + step, step)):
        off = step // 2 if j % 2 else 0
        for x in range(-step, W + step, step):
            cx = x + off
            d.ellipse((cx - r, y - r, cx + r, y + r), fill=dot)
    return im

def ctext(d, y, text, font, fill, x=W // 2, anchor="ma"):
    d.text((x, y), text, font=font, fill=fill, anchor=anchor)

def rounded_mask(size, rad):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), rad, fill=255)
    return m

def shadow(size, rad, blur=28, opacity=110):
    pad = blur * 3
    s = Image.new("RGBA", (size[0] + 2 * pad, size[1] + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((pad, pad + 14, pad + size[0], pad + size[1] + 14), rad, fill=(40, 30, 20, opacity))
    return s.filter(ImageFilter.GaussianBlur(blur)), pad

def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def ease_back(t):
    t = max(0, min(1, t)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

# ---------- layer statici ----------
BG = dots_bg()
PH = 820            # lato foto
PX, PY = (W - PH) // 2, 345
RAD = 36
SH, SHPAD = shadow((PH, PH), RAD)
MASK = rounded_mask((PH, PH), RAD)

def header_layer():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    ctext(d, 112, "Erboristeria", ds(64), GREEN)
    ctext(d, 192, "APE COSMETICA  ·  OLBIA", it("SemiBold", 30), GREEN2)
    # nastro black friday
    d.rounded_rectangle((W // 2 - 190, 248, W // 2 + 190, 304), 28, fill=(20, 20, 20))
    ctext(d, 276, "BLACK FRIDAY", it("Bold", 32), (255, 255, 255), anchor="mm")
    return L
HEADER = header_layer()

def price_layer(p):
    L = Image.new("RGBA", (W, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    ctext(d, 10, p["brand"], it("SemiBold", 30), GREEN2)
    ctext(d, 50, p["name"], pf(700, 84), GREEN)
    ctext(d, 158, p["sub"], it("Regular", 30), GREY)
    # prezzi
    fo, fn = pf(500, 54), pf(900, 128)
    old = "€ " + p["old"]; new = "€ " + p["new"]
    wo = d.textlength(old, font=fo); wn = d.textlength(new, font=fn)
    gap = 44; tot = wo + gap + wn; x0 = (W - tot) / 2
    yb = 320  # baseline comune
    d.text((x0, yb), old, font=fo, fill=GREY, anchor="ls")
    d.line((x0 - 6, yb - 20, x0 + wo + 6, yb - 20), fill=RED, width=5)
    d.text((x0 + wo + gap, yb), new, font=fn, fill=GREEN, anchor="ls")
    ctext(d, 352, "solo fino a " + FINE_PROMO, it("Medium", 30), RED)
    return L

def badge_img(txt):
    s = 230
    B = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(B)
    d.ellipse((6, 6, s - 6, s - 6), fill=RED)
    d.ellipse((18, 18, s - 18, s - 18), outline=(255, 255, 255), width=3)
    d.text((s // 2, s // 2 - 4), txt, font=pf(900, 74), fill=(255, 255, 255), anchor="mm")
    d.text((s // 2, s // 2 + 52), "BLACK FRIDAY", font=it("Bold", 17), fill=(255, 235, 235), anchor="mm")
    return B

def prep_photo(p):
    im = ImageOps.exif_transpose(Image.open(FOTO + p["img"])).convert("RGB")
    side = p.get("side", min(im.size)); x0 = (im.size[0] - side) // 2; y0 = min(p["y0"], im.size[1] - side)
    im = im.crop((x0, y0, x0 + side, y0 + side))
    big = int(PH * 1.12)
    return im.resize((big, big), Image.LANCZOS)

SLIDES = []
for p in P:
    SLIDES.append(dict(photo=prep_photo(p), price=price_layer(p),
                       badge=badge_img(p["badge"]) if p["badge"] else None))

def render_slide(i, t, dur):
    s = SLIDES[i]
    fr = BG.copy().convert("RGBA")
    fr.alpha_composite(SH, (PX - SHPAD, PY - SHPAD))
    # ken burns: zoom lento + leggero pan alternato
    k = t / dur
    z = 1.12 - 0.10 * k
    src = s["photo"]; S = src.size[0]
    cs = int(S * (1.0 / z))
    dx = int((S - cs) * (0.5 + (0.25 if i % 2 else -0.25) * (k - 0.5)))
    dy = int((S - cs) * 0.5)
    ph = src.crop((dx, dy, dx + cs, dy + cs)).resize((PH, PH), Image.BILINEAR)
    fr.paste(ph, (PX, PY), MASK)
    # cornice bianca sottile
    ImageDraw.Draw(fr).rounded_rectangle((PX, PY, PX + PH, PY + PH), RAD, outline=(255, 255, 255), width=8)
    fr.alpha_composite(HEADER)
    # pannello prezzi che sale
    fo = max(0.0, min(1.0, (dur - XF - t) / 0.25)) if i < len(SLIDES) - 1 else max(0.0, min(1.0, (dur - t) / 0.3))
    e = ease((t - 0.35) / 0.5) * fo
    if e > 0:
        lay = s["price"]
        if e < 1:
            a = lay.getchannel("A").point(lambda v: int(v * e))
            lay = lay.copy(); lay.putalpha(a)
        fr.alpha_composite(lay, (0, int(PY + PH + 42 + (1 - ease((t - 0.35) / 0.5)) * 60)))
    # badge che "salta"
    if s["badge"] is not None:
        e2 = ease_back((t - 0.55) / 0.45) * fo
        if (t - 0.55) > 0 and e2 > 0.02:
            sz = max(1, int(230 * e2))
            b = s["badge"].resize((sz, sz), Image.BICUBIC).rotate(-12, expand=True, resample=Image.BICUBIC)
            cx, cy = PX + PH - 40, PY + 40
            fr.alpha_composite(b, (cx - b.size[0] // 2, cy - b.size[1] // 2))
    return fr.convert("RGB")

# ---------- scena Black Friday L'Erbolario ----------
_sc = ImageOps.exif_transpose(Image.open(os.path.join(BASE, "foto", "2026-11-scaffale-erbolario", "scaffale.jpg"))).convert("RGB")
ERB = _sc.crop((0, 0, _sc.size[0], _sc.size[0])).resize((int(PH * 1.12), int(PH * 1.12)), Image.LANCZOS)
ERB_BADGE = badge_img("-50%")
def erb_text():
    L = Image.new("RGBA", (W, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 10, "BLACK FRIDAY L'ERBOLARIO", it("Bold", 32), GREEN2)
    ctext(d, 52, "fino al -50%", pf(900, 120), GREEN)
    ctext(d, 196, "Vieni in negozio a scoprire le linee in sconto:", it("Medium", 34), GREY)
    ctext(d, 244, "Ginepro Nero · Iris Bianco · Frangipani", pf(700, 46), GREEN)
    ctext(d, 304, "e tante altre", it("Medium", 32), GREY)
    ctext(d, 352, "dal 21 al 28 novembre · fino a esaurimento scorte", it("Medium", 30), RED)
    return L
ERB_TXT = erb_text()
def render_erbolario(t, dur):
    fr = BG.copy().convert("RGBA")
    fr.alpha_composite(SH, (PX - SHPAD, PY - SHPAD))
    k = t / dur; z = 1.12 - 0.10 * k; S = ERB.size[0]; cs = int(S / z)
    ph = ERB.crop(((S - cs) // 2, 0, (S - cs) // 2 + cs, cs)).resize((PH, PH), Image.BILINEAR)
    fr.paste(ph, (PX, PY), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((PX, PY, PX + PH, PY + PH), RAD, outline=(255, 255, 255), width=8)
    fr.alpha_composite(HEADER)
    fo = max(0.0, min(1.0, (dur - XF - t) / 0.25)); e = ease((t - 0.35) / 0.5) * fo
    if e > 0:
        lay = ERB_TXT.copy(); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * e)))
        fr.alpha_composite(lay, (0, int(PY + PH + 42 + (1 - ease((t - 0.35) / 0.5)) * 60)))
    e2 = ease_back((t - 0.55) / 0.45) * fo
    if t > 0.55 and e2 > 0.02:
        sz = max(1, int(230 * e2)); b = ERB_BADGE.resize((sz, sz), Image.BICUBIC).rotate(-12, expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(b, (PX + PH - 40 - b.size[0] // 2, PY + 40 - b.size[1] // 2))
    return fr.convert("RGB")

def render_nonetutto(t, dur):
    fr = INTRO_BG.copy().convert("RGBA")
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = [ease((t - 0.15 - k * 0.3) / 0.5) for k in range(4)]
    def A(c, x): return c + (int(255 * x),)
    ctext(d, 520 + (1 - a[0]) * 30, "E non è tutto…", ds(130), A((214, 236, 196), a[0]))
    ctext(d, 760 + (1 - a[1]) * 30, "tanti altri prodotti", pf(900, 96), A((255, 255, 255), a[1]))
    ctext(d, 880 + (1 - a[1]) * 30, "in sconto", pf(900, 96), A((255, 210, 120), a[1]))
    ctext(d, 1040 + (1 - a[2]) * 30, "cosmesi naturale, tisane e benessere", it("Medium", 40), A(CREAM, a[2]))
    y = 1130 + (1 - a[2]) * 30   # riquadro Vaniglia Bianca
    d.rounded_rectangle((200, y, W - 200, y + 110), 55, fill=A((255, 255, 255), a[2]))
    ctext(d, y + 55, "Vaniglia Bianca  -20%", pf(800, 60), A(GREEN, a[2]), anchor="mm")
    ctext(d, 1330 + (1 - a[3]) * 30, "e le nostre confezioni regalo", pf(700, 62), A((255, 255, 255), a[3]))
    ctext(d, 1415 + (1 - a[3]) * 30, "fino al -30%", pf(900, 96), A((255, 210, 120), a[3]))
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- intro ----------
INTRO_BG = dots_bg(GREEN, (52, 88, 64), 64, 6)
def render_intro(t, dur):
    fr = INTRO_BG.copy().convert("RGBA")
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a1 = a2 = a3 = a4 = 1.0   # scritte visibili dal primo fotogramma (copertina automatica)
    def A(c, a): return c + (int(255 * a),)
    ctext(d, 150, "Erboristeria", ds(96), A((214, 236, 196), a1))
    ctext(d, 270, "APE COSMETICA  ·  OLBIA", it("Bold", 44), A(CREAM, a1))
    ctext(d, 470, "BLACK", pf(900, 210), A((255, 255, 255), a2))
    ctext(d, 680, "FRIDAY", pf(900, 210), A((255, 255, 255), a2))
    ctext(d, 930, "dal 21 al 28 novembre", ds(110), A((214, 236, 196), a3))
    for k, (riga, col) in enumerate([("L'Erbolario fino al -50%", (255, 210, 120)),
                                     ("tanti altri prodotti in sconto", (255, 255, 255)),
                                     ("confezioni regalo fino al -30%", (255, 210, 120))]):
        ctext(d, 1150 + k * 105, riga, pf(800, 66), A(col, a4))
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- finale ----------
_logo = Image.open(LOGO_PATH).convert("RGB").resize((380, 380), Image.LANCZOS)
LOGO = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
ImageDraw.Draw(LOGO).rounded_rectangle((0, 0, 419, 419), 48, fill=(255, 255, 255, 255))
LOGO.paste(_logo, (20, 20))
def render_outro(t, dur):
    fr = INTRO_BG.copy().convert("RGBA")
    a = [ease((t - k * 0.22) / 0.5) for k in range(6)]
    if a[0] > 0:
        lg = LOGO.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a[0])))
        fr.alpha_composite(lg, ((W - 420) // 2, int(150 + (1 - a[0]) * 30)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    def A(c, x): return c + (int(255 * x),)
    ctext(d, 600 + (1 - a[1]) * 30, "Vieni a trovarci!", ds(116), A((214, 236, 196), a[1]))
    y = 790 + (1 - a[2]) * 30
    ctext(d, y, "Queste sono solo alcune idee:", it("Medium", 38), A(CREAM, a[2]))
    ctext(d, y + 52, "in negozio ne trovi tante altre!", pf(700, 56), A((255, 255, 255), a[2]))
    ctext(d, y + 138, "vieni a scoprirle nei nostri negozi", it("SemiBold", 34), A((255, 210, 120), a[2]))
    y = 1010 + (1 - a[3]) * 30
    d.rounded_rectangle((140, y, W - 140, y + 140), 26, fill=A((255, 210, 120), a[3]))
    ctext(d, y + 24, "BLACK FRIDAY", it("Bold", 32), A(GREEN, a[3]))
    ctext(d, y + 66, "fino a " + FINE_PROMO, pf(700, 48), A(GREEN, a[3]))
    y = 1210 + (1 - a[4]) * 30
    ctext(d, y, "Viale Aldo Moro 215", pf(600, 56), A((255, 255, 255), a[4]))
    ctext(d, y + 72, "Corso Umberto 153", pf(600, 56), A((255, 255, 255), a[4]))
    ctext(d, y + 152, "Olbia  ·  lun–sab  9.00–13.15  ·  15.30–19.30", it("Medium", 32), A(CREAM, a[4]))
    ctext(d, 1500 + (1 - a[5]) * 30, "apecosmetica.com", it("SemiBold", 38), A((214, 236, 196), a[5]))
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- timeline ----------
segs = [("intro", None, 3.0), ("erbolario", None, 3.2), ("nonetutto", None, 2.8)] + [("slide", i, 2.5) for i in range(len(P))] + [("outro", None, 5.0)]
XF = 0.35
starts = []; t0 = 0
for s in segs:
    starts.append(t0); t0 += s[2] - XF
TOTAL = t0 + XF

def seg_frame(k, t):
    kind, i, dur = segs[k]
    if kind == "intro": return render_intro(t, dur)
    if kind == "outro": return render_outro(t, dur)
    if kind == "erbolario": return render_erbolario(t, dur)
    if kind == "nonetutto": return render_nonetutto(t, dur)
    return render_slide(i, t, dur)

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
N = int(TOTAL * FPS)
cover_t = 1.5
for n in range(N):
    t = n / FPS
    act = [k for k in range(len(segs)) if starts[k] <= t < starts[k] + segs[k][2]]
    if len(act) == 1:
        img = seg_frame(act[0], t - starts[act[0]])
    else:
        a, b = act[0], act[-1]
        ia = seg_frame(a, t - starts[a]); ib = seg_frame(b, t - starts[b])
        img = Image.blend(ia, ib, ease((t - starts[b]) / XF))
    if abs(t - cover_t) < 0.5 / FPS:
        img.save(OUT.replace(".mp4", "_copertina.jpg"), quality=92)
    ff.stdin.write(img.tobytes())
ff.stdin.close(); ff.wait()
print("durata", round(TOTAL, 2), "s, frame", N)
