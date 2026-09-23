# Skills 质量深度体检报告

> 生成日期：2026-09-24 · 分支：SKill · 基线：161 个 skill
> 复现：`python scripts/validate_skills.py`（错误阻断 CI，警告仅提示）

## 一、总体结论

| 维度 | 状态 | 说明 |
|------|------|------|
| 结构合规（SKILL.md/frontmatter/命名） | ✅ 已清零 | 2026-09-24 修复 10 个 frontmatter 问题 + 4 个目录重命名 |
| 索引一致性（目录↔README） | ✅ 已清零 | 11 个漏登记 + 1 个重复已修复，CI 持续拦截 |
| description 长度（30~1024 字符） | ✅ 已清零 | lark-approval / lark-attendance / public-skill / tencent-meeting-mcp / qclaw-text-file 已修复 |
| 触发路由边界 | 🟡 大部分明确 | 重叠域（新闻×5/搜索×3/简历×2/数据×2/自省×2）已加反触发 |
| 触发条件表述 | ✅ 已清零 | 60 个 skill 已补触发语（2026-09-24，三批次并行修补） |
| 正文规模（>500 行） | ⚠️ 9 条警告 | 违反渐进式披露原则 |
| 冗余文件（README/CHANGELOG） | ⚠️ 13 条警告 | 违反 skill-creator 分发规范 |

## 二、已修复清单（2026-09-24）

**description 过短（4）**：`lark-approval`(21→71) `lark-attendance`(18→66) `public-skill`(42→113) `tencent-meeting-mcp`(37→94) — 均补充触发场景与边界。

**description 过长（1）**：`qclaw-text-file`(1238→658) — 保留 write 拦截全部强制规则，详细规则正文已有重复，压缩不影响行为。

## 三、存量警告与处置建议（按优先级）

### P1 · description 缺触发条件（~~57~~ 60 个）— ✅ 已完成

2026-09-24 三批次并行修补 60 个 skill：保留原文追加具体触发句（含真实用户说法关键词），重叠域加反触发。修补中发现并修复 5 个引号未闭合缺陷（lark-calendar/base/contact/minutes/vc），已将「description 引号闭合」纳入校验脚本错误级检查。

### P2 · 正文过长（9 个）

| skill | 行数 | 建议 |
|-------|------|------|
| gh-cli | 2184 | 命令参考移至 references/ |
| github-skill | 2072 | 同上 |
| notion | 1370 | API 细节移至 references/ |
| weiyun | 690 | 拆分操作手册 |
| pdf | 658 | 上游官方包，随上游更新 |
| self-improving-agent | 643 | 拆分示例库 |
| lark-mail | 640 | 拆分 API 参考 |
| wx-cli-wechat-local-data | 580 | 拆分命令手册 |
| acad-paper-prompter / lark-slides | 544/517 | 提示词库移至 references/ |

**建议**：只拆自建 skill；上游官方包（pdf 等）保持原样以便跟进更新。

### P3 · 冗余文件（13 个）

`README.md`(11) / `CHANGELOG.md`(2)，多为上游包自带。
**建议**：新增贡献严格执行规范；存量上游文件保留（删除有信息损失且增加与上游的 diff），自建 skill 逐步清理。

## 四、防护机制现状

1. **本地**：`scripts/hooks/pre-commit`（`bash scripts/install-hooks.sh` 安装）
2. **CI**：`quality-check.yml` 在 push/PR 到 main/master/SKill 时运行，错误级检查阻断
3. **规范**：README「📝 Skill 贡献规范」五条

错误级检查（阻断）：SKILL.md 存在性、frontmatter 完整性、name=目录名、命名规范、索引一致、分类计数、总数一致、desc 长度 30~1024、大文件 >5MB。
警告级检查（提示）：触发条件缺失、正文 >500 行、冗余文件。
