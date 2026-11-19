"""Reel di Natale (1080x1920, Reel/Storie) per Erboristeria Ape Cosmetica.

Uso:  python3 genera_video_natale.py <file_uscita.mp4>
Richiede: Python 3 con Pillow, ffmpeg.
Una sola foto della confezione, mostrata in più inquadrature (lista SCENE: ritaglio quadrato
x, y, lato in pixel della foto originale + testi). Nessun prezzo: il cartellino in foto era
quello del Black Friday e i ritagli lo lasciano fuori.
Viene salvata anche la copertina <file_uscita>_copertina.jpg.
"""
import os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FOTO = os.path.join(BASE, "foto", "2026-natale", "latte-asina.jpg")
FONT = os.path.join(BASE, "font") + os.sep
LOGO_PATH = os.path.join(BASE, "logo.png")
OUT = sys.argv[1] if len(sys.argv) > 1 else "natale.mp4"

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
RED = (176, 32, 38)
GREY = (120, 112, 100)
GOLD = (255, 210, 120)
MINT = (214, 236, 196)

# ---------- scene: ritaglio (x, y, lato) dalla foto originale 2132x2576 ----------
SCENE = [
    dict(crop=(66, 40, 2000), brand="DELICATO D'ASINA", name="Latte d'Asina",
         sub="la confezione regalo", tag="confezionata a mano in negozio"),
    dict(crop=(250, 1000, 850), brand="STRUCCANTE SOLIDO VISO", name="al latte d'asina",
         sub="con burro di karité", tag="delicato · rivitalizzante"),
    dict(crop=(1100, 1020, 800), brand="DOCCIA SCHIUMA SOLIDO SCRUB", name="al latte d'asina",
         sub="nutriente · naturale", tag="niente flacone, solo il panetto"),
    dict(crop=(680, 260, 850), brand="SACCHETTO 100% SISAL", name="per i solidi",
         sub="per sapone e detergenti solidi", tag="per usarli fino all'ultimo pezzetto"),
]

def dots_bg(color=CREAM, dot=KRAFT_DOT, step=64, r=6):
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

# ---------- neve ----------
random.seed(7)
FIOCCHI = [(random.uniform(0, W), random.uniform(0, H), random.uniform(3, 9), random.uniform(40, 110),
            random.uniform(0, 6.28)) for _ in range(90)]
def snow(fr, t, color=(255, 255, 255), alpha=170):
    import math
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for x, y, r, v, ph in FIOCCHI:
        yy = (y + v * t) % (H + 40) - 20
        xx = x + 18 * math.sin(t * 1.3 + ph)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=color + (alpha,))
    fr.alpha_composite(L)

def stella(d, cx, cy, r, fill):
    import math
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)

# ---------- layer statici ----------
BG = dots_bg()
PH = 820
PX, PY = (W - PH) // 2, 345
RAD = 36
SH, SHPAD = shadow((PH, PH), RAD)
MASK = rounded_mask((PH, PH), RAD)

def header_layer():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    ctext(d, 112, "Erboristeria", ds(64), GREEN)
    ctext(d, 192, "APE COSMETICA  ·  OLBIA", it("SemiBold", 30), GREEN2)
    d.rounded_rectangle((W // 2 - 210, 248, W // 2 + 210, 304), 28, fill=RED)
    ctext(d, 276, "IDEE REGALO DI NATALE", it("Bold", 28), (255, 255, 255), anchor="mm")
    stella(d, W // 2 - 250, 276, 20, (200, 160, 80))
    stella(d, W // 2 + 250, 276, 20, (200, 160, 80))
    return L
HEADER = header_layer()

def text_layer(s):
    L = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    ctext(d, 10, s["brand"], it("SemiBold", 30), GREEN2)
    ctext(d, 52, s["name"], pf(700, 92), GREEN)
    ctext(d, 172, s["sub"], it("Regular", 34), GREY)
    ctext(d, 250, s["tag"], ds(66), RED)
    return L

SRC = ImageOps.exif_transpose(Image.open(FOTO)).convert("RGB")
def prep_photo(s):
    x, y, side = s["crop"]
    big = int(PH * 1.12)
    return SRC.crop((x, y, x + side, y + side)).resize((big, big), Image.LANCZOS)

SLIDES = [dict(photo=prep_photo(s), text=text_layer(s)) for s in SCENE]
XF = 0.35

def render_slide(i, t, dur):
    s = SLIDES[i]
    fr = BG.copy().convert("RGBA")
    snow(fr, t + i * 3, color=(214, 196, 168), alpha=120)
    fr.alpha_composite(SH, (PX - SHPAD, PY - SHPAD))
    k = t / dur
    z = 1.12 - 0.10 * k
    src = s["photo"]; S = src.size[0]
    cs = int(S * (1.0 / z))
    dx = int((S - cs) * (0.5 + (0.25 if i % 2 else -0.25) * (k - 0.5)))
    dy = int((S - cs) * 0.5)
    ph = src.crop((dx, dy, dx + cs, dy + cs)).resize((PH, PH), Image.BILINEAR)
    fr.paste(ph, (PX, PY), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((PX, PY, PX + PH, PY + PH), RAD, outline=(255, 255, 255), width=8)
    fr.alpha_composite(HEADER)
    fo = max(0.0, min(1.0, (dur - XF - t) / 0.25))
    e = ease((t - 0.35) / 0.5) * fo
    if e > 0:
        lay = s["text"]
        if e < 1:
            lay = lay.copy(); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * e)))
        fr.alpha_composite(lay, (0, int(PY + PH + 46 + (1 - ease((t - 0.35) / 0.5)) * 60)))
    return fr.convert("RGB")

# ---------- intro ----------
INTRO_BG = dots_bg(GREEN, (52, 88, 64), 64, 6)
def render_intro(t, dur):
    fr = INTRO_BG.copy().convert("RGBA")
    snow(fr, t)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a1 = ease(t / 0.6); a2 = ease((t - 0.45) / 0.6); a3 = ease((t - 0.95) / 0.6); a4 = ease((t - 1.5) / 0.5)
    def A(c, a): return c + (int(255 * a),)
    stella(d, W // 2, 420 + (1 - a1) * 30, 46, A(GOLD, a1))
    ctext(d, 500 + (1 - a1) * 40, "Erboristeria Ape Cosmetica", it("SemiBold", 36), A(CREAM, a1))
    ctext(d, 580 + (1 - a2) * 40, "Il Natale", pf(900, 190), A((255, 255, 255), a2))
    ctext(d, 820 + (1 - a3) * 30, "si incarta a mano", ds(118), A(MINT, a3))
    ctext(d, 1080 + (1 - a4) * 30, "Un regalo che coccola", it("Medium", 50), A(CREAM, a4))
    ctext(d, 1146 + (1 - a4) * 30, "anche la pelle", pf(800, 86), A(GOLD, a4))
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- finale ----------
_logo = Image.open(LOGO_PATH).convert("RGB").resize((380, 380), Image.LANCZOS)
LOGO = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
ImageDraw.Draw(LOGO).rounded_rectangle((0, 0, 419, 419), 48, fill=(255, 255, 255, 255))
LOGO.paste(_logo, (20, 20))
def render_outro(t, dur):
    fr = INTRO_BG.copy().convert("RGBA")
    snow(fr, t + 5)
    a = [ease((t - k * 0.22) / 0.5) for k in range(6)]
    if a[0] > 0:
        lg = LOGO.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a[0])))
        fr.alpha_composite(lg, ((W - 420) // 2, int(150 + (1 - a[0]) * 30)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    def A(c, x): return c + (int(255 * x),)
    ctext(d, 600 + (1 - a[1]) * 30, "Vieni a trovarci!", ds(116), A(MINT, a[1]))
    y = 790 + (1 - a[2]) * 30
    ctext(d, y, "Questa è solo una delle nostre idee:", it("Medium", 38), A(CREAM, a[2]))
    ctext(d, y + 52, "in negozio ne trovi tante altre!", pf(700, 56), A((255, 255, 255), a[2]))
    ctext(d, y + 138, "vieni a scoprirle nei nostri negozi", it("SemiBold", 34), A(GOLD, a[2]))
    y = 1010 + (1 - a[3]) * 30
    d.rounded_rectangle((180, y, W - 180, y + 120), 26, fill=A(RED, a[3]))
    ctext(d, y + 60, "Buone Feste", ds(80), A((255, 255, 255), a[3]), anchor="mm")
    y = 1200 + (1 - a[4]) * 30
    ctext(d, y, "Viale Aldo Moro 215", pf(600, 56), A((255, 255, 255), a[4]))
    ctext(d, y + 72, "Corso Umberto 153", pf(600, 56), A((255, 255, 255), a[4]))
    ctext(d, y + 152, "Olbia  ·  lun–sab  9.00–13.15  ·  15.30–19.30", it("Medium", 32), A(CREAM, a[4]))
    ctext(d, 1490 + (1 - a[5]) * 30, "apecosmetica.com", it("SemiBold", 38), A(MINT, a[5]))
    fr.alpha_composite(L)
    return fr.convert("RGB")

# ---------- timeline ----------
segs = [("intro", None, 3.0)] + [("slide", i, 3.0) for i in range(len(SCENE))] + [("outro", None, 5.0)]
starts = []; t0 = 0
for s in segs:
    starts.append(t0); t0 += s[2] - XF
TOTAL = t0 + XF

def seg_frame(k, t):
    kind, i, dur = segs[k]
    if kind == "intro": return render_intro(t, dur)
    if kind == "outro": return render_outro(t, dur)
    return render_slide(i, t, dur)

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
N = int(TOTAL * FPS)
cover_t = starts[1] + 1.6
for n in range(N):
    t = n / FPS
    act = [k for k in range(len(segs)) if starts[k] <= t < starts[k] + segs[k][2]]
    if len(act) == 1:
        img = seg_frame(act[0], t - starts[act[0]])
    else:
        a, b = act[0], act[-1]
        img = Image.blend(seg_frame(a, t - starts[a]), seg_frame(b, t - starts[b]), ease((t - starts[b]) / XF))
    if abs(t - cover_t) < 0.5 / FPS:
        img.save(OUT.replace(".mp4", "_copertina.jpg"), quality=92)
    ff.stdin.write(img.tobytes())
ff.stdin.close(); ff.wait()
print("durata", round(TOTAL, 2), "s, frame", N)
