// Story #81 (epic #80, S1): the golden fixture. One synthetic GitHub answer (roadmap/fixtures/golden-issues.json) went once through the
// reference Python roadmap (roadmap/fixtures/expected.py captured roadmap/fixtures/golden-expected.json). The JS model must equal it field by field.
// Run: node --test roadmap/*.test.js          ROADMAP_STRICT=1 runs the todo tests as real failures (the red run; stories #82 and #83 turn them green).
const test = require('node:test'), assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path');
const { build, fromGraphql, clock } = require('./render.js');

const read = (f) => JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', f), 'utf8'));
const resp = read('golden-issues.json'), want = read('golden-expected.json'), d = fromGraphql(resp), model = build(d.issues, d.prs);
const later = (story, what) => process.env.ROADMAP_STRICT ? {} : { todo: `story ${story}: ${what}` };
const pick = (o, keys) => Object.fromEntries(keys.map(k => [k, o[k] === undefined ? null : o[k]]));   // a field the JS does not have yet reads as null, so the diff names it
const nums = (rows) => (rows || []).map(s => s.number);

test('golden: the fixture is synthetic, 20 to 40 issues, with parents, milestones, Needs lines and doing times', () => {
  const issues = resp.data.repository.issues.nodes;
  assert.ok(issues.length >= 20 && issues.length <= 40, String(issues.length));
  assert.ok(issues.some(i => i.parent) && issues.some(i => /^Part of epic/m.test(i.body)), 'parents both ways');
  assert.ok(issues.some(i => i.milestone) && issues.some(i => /^Needs: #\d+/m.test(i.body)), 'milestones and Needs');
  assert.ok(issues.some(i => i.timelineItems.nodes.some(t => t.label.name === 'doing')), 'doing label times');
  assert.equal(want.now, '2026-11-11T05:30:00Z');
});

test('golden: the epics are the same (number, plain title, state)', () => {
  assert.deepEqual(model.epics, want.epics);
});

test('golden: every story has the same epic, column, words and pull request', () => {
  const keys = ['number', 'epic', 'column', 'raw', 'text', 'needsWords'];
  assert.deepEqual(model.stories.map(s => ({ ...pick(s, keys), pr: s.pr ? s.pr.number : null })), want.stories.map(s => pick(s, keys.concat('pr'))));
});

test('golden: every story has the same milestone, priority, Needs, blockers, start time and cycle minutes', () => {
  const keys = ['number', 'milestone', 'prio', 'needs', 'blockedBy', 'started', 'cycleMin'];
  assert.deepEqual(model.stories.map(s => pick(s, keys)), want.stories.map(s => pick(s, keys)));
});

test('golden: the timeline groups closed stories by India close day, newest first', later('#83', 'model.timeline'), () => {
  assert.deepEqual((model.timeline || []).map(d => ({ day: d.day, stories: nums(d.stories) })), want.timeline);
});

test('golden: you are here, the Next order and the older work are the same', later('#83', 'model.here, model.next, model.older'), () => {
  assert.deepEqual({ doing: nums((model.here || {}).doing), next: model.here && model.here.next ? model.here.next.number : null }, want.here);
  assert.deepEqual(nums(model.next), want.next);
  assert.deepEqual(nums(model.older), want.older);
});

test('golden: the milestones have the same due date, counts, days left and late flag', later('#83', 'model.milestones and clock(model, now)'), () => {
  clock(model, new Date(want.now));
  const keys = ['title', 'due', 'done', 'total', 'daysLeft', 'late'];
  assert.deepEqual((model.milestones || []).map(m => pick(m, keys)), want.milestones);
});

test('golden: the dependency map has the same nodes, edges, hidden arrows and crossings', later('#83', 'model.map with measured crossings'), () => {
  assert.deepEqual(model.map, want.map);
});

test('golden: the longest chain of open work is the same', later('#83', 'model.chain'), () => {
  assert.deepEqual(nums(model.chain), want.chain);
});

test('the roadmap tests run from scripts/check_local.sh and CI with the same command', () => {
  const local = fs.readFileSync(path.join(__dirname, '..', 'scripts', 'check_local.sh'), 'utf8');
  const ci = fs.readFileSync(path.join(__dirname, '..', '.github', 'workflows', 'ci.yml'), 'utf8');
  assert.ok(local.includes('node --test roadmap/*.test.js') && ci.includes('node --test roadmap/*.test.js'));
});
