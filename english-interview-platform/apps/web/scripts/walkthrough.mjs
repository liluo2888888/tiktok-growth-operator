/**
 * One-off UI walkthrough: Onboarding → Quest Map → Interview → Feedback → Passport
 * Run: node scripts/walkthrough.mjs
 */
import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(__dirname, "..", "walkthrough-screenshots");
const base = process.env.WALKTHROUGH_BASE ?? "http://localhost:5174";

async function shot(page, name) {
  const file = path.join(outDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`screenshot: ${file}`);
}

async function main() {
  await mkdir(outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  await page.goto(base);
  await page.evaluate(() => localStorage.clear());
  await page.goto(`${base}/onboarding`);
  await page.waitForLoadState("networkidle");
  await shot(page, "01-onboarding");

  await page.getByRole("button", { name: "下一步" }).click();
  await page.waitForTimeout(400);
  await shot(page, "02-onboarding-role");

  await page.getByRole("button", { name: "进入任务地图" }).click();
  await page.waitForURL("**/quest-map");
  await shot(page, "03-quest-map");

  const tile = page.locator(".mission-tile").first();
  await tile.hover();
  await page.waitForTimeout(300);
  await shot(page, "04-quest-map-hover");

  await tile.click();
  await page.waitForURL("**/quest-start**");
  await shot(page, "05-quest-start");

  await page.getByRole("button", { name: "开始练习" }).click();
  await page.waitForURL("**/interview**");
  await page.locator(".loading-block").waitFor({ state: "hidden", timeout: 25000 }).catch(() => {});
  const errBanner = page.locator(".error-banner");
  if (await errBanner.isVisible().catch(() => false)) {
    const msg = await errBanner.locator("p").textContent();
    throw new Error(`Interview failed to start: ${msg}`);
  }
  await page.waitForFunction(
    () => {
      const el = document.querySelector(".question-text");
      const t = el?.textContent?.trim() ?? "";
      return t.length > 15 && !t.startsWith("正在加载");
    },
    { timeout: 25000 }
  );
  await shot(page, "06-interview");

  const textarea = page.locator("#interview-answer");
  await textarea.click();
  await textarea.fill("");
  const answer =
    "I am a product manager with five years of experience building B2B SaaS tools. I enjoy turning user research into clear roadmaps and shipping iteratively with cross-functional teams.";
  await textarea.pressSequentially(answer, { delay: 5 });
  const submit = page.getByRole("button", { name: /提交并查看反馈/i });
  await page.waitForFunction(
    () => {
      const btn = document.querySelector("button.btn-primary");
      return btn && !btn.disabled && btn.textContent?.includes("提交");
    },
    { timeout: 25000 }
  );
  await shot(page, "07-interview-filled");

  await submit.click();
  await page.waitForURL("**/feedback**", { timeout: 30000 });
  await page.waitForSelector(".readiness-hero-value", { timeout: 30000 });
  await shot(page, "08-feedback");

  await page.getByLabel("主导航").getByRole("link", { name: "护照" }).click();
  await page.waitForURL("**/passport");
  await page.waitForTimeout(500);
  await shot(page, "09-passport");

  await page.goto(base);
  await page.waitForLoadState("networkidle");
  await shot(page, "10-home-manifesto");

  const errors = [];
  const checks = [["home-manifesto", await page.locator(".home-manifesto").count()]];
  await page.goto(`${base}/quest-map`);
  checks.push(["mission tiles", await page.locator(".mission-tile").count()]);
  checks.push(["mission-tile-arrow", await page.locator(".mission-tile-arrow").count()]);

  console.log("\n--- checks ---");
  for (const [name, count] of checks) {
    console.log(`${name}: ${count}`);
    if (count === 0) errors.push(`Missing: ${name}`);
  }

  await browser.close();
  if (errors.length) {
    console.error("FAILED:", errors.join("; "));
    process.exit(1);
  }
  console.log("\nWalkthrough complete.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
