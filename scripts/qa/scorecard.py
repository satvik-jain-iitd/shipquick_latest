#!/usr/bin/env python3
"""QA loop scorecard. Usage: scorecard.py <qa_home> | --selftest
Reads <qa_home>/runs.jsonl and <qa_home>/design-audit.jsonl (both optional). Prints plain text."""
import json, sys, os, collections

def load(p):
    if not os.path.exists(p): return []
    return [json.loads(l) for l in open(p) if l.strip()]

def card(rows, audit, params):
    out = []
    runs = collections.OrderedDict()
    for r in rows: runs.setdefault(r['run'], []).append(r)
    out.append('Runs: run | scope | rows | pass | fail | pending | new bugs | new cases | auto share')
    clean = []
    seen_bugs = set()
    for k, rs in runs.items():
        c = collections.Counter(r['result'] for r in rs)
        bugs = {r['bug'] for r in rs if r.get('bug')} - seen_bugs
        seen_bugs |= bugs
        new_cases = sum(1 for r in rs if r.get('new_case'))
        auto = sum(1 for r in rs if r['by'] == 'auto') / len(rs)
        scope = 'full' if any(r.get('scope') == 'full' for r in rs) else 'screen'
        out.append(f"  {k} | {scope} | {len(rs)} | {c['pass']} | {c['fail']} | {c['pending']} | {len(bugs)} | {new_cases} | {auto:.0%}")
        if scope == 'full':
            clean.append(len(bugs) == 0 and c['fail'] == 0 and new_cases >= params['new_attacks_per_run'])
    # attack yield, Laplace-smoothed: (fails+1)/(tries+2)
    t = collections.Counter(r.get('attack', 'basic') for r in rows)
    f = collections.Counter(r.get('attack', 'basic') for r in rows if r['result'] == 'fail')
    out.append('Attack yield: attack | tries | fails | next weight')
    for a, n in sorted(t.items(), key=lambda x: -(f[x[0]] + 1) / (x[1] + 2)):
        out.append(f"  {a} | {n} | {f[a]} | {(f[a] + 1) / (n + 2):.2f}")
    # coverage debt: bugs whose latest row is not an auto pass
    last = {}
    for r in rows:
        if r.get('bug'): last[r['bug']] = r
    debt = [f"#{b} ({r['case']}, last {r['by']} {r['result']})" for b, r in last.items() if not (r['by'] == 'auto' and r['result'] == 'pass')]
    out.append('Coverage debt (bug without a passing auto test): ' + (', '.join(debt) or 'none'))
    esc = [f"#{r['bug']} {r['case']}" for r in rows if r.get('escape')]
    out.append('Escapes (owner found outside the cases): ' + (', '.join(esc) or 'none'))
    if audit:
        last_run = max(a['run'] for a in audit)
        cur = [a for a in audit if a['run'] == last_run]
        sev = collections.Counter(a['severity'] for a in cur if a['kind'] == 'issue')
        bucket = collections.Counter(a.get('bucket', '?') for a in cur if a['kind'] == 'issue')
        out.append(f"Design audit run {last_run}: {len({a['screen'] for a in cur})} screens, "
                   f"{sum(1 for a in cur if a['kind']=='good')} good, issues {dict(sev)}, roadmap {dict(bucket)}")
    k = params['clean_runs_to_stop']
    streak = 0
    for c in reversed(clean):
        if not c: break
        streak += 1
    out.append(f"Stop rule: {streak} of {k} clean full runs in a row -> {'DONE' if streak >= k else 'keep going'}")
    return '\n'.join(out)

def selftest():
    p = {'new_attacks_per_run': 1, 'clean_runs_to_stop': 2}
    rows = [
        {'run': 1, 'scope': 'full', 'case': 'TC 1.8', 'attack': 'NET-OFF', 'by': 'probe', 'result': 'fail', 'bug': 7, 'new_case': True},
        {'run': 2, 'scope': 'full', 'case': 'TC 1.8', 'attack': 'NET-OFF', 'by': 'auto', 'result': 'pass', 'bug': 7, 'new_case': False},
        {'run': 2, 'scope': 'full', 'case': 'TC 1.9', 'attack': 'TAP-DOUBLE', 'by': 'auto', 'result': 'pass', 'new_case': True},
        {'run': 3, 'scope': 'full', 'case': 'TC 2.1', 'attack': 'ENV-STALE', 'by': 'owner', 'result': 'pass', 'new_case': True},
    ]
    s = card(rows, [], p)
    assert 'Coverage debt (bug without a passing auto test): none' in s, s
    assert '2 of 2 clean full runs' in s and 'DONE' in s, s
    assert '| NET-OFF | 2 | 1 | 0.50' in s.replace('  ', '| ', 1) or 'NET-OFF | 2 | 1 | 0.50' in s, s
    rows[1]['result'] = 'fail'
    s = card(rows, [], p)
    assert '#7' in s and 'keep going' in s, s
    print('selftest ok')

if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: selftest(); sys.exit()
    home = sys.argv[1]
    params = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'params.json')))
    print(card(load(os.path.join(home, 'runs.jsonl')), load(os.path.join(home, 'design-audit.jsonl')), params))
