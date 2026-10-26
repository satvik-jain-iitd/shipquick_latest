// The live roadmap page (story #44, docs/LIVE_ROADMAP.md). Ported from GoServe scripts/roadmap.py (radar log: docs/research/repo-radar.md).
// Pure functions: GitHub data goes in, one HTML page comes out. No require, so build.js can paste this file into an n8n Code node.
const COLUMNS = ['To do', 'Doing', 'Review', 'Done'];
const MAX_NODES = 100;   // ponytail: one GitHub page of issues; `truncated` tells the page when there are more. Add paging when a project passes 100 issues.
// Words a stranger does not need. The Board keeps the story's own words (raw); every other section gets the plain swap.
const PLAIN = [[/\bCI\/CD\b/g, 'build and deploy'], [/\bPRs?\b/g, 'change'], [/\bCI checks\b/g, 'checks'], [/\bCI\b/g, 'the checks'], [/\brpc\b/gi, 'server call'], [/\bmigrations?\b/gi, 'database change'], [/\be2e\b/gi, 'end-to-end test']];
const plain = (t) => PLAIN.reduce((s, [re, w]) => s.replace(re, w), t);
const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function section(body, name) {
  const m = new RegExp('^##\\s+' + name + '\\s*\\n([\\s\\S]*?)(?=^##\\s|$(?![\\s\\S]))', 'm').exec(body || '');
  return m ? m[1].trim() : '';
}
function firstSentence(text) {
  const line = (text || '').trim().split('\n')[0].replace(/^[-*]\s+/, '').trim(), m = /^(.+?[.!?])(\s|$)/.exec(line);
  return (m ? m[1] : line).trim();
}
// The roadmap words of a story: the first sentence under "## Business", or a "**Business line:**" line.
function businessLine(body) {
  const own = /^\*\*Business line:\*\*\s*(.+)$/m.exec(body || '');
  return firstSentence(own ? own[1] : section(body, 'Business'));
}
function epicOf(issue) {
  if (issue.parent) return issue.parent.number;
  const m = /Part of (?:epic )?(?:E\d+\s*)?\(?#(\d+)/i.exec(issue.body || '');
  return m ? Number(m[1]) : null;
}
const prFor = (n, prs) => prs.find(p => p.title.includes('(#' + n + ')') || new RegExp('^[\\w-]+/' + n + '-').test(p.headRefName || ''));
function column(issue, pr) {
  if (issue.state === 'CLOSED') return 'Done';
  if (!pr) return issue.labels.includes('doing') ? 'Doing' : 'To do';
  const green = pr.checks.length > 0 && pr.checks.every(c => (c.conclusion || '').toUpperCase() === 'SUCCESS');
  return green && !pr.isDraft ? 'Review' : 'Doing';
}

// The page's data: epics in number order, stories with their epic, column, sentence and pull request.
function build(issues, prs) {
  const epics = issues.filter(i => i.labels.includes('epic')).sort((a, b) => a.number - b.number);
  const stories = issues.filter(i => i.labels.includes('story') || i.labels.includes('user-story')).sort((a, b) => a.number - b.number).map(i => {
    const pr = prFor(i.number, prs) || null, sentence = businessLine(i.body);
    return { number: i.number, title: i.title, epic: epicOf(i), state: i.state, closedAt: i.closedAt, pr, column: column(i, pr), raw: sentence || i.title, text: plain(sentence || i.title), needsWords: !sentence };
  });
  return { epics: epics.map(e => ({ number: e.number, title: plain(e.title.replace(/^(Epic|Feature):?\s*(E\d+:?)?\s*/i, '')), state: e.state })), stories };
}

// GitHub GraphQL answer (see roadmap/build.js, QUERY) -> {issues, prs, truncated}. An error answer throws, so nothing is saved.
function fromGraphql(resp) {
  if (resp.errors || !resp.data || !resp.data.repository) throw new Error('GitHub: ' + ((resp.errors || []).map(e => e.message).join('; ') || 'no data'));
  const r = resp.data.repository;
  return {
    truncated: !!((r.issues.pageInfo || {}).hasNextPage || (r.pullRequests.pageInfo || {}).hasNextPage),
    issues: r.issues.nodes.map(n => ({ ...n, labels: n.labels.nodes.map(l => l.name) })),
    prs: r.pullRequests.nodes.map(p => {
      const roll = (((p.commits.nodes[0] || {}).commit || {}).statusCheckRollup || {}).state;
      return { number: p.number, title: p.title, headRefName: p.headRefName, isDraft: p.isDraft, checks: roll ? [{ conclusion: roll }] : [] };
    }),
  };
}

function render(model, project, now) {
  const stories = model.stories, epicName = Object.fromEntries(model.epics.map(e => [e.number, e.title]));
  const hhmm = new Date(now.getTime() + 19800000).toISOString().slice(11, 16);   // India time, UTC + 5:30
  const closedStories = stories.filter(s => s.column === 'Done').sort((a, b) => String(b.closedAt).localeCompare(String(a.closedAt)));
  const byEpic = new Map(); for (const s of closedStories) { const k = s.epic || 0; byEpic.set(k, (byEpic.get(k) || []).concat(s)); }   // Map keeps the order of the newest story first
  const delivered = [...byEpic].map(([k, list]) => `<details><summary><b>${esc(epicName[k] || 'Other work')}</b> <span class="mono">${list.length} done</span></summary><ul>${list.map(s => `<li>${esc(s.text)}</li>`).join('')}</ul></details>`).join('');
  const nowRows = stories.filter(s => s.column === 'Doing' || s.column === 'Review').map(s => `<li><b>${esc(s.text)}</b> <span class="mono">${s.column.toLowerCase()}</span></li>`).join('') || '<li>Nothing is being built right now.</li>';
  const nextRows = model.epics.concat([{ number: null, title: 'Other work' }]).map(e => ({ e, list: stories.filter(s => s.column === 'To do' && (s.epic || null) === e.number) })).filter(x => x.list.length)
    .map(({ e, list }) => `<li><b>${esc(e.title)}</b><ul>${list.map(s => `<li>${esc(s.text)}</li>`).join('')}</ul></li>`).join('') || '<li>Nothing is queued.</li>';
  const board = COLUMNS.map(c => `<section class="col"><h3>${c} <span class="mono">${stories.filter(s => s.column === c).length}</span></h3>` + stories.filter(s => s.column === c).map(s =>
    `<div class="card" data-story="${s.number}"><span class="tag">${esc(epicName[s.epic] || 'no epic')}</span><p>${esc(s.raw)}</p><span class="mono">#${s.number}${s.pr ? ' · PR #' + s.pr.number : ''}</span></div>`).join('') + '</section>').join('');
  const needs = stories.filter(s => s.needsWords).length, done = closedStories.length;
  const notes = [needs ? `<span class="needs">${needs} ${needs === 1 ? 'story still needs' : 'stories still need'} plain words</span>` : '', project.truncated ? `<span class="needs">Showing the newest ${MAX_NODES} issues only.</span>` : ''].filter(Boolean).join(' · ');
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="300"><title>${esc(project.title)} roadmap</title>
<style>
:root { --primary:#3B82F6; --dark:#2563EB; --text:#1F2937; --bg:#FFFFFF; --muted:#6B7280; --alt:#F3F4F6; --error:#B3261E; }
body { margin:0; background:var(--bg); color:var(--text); font:17px/1.5 Roboto, system-ui, sans-serif; }
main { max-width:960px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:32px; margin:0 0 4px; } h2 { font-size:22px; margin:40px 0 12px; border-bottom:2px solid var(--primary); padding-bottom:4px; } h3 { font-size:16px; margin:0 0 8px; }
.mono { font-family:ui-monospace, monospace; font-size:13px; color:var(--muted); }
.vision { background:var(--alt); border-left:4px solid var(--dark); border-radius:6px; padding:16px 20px; font-size:20px; }
details { background:var(--alt); border-radius:6px; padding:10px 16px; margin:8px 0; } summary { cursor:pointer; }
ul { padding-left:20px; } li { margin:4px 0; }
.board { display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; } @media (max-width:720px) { .board { grid-template-columns:1fr 1fr; } }
.col { background:var(--alt); border-radius:6px; padding:10px; min-height:80px; }
.card { background:var(--bg); border:1px solid #E5E7EB; border-radius:6px; padding:10px 12px; margin:8px 0; font-size:15px; } .card p { margin:6px 0; }
.tag { display:inline-block; background:var(--primary); color:#fff; border-radius:999px; padding:1px 10px; font-size:12px; }
footer { margin-top:40px; } .needs { color:var(--error); }
</style></head><body><main>
<h1>${esc(project.title)} roadmap</h1><p class="mono">updated ${hhmm} IST · ${done} of ${stories.length} stories done</p>
<section id="vision"><h2>Vision</h2><div class="vision">${esc(project.vision)}</div></section>
<section id="delivered"><h2>Delivered</h2>${delivered || '<p>Nothing finished yet.</p>'}</section>
<section id="now"><h2>Now</h2><ul>${nowRows}</ul></section>
<section id="next"><h2>Next</h2><ul>${nextRows}</ul></section>
<section id="board"><h2>Board</h2><div class="board">${board}</div></section>
<footer class="mono">${notes ? notes + ' · ' : ''}made by roadmap/render.js from the GitHub issues and pull requests</footer>
</main></body></html>
`;
}

const page = (resp, project, now) => { const d = fromGraphql(resp); return render(build(d.issues, d.prs), { ...project, truncated: d.truncated }, now); };
module.exports = { build, render, fromGraphql, page, businessLine, plain, MAX_NODES };
