---
name: promo-render
description: 确定性宣传片渲染管线。把「截图素材 + JSON 配置」变成 720p30 带 BGM 的 MP4 宣传片：渲染页生成 → __seek 逐帧采集 → ffmpeg 合成 → 程序化 BGM 灌轨。零剪辑软件、零外部素材、零版权风险，出片可复现。当用户说「做宣传片」「生成 promo 视频」「给系统/项目录一段介绍视频」「确定性渲染出片」「视频加 BGM」「批量出片」「渲染流水线」或要求「把截图变成视频」时使用。适合 10–40s 的产品演示/赛题展示/操作回顾短片。
---

# promo-render · 确定性宣传片流水线

版本：v1.0.0 ｜ 维护：NEC（new-energy-coder-club）｜ 案例：https://tower.newenergycoder.club（影像区 CAM-07）

## 核心思想

不用剪辑软件，用**浏览器确定性渲染**：一张 HTML 渲染页承载 GSAP 暂停时间轴，每一帧通过 `__seek(t)` 精确寻址，Playwright 逐帧截图，ffmpeg 合成 MP4。同一配置永远渲出同一视频（改一帧只改配置）。

```
config.json ──▶ build_render_page.py ──▶ render.html (+自托管字体)
                                              │
                          静态服务 + capture.py（__seek 逐帧截图 × fps×秒数）
                                              │
                    encode.sh（ffmpeg 合成，可选 synth_bgm.py 音轨灌入）
                                              │
                                    promo.mp4（720p30 · H.264 · AAC）
```

## 调用仓库（生态集成关系）

| 仓库 | 角色 | 调用方式 |
|---|---|---|
| `new-energy-coder-club/cyber-gsap-intro` | **出片落地站**（Vite+React+GSAP，tower.newenergycoder.club） | MP4 放 `public/videos/`；在 `src/components/ShowcaseSection.tsx` 的 `MAIN_FEEDS/ANGLE_FEEDS/MES_PROMO` 注册；`vercel --prod` 上线 |
| `robo-tower-demo` | 上游渲染思想来源（capture.js + encode.sh 确定性管线）与素材源（`dist/*.mp4` 机器/T1 影像） | 复刻其「逐帧采集→ffmpeg」模式；其 `dist/` 视频经本 Skill 站点副本分发 |
| `wiring-animation` | GSAP vendor 提供方 | `--gsap-src /wiring/vendor/gsap.min.js`（3.13+，含 easeReverse） |
| `new-energy-coder-club/new_energy_coder_club` | **本 Skill 宿主仓库**（skills/promo-render/） | 团队成员 clone 后软链/拷贝到本地 skills 目录即被 Kimi 自动发现 |
| `416 MES`（mes.newenergycoder.club） | 素材生产系统 | 操作截图来源（建档/标签/入库/查询全流程） |

落地工作流（以 NEC 战队为例）：
真实系统截图 → promo-render 出片 → `public/videos/` → 影像区注册 → `vercel --prod` → tower.newenergycoder.club 全球可访问。

## 环境前置（一次性）

| 依赖 | 版本 | 安装 |
|---|---|---|
| Python | ≥3.10 | 系统自带或 brew |
| Playwright + Chromium | 最新 | `pip3 install playwright && python3 -m playwright install chromium` |
| numpy | ≥1.24 | `pip3 install numpy` |
| ffmpeg | ≥5 | `brew install ffmpeg` |
| GSAP | ≥3.13 | 用 `--gsap-src` 指向任意 gsap.min.js（本生态用 wiring 沙盘同源 vendor） |

国内网络提示：`fonts.googleapis.com` 不可达，本 Skill 已自托管 Orbitron/Share Tech Mono 两份 woff2（`assets/`），生成时自动拷贝，渲染全程不需要外网。GitHub 克隆/下载受阻走 `https://gh-proxy.com/https://github.com/...` 镜像。

## 零基础用法（对着 Kimi 说人话即可）

在 Kimi Code / kimi CLI 里，把素材目录和诉求说清楚，例如：

```
用 promo-render skill 给我做一个 18 秒宣传片：
- 素材截图在 ~/shots/system/（5 张手机截图 + 1 张宽横幅）
- 主题「XX 系统操作回顾」，主色 #00f0ff
- 结构：片头 → 横幅展示 → 三步操作各一幕 → 收尾带网址 xx.example.com
- BGM 要燃一点（100bpm），出到 ~/out/promo.mp4
```

Kimi 会替你：写 `config.json` → 起本地静态服务 → 跑三步脚本 → 质检帧 → 交付 MP4。
你要做的只有两件：**准备截图**、**验收成片**。

## 标准流程（Agent 执行口径）

```bash
# ① 写配置（参照 reference/config.example.json）
$EDITOR config.json

# ② 生成渲染页（字体自动拷贝到 out/fonts/）
python3 scripts/build_render_page.py config.json -o ./out --gsap-src /wiring/vendor/gsap.min.js

# ③ 起静态服务（素材路径需可访问；cyber-gsap-intro 项目放 public/ 下由 Vite 伺服）
python3 -m http.server 8899 -d ./out &

# ④ 逐帧采集（duration = 配置中最晚 scene.out）
python3 scripts/capture.py --url http://localhost:8899/render.html \
    --duration 20 --fps 30 --out /tmp/promo-frames

# ⑤（可选）合成 BGM
python3 scripts/synth_bgm.py --duration 48 --bpm 80 --key Am --out /tmp/bgm.wav

# ⑥ 合成出片（带 BGM 灌轨，时长自动对齐视频）
bash scripts/encode.sh /tmp/promo-frames ./promo.mp4 /tmp/bgm.wav 20 30
```

## config.json 全字段速查

顶层字段：

| 字段 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `width` / `height` | 否 | 1280×720 | 画布分辨率（站点影像区为 16:9） |
| `fps` | 否 | 30 | 采集帧率（影院长片感 24，电竞感 60） |
| `accent` | 否 | `#34d399` | 全局主色（#RRGGBB），驱动 HUD 边框/字幕/光晕 |
| `title{}` | 是* | — | *`title` 场景存在时必填：`kicker/main/sub/mini` |
| `scenes[]` | 是 | — | 分镜数组，按 `at` 排序，至少 2 幕 |
| `bgm{}` | 否 | enabled:false | `enabled/duration/bpm/key(Am/Em/Cm)/mux_seconds` |

五种场景类型（公共字段：`at` 入点、`out` 出点，单位秒；相邻幕建议重叠 ~0.3s，淡入淡出 0.4s 自动处理）：

| type | 必填字段 | 可选字段 | 画面 |
|---|---|---|---|
| `title` | —（用顶层 `title{}`） | — | 居中大字片头，自带 RGB 分离抖动 |
| `wide` | `src`, `caption` | `kenburns{scale:[a,b],x:[a,b]}`, `chips[]`（可用 `<b>`）, `footnote` | 1100px 宽横幅（网页横屏截图），支持 Ken Burns 推拉横移 |
| `phone_text` | `src`, `badge`, `headline`, `points[]` | — | 左侧编号要点（右滑入）+ 右侧 300×592 手机截图（带回旋入场） |
| `split` | `left`, `right`, `caption`, `footnote` | — | 双 270×520 手机截图错峰升起，上下字幕条 |
| `endcard` | `flow`, `url`, `tag` | — | 居中流程行 + 大网址 + 落款（全程无淡出，定格到片尾） |

时长预算参考：片头 ≤2s / 单内容幕 3–3.5s / 收尾 2.5s。20s 视频 ≈ 7 幕。

## 站点集成（cyber-gsap-intro 口径）

```tsx
// src/components/ShowcaseSection.tsx
const MES_PROMO: Feed = {
  cam: 'CAM-08', label: 'XXX PROMO // 主题',
  src: '/videos/xxx-promo.mp4',
  accent: 'emerald',   // cyan | magenta | amber | emerald
  rec: '20S',
}
```

部署：`npm run build && vercel --prod`（约 15s，自动 alias 到 tower.newenergycoder.club）。

## 优化旋钮（按需求调）

| 目标 | 调什么 |
|---|---|
| 节奏更快 | `bpm` 80→100；`energy` 0.5→1（鼓组加重） |
| 更氛围 | `--energy 0`（纯 pad+arp，无鼓） |
| 换调性 | `--key Em`（暗色小调）/ `--key Cm`（更深沉） |
| 镜头运动更强 | `kenburns.scale` 差拉大（1.2→1.0）、`x` 行程 ±100+ |
| 静帧展示 | 删 `kenburns`，画面即定格 |
| 字幕更久可读 | 单幕 `out-at` ≥ 3s；`footnote` 别超 40 字 |
| 文件更小 | `encode.sh` 里 `-crf 18` → 23；要更清晰反向调 |
| 循环无缝 | BGM `--duration` 设成视频整数倍；视频首尾幕都用纯黑底 |

## QA 清单（出片必查）

- [ ] `ffprobe`：时长 = Σ 配置帧数/fps；流 = video(h264) [+ audio(aac)]
- [ ] 抽 5 帧（片头/各幕中点/收尾）肉眼检查：无文字溢出、无字体回退（标题必须是 Orbitron）
- [ ] 收尾页网址/标签无截断（`white-space:nowrap` 大行注意字号 ≤30px）
- [ ] 音画：BGM 在片头淡入、收尾淡出；视频循环无爆音
- [ ] 素材版权：截图为自有系统/已授权素材

## 已知坑（血泪记录）

1. **Playwright 走代理时 localhost 必须 bypass**：全局代理会让 localhost 也进代理导致页面卡死；本 Skill 的 capture.py 默认直连（字体已自托管，无需外网）。
2. **`<video preload="metadata">` + autoplay 在部分浏览器不自动播**：站点内嵌 LOOP 一律 `preload="auto"`（文件小无所谓）。
3. **iframe 指目录路径**：Vite dev 下 `/wiring/` 会回退 SPA，必须 `/wiring/index.html`。
4. **CSS 动画不可 seek**：渲染页内所有动效必须走 GSAP 时间轴（`__seek` 才能定位）；CSS keyframes 只在实时预览有效，采集会静止。
5. **Google Fonts 国内不可达**：渲染页一律用自托管 woff2（assets/ 已带，生成时自动拷贝）。
6. **首幕必须淡出**：scene0 也要配 `out`，否则与第二幕叠影（v1.0.0 已修复生成器默认行为：除末幕外全部自动淡出）。

## 变更记录

- v1.0.0（2026-10-01）：首个发布。由 416 MES 20s 宣传片实战封装；修复首幕淡出缺失与短时长 BGM 的 ADSR 溢出问题。

## 文件结构

```
promo-render/
├── SKILL.md                       ← 本文件
├── scripts/
│   ├── build_render_page.py       # config.json → render.html（分镜/字幕/时间轴生成）
│   ├── capture.py                 # Playwright __seek 逐帧采集
│   ├── encode.sh                  # ffmpeg 合成 + BGM 灌轨
│   └── synth_bgm.py               # numpy 程序化 BGM（bpm/key/energy 可调）
├── reference/
│   └── config.example.json        # 20s MES 宣传片完整配置样例
└── assets/                        # 自托管 woff2 ×2（Orbitron 900 / Share Tech Mono）
```

## 案例

- `tower.newenergycoder.club` 影像区 CAM-07《416 MES · 赛题二宣传片》：20s / 7 幕 / Am 80bpm，即由本管线出片；渲染演示页 `/tools/skill-demo/render.html` 为 example 配置实时产物。
