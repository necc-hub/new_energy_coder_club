# 项目模板（Project Templates）

模板用于统一项目信息和最小验证方式，不要求每个项目都创建一套庞大目录。

## 可用模板

| 模板 | 适用场景 | 说明 |
|---|---|---|
| [通用项目 README](../../docs/templates/README_PROJECT_TEMPLATE.md) | 所有新项目 | 首选；包含状态、负责人、验证、Roadmap 和许可证字段 |
| [AI 项目模板](./ai_project_template/README.md) | 数据分析、模型训练 | 提供 Python 项目结构示例；部分源码和文档需按项目补充 |
| [嵌入式项目模板](./embedded_project_template/README.md) | MCU、智能硬件、通信 | 提供硬件、构建、烧录和测试章节示例 |

机器人项目使用通用项目 README，并按实际需要添加 ROS 包、固件、硬件和模型目录。目前没有独立的机器人或通用目录模板，请不要再引用不存在的路径。

## 使用方法

### 1. 从仓库根目录复制模板

```bash
cp docs/templates/README_PROJECT_TEMPLATE.md projects/your-project/README.md
```

AI 或嵌入式项目可参考相应目录中的详细章节，但只复制实际需要的文件。模板中的 `your-project`、`<项目名称>`、`@xxx` 等占位符必须替换。

### 2. 先写最小验证

README 顶部至少填写：

- 状态：`active` / `maintenance` / `archived` / `待复核`
- 负责人：GitHub ID 或“待认领”
- 最后验证：实际日期；未运行则写“未记录”
- 复现入口：一条实际可运行命令，或明确标注“待补最小 Demo”
- 下一步：一个可交付任务或 Issue

不要把示例命令、规划中的目录或硬件指标写成已经实现的功能。

### 3. 提交前检查

```bash
git status --short
python3 .github/scripts/check_links.py projects/your-project/README.md projects/README.md
npx --no-install markdownlint --config .github/markdownlint.json -- projects/your-project/README.md projects/README.md
```

新项目还需更新[项目总索引](../README.md)。图片、图纸、PDF 和数据集遵循[仓库资产规范](../../docs/contribute/repository-assets.md)。

## 模板维护

- 模板应与当前贡献流程、主许可证和 GitHub 组织保持一致。
- 新增模板必须提供自身可访问的 README，不能只在索引里创建空链接。
- 删除模板示例中的失效相对链接；指向真实参考资料时使用完整 URL。
- 示例配置和示例代码要注明“示例”，不能替代实际运行验证。

最后复核：2026-11-25。
