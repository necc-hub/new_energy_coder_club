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


def build_soul(args, n_total, out):
    """灵魂乐 groove：Fmaj7 → Em7 → Dm7 → C7（每和弦 2 小节），摇摆 8 分。"""
    SR = 44100
    bpm = args.bpm
    beat = 60.0 / bpm
    eighth = beat / 2
    swing = 0.58
    bar = beat * 4

    def t_e(i):
        base = i * eighth
        if i % 2 == 1:
            base += eighth * (swing * 2 - 1)
        return base

    CH = [
        (43.65, [174.61, 220.00, 261.63, 329.63]),   # Fmaj7
        (41.20, [164.81, 196.00, 246.94, 293.66]),   # Em7
        (36.71, [146.83, 174.61, 220.00, 261.63]),   # Dm7
        (32.70, [130.81, 164.81, 196.00, 233.08]),   # C7
    ]
    BASS_PAT = [(0, 0, 1.0), (2, 12, 0.7), (3, 7, 0.8), (4, 0, 0.9), (6, 12, 0.6), (7, 7, 0.7)]
    rng = np.random.default_rng(77)

    def add(i0, n, sig):
        if i0 < n_total:
            out[i0:i0 + n] += sig[:max(0, min(n, n_total - i0))]

    for ci in range(4):
        start = ci * 2 * bar
        dur_c = 2 * bar
        seg = int(dur_c * SR)
        i0 = int(start * SR)
        if i0 >= n_total:
            break
        tt = np.arange(seg) / SR
        root, tones = CH[ci]
        # Hammond 风琴垫（leslie 颤音）
        pad = sum(np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) for f in tones)
        pad *= (0.65 + 0.35 * np.sin(2 * np.pi * 6 * tt)) * 0.05 * np.minimum(tt / 0.3, 1)
        add(i0, seg, pad)
        for bar_i in range(2):
            bs = start + bar_i * bar
            # Rhodes 刺和：& of 2（eighth 3）与 beat 4（eighth 6）
            for e_idx in (3, 6):
                st = bs + t_e(e_idx)
                j0 = int(st * SR)
                nn = int(0.5 * SR)
                t2 = np.arange(nn) / SR
                stab = sum(np.sin(2 * np.pi * f * t2) + 0.5 * np.sin(2 * np.pi * 2 * f * t2)
                           + 0.12 * np.sin(2 * np.pi * 3.02 * f * t2) for f in tones)
                stab *= np.exp(-t2 * 7.5) * 0.13
                add(j0, nn, stab)
            # 放克贝斯
            for e_idx, semi, vel in BASS_PAT:
                st = bs + t_e(e_idx)
                j0 = int(st * SR)
                nn = int(0.30 * SR)
                t2 = np.arange(nn) / SR
                f = root * 2 ** (semi / 12)
                note = (np.sin(2 * np.pi * f * t2) + 0.3 * np.sin(2 * np.pi * 2 * f * t2)) * np.exp(-t2 * 10) * 0.34 * vel
                add(j0, nn, note)
            # 鼓组：kick 1&3，snare 2&4，hat 8 分
            for e_idx in range(8):
                st = bs + t_e(e_idx)
                j0 = int(st * SR)
                if e_idx in (0, 4):
                    nn = int(0.22 * SR)
                    t2 = np.arange(nn) / SR
                    f0 = 120 - 65 * (t2 / 0.22)
                    add(j0, nn, np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.exp(-t2 * 22) * 0.5)
                if e_idx in (2, 6):
                    nn = int(0.14 * SR)
                    t2 = np.arange(nn) / SR
                    body = np.sin(2 * np.pi * 185 * t2) * np.exp(-t2 * 26) * 0.35
                    noiz = np.diff(rng.standard_normal(nn + 1)) * np.exp(-t2 * 45) * 0.30
                    add(j0, nn, body + noiz)
                nn = int(0.05 * SR)
                t2 = np.arange(nn) / SR
                add(j0, nn, np.diff(rng.standard_normal(nn + 1)) * np.exp(-t2 * 90) * 0.075)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, default=48)
    ap.add_argument("--bpm", type=int, default=80)
    ap.add_argument("--style", choices=["ambient", "soul"], default="ambient",
                    help="ambient=氛围合成波（默认） soul=灵魂乐 groove（Rhodes+贝斯+摇摆鼓组+风琴）")
    ap.add_argument("--key", choices=list(KEYS) + ["F"], default="Am", help="soul 风格固定 F 进行，此参数仅 ambient 生效")
    ap.add_argument("--energy", type=float, default=0.5, help="0=纯氛围 1=鼓组加满")
    ap.add_argument("--lead", action="store_true", help="ambient 风格：加 theremin 式滑音主音（科幻感）")
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

    if args.style == "soul":
        build_soul(args, n_total, out)
    else:
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
