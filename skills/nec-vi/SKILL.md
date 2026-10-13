---
name: nec-vi
description: NEC 战队（常州工学院 New Energy Coder）品牌视觉规范。当用户需要设计海报、PPT、网页、视频片头、周边等任何 NEC 对外视觉物料时使用，确保队标、标准色、字体、安全空间符合 VI 手册。触发词：NEC 海报、队标使用、品牌色、VI 规范、nec-vi、做一张战队宣传图。
---

# NEC 主视觉 VI 规范（nec-vi）

> 单一事实来源：《NEC 主视觉 VI 规范手册 V1.0》，线上素材库（永远最新）：https://hub.newenergycoder.club/brand/
> 品牌口号：**BUILT TO DAWN · 为黎明而造** · KEEP BUILDING
> 视觉母题：工程蓝图 × 破晓地平线。调性：工程感、精确、冷静、向上。

## 标准色（十六进制，禁止目测取色）

| 角色 | 色名 | 值 | 用途 |
|---|---|---|---|
| 品牌主色 | NEC 蓝 | `#1A2FA0` | 标志主色、主按钮、核心强调 |
| 深色底 | NEC 藏青 | `#141B5E` | 深色背景、标题强调底 |
| 正文墨青 | 墨青 | `#0B1033` | 浅色底上的标题/正文 |
| 强调 | 破晓青 | `#1FA9E8` | 交互、亮点、数据高亮 |
| 辅助 | 破晓浅青 | `#4FC3F7` | 渐变伴侣、次级强调 |
| 浅底 | 雾灰蓝 | `#F4F6FB` | 浅色区块背景 |
| 次级文字 | 灰 | `#5A6472` | 说明文字 |
| 描边 | 线灰 | `#D9DFF0` | 分割线/描边 |

品牌蓝渐变：`linear-gradient(180deg, #2B3FC2 0%, #10277E 100%)`；地平线装饰线：`#1FA9E8 → #4FC3F7 → 透明` 横向渐变。

## 字体

- 中文：**思源黑体（Source Han Sans SC）** 优先，微软雅黑兜底
- 西文/数字：Arial / Helvetica
- 大标题/口号：Arial Black
- 编号/代码/数据：IBM Plex Mono / Consolas 等宽

## 队标使用

- 优先矢量 SVG，禁止使用旧版 PNG。版本选择：浅色底用 `nec-logo.svg`；深色底用 `nec-logo-white.svg`；单色印刷/雕刻用 `nec-logo-mono.svg`；封面页眉用横版组合 `nec-lockup-h.svg`（深底 `-white` 版）。
- 安全空间：标志四周预留 ≥ 1 个 N 字笔画宽（约标志高度 18%）净空，任何元素不得进入。
- 最小尺寸：屏幕单独标志宽 ≥ 32px；横版组合高 ≥ 24px；印刷宽 ≥ 12mm；刺绣/雕刻 ≥ 25mm（用单色版）。
- 横版组合中的文字间距固定，**不可重排、不可换字体、不可加装饰线**。

## 使用禁忌

1. 禁止拉伸、旋转、倾斜、改色、加阴影/描边/渐变覆盖标志
2. 禁止在杂乱照片亮区直接用彩色标志（用反白版或加藏青衬底）
3. 禁止把 NEC 蓝替换为相近蓝（如纯蓝 #0000FF）
4. 禁止非规范字体（宋体/楷体/综艺体等）用于正式物料

## 素材获取

全部矢量文件与手册在线获取：`https://hub.newenergycoder.club/brand/`（含 nec-logo 系列、lockup、favicon、PPT 模板、nec-tokens.css）。网页开发直接 `<link rel="stylesheet" href="/brand/nec-tokens.css">` 使用 `--nec-*` 变量。
