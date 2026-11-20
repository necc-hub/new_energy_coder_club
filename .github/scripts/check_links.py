#!/usr/bin/env python3
"""检查 Markdown 文件中的内部链接与锚点。

规则：
- 相对路径文件链接必须指向存在的文件
- 同文档锚点（#heading）必须存在
- 锚点转 Markdown 规范 slug（GitHub 风格）：小写、空格转连字符、去除标点
- 只检查仓库内链接；http(s) 外链与 mailto 不在范围内（避免 CI 因外网波动误报）
"""
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {".git", "node_modules", "_build", ".claude"}

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def slugify(heading: str) -> str:
    """GitHub 风格的 heading -> anchor 转换（含中文处理）。"""
    text = heading.strip().lower()
    # 去除标点（保留中文/字母/数字/空格/连字符）
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("P") and ch not in ("-",):
            continue
        out.append(ch)
    text = "".join(out)
    return text.replace(" ", "-")


def heading_anchors(md_text: str) -> set:
    anchors = set()
    in_code = False
    for line in md_text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            anchors.add(slugify(m.group(2)))
    return anchors


def main() -> int:
    errors = []
    # 支持两种模式：
    #   无参数 —— 全量扫描（可用于周期性报告）
    #   传入文件列表 —— 只检查这些文件（CI 在 PR 中传改动文件，防止新增死链）
    if len(sys.argv) > 1:
        md_files = [(REPO / a) for a in sys.argv[1:] if a.endswith(".md")]
    else:
        md_files = []
        for p in REPO.rglob("*.md"):
            # 只按仓库内相对路径判断排除目录（worktree 自身可能位于 .claude 下）
            rel_parts = p.relative_to(REPO).parts
            if any(part in EXCLUDE_DIRS for part in rel_parts):
                continue
            md_files.append(p)

    for md in sorted(md_files):
        rel = md.relative_to(REPO)
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            errors.append(f"{rel}: 读取失败 {e}")
            continue
        # 跳过代码块内的链接
        filtered_lines = []
        in_code = False
        for line in text.splitlines():
            if line.strip().startswith("```"):
                in_code = not in_code
                filtered_lines.append("")
                continue
            filtered_lines.append("" if in_code else line)
        filtered = "\n".join(filtered_lines)

        for m in LINK_RE.finditer(filtered):
            target = m.group(2)
            if target.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            # 剥离锚点
            if target.startswith("#"):
                anchor = target[1:]
                if anchor and anchor not in heading_anchors(text):
                    errors.append(f"{rel}: 锚点 #{anchor} 不存在")
                continue
            path_part, _, anchor = target.partition("#")
            # Markdown 链接中的路径可能带 URL 编码（如 %E7%99%BE = 百），先解码再匹配文件系统
            path_part = unquote(path_part)
            target_path = (md.parent / path_part).resolve() if path_part else md
            try:
                target_path.relative_to(REPO)
            except ValueError:
                continue  # 指向仓库外（如绝对路径），跳过
            if not target_path.exists():
                errors.append(f"{rel}: 链接目标不存在 {target}")
            elif anchor:
                if target_path.suffix == ".md":
                    try:
                        t = target_path.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    if anchor not in heading_anchors(t):
                        errors.append(f"{rel}: {target} 中的锚点 #{anchor} 不存在")

    if errors:
        print(f"❌ 发现 {len(errors)} 个链接问题：")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"✅ 检查了 {len(md_files)} 个 Markdown 文件，链接全部有效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
