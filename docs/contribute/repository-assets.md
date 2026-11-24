# 仓库资产规范（图片、图纸与归档文件）

## 当前存储约定

本仓库以文档、图片和工程资料为主。现有 PNG/JPEG/GIF 均为普通 Git 二进制对象，**不是 Git LFS pointer**。为避免混合存储导致 clone 后文件异常，当前 `.gitattributes` 只声明二进制类型，不启用 LFS filter。

在维护者完成单独的 LFS 评估前：

- 不要只对部分新图片执行 `git lfs track`。
- 不要直接运行 `git lfs migrate` 重写历史。
- 不要提交由 `git lfs` 产生的 pointer 文件，却省略对应 LFS 对象。
- 如果确需迁移历史，先备份、通知协作者，并在独立 PR/维护窗口执行。

## 新文件放哪里

| 内容 | 推荐位置 |
|---|---|
| 文档必需的小图片、PDF、STEP | 与对应项目/赛季文档放在同一目录 |
| 多项目共用的 Logo、通用图片 | `shared/images/` |
| 通用模型和标准件 | `shared/models/` |
| 完整软件源码 | 对应项目目录或独立源码仓库 |
| 大型数据集、视频、安装包、构建产物 | 对象存储、Release 或受控网盘，仓库只保存来源和校验信息 |

单文件超过 10 MiB 时，提交前先说明为什么必须进入 Git。能用外链或 Release 替代的，不重复入库。不要提交 `node_modules/`、构建输出、缓存、系统自动生成的文件。

## 本地开发环境

活跃 Git 工作区应放在 APFS 等支持 POSIX 语义的文件系统上。macOS 在 ExFAT 等非原生文件系统上会不断生成 `._*` AppleDouble 文件；`.gitignore` 不能阻止它们进入 `.git/` 内部。

- `/Volumes/Data`（ExFAT）：只做大文件周转，不作为长期活跃仓库位置。
- 内置盘：存放代码、Git 工作区和 `node_modules`。
- NAS：用于照片、视频、备份和归档，不在其上运行高频 Git 或 npm 操作。

如果 `git count-objects` 或 `git log` 报 AppleDouble/garbage 警告，优先迁移到健康的 APFS clone，不要在其他协作者仍在使用时清理共享 `.git` 目录。

## 来源与许可证

仓库主许可证不自动覆盖第三方资产。引用竞赛规则、厂商手册、网盘资料、图纸或图片时，应在邻近 README 记录：

- 原作者或发布机构
- 原始链接与获取日期
- 是否允许再分发；不确定时只保存链接，不复制原文件
- 本地修改说明（如有）

密钥、未公开个人信息、未授权的商业资料不得提交。发现后不要仅删除最新文件，应联系维护者评估历史清理。

## 提交前检查

```bash
git status --short
git diff --stat
git ls-files | grep -E '(^|/)\._|\.DS_Store|Thumbs\.db'
```

最后一条命令应无输出。PR 中说明新增资产的来源、大小和用途。
