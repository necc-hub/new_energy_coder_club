---
name: nec-ppt
description: NEC 战队答辩/汇报 PPT 模板与排版规范。当用户需要制作 NEC 答辩 PPT、赛季汇报、路演幻灯片、技术方案演示时使用，自动套用官方模板（NEC-PPT-Template_V1.0.pptx）的版式、字体与品牌色。触发词：NEC PPT、答辩 PPT、汇报幻灯片、nec-ppt、路演模板。
---

# NEC PPT 模板与排版规范（nec-ppt）

> 官方模板：https://hub.newenergycoder.club/brand/NEC-PPT-Template_V1.0.pptx
> 色彩与字体细节以 nec-vi Skill /《NEC 主视觉 VI 规范手册》为准，本 Skill 只管 PPT 落地。

## 模板使用

1. 从上述地址下载 `NEC-PPT-Template_V1.0.pptx`，在其副本上制作，不要从空白演示文稿开始。
2. 模板页型：封面（横版 lockup + 藏青底）/ 目录 / 章节页 / 图文内容页 / 数据页 / 结尾页（口号 BUILT TO DAWN）。
3. 生成或修改 .pptx 时用 python-pptx 等工具继承模板母版，不要覆盖主题色。

## 字体规则（模板已内置，改动时遵守）

- 中文一律**思源黑体（Source Han Sans SC）**，并确保东亚字体（a:ea）显式设置，避免 PowerPoint 回退默认中文字体
- 西文标题 Arial Black、正文 Arial；等宽场景（编号/代码/数据）Consolas
- 字阶建议：封面主标 40-54pt / 章节页 32-40pt / 页标题 24-28pt / 正文 14-18pt / 注释 ≥10.5pt

## 配色规则

- 深色页：藏青 `#141B5E` 底 + 反白标志 + 白色标题 + 破晓青 `#1FA9E8` 强调
- 浅色页：白/雾灰蓝 `#F4F6FB` 底 + 墨青 `#0B1033` 正文 + NEC 蓝 `#1A2FA0` 强调
- 数据图表系列色顺序：`#1A2FA0` → `#1FA9E8` → `#4FC3F7` → `#5A6472`，禁止彩虹配色
- 每页强调色不超过 1 处主强调

## 版式禁忌

- 每页一个核心观点；文字行数 ≤ 8 行的内容页优先
- 禁止标志变形/改色/压字；安全空间 ≥ 标志高度 18%
- 禁止使用模板外主题色与宋体等非规范字体
- 对外场合结尾页保留口号：**BUILT TO DAWN · 为黎明而造**
