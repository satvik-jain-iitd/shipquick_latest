# Two live links: dev and production

Story #120. The owner tests every change by hand on a dev link before it reaches real users on a production link. This rule is generic — it names no host.

## The rule

- **Two environments from the first deploy.** `dev` branch deploys to the dev link, `main` deploys to the production link. Both start from the same commit, so they look and work the same on day one.
- **Every story merges to `dev` first** and shows up on the dev link. No story skips straight to production.
- **Promotion is one `dev -> main` release PR.** Its body carries a `## UAT on dev (<dev link>)` checklist (`docs/templates/uat-checklist.md`): one box per story, "Old flows still work", "Design matches the approved boards", and a `Known bugs going to production:` line. Every story line is followable by a new user: the exact link and test data, numbered one-action steps, and an **Expected:** line with exact text. `scripts/review_merge.sh` refuses to merge a PR into `main` while the section is missing, a story line is not followable (`scripts/check_uat.py`), or any box is still unticked — in every mode, even auto. The owner ticks every box on the dev link itself.
- **Separate data.** Dev uses its own database, keys and webhooks. It never writes to production data.
- **Both links are visible.** `Dev link:` and `Production link:` sit at the top of the project's `CLAUDE.md` (see the project template) and on the live roadmap page. `scripts/check_environments.sh` fails a project's own CI once it is past milestone D0 and either line is still empty or a placeholder.
- **Drift check.** After a promotion, `main` and `dev` should point at the same app code. `scripts/env_drift.sh` compares the two branches and prints what is only on dev.

## Worked examples

These are examples of hosts that fit the rule above — not a requirement to use any of them.

### Example: Vercel
- `main` and `dev` each get their own Vercel project (or one project with `main` as Production and `dev` as a named Preview/branch deployment).
- `Production link:` is the project's production domain. `Dev link:` is the branch deployment URL for `dev` (Vercel gives every branch a stable URL when branch deployments are turned on).
- Separate data: a second Postgres/Neon/Supabase instance (or a separate schema) wired to the `dev` deployment's env vars only.

### Example: Cloudflare (Workers / Pages)
- Two Wrangler environments in `wrangler.toml` (`[env.dev]`, default/production), each with its own routes and bindings, or two separate Workers/Pages projects.
- `Production link:` is the production route (custom domain or `*.workers.dev` / `*.pages.dev` default). `Dev link:` is the dev environment's route.
- Separate data: separate D1 database / KV namespace / R2 bucket IDs per environment, set in each `[env.*]` block.

### Example: a VM (self-hosted, e.g. the Oracle box)
- Two systemd services (or two ports behind the same reverse proxy) running the `main` and `dev` checkouts, each with its own `.env`.
- `Production link:` points at the production port/subdomain; `Dev link:` at the dev port/subdomain (for example `dev.project.example.com`).
- Separate data: a separate SQLite file or Postgres database per checkout; deploy `dev` on every push to `dev`, deploy `main` only after a reviewed promotion PR.
