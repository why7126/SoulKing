import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const events = [];
page.on("console", (msg) => events.push(`console:${msg.text()}`));

await page.goto("http://127.0.0.1:8000/", { waitUntil: "networkidle" });
await page.waitForTimeout(800);

const before = await page.evaluate(() => ({
  hidden: document.querySelector("#frontUserMenu")?.classList.contains("hidden"),
  display: getComputedStyle(document.querySelector("#frontUserMenu")).display,
  bound: document.querySelector("#frontUserMenuBtn")?.dataset.skUserMenuBound,
}));

await page.click("#frontUserMenuBtn");
await page.waitForTimeout(400);

const after = await page.evaluate(() => ({
  hidden: document.querySelector("#frontUserMenu")?.classList.contains("hidden"),
  display: getComputedStyle(document.querySelector("#frontUserMenu")).display,
  expanded: document.querySelector("#frontUserMenuBtn")?.getAttribute("aria-expanded"),
  rect: (() => {
    const r = document.querySelector("#frontUserMenu")?.getBoundingClientRect();
    return r ? { top: r.top, left: r.left, width: r.width, height: r.height } : null;
  })(),
}));

console.log(JSON.stringify({ before, after, events }, null, 2));
await browser.close();
