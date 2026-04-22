# Auto-Detected Corrections Log
> 自动检测用户纠正信号，每周 review 一次
> 触发信号：不对/错了/不是/等等/No/Actually/Wait/但/不过/嗯（勉强接受）

## 格式
```
### {timestamp}
- **信号**: {检测到的关键词}
- **用户说**: {原始消息}
- **上下文**: {我之前的回复摘要}
- **类别**: correction | preference | reinforcement
- **置信度**: {0.0-1.0}
- **已处理**: ⬜
```

---
