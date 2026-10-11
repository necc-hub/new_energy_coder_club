---
name: nec-kv-design
description: 常州工NEC 主视觉（KV）设计与出图系统。基于「BUILT TO DAWN / KEEP BUILDING / 为黎明而造」VI 体系，用自包含 HTML 模板 + 无头 Chrome 渲染，产出横版 16:9、竖版海报、方版社媒、飞书工作台宣传栏（1380×450）等规格的品牌物料 PNG。当用户说"做 NEC 主视觉"、"出 NEC 海报"、"飞书宣传栏"、"NEC banner"、"BUILT TO DAWN 物料"、"更新 hub 主视觉"时使用。
---

# nec-kv-design — 常州工NEC 主视觉设计系统

## 设计规范（VI 速查，改动时必须保持一致）

- **Slogan**：BUILT TO DAWN（主）/ KEEP BUILDING（辅）/ 为黎明而造（中文）
- **主色**：亮蓝 `#1FA9E8`、浅蓝 `#4FC3F7`；深色：藏青 `#141B5E`、墨色 `#0B1033`；白底
- **纹理**：蓝图网格（大格 `rgba(31,169,232,.13)`，小格 `rgba(31,169,232,.05)`）
- **字体**：英文 Archivo 900（回退 Arial Black）；中文 Noto Sans SC 900（回退微软雅黑）；标注 IBM Plex Mono
- **核心图形**：破晓地平线（DAWN LINE，3-4px 青色横线）+ 刻度太阳（描边圆 + 虚线内环 + 准星 SVG）
- **固定元素**：四角套准十字 / 顶部 mono 图签 / 底部品牌锁（KEEP BUILDING▮ + N Logo + 常州工NEC in CIT + newenergycoder.club + 渐变底线）
- Logo 源文件：`assets/nec-logo.png`（蓝色立体 N）

## 工作流（两步出图）

```bash
# 1. 注入 Logo，生成自包含 HTML 到 dist/
python scripts/build.py            # 全部；或 build.py kv / build.py feishu

# 2. 无头 Chrome 逐画板截图为 PNG（需本机有 Chrome 或 Edge）
bash scripts/render.sh             # 1x；SCALE=2 bash scripts/render.sh 出 2 倍印刷图
```

## 画板清单（模板 → 规格 → 用途）

| 模板 | board 参数 | 规格 | 用途 |
|---|---|---|---|
| `templates/kv_template.html` | `h` | 1920×1080 | 横版主 KV：PPT 封面 / 演示横幅 |
| 同上 | `v` | 1080×1920 | 竖版海报 / 展架 / 推文头图 |
| 同上 | `s` | 1080×1080 | 方版社媒 / 头像 |
| `templates/feishu_banner_template.html` | `f1` | 1380×450 | 飞书宣传栏 A 浅色蓝图版（推荐） |
| 同上 | `f2` | 1380×450 | 飞书宣传栏 B 深色科技版 |
| 同上 | `f3` | 1380×450 | 飞书宣传栏 C 极简功能版 |

浏览器直接打开 `dist/index.html`（或 `feishu_banner.html`）可预览全部画板；`?board=h|v|s|f1|f2|f3` 单看一版。

## 改版式 / 文案

1. 编辑 `templates/*.html`（CSS 按画板分区，注释标明 H/V/S 或 F1/F2/F3），**不要**改生成出的 `dist/*.html`。
2. 重跑两步工作流。
3. **每次改完必须截图回读检查碰撞**：标题与太阳/地平线、品牌锁与圆弧是历史高发碰撞点（参考：太阳底缘距底部品牌锁 ≥30px；地平线与中文副标垂直间距 ≥40px）。

## 部署到 hub.newenergycoder.club（可选）

门户源码在 `nec-hub/public/index.html`（Cloudflare Worker 静态资产）。把 Hero 区按本 VI 改写后：

```bash
# 关键：Cloudflare API 的 IPv4 被阻断时必须走 IPv6，否则 fetch failed
NODE_OPTIONS="--dns-result-order=ipv6first" wrangler deploy
# 若命令挂住不退：查 %APPDATA%/xdg.config/.wrangler/logs 最新日志，
# 出现 "Current Version ID" 即部署成功（挂住只是遥测上报失败）。
# 验证：curl https://hub.newenergycoder.club/api/health 与首页源码关键字
```

## 注意

- 出图依赖 Google Fonts（Archivo / IBM Plex Mono / Noto Sans SC），离线时自动回退系统字体，版式不变但字重观感略降。
- Chrome 无头截图写不进 OneDrive 同步目录时，先截到 `$TEMP` 再复制回来。
- 印刷场景用 `SCALE=2` 出 2 倍图，或拿 `dist/*.html` 直接交付设计/打印店。
