"""Reel verticale (1080x1920) "Regali che scaldano": confezioni regalo di tisane, tè e miele.

Racconto: apertura (scritte visibili dal primo fotogramma) -> preparazione passo per passo con foto vere
(scatola con paglia e carta, tazza, tisana, scatola chiusa con il fiocco) -> un'altra confezione con prezzo ->
"e tante altre idee" (scaffali) -> "scegli per tempo, noi prepariamo" -> finale con logo.
Uso:  python3 reel_regali_tisane.py <uscita.mp4>   (Pillow + ffmpeg). Salva anche <uscita>_copertina.jpg.
Musica: python3 musica_natale.py --monta <video> <video_con_musica>.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE, "font") + os.sep
FOTO_DIR = os.path.join(BASE, "foto", "2026-11-regali-tisane") + os.sep
LOGO_PATH = os.path.join(BASE, "logo.png")
OUT = sys.argv[1] if len(sys.argv) > 1 else "reel_regali_tisane.mp4"

def pf(w, s): return ImageFont.truetype(FONT + "playfair-display-latin-%d-normal.woff" % w, s)
def ds(s): return ImageFont.truetype(FONT + "dancing-script-latin-700-normal.woff", s)
def it(w, s): return ImageFont.truetype(FONT + "inter-latin-%d-normal.woff" % {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}[w], s)

CREAM, DOT = (247, 241, 230), (214, 196, 168)
GREEN, GREEN2, GDOT = (38, 70, 52), (62, 104, 74), (52, 88, 64)
GREY, LIGHT, YELLOW, RED = (120, 112, 100), (214, 236, 196), (255, 210, 120), (150, 30, 40)

# ---------- contenuti ----------
SFONDO_INTRO = "scaffale-neavita.jpg"
PASSI = [  # foto (una o due, la seconda entra in dissolvenza), numero, etichetta, titolo, sottotitolo
    (["scatola-paglia.jpg", "scatola-carta.jpg"], "1", "LA BASE", "Scatola e paglietta", "prima la paglia, poi la carta colorata"),
    (["scatola-tazza.jpg"], "2", "LA TAZZA", "Tisaniera Neavita", "con coperchio e filtro"),
    (["scatola-tazza-tisana.jpg"], "3", "LA TISANA", "Tisana Bio Armonia e Relax", "confezionata da noi in negozio · 100 g"),
    (["scatola-chiusa.jpg"], "4", "IL TOCCO FINALE", "Si chiude con il fiocco", "pronta da mettere sotto l'albero"),
]
ALTRA = ("confezione-22.jpg", "UN'ALTRA IDEA", "Tazza, miele e Tea & Bears",
         "Miele di Sardegna Eucalipto 250 g · tè Neavita", "23,50 €")
GALLERIA = [
    ("scaffale-neavita.jpg", "Tè e tisane Neavita", "latte natalizie, tazze, cofanetti e bottiglie"),
    ("scaffale-teiere.jpg", "Teiere e tisaniere", "da abbinare alla tisana che preferisci"),
    ("yogi-leone.jpg", "Yogi Tea e cioccolato Leone", "calendario dell'Avvento e confezioni già pronte"),
    ("infusi-frutta.jpg", "Infusi di frutta e miele", "infusi confezionati da noi · 100 g a 6,00 €"),
]
TIMELINE = [("intro", None, 3.2)] + [("passo", i, 2.7) for i in range(len(PASSI))] + [("altra", None, 2.9)]
TIMELINE += [("galleria", i, 2.8) for i in range(len(GALLERIA))] + [("pertempo", None, 3.4), ("outro", None, 4.6)]
XF = 0.35

# ---------- utilità ----------
def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_io(t): t = clamp(t); return 3 * t * t - 2 * t * t * t
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
def header(dark, grande=False):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    if grande:
        ctext(d, 80, "Erboristeria", ds(116), LIGHT if dark else GREEN)
        ctext(d, 232, "APE COSMETICA  ·  OLBIA", it("Bold", 52), CREAM if dark else GREEN2)
    else:
        ctext(d, 98, "Erboristeria", ds(76), LIGHT if dark else GREEN)
        ctext(d, 192, "APE COSMETICA  ·  OLBIA", it("Bold", 36), CREAM if dark else GREEN2)
    return L
HEAD_C, HEAD_G, HEAD_COP = header(False), header(True), header(True, True)

CW, CH = 780, 1040; CX, CY = (W - CW) // 2, 280; RAD = 34
SH, SHP = shadow(CW, CH, RAD); MASK = rmask(CW, CH, RAD)
TXT_Y = CY + CH + 40

def fit(im, w=CW, h=CH):
    """Ritaglio centrale nelle proporzioni della card (più grande del necessario, per lo zoom)."""
    r = w / h; iw, ih = im.size
    if iw / ih > r: nw = int(ih * r); im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else: nh = int(iw / r); im = im.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    return im.resize((int(w * 1.1), int(h * 1.1)), Image.LANCZOS)
def zoom(im, k, z0=1.0, z1=1.1):
    z = z1 - (z1 - z0) * k; iw, ih = im.size; cw, ch = CW * 1.1 / z, CH * 1.1 / z
    return im.crop((int((iw - cw) / 2), int((ih - ch) / 2), int((iw + cw) / 2), int((ih + ch) / 2))).resize((CW, CH), Image.BILINEAR)
def card(fr, img):
    fr.alpha_composite(SH, (CX - SHP, CY - SHP)); fr.paste(img, (CX, CY), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((CX, CY, CX + CW, CY + CH), RAD, outline=(255, 255, 255), width=8)

def testo(lab, tit, sub, prezzo=None, num=None):
    L = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = it("Bold", 28)
    if num:
        lw = d.textlength(lab, font=f); x0 = (W - (52 + 14 + lw)) / 2
        d.ellipse((x0, -4, x0 + 52, 48), fill=GREEN)
        d.text((x0 + 26, 22), num, font=it("Bold", 30), fill=(255, 255, 255), anchor="mm")
        d.text((x0 + 66, 22), lab, font=f, fill=GREEN2, anchor="lm")
    else:
        ctext(d, 0, lab, f, GREEN2)
    size = 80
    while d.textlength(tit, font=pf(700, size)) > 900 and size > 48: size -= 2
    ctext(d, 52 + (80 - size) // 2, tit, pf(700, size), GREEN)
    ctext(d, 158, sub, it("Regular", 32), GREY)
    if prezzo:
        fp = pf(800, 56); w = d.textlength(prezzo, font=fp) + 90
        d.rounded_rectangle((W / 2 - w / 2, 212, W / 2 + w / 2, 298), 43, fill=YELLOW)
        ctext(d, 255, prezzo, fp, GREEN, anchor="mm")
    return L

TAGLI = {"scatola-chiusa.jpg": (0, 0, 1512, 1850)}   # tolto il bordo in basso (si vedevano le scarpe)
P_IMG = [[fit(foto(n).crop(TAGLI[n]) if n in TAGLI else foto(n)) for n in p[0]] for p in PASSI]
P_TXT = [testo(p[2], p[3], p[4], num=p[1]) for p in PASSI]
ALTRA_IMG = fit(ImageEnhance.Brightness(foto(ALTRA[0])).enhance(1.05)); ALTRA_TXT = testo(*ALTRA[1:])
GAL_IMG = [foto(g[0]) for g in GALLERIA]; GAL_TXT = [testo("E TANTE ALTRE IDEE", g[1], g[2]) for g in GALLERIA]
_bg = foto(SFONDO_INTRO); _s = max(W / _bg.size[0], H / _bg.size[1])
_bg = _bg.resize((int(_bg.size[0] * _s) + 1, int(_bg.size[1] * _s) + 1), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
INTRO_BG = _bg.crop(((_bg.size[0] - W) // 2, (_bg.size[1] - H) // 2, (_bg.size[0] - W) // 2 + W, (_bg.size[1] - H) // 2 + H))

def scene_text(fr, layer, t, dur, dy=0):
    e = ease((t - 0.3) / 0.5) * clamp((dur - XF - t) / 0.25)
    if e > 0: fr.alpha_composite(fade(layer, e), (0, int(TXT_Y + dy + (1 - ease((t - 0.3) / 0.5)) * 40)))

def render_passo(i, t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C)
    ims = P_IMG[i]; k = clamp(t / dur)
    img = zoom(ims[0], k)
    if len(ims) == 2: img = Image.blend(img, zoom(ims[1], k), ease_io((t - 1.2) / 0.6))
    card(fr, img); scene_text(fr, P_TXT[i], t, dur)
    return fr.convert("RGB")

def render_altra(t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C)
    card(fr, zoom(ALTRA_IMG, clamp(t / dur))); scene_text(fr, ALTRA_TXT, t, dur, -6)
    return fr.convert("RGB")

def render_galleria(i, t, dur):
    fr = BG_C.copy(); fr.alpha_composite(HEAD_C)
    im = GAL_IMG[i]; iw, ih = im.size; k = ease_io(clamp(t / dur))
    if iw / ih > CW / CH:      # foto larga: scorre da sinistra a destra
        ww = int(ih * CW / CH); x = int((iw - ww) * k); crop = im.crop((x, 0, x + ww, ih))
    else:                      # foto alta: scorre dall'alto in basso
        hh = int(iw * CH / CW); y = int((ih - hh) * k); crop = im.crop((0, y, iw, y + hh))
    card(fr, crop.resize((CW, CH), Image.BILINEAR)); scene_text(fr, GAL_TXT[i], t, dur)
    return fr.convert("RGB")

def render_intro(t, dur, copertina=False):
    z = 1.0 + 0.06 * clamp(t / dur); cw, ch = W / z, H / z
    fr = INTRO_BG.crop((int((W - cw) / 2), int((H - ch) / 2), int((W + cw) / 2), int((H + ch) / 2))).resize((W, H), Image.BILINEAR).convert("RGBA")
    fr.alpha_composite(Image.new("RGBA", (W, H), GREEN + (180,)))
    fr.alpha_composite(HEAD_COP if copertina else HEAD_G)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)   # scritte visibili dal primo fotogramma
    ctext(d, 440, "Natale si avvicina…", ds(110), LIGHT + (255,))
    ctext(d, 630, "Regali che", pf(900, 110), (255, 255, 255, 255))
    ctext(d, 760, "scaldano", pf(900, 120), YELLOW + (255,))
    ctext(d, 960, "tisane, tè, miele e tazze", pf(700, 64), (255, 255, 255, 255))
    ctext(d, 1050, "in confezioni regalo preparate da noi", it("Medium", 42), CREAM + (255,))
    fr.alpha_composite(L)
    return fr.convert("RGB")

def render_pertempo(t, dur):
    fr = BG_G.copy(); fr.alpha_composite(HEAD_G)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = [ease((t - 0.2 - k * 0.35) / 0.55) for k in range(4)]
    ctext(d, 470 + (1 - a[0]) * 30, "Non aspettare", ds(120), A(LIGHT, a[0]))
    ctext(d, 610 + (1 - a[0]) * 30, "l'ultimo momento!", ds(120), A(LIGHT, a[0]))
    ctext(d, 840 + (1 - a[1]) * 30, "Vieni a scegliere i tuoi regali", pf(700, 64), A((255, 255, 255), a[1]))
    ctext(d, 930 + (1 - a[1]) * 30, "per tempo", pf(900, 96), A(YELLOW, a[1]))
    y = 1120 + (1 - a[2]) * 30
    d.rounded_rectangle((150, y, W - 150, y + 120), 60, fill=A(YELLOW, a[2]))
    ctext(d, y + 60, "e noi li prepariamo per te", pf(700, 52), A(GREEN, a[2]), anchor="mm")
    ctext(d, 1300 + (1 - a[3]) * 30, "tu scegli, al resto pensiamo noi", it("Medium", 40), A(CREAM, a[3]))
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
    ctext(d, 820 + (1 - a[2]) * 30, "Scegli i tuoi regali per tempo:", it("Medium", 40), A(CREAM, a[2]))
    ctext(d, 874 + (1 - a[2]) * 30, "al resto pensiamo noi", pf(700, 62), A((255, 255, 255), a[2]))
    y = 1050 + (1 - a[3]) * 30
    ctext(d, y, "Viale Aldo Moro 215", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 72, "Corso Umberto 153", pf(600, 56), A((255, 255, 255), a[3]))
    ctext(d, y + 152, "Olbia  ·  lun–sab  9.00–13.15  ·  15.30–19.30", it("Medium", 32), A(CREAM, a[3]))
    ctext(d, 1440 + (1 - a[4]) * 30, "apecosmetica.com", it("SemiBold", 38), A(LIGHT, a[4]))
    fr.alpha_composite(L)
    return fr.convert("RGB")

def frame(k, t):
    kind, i, dur = TIMELINE[k]
    if kind == "passo": return render_passo(i, t, dur)
    if kind == "galleria": return render_galleria(i, t, dur)
    return {"intro": render_intro, "altra": render_altra, "pertempo": render_pertempo, "outro": render_outro}[kind](t, dur)

starts, t0 = [], 0.0
for s in TIMELINE: starts.append(t0); t0 += s[2] - XF
TOTAL = t0 + XF
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
render_intro(1.5, TIMELINE[0][2], copertina=True).save(OUT.replace(".mp4", "_copertina.jpg"), quality=92)
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
