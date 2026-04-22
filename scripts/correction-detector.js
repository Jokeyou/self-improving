#!/usr/bin/env node
/**
 * Correction Detector
 * 检测用户消息中的纠正信号，返回结构化结果
 */

const correctionSignals = [
  // 中文强信号
  { pattern: /不对|错了|不是这样|不是的|搞错了|记错了|说错了/i, weight: 0.95, label: '直接否定' },
  { pattern: /实际上|事实上|其实|不过/i, weight: 0.75, label: '转折否定' },
  { pattern: /等等|等一下|慢着|先别/i, weight: 0.6, label: '暂停纠正' },
  { pattern: /重新|再来|不算|不算数/i, weight: 0.5, label: '重来请求' },
  
  // 中文弱信号（需要结合上下文）
  { pattern: /但.*是|可是|然而/i, weight: 0.4, label: '委婉转折' },
  
  // 英文信号
  { pattern: /no\b|not right|that's wrong|i'm afraid|i disagree/i, weight: 0.95, label: '直接否定(EN)' },
  { pattern: /actually|wait|in fact|however|but/i, weight: 0.6, label: '转折(EN)' },
  { pattern: /on second thought|let me reconsider/i, weight: 0.7, label: '重新考虑' },
  
  // 勉强接受信号
  { pattern: /^嗯[，,\.]|^好吧|^行吧|^算了/i, weight: 0.3, label: '勉强接受' },
];

const rejectionSignals = [
  /不要说.*了|别说了|停止|stop|don't do/i,
  /我说了.*次|跟你说.*遍了/i,
  /怎么又|为什么老|每次都/i,
];

/**
 * 检测消息中的纠正信号
 * @param {string} userMessage - 用户消息
 * @param {string} assistantContext - 助手上一次回复的摘要（可选）
 * @returns {object|null} - 检测结果或null
 */
function detect(userMessage, assistantContext = '') {
  if (!userMessage || typeof userMessage !== 'string') {
    return null;
  }

  const trimmed = userMessage.trim();
  
  // 检查拒绝/叫停信号
  for (const signal of rejectionSignals) {
    if (signal.test(trimmed)) {
      return {
        detected: true,
        category: 'stop_signal',
        label: '叫停/重复警告',
        confidence: 0.95,
        matchedPattern: signal.toString(),
        raw: trimmed.slice(0, 100),
      };
    }
  }

  // 检查纠正信号
  let bestMatch = null;
  let bestWeight = 0;

  for (const signal of correctionSignals) {
    const match = trimmed.match(signal.pattern);
    if (match) {
      // 弱信号需要更多上下文验证
      if (signal.weight < 0.5 && !assistantContext) {
        continue;
      }
      if (signal.weight > bestWeight) {
        bestWeight = signal.weight;
        bestMatch = {
          detected: true,
          category: signal.weight >= 0.7 ? 'correction' : 'weak_correction',
          label: signal.label,
          confidence: signal.weight,
          matchedPattern: match[0],
          raw: trimmed.slice(0, 100),
          context: assistantContext.slice(0, 50),
        };
      }
    }
  }

  return bestMatch;
}

/**
 * 格式化检测结果为 markdown 条目
 */
function formatMarkdownEntry(result, timestamp) {
  return [
    `### ${timestamp}`,
    `- **信号**: ${result.label} "${result.matchedPattern}"`,
    `- **用户说**: ${result.raw}`,
    `- **上下文**: ${result.context || '(无)'} `,
    `- **类别**: ${result.category}`,
    `- **置信度**: ${result.confidence.toFixed(2)}`,
    `- **已处理**: ⬜`,
    ``,
  ].join('\n');
}

// CLI 模式
if (require.main === module) {
  const userMsg = process.argv[2] || '';
  const context = process.argv[3] || '';
  
  const result = detect(userMsg, context);
  
  if (result) {
    console.log(JSON.stringify(result, null, 2));
    process.exit(0);
  } else {
    process.exit(1);
  }
}

module.exports = { detect, formatMarkdownEntry, correctionSignals };
