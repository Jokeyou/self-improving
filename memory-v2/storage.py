#!/usr/bin/env python3
"""
Vex Memory V2 Storage Layer
结构化记忆存储，支持 facts/置信度/双写
"""

import json
import os
import threading
import time
from datetime import datetime, timezone
from typing import Optional

STORAGE_PATH = os.path.expanduser("~/self-improving/memory-v2/memory.json")
STORAGE_LOCK = threading.Lock()

# 最低置信度阈值
MIN_CONFIDENCE = 0.85


def _load() -> dict:
    """加载存储，加锁保证线程安全"""
    with STORAGE_LOCK:
        if not os.path.exists(STORAGE_PATH):
            return _create_empty()
        try:
            with open(STORAGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return _create_empty()


def _save(data: dict) -> None:
    """保存存储，加锁保证线程安全"""
    with STORAGE_LOCK:
        os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
        data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
        tmp = STORAGE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STORAGE_PATH)


def _create_empty() -> dict:
    """创建空存储结构"""
    return {
        "version": "1.0",
        "user": {
            "workContext": {"summary": "", "updatedAt": ""},
            "personalContext": {"summary": "", "updatedAt": ""},
            "topOfMind": {"summary": "", "updatedAt": ""},
        },
        "history": {
            "recentMonths": {"summary": "", "updatedAt": ""},
            "earlierContext": {"summary": "", "updatedAt": ""},
            "longTermBackground": {"summary": "", "updatedAt": ""},
        },
        "facts": [],
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }


def _gen_id(content: str) -> str:
    """生成唯一 fact ID"""
    import hashlib
    ts = int(time.time() * 1000)
    h = hashlib.md5(content.encode()).hexdigest()[:6]
    return f"fact_{ts}_{h}"


# ─── 核心 API ───────────────────────────────────────────────


def add_fact(
    content: str,
    category: str = "fact",
    confidence: float = 0.9,
    tags: list = None,
    source: str = "manual",
) -> Optional[dict]:
    """
    添加一条事实记录。
    只有 confidence >= MIN_CONFIDENCE 才会入库。
    返回新 fact 或 None（被过滤）。
    """
    if confidence < MIN_CONFIDENCE:
        return None

    data = _load()
    now = datetime.now(timezone.utc).isoformat()

    fact = {
        "id": _gen_id(content),
        "content": content,
        "category": category,
        "confidence": confidence,
        "tags": tags or [],
        "source": source,
        "createdAt": now,
        "updatedAt": now,
        "valid": True,
    }

    data["facts"].append(fact)
    _save(data)
    return fact


def update_fact(fact_id: str, **kwargs) -> bool:
    """更新一条 fact（只更新提供的字段）"""
    data = _load()
    for fact in data["facts"]:
        if fact["id"] == fact_id:
            for key, val in kwargs.items():
                if key in fact and key not in ("id", "createdAt"):
                    fact[key] = val
            fact["updatedAt"] = datetime.now(timezone.utc).isoformat()
            _save(data)
            return True
    return False


def invalidate_fact(fact_id: str, correction_content: str = None) -> bool:
    """废弃一条 fact（被用户纠正时调用）"""
    data = _load()
    for fact in data["facts"]:
        if fact["id"] == fact_id:
            fact["valid"] = False
            fact["updatedAt"] = datetime.now(timezone.utc).isoformat()
            if correction_content:
                fact["correctionNote"] = correction_content
            _save(data)
            return True
    return False


def search_facts(
    query: str = None,
    category: str = None,
    tags: list = None,
    valid_only: bool = True,
    limit: int = 20,
) -> list:
    """
    检索 facts。
    - query: 关键词匹配 content
    - category: 按类别过滤
    - tags: 按标签过滤（任一匹配）
    - valid_only: 只返回有效 facts
    - limit: 返回数量上限
    """
    data = _load()
    results = []

    for fact in data["facts"]:
        if valid_only and not fact.get("valid", True):
            continue
        if category and fact["category"] != category:
            continue
        if tags and not any(t in fact.get("tags", []) for t in tags):
            continue
        if query and query.lower() not in fact["content"].lower():
            continue
        results.append(fact)
        if len(results) >= limit:
            break

    return results


def get_fact_by_id(fact_id: str) -> Optional[dict]:
    """按 ID 获取单条 fact"""
    data = _load()
    for fact in data["facts"]:
        if fact["id"] == fact_id:
            return fact
    return None


def update_user_context(context_type: str, summary: str) -> bool:
    """
    更新用户上下文摘要。
    context_type: workContext | personalContext | topOfMind
    """
    data = _load()
    if context_type not in data["user"]:
        return False
    data["user"][context_type]["summary"] = summary
    data["user"][context_type]["updatedAt"] = datetime.now(timezone.utc).isoformat()
    _save(data)
    return True


def get_stats() -> dict:
    """返回存储统计"""
    data = _load()
    total = len(data["facts"])
    valid = sum(1 for f in data["facts"] if f.get("valid", True))
    by_category = {}
    for f in data["facts"]:
        c = f["category"]
        by_category[c] = by_category.get(c, 0) + 1
    return {
        "total_facts": total,
        "valid_facts": valid,
        "invalid_facts": total - valid,
        "by_category": by_category,
        "storage_path": STORAGE_PATH,
    }


# ─── 双写支持 ───────────────────────────────────────────────


def dual_write_fact(content: str, category: str, confidence: float, source: str) -> None:
    """
    双写模式：同时写入新版 memory.json 和旧版 corrections.md
    保证迁移期间不丢数据。
    """
    result = add_fact(content, category, confidence, source=source)
    if result:
        _append_to_legacy_corrections(content, category, source)
    return result


def _append_to_legacy_corrections(content: str, category: str, source: str) -> None:
    """追加到旧版 corrections.md（向后兼容）"""
    legacy_path = os.path.expanduser("~/self-improving/corrections.md")
    if not os.path.exists(legacy_path):
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    entry = f"\n### {now} [auto:{category}]\n- {content} (source: {source})\n"
    try:
        with open(legacy_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except IOError:
        pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: storage.py <action> [args]")
        print("Actions: add, search, stats, invalidate")
        sys.exit(1)

    action = sys.argv[1]

    if action == "stats":
        print(json.dumps(get_stats(), indent=2, ensure_ascii=False))
    elif action == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else None
        for f in search_facts(query=query):
            print(f"[{f['id']}] {f['content'][:60]}... ({f['category']})")
    elif action == "add":
        content = sys.argv[2] if len(sys.argv) > 2 else "test"
        r = add_fact(content, "test", 0.95)
        print("Added:", r["id"] if r else "filtered")
    elif action == "invalidate":
        fid = sys.argv[2] if len(sys.argv) > 2 else None
        if fid:
            print("OK:", invalidate_fact(fid))
