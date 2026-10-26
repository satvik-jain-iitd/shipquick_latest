// S0.12: ROADMAP.md from GitHub data (story #49). No token, no network: a fixture replaces the GitHub answer.
// Run: node --test roadmap/*.test.js
const test = require('node:test'), assert = require('node:assert/strict'), fs = require('node:fs'), os = require('node:os'), path = require('node:path'), { spawnSync } = require('node:child_process');
const { markdown, run } = require('./roadmap.js'), { build } = require('./render.js');

const issue = (number, title, body, state, labels, parent, closedAt) => ({ number, title, body, state, closedAt: closedAt || null, parent: parent ? { number: parent } : null, labels: { nodes: labels.map(name => ({ name })) } });
const RESP = { data: { repository: {
  issues: { pageInfo: { hasNextPage: false }, nodes: [
    issue(1, 'Epic: v1 Kitchen app', '## Business\nThe cook has one screen.', 'OPEN', ['epic']),
    issue(10, 'Story: cancelled ticket', '## Business\nA cook sees a cancelled ticket. The PR adds a stamp.', 'CLOSED', ['user-story'], 1, '2026-10-21T10:00:00Z'),
    issue(11, 'Story: cash day', '## Business\nThe rider\'s cash adds up.', 'OPEN', ['user-story'], 1),
    issue(12, 'Story: hand-over | with a pipe', '## Business\nThe kitchen <b>confirms</b> the cash.', 'OPEN', ['user-story'], 1),
    issue(13, 'Story: no words', 'Just a title.', 'OPEN', ['user-story'], 1),
    issue(99, 'A bug', '', 'OPEN', ['bug']),
  ] },
  pullRequests: { pageInfo: { hasNextPage: false }, nodes: [{ number: 50, title: 'feat: cash (#11)', headRefName: 'feat/11-cash', isDraft: false, commits: { nodes: [{ commit: { statusCheckRollup: { state: 'SUCCESS' } } }] } }] } } } };
const PROJECT = { title: 'Kitchen', vision: 'Hot meals at your door.', repo: 'o/kitchen' };
const md = markdown(RESP, PROJECT), part = (a, b) => md.split(`## ${a}`)[1].split(`## ${b}`)[0];

test('S0.12 the page has Vision, Delivered, Now, Next and Board in this order', () => {
  const at = ['Vision', 'Delivered', 'Now', 'Next', 'Board'].map(h => md.indexOf('## ' + h));
  assert.ok(at.every(i => i > 0) && [...at].sort((a, b) => a - b).join() === at.join(), String(at));
  assert.ok(md.startsWith('# Kitchen roadmap') && part('Vision', 'Delivered').includes('Hot meals at your door.'));
});

test('S0.12 delivered is folded shut and keeps the first sentence only; now and next follow the pull requests', () => {
  const d = part('Delivered', 'Now');
  assert.ok(d.includes('<details>') && !d.includes('<details open') && d.includes('A cook sees a cancelled ticket.'));
  assert.ok(!d.includes('adds a stamp'));
  assert.ok(part('Now', 'Next').includes('The rider&#39;s cash adds up.') || part('Now', 'Next').includes("The rider's cash adds up."));
  assert.ok(part('Now', 'Next').includes('review'));
  assert.ok(part('Next', 'Board').includes('confirms') && !part('Next', 'Board').includes('cash adds up'));
});

test('S0.12 plain words outside the board; the board keeps the story words and links each issue', () => {
  const top = md.split('## Board')[0];
  assert.equal(/\b(PR|CI|rpc|migration)\b/.test(top), false);
  assert.ok(md.split('## Board')[1].includes('[#10](https://github.com/o/kitchen/issues/10)'));
  assert.ok(md.includes('1 story still needs plain words'));
});

test('S0.12 text from GitHub cannot break the table or add markup', () => {
  assert.ok(!md.includes('<b>confirms') && md.includes('&lt;b&gt;'));   // the tag from GitHub is neutralised (our own <details> and <b> stay)
  const bad = markdown({ data: { repository: { issues: { pageInfo: {}, nodes: [issue(5, '[x](javascript:alert(1)) <script>', '## Business\n<img src=x onerror=1> and `code` end.', 'OPEN', ['user-story'])] }, pullRequests: { nodes: [] } } } }, PROJECT);
  assert.ok(!bad.includes('<script') && !bad.includes('<img') && !bad.includes('](javascript:'));
  const pipe = markdown({ data: { repository: { issues: { pageInfo: {}, nodes: [issue(6, 'a | b', 'no words', 'OPEN', ['user-story'])] }, pullRequests: { nodes: [] } } } }, PROJECT);
  assert.ok(pipe.includes('a \\| b') && !pipe.includes('a | b'));   // one cell, not two
});

test('S0.12 the page does not change from run to run, so no empty commits (no clock inside)', () => {
  assert.equal(markdown(RESP, PROJECT), md);
  assert.ok(!/\d\d:\d\d/.test(md));
});

test('S0.12 a project with more than one page of issues says so', () => {
  const more = JSON.parse(JSON.stringify(RESP)); more.data.repository.issues.pageInfo.hasNextPage = true;
  assert.ok(markdown(more, PROJECT).includes('newest 100'));
  assert.ok(!md.includes('newest 100'));
});

test('S0.12 an error answer from GitHub stops the run and writes nothing', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rm-')), out = path.join(dir, 'ROADMAP.md');
  fs.writeFileSync(path.join(dir, 'resp.json'), JSON.stringify({ errors: [{ message: 'Bad credentials' }] }));
  fs.writeFileSync(path.join(dir, 'roadmap.json'), JSON.stringify(PROJECT));
  const r = spawnSync('node', [path.join(__dirname, 'roadmap.js'), path.join(dir, 'resp.json'), path.join(dir, 'roadmap.json'), out], { encoding: 'utf8' });
  assert.equal(r.status, 1); assert.match(r.stderr, /Bad credentials/); assert.equal(fs.existsSync(out), false);
});

test('S0.12 the command reads roadmap.json (title, vision), takes the repo from GITHUB_REPOSITORY, and writes ROADMAP.md', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rm-')), out = path.join(dir, 'ROADMAP.md');
  fs.writeFileSync(path.join(dir, 'resp.json'), JSON.stringify(RESP));
  fs.writeFileSync(path.join(dir, 'roadmap.json'), JSON.stringify({ title: 'Kitchen', vision: 'Hot meals.' }));
  const r = spawnSync('node', [path.join(__dirname, 'roadmap.js'), path.join(dir, 'resp.json'), path.join(dir, 'roadmap.json'), out], { encoding: 'utf8', env: { ...process.env, GITHUB_REPOSITORY: 'o/kitchen' } });
  assert.equal(r.status, 0, r.stderr);
  const text = fs.readFileSync(out, 'utf8'); assert.ok(text.includes('Hot meals.') && text.includes('github.com/o/kitchen/issues/10'));
  fs.writeFileSync(path.join(dir, 'roadmap.json'), JSON.stringify({ title: 'Kitchen' }));   // a child that forgot the vision gets a clear error, not an empty page
  assert.equal(spawnSync('node', [path.join(__dirname, 'roadmap.js'), path.join(dir, 'resp.json'), path.join(dir, 'roadmap.json'), out], { encoding: 'utf8' }).status, 1);
});

test('S0.12 the GraphQL query is a file the workflow can hand to gh, with owner and name as variables', () => {
  const q = fs.readFileSync(path.join(__dirname, 'query.graphql'), 'utf8');
  assert.ok(q.includes('$owner: String!') && q.includes('$name: String!') && q.includes('statusCheckRollup') && q.includes('parent { number }'));
});
