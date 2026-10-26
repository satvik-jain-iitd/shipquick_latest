// S0.11 and S0.12: the roadmap renderer (story #44). A fixture of issues and pull requests goes in; one HTML page comes out.
// Run: node --test roadmap/   (no token, no network)
const test = require('node:test'), assert = require('node:assert/strict'), crypto = require('node:crypto');
const { build, render, fromGraphql, page } = require('./render.js'), { sha256hex } = require('./sha256.js');

const STORY = 'Part of epic #1.\n\n## Business\nA cook sees a cancelled ticket for a minute. The PR adds a stamp.\n\n## Product\n- rpc and migration words here.';
const ISSUES = [
  { number: 1, title: 'Epic: v1 Kitchen app', body: '## Business\nThe cook has one screen.', state: 'OPEN', labels: ['epic'], closedAt: null, parent: null },
  { number: 2, title: 'Epic: Cash', body: '## Business\nCash adds up.', state: 'OPEN', labels: ['epic'], closedAt: null, parent: null },
  { number: 10, title: 'Story: cancelled ticket', body: STORY, state: 'CLOSED', labels: ['user-story'], closedAt: '2026-10-21T10:00:00Z', parent: null },
  { number: 11, title: 'Story: cash day', body: 'Part of epic #2.\n\n## Business\nThe rider\'s cash adds up at the end of the night.', state: 'OPEN', labels: ['user-story'], closedAt: null, parent: null },
  { number: 12, title: 'Story: hand-over', body: '## Business\nThe kitchen confirms the rider\'s cash.', state: 'OPEN', labels: ['user-story'], closedAt: null, parent: { number: 2 } },
  { number: 13, title: 'Story: no words yet', body: 'Part of epic #2.\n\nJust a title.', state: 'OPEN', labels: ['user-story'], closedAt: null, parent: null },
  { number: 14, title: 'Story: marked doing', body: '**Business line:** The owner sees a stamp on the page.', state: 'OPEN', labels: ['story', 'doing'], closedAt: null, parent: { number: 2 } },
  { number: 15, title: 'Story: closed later', body: '## Business\nThe stamp is shown.', state: 'CLOSED', labels: ['user-story'], closedAt: '2026-10-25T10:00:00Z', parent: { number: 1 } },
  { number: 99, title: 'A bug, not a story', body: '', state: 'OPEN', labels: ['bug'], closedAt: null, parent: null },
];
const PRS = [
  { number: 50, title: 'feat(app): cash day (#11)', headRefName: 'feat/11-cash-day', isDraft: false, checks: [{ conclusion: 'SUCCESS' }, { conclusion: 'SUCCESS' }] },
  { number: 51, title: 'feat(app): hand-over', headRefName: 'ci/12-handover', isDraft: false, checks: [{ conclusion: 'FAILURE' }] },
];
const NOW = new Date('2026-10-25T03:35:00Z');   // 09:05 in India
const PROJECT = { title: 'Kitchen', vision: 'Hot meals at your door.' };
const JARGON = /\b(PR|CI|rpc|migration|e2e)\b/;
const model = build(ISSUES, PRS), html = render(model, PROJECT, NOW), part = (from, to) => html.split(`id="${from}"`)[1].split(`id="${to}"`)[0];

test('S0.11 every open story is on the board once, a bug is not a story', () => {
  const board = html.split('id="board"')[1];
  for (const n of [11, 12, 13, 14]) assert.equal(board.split(`data-story="${n}"`).length - 1, 1, String(n));
  assert.ok(!html.includes('data-story="99"'));
});

test('S0.11 columns follow the pull requests and the doing label', () => {
  const cols = Object.fromEntries(model.stories.map(s => [s.number, s.column]));
  assert.deepEqual(cols, { 10: 'Done', 11: 'Review', 12: 'Doing', 13: 'To do', 14: 'Doing', 15: 'Done' });   // green checks = Review, red = Doing, label doing = Doing, no PR = To do
});

test('S0.11 the epic comes from the parent link or the "Part of" line', () => {
  assert.deepEqual(Object.fromEntries(model.stories.map(s => [s.number, s.epic])), { 10: 1, 11: 2, 12: 2, 13: 2, 14: 2, 15: 1 });
});

test('S0.11 delivered lists closed stories newest first, with the first sentence only, folded shut', () => {
  const d = part('delivered', 'now');
  assert.ok(d.includes('A cook sees a cancelled ticket for a minute.'));
  assert.ok(!d.includes('The PR adds a stamp') && !d.includes('adds a stamp.'));
  assert.ok(d.indexOf('The stamp is shown.') < d.indexOf('A cook sees a cancelled ticket'), 'newest first');
  assert.ok(!/<details[^>]*\bopen\b/.test(d), 'folded shut');
  assert.ok(!d.includes('cash'), 'open stories are not delivered');
});

test('S0.11 now = stories with a pull request or the doing label; next = open stories with no pull request', () => {
  const now = part('now', 'next'), next = part('next', 'board');
  for (const t of ['The rider&#39;s cash adds up at the end of the night.', 'The kitchen confirms the rider&#39;s cash.', 'The owner sees a stamp on the page.']) assert.ok(now.includes(t), t);
  assert.ok(now.includes('review') && now.includes('doing'));
  assert.ok(next.includes('Story: no words yet') && !next.includes('cash adds up'));
});

test('S0.11 plain words outside the board, the board keeps the story words, vision and time are shown', () => {
  assert.deepEqual(html.split('id="board"')[0].match(JARGON), null);
  assert.ok(html.includes('1 story still needs plain words'));
  assert.ok(html.includes('Hot meals at your door.') && html.includes('updated 09:05 IST'));
  assert.ok(html.includes('http-equiv="refresh" content="300"'));
});

test('S0.11 text from GitHub is escaped, the page has no script', () => {
  const bad = build([{ ...ISSUES[3], title: '<img src=x onerror=alert(1)>', body: '## Business\n<script>alert(1)</script> is shown.' }], []);
  const out = render(bad, { title: '<b>x</b>', vision: '<i>v</i>' }, NOW);
  assert.ok(!out.includes('<script') && !out.includes('<img') && !out.includes('<b>x') && !out.includes('<i>v'));
});

test('S0.11 a project with more issues than one page of GitHub data says so on the page', () => {
  assert.ok(render(model, { ...PROJECT, truncated: true }, NOW).includes('newest 100'));
  assert.ok(!html.includes('newest 100'));
});

test('S0.11 GitHub GraphQL data becomes issues and pull requests; the check state sets the column', () => {
  const resp = { data: { repository: {
    issues: { pageInfo: { hasNextPage: true }, nodes: [{ number: 11, title: 'S', body: '## Business\nOne.', state: 'OPEN', closedAt: null, parent: null, labels: { nodes: [{ name: 'user-story' }] } }] },
    pullRequests: { nodes: [{ number: 5, title: 'x (#11)', headRefName: 'feat/11-x', isDraft: false, commits: { nodes: [{ commit: { statusCheckRollup: { state: 'SUCCESS' } } }] } }] } } } };
  const d = fromGraphql(resp);
  assert.equal(d.truncated, true);
  assert.deepEqual(d.issues[0].labels, ['user-story']);
  assert.equal(build(d.issues, d.prs).stories[0].column, 'Review');
  const none = fromGraphql({ data: { repository: { issues: { pageInfo: { hasNextPage: false }, nodes: [] }, pullRequests: { nodes: [{ number: 6, title: 'y', headRefName: 'z', isDraft: false, commits: { nodes: [] } }] } } } });
  assert.equal(none.truncated, false);
  assert.deepEqual(none.prs[0].checks, []);
  assert.throws(() => fromGraphql({ errors: [{ message: 'Bad credentials' }] }), /Bad credentials/);   // fail closed: nothing is saved
});

test('S0.11 page() = GraphQL data + project to html in one call', () => {
  const resp = { data: { repository: { issues: { pageInfo: { hasNextPage: false }, nodes: [] }, pullRequests: { nodes: [] } } } };
  assert.ok(page(resp, PROJECT, NOW).includes('Hot meals at your door.'));
});

test('S0.12 sha256hex matches node crypto, including non-ASCII text', () => {
  for (const s of ['', 'abc', 'k'.repeat(55), 'k'.repeat(56), 'k'.repeat(64), 'key-é-日本'])
    assert.equal(sha256hex(s), crypto.createHash('sha256').update(s).digest('hex'), s);
});
