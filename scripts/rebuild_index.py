#!/usr/bin/env python3
"""
rebuild_index.py
扫描 ~/self-improving/ 目录下所有 .md 文件，
自动重建 index.md 路由索引。

每小时 cron 自动跑，结果推送 GitHub。
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

SELF_IMPROVING = Path.home() / "self-improving"
INDEX_FILE = SELF_IMPROVING / "index.md"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

EXCLUDE_DIRS = {"backup", "archive", ".dreams", "__pycache__", "memory-v2"}


def get_md_files():
    files = []
    for root, _, filenames in os.walk(SELF_IMPROVING):
        parts = Path(root).parts
        if any(ex in parts for ex in EXCLUDE_DIRS):
            continue
        for f in filenames:
            if f.endswith(".md") and f != "index.md":
                rel = os.path.relpath(os.path.join(root, f), SELF_IMPROVING)
                files.append(rel)
    return sorted(files)


def get_file_info(rel_path):
    full_path = SELF_IMPROVING / rel_path
    if not full_path.exists():
        return None
    stat = full_path.stat()
    with open(full_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    lines = len(content.splitlines())
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else rel_path
    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
    return {"lines": lines, "modified": modified, "title": title}


def guess_category(rel_path):
    if "/domains/" in rel_path:
        return "领域"
    elif "/projects/" in rel_path:
        return "项目"
    elif "/memory/" in rel_path:
        return "日志"
    elif "correction" in rel_path.lower():
        return "纠正"
    elif "heartbeat" in rel_path.lower():
        return "心跳"
    elif "darwin" in rel_path.lower():
        return "达尔文"
    else:
        return "核心"


def rebuild():
    files = get_md_files()
    all_files_sorted = []
    for rel in files:
        info = get_file_info(rel)
        if info:
            all_files_sorted.append((rel, info))

    all_files_sorted.sort(key=lambda x: x[1]["modified"], reverse=True)

    out = []
    out.append("# Memory Index（路由索引）")
    out.append("")
    out.append("> ⚠️ 本文件由脚本自动生成，每小时更新一次。")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 📁 文件清单（按更新时间倒序）")
    out.append("")
    out.append("| 文件 | 分类 | 行数 | 更新 | 标题 |")
    out.append("|---|---|---|---|---|")
    for rel, info in all_files_sorted:
        cat = guess_category(rel)
        title = info["title"][:35]
        out.append(f"| `{rel}` | {cat} | {info['lines']} | {info['modified']} | {title} |")
    out.append("")
    out.append(f"*最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    content = "\n".join(out)
    INDEX_FILE.write_text(content, encoding="utf-8")
    print(f"✅ index.md 重建完成，共 {len(files)} 个文件")
    return content


def git_push():
    try:
        subprocess.run(["git", "add", "index.md"], cwd=SELF_IMPROVING, check=True)
        result = subprocess.run(
            ["git", "commit", "-m", f"auto: rebuild index.md ({datetime.now().strftime('%Y-%m-%d %H:%M')})"],
            cwd=SELF_IMPROVING, capture_output=True, text=True
        )
        if result.returncode != 0:
            print("commit 跳过（无变化）")
            return
        remote_url = f"https://{os.environ.get("GITHUB_TOKEN","")}@github.com/Jokeyou/self-improving.git"
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=SELF_IMPROVING, check=True)
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=SELF_IMPROVING, capture_output=True, text=True,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
        print("✅ 已推送 GitHub")
    except Exception as e:
        print(f"⚠️ 推送失败: {e}")


if __name__ == "__main__":
    rebuild()
    if "--push" in __import__("sys").argv:
        git_push()
