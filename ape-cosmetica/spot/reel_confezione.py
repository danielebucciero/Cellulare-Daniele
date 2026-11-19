"""Reel verticale (1080x1920) "come nasce una confezione regalo".

Racconto: apertura -> 3 ingredienti (ognuno "vola" nel vassoio in basso) -> incarto animato con carta kraft,
nastro e fiocco -> foto della confezione finita -> finale con logo e indirizzi.
Uso:  python3 reel_confezione.py <nome_confezione> <file_uscita.mp4>   (Pillow + ffmpeg).
Salva anche <uscita>_copertina.jpg. Confezioni disponibili: vedi CONFEZIONI (tisane, dattero).
Per una nuova confezione: aggiungere una voce a CONFEZIONI e le foto in foto/<foto_dir>/.
Regole di comunicazione: ../README.md (niente prenotazioni, niente "pezzo unico", niente claim sulla salute).
"""
import os, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE, "font") + os.sep
LOGO_PATH = os.path.join(BASE, "logo.png")
def pf(w, s): return ImageFont.truetype(FONT + "playfair-display-latin-%d-normal.woff" % w, s)
def ds(s): return ImageFont.truetype(FONT + "dancing-script-latin-700-normal.woff", s)
def it(w, s): return ImageFont.truetype(FONT + "inter-latin-%d-normal.woff" % {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}[w], s)

CREAM, DOT = (247, 241, 230), (214, 196, 168)
GREEN, GREEN2, GDOT = (38, 70, 52), (62, 104, 74), (52, 88, 64)
GREY, LIGHT, YELLOW = (120, 112, 100), (214, 236, 196), (255, 210, 120)
KRAFT, KDOT = (200, 165, 122), (150, 112, 78)
# ---------- contenuti: una voce per ogni confezione ----------
# passi: foto (una o due), y0 del ritaglio 4:5, numero, etichetta, titolo, sottotitolo
# coperchio: None = carta kraft a pois che si chiude; oppure (foto, (x0, y0, x1, y1)) = coperchio vero che scende
CONFEZIONI = {
    "tisane": dict(
        foto_dir="2026-11-confezione-tisane",
        passi=[(["tisaniera.jpg", "tisaniera-filtro.jpg"], [140, 80], "1", "LA TAZZA", "Tisaniera Neavita", "con filtro in acciaio e coperchio"),
               (["infuso-fiocchi-di-neve.jpg"], [60], "2", "L'INFUSO", "Fiocchi di Neve", "mela, ibisco, cannella, mandorle e pepe rosa"),
               (["miele-millefiori.jpg"], [60], "3", "IL MIELE", "Miele di Sardegna", "Millefiori · Apicoltura Derosas")],
        incarto=("4", "IL TOCCO FINALE", "Nastro e fiocco", "la confezioniamo a mano, in negozio"),
        coperchio=None, nastro=((236, 150, 196), (196, 96, 150)),
        finale=("confezione-finita.jpg", 40, "ECCO IL RISULTATO", "Pronta da regalare!",
                "nella foto: tazza, miele di Sardegna e tisane Neavita", "23,50 €")),
    "dattero": dict(
        foto_dir="2026-11-confezione-dattero",
        passi=[(["bagnoschiuma.jpg"], [(150, 220, 1270, 1620)], "1", "IL BAGNOSCHIUMA", "Bagnoschiuma", "L'Erbolario Nettare di Dattero · 250 ml"),
               (["crema-corpo.jpg"], [20], "2", "LA CREMA", "Crema Fluida Corpo", "L'Erbolario Nettare di Dattero · 200 ml"),
               (["profumo.jpg"], [(270, 480, 1190, 1630)], "3", "IL PROFUMO", "Profumo", "L'Erbolario Nettare di Dattero · 15 ml")],
        incarto=("4", "IL TOCCO FINALE", "Scatola e fiocco", "la confezioniamo a mano, in negozio"),
        coperchio=("scatola-erbolario.jpg", (250, 370, 1310, 1695)), nastro=((104, 118, 70), (66, 78, 42)),
        finale=("confezione-finita.jpg", 40, "ECCO IL RISULTATO", "Pronta da regalare!",
                "bagnoschiuma, crema corpo e profumo 15 ml", "57,50 €")),
}
NOME = sys.argv[1] if len(sys.argv) > 1 else "tisane"
OUT = sys.argv[2] if len(sys.argv) > 2 else "reel_%s.mp4" % NOME
CFG = CONFEZIONI[NOME]
FOTO_DIR = os.path.join(BASE, "foto", CFG["foto_dir"]) + os.sep
PASSI, INCARTO, FINALE = CFG["passi"], CFG["incarto"], CFG["finale"]
PINK, PINK_D = CFG["nastro"]
TIMELINE = [("intro", None, 3.0), ("passo", 0, 3.6), ("passo", 1, 3.0), ("passo", 2, 2.9),
            ("incarto", None, 3.0), ("finale", None, 3.6), ("outro", None, 4.4)]
XF = 0.35
FLY = 0.55          # durata del "volo" nel vassoio

# ---------- utilità ----------
def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_io(t): t = clamp(t); return 3 * t * t - 2 * t * t * t
def ease_back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def dots(w, h, color, dot, step=64, r=6):
    im = Image.new("RGB", (w, h), color); d = ImageDraw.Draw(im)
    for j, y in enumerate(range(-step, h + step, step)):
        off = step // 2 if j % 2 else 0
        for x in range(-step, w + step, step):
            d.ellipse((x + off - r, y - r, x + off + r, y + r), fill=dot)
    return im
def ctext(d, y, text, font, fill, anchor="ma", x=W // 2): d.text((x, y), text, font=font, fill=fill, anchor=anchor)
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

def load(name, y0, w, h):
    im = ImageOps.exif_transpose(Image.open(FOTO_DIR + name)).convert("RGB")
    if isinstance(y0, tuple):  # ritaglio esplicito (x0, y0, x1, y1), in proporzione 4:5
        return im.crop(y0)
    cw = im.size[0]; ch = int(cw * h / w); y0 = min(y0, im.size[1] - ch)
    return im.crop((0, y0, cw, y0 + ch))

BG_CREAM = dots(W, H, CREAM, DOT).convert("RGBA")
BG_GREEN = dots(W, H, GREEN, GDOT).convert("RGBA")

def header(dark):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 112, "Erboristeria", ds(64), LIGHT if dark else GREEN)
    ctext(d, 192, "APE COSMETICA  ·  OLBIA", it("SemiBold", 30), CREAM if dark else GREEN2)
    return L
HEAD_C, HEAD_G = header(False), header(True)

# ---------- geometria ----------
CW, CH = 720, 900; CX, CY = (W - CW) // 2, 290; RAD = 34
SH, SHP = shadow(CW, CH, RAD); MASK = rmask(CW, CH, RAD)
TXT_Y = CY + CH + 36
TS = 118; TRAY_Y = 1560; TGAP = 34
TRAY_X = [W // 2 - TS * 3 // 2 - TGAP + k * (TS + TGAP) for k in range(3)]
TMASK = rmask(TS, TS, 22)

PHOTOS = [[load(n, y, CW, CH) for n, y in zip(p[0], p[1])] for p in PASSI]
THUMBS = []
for ph in PHOTOS:
    src = ph[-1] if len(ph) == 1 else ph[0]
    s = min(src.size); THUMBS.append(src.crop(((src.size[0] - s) // 2, (src.size[1] - s) // 2,
                                              (src.size[0] + s) // 2, (src.size[1] + s) // 2)))
FIN = ImageEnhance.Brightness(load(FINALE[0], FINALE[1], CW, CH)).enhance(1.18)

def kb(img, k, z0=1.08):
    z = z0 - (z0 - 1) * k; w, h = img.size; cw, ch = w / z, h / z
    return img.crop((int((w - cw) / 2), int((h - ch) / 2), int((w + cw) / 2), int((h + ch) / 2))).resize((CW, CH), Image.BILINEAR)

def thumb_img(k, size):
    t = THUMBS[k].resize((size, size), Image.BILINEAR).convert("RGBA")
    m = rmask(size, size, max(8, size * 22 // TS)); t.putalpha(m)
    b = Image.new("RGBA", (size + 10, size + 10), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle((0, 0, size + 9, size + 9), max(10, size * 26 // TS), fill=(255, 255, 255, 255))
    b.alpha_composite(t, (5, 5)); return b

def draw_tray(fr, filled, alpha=1.0, title=True):
    if alpha <= 0: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    if title: ctext(d, TRAY_Y - 50, "nella confezione", it("SemiBold", 26), A(GREEN2, alpha))
    for k in range(3):
        x = TRAY_X[k]
        if k < filled: L.alpha_composite(thumb_img(k, TS), (x - 5, TRAY_Y - 5))
        else: d.rounded_rectangle((x, TRAY_Y, x + TS, TRAY_Y + TS), 22, outline=A(KDOT, 0.8), width=4)
    fr.alpha_composite(fade(L, alpha))

def step_text(num, lab, tit, sub, dark=False):
    L = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = it("Bold", 28); lw = d.textlength(lab, font=f); tot = 52 + 14 + lw; x0 = (W - tot) / 2
    d.ellipse((x0, -4, x0 + 52, 48), fill=GREEN if not dark else YELLOW)
    d.text((x0 + 26, 22), num, font=it("Bold", 30), fill=(255, 255, 255) if not dark else GREEN, anchor="mm")
    d.text((x0 + 66, 22), lab, font=f, fill=GREEN2 if not dark else LIGHT, anchor="lm")
    ctext(d, 66, tit, pf(700, 80), GREEN if not dark else (255, 255, 255))
    ctext(d, 170, sub, it("Regular", 33), GREY if not dark else CREAM)
    return L
STEP_TXT = [step_text(p[2], p[3], p[4], p[5]) for p in PASSI]
WRAP_TXT = step_text(*INCARTO)

def card_frame(fr, img):
    fr.alpha_composite(SH, (CX - SHP, CY - SHP)); fr.paste(img, (CX, CY), MASK)
    ImageDraw.Draw(fr).rounded_rectangle((CX, CY, CX + CW, CY + CH), RAD, outline=(255, 255, 255), width=8)

# ---------- fiocco ----------
def make_bow(size, PINK=PINK, PINK_D=PINK_D):
    S = size * 3; B = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(B)
    c = S // 2
    for sgn in (-1, 1):  # code
        d.polygon([(c, c), (c + sgn * S * 0.10, c + S * 0.42), (c + sgn * S * 0.22, c + S * 0.36)], fill=PINK_D)
    for sgn in (-1, 1):  # asole
        L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((c - S * 0.24, c - S * 0.13, c + S * 0.24, c + S * 0.13), fill=PINK, outline=PINK_D, width=S // 45)
        dl.ellipse((c - S * 0.12, c - S * 0.05, c + S * 0.12, c + S * 0.05), fill=PINK_D)
        L = L.rotate(sgn * -28, center=(c, c), resample=Image.BICUBIC)
        B.alpha_composite(L, (int(sgn * S * 0.21), -int(S * 0.04)))
    d.ellipse((c - S * 0.075, c - S * 0.085, c + S * 0.075, c + S * 0.065), fill=PINK_D)
    return B.resize((size, size), Image.LANCZOS)
BOW = make_bow(330)
BOW_INTRO = make_bow(330, (255, 210, 120), (200, 150, 60))  # fiocco chiaro sul fondo verde
PAPER = dots(CW, CH, KRAFT, KDOT, step=58, r=7).convert("RGBA")
LID = None
if CFG["coperchio"]:
    _l = ImageOps.exif_transpose(Image.open(FOTO_DIR + CFG["coperchio"][0])).convert("RGB")
    LID = _l.crop(CFG["coperchio"][1]).resize((CW, CH), Image.LANCZOS).convert("RGBA")

def wrapped_card(t):
    """Contenuto della card durante l'incarto: ingredienti sulla paglietta -> carta che si chiude -> nastro -> fiocco."""
    C = Image.new("RGBA", (CW, CH), (247, 236, 214, 255))
    d = ImageDraw.Draw(C)
    for k in range(260):  # paglietta
        x = (k * 97) % CW; y = (k * 53) % CH; col = [(120, 170, 90), (190, 60, 80), (230, 150, 190)][k % 3]
        d.arc((x - 40, y - 12, x + 40, y + 12), 200, 340, fill=col, width=5)
    big = 300; pos = [(CW // 2 - big - 10, 150), (CW // 2 + 10, 150), (CW // 2 - big // 2, 480)]
    for k in range(3):
        C.alpha_composite(thumb_img(k, big), pos[k])
    e = ease_io((t - 0.75) / 0.7)  # carta
    if e > 0 and LID is not None:   # il coperchio vero scende dall'alto
        C.alpha_composite(LID, (0, int(-CH + CH * e)))
    elif e > 0:
        half = CW // 2
        C.alpha_composite(PAPER.crop((0, 0, half + 4, CH)), (int(-half - 4 + (half + 4) * e), 0))
        C.alpha_composite(PAPER.crop((half - 4, 0, CW, CH)), (int(CW - (half + 4) * e), 0))
    r = ease_io((t - 1.45) / 0.45)  # nastro
    if r > 0:
        d = ImageDraw.Draw(C); bw = 64
        d.rectangle((CW // 2 - bw // 2, CH // 2 - int(CH / 2 * r), CW // 2 + bw // 2, CH // 2 + int(CH / 2 * r)), fill=PINK)
        d.rectangle((CW // 2 - int(CW / 2 * r), CH // 2 - bw // 2, CW // 2 + int(CW / 2 * r), CH // 2 + bw // 2), fill=PINK)
        for off in (-bw // 2 + 6, bw // 2 - 8):
            d.line((CW // 2 + off, CH // 2 - int(CH / 2 * r), CW // 2 + off, CH // 2 + int(CH / 2 * r)), fill=PINK_D, width=3)
    return C

# ---------- scene ----------
def render_intro(t, dur):
    fr = BG_GREEN.copy(); fr.alpha_composite(HEAD_G)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = [ease((t - 0.25 - k * 0.35) / 0.55) for k in range(4)]
    ctext(d, 470 + (1 - a[0]) * 30, "Come nasce una", ds(110), A(LIGHT, a[0]))
    ctext(d, 640 + (1 - a[1]) * 30, "confezione", pf(900, 150), A((255, 255, 255), a[1]))
    ctext(d, 810 + (1 - a[1]) * 30, "regalo", pf(900, 150), A((255, 255, 255), a[1]))
    ctext(d, 1030 + (1 - a[2]) * 30, "la prepariamo noi, a mano, in negozio", it("Medium", 42), A(CREAM, a[2]))
    fr.alpha_composite(L)
    b = ease_back((t - 1.4) / 0.5)
    if t > 1.4 and b > 0.02:
        s = max(1, int(330 * b)); bw = BOW_INTRO.resize((s, s), Image.BICUBIC)
        fr.alpha_composite(bw, (W // 2 - s // 2, 1240 - s // 2 + 120))
    return fr.convert("RGB")

def render_passo(i, t, dur):
    fr = BG_CREAM.copy(); fr.alpha_composite(HEAD_C)
    ph = PHOTOS[i]
    if len(ph) == 2:
        m = ease_io((t - 1.5) / 0.5)
        img = Image.blend(kb(ph[0], clamp(t / dur)), kb(ph[1], clamp(t / dur)), m)
    else:
        img = kb(ph[0], clamp(t / dur))
    t_fly = dur - XF - FLY
    f = ease_io((t - t_fly) / FLY)
    # vassoio: gli slot precedenti sono già pieni
    draw_tray(fr, i)
    if f <= 0:
        card_frame(fr, img)
    else:  # la card rimpicciolisce e vola nello slot i
        s = 1 - f; w = int(CW + (TS - CW) * f); h = int(CH + (TS - CH) * f)
        x = int(CX + (TRAY_X[i] - CX) * f); y = int(CY + (TRAY_Y - CY) * f)
        if f >= 1:
            draw_tray(fr, i + 1, title=False)
        else:
            src = img if f < 0.5 else THUMBS[i].resize((CW, CH))
            c = src.resize((max(1, w), max(1, h)), Image.BILINEAR).convert("RGBA")
            c.putalpha(rmask(c.size[0], c.size[1], int(RAD * s + 22 * f)))
            fr.alpha_composite(c, (x, y))
    e = ease((t - 0.35) / 0.5) * clamp((t_fly + 0.15 - t) / 0.3)
    if e > 0: fr.alpha_composite(fade(STEP_TXT[i], e), (0, int(TXT_Y + (1 - ease((t - 0.35) / 0.5)) * 40)))
    return fr.convert("RGB")

def render_incarto(t, dur):
    fr = BG_CREAM.copy(); fr.alpha_composite(HEAD_C)
    # gli ingredienti escono dal vassoio ed entrano nella card
    draw_tray(fr, 3, alpha=1 - ease(t / 0.5))
    card = wrapped_card(t)
    fr.alpha_composite(SH, (CX - SHP, CY - SHP))
    card.putalpha(MASK); fr.alpha_composite(card, (CX, CY))
    ImageDraw.Draw(fr).rounded_rectangle((CX, CY, CX + CW, CY + CH), RAD, outline=(255, 255, 255), width=8)
    b = ease_back((t - 1.95) / 0.45)
    if t > 1.95 and b > 0.02:
        s = max(1, int(330 * b)); bw = BOW.resize((s, s), Image.BICUBIC)
        fr.alpha_composite(bw, (CX + CW // 2 - s // 2, CY + CH // 2 - s // 2 - 20))
    e = ease((t - 0.3) / 0.5)
    fr.alpha_composite(fade(WRAP_TXT, e), (0, int(TXT_Y + (1 - e) * 40)))
    return fr.convert("RGB")

FIN_TXT = None
def fin_text():
    L = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 0, FINALE[2], it("Bold", 28), GREEN2)
    ctext(d, 44, FINALE[3], pf(700, 84), GREEN)
    ctext(d, 154, FINALE[4], it("Regular", 31), GREY)
    f = pf(800, 56); w = d.textlength(FINALE[5], font=f) + 90
    d.rounded_rectangle((W / 2 - w / 2, 214, W / 2 + w / 2, 300), 43, fill=YELLOW)
    ctext(d, 257, FINALE[5], f, GREEN, anchor="mm")
    return L
FIN_TXT = fin_text()

def render_finale(t, dur):
    fr = BG_CREAM.copy(); fr.alpha_composite(HEAD_C)
    card_frame(fr, kb(FIN, clamp(t / dur)))
    e = ease((t - 0.4) / 0.5)
    fr.alpha_composite(fade(FIN_TXT, e), (0, int(TXT_Y - 6 + (1 - e) * 40)))
    return fr.convert("RGB")

_lg = Image.open(LOGO_PATH).convert("RGB").resize((380, 380), Image.LANCZOS)
LOGO = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
ImageDraw.Draw(LOGO).rounded_rectangle((0, 0, 419, 419), 48, fill=(255, 255, 255, 255)); LOGO.paste(_lg, (20, 20))
def render_outro(t, dur):
    fr = BG_GREEN.copy()
    a = [ease((t - k * 0.22) / 0.5) for k in range(5)]
    if a[0] > 0: fr.alpha_composite(fade(LOGO, a[0]), ((W - 420) // 2, int(170 + (1 - a[0]) * 30)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, 630 + (1 - a[1]) * 30, "Ti aspettiamo!", ds(120), A(LIGHT, a[1]))
    ctext(d, 820 + (1 - a[2]) * 30, "Confezioni regalo personalizzate", pf(700, 58), A((255, 255, 255), a[2]))
    ctext(d, 900 + (1 - a[2]) * 30, "in negozio ne trovi tante altre", it("Medium", 40), A(YELLOW, a[2]))
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
    if kind == "passo": return render_passo(i, t, dur)
    return {"intro": render_intro, "incarto": render_incarto, "finale": render_finale, "outro": render_outro}[kind](t, dur)

starts, t0 = [], 0.0
for s in TIMELINE: starts.append(t0); t0 += s[2] - XF
TOTAL = t0 + XF
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
cover_t = starts[5] + 1.6
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
