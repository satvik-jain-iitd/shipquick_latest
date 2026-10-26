// S0.12 and S0.13: the two n8n workflows built by roadmap/build.js (story #44). Local only: no n8n, no network, no token.
// Run: node --test roadmap/
const test = require('node:test'), assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path');
const { checkLayout } = require('./lib/layout_checks.js'), { sha256hex } = require('./sha256.js');
const { buildMain, buildSub, projects } = require('./build.js');

const main = buildMain(), sub = buildSub();
const node = (b, name) => b.wf.nodes.find(n => n.name === name);
const targets = (b, from, out = 0) => ((b.wf.connections[from] || {}).main || [])[out]?.map(c => c.node) || [];
const run = (b, name, vars) => new Function('$input', '$', node(b, name).parameters.jsCode)(...vars);   // the node's code is self-contained: only $input and $ come from n8n
const KEY = 'test-key-not-real-0123456789';
const withKey = (j) => ({ first: () => ({ json: j }), all: () => [{ json: j }] });
const cfg = (q) => ({ query: q, projects_json: JSON.stringify([{ slug: 'p', sha256: sha256hex(KEY) }]) });

test('S0.12 projects.json holds a key hash and never a key; every row has what the page needs', () => {
  assert.ok(projects.length >= 1);
  for (const p of projects) {
    for (const f of ['slug', 'title', 'repo', 'vision', 'sha256']) assert.ok(p[f], p.slug + ' ' + f);
    assert.match(p.sha256, /^[0-9a-f]{64}$/);
    assert.match(p.repo, /^[\w.-]+\/[\w.-]+$/);
    assert.equal(p.key, undefined);
  }
});

test('S0.12 MAIN: every 15 minutes plus a GET webhook, then Config, then the kill switch before any build', () => {
  const t = node(main, 'Every 15 minutes').parameters.rule.interval[0], w = node(main, 'GET roadmap').parameters;
  assert.deepEqual([t.field, t.minutesInterval], ['minutes', 15]);
  assert.deepEqual([w.httpMethod, w.path, w.responseMode], ['GET', 'roadmap', 'responseNode']);
  assert.deepEqual(targets(main, 'Every 15 minutes'), ['Config']);
  assert.deepEqual(targets(main, 'GET roadmap'), ['Config']);
  assert.deepEqual(targets(main, 'Config'), ['Web request?']);
  assert.deepEqual(targets(main, 'Web request?', 1), ['Kill switch?']);        // the schedule path
  assert.deepEqual(targets(main, 'Kill switch?', 0), []);                       // kill = stop, nothing is built
  assert.deepEqual(targets(main, 'Kill switch?', 1), ['One item per project']);
  assert.deepEqual(targets(main, 'One item per project'), ['Call SQ Roadmap 11 Build Page']);
});

test('S0.12 MAIN: Config ships dry_run true and kill false, and carries the projects', () => {
  const v = Object.fromEntries(node(main, 'Config').parameters.assignments.assignments.map(a => [a.name, a.value]));
  assert.equal(v.dry_run, true); assert.equal(v.kill, false);
  assert.deepEqual(JSON.parse(v.projects_json), projects);
  assert.equal(node(main, 'Config').parameters.includeOtherFields, true);       // the webhook query must survive
});

test('S0.12 a right key serves the page, a wrong key, a missing key or an unknown project gets 404', () => {
  const check = (q) => run(main, 'Check key', [withKey(cfg(q)), null])[0].json;
  assert.deepEqual(check({ s: 'p', k: KEY }), { ok: true, slug: 'p' });
  assert.equal(check({ s: 'p', k: KEY + 'x' }).ok, false);
  assert.equal(check({ s: 'p' }).ok, false);
  assert.equal(check({ s: 'nope', k: KEY }).ok, false);
  assert.equal(check({ s: 'p', k: 'x'.repeat(5000) }).ok, false);
  assert.deepEqual(targets(main, 'Key ok?', 0), ['Get page']);
  assert.deepEqual(targets(main, 'Key ok?', 1), ['Respond 404']);
  assert.equal(node(main, 'Respond 404').parameters.options.responseCode, 404);
  assert.deepEqual(targets(main, 'Get page'), ['Respond page']);
  assert.equal(node(main, 'Get page').alwaysOutputData, true);                  // a project not built yet still gets an answer
});

test('S0.12 the page is sent as HTML and is never cached', () => {
  const h = Object.fromEntries(node(main, 'Respond page').parameters.options.responseHeaders.entries.map(e => [e.name, e.value]));
  assert.match(h['Content-Type'], /^text\/html/); assert.equal(h['Cache-Control'], 'no-store');
});

test('S0.12 MAIN calls the SUB by id from ids.json, and waits for it', () => {
  const c = node(main, 'Call SQ Roadmap 11 Build Page').parameters;
  assert.equal(c.source, 'database'); assert.equal(c.options.waitForSubWorkflow, true); assert.equal(c.mode, 'each');   // one SUB run per project; assert.ok(c.workflowId.value);
});

test('S0.13 SUB: typed inputs, one GitHub call per project with a read-only credential, render, then the write gate', () => {
  const f = node(sub, 'Start').parameters.workflowInputs.values.map(v => v.name);
  assert.deepEqual(f, ['slug', 'title', 'repo', 'vision', 'dry_run']);
  const h = node(sub, 'Get GitHub data').parameters;
  assert.equal(h.method, 'POST'); assert.equal(h.url, 'https://api.github.com/graphql');
  assert.equal(h.genericAuthType, 'httpHeaderAuth');                            // the token is an n8n credential
  assert.deepEqual(targets(sub, 'Start'), ['Get GitHub data']);
  assert.deepEqual(targets(sub, 'Get GitHub data'), ['Render page']);
  assert.deepEqual(targets(sub, 'Render page'), ['Dry run?']);
  assert.deepEqual(targets(sub, 'Dry run?', 0), []);                            // dry run = nothing is saved
  assert.deepEqual(targets(sub, 'Dry run?', 1), ['Save page']);
  assert.equal(node(sub, 'Save page').parameters.operation, 'upsert');
});

test('S0.13 the Render page node turns the GitHub answer of one project into one row', () => {
  const resp = { data: { repository: { issues: { pageInfo: { hasNextPage: false }, nodes: [] }, pullRequests: { nodes: [] } } } };
  const starts = [{ json: { slug: 'a', title: 'A', vision: 'Va', dry_run: true } }, { json: { slug: 'b', title: 'B', vision: 'Vb', dry_run: false } }];
  const one = (start) => run(sub, 'Render page', [{ all: () => [{ json: resp }] }, (n) => { assert.equal(n, 'Start'); return { first: () => start }; }]);
  const out = [one(starts[0])[0], one(starts[1])[0]];
  assert.deepEqual(out.map(o => [o.json.slug, o.json.dry_run]), [['a', true], ['b', false]]);
  assert.ok(out[0].json.html.includes('Va') && out[1].json.html.includes('Vb'));
  assert.match(out[0].json.updated_at, /^\d{4}-\d\d-\d\dT/);
});

test('S0.13 no workflow holds a token or a key', () => {
  const text = JSON.stringify([main.wf, sub.wf]);
  assert.ok(!/ghp_|github_pat_|gho_|Bearer /.test(text));
  assert.ok(!text.includes(KEY));
  assert.ok(node(sub, 'Get GitHub data').credentials.httpHeaderAuth.name);
});

test('S0.13 the canvas: one sticky box per step, left to right, nothing through a box, both workflows', () => {
  for (const b of [main, sub]) assert.deepEqual(checkLayout(b.wf, b.sections), [], b.wf.name);
});

test('S0.13 every node sits in exactly one box and every note has What and Needs in plain words', () => {
  for (const b of [main, sub]) for (const s of b.sections) assert.ok(s.what && s.needs && s.nodes.length, s.name);
});

test('S0.13 the committed workflow files equal a fresh build (the repo is the source of truth)', () => {
  for (const [file, b] of [['SQ_Roadmap_01.json', main], ['SQ_Roadmap_11.json', sub]])
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(__dirname, 'workflows', file), 'utf8')), JSON.parse(JSON.stringify(b.wf)), file);
});

test('S0.12 the MAIN keeps no successful run, so the key and the page never sit in the n8n history; errors stay saved', () => {
  assert.equal(main.wf.settings.saveDataSuccessExecution, 'none');
  assert.equal(main.wf.settings.saveManualExecutions, false);
  assert.equal(main.wf.settings.saveDataErrorExecution, undefined);   // the default (all) stays, so a failure can be read
});

test('S0.12 the SETTINGS note says the kill switch stops builds only and the link keeps answering', () => {
  assert.match(main.sections.find(s => s.name === 'SETTINGS').needs, /Kill stops the builds only.*link keeps answering/);
});

test('S0.13 build.js refuses to write while ids.json has TBD ids, unless --draft', () => {
  const { spawnSync } = require('node:child_process'), file = path.join(__dirname, 'workflows', 'SQ_Roadmap_01.json'), before = fs.readFileSync(file, 'utf8');
  const bad = spawnSync('node', [path.join(__dirname, 'build.js')], { encoding: 'utf8' });
  assert.equal(bad.status, 1); assert.match(bad.stderr, /placeholder ids/);
  assert.equal(fs.readFileSync(file, 'utf8'), before);
  assert.equal(spawnSync('node', [path.join(__dirname, 'build.js'), '--draft'], { encoding: 'utf8' }).status, 0);
});
