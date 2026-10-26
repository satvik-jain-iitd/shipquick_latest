#!/usr/bin/env node
// ROADMAP.md from GitHub data (story #49, docs/LIVE_ROADMAP.md). The reusable workflow .github/workflows/roadmap.yml runs this.
//   node roadmap/roadmap.js <github-answer.json> <roadmap.json> [ROADMAP.md]     (no third argument: print the page)
// The page has no clock inside, so an unchanged project makes no new commit. render.js (the HTML page) stays as it is; this file only writes Markdown.
const fs = require('node:fs');
const { build, fromGraphql, MAX_NODES } = require('./render.js');

// Text from GitHub is data: neutralise every character that Markdown or HTML would act on (a link, a tag, a table cell).
const esc = (t) => String(t == null ? '' : t).replace(/\s+/g, ' ').replace(/[\\`*_[\]()|<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c] || '\\' + c));

function markdown(resp, project) {
  const d = fromGraphql(resp), model = build(d.issues, d.prs), stories = model.stories;
  const epicName = Object.fromEntries(model.epics.map(e => [e.number, e.title]));
  const link = (n) => project.repo ? `[#${n}](https://github.com/${project.repo}/issues/${n})` : `#${n}`;
  const closed = stories.filter(s => s.column === 'Done').sort((a, b) => String(b.closedAt).localeCompare(String(a.closedAt)));
  const byEpic = new Map(); for (const s of closed) byEpic.set(s.epic || 0, (byEpic.get(s.epic || 0) || []).concat(s));   // newest story first, so the epic with the newest story is first
  const delivered = [...byEpic].map(([k, list]) => `<details><summary><b>${esc(epicName[k] || 'Other work')}</b> · ${list.length} done</summary>\n\n${list.map(s => `- ${esc(s.text)} ${link(s.number)}`).join('\n')}\n\n</details>`).join('\n\n');
  const now = stories.filter(s => s.column === 'Doing' || s.column === 'Review').map(s => `- **${esc(s.text)}** · ${s.column.toLowerCase()} · ${link(s.number)}`).join('\n');
  const next = model.epics.concat([{ number: null, title: 'Other work' }]).map(e => ({ e, list: stories.filter(s => s.column === 'To do' && (s.epic || null) === e.number) })).filter(x => x.list.length)
    .map(({ e, list }) => `### ${esc(e.title)}\n\n${list.map(s => `- ${esc(s.text)} ${link(s.number)}`).join('\n')}`).join('\n\n');
  const cols = ['To do', 'Doing', 'Review', 'Done'], cell = (c) => stories.filter(s => s.column === c).map(s => `${esc(s.raw)} ${link(s.number)}`).join('<br><br>');
  const needs = stories.filter(s => s.needsWords).length;
  const notes = [needs ? `${needs} ${needs === 1 ? 'story still needs' : 'stories still need'} plain words` : '', d.truncated ? `Showing the newest ${MAX_NODES} issues only` : ''].filter(Boolean).join(' · ');
  return `# ${esc(project.title)} roadmap

_${closed.length} of ${stories.length} stories done. Written by the ShipQuick roadmap workflow from the issues and pull requests. Do not edit by hand.${notes ? ' ' + notes + '.' : ''}_

## Vision

> ${esc(project.vision)}

## Delivered

${delivered || 'Nothing finished yet.'}

## Now

${now || 'Nothing is being built right now.'}

## Next

${next || 'Nothing is queued.'}

## Board

| ${cols.join(' | ')} |
| ${cols.map(() => '---').join(' | ')} |
| ${cols.map(cell).join(' | ')} |
`;
}

function run(respFile, settingsFile, outFile, env) {
  const settings = JSON.parse(fs.readFileSync(settingsFile, 'utf8'));
  for (const f of ['title', 'vision']) if (typeof settings[f] !== 'string' || !settings[f].trim()) throw new Error(`${settingsFile}: "${f}" is missing. roadmap.json needs a title and a vision line.`);
  const text = markdown(JSON.parse(fs.readFileSync(respFile, 'utf8')), { title: settings.title, vision: settings.vision, repo: (env || process.env).GITHUB_REPOSITORY });
  if (outFile) fs.writeFileSync(outFile, text); else process.stdout.write(text);   // the page is built before anything is written: an error leaves the old file alone
}

if (require.main === module) {
  try { run(process.argv[2], process.argv[3], process.argv[4]); } catch (e) { console.error(e.message); process.exit(1); }
}
module.exports = { markdown, run };
