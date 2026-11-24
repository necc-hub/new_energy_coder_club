# 首批 Good First Issue 任务

> 已于 2026-11-24 发布到 GitHub，统一带有 `good first issue` 标签。认领前先在对应 Issue 下评论预计完成时间；任务完成后由维护者关闭 Issue，并在此保留交付 PR 链接。

## 通用提交要求

```bash
npm ci --ignore-scripts --no-audit --no-fund
npx --no-install markdownlint --config .github/markdownlint.json --fix -- <修改的Markdown文件>
npx --no-install markdownlint --config .github/markdownlint.json -- <修改的Markdown文件>
python3 .github/scripts/check_links.py <修改的Markdown文件>
```

文件确实未归档时，不要编造新路径；删除失效链接格式，并保留“资料未归档”说明。每个 PR 只处理对应任务文件，避免混入其他历史目录整改。

## 1. 修复 2025 ROBOCON 上位机组文档内部链接

**Issue**：[necc-hub/new_energy_coder_club#30](https://github.com/necc-hub/new_energy_coder_club/issues/30)

- 文件：`competitions/2025-robocon/上位机组.md`
- 类型：`documentation`
- 预计：1–2 小时
- 完成标准：修复当前约 22 个内部链接问题；该文件通过 markdownlint 与链接检查。
- 带教人：维护者认领后指定

## 2. 修复 2025 ROBOCON 赛季主页内部链接

**Issue**：[necc-hub/new_energy_coder_club#31](https://github.com/necc-hub/new_energy_coder_club/issues/31)

- 文件：`competitions/2025-robocon/Readme.md`
- 类型：`documentation`
- 预计：1–2 小时
- 完成标准：修复当前约 6 个内部链接问题；不修改历史竞赛结论；该文件通过 markdownlint 与链接检查。
- 带教人：维护者认领后指定

## 3. 修复 2024 ROBOCON 电控组文档图片链接

**Issue**：[necc-hub/new_energy_coder_club#32](https://github.com/necc-hub/new_energy_coder_club/issues/32)

- 文件：`competitions/2024-robocon/电控组/Readme.md`
- 类型：`documentation`
- 预计：1–2 小时
- 完成标准：修复当前约 14 个内部链接问题；图片仍存在时改指真实路径，不存在时注明未归档；该文件通过 markdownlint 与链接检查。
- 带教人：维护者认领后指定

## 4. 整理 MICA 验证文档入口与失效链接

**Issue**：[necc-hub/new_energy_coder_club#33](https://github.com/necc-hub/new_energy_coder_club/issues/33)

- 文件：`projects/research-horizontal/mica-validation/README.md`
- 类型：`documentation`
- 预计：1–2 小时
- 完成标准：修复当前约 9 个内部链接问题；在 README 顶部补状态、负责人、最后验证日期和复现入口；未知字段写“待复核”，不能虚构。
- 额外验证：文档中给出的环境命令若未实际执行，必须标注“历史记录，未在本次验证”。
- 带教人：维护者认领后指定

## 5. 补充 Quickstart 的 Windows 实际验证记录

**Issue**：[necc-hub/new_energy_coder_club#34](https://github.com/necc-hub/new_energy_coder_club/issues/34)

- 文件：`docs/start-here/60min.md`、`docs/nec-quickstart/README.md`
- 类型：`documentation`
- 预计：30–60 分钟
- 完成标准：在 Windows 11 + Python 3.11 实际运行 Demo；记录使用的终端、完整命令、输出文件路径及一个常见问题；未实际测试不得标记完成。
- 验证：`python docs/nec-quickstart/hello_nec.py --seconds 2`
- 带教人：维护者认领后指定

## 6. 为 hello_nec.py 增加 `--plot` 开关

**Issue**：[necc-hub/new_energy_coder_club#35](https://github.com/necc-hub/new_energy_coder_club/issues/35)

- 文件：`docs/nec-quickstart/hello_nec.py`、`docs/nec-quickstart/README.md`
- 类型：`enhancement`
- 预计：1–2 小时
- 完成标准：支持 `--plot ascii` 与 `--plot off`，默认保持 `ascii`；`off` 不输出轨迹图但仍生成 CSV；README 增加两个示例。
- 验证：

  ```bash
  python3 docs/nec-quickstart/hello_nec.py --seconds 2 --plot ascii
  python3 docs/nec-quickstart/hello_nec.py --seconds 2 --plot off
  python3 docs/nec-quickstart/hello_nec.py --help
  ```

- 带教人：维护者认领后指定
