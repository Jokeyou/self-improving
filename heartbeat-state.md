# Self-Improving Heartbeat State

last_heartbeat_started_at: 2026-04-21T07:06:00+08:00
last_reviewed_change_at: 2026-04-21T07:06:00+08:00
last_heartbeat_result: OK
last_actions: corrections.md更新（小红书封面图规则）；写2026-04-06会话小结（日记）到memory/2026-04-06.md；发现两个cron任务error待查（每日历史/认知冲刷）
lastSessionSummaryAt: 2026-04-12T12:11:00+08:00

## Darwin Skill 触发追踪

### 近7天用户纠正检查（每次Heartbeat执行）
读取 corrections.md 中近7天新增记录：
- 芯早参封面图：2026-04-08（1次）
- 无其他新增
→ 触发阈值：同skill ≥ 2次 → 未触发

### Skill 周调用统计（手动更新，待自动）
| Skill | 本周调用 | 状态 |
|-------|---------|------|
| darwin-skill | - | 待追踪 |
| 芯早参封面 | - | 待追踪 |

### T2 周统计（来自 session 解析，供参考）

| Skill | 近7天出现次数 | 阈值 | 状态 |
|-------|-------------|------|------|
| 认知冲刷 | 9 | ≥5 | ⚠️ 关注 |
| 了解我 | 9 | ≥5 | ⚠️ 关注 |
| 芯早参/芯片日报 | 6 | ≥5 | ⚠️ 关注 |
| 芯早参封面 | 5 | ≥5 | ⚠️ 关注 |
| 马斯克视角 | 7 | ≥5 | ⚠️ 关注 |

（数据基于 session 关键词统计，不能区分"用户提到"和"skill 被激活"）

### 触发状态
- T1（用户纠正）：未触发（最多1次，未达阈值2）
- T2（热度）：本周扫描完，符合条件：认知冲刷/了解我/芯早参封面/马斯克视角（≥5次且无correction）
- T3（定时）：已关闭，用户选择仅依赖T1+T2
