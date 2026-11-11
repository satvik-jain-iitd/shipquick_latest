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

// Story #83 part (b): the dependency map, the longest chain and the milestone clock (docs/LIVE_ROADMAP.md).
// Arcs are [low, high] positions on one line. Two arcs cross when they interleave (a < c < b < d); nested or touching arcs do not.
const crossings = (arcs) => arcs.reduce((n, [a, b], i) => n + arcs.slice(i + 1).filter(([c, d]) => (a < c && c < b && b < d) || (c < a && a < d && d < b)).length, 0);
const perms = (xs) => xs.length < 2 ? [xs] : xs.flatMap((x, i) => perms(xs.slice(0, i).concat(xs.slice(i + 1))).map(p => [x].concat(p)));
const MAX_SEARCH = 7;   // shortcut: every order is tried up to 7 milestones (5040 orders); past that the due order stays. Add a greedy swap pass when a project has more.
// One edge per pair of milestones: a story in `to` waits for a story in `from`. Needs inside one milestone are not edges. A forward arrow that only
// repeats a longer path (A to B to C hides A to C) is left out. Nodes come in due order unless another order has fewer crossings.
function depMap(stories, milestones) {
  const pos = Object.fromEntries(milestones.map((m, i) => [m.title, i])), byN = Object.fromEntries(stories.map(s => [s.number, s])), count = new Map();
  for (const st of stories) for (const n of st.needs) {
    const dep = byN[n], k = dep && JSON.stringify([dep.milestone, st.milestone]);
    if (dep && dep.milestone && st.milestone && dep.milestone !== st.milestone) count.set(k, (count.get(k) || 0) + 1);
  }
  const edges = [...count].map(([k, c]) => { const [a, b] = JSON.parse(k); return { from: a, to: b, count: c, back: pos[a] > pos[b] }; })
    .sort((x, y) => pos[x.from] - pos[y.from] || pos[x.to] - pos[y.to]);
  const fwd = {}; for (const e of edges) if (!e.back) (fwd[e.from] = fwd[e.from] || []).push(e.to);
  const reach = (a, b) => {   // is b reachable from a without the direct a to b arrow?
    const seen = new Set(), todo = (fwd[a] || []).filter(x => x !== b);
    while (todo.length) { const x = todo.pop(); if (x === b) return true; if (!seen.has(x)) { seen.add(x); todo.push(...(fwd[x] || [])); } }
    return false;
  };
  const kept = edges.filter(e => e.back || !reach(e.from, e.to));
  const arcs = (order) => { const p = Object.fromEntries(order.map((t, i) => [t, i])); return kept.map(e => [p[e.from], p[e.to]].sort((x, y) => x - y)); };
  let nodes = milestones.map(m => m.title), best = crossings(arcs(nodes));
  if (best && nodes.length <= MAX_SEARCH) for (const o of perms(nodes)) { const n = crossings(arcs(o)); if (n < best) { nodes = o; best = n; } }
  return { nodes, edges: kept, hidden: edges.length - kept.length, crossings: best };
}
// The longest line of open stories where each waits for the one before. Ties go to the lowest story numbers (the reference's rule, memo included).
function longestChain(stories) {
  const open = new Map(stories.filter(s => s.state !== 'CLOSED').map(s => [s.number, s])), best = new Map();
  const lex = (a, b) => { for (let i = 0; i < Math.min(a.length, b.length); i++) if (a[i] !== b[i]) return a[i] - b[i]; return a.length - b.length; };
  const pick = (list, dflt) => list.reduce((w, c) => (c.length - w.length || -lex(c, w)) > 0 ? c : w, list[0] || dflt);
  const chain = (n, seen) => {
    if (!best.has(n)) best.set(n, pick(open.get(n).needs.filter(d => open.has(d) && !seen.includes(d)).map(d => chain(d, seen.concat(n)).concat(n)), [n]));
    return best.get(n);
  };
  return pick([...open.keys()].map(n => chain(n, [])), []).map(n => open.get(n));
}
const daysBetween = (a, b) => Math.round((Date.parse(a) - Date.parse(b)) / 86400000);   // two YYYY-MM-DD days
// Days left and the late flag depend on the page clock, so they are set when the page is drawn.
function clock(model, now, tz = model.tz || TZ) {
  const today = dayOf(now, tz);
  for (const m of model.milestones || []) {
    m.daysLeft = m.due ? daysBetween(dayOf(m.due, tz), today) : null;
    m.late = !!(m.due && m.daysLeft < 0 && m.done < m.total);
  }
  return model;
}
// A vertical stack of milestone boxes. Arrows are arcs on the right, so none runs through a box; a wider span gets a wider arc. Dotted = waits for a later milestone.
// Colours are theme tokens, so the picture follows the Night theme.
function mapSvg(mp) {
  const gap = 62, h = 40, w = 250, ys = Object.fromEntries(mp.nodes.map((t, i) => [t, 20 + i * gap])), pos = Object.fromEntries(mp.nodes.map((t, i) => [t, i]));
  const height = 40 + Math.max(mp.nodes.length - 1, 0) * gap + h, width = 24 + w + 50 + 36 * Math.max(mp.nodes.length - 1, 1) + 90, x = 24 + w;
  const paths = mp.edges.map(e => {
    const y1 = ys[e.from] + h / 2, y2 = ys[e.to] + h / 2, off = 50 + 36 * Math.abs(pos[e.from] - pos[e.to]);
    return `<g data-edge="${esc(e.from)} to ${esc(e.to)}"><path d="M${x} ${y1} C${x + off} ${y1} ${x + off} ${y2} ${x + 6} ${y2}" style="fill:none;stroke:var(--dark);stroke-width:2"${e.back ? ' stroke-dasharray="6 4"' : ''} marker-end="url(#ah)"/>`
      + `<text x="${x + off * 0.75 + 6}" y="${(y1 + y2) / 2 + 5}" font-size="14" style="fill:var(--text)">${e.count} need${e.count === 1 ? '' : 's'}</text></g>`;
  }).join('');
  const boxes = mp.nodes.map(t => `<g><rect x="24" y="${ys[t]}" width="${w}" height="${h}" rx="6" style="fill:var(--alt);stroke:var(--dark)"/><text x="36" y="${ys[t] + 25}" font-size="15" style="fill:var(--text)">${esc(t.slice(0, 30))}</text></g>`).join('');
  const n = mp.crossings, hid = mp.hidden ? ` ${mp.hidden} arrow${mp.hidden === 1 ? '' : 's'} that only repeat a longer path ${mp.hidden === 1 ? 'is' : 'are'} left out.` : '';
  return `<svg viewBox="0 0 ${width} ${height}" width="100%" role="img" aria-label="Which milestone waits for which"><defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">`
    + `<path d="M0 0 L8 4 L0 8 z" style="fill:var(--dark)"/></marker></defs>${boxes}${paths}</svg>`
    + `<p class="mono">Arrow: the later box waits for the earlier box. Dotted: it waits for a later milestone. ${n} crossing${n === 1 ? '' : 's'}.${hid}</p>`;
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
  // Milestone bars: done over total, earliest due first, no due date last. clock() adds the days left when the page is drawn.
  const mss = new Map();
  for (const s of stories.filter(x => x.milestone)) {
    const m = mss.get(s.milestone) || { title: s.milestone, due: due[s.milestone] === '9999' ? null : due[s.milestone], done: 0, total: 0 };
    m.total += 1; m.done += s.state === 'CLOSED' ? 1 : 0; mss.set(s.milestone, m);
  }
  const milestones = [...mss.values()].sort((a, b) => (a.due == null) - (b.due == null) || String(a.due).localeCompare(String(b.due)));
  return { tz, timeline, here, next, older, milestones, map: depMap(stories, milestones), chain: longestChain(stories), epics: epics.map(e => ({ number: e.number, title: plain(e.title.replace(/^(Epic|Feature):?\s*(E\d+:?)?\s*/i, '')), state: e.state })), stories };
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
  const tz = model.tz || project.timezone || TZ, hhmm = hm(now, tz), today = dayOf(now, tz), tzName = zoneName(tz, now);
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
  clock(model, now, tz);
  const bar = (m) => {
    const pct = m.total ? Math.round(100 * m.done / m.total) : 0, d = m.daysLeft, s = (k) => k === 1 ? '' : 's';
    const when = m.due == null ? 'no due date' : m.late ? `late by ${-d} day${s(-d)}` : d === 0 ? 'due today' : d > 0 ? `${d} day${s(d)} left` : 'finished after its date';
    return `<div class="bar${m.late ? ' late' : ''}" data-milestone="${esc(m.title)}"><b>${esc(m.title)}</b> <span class="mono">${m.done} of ${m.total} · ${m.due ? 'due ' + dayLabel(dayOf(m.due, tz)) + ' · ' : ''}${when}</span>`
      + `<div class="track"><div class="fill" style="width:${pct}%"></div></div></div>`;
  };
  const milestones = model.milestones || [], mp = model.map || { nodes: [] }, chain = model.chain || [];
  const bars = milestones.map(bar).join('') || '<p>No milestones yet.</p>';
  const chainLine = chain.length ? `<p>Longest chain of open work (${chain.length}): <span class="mono">${chain.map(c => '#' + c.number).join(' → ')}</span></p>` : '<p>No open work waits on other work.</p>';
  const needs = stories.filter(s => s.needsWords).length, done = closedStories.length;
  const notes = [needs ? `<span class="needs">${needs} ${needs === 1 ? 'story still needs' : 'stories still need'} plain words</span>` : '', project.truncated ? `<span class="needs">Showing the newest ${MAX_NODES} issues only.</span>` : ''].filter(Boolean).join(' · ');
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta http-equiv="refresh" content="300"><title>${esc(project.title)} roadmap</title>
<style>
:root { --primary:#3B82F6; --dark:#2563EB; --text:#1F2937; --bg:#FFFFFF; --muted:#6B7280; --alt:#F3F4F6; --line:#E5E7EB; --error:#B3261E; }
@media (prefers-color-scheme: dark) { :root { --primary:#60A5FA; --dark:#93C5FD; --text:#F3F4F6; --bg:#111827; --muted:#9CA3AF; --alt:#1F2937; --line:#374151; --error:#F2B8B5; } }
body { margin:0; background:var(--bg); color:var(--text); font:17px/1.5 Roboto, system-ui, sans-serif; }
main { max-width:960px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:32px; margin:0 0 4px; } h2 { font-size:22px; margin:40px 0 12px; border-bottom:2px solid var(--primary); padding-bottom:4px; } h3 { font-size:16px; margin:0 0 8px; }
.mono { font-family:ui-monospace, monospace; font-size:13px; color:var(--muted); }
.vision { background:var(--alt); border-left:4px solid var(--dark); border-radius:6px; padding:16px 20px; font-size:20px; }
details { background:var(--alt); border-radius:6px; padding:10px 16px; margin:8px 0; } summary { cursor:pointer; }
ul { padding-left:20px; } li { margin:4px 0; }
.board { display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; } @media (max-width:720px) { .board { grid-template-columns:1fr 1fr; } }
.col { background:var(--alt); border-radius:6px; padding:10px; min-height:80px; min-width:0; overflow-wrap:anywhere; }
.card { background:var(--bg); border:1px solid var(--line); border-radius:6px; padding:10px 12px; margin:8px 0; font-size:15px; } .card p { margin:6px 0; }
.tag { display:inline-block; background:var(--alt); color:var(--text); border:1px solid var(--primary); border-radius:999px; padding:1px 10px; font-size:12px; }
.bar { background:var(--alt); border-radius:6px; padding:8px 12px; margin:8px 0; } .track { background:var(--line); border-radius:999px; height:10px; margin-top:6px; } .fill { background:var(--primary); border-radius:999px; height:10px; } .bar.late .fill { background:var(--error); } .bar.late b { color:var(--error); }
footer { margin-top:40px; } .needs { color:var(--error); }
</style></head><body><main>
<h1>${esc(project.title)} roadmap</h1><p class="mono">updated ${hhmm} ${esc(tzName)} · ${done} of ${stories.length} stories done</p>
<section id="vision"><h2>Vision</h2><div class="vision">${esc(project.vision)}</div></section>
<section id="here"><h2>You are here</h2><p>It is ${hhmm} ${esc(tzName)}, ${dayLabel(today)}.</p><ul>${hereRows}</ul>${hereNext}</section>
<section id="milestones"><h2>Milestones</h2>${bars}</section>
<section id="map"><h2>What waits for what</h2>${mp.nodes.length ? mapSvg(mp) : '<p>No milestones yet.</p>'}${chainLine}</section>
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
module.exports = { build, render, fromGraphql, page, businessLine, plain, clock, crossings, mapSvg, MAX_NODES };
