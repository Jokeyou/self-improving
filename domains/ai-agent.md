# Domain: AI Agent

AI Agent 架构与工程经验积累

## 核心架构模式
（参考 Claude Code 六层架构：CLI引导 → 初始化 → TUI/REPL → 执行内核 → Tool/Permission → Memory/扩展）

## Memory 设计
- 分层原则：Auto Memory / Session Memory / Agent Memory / Team Memory 各司其职
- MEMORY.md = 索引入口，不是正文仓库
- Relevant Recall：不要全塞 prompt，先扫文件头做轻量选择

## Tool Call 工程
- Tool = 运行时协议对象（含并发安全/读写性质/权限声明）
- 并发调度：读可并发，写必须串行
- Schema 校验 + 语义校验双层

## 安全设计
- 双闸门：Tool Permission（应用层） + Sandbox（系统层）
- 外部输入 Unicode 清洗：NFKC 规范化 + 危险字符过滤
- 危险模式：python:* / node:* 等宽泛授权必须拒绝

## 待补充
- Sandbox 实现细节
- MCP 协议集成
