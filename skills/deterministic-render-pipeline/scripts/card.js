// 片尾卡采帧：独立 endcard 页同样走 __seek/__ready 协议
// 用法: node card.js   （环境变量 CAPTURE_URL 同 capture.js；endcard 路径可在下方改）
// 默认 90 帧 = 3s@30fps，与 12s 正片 concat 成 15s 成片
import { chromium } from 'playwright';
import fs from 'node:fs';

const baseUrl = process.env.CAPTURE_URL ?? 'http://127.0.0.1:8123';
const endcardPath = process.env.ENDCARD_PATH ?? 'render/endcard.html'; // 相对项目根
const N = 90;

fs.mkdirSync('frames-card', { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('pageerror', e => { console.error('PAGE ERROR:', e.message); process.exit(1); });
await page.goto(`${baseUrl}/${endcardPath}`);
await page.waitForFunction('window.__ready === true');
for (let i = 0; i < N; i++) {
  await page.evaluate(t => window.__seek(t), i / 30);
  await page.screenshot({ path: `frames-card/${String(i).padStart(4, '0')}.png` });
}
await browser.close();
console.log(`endcard ${N} frames -> frames-card/`);
