---
name: qclaw-openclaw
description: QClaw OpenClaw CLI 包装器。从 ~/.qclaw/qclaw.json 读取 QClaw 桌面应用的运行时路径（独立 Node.js 二进制 + openclaw.mjs），跨平台执行 openclaw 命令（config get/set、cron list、skills list 等）。当用户需要在本机以命令行方式操作 OpenClaw（查看/修改网关配置、管理定时任务、列出 skills）且已安装 QClaw 桌面应用时使用。触发词：openclaw 命令、qclaw cli、openclaw config、openclaw cron、openclaw skills。
---

# QClaw OpenClaw CLI

通过 QClaw 桌面应用内置的独立 Node.js 运行时执行 openclaw 命令，无需系统安装 Node。

## 前置条件

- 已安装并**启动过** QClaw 桌面应用（生成 `~/.qclaw/qclaw.json` 元信息文件）
- 元信息缺失时脚本会报错退出，提示用户先启动 QClaw

## 用法

Windows：

```cmd
scripts\openclaw-win.cmd <command> [args...]
```

macOS：

```bash
bash scripts/openclaw-mac.sh <command> [args...]
```

## 常用命令示例

```text
config get gateway.port     # 查看网关端口
cron list                   # 列出定时任务
skills list                 # 列出已安装 skills
```

## 工作机制

1. 读取 `~/.qclaw/qclaw.json`，解析出 `cli.nodeBinary`、`cli.openclawMjs`、`stateDir`、`configPath`
2. 校验 Node 二进制与 openclaw.mjs 存在（失效时提示重启 QClaw 刷新元信息）
3. 注入 `NODE_OPTIONS=--no-warnings` 等环境变量后用内置 Node 执行 openclaw 命令
