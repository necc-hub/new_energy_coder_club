#!/usr/bin/env python3
"""promo-render: 配置 JSON → 确定性渲染页 render.html

用法:
  python3 build_render_page.py config.json -o ./outdir
输出:
  outdir/render.html (+ fonts/ 自托管字体目录)
渲染页契约: window.__seek(t) 精确寻址; window.__ready === true 后可采集
"""
import argparse, json, shutil, sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
FONTS = SKILL_DIR / "assets"

HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{doc_title}</title>
<style>
@font-face{{font-family:'Orbitron';font-weight:900;font-style:normal;font-display:swap;src:url('./fonts/orbitron-latin-900-normal.woff2') format('woff2')}}
@font-face{{font-family:'Share Tech Mono';font-weight:400;font-style:normal;font-display:swap;src:url('./fonts/share-tech-mono-latin-400-normal.woff2') format('woff2')}}
html,body{{margin:0;height:100%;background:#05010f;overflow:hidden}}
#stage{{zoom:{zoom};position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#05010f;font-family:'Share Tech Mono','PingFang SC',monospace}}
.grid{{position:absolute;inset:-60px;background-image:linear-gradient(rgba(0,240,255,.16) 1px,transparent 1px),linear-gradient(90deg,rgba(0,240,255,.16) 1px,transparent 1px);background-size:44px 44px;transform:perspective(700px) rotateX(56deg);transform-origin:center 70%;mask-image:radial-gradient(ellipse at center,#000 40%,transparent 78%)}}
.scan{{position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(to bottom,rgba(255,255,255,.04) 0 1px,transparent 1px 3px);mix-blend-mode:overlay}}
.vig{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at center,transparent 52%,rgba(2,0,10,.9) 100%)}}
.scene{{position:absolute;inset:0;opacity:0;visibility:hidden}}
.hud{{border:1px solid {accent}B3;background:rgba(3,12,8,.72);backdrop-filter:blur(3px)}}
.cap{{display:inline-block;padding:8px 16px;font-size:15px;letter-spacing:.22em;color:{accent}}}
.big{{font-family:'Orbitron','PingFang SC',sans-serif;font-weight:900;color:#fff;letter-spacing:.06em}}
.phone{{position:absolute;overflow:hidden;border:2px solid {accent}A6;box-shadow:0 0 44px {accent}40;background:#0a0f1c}}
.phone img{{width:100%;height:100%;object-fit:cover;object-position:top}}
.chip{{display:inline-block;margin-right:14px;padding:7px 14px;border:1px solid {accent}8C;color:#d9efe4;font-size:15px;letter-spacing:.18em;background:rgba(3,12,8,.7)}}
.chip b{{color:{accent};font-weight:400}}
.pt{{font-size:22px;line-height:1.9;color:#d5eae0;letter-spacing:.1em}}
.pt b{{color:{accent};font-weight:400}}
</style>
</head>
<body>
<div id="stage">
  <div class="grid"></div>
{scenes}
  <div class="scan"></div>
  <div class="vig"></div>
</div>
<script src="{gsap_src}"></script>
<script>
const tl = gsap.timeline({{paused:true, defaults:{{ease:'power2.out'}}}})
{timeline}
window.__seek = (t) => {{ tl.seek(Math.min(t, {total}-0.001), false) }}
Promise.all(Array.from(document.images).map((i)=>i.complete?1:new Promise((r)=>{{i.onload=r;i.onerror=r}})))
  .then(()=>{{document.fonts.ready.then(()=>{{window.__ready=true}})}})
</script>
</body>
</html>
"""


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def scene_html(cfg, sc, idx):
    t, sid = sc["type"], f"s{idx}"
    if t == "title":
        ti = cfg["title"]
        return f'''  <div class="scene" id="{sid}"{ " style=\"opacity:1;visibility:visible\"" if idx == 0 else "" }>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">
      <div class="cap" id="{sid}-kicker">{esc(ti.get("kicker",""))}</div>
      <div class="big" id="{sid}-main" style="margin-top:26px;font-size:110px;line-height:1;text-shadow:0 0 26px {cfg['accent']}B3,0 0 90px {cfg['accent']}4D">{esc(ti["main"])}</div>
      <div id="{sid}-sub" style="margin-top:24px;font-size:26px;letter-spacing:.5em;color:{cfg['accent']}CC">{esc(ti.get("sub",""))}</div>
      <div id="{sid}-mini" style="margin-top:36px;font-size:15px;letter-spacing:.3em;color:#475569">{esc(ti.get("mini",""))}</div>
    </div>
  </div>'''
    if t == "wide":
        kb = sc.get("kenburns", {})
        s0, s1 = kb.get("scale", [1.15, 1.0])
        x0, x1 = kb.get("x", [-60, 60])
        chips = "".join(f'<span class="chip">{c}</span>' for c in sc.get("chips", []))
        foot = f'<div style="position:absolute;top:600px;left:90px;font-size:16px;letter-spacing:.22em;color:#64748b">{esc(sc["footnote"])}</div>' if sc.get("footnote") else ""
        return f'''  <div class="scene" id="{sid}">
    <div style="position:absolute;top:40px;left:70px" class="cap hud">{esc(sc["caption"])}</div>
    <div style="position:absolute;top:160px;left:90px;width:1100px;height:326px;overflow:hidden;border:2px solid {cfg['accent']}80;box-shadow:0 0 50px {cfg['accent']}2E">
      <img id="{sid}-img" src="{sc['src']}" style="width:100%;height:100%;object-fit:cover;object-position:top">
    </div>
    <div style="position:absolute;top:516px;left:90px">{chips}</div>
    {foot}
  </div>'''
    if t == "phone_text":
        pts = "".join(f'<div class="{sid}-pt pt">{p}</div>' for p in sc["points"])
        return f'''  <div class="scene" id="{sid}">
    <div class="phone" id="{sid}-phone" style="top:64px;left:880px;width:300px;height:592px"><img src="{sc['src']}"></div>
    <div style="position:absolute;top:110px;left:90px;width:720px">
      <div class="cap hud {sid}-pt">{esc(sc["badge"])}</div>
      <div class="big {sid}-pt" style="margin-top:26px;font-size:58px;text-shadow:0 0 20px {cfg['accent']}8C">{esc(sc["headline"])}</div>
      <div style="margin-top:24px">{pts}</div>
    </div>
  </div>'''
    if t == "split":
        return f'''  <div class="scene" id="{sid}">
    <div class="phone {sid}-ph" style="top:90px;left:220px;width:270px;height:520px"><img src="{sc['left']}"></div>
    <div class="phone {sid}-ph" style="top:120px;left:650px;width:270px;height:520px"><img src="{sc['right']}"></div>
    <div style="position:absolute;top:64px;left:0;width:100%;text-align:center"><span class="cap hud">{esc(sc["caption"])}</span></div>
    <div class="{sid}-foot" style="position:absolute;top:640px;left:0;width:100%;text-align:center;font-size:17px;letter-spacing:.2em;color:{cfg['accent']}CC">{esc(sc["footnote"])}</div>
  </div>'''
    if t == "carousel":
        imgs = sc["images"]
        slides = []
        caps = []
        dots = []
        for k, im in enumerate(imgs):
            off = "transform:translateX(920px)" if k > 0 else ""
            slides.append(f'    <div class="{sid}-slide" id="{sid}-slide-{k}" style="position:absolute;inset:0;{off}"><img src="{im["src"]}" style="width:100%;height:100%;object-fit:cover"></div>')
            op = 1 if k == 0 else 0
            caps.append(f'    <div class="{sid}-cap" id="{sid}-cap-{k}" style="position:absolute;bottom:14px;left:0;width:100%;text-align:center;font-size:17px;letter-spacing:.2em;color:{cfg["accent"]};opacity:{op};text-shadow:0 0 12px rgba(0,0,0,.9)">{im.get("caption","")}</div>')
            bg = cfg["accent"] if k == 0 else "rgba(255,255,255,0.18)"
            dots.append(f'    <span id="{sid}-dot-{k}" style="display:inline-block;width:10px;height:10px;margin-left:8px;background:{bg}"></span>')
        return f'''  <div class="scene" id="{sid}">
    <div style="position:absolute;top:40px;left:70px" class="cap hud">{esc(sc.get("caption",""))}</div>
    <div id="{sid}-frame" style="position:absolute;top:96px;left:190px;width:900px;height:540px;overflow:hidden;border:2px solid {cfg['accent']}80;box-shadow:0 0 50px {cfg['accent']}2E">
{chr(10).join(slides)}
{chr(10).join(caps)}
    </div>
    <div style="position:absolute;top:56px;right:90px;text-align:right">
{chr(10).join(dots)}
    </div>
  </div>'''
    if t == "endcard":
        return f'''  <div class="scene" id="{sid}">
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">
      <div id="{sid}-flow" class="big" style="font-size:30px;letter-spacing:.12em;white-space:nowrap;text-shadow:0 0 18px {cfg['accent']}8C">{esc(sc["flow"])}</div>
      <div id="{sid}-url" style="margin-top:36px;font-size:30px;letter-spacing:.3em;color:{cfg['accent']};text-shadow:0 0 16px {cfg['accent']}99">{esc(sc["url"])}</div>
      <div id="{sid}-tag" style="margin-top:30px;font-size:16px;letter-spacing:.4em;color:#64748b">{esc(sc["tag"])}</div>
    </div>
  </div>'''
    raise SystemExit(f"未知场景类型: {t}")


def scene_tl(cfg, sc, idx, last):
    t, sid, a, o = sc["type"], f"s{idx}", sc["at"], sc["out"]
    dur = o - a
    L = []
    if idx > 0:
        L.append(f"tl.fromTo('#{sid}', {{autoAlpha:0}}, {{autoAlpha:1, duration:0.4}}, {a})")
    inner_a = a + 0.15
    if t == "title":
        L += [
            f"tl.fromTo('#{sid}-kicker', {{opacity:0,y:24}}, {{opacity:1,y:0,duration:0.35}}, {a+0.05})",
            f"tl.fromTo('#{sid}-main', {{opacity:0,scale:1.35,filter:'blur(10px)'}}, {{opacity:1,scale:1,filter:'blur(0px)',duration:0.55,ease:'power4.out'}}, {a+0.15})",
            f"tl.to('#{sid}-main', {{x:-7,duration:0.06,ease:'none'}}, {a+0.85})",
            f"tl.to('#{sid}-main', {{x:6,duration:0.06,ease:'none'}}, {a+0.91})",
            f"tl.to('#{sid}-main', {{x:0,duration:0.06,ease:'none'}}, {a+0.97})",
            f"tl.fromTo('#{sid}-sub', {{opacity:0,y:20}}, {{opacity:1,y:0,duration:0.4}}, {a+0.6})",
        ]
        if "mini" in cfg.get("title", {}):
            L.append(f"tl.fromTo('#{sid}-mini', {{opacity:0}}, {{opacity:1,duration:0.4}}, {a+1.0})")
    elif t == "wide":
        kb = sc.get("kenburns", {})
        s0, s1 = kb.get("scale", [1.15, 1.0])
        x0, x1 = kb.get("x", [-60, 60])
        n_chips = len(sc.get("chips", []))
        L += [
            f"tl.fromTo('#{sid}-img', {{scale:{s0},x:{x0}}}, {{scale:{s1},x:{x1},duration:{dur-0.55},ease:'none'}}, {a+0.15})",
        ]
        if n_chips:
            L.append(f"tl.fromTo('#{sid} .chip', {{opacity:0,y:18}}, {{opacity:1,y:0,duration:0.35,stagger:0.18}}, {a+0.7})")
    elif t == "phone_text":
        L += [
            f"tl.fromTo('#{sid}-phone', {{x:340,rotate:5,opacity:0}}, {{x:0,rotate:0,opacity:1,duration:0.7,ease:'back.out(1.3)'}}, {a+0.15})",
            f"tl.fromTo('.{sid}-pt', {{opacity:0,x:-46}}, {{opacity:1,x:0,duration:0.42,stagger:0.2}}, {a+0.4})",
        ]
    elif t == "split":
        L += [
            f"tl.fromTo('.{sid}-ph', {{y:200,opacity:0}}, {{y:0,opacity:1,duration:0.6,stagger:0.2,ease:'back.out(1.4)'}}, {a+0.15})",
            f"tl.fromTo('.{sid}-foot', {{opacity:0}}, {{opacity:1,duration:0.4}}, {a+0.7})",
        ]
    elif t == "carousel":
        imgs = sc["images"]
        n_img = len(imgs)
        iv = sc.get("interval") or (dur - 1.1) / n_img
        for k in range(1, n_img):
            tk = a + 0.5 + k * iv
            L += [
                f"tl.to('#{sid}-slide-{k-1}', {{x:-920,duration:0.55,ease:'power2.inOut'}}, {tk:.3f})",
                f"tl.fromTo('#{sid}-slide-{k}', {{x:920}}, {{x:0,duration:0.55,ease:'power2.inOut'}}, {tk:.3f})",
                f"tl.to('#{sid}-cap-{k-1}', {{opacity:0,duration:0.3}}, {tk:.3f})",
                f"tl.fromTo('#{sid}-cap-{k}', {{opacity:0}}, {{opacity:1,duration:0.3}}, {tk+0.15:.3f})",
                f"tl.to('#{sid}-dot-{k-1}', {{backgroundColor:'rgba(255,255,255,0.18)',duration:0.2}}, {tk:.3f})",
                f"tl.to('#{sid}-dot-{k}', {{backgroundColor:'{cfg['accent']}',duration:0.2}}, {tk:.3f})",
            ]
    elif t == "endcard":
        L += [
            f"tl.fromTo('#{sid}-flow', {{opacity:0,y:26}}, {{opacity:1,y:0,duration:0.55}}, {a+0.15})",
            f"tl.fromTo('#{sid}-url', {{opacity:0,y:22}}, {{opacity:1,y:0,duration:0.45}}, {a+0.65})",
            f"tl.fromTo('#{sid}-tag', {{opacity:0}}, {{opacity:1,duration:0.4}}, {a+1.05})",
        ]
    if not last:
        L.append(f"tl.to('#{sid}', {{autoAlpha:0, duration:0.4, ease:'power1.in'}}, {o-0.35})")
    return "\n".join(x for x in L if x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--gsap-src", default="/wiring/vendor/gsap.min.js",
                    help="GSAP 3.13+ 地址（带 easeReverse 的 vendor），默认复用 wiring 沙盘同源")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    scenes_html = "\n".join(scene_html(cfg, sc, i) for i, sc in enumerate(cfg["scenes"]))
    last_idx = len(cfg["scenes"]) - 1
    timeline = "\n".join(scene_tl(cfg, sc, i, i == last_idx) for i, sc in enumerate(cfg["scenes"]))
    total = max(sc["out"] for sc in cfg["scenes"])

    html = HTML.format(
        W=1280, H=720,
        zoom=cfg.get("width", 1280) / 1280,
        doc_title=cfg.get("doc_title", cfg.get("title", {}).get("main", "promo")),
        accent=cfg.get("accent", "#34d399"),
        scenes=scenes_html, timeline=timeline,
        total=total, gsap_src=args.gsap_src,
    )
    (out / "render.html").write_text(html, encoding="utf-8")

    fdir = out / "fonts"
    fdir.mkdir(exist_ok=True)
    for f in FONTS.glob("*.woff2"):
        shutil.copy(f, fdir / f.name)

    n = len(cfg["scenes"])
    print(json.dumps({
        "ok": True, "render": str(out / "render.html"),
        "scenes": n, "duration": total,
        "frames": int(round(total * cfg.get("fps", 30))),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
