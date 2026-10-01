---
name: deterministic-render-pipeline
description: 确定性 Web 场景（Three.js/Canvas/DOM）无头逐帧采集成片管线：__seek/__ready 页面协议、playwright 采帧、ffmpeg 多视角多风格出片、片尾卡 concat、端口自愈与并行会话安全。当用户要求给代码生成的场景/动画"出片、重渲、渲染成 mp4、多视角视频、换风格出片、加片尾卡、逐帧截图质检"，或搭建同款确定性渲染管线时使用。
---

# 确定性渲染出片管线

把"代码生成的场景"稳定变成 mp4 的工程方法。核心思想：**渲染确定性**——同一帧号永远得到同一画面，采帧与编码分离。

## 四条铁律（建场景时就要遵守）

1. **页面协议**：入口页暴露 `window.__seek(t)`（把场景推到绝对时间 t 秒，幂等）和 `window.__ready === true`（资源加载完）。不用 `requestAnimationFrame` 驱动进度，动画状态是 t 的纯函数。
2. **时间轴纯函数**：所有动画状态（位置/透明度/相机）来自 `timeline.js` 式的纯函数，可用 `node --test` 单测；不要散落在渲染循环里。
3. **场地数据单一真相**：布局坐标集中在一个 `FIELD` 常量对象，测试逐值锁定；改布局先改 FIELD 再改测试。
4. **运动约束进测试**：如"0.1s 采样位移 < N 单位"，防止改路径后出现瞬移。

## 出片流程

复制 `scripts/` 四个模板到项目的 `render/`，按需微调（页面 URL 参数名、时长、分辨率都在文件头）：

| 文件 | 作用 |
|---|---|
| `capture.js` | playwright 无头逐帧截图，`__seek(i/fps)` 步进 N 帧 → `帧目录/%04d.png` |
| `encode.sh` | ffmpeg 把帧目录封装成 720p H.264 mp4（帧数不足 360 拒绝封装） |
| `card.js` | 片尾卡采帧：加载独立 endcard 页同样 `__seek` 步进（90 帧=3s） |
| `render_all.sh` | 一键全量出片驱动：起服务→多视角采帧→逐条封装→concat 片尾卡 |

标准命令序列：

```bash
python3 -m http.server 8123                          # 终端 1：项目根静态服务
node render/capture.js frames                        # 主视角 360 帧（12s@30fps）
bash render/encode.sh dist/base12.mp4 frames         # 封装 12s 正片
node render/card.js                                  # 片尾卡 90 帧 → frames-card/
ffmpeg -y -framerate 30 -i frames-card/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 /tmp/card.mp4
ffmpeg -y -i dist/base12.mp4 -i /tmp/card.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1[out]" -map "[out]" -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart dist/final.mp4
```

多视角/多风格用环境变量传给 capture.js（拼到页面 URL query）：

```bash
CAPTURE_VIEW=top node render/capture.js frames-top            # ?view=top
CAPTURE_STYLE=blueprint node render/capture.js frames-bp      # ?style=blueprint
```

页面侧用 `new URLSearchParams(location.search)` 读取并切换相机/配色。

## 坑（都是血泪）

- **并行会话杀端口**：多 agent 同机工作时，别的会话可能 `lsof -ti:8123 | xargs kill -9` 抢端口。`render_all.sh` 的 `ensure_server` 已内置：高位端口（8190+）+ 每次采帧前探活 + 死了自动换端口重起 + trap 退出清理。不要裸奔 `python3 -m http.server`。
- **函数前导 env 会泄漏**：bash 里 `VAR=x func` 对自定义函数会把 VAR 留在当前 shell，污染后续调用——函数内用子 shell `( export VAR=...; node ... )`。
- **帧目录残留**：重渲前 `rm -rf` 帧目录，否则中断的旧帧会被 encode.sh 混进去。
- **共面闪烁**：贴地薄板微抬 3mm（0.003）；材质 transparent 仅在需要时开启。
- **MP4 规范**：必须 `-pix_fmt yuv420p`，否则部分播放器绿屏。

## 改动后重渲清单

1. 改文案/布局/配色 → `npm test` 全绿 → 全量重渲所有视角（几何改动影响每条片）。
2. 只改标注/字幕样式 → 只重渲受影响的风格或视角。
3. 抽帧质检：`ffmpeg -ss <t> -i out.mp4 -frames:v 1 qa.png`，对照需求方给的参考图逐张比对，再交付。
4. 交付前 `ffprobe` 确认时长（正片+片尾卡=15s 之类）与 1280×720。

## 依赖

node ≥ 20、`playwright`（`npx playwright install chromium`）、ffmpeg、`python3`。测试用 `node --test`（零依赖）。
