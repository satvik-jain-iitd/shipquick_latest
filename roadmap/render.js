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
// Story #82: the data behind the time, order and dependency views (docs/LIVE_ROADMAP.md). Labels P0..P9 give the priority; `Needs: #n, #m` lines
// give the dependencies; the start is the first `doing` label time, or a `Started: <UTC time>` line in the body when the label was never set.
const prioOf = (labels) => { const p = labels.map(l => /^P(\d)$/.exec(l)).filter(Boolean).map(m => Number(m[1])); return p.length ? Math.min(...p) : null; };
const needsOf = (body) => (String(body || '').match(/^Needs:.*$/gm) || []).flatMap(l => [...l.matchAll(/#(\d+)/g)].map(m => Number(m[1])));
const startOf = (issue) => { const m = /^Started:\s*(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z)/m.exec(issue.body || ''); return issue.doingAt || (m ? m[1] : null); };
// Story #83: days and clock times in the project's timezone (an input, default Asia/Kolkata). Intl does the zone maths, so the machine's own zone never matters.
const TZ = 'Asia/Kolkata', MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const dayOf = (iso, tz) => new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(iso));   // 2026-10-25
const dayLabel = (day) => Number(day.slice(8)) + ' ' + MON[Number(day.slice(5, 7)) - 1];   // 25 Oct (own month names: ICU spells September differently by version)
const hm = (iso, tz) => new Intl.DateTimeFormat('en-GB', { timeZone: tz, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(new Date(iso));
const zoneName = (tz, at) => (new Intl.DateTimeFormat('en-IN', { timeZone: tz, timeZoneName: 'short' }).formatToParts(at).find(p => p.type === 'timeZoneName') || {}).value || tz;
const at = (iso, tz, day) => (dayOf(iso, tz) === day ? '' : dayLabel(dayOf(iso, tz)) + ' ') + hm(iso, tz);   // the date only when it is not the day in view
const took = (m) => m == null ? 'no start time' : m < 60 ? m + ' min' : Math.floor(m / 60) + ' h' + (m % 60 ? ' ' + (m % 60) + ' min' : '');   // shortcut: hours, no days; add days when a story runs past a day often
const minutes = (from, to) => from && to ? Math.round((new Date(to) - new Date(from)) / 60000) : null;
function column(issue, pr) {
  if (issue.state === 'CLOSED') return 'Done';
  if (!pr) return issue.labels.includes('doing') ? 'Doing' : 'To do';
  const green = pr.checks.length > 0 && pr.checks.every(c => (c.conclusion || '').toUpperCase() === 'SUCCESS');
  return green && !pr.isDraft ? 'Review' : 'Doing';
}

// The page's data: epics in number order, stories with their epic, column, sentence and pull request.
function build(issues, prs, tz = TZ) {
  const epics = issues.filter(i => i.labels.includes('epic')).sort((a, b) => a.number - b.number);
  const isStory = (i) => i.labels.includes('story') || i.labels.includes('user-story');
  const open = new Set(issues.filter(i => isStory(i) && i.state !== 'CLOSED').map(i => i.number));   // a Needs number is a blocker only while it is an open story
  const stories = issues.filter(isStory).sort((a, b) => a.number - b.number).map(i => {
    const pr = prFor(i.number, prs) || null, sentence = businessLine(i.body), needs = needsOf(i.body), started = startOf(i);
    return { number: i.number, title: i.title, epic: epicOf(i), state: i.state, createdAt: i.createdAt || null, closedAt: i.closedAt, pr, column: column(i, pr), raw: sentence || i.title, text: plain(sentence || i.title), needsWords: !sentence,
      milestone: i.milestone ? i.milestone.title : null, prio: prioOf(i.labels), needs, blockedBy: needs.filter(n => open.has(n)), started, cycleMin: minutes(started, i.closedAt) };
  });
  // You are here, Next and older work. A plan label decides: doing is in progress; ready or blocked is planned (Next); none is older work.
  const labels = Object.fromEntries(issues.map(i => [i.number, i.labels])), has = (s, l) => labels[s.number].includes(l);
  const due = Object.fromEntries(issues.filter(i => i.milestone).map(i => [i.milestone.title, i.milestone.dueOn || '9999']));
  const msKey = (s) => s.milestone ? due[s.milestone] + ' ' + s.milestone : '\uffff';   // earliest due milestone first, no milestone last
  const openStories = stories.filter(s => s.state !== 'CLOSED');
  const next = openStories.filter(s => !has(s, 'doing') && (has(s, 'ready') || has(s, 'blocked')))
    .sort((a, b) => msKey(a).localeCompare(msKey(b)) || (a.prio == null ? 9 : a.prio) - (b.prio == null ? 9 : b.prio) || a.number - b.number);
  const older = openStories.filter(s => s.column === 'To do' && !['doing', 'ready', 'blocked'].some(l => has(s, l)));
  const here = { doing: openStories.filter(s => has(s, 'doing')), next: next.find(s => has(s, 'ready') && !s.blockedBy.length) || null };
  const timeline = [];
  for (const s of stories.filter(x => x.state === 'CLOSED' && x.closedAt).sort((a, b) => b.closedAt.localeCompare(a.closedAt))) {
    const day = dayOf(s.closedAt, tz), last = timeline[timeline.length - 1];
    if (last && last.day === day) last.stories.push(s); else timeline.push({ day, stories: [s] });
  }
  return { tz, timeline, here, next, older, epics: epics.map(e => ({ number: e.number, title: plain(e.title.replace(/^(Epic|Feature):?\s*(E\d+:?)?\s*/i, '')), state: e.state })), stories };
}

// GitHub GraphQL answer (see roadmap/build.js, QUERY) -> {issues, prs, truncated}. An error answer throws, so nothing is saved.
function fromGraphql(resp) {
  if (resp.errors || !resp.data || !resp.data.repository) throw new Error('GitHub: ' + ((resp.errors || []).map(e => e.message).join('; ') || 'no data'));
  const r = resp.data.repository;
  return {
    truncated: !!((r.issues.pageInfo || {}).hasNextPage || (r.pullRequests.pageInfo || {}).hasNextPage),
    issues: r.issues.nodes.map(n => {
      const doing = ((n.timelineItems || {}).nodes || []).filter(t => (t.label || {}).name === 'doing').map(t => t.createdAt).sort();   // the first time the label went on
      return { ...n, labels: n.labels.nodes.map(l => l.name), doingAt: doing[0] || null };
    }),
    prs: r.pullRequests.nodes.map(p => {
      const roll = (((p.commits.nodes[0] || {}).commit || {}).statusCheckRollup || {}).state;
      return { number: p.number, title: p.title, headRefName: p.headRefName, isDraft: p.isDraft, checks: roll ? [{ conclusion: roll }] : [] };
    }),
  };
}

function render(model, project, now) {
  const stories = model.stories, epicName = Object.fromEntries(model.epics.map(e => [e.number, e.title]));
  const tz = project.timezone || model.tz || TZ, hhmm = hm(now, tz), today = dayOf(now, tz), tzName = zoneName(tz, now);
  const closedStories = stories.filter(s => s.column === 'Done').sort((a, b) => String(b.closedAt).localeCompare(String(a.closedAt)));
  const byEpic = new Map(); for (const s of closedStories) { const k = s.epic || 0; byEpic.set(k, (byEpic.get(k) || []).concat(s)); }   // Map keeps the order of the newest story first
  const range = (list) => { const days = list.filter(s => s.closedAt).map(s => dayOf(s.closedAt, tz)).sort(), a = days[0], b = days[days.length - 1];
    return a ? ' · ' + dayLabel(a) + (b !== a ? ' to ' + dayLabel(b) : '') : ''; };
  const delivered = [...byEpic].map(([k, list]) => `<details><summary><b>${esc(epicName[k] || 'Other work')}</b> <span class="mono">${list.length} done${range(list)}</span></summary><ul>${list.map(s => `<li>${esc(s.text)}</li>`).join('')}</ul></details>`).join('');
  const nowRows = stories.filter(s => s.column === 'Doing' || s.column === 'Review').map(s => `<li><b>${esc(s.text)}</b> <span class="mono">${s.column.toLowerCase()}</span></li>`).join('') || '<li>Nothing is being built right now.</li>';
  const here = model.here || { doing: [], next: null }, timeline = model.timeline || [], older = model.older || [];
  const hereRows = here.doing.map(s => `<li><b>${esc(s.text)}</b> <span class="mono">#${s.number} · ${s.started ? 'since ' + at(s.started, tz, today) : 'no start time'}</span></li>`).join('') || '<li>Nothing is in progress.</li>';
  const hereNext = here.next ? `<p>Next up: <b>${esc(here.next.text)}</b> <span class="mono">#${here.next.number}</span></p>` : '<p>No ready story is waiting.</p>';
  const nextRows = (model.next || []).map(s => `<li>${esc(s.text)} <span class="mono">#${s.number}${s.milestone ? ' · ' + esc(s.milestone) : ''}${s.prio == null ? '' : ' · P' + s.prio}</span>${s.blockedBy.length ? ` <span class="needs">blocked by ${s.blockedBy.map(n => '#' + n).join(', ')}</span>` : ''}</li>`).join('') || '<li>Nothing is queued.</li>';
  const olderBlock = older.length ? `<details><summary>${older.length} ${older.length === 1 ? 'story has' : 'stories have'} no plan yet</summary><ul>${older.map(s => `<li>${esc(s.text)} <span class="mono">#${s.number}</span></li>`).join('')}</ul></details>` : '<p>No older work.</p>';
  // shortcut: every close day is listed; fold the days past the first few when a project's timeline grows long.
  const timelineRows = timeline.map(d => `<h3>${dayLabel(d.day)}</h3><ul>${d.stories.map(s => `<li>${esc(s.text)} <span class="mono">#${s.number} · ${s.started ? 'start ' + at(s.started, tz, d.day) + ' · ' : ''}closed ${at(s.closedAt, tz, d.day)} · ${took(s.cycleMin)}</span></li>`).join('')}</ul>`).join('') || '<p>Nothing closed yet.</p>';
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
<h1>${esc(project.title)} roadmap</h1><p class="mono">updated ${hhmm} ${esc(tzName)} · ${done} of ${stories.length} stories done</p>
<section id="vision"><h2>Vision</h2><div class="vision">${esc(project.vision)}</div></section>
<section id="here"><h2>You are here</h2><p>It is ${hhmm} ${esc(tzName)}, ${dayLabel(today)}.</p><ul>${hereRows}</ul>${hereNext}</section>
<section id="delivered"><h2>Delivered</h2>${delivered || '<p>Nothing finished yet.</p>'}</section>
<section id="now"><h2>Now</h2><ul>${nowRows}</ul></section>
<section id="next"><h2>Next</h2><ol>${nextRows}</ol></section>
<section id="older"><h2>Older work</h2>${olderBlock}</section>
<section id="timeline"><h2>Timeline</h2>${timelineRows}</section>
<section id="board"><h2>Board</h2><div class="board">${board}</div></section>
<footer class="mono">${notes ? notes + ' · ' : ''}made by roadmap/render.js from the GitHub issues and pull requests</footer>
</main></body></html>
`;
}

const page = (resp, project, now) => { const d = fromGraphql(resp); return render(build(d.issues, d.prs, project.timezone || TZ), { ...project, truncated: d.truncated }, now); };
module.exports = { build, render, fromGraphql, page, businessLine, plain, MAX_NODES };
