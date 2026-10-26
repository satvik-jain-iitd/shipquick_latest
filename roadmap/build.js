#!/usr/bin/env node
// Builds the two n8n workflows of the live roadmap (story #44, docs/LIVE_ROADMAP.md). The repo is the source of truth: never edit a node in the n8n editor.
//   node roadmap/build.js            writes roadmap/workflows/SQ_Roadmap_01.json and SQ_Roadmap_11.json
//   node roadmap/build.js --hash K   prints the SHA-256 of a page key K (for projects.json; the key itself goes to ~/Desktop/Secrets only)
//   node roadmap/build.js --draft    same as the first, allowed while ids.json still has TBD ids; such files must not be deployed
// n8n rulebook B11 (MAIN owns triggers, Config, kill switch; SUB does one job), B12 (sticky-note boxes, left to right), 95.9 (ids in one file).
const fs = require('node:fs'), path = require('node:path');
const { layout } = require('./lib/layout.js'), { sha256hex } = require('./sha256.js');
const projects = require('./projects.json'), IDS = require('./ids.json');
const PLACEHOLDERS = Object.entries(IDS).filter(([, v]) => typeof v === 'string' && v.startsWith('TBD'));

const GRAPHQL = `query($owner: String!, $name: String!) { repository(owner: $owner, name: $name) {
  issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) { pageInfo { hasNextPage } nodes { number title body state closedAt labels(first: 10) { nodes { name } } parent { number } } }
  pullRequests(states: OPEN, first: 100) { pageInfo { hasNextPage } nodes { number title headRefName isDraft commits(last: 1) { nodes { commit { statusCheckRollup { state } } } } } } } }`;
const RENDER = fs.readFileSync(path.join(__dirname, 'render.js'), 'utf8'), SHA = fs.readFileSync(path.join(__dirname, 'sha256.js'), 'utf8');
// A Code node is one string, so the source files are pasted in whole (their `module.exports` line removed) and a short runner follows.
const bundle = (src, runner) => src.split('\n').filter(l => !l.startsWith('module.exports')).join('\n') + '\n' + runner;

const mk = (name, type, typeVersion, parameters, extra) => Object.assign({ parameters, type, typeVersion, name }, extra || {});
const E = (js) => '={{ ' + js + ' }}';
const code = (name, jsCode) => mk(name, 'n8n-nodes-base.code', 2, { jsCode });
const ifBool = (name, left) => mk(name, 'n8n-nodes-base.if', 2.2, { conditions: { options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 2 }, conditions: [{ id: 'c1', leftValue: left, rightValue: '', operator: { type: 'boolean', operation: 'true', singleValue: true } }], combinator: 'and' }, options: {} });
const table = () => ({ __rl: true, value: IDS.table, mode: 'id' });
const bySlug = [{ keyName: 'slug', keyValue: E('$json.slug') }];
const respond = (name, body, options) => mk(name, 'n8n-nodes-base.respondToWebhook', 1.1, { respondWith: 'text', responseBody: body, options });
const S = (name, what, needs, color, nodes) => ({ name, what, needs, color, nodes });

function finish(key, name, nodes, links, sections, settings) {
  const conn = {};
  for (const [from, to, out = 0] of links) { conn[from] = conn[from] || { main: [] }; while (conn[from].main.length <= out) conn[from].main.push([]); conn[from].main[out].push({ node: to, type: 'main', index: 0 }); }
  const withIds = nodes.map((n, i) => ({ id: `sq-roadmap-${key}-${String(i + 1).padStart(2, '0')}-` + n.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''), ...n }));
  const placed = layout({ nodes: withIds, sections, edges: links.map(l => [l[0], l[1], 'main']) });
  const wf = { name, nodes: placed.nodes, connections: conn, settings: { executionOrder: 'v1', ...(IDS.errorWorkflow ? { errorWorkflow: IDS.errorWorkflow } : {}), ...settings } };
  return { wf, sections };
}

// ---- MAIN: SQ Roadmap 01 ----
function buildMain() {
  const set = (name, value, type) => ({ id: 'a-' + name, name, value, type });
  const nodes = [
    mk('Every 15 minutes', 'n8n-nodes-base.scheduleTrigger', 1.2, { rule: { interval: [{ field: 'minutes', minutesInterval: 15 }] } }),
    mk('GET roadmap', 'n8n-nodes-base.webhook', 2, { httpMethod: 'GET', path: 'roadmap', responseMode: 'responseNode', options: {} }),
    mk('Config', 'n8n-nodes-base.set', 3.4, { assignments: { assignments: [set('kill', false, 'boolean'), set('dry_run', true, 'boolean'), set('projects_json', JSON.stringify(projects), 'string')] }, includeOtherFields: true, options: {} }),
    ifBool('Web request?', E('$json.query !== undefined')),
    code('Check key', bundle(SHA, `const j = $input.first().json, q = j.query || {};
const p = JSON.parse(j.projects_json).find(x => x.slug === q.s);
const ok = !!p && typeof q.k === 'string' && q.k.length <= 200 && sha256hex(q.k) === p.sha256;
return [{ json: { ok, slug: ok ? p.slug : '' } }];`)),
    ifBool('Key ok?', E('$json.ok')),
    mk('Get page', 'n8n-nodes-base.dataTable', 1.1, { operation: 'get', dataTableId: table(), filters: { conditions: bySlug }, returnAll: false, limit: 1 }, { alwaysOutputData: true }),
    respond('Respond page', E(`$json.html || '<p>Not built yet. Try again in 15 minutes.</p>'`), { responseHeaders: { entries: [{ name: 'Content-Type', value: 'text/html; charset=utf-8' }, { name: 'Cache-Control', value: 'no-store' }] } }),
    respond('Respond 404', 'Not found', { responseCode: 404 }),
    ifBool('Kill switch?', E('$json.kill')),
    code('One item per project', `const c = $input.first().json;
return JSON.parse(c.projects_json).map(p => ({ json: { slug: p.slug, title: p.title, repo: p.repo, vision: p.vision, dry_run: c.dry_run } }));`),
    mk('Call SQ Roadmap 11 Build Page', 'n8n-nodes-base.executeWorkflow', 1.2, {
      source: 'database', workflowId: { __rl: true, value: IDS.sub, mode: 'id' },
      workflowInputs: { mappingMode: 'defineBelow', value: Object.fromEntries(['slug', 'title', 'repo', 'vision', 'dry_run'].map(f => [f, E('$json.' + f)])), matchingColumns: [],
        schema: ['slug', 'title', 'repo', 'vision', 'dry_run'].map(id => ({ id, displayName: id, required: false, defaultMatch: false, display: true, canBeUsedToMatch: true, type: id === 'dry_run' ? 'boolean' : 'string', removed: false })), attemptToConvertTypes: false, convertFieldsToString: false },
      mode: 'each', options: { waitForSubWorkflow: true } }),   // one SUB run per project; a failure stops the later ones and the Error Alert fires (95.14: no continue-on-fail)
  ];
  const links = [['Every 15 minutes', 'Config'], ['GET roadmap', 'Config'], ['Config', 'Web request?'], ['Web request?', 'Check key', 0], ['Web request?', 'Kill switch?', 1],
    ['Check key', 'Key ok?'], ['Key ok?', 'Get page', 0], ['Key ok?', 'Respond 404', 1], ['Get page', 'Respond page'],
    ['Kill switch?', 'One item per project', 1], ['One item per project', 'Call SQ Roadmap 11 Build Page']];
  const sections = [
    S('WHEN IT RUNS', 'Two ways in. A timer every 15 minutes builds the pages. A GET link serves a page to the owner.', 'Nothing. The link looks like /webhook/roadmap?s=<project>&k=<key>.', 4, ['Every 15 minutes', 'GET roadmap']),
    S('SETTINGS', 'Holds every setting in one place. Tells a page request from a timer run.', 'Config keys: kill, dry_run, projects_json. Kill stops the builds only. The link keeps answering with the last saved page, because serving only reads.', 3, ['Config', 'Web request?']),
    S('SERVE THE PAGE', 'Checks the key by its hash. A right key gets the saved page. A wrong key gets 404.', 'Data Table roadmap_pages (read). Query fields s and k.', 6, ['Check key', 'Key ok?', 'Get page', 'Respond page', 'Respond 404']),
    S('BUILD THE PAGES', 'Stops when the kill switch is on. Otherwise asks the build workflow for one page per project.', 'Config keys: kill, dry_run, projects_json. Workflow SQ Roadmap 11 Build Page.', 5, ['Kill switch?', 'One item per project', 'Call SQ Roadmap 11 Build Page']),
  ];
  // A page request carries the key in its query. Do not keep successful runs: the key and the page must not sit in n8n's history (reviewer, PR #48).
  return finish('01', 'SQ Roadmap 01', nodes, links, sections, { saveDataSuccessExecution: 'none', saveManualExecutions: false });
}

// ---- SUB: SQ Roadmap 11 Build Page ----
function buildSub() {
  const cols = ['slug', 'html', 'updated_at'], field = (id) => ({ id, displayName: id, required: false, defaultMatch: false, display: true, type: 'string', readOnly: false, removed: false });
  const nodes = [
    mk('Start', 'n8n-nodes-base.executeWorkflowTrigger', 1.1, { inputSource: 'workflowInputs', workflowInputs: { values: ['slug', 'title', 'repo', 'vision'].map(name => ({ name, type: 'string' })).concat([{ name: 'dry_run', type: 'boolean' }]) } }),
    mk('Get GitHub data', 'n8n-nodes-base.httpRequest', 4.5, {
      method: 'POST', url: 'https://api.github.com/graphql', authentication: 'genericCredentialType', genericAuthType: 'httpHeaderAuth',
      sendHeaders: true, headerParameters: { parameters: [{ name: 'User-Agent', value: 'sq-roadmap' }] },
      sendBody: true, specifyBody: 'json', jsonBody: E(`JSON.stringify({ query: ${JSON.stringify(GRAPHQL)}, variables: { owner: $json.repo.split('/')[0], name: $json.repo.split('/')[1] } })`), options: {} },
      { credentials: { httpHeaderAuth: { id: IDS.credential, name: 'SQ Roadmap GitHub read-only' } }, retryOnFail: true, maxTries: 2, waitBetweenTries: 5000 }),
    code('Render page', bundle(RENDER, `const p = $('Start').first().json, now = new Date();   // one project per run (the MAIN calls with mode each)
return $input.all().map(it => {
  return { json: { slug: p.slug, dry_run: p.dry_run, updated_at: now.toISOString(), html: page(it.json, { title: p.title, vision: p.vision }, now) } }; });`)),
    ifBool('Dry run?', E('$json.dry_run')),
    mk('Save page', 'n8n-nodes-base.dataTable', 1.1, { operation: 'upsert', dataTableId: table(), matchType: 'allConditions', filters: { conditions: bySlug },
      columns: { mappingMode: 'defineBelow', value: Object.fromEntries(cols.map(c => [c, E('$json.' + c)])), matchingColumns: ['slug'], schema: cols.map(field) }, options: {} }),
  ];
  const links = [['Start', 'Get GitHub data'], ['Get GitHub data', 'Render page'], ['Render page', 'Dry run?'], ['Dry run?', 'Save page', 1]];
  const sections = [
    S('INPUT', 'Takes one project per item from the MAIN: slug, title, repo, vision and the dry_run flag.', 'Input fields slug, title, repo, vision, dry_run. Nothing is read from the parent.', 4, ['Start']),
    S('READ GITHUB', 'Asks GitHub for the issues and open pull requests of the project repo. Read only.', 'Credential SQ Roadmap GitHub read-only (issues, pull requests, metadata).', 3, ['Get GitHub data']),
    S('RENDER', 'Turns the GitHub answer into one HTML page. A GitHub error stops the run, so nothing is saved.', 'The GitHub answer and the Start item.', 5, ['Render page']),
    S('SAVE', 'On a dry run it stops here. Otherwise it saves the page, one row per project.', 'Data Table roadmap_pages (write): slug, html, updated_at.', 6, ['Dry run?', 'Save page']),
  ];
  return finish('11', 'SQ Roadmap 11 Build Page', nodes, links, sections, { ...(IDS.main ? { callerPolicy: 'workflowsFromAList', callerIds: IDS.main } : {}) });
}

if (require.main === module) {
  if (PLACEHOLDERS.length && !process.argv.includes('--draft')) { console.error('ids.json still has placeholder ids (' + PLACEHOLDERS.map(p => p[0]).join(', ') + '). Fill them in after the n8n setup, or pass --draft to write a draft that must not be deployed.'); process.exit(1); }
  if (process.argv[2] === '--hash') { console.log(sha256hex(process.argv[3] || '')); process.exit(0); }
  const dir = path.join(__dirname, 'workflows');
  for (const [file, b] of [['SQ_Roadmap_01.json', buildMain()], ['SQ_Roadmap_11.json', buildSub()]]) fs.writeFileSync(path.join(dir, file), JSON.stringify(b.wf, null, 2) + '\n');
  console.log('wrote roadmap/workflows/SQ_Roadmap_01.json and SQ_Roadmap_11.json');
}
module.exports = { buildMain, buildSub, projects, GRAPHQL, PLACEHOLDERS };
