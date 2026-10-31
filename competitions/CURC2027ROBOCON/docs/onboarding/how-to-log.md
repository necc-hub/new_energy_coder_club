# 如何提交学习进度与学习记录

提交学习进度和学习记录是 NEC 新人最重要的"作业"之一。不是为了检查你学得多快，而是为了：

- 帮你梳理学过的内容
- 让组长了解你的进度和困惑
- 留下可追溯的成长轨迹

两种提交方式：

1. **个人进度看板**（`members/<你的姓名>.md`）：你的总进度表，参考 26 赛季做法。
2. **详细学习记录**（`logs/<方向>/<昵称>/<日期>-<主题>.md`）：每次具体学习的记录。

---

## 写在前面

- **不要求写得多完美**，但求真实、具体、有思考。
- 每次学习完一个主题，或者一周学习结束后，都可以写一篇。
- 不会写可以参考 [templates/learning-log-template.md](./templates/learning-log-template.md)。

---

## 第一步：Fork / 克隆仓库

### 如果你没有写权限

1. 打开 Gitee 仓库首页：https://gitee.com/darrenpig/new_energy_coder_club
2. 点击右上角 **Fork** 按钮，把仓库 Fork 到你自己的账号下。
3. 克隆你自己的 Fork：

```bash
git clone https://gitee.com/<你的用户名>/new_energy_coder_club.git
cd new_energy_coder_club
```

### 如果你有写权限

```bash
git clone https://gitee.com/darrenpig/new_energy_coder_club.git
cd new_energy_coder_club
git checkout -b feat/<你的昵称>-learning-log
```

---

## 第二步 A：创建你的个人进度看板

参考 26 赛季做法，每位新人需要创建一个以自己姓名命名的进度文件。

文件路径规范：

```text
competitions/CURC2027ROBOCON/docs/onboarding/members/<你的姓名>.md
```

示例：

```text
competitions/CURC2027ROBOCON/docs/onboarding/members/朱佩韦.md
```

模板位置：[members/新人进度模板.md](./members/新人进度模板.md)

示例文件：[members/朱佩韦.md](./members/朱佩韦.md)

---

## 第二步 B：创建你的详细学习记录文件

每次学完一个具体主题，可以写一篇详细记录。

文件路径规范：

```text
competitions/CURC2027ROBOCON/docs/onboarding/logs/<方向>/<你的昵称>/<YYYYMMDD>-<主题>.md
```

示例：

```text
competitions/CURC2027ROBOCON/docs/onboarding/logs/electrical/darrenpig/20250701-stm32-gpio.md
```

### 方向名必须是小写英文

| 方向 | 目录名 |
|------|--------|
| 机械 | `mechanical` |
| 电控 | `electrical` |
| 硬件 | `hardware` |
| 视觉 | `vision` |
| 运营 | `operations` |

---

## 第三步：按模板写内容

复制 [templates/learning-log-template.md](./templates/learning-log-template.md) 的内容，填充你自己的学习情况。

---

## 第四步：提交

建议把个人进度看板和详细学习记录一起提交：

```bash
git add .
git commit -m "docs(onboarding): update 学习进度 by <姓名>"
git push origin <你的分支名>
```

如果只提交详细学习记录：

```bash
git add .
git commit -m "docs(onboarding): add 学习记录 by <昵称> - <主题>"
git push origin <你的分支名>
```

---

## 第五步：发起 Pull Request

1. 打开你的 Gitee Fork 页面。
2. 点击 **Pull Request** → **新建 Pull Request**。
3. 源分支选你的分支，目标分支选 `darrenpig/new_energy_coder_club:master`。
4. 标题写清楚：`[学习记录] <方向> <昵称> <日期>-<主题>`
5. 正文简单说明学习内容和遇到的问题。
6. 指定 Reviewer：对应方向的组长。

---

## 命名示例

### 个人进度看板

| 文件路径 | 说明 |
|---------|------|
| `members/朱佩韦.md` | 朱佩韦的个人学习进度看板 |
| `members/凌敏菲.md` | 凌敏菲的个人学习进度看板 |

### 详细学习记录

| 文件路径 | 说明 |
|---------|------|
| `logs/mechanical/alice/20250705-sw2025-sketch.md` | Alice 的机械 SW 草图学习记录 |
| `logs/electrical/bob/20250710-stm32-timer.md` | Bob 的 STM32 定时器学习记录 |
| `logs/vision/carol/20250715-opencv-basic.md` | Carol 的 OpenCV 基础学习记录 |

---

## 常见问题

**Q：我不会用 Git 怎么办？**  
A：先学 [大学生扫盲课：Git、GitHub、Gitee 完整讲解](https://www.bilibili.com/video/BV1d7jbefEee)，这是基础。

**Q：我学习进度很慢，不好意思写。**  
A：写记录本身就是学习的一部分。哪怕只学了一个概念，也可以写出来。

**Q：可以写踩坑记录吗？**  
A：非常欢迎。踩坑记录往往比成功记录更有价值。
