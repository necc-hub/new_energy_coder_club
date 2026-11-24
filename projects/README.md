# 项目目录（Projects）

这里汇总 NEC 的机器人、嵌入式、工业控制与科研项目。竞赛资产请查看[竞赛索引](../competitions/README.md)。

> 本页最后复核：2026-11-24。状态表示当前文档维护情况，不代表硬件已经通过运行验收；未确认的信息统一标为“待复核”，避免沿用历史状态造成误导。

## 项目索引

| 项目 | 方向 | 文档状态 | 最近验证 | 入口与下一步 |
|---|---|---|---|---|
| 流体工作站 | 工业控制 / 树莓派 | 待复核 | 未记录 | [项目说明](./5axis-fluid-workstation/README.md)；完整代码见文内主仓库 |
| 星闪手柄 | NearLink / WS63 | 待复核 | 未记录 | [资料与开发指南](./星闪手柄/readme.md)；先补环境版本与最小 Demo |
| 人形机器人 | 机器人 / 开源资料 | 资料索引 | 2026-11-24（仅链接结构） | [资料入口](./robotics/人形机器人/Readme.md)；需补项目目标与可复现基线 |
| 飞控通讯 | PX4 / MAVLink | 待复核 | 未记录 | [历史进度](./robotics/飞控通讯/readme.md)；确认 2025 年交付结果并归档 |
| 机器狗 K230 | K230 / ESP32 | 示例已入库 | 未记录 | [代码与学习路线](./robotics/机器狗-k230/README.md)；先验证一个感知 Demo |
| 科研横向项目 | 产学研 / 技术验证 | 混合归档 | 未记录 | [项目总览](./research-horizontal/Readme.md)；逐项补负责人和结论 |
| 项目模板 | AI / 嵌入式 | 可复用模板 | 2026-11-24（仅结构） | [模板目录](./templates/README.md)；新项目从模板开始 |

## 按技术栈查找

- **机器人**：[机器人项目总览](./robotics/README.md)
- **嵌入式与 NearLink**：[星闪手柄](./星闪手柄/readme.md)、[机器狗 K230](./robotics/机器狗-k230/README.md)
- **工业 AI 与控制**：[流体工作站](./5axis-fluid-workstation/README.md)
- **产业合作与技术调研**：[科研横向项目](./research-horizontal/Readme.md)

## 项目维护约定

每个活跃项目的 README 顶部应维护以下字段：

```text
状态：active / maintenance / archived / 待复核
负责人：GitHub ID 或“待认领”
最后验证：YYYY-MM-DD；未验证则明确写“未记录”
复现入口：一条命令或一份具体文档
下一步：一个可交付任务或 Issue
```

- `active`：有明确负责人和近期可验证进展。
- `maintenance`：不主动扩展功能，但会修复文档和关键问题。
- `archived`：历史资产保留，不再承诺更新。
- `待复核`：历史状态尚未确认，不应直接对外宣传为“进行中”。

新增项目时，从[项目模板](./templates/README.md)创建 README，并更新本页索引。图片、图纸、压缩包等大文件遵循[仓库资产规范](../docs/contribute/repository-assets.md)。

## 参与贡献

- 首次参与先阅读[新人 60 分钟上手](../docs/start-here/60min.md)和[贡献指南](../CONTRIBUTING.md)。
- 在 GitHub Issues 中认领带 `good first issue` 标签的任务；没有合适任务时，可提交“补充项目复现步骤”的 Issue。
- 提交 PR 时写明修改内容、验证方式和仍需负责人确认的事项。
