# 贡献指南（Contributing）

## 平台分工

- **GitHub**：Issue、Pull Request、CI 和正式仓库规范的主入口。
- **Gitee**：国内访问镜像；如镜像与 GitHub 不一致，以 GitHub 为准。
- **飞书**：课程、活动与社区知识库；贡献流程冲突时，以本文件和仓库文档为准。

主仓库：[necc-hub/new_energy_coder_club](https://github.com/necc-hub/new_energy_coder_club)。

## 第一次贡献

1. 阅读[新人 60 分钟上手](docs/start-here/60min.md)，跑通无硬件 Demo。
2. 在 GitHub Issues 中选择带 `good first issue` 标签的任务，并在 Issue 下说明预计完成时间。
3. Fork 后创建分支，分支名建议使用 `docs/<issue-id>-<简述>`、`fix/<issue-id>-<简述>` 或 `feat/<issue-id>-<简述>`。
4. 尽早提交 Draft PR，在描述中关联 Issue，并写清验证方式与待确认事项。
5. Review 通过后由维护者合并。不要直接在 PR 中混入与任务无关的历史目录重构。

文档修改、图纸整理、教程复盘与代码贡献同等重要。

## 提交与验收

- Commit 使用 Conventional Commits，例如 `docs: ...`、`fix: ...`、`feat: ...`、`ci: ...`。
- 新功能需包含最小可运行 Demo 或验证步骤；不要以“理论上可行”代替实际验证。
- 修改文档时检查内部链接、标题层级、命令路径和输出；结尾应给出下一步。
- 项目 README 需维护状态、负责人、最后验证日期、复现入口和下一步，格式见[项目索引](projects/README.md)。
- 图片、图纸、PDF 和压缩包遵循[仓库资产规范](docs/contribute/repository-assets.md)。

建议验证命令：

```bash
python3 docs/nec-quickstart/hello_nec.py --seconds 2
python3 .github/scripts/check_links.py README.md projects/README.md competitions/README.md
```

如果改动了其他 Markdown 文件，也把它们作为参数追加到链接检查命令后。CI 会对本次改动的 Markdown 文件运行 markdownlint 和内部链接检查。

## 线下 A416 与线上 NEC

- 线下成员同样通过 GitHub PR 沉淀可复用资产；硬件无法远程运行时，应在 PR 中注明实际验证环境。
- 新人推荐先掌握 Markdown、Git/GitHub 基础与飞书知识库使用，再进入具体技术栈。
- 提问时提供目标、已尝试步骤、完整报错和相关文件路径；不要只写“运行不了”。
