#!/usr/bin/env python3
"""promo-render: 程序化赛博氛围 BGM 合成（无版权依赖）

用法:
  python3 synth_bgm.py --duration 48 --bpm 80 --key Am --out /tmp/bgm.wav
  python3 synth_bgm.py --duration 43 --bpm 100 --key Em --energy 1 --out /tmp/bgm.wav

和声: 小调 i → VI → VII → i（Am: Am F G Am / Em: Em C D Em / Cm: Cm Ab Bb Cm）
"""
import argparse, wave
import numpy as np

SR = 44100
KEYS = {"Am": 110.00, "Em": 82.41, "Cm": 65.41}  # 根音 A2/E2/C2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, default=48)
    ap.add_argument("--bpm", type=int, default=80)
    ap.add_argument("--key", choices=list(KEYS), default="Am")
    ap.add_argument("--energy", type=float, default=0.5, help="0=纯氛围 1=鼓组加满")
    ap.add_argument("--lead", action="store_true", help="加入 theremin 式滑音主音（科幻感）")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = KEYS[args.key]
    bar = 240.0 / args.bpm          # 4 拍/小节
    chord_dur = args.duration / 4   # 四个和弦均分
    semi = lambda s: root * 2 ** (s / 12)
    CHORDS = [  # (级, 三和弦半音集)
        (0, [0, 3, 7]), (8, [0, 4, 7]), (10, [0, 4, 7]), (0, [0, 3, 7]),
    ]
    n_total = int(SR * args.duration)
    out = np.zeros(n_total)

    def adsr(n, a, d, s, r):
        total = a + d + r
        if total > n / SR:
            k = (n / SR) / total * 0.9
            a, d, r = a * k, d * k, r * k
        e = np.ones(n)
        na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
        if na:
            e[:na] = np.linspace(0, 1, na)
        if nd:
            e[na:na + nd] = np.linspace(1, s, nd)
        if nr:
            e[-nr:] *= np.linspace(1, 0, nr)
        return e

    for ci, (shift, tones) in enumerate(CHORDS):
        start = ci * chord_dur
        i0 = int(start * SR)
        seg = int(chord_dur * SR)
        tt = np.arange(seg) / SR
        freqs = [semi(shift + t) for t in tones]
        pad = np.zeros(seg)
        for f in freqs:
            pad += np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.004 * tt)
        pad *= adsr(seg, 2.2, 3.0, 0.8, 2.5) * 0.045
        sub_f = semi(shift) / 4
        subw = np.sin(2 * np.pi * sub_f * tt) * (0.75 + 0.25 * np.sin(2 * np.pi * 2.0 * tt))
        subw *= adsr(seg, 0.8, 2.0, 0.9, 1.5) * 0.22
        out[i0:i0 + seg] += pad + subw
        # 分解和弦（8 分音符）
        note = 30.0 / args.bpm
        arp = freqs + [f * 2 for f in freqs]
        seq = (arp + arp[::-1])
        k = 0
        st = start
        while st < start + chord_dur - note / 2:
            f = seq[k % len(seq)]
            j0 = int(st * SR)
            nn = int(0.36 * SR)
            t2 = np.arange(nn) / SR
            pl = (np.sin(2 * np.pi * f * t2) + 0.4 * np.sin(4 * np.pi * f * t2)) * np.exp(-t2 * 9) * 0.16
            if j0 + nn <= n_total:
                out[j0:j0 + nn] += pl
            if j0 + int(note * SR) + nn <= n_total:
                out[j0 + int(note * SR):j0 + int(note * SR) + nn] += pl * 0.35
            k += 1
            st += note

    # 鼓组（energy 控制强度）
    rng = np.random.default_rng(416)
    beat = 60.0 / args.bpm
    for b in range(int(args.duration / beat)):
        st = b * beat
        i0 = int(st * SR)
        nn = int(0.25 * SR)
        t2 = np.arange(nn) / SR
        f0 = 110 - 60 * (t2 / 0.25)
        kick = np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.exp(-t2 * 18) * 0.30 * args.energy
        out[i0:i0 + nn] += kick
        j0 = int((st + beat / 2) * SR)
        mm = int(0.06 * SR)
        hat = np.diff(rng.standard_normal(mm + 1)) * np.exp(-np.arange(mm) / SR * 80) * 0.05 * (0.3 + 0.7 * args.energy)
        if j0 + mm < n_total:
            out[j0:j0 + mm] += hat

    # theremin 式滑音主音（--lead）
    if args.lead:
        for ci, (shift, tones) in enumerate(CHORDS):
            start = ci * chord_dur
            seg = int(chord_dur * SR)
            i0 = int(start * SR)
            tt = np.arange(seg) / SR
            f0 = semi(shift + 12)
            f1 = semi(shift + tones[-1] + 12)
            frac = np.clip(tt / (chord_dur * 0.7), 0, 1)
            freq = f0 + (f1 - f0) * frac ** 2
            vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * tt)
            phase = np.cumsum(2 * np.pi * freq * vib / SR)
            env = np.sin(np.pi * np.clip(tt / chord_dur, 0, 1)) ** 2
            out[i0:i0 + seg] += np.sin(phase) * env * 0.055

    fade = min(1.5, args.duration * 0.05)
    out[:int(fade * SR)] *= np.linspace(0, 1, int(fade * SR))
    out[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))
    out = np.tanh(out * 1.4)
    out /= np.max(np.abs(out))
    out *= 0.89
    stereo = np.stack([out, np.roll(out, 128)], axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(args.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"bgm: {args.out} ({args.duration}s, {args.bpm}bpm, {args.key})")


if __name__ == "__main__":
    main()
