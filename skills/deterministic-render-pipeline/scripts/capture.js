// 确定性场景无头逐帧采帧（__seek/__ready 协议）
// 用法: node capture.js [outDir] [fps]
//   环境变量: CAPTURE_URL（默认 http://127.0.0.1:8123）、CAPTURE_STYLE、CAPTURE_VIEW
//   CAPTURE_STYLE/VIEW 会拼成 ?style=..&view=.. 加到 URL，页面侧自行解析切换
// 前提: 页面暴露 window.__seek(t)（幂等推进到绝对时间 t 秒）与 window.__ready === true
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const outDir = process.argv[2] ?? 'frames';
const fps = Number(process.argv[3] ?? 30);
const N = 360; // 12s × 30fps；改片长就改这里
const baseUrl = process.env.CAPTURE_URL ?? 'http://127.0.0.1:8123';
const style = process.env.CAPTURE_STYLE;
const view = process.env.CAPTURE_VIEW;

const q = new URLSearchParams();
if (style) q.set('style', style);
if (view) q.set('view', view);
const pageUrl = q.toString() ? `${baseUrl}/?${q}` : baseUrl + '/';

fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('pageerror', e => { console.error('PAGE ERROR:', e.message); process.exit(1); });
await page.goto(pageUrl);
await page.waitForFunction('window.__ready === true');

for (let i = 0; i < N; i++) {
  const t = i / fps;
  await page.evaluate(t => window.__seek(t), t);
  const file = path.join(outDir, String(i).padStart(4, '0') + '.png');
  await page.screenshot({ path: file });
  if (i % 60 === 0) console.log(`frame ${i}/${N}`);
}
await browser.close();
console.log(`done: ${N} frames -> ${outDir}`);
