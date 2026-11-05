// Template for story #146 (docs/SCREENS.md). Copy to <SCREENS_APP_DIR>/<SCREENS_SPEC>
// (default tests/e2e/screens.spec.ts) and fill in STEPS for your own screens. Every screen listed in
// docs/screens.txt is rendered and compared with its accepted picture. Adding a screen means adding a
// line to docs/screens.txt, never a new spec -- unless it needs a setup step nothing else does yet.
import { test, expect, type BrowserContext, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Scoped retry: a screens spec exists to catch exactly the kind of change retries paper over
// (docs/SCREENS.md). Keep the rest of your e2e suite's own retry policy untouched.
test.describe.configure({ retries: 0 });

type Screen = { name: string; path: string; width: number; height: number; step: string };

// Adjust the relative path if this spec does not sit three levels under the repo root.
const screens: Screen[] = readFileSync(resolve(import.meta.dirname, "../../../docs/screens.txt"), "utf8")
  .split("\n")
  .map((l) => l.trim())
  .filter((l) => l && !l.startsWith("#"))
  .map((l) => {
    const [name, path, vp, step] = l.split("|").map((x) => x.trim());
    const [width, height] = vp.split("x").map(Number);
    return { name, path, width, height, step };
  });

// A fixed instant for anything the screen renders that depends on the clock (a greeting, a relative
// timestamp). Pick one that exercises your real copy, not midnight.
const FIXED_TIME = new Date(2026, 0, 1, 9, 0, 0);

// One function per setup step named in docs/screens.txt's fourth column. Each one gets the screen to
// the state it should be screenshotted in -- log in, add an item to a cart, open a drawer, whatever
// your other e2e specs already do to reach that screen.
const STEPS: Record<string, (context: BrowserContext, page: Page, path: string) => Promise<void>> = {
  // home: async (context, page, path) => { await page.goto(path); await expect(page.getByRole("heading", { name: "Home" })).toBeVisible(); },
};

test("every screen in docs/screens.txt names a known setup step", () => {
  expect(screens.length).toBeGreaterThan(0);
  for (const s of screens) {
    expect(Object.keys(STEPS), `${s.name}: unknown setup step "${s.step}" -- add it to STEPS above`).toContain(s.step);
  }
});

for (const s of screens) {
  test(`screen ${s.name} matches its accepted picture`, async ({ page, context }) => {
    await page.clock.install({ time: FIXED_TIME });
    await page.setViewportSize({ width: s.width, height: s.height });
    await STEPS[s.step](context, page, s.path);
    await page.evaluate(() => document.fonts.ready);   // self-host your fonts, docs/SCREENS.md
    if (process.env.SCREENS_OUT) {
      await page.screenshot({ path: `${process.env.SCREENS_OUT}/${s.name}.png` });
    }
    if (process.env.SCREENS_RENDER_ONLY) return;
    // maxDiffPixels: 10 is set here too, not only in playwright.config.ts (docs/SCREENS.md), so a
    // copied template is right even if the project's own config is never touched.
    await expect(page).toHaveScreenshot(`${s.name}.png`, { maxDiffPixels: 10 });
  });
}
