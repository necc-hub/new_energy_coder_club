# Good First Issue：新人任务指南

> 你不需要“很强”才能贡献。你只需要从一个有明确验收标准的小任务开始。

## 找到真实任务

在 GitHub 查看[所有带 `good first issue` 标签的开放任务](https://github.com/necc-hub/new_energy_coder_club/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。

文档任务通常还带有 `documentation` 标签；代码缺陷使用 `bug`，新功能使用 `enhancement`。难度、预计耗时、涉及方向和带教人写在 Issue 正文，不依赖尚未创建的标签。

一个合格的新人任务必须包含：

- 2 小时以内可完成，不依赖昂贵硬件
- 具体的修改文件路径
- 可勾选的交付标准
- 可复制的验证命令或检查方法
- 带教人，或“维护者认领后指定”的明确说明

## 认领与提交

1. 在 Issue 下评论：“我想认领这个任务，预计在 X 天内提交 PR。”等待维护者确认，避免重复劳动。
2. 创建分支：`gfi/<issue-id>-<short-title>`。
3. 尽早提交 Draft PR，描述中写 `Fix #<issue-id>`，并列出已完成与待确认项。
4. 在本地执行 Issue 给出的验证命令；不要只写“已检查”而没有实际输出。
5. Review 通过后由维护者合并。若无法继续，请在 Issue 中说明并释放任务。

## 统一验收口径

### 文档任务

- 内部链接有效，关键步骤和路径可复制。
- 结构清晰，包含必要的环境、输出与至少一条常见问题。
- 对未实际运行的硬件流程明确标注“未验证”，不能伪造结果。

### 代码任务

- 提供最小复现或最小验证，默认行为不被意外改变。
- 跑通 `python3 docs/nec-quickstart/hello_nec.py --seconds 2`（与任务无关的硬件项目可在 PR 中说明替代验证）。
- PR 描述写清修改内容、验证命令和实际结果。

## 维护者发布任务

使用 Issue 模板 **Good first issue**。模板会强制填写背景、文件、完成标准、验证方法、耗时和带教人。不要把“学习某技术”“优化项目”“完善文档”这类没有交付物的条目直接标为新人任务。

首批任务已经发布，见[首批 Good First Issue 任务及 Issue 链接](../contribute/good-first-issue-backlog.md)。后续新增任务也应在此登记，完成时补充交付 PR 链接。

## 提问格式

- 我在运行：完整命令
- 我的环境：Windows/macOS/Linux、Python/编译器版本
- 实际结果：完整报错或截图
- 我已尝试：步骤与结果
- 相关文件：仓库内路径或 Issue/PR 链接
