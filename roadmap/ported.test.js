// Story #81 (epic #80, S1): the reference roadmap's test suite, ported to node:test. 28 of its 33 tests are here; the 5 deploy tests
// (a shell wrapper around a Pages upload with the child's own vault file) belong to the kit's own deploy story (S4), not to this port.
// A test the JS cannot pass yet is marked todo with the story that turns it green: #82 (data in the model) or #83 (the page and its derived model).
// Run: node --test roadmap/*.test.js          ROADMAP_STRICT=1 runs the todo tests as real failures (the red run of #81).
const test = require('node:test'), assert = require('node:assert/strict'), path = require('node:path'), { spawnSync } = require('node:child_process');
const rm = require('./render.js'), { build, render } = rm;

const later = (story, what) => process.env.ROADMAP_STRICT ? {} : { todo: `story ${story}: ${what}` };
const sec = (html, id) => (html.split(`id="${id}"`)[1] || '').split('</section>')[0];
const nums = (rows) => (rows || []).map(s => s.number);
const byNumber = (model) => Object.fromEntries(model.stories.map(s => [s.number, s]));
const PROJECT = { title: 'Kitchen', vision: 'Hot meals at your door.' };
const JARGON = /\b(PR|CI|rpc|migration|e2e)\b/;

// ---- The first page: board, columns, delivered, plain words, now. ----
const STORY = 'Part of epic E1 (#1).\n\n## Business\nA cook sees a cancelled ticket for a minute. The PR adds a stamp.\n\n## Product\n- rpc and migration words here.';
const ISSUES = [
  { number: 1, title: 'Epic E1: Kitchen app', body: '## Business\nThe cook has one screen.', state: 'CLOSED', labels: ['epic'], closedAt: '2026-10-20T10:00:00Z', parent: null },
  { number: 2, title: 'Epic E2: Cash', body: '## Business\nCash adds up.', state: 'OPEN', labels: ['epic'], closedAt: null, parent: null },
  { number: 10, title: 'Story: cancelled ticket', body: STORY, state: 'CLOSED', labels: ['story'], closedAt: '2026-10-21T10:00:00Z', parent: null },
  { number: 11, title: 'Story: cash day', body: 'Part of epic E2 (#2).\n\n## Business\nThe rider\'s cash adds up at the end of the night.', state: 'OPEN', labels: ['story'], closedAt: null, parent: null },
  { number: 12, title: 'Story: hand-over', body: '## Business\nThe kitchen confirms the rider\'s cash.', state: 'OPEN', labels: ['story'], closedAt: null, parent: { number: 2 } },
  { number: 13, title: 'Story: no words yet', body: 'Part of epic E2 (#2).\n\nJust a title.', state: 'OPEN', labels: ['story'], closedAt: null, parent: null },
  { number: 99, title: 'A bug, not a story', body: '', state: 'OPEN', labels: ['bug'], closedAt: null, parent: null },
];
const PRS = [
  { number: 50, title: 'feat(app): cash day (#11)', headRefName: 'feat/11-cash-day', isDraft: false, checks: [{ conclusion: 'SUCCESS' }, { conclusion: 'SUCCESS' }] },
  { number: 51, title: 'feat(app): hand-over', headRefName: 'feat/12-handover', isDraft: false, checks: [{ conclusion: 'FAILURE' }] },
];
const AT_0905 = new Date('2026-10-25T03:35:00Z');   // 09:05 India time
const model1 = build(ISSUES, PRS), html1 = render(model1, PROJECT, AT_0905);

test('S1 every open story is on the board once; a bug is not a story', () => {
  const board = html1.split('id="board"')[1];
  for (const n of [11, 12, 13]) assert.equal(board.split(`data-story="${n}"`).length - 1, 1, String(n));
  assert.ok(!html1.includes('data-story="99"'));
});

test('S1 columns follow the pull requests: green checks = Review, red = Doing, no pull request = To do', () => {
  assert.deepEqual(Object.fromEntries(model1.stories.map(s => [s.number, s.column])), { 10: 'Done', 11: 'Review', 12: 'Doing', 13: 'To do' });
});

test('S1 a closed epic is under Delivered with its story sentence, first sentence only, open epics stay out', () => {
  const delivered = sec(html1, 'delivered');
  assert.ok(delivered.includes('Kitchen app'));
  assert.ok(delivered.includes('A cook sees a cancelled ticket for a minute.'));
  assert.ok(!delivered.includes('The PR adds a stamp'));
  assert.ok(!delivered.split('</details>')[0].includes('Cash'));
});

test('S1 the epic comes from the parent link or the "Part of" line', () => {
  assert.deepEqual(Object.fromEntries(model1.stories.map(s => [s.number, s.epic])), { 10: 1, 11: 2, 12: 2, 13: 2 });
});

test('S1 no jargon outside the board, and a count of stories without plain words (the title stands in)', () => {
  assert.equal(html1.split('id="board"')[0].match(JARGON), null);
  assert.ok(html1.includes('1 story still needs plain words'));
  assert.ok(html1.includes('Story: no words yet'));
});

test('S1 Now lists the open pull requests with the plain sentence, and the page says when it was made', () => {
  const now = sec(html1, 'now');
  assert.ok(now.includes('The rider&#39;s cash adds up at the end of the night.'));
  assert.ok(now.includes('The kitchen confirms the rider&#39;s cash.'));
  assert.ok(now.includes('review') && now.includes('doing'));
  assert.ok(html1.includes('updated 09:05'));
  assert.ok(html1.includes('http-equiv="refresh" content="300"'));
});

// ---- The v2 page: timeline by close day, start and cycle time, You are here, Next order, Delivered date range. ----
const issue = (n, title, o = {}) => ({ number: n, title, body: o.body === undefined ? `Part of epic E9 (#9).\n\n## Business\n${title} works.` : o.body, state: o.state || 'OPEN',
  labels: o.labels || ['story'], closedAt: o.closedAt || null, doingAt: o.doingAt || null, milestone: o.milestone || null, parent: o.parent || null });
const M1 = { title: 'M1 MVP2', dueOn: '2026-10-27T18:29:00Z' }, M2 = { title: 'M2 Design', dueOn: '2026-10-28T18:29:00Z' };
const V2 = [
  issue(9, 'Epic E9: Plan v2', { labels: ['epic'], body: '## Business\nOne plan.' }),
  issue(20, 'Story A done early', { state: 'CLOSED', closedAt: '2026-10-24T20:00:00Z', doingAt: '2026-10-24T18:00:00Z', milestone: M1 }),   // 25 Oct 01:30 India, took 2 h
  issue(21, 'Story B done late', { state: 'CLOSED', closedAt: '2026-10-25T06:00:00Z', doingAt: '2026-10-25T05:15:00Z', milestone: M1 }),    // 25 Oct 11:30 India, took 45 min
  issue(22, 'Story C done no start', { state: 'CLOSED', closedAt: '2026-10-23T06:00:00Z', milestone: M1 }),                                  // never marked doing
  issue(23, 'Story D in progress', { labels: ['story', 'doing', 'P0'], doingAt: '2026-10-26T04:00:00Z', milestone: M1 }),
  issue(24, 'Story E ready p1', { labels: ['story', 'ready', 'P1'], milestone: M1 }),
  issue(25, 'Story F ready p0 later milestone', { labels: ['story', 'ready', 'P0'], milestone: M2, body: 'Part of epic E9 (#9).\n\n## Business\nF works.\n\nNeeds: #26' }),
  issue(26, 'Story G ready p0 first', { labels: ['story', 'ready', 'P0'], milestone: M1 }),
  issue(40, 'Story old open, no plan labels', { milestone: M1 }),
  issue(27, 'Story H blocked', { labels: ['story', 'blocked', 'P0'], milestone: M1, body: 'Part of epic E9 (#9).\n\n## Business\nH works.\n\n## Needs\nNeeds: #23\nNeeds: #26' }),
];
const NOW = new Date('2026-10-26T05:30:00Z');   // 26 Oct 11:00 India time
const V = { title: 'Plan', vision: 'Vision.' };
const model2 = build(V2, []), html2 = render(model2, V, NOW);

test('S1 the timeline groups closed stories by India close day, newest first', later('#83', 'model.timeline and the timeline section'), () => {
  assert.deepEqual((model2.timeline || []).map(d => [d.day, nums(d.stories)]), [['2026-10-25', [21, 20]], ['2026-10-23', [22]]]);   // 20 closed at 01:30 India on the 25th, not the 24th UTC
  const tl = sec(html2, 'timeline');
  assert.ok(tl.indexOf('25 Oct') >= 0 && tl.indexOf('25 Oct') < tl.indexOf('23 Oct'));
});

test('S1 the start is the first doing label and the cycle time is close minus start', later('#82 and #83', 'story.cycleMin, then the timeline shows it'), () => {
  const by = byNumber(model2);
  assert.deepEqual([by[20].cycleMin, by[21].cycleMin, by[22].cycleMin], [120, 45, null]);
  const tl = sec(html2, 'timeline');
  assert.ok(tl.includes('2 h') && tl.includes('45 min') && tl.includes('no start time'));   // honest: the story was never marked doing
});

test('S1 You are here shows the time, the story in progress and the next ready story', later('#83', 'model.here and the here section'), () => {
  const here = model2.here || {};
  assert.deepEqual(nums(here.doing), [23]);
  assert.equal(here.next && here.next.number, 26);   // P0 in the earliest milestone, then the lowest number
  const h = sec(html2, 'here');
  for (const t of ['11:00', 'Story D in progress', 'since 09:30', 'Story G ready p0 first']) assert.ok(h.includes(t), t);   // 04:00 UTC is 09:30 India
});

test('S1 Next is sorted by milestone, then priority, then number, and marks blocked stories', later('#83', 'model.next and the next section'), () => {
  assert.deepEqual(nums(model2.next), [26, 27, 24, 25]);   // M1 first: P0 (26, 27) then P1 (24); M2 last. Doing and done stories are not in Next.
  assert.ok(sec(html2, 'next').includes('blocked by #23, #26'));
});

test('S1 stories without a ready or blocked label are older work and stay out of Next', later('#83', 'model.older and the older section'), () => {
  assert.ok(!nums(model2.next).includes(40));
  assert.deepEqual(nums(model2.older), [40]);
  assert.ok(sec(html2, 'older').includes('Story old open, no plan labels'));
});

test('S1 Needs lines become numbers', () => {
  const by = byNumber(model2);
  assert.deepEqual(by[27].needs, [23, 26]);
  assert.deepEqual(by[26].needs, []);
});

test('S1 delivered epics show their date range and stay folded', later('#83', 'the delivered date range'), () => {
  const issues = V2.concat([issue(30, 'Epic E8: Old', { state: 'CLOSED', labels: ['epic'], closedAt: '2026-10-25T07:00:00Z', body: '## Business\nOld work.' }),
    issue(31, 'Story old one', { state: 'CLOSED', closedAt: '2026-10-21T08:00:00Z', parent: { number: 30 } }),
    issue(32, 'Story old two', { state: 'CLOSED', closedAt: '2026-10-25T07:00:00Z', parent: { number: 30 } })]);
  const d = sec(render(build(issues, []), V, NOW), 'delivered');
  assert.ok(d.includes('21 Oct to 25 Oct'));
  assert.ok(!d.includes('<details open'));
});

// ---- Milestone bars, the dependency map, the longest chain. ----
test('S1 milestone bars count done over total, with the due date and the days left', later('#83', 'model.milestones, clock and the milestones section'), () => {
  const ms = Object.fromEntries((model2.milestones || []).map(m => [m.title, m]));
  assert.deepEqual((model2.milestones || []).map(m => m.title), ['M1 MVP2', 'M2 Design']);   // by due date
  assert.deepEqual([ms['M1 MVP2'].done, ms['M1 MVP2'].total, ms['M1 MVP2'].daysLeft, ms['M1 MVP2'].late], [3, 8, 1, false]);
  assert.deepEqual([ms['M2 Design'].done, ms['M2 Design'].total, ms['M2 Design'].daysLeft], [0, 1, 2]);
  const bar = sec(html2, 'milestones');
  assert.ok(bar.includes('3 of 8') && bar.includes('due 27 Oct') && bar.includes('1 day left'));
});

test('S1 a milestone past its due date with work left is late and red', later('#83', 'the late flag on the bar'), () => {
  const bar = sec(render(build(V2, []), V, new Date('2026-10-30T03:30:00Z')), 'milestones');   // 30 Oct 09:00 India
  assert.ok(bar.includes('class="bar late"') && bar.includes('late by 2 days'));
});

test('S1 the map has one edge per pair of milestones with the number of needs', later('#83', 'model.map.edges'), () => {
  assert.deepEqual((model2.map || {}).edges, [{ from: 'M1 MVP2', to: 'M2 Design', count: 1, back: false }]);   // 25 (M2) needs 26 (M1); needs inside one milestone are not edges
});

test('S1 a need on a later milestone is a backward edge', later('#83', 'model.map.edges with back: true'), () => {
  const m = build(V2.concat([issue(41, 'Story early needs late', { labels: ['story', 'blocked', 'P0'], milestone: M1, body: 'Needs: #25' })]), []);
  assert.deepEqual(((m.map || {}).edges || []).filter(e => e.back), [{ from: 'M2 Design', to: 'M1 MVP2', count: 1, back: true }]);
});

test('S1 crossings are measured, not guessed', later('#83', 'crossings() exported from render.js'), () => {
  assert.equal(rm.crossings([[0, 2], [1, 3]]), 1);   // interleaved arcs cross
  assert.equal(rm.crossings([[0, 3], [1, 2]]), 0);   // nested arcs do not
  assert.equal(rm.crossings([[0, 1], [1, 2], [2, 3]]), 0);   // arcs that only touch at a box do not
  assert.equal(model2.map.crossings, 0);
});

test('S1 the svg labels every arrow and names the crossings', later('#83', 'the map section'), () => {
  const svg = sec(html2, 'map');
  assert.equal(svg.split('<svg').length - 1, 1);
  assert.equal(svg.split('data-edge=').length - 1, 1);
  for (const t of ['1 need', '0 crossings', 'M1 MVP2']) assert.ok(svg.includes(t), t);
});

test('S1 an arrow that only repeats a longer path is hidden and counted', later('#83', 'model.map.hidden'), () => {
  const m3 = { title: 'M3 Late', dueOn: '2026-10-29T18:29:00Z' };
  const issues = V2.concat([issue(50, 'Story L1', { labels: ['story', 'blocked'], milestone: m3, body: 'Needs: #26\nNeeds: #25' })]);   // M3 waits for M1 and M2; M2 already waits for M1
  const mp = build(issues, []).map || {};
  assert.deepEqual((mp.edges || []).map(e => [e.from, e.to]), [['M1 MVP2', 'M2 Design'], ['M2 Design', 'M3 Late']]);
  assert.equal(mp.hidden, 1);
  assert.ok(sec(render(build(issues, []), V, NOW), 'map').includes('1 arrow'));
});

test('S1 the longest chain of open work is listed, ties go to the lowest numbers', later('#83', 'model.chain'), () => {
  assert.deepEqual(nums(model2.chain), [23, 27]);
  assert.ok(html2.includes('Longest chain'));
});

// ---- The page clock. ----
test('S1 the page clock is India time even when the machine runs in UTC or another zone', () => {
  const script = `const r = require(${JSON.stringify(path.join(__dirname, 'render.js'))}); process.stdout.write(r.render(r.build([], []), { title: 'x', vision: 'v' }, new Date('2026-10-25T03:35:00Z')));`;
  for (const TZ of ['UTC', 'America/New_York']) {
    const r = spawnSync('node', ['-e', script], { encoding: 'utf8', env: { ...process.env, TZ } });
    assert.equal(r.status, 0, r.stderr);
    assert.ok(r.stdout.includes('updated 09:05'), TZ);
  }
});

// ---- Night theme and phone layout. ----
test('S1 the page has a night theme that follows the phone, and a phone-width layout', later('#83', 'the color-scheme meta and the dark media block'), () => {
  assert.ok(html2.includes('<meta name="viewport" content="width=device-width, initial-scale=1">'));
  assert.ok(html2.includes('<meta name="color-scheme" content="light dark">'));
  const night = (html2.split('@media (prefers-color-scheme: dark)')[1] || '').split('</style>')[0];
  const used = [...(html2.match(/body \{([^}]*)\}/) || ['', ''])[1].matchAll(/var\((--[\w-]+)\)/g)].map(m => m[1]);   // the tokens the body paints with
  assert.ok(used.length >= 2, 'body uses tokens for its background and text');
  for (const token of used) assert.ok(night.includes(token), token + ' must change at night');
  assert.ok(html2.includes('@media (max-width:720px)'));
});

test('S1 board columns may shrink and wrap long words, so a phone does not scroll sideways', later('#83', 'the .col rule'), () => {
  const col = (html2.match(/\.col \{([^}]*)\}/) || ['', ''])[1];
  assert.ok(col.includes('min-width:0') && col.includes('overflow-wrap:anywhere'), col);
});

test('S1 the map svg uses theme colours, so it follows night', later('#83', 'mapSvg() exported from render.js'), () => {
  const svg = rm.mapSvg(build(V2, []).map);
  assert.equal(svg.match(/#[0-9A-Fa-f]{6}\b/), null, 'no fixed colour: it would stay light at night');
  assert.ok(svg.includes('var(--'));
});

// ---- A "Started:" line stands in for a missing doing label on an old closed story. ----
const cycle = (o = {}) => {
  const extra = o.bodyExtra || '';
  const i = issue(40, 'Story S', { state: 'CLOSED', closedAt: '2026-10-25T06:00:00Z', milestone: M1, doingAt: o.doingAt, body: `Part of epic E9 (#9).\n\n## Business\nS works.\n${extra}` });
  return byNumber(build([issue(9, 'Epic E9: Plan v2', { labels: ['epic'], body: '## Business\nOne plan.' }), i], []))[40].cycleMin;
};

test('S1 a Started line gives the start when there is no doing label', () => {
  assert.equal(cycle({ bodyExtra: 'Started: 2026-10-25T04:00:00Z (estimated)' }), 120);
});

test('S1 the doing label wins over a Started line', () => {
  assert.equal(cycle({ doingAt: '2026-10-25T05:15:00Z', bodyExtra: 'Started: 2026-10-25T04:00:00Z (estimated)' }), 45);
});

test('S1 no label and no line means no cycle time, and a bad line is ignored', () => {
  assert.equal(cycle(), null);
  assert.equal(cycle({ bodyExtra: 'Started: yesterday' }), null);
  assert.equal(cycle({ bodyExtra: 'Not started: 2026-10-25T04:00:00Z' }), null);   // only a line that begins with Started:
});
