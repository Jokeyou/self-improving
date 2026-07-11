#!/usr/bin/env python3
"""
Auto-Learn Integration
将 correction-detector 的检测结果自动写入 memory-v2 存储

调用方式:
  python3 auto_learn.py check "<user_message>" "<assistant_context>"
  python3 auto_learn.py stats
  python3 auto_learn.py search "<query>"
  python3 auto_learn.py list
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

# 导入存储层
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storage import add_fact, search_facts, get_stats, invalidate_fact

AUTO_LOG = os.path.expanduser("~/self-improving/corrections-auto.md")


def _timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def _call_detector(message: str, context: str = "") -> dict:
    """调用 Node.js correction-detector.js"""
    try:
        result = subprocess.run(
            ["node",
             os.path.expanduser("~/self-improving/scripts/correction-detector.js"),
             message, context],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"detected": False}
    except Exception:
        return {"detected": False}


def _parse_auto_log() -> list:
    """解析 corrections-auto.md 中的未处理条目"""
    if not os.path.exists(AUTO_LOG):
        return []
    
    entries = []
    try:
        with open(AUTO_LOG, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 匹配未处理的条目（已处理标记 ✅，未处理标记 ⬜）
        pattern = r"### (\d{4}-\d{2}-\d{2} \d{2}:\d{2})\n- \*\*信号\*\*: (.+?)\n- \*\*用户说\*\*: (.+?)\n- \*\*上下文\*\*: (.+?) \n- \*\*类别\*\*: (.+?)\n- \*\*置信度\*\*: ([\d.]+)\n- \*\*已处理\*\*: (⬜|✅)"
        for m in re.finditer(pattern, content):
            entries.append({
                "timestamp": m.group(1),
                "signal": m.group(2),
                "user_said": m.group(3),
                "context": m.group(4),
                "category": m.group(5),
                "confidence": float(m.group(6)),
                "processed": m.group(7) == "✅",
            })
    except Exception:
        pass
    return entries


def _mark_processed(timestamp: str) -> bool:
    """标记某条auto log为已处理"""
    if not os.path.exists(AUTO_LOG):
        return False
    try:
        with open(AUTO_LOG, "r", encoding="utf-8") as f:
            content = f.read()
        # 找到对应时间戳的条目，将 ⬜ 改为 ✅
        # 简单替换：只改第一个出现的（该条目内只有一个 ⬜）
        new_content = content.replace(
            f"### {timestamp}\n- **已处理**: ⬜",
            f"### {timestamp}\n- **已处理**: ✅",
            1
        )
        if new_content == content:
            return False
        with open(AUTO_LOG, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception:
        return False


def check_and_record(user_message: str, assistant_context: str = "") -> dict:
    """
    主入口：检测用户消息中的纠正信号，写入 memory-v2
    返回 dict: {detected: bool, fact: dict or None}
    """
    detection = _call_detector(user_message, assistant_context)
    
    if not detection.get("detected"):
        return {"detected": False, "fact": None}
    
    # 分类映射
    cat = detection.get("category", "correction")
    if cat == "stop_signal":
        cat = "behavior"
    
    confidence = detection.get("confidence", 0.8)
    raw = detection.get("raw", "")[:200]
    
    # 构造 fact 内容
    content = f"[纠正] {raw}"
    if assistant_context:
        content += f" | 上下文: {assistant_context[:50]}"
    
    # 写入 storage（阈值检查在 add_fact 内部统一处理）
    tags = ["auto-detected", detection.get("label", "")]
    source = "correction-auto"
    fact = add_fact(
        content=content,
        category=cat,
        confidence=confidence,
        tags=tags,
        source=source,
    )
    if fact is not None:
        _mark_processed(_timestamp())
        return {"detected": True, "fact": fact, "confidence": confidence}
    
    return {"detected": True, "fact": None, "confidence": confidence, "reason": "below storage threshold"}


def review_pending() -> list:
    """返回所有未处理的 auto-log 条目"""
    return [e for e in _parse_auto_log() if not e["processed"]]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: auto_learn.py <check|stats|search|list|review> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "check":
        msg = sys.argv[2] if len(sys.argv) > 2 else ""
        ctx = sys.argv[3] if len(sys.argv) > 3 else ""
        r = check_and_record(msg, ctx)
        print(json.dumps(r, indent=2, ensure_ascii=False))
    
    elif cmd == "stats":
        print(json.dumps(get_stats(), indent=2, ensure_ascii=False))
    
    elif cmd == "search":
        q = sys.argv[2] if len(sys.argv) > 2 else None
        for f in search_facts(query=q):
            print(f"[{f['id']}] {f['content'][:80]}")
    
    elif cmd == "list":
        for f in search_facts(limit=50):
            status = "✅" if f.get("valid") else "❌"
            print(f"{status} [{f['category']}] {f['content'][:70]}")
    
    elif cmd == "review":
        pending = review_pending()
        print(f"待处理: {len(pending)} 条")
        for e in pending:
            print(f"  [{e['timestamp']}] {e['user_said'][:50]}")
    
    else:
        print(f"Unknown command: {cmd}")
