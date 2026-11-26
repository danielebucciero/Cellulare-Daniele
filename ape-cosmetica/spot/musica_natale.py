"""Musica natalizia ORIGINALE (composta e sintetizzata qui, nessun diritto di terzi) per i Reel.

Campanelle (glockenspiel), arpa, accordi morbidi, basso leggero e sonagli; Re maggiore, 96 bpm.
Uso:
  python3 musica_natale.py <uscita.wav> <durata_secondi>
  python3 musica_natale.py --monta <video.mp4> <video_con_musica.mp4>   (crea la musica della durata giusta e la unisce)
Richiede numpy e ffmpeg.
"""
import sys, subprocess, json, wave, tempfile, os
import numpy as np

SR = 44100
# stile: "natale" (predefinito), "allegro" (più veloce e brillante), "dolce" (lento, senza sonagli)
STILE = os.environ.get("MUSICA_STILE", "natale")
BPM = {"natale": 96, "allegro": 118, "dolce": 76}.get(STILE, 96)
BEAT = 60 / BPM
rng = np.random.default_rng(7)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR)); e[:na] *= np.linspace(0, 1, na)
    return e

def bell(f, dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) * env(n, 0.002, 0.9)
         + 0.45 * np.sin(2 * np.pi * f * 2.0 * t) * env(n, 0.002, 0.35)
         + 0.25 * np.sin(2 * np.pi * f * 3.01 * t) * env(n, 0.001, 0.18)
         + 0.12 * np.sin(2 * np.pi * f * 4.17 * t) * env(n, 0.001, 0.08))
    return s

def harp(f, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) for k in range(5))
    return s * env(n, 0.004, 0.45)

def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            s += np.sin(2 * np.pi * ff * t) + 0.25 * np.sin(2 * np.pi * 2 * ff * t)
    a = min(n, int(0.6 * SR)); r = min(n, int(0.8 * SR))
    e = np.ones(n); e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r)
    return s * e / (len(freqs) * 3)

def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * env(n, 0.01, 0.6)

def sleigh(dur=0.16):
    """Sonaglio: alcune parziali metalliche acute con tremolo, più un filo di rumore."""
    n = int(dur * SR); t = np.arange(n) / SR
    freqs = rng.uniform(4200, 8800, 6)
    x = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) for f in freqs) / 6
    x += 0.15 * rng.standard_normal(n)
    tr = 0.6 + 0.4 * np.sin(2 * np.pi * 28 * t) ** 2
    return x * env(n, 0.002, 0.045) * tr * 0.22

def reverb(x, secs=2.2, decay=0.55, seed=1):
    r = np.random.default_rng(seed)
    n = int(secs * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / decay); ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n; N = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]
    return y

# ---------- composizione (originale) ----------
D, E, Fs, G, A, B, Cs = 62, 64, 66, 67, 69, 71, 73
CHORDS = [  # (fondamentale, note dell'accordo) per battuta
    (D, [D, Fs, A]), (B - 12, [B - 12, D, Fs]), (G - 12, [G - 12, B - 12, D]), (A - 12, [A - 12, Cs, E]),
    (D, [D, Fs, A]), (B - 12, [B - 12, D, Fs]), ("GA", None), (D, [D, Fs, A]),
]
MELODY = [  # (nota MIDI, durata in battiti), 4 battiti per battuta
    [(81, 1), (78, .5), (81, .5), (86, 1), (81, 1)],
    [(83, 1), (78, .5), (83, .5), (86, 2)],
    [(79, 1), (83, .5), (86, .5), (83, 1), (79, 1)],
    [(81, 1), (85, .5), (88, .5), (85, 2)],
    [(86, 1), (81, .5), (78, .5), (81, 1), (86, 1)],
    [(86, 1), (83, .5), (78, .5), (83, 2)],
    [(79, .5), (83, .5), (86, 1), (81, .5), (85, .5), (88, 1)],
    [(86, 4)],
]

if STILE == "allegro":
    MELODY = [
        [(78, .5), (81, .5), (86, .5), (81, .5), (83, 1), (81, 1)],
        [(78, .5), (83, .5), (86, .5), (83, .5), (85, 2)],
        [(79, .5), (83, .5), (86, .5), (88, .5), (86, 1), (83, 1)],
        [(81, .5), (85, .5), (88, .5), (85, .5), (88, 2)],
        [(90, .5), (88, .5), (86, .5), (85, .5), (86, 1), (81, 1)],
        [(83, .5), (86, .5), (90, .5), (86, .5), (88, 2)],
        [(79, .5), (83, .5), (86, .5), (88, .5), (85, .5), (88, .5), (90, 1)],
        [(86, 4)],
    ]
def componi(durata):
    n = int((durata + 0.5) * SR)
    Lb, Rb = np.zeros(n), np.zeros(n)     # campanelle + arpa (stereo)
    padm, bassm, bells_sl = np.zeros(n), np.zeros(n), np.zeros(n)
    def add(buf, sig, t0, g=1.0):
        i = int(t0 * SR)
        if i >= n: return
        j = min(n, i + len(sig)); buf[i:j] += g * sig[:j - i]
    bar = 4 * BEAT
    # battute necessarie: per video più lunghi si ripetono le prime 6 e si chiude sempre con le ultime 2
    nbars = max(len(MELODY), int(round((durata - 1.2) / bar)))
    seq = [k % 6 for k in range(nbars - 2)] + [6, 7]
    start = 0.15
    for b in range(nbars):
        q = seq[b]
        t_bar = start + b * bar
        # accordi, basso, arpa
        if CHORDS[q][0] == "GA":
            parts = [(0, G - 12, [G - 12, B - 12, D]), (2, A - 12, [A - 12, Cs, E])]
        else:
            parts = [(0, CHORDS[q][0], CHORDS[q][1])]
        for k, (off, root, notes) in enumerate(parts):
            length = (4 if len(parts) == 1 else 2) * BEAT
            last = (b == nbars - 1)
            add(padm, pad([hz(m) for m in notes], length + (2.5 if last else 0.3)), t_bar + off * BEAT, 0.55)
            add(bassm, bass(hz(root - 12), length), t_bar + off * BEAT, 0.4)
            arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 24]
            steps = int(length / (BEAT / 2))
            for s in range(steps if not last else 4):
                m = arp[s % 4]
                sig = harp(hz(m))
                pan = 0.35 if s % 2 else -0.35
                add(Lb, sig, t_bar + off * BEAT + s * BEAT / 2, 0.16 * (1 - pan))
                add(Rb, sig, t_bar + off * BEAT + s * BEAT / 2, 0.16 * (1 + pan))
        # melodia sulle campanelle
        tt = t_bar
        for m, d in MELODY[q]:
            sig = bell(hz(m), 3.0 if b == nbars - 1 else 2.2)
            add(Lb, sig, tt, 0.30); add(Rb, sig, tt, 0.30)
            tt += d * BEAT
        # sonagli: ottavi leggeri, accento sui battiti 2 e 4 (dalla 2a battuta, non nell'ultima)
        if 1 <= b < nbars - 1:
            for s in range(8):
                g = 0.9 if s in (2, 6) else 0.45
                add(bells_sl, sleigh(), t_bar + s * BEAT / 2, g)
    # scintillio finale (arpeggio veloce discendente)
    tf = start + (nbars - 1) * bar + 0.2
    for k, m in enumerate([98, 93, 90, 86, 81, 78]):
        sig = bell(hz(m), 2.5); add(Lb, sig, tf + k * 0.09, 0.13); add(Rb, sig, tf + k * 0.09, 0.13)

    if STILE == "dolce": bells_sl = bells_sl * 0.0
    if STILE == "allegro": bassm = bassm * 1.25
    L = Lb + padm * 0.9 + bassm + bells_sl * 0.55
    R = Rb + padm * 0.9 + bassm + bells_sl * 0.4
    L = 0.78 * L + 0.32 * reverb(L, seed=1)
    R = 0.78 * R + 0.32 * reverb(R, seed=2)
    st = np.stack([L, R], 1)[: int(durata * SR)]
    # dissolvenza finale e normalizzazione
    f = min(len(st), int(1.8 * SR)); st[-f:] *= np.linspace(1, 0, f)[:, None] ** 1.5
    fi = int(0.02 * SR); st[:fi] *= np.linspace(0, 1, fi)[:, None]
    st *= 0.70 / np.max(np.abs(st))   # circa -14 LUFS, il livello dei social
    return st

def salva_wav(path, st):
    data = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())

def durata_video(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])

if __name__ == "__main__":
    if sys.argv[1] == "--monta":
        src, dst = sys.argv[2], sys.argv[3]
        dur = durata_video(src)
        with tempfile.TemporaryDirectory() as td:
            wav = os.path.join(td, "musica.wav"); salva_wav(wav, componi(dur))
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst], check=True)
        print("creato", dst, "durata", round(dur, 2), "s")
    else:
        salva_wav(sys.argv[1], componi(float(sys.argv[2])))
        print("creato", sys.argv[1])
