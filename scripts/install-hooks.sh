#!/usr/bin/env bash
# 安装仓库 Git 钩子（pre-commit: skills 一致性校验）
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
cp "$REPO_ROOT/scripts/hooks/pre-commit" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"
echo "✅ pre-commit 钩子已安装到 $HOOKS_DIR/pre-commit"
