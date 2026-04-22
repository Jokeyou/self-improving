const { detect } = require('./correction-detector.js');

const tests = [
  '不对，端口应该是8334',
  '错了，密码不对',
  '等等，这个IP我看看',
  '行吧，就这样',
  'no, thats not right',
  'actually, i prefer the other way',
  '看起来不错',
  '等等，先别发送',
  '怎么又犯同样的错误',
];

tests.forEach(t => {
  const r = detect(t);
  console.log('---');
  console.log('输入:', t);
  console.log('结果:', r ? `[${r.label}] 置信度:${r.confidence}` : '无信号');
});
