# 27 赛季新人学习区（Onboarding）

欢迎来到 NEC · CURC2027ROBOCON 新人学习区！

这里是你从 0 到 1 加入团队、记录学习过程的专属空间。

---

## 这个区是做什么的？

- **汇总学习资源**：把招新时提到的课程、视频、文档按方向整理在一起，方便查找。
- **记录学习过程**：每个人按模板写学习记录，形成自己的成长轨迹。
- **降低沟通成本**：组长可以通过学习记录了解你的进度和基础，面试/分任务时更有针对性。

---

## 文件结构

```text
docs/onboarding/
├── README.md                      # 本文件：总入口
├── resources.md                   # 学习资源清单
├── how-to-log.md                  # 如何提交学习记录/进度
├── templates/
│   └── learning-log-template.md  # 详细学习记录模板
├── members/                       # 新成员个人进度看板
│   ├── README.md
│   ├── 新人进度模板.md
│   └── 朱佩韦.md                 # 示例
└── logs/                          # 详细学习记录存放处
    ├── mechanical/                # 机械组
    ├── electrical/                # 电控组
    ├── hardware/                  # 硬件组
    ├── vision/                    # 视觉组
    └── operations/                # 运营组
```

---

## 新人第一步

1. 先读 [resources.md](./resources.md)，找到自己方向的学习资料。
2. 再读对应 SIG 的 `README.md`，查看本方向的**新人学习路线**：
   - [机械组新人学习路线](../../机构SIG/机械组/README.md)
   - [电控组新人学习路线](../../机构SIG/电控组/README.md)
   - [视觉组新人学习路线](../../视觉SIG/视觉组/README.md)
   - [硬件组新人学习路线](../../视觉SIG/硬件组/README.md)
   - [运营组新人学习路线](../../运营SIG/README.md)
3. 再读 [how-to-log.md](./how-to-log.md)，了解怎么提交学习进度和学习记录。
4. **创建你的个人进度看板**：复制 [members/新人进度模板.md](./members/新人进度模板.md)，创建 `members/<你的姓名>.md`。
5. **写详细学习记录**：参考 [templates/learning-log-template.md](./templates/learning-log-template.md)，把每次学习的具体内容放到 `logs/<你的方向>/<你的昵称>/<YYYYMMDD>-<主题>.md`。
6. 提交 Pull Request。

---

## 提交规范

### 个人进度看板（必须）

- **文件位置**：`members/<你的姓名>.md`
- **更新频率**：首次加入后尽快提交，之后每 1-2 周更新一次
- **作用**：让组长快速了解你的整体进度

### 详细学习记录（建议）

- **文件位置**：`logs/<方向>/<昵称>/<YYYYMMDD>-<主题>.md`
- **方向可选**：`mechanical` / `electrical` / `hardware` / `vision` / `operations`
- **作用**：记录每次具体学习的内容、踩坑、收获

### 通用

- **提交方式**：Fork 仓库 → 在分支上写 → 提交 Pull Request
- **Review 人**：对应方向的组长或领队

---

## 有问题怎么办？

- 技术问题：先在对应 SIG 群里问，或者开 Issue 讨论。
- 仓库操作问题：看 [how-to-log.md](./how-to-log.md)，还搞不定就 @ 领队。

---

## 相关链接

- [CURC2027ROBOCON 赛季总入口](../../README.md)
- [通用学习资源](../../../docs/learn/)
- [社区贡献指南](../../../../CONTRIBUTING.md)
