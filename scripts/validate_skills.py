#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SKill 分支一致性校验：skills/ 目录 vs SKILL.md frontmatter vs README 索引。

用法: python scripts/validate_skills.py
任一检查失败以非零码退出，可直接接入 CI。
"""
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")
README = os.path.join(ROOT, "README.md")

errors = []
warnings = []


def check(cond, msg):
    if not cond:
        errors.append(msg)
        print(f"  ❌ {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  ⚠️ {msg}")


def main():
    dirs = sorted(
        d for d in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, d))
    )
    print(f"共发现 {len(dirs)} 个 skill 目录")

    # 1. 每个目录必须有 SKILL.md，frontmatter 含 name/description，name 与目录一致
    names = {}
    for d in dirs:
        p = os.path.join(SKILLS_DIR, d, "SKILL.md")
        if not os.path.isfile(p):
            check(False, f"{d}: 缺少 SKILL.md")
            continue
        head = open(p, encoding="utf-8-sig").read(4000)
        fm = re.match(r"^---\n(.*?)\n---", head, re.S)
        check(fm is not None, f"{d}: SKILL.md 缺少 YAML frontmatter")
        # 单行引号 description 必须同行闭合（防止 YAML 结构被破坏）
        for line in head.split("\n"):
            if line.startswith('description: "') and not line.rstrip().endswith('"'):
                check(False, f"{d}: description 引号未闭合，会破坏 YAML 结构")
                break
        if not fm:
            continue
        name_m = re.search(r"^name:\s*[\"']?([^\s\"']+)[\"']?\s*$", fm.group(1), re.M)
        desc_m = re.search(r"^description:\s*(.*?)(?=^\w+:|\Z)", fm.group(1), re.S | re.M)
        check(name_m is not None, f"{d}: frontmatter 缺少 name")
        check(desc_m is not None, f"{d}: frontmatter 缺少 description")
        if desc_m:
            desc = desc_m.group(1).strip().strip('"\'').replace("\n", " ")
            dl = len(desc)
            check(dl >= 30, f"{d}: description 过短({dl}字符)，不足以支撑触发路由")
            check(dl <= 1024, f"{d}: description 过长({dl}字符)，超过 1024 上限")
            if not re.search(r"(当.*时(使用|触发|激活)|[Uu]se when|[Uu]se this|触发词|NOT for|反触发|Keywords|仅当|用于当)", desc):
                warn(f"{d}: description 缺少明确触发条件（Use when / 当...时使用）")
        body_lines = head.count("\n")
        if body_lines > 500:
            warn(f"{d}: SKILL.md 正文 {body_lines} 行，建议拆分至 references/（渐进式披露）")
        for junk in ("README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"):
            if os.path.isfile(os.path.join(SKILLS_DIR, d, junk)):
                warn(f"{d}: 冗余文件 {junk}（skill-creator 规范不建议随包分发）")
        if name_m:
            names[d] = name_m.group(1)
            check(names[d] == d, f"{d}: frontmatter name({names[d]}) 与目录名不一致")

    # 2. 命名规范：小写字母/数字/连字符
    for d in dirs:
        check(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", d) is not None,
              f"{d}: 目录名不符合 lowercase-hyphen 规范")

    # 3. README 索引一致性
    readme = open(README, encoding="utf-8-sig").read()
    sec_start = readme.find("本仓库收录了")
    sec_end = readme.find("### 📁 Skill 文件结构")
    check(sec_start != -1 and sec_end != -1, "README: 未找到索引区（本仓库收录了 ... Skill 文件结构）")
    if sec_start != -1 and sec_end != -1:
        sec = readme[sec_start:sec_end]
        items = re.findall(r"`([A-Za-z0-9_-]+)`", sec)
        indexed = set(items)
        dup = {k: v for k, v in Counter(items).items() if v > 1}
        check(not dup, f"README: 索引重复列出 {sorted(dup)}")
        check(indexed == set(dirs),
              f"README: 索引与目录不一致（未索引: {sorted(set(dirs) - indexed)}；"
              f"索引多余: {sorted(indexed - set(dirs))}）")

        # 4. 各分类声明数量与实际列出数量一致
        for m in re.finditer(r"#### (.*?)\((\d+)\)\n\n>.*?\n\n((?:`[^`]+`\s*)+)", readme, re.S):
            declared, listed = int(m.group(2)), len(re.findall(r"`[^`]+`", m.group(3)))
            check(declared == listed,
                  f"README: 分类「{m.group(1).strip()}」声明 {declared} 实际列出 {listed}")

    # 5. README 总数声明与实际目录数一致
    total_m = re.search(r"\| Skills 总数 \| \*\*(\d+)\*\* \|", readme)
    check(total_m is not None, "README: 未找到「Skills 总数」表格行")
    if total_m:
        check(int(total_m.group(1)) == len(dirs),
              f"README: Skills 总数声明 {total_m.group(1)}，实际 {len(dirs)}")

    # 6. 大文件检查：>5MB 不得入库（白名单除外）
    LARGE_FILE_WHITELIST = {"kc-gui/kc.exe"}  # kc-gui 运行依赖，历史例外
    for dirpath, _dirnames, filenames in os.walk(SKILLS_DIR):
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, SKILLS_DIR).replace(os.sep, "/")
            if os.path.getsize(fp) > 5 * 1024 * 1024 and rel not in LARGE_FILE_WHITELIST:
                check(False, f"大文件入库(>5MB): skills/{rel}，请改用 Release 资产或 Git LFS")

    if warnings:
        print(f"\n共 {len(warnings)} 条警告（不阻断，建议逐步改进）")
    if errors:
        print(f"校验失败，共 {len(errors)} 个错误")
        sys.exit(1)
    print("\n✅ 全部校验通过")


if __name__ == "__main__":
    main()
