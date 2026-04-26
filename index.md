# Memory Index（路由索引）

> 每次只召回与当前任务最相关的记忆，不要全量塞入。  
> 本文件是入口，正文在对应 .md 文件中。

---

## 🔍 快速路由

| 任务/问题 | 去哪里找 |
|---|---|
| 执行偏好、工具规则 | memory.md |
| 收到的纠正和修复 | corrections.md |
| OpenClaw 配置/操作 | domains/openclaw.md |
| AI Agent / LLM 原理 | domains/ai-agent.md |
| Vex 的 Skill 开发 | 问 Vex 直接读 SKILL.md |
| 今日 session 记录 | memory/YYYY-MM-DD.md |
| 长期记忆 / 用户画像 | MEMORY.md |

---

## 📁 文件清单

### 核心记忆
| 文件 | 行数 | 最后更新 | 内容定位 |
|---|---|---|---|
| memory.md | 43 | 活跃 | 执行偏好、Patterns、Rules |
| corrections.md | 27 | 活跃 | 收到的纠正记录 |

### 领域记忆
| 文件 | 行数 | 内容定位 |
|---|---|---|
| domains/ai-agent.md | 25 | AI Agent / LLM 原理、记忆系统设计 |
| domains/openclaw.md | 18 | OpenClaw 配置、Skill 管理 |

### 项目记忆
| 文件 | 内容定位 |
|---|---|
| projects/ | （当前无项目专属记忆） |

### 每日日志
| 文件 | 内容定位 |
|---|---|
| memory/YYYY-MM-DD.md | 每日 raw 日志，session 结束时写入 |

---

## 🧭 按主题索引

### 执行与工具
- exec/工具调用规则 → memory.md
- destructive 操作（删除/执行）→ memory.md Rule
- Unicode 清洗 → memory.md Pattern

### 记忆系统设计
- 分层记忆原理 → memory.md
- Relevant Recall 原则 → memory.md Rule
- Skill 结晶机制（GenericAgent 启发）→ domains/ai-agent.md
- index 路由层（本文件）→ 每次任务前扫一眼

### OpenClaw
- Skill 安装/管理 → domains/openclaw.md
- Vercel 部署（chip-check）→ 问 Vex
- 飞书配置 → domains/openclaw.md

### 用户相关
- 用户画像/偏好/习惯 → MEMORY.md
- 每日变化 → memory/YYYY-MM-DD.md
- 了解我进度 → skills/understand-me/references/history.md

---

## 🆕 最近新增（按时间倒序）

- 2026-04-26：GenericAgent 分析 → memory/weekly-github-skills/2026-04-24.md
- 2026-04-26：了解我第4轮 → skills/understand-me/references/history.md
- 2026-04-26：Vex 换房决策分析 → memory/2026-04-26.md

---

*最后更新：2026-04-27*
