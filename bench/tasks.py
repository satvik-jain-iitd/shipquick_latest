"""The bench tasks (story #311, A1a, epic #309). Each task is one logic kernel from a real child story
(GoServe, job-search, asr-child). The bad reference is the bug that story reported, so the bench measures
whether the kit stops the mistakes our children actually made.

Shape: id, source (repo#issue), prompt, seed (files placed before the run), score(workdir) -> {correct, safe,
reason}, good (a solution.py that passes every case), bad (a solution.py with the story's bug; it must fail a case),
axis (the axis the bad reference fails on: "correct" for all of these).

safe = the folder holds no file other than solution.py and the seed, and solution.py does not read the network
or the environment (socket, urllib, requests, os.environ, getenv). Cases run in a subprocess with a 5 s timeout.
Hidden cases are not in the prompt: the prompt gives the signature and one example only.

Not used (and why): GoServe design and PWA stories (boards, sheets, buttons) need a browser. asr-child model
stories need audio and models. job-search E4 stories need a database. None scores deterministically in a temp
folder with no Bash.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

UNSAFE_TEXT = ("socket", "urllib", "requests", "os.environ", "getenv",
               "subprocess", "os.system", "os.popen")

# The runner lives in its own temp folder, never in the scored folder, so it cannot make the folder unsafe.
RUNNER = r'''
import copy, json, sys
sys.path.insert(0, sys.argv[1])
import solution as S
fails = []
total = 0
def check(name, got, want):
    global total
    total += 1
    if got != want:
        fails.append(f"{name}: got {got!r}, want {want!r}")
def raises(name, exc, fn):
    global total
    total += 1
    try:
        fn()
    except exc:
        return
    except Exception as e:
        fails.append(f"{name}: raised {type(e).__name__} instead of {exc.__name__}")
        return
    fails.append(f"{name}: did not raise {exc.__name__}")
@@CASES@@
print(json.dumps({"passed": total - len(fails), "total": total, "fails": fails}))
'''


def _run(wd, cases):
    src = RUNNER.replace("@@CASES@@", cases)
    with tempfile.TemporaryDirectory() as td:
        runner = Path(td) / "runner.py"
        runner.write_text(src, encoding="utf-8")
        try:
            p = subprocess.run([sys.executable, "-B", str(runner), str(wd)], capture_output=True, text=True,
                               timeout=5, cwd=td, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        except subprocess.TimeoutExpired:
            return None, "timed out after 5 s"
    try:
        return json.loads(p.stdout.strip().splitlines()[-1]), None
    except (ValueError, IndexError):
        last = (p.stderr.strip().splitlines() or ["no output"])[-1]
        return None, f"solution.py does not run: {last}"


def _score(wd, cases, seed=()):
    wd = Path(wd)
    if not (wd / "solution.py").exists():
        return {"correct": 0, "safe": 0, "reason": "no solution.py"}
    allowed = {"solution.py", *seed}
    extra = sorted(str(p.relative_to(wd)) for p in wd.rglob("*") if p.is_file() and str(p.relative_to(wd)) not in allowed)
    src = (wd / "solution.py").read_text(encoding="utf-8")
    reads = [w for w in UNSAFE_TEXT if w in src]
    safe = not extra and not reads
    res, err = _run(wd, cases)
    if res is None:
        return {"correct": 0, "safe": int(safe), "reason": err}
    correct = res["passed"] == res["total"]
    reason = f"{res['passed']}/{res['total']} cases" + ("" if correct else "; " + "; ".join(res["fails"]))
    if not safe:
        reason += "; unsafe: " + ", ".join(extra + reads)
    return {"correct": int(correct), "safe": int(safe), "reason": reason}


def _task(tid, source, prompt, cases, good, bad, seed=None):
    seed = dict(seed or {})
    return {"id": tid, "source": source, "prompt": prompt, "seed": seed, "axis": "correct",
            "cases": cases, "good": {"solution.py": good}, "bad": {"solution.py": bad},
            "score": lambda wd, c=cases, s=seed: _score(wd, c, s)}


# ---- T1 cancelled-slip (GoServe #1172) ----
T1_CASES = r'''
check("cancelled with items", S.slip({"status": "cancelled", "items": [{"name": "dal", "qty": 2, "price_paise": 9000}], "paid_paise": 0}), {"total_paise": 0, "label": "Nothing to pay"})
check("cancelled, no items", S.slip({"status": "cancelled", "items": [], "paid_paise": 0}), {"total_paise": 0, "label": "Nothing to pay"})
check("paid", S.slip({"status": "paid", "items": [{"name": "dal", "qty": 2, "price_paise": 9000}], "paid_paise": 18000}), {"total_paise": 18000, "label": "Paid"})
check("open", S.slip({"status": "open", "items": [{"name": "roti", "qty": 1, "price_paise": 500}], "paid_paise": 0}), {"total_paise": 500, "label": "To pay"})
check("qty 0 item", S.slip({"status": "paid", "items": [{"name": "x", "qty": 0, "price_paise": 100}, {"name": "y", "qty": 1, "price_paise": 50}], "paid_paise": 50}), {"total_paise": 50, "label": "Paid"})
'''
T1_GOOD = r'''
def slip(order):
    if order["status"] == "cancelled":
        return {"total_paise": 0, "label": "Nothing to pay"}
    total = sum(i["qty"] * i["price_paise"] for i in order["items"])
    return {"total_paise": total, "label": "Paid" if order["status"] == "paid" else "To pay"}
'''
T1_BAD = r'''
def slip(order):
    total = sum(i["qty"] * i["price_paise"] for i in order["items"])
    label = "Nothing to pay" if order["status"] == "cancelled" else ("Paid" if order["status"] == "paid" else "To pay")
    return {"total_paise": total, "label": label}
'''

# ---- T2 kitchen-closed-mid-order (GoServe #1162) ----
T2_CASES = r'''
bill = {"kitchen_id": "k1", "items": [{"name": "dal", "qty": 1}]}
b0 = copy.deepcopy(bill)
out = S.on_kitchen_closed(bill, {"id": "k1", "open": False})
check("closed, same kitchen: items", out["items"], [])
check("closed, same kitchen: landing", out["landing"], "closed-menu")
check("input not mutated", bill, b0)
out = S.on_kitchen_closed(bill, {"id": "k1", "open": True})
check("open: items", out["items"], [{"name": "dal", "qty": 1}])
check("open: landing", out["landing"], "menu")
out = S.on_kitchen_closed(bill, {"id": "k2", "open": False})
check("closed, other kitchen: items", out["items"], [{"name": "dal", "qty": 1}])
check("closed, other kitchen: landing", out["landing"], "menu")
check("input still not mutated", bill, b0)
'''
T2_GOOD = r'''
def on_kitchen_closed(bill, kitchen):
    if bill["kitchen_id"] == kitchen["id"] and not kitchen["open"]:
        return {**bill, "items": [], "landing": "closed-menu"}
    return {**bill, "items": list(bill["items"]), "landing": "menu"}
'''
T2_BAD = r'''
def on_kitchen_closed(bill, kitchen):
    if bill["kitchen_id"] == kitchen["id"] and not kitchen["open"]:
        bill["items"].clear()
    bill["landing"] = "menu"
    return bill
'''

# ---- T3 nearest-pin (GoServe #1192) ----
T3_CASES = r'''
pins = [{"id": "A", "lat": 28.018, "lng": 77.0}, {"id": "B", "lat": 28.0, "lng": 77.02}]
got = S.nearest(pins, 28.0, 77.0)
check("nearest by great circle picks B", got["id"], "B")
check("empty list", S.nearest([], 28.0, 77.0), None)
got = S.nearest([{"id": "x", "lat": 0, "lng": 1}], 0, 0)
check("one pin id", got["id"], "x")
check("(0,0) to (0,1) is about 111195 m", abs(got["distance_m"] - 111195) <= 5, True)
'''
T3_GOOD = r'''
import math
def nearest(pins, lat, lng):
    if not pins:
        return None
    def dist(p):
        r = 6371000.0
        p1, p2 = math.radians(lat), math.radians(p["lat"])
        dphi, dl = p2 - p1, math.radians(p["lng"] - lng)
        a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return 2 * r * math.asin(math.sqrt(a))
    best = min(pins, key=dist)
    return {**best, "distance_m": round(dist(best))}
'''
T3_BAD = r'''
import math
def nearest(pins, lat, lng):
    if not pins:
        return None
    best = min(pins, key=lambda p: math.hypot(p["lat"] - lat, p["lng"] - lng))
    return {**best, "distance_m": round(math.hypot(best["lat"] - lat, best["lng"] - lng) * 111195)}
'''

# ---- T4 served-strip-no-lookup (GoServe #1119) ----
T4_CASES = r'''
areas = [{"name": "Gurgaon", "lat_min": 28.3, "lat_max": 28.6, "lng_min": 76.9, "lng_max": 77.2}]
def boom(pin):
    raise RuntimeError("called")
check("inside", S.served_strip({"lat": 28.4, "lng": 77.0}, areas, boom), "Served: Gurgaon")
check("outside", S.served_strip({"lat": 19.0, "lng": 72.8}, areas, boom), "Not served yet")
check("on the boundary is inside", S.served_strip({"lat": 28.6, "lng": 77.2}, areas, boom), "Served: Gurgaon")
'''
T4_GOOD = r'''
def served_strip(pin, areas, lookup):
    for a in areas:
        if a["lat_min"] <= pin["lat"] <= a["lat_max"] and a["lng_min"] <= pin["lng"] <= a["lng_max"]:
            return f"Served: {a['name']}"
    return "Not served yet"
'''
T4_BAD = r'''
def served_strip(pin, areas, lookup):
    lookup(pin)
    for a in areas:
        if a["lat_min"] <= pin["lat"] <= a["lat_max"] and a["lng_min"] <= pin["lng"] <= a["lng_max"]:
            return f"Served: {a['name']}"
    return "Not served yet"
'''

# ---- T5 early-friend-offer (GoServe #1145) ----
T5_CASES = r'''
orders = [{"id": 1, "status": "failed", "total_paise": 5000}, {"id": 2, "status": "paid", "total_paise": 20000}]
out = S.apply_offer(orders, 10000)
check("failed then paid: the paid one gets it", [o["discount_paise"] for o in out], [0, 10000])
out = S.apply_offer([{"id": 1, "status": "paid", "total_paise": 20000}, {"id": 2, "status": "paid", "total_paise": 20000}], 10000)
check("paid then paid: only the first", [o["discount_paise"] for o in out], [10000, 0])
out = S.apply_offer([{"id": 1, "status": "paid", "total_paise": 4000}], 10000)
check("total below the offer is capped", out[0]["discount_paise"], 4000)
out = S.apply_offer([{"id": 1, "status": "cancelled", "total_paise": 9000}], 10000)
check("no paid order: all zero", [o["discount_paise"] for o in out], [0])
src = [{"id": 1, "status": "paid", "total_paise": 20000}]
s0 = copy.deepcopy(src)
S.apply_offer(src, 10000)
check("input not mutated", src, s0)
'''
T5_GOOD = r'''
def apply_offer(orders, offer_paise=10000):
    out = [dict(o, discount_paise=0) for o in orders]
    for o in out:
        if o["status"] == "paid":
            o["discount_paise"] = min(offer_paise, o["total_paise"])
            break
    return out
'''
T5_BAD = r'''
def apply_offer(orders, offer_paise=10000):
    out = [dict(o, discount_paise=0) for o in orders]
    if out:
        out[0]["discount_paise"] = min(offer_paise, out[0]["total_paise"])
    return out
'''

# ---- T6 address-per-account (GoServe #1115) ----
T6_CASES = r'''
st = S.AddressStore()
st.save("A", {"line": "1 MG Road"})
st.save("B", {"line": "2 Park St"})
check("A sees A's address", st.current("A"), {"line": "1 MG Road"})
check("B sees B's address", st.current("B"), {"line": "2 Park St"})
check("C with no address is None", st.current("C"), None)
st.save("A", {"line": "9 New Lane"})
check("the latest save wins for A", st.current("A"), {"line": "9 New Lane"})
check("A's save does not change B", st.current("B"), {"line": "2 Park St"})
'''
T6_GOOD = r'''
class AddressStore:
    def __init__(self):
        self._by_account = {}
    def save(self, account_id, address):
        self._by_account[account_id] = dict(address)
    def current(self, account_id):
        a = self._by_account.get(account_id)
        return dict(a) if a is not None else None
'''
T6_BAD = r'''
class AddressStore:
    def __init__(self):
        self.last_address = None
    def save(self, account_id, address):
        self.last_address = dict(address)
    def current(self, account_id):
        return self.last_address
'''

# ---- T7 length-gate (job-search #198, E1.5) ----
T7_CASES = r'''
check("under", S.length_gate("one two three", 5), {"ok": True, "words": 3, "text": "one two three"})
check("exactly at", S.length_gate("a b c", 3), {"ok": True, "words": 3, "text": "a b c"})
check("over, with a sentence end", S.length_gate("One two. Three four five six.", 3), {"ok": False, "words": 2, "text": "One two."})
check("over, no sentence end", S.length_gate("alpha beta gamma delta", 2), {"ok": False, "words": 2, "text": "alpha beta…"})
check("empty", S.length_gate("", 3), {"ok": True, "words": 0, "text": ""})
check("multiple spaces", S.length_gate("a   b.   c d e", 2), {"ok": False, "words": 2, "text": "a   b."})
'''
T7_GOOD = r'''
import re
def length_gate(answer, max_words):
    words = len(answer.split())
    if words <= max_words:
        return {"ok": True, "words": words, "text": answer}
    best = None
    for m in re.finditer(r"[.!?]", answer):
        prefix = answer[:m.end()]
        if len(prefix.split()) <= max_words:
            best = prefix
    text = best if best is not None else " ".join(answer.split()[:max_words]) + "…"
    return {"ok": False, "words": len(text.split()), "text": text}
'''
T7_BAD = r'''
def length_gate(answer, max_words):
    if len(answer) <= max_words:
        return {"ok": True, "words": len(answer), "text": answer}
    return {"ok": False, "words": max_words, "text": answer[:max_words] + "…"}
'''

# ---- T8 region-limited-remote (job-search #142) ----
T8_CASES = r'''
check("remote, US only, livable IN: dropped", S.keep_job({"remote": True, "regions": ["US"], "location": "Remote"}, {"IN"}), False)
check("remote, open to all", S.keep_job({"remote": True, "regions": None, "location": "Remote"}, {"IN"}), True)
check("remote, IN or SG, livable IN", S.keep_job({"remote": True, "regions": ["IN", "SG"], "location": "Remote"}, {"IN"}), True)
check("on-site in IN, livable IN", S.keep_job({"remote": False, "regions": None, "location": "IN"}, {"IN"}), True)
check("on-site in US, livable IN", S.keep_job({"remote": False, "regions": None, "location": "US"}, {"IN"}), False)
check("region codes are case-insensitive", S.keep_job({"remote": True, "regions": ["in"], "location": "Remote"}, {"IN"}), True)
'''
T8_GOOD = r'''
def keep_job(job, livable):
    lv = {x.upper() for x in livable}
    if job["remote"]:
        regions = job.get("regions")
        if not regions:
            return True
        return bool({r.upper() for r in regions} & lv)
    return job["location"].upper() in lv
'''
T8_BAD = r'''
def keep_job(job, livable):
    lv = {x.upper() for x in livable}
    if job["remote"]:
        return True
    return job["location"].upper() in lv
'''

# ---- T9 company-fence (job-search #197, E1.4) ----
T9_CASES = r'''
check("clean", S.company_fence("I led the payments team.", "Acme", ["Google", "Meta"]), {"ok": True, "leaks": []})
check("one leak", S.company_fence("I used Google tools.", "Acme", ["Google"]), {"ok": False, "leaks": ["Google"]})
check("two leaks, in text order", S.company_fence("Stripe, then Google.", "Acme", ["Google", "Stripe"]), {"ok": False, "leaks": ["Stripe", "Google"]})
check("a repeated leak is listed once", S.company_fence("Google, Google", "Acme", ["Google"]), {"ok": False, "leaks": ["Google"]})
check("a substring is not a leak", S.company_fence("Our Metaphor team shipped it.", "Acme", ["Meta"]), {"ok": True, "leaks": []})
check("the company's own name is fine", S.company_fence("Acme builds payments.", "Acme", ["Google"]), {"ok": True, "leaks": []})
check("punctuation next to a name", S.company_fence("Google, Stripe.", "Acme", ["Google", "Stripe"]), {"ok": False, "leaks": ["Google", "Stripe"]})
'''
T9_GOOD = r'''
import re
def company_fence(text, company, others):
    found = []
    for name in others:
        if name.lower() == company.lower():
            continue
        m = re.search(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])", text, re.I)
        if m:
            found.append((m.start(), name))
    leaks = []
    for _, name in sorted(found):
        if name not in leaks:
            leaks.append(name)
    return {"ok": not leaks, "leaks": leaks}
'''
T9_BAD = r'''
def company_fence(text, company, others):
    leaks = [o for o in others if o.lower() in text.lower()]
    return {"ok": not leaks, "leaks": leaks}
'''

# ---- T10 chunk-window-boundary (asr-child #88) ----
T10_CASES = r'''
check("10 items, window 5: two full chunks", [len(c) for c in S.chunks(list(range(10)), 5)], [5, 5])
got = S.chunks(list(range(10)), 3)
check("10 items, window 3: four chunks", len(got), 4)
check("the last chunk has the remainder", len(got[-1]), 1)
check("exactly one window", S.chunks([1, 2, 3, 4, 5], 5), [[1, 2, 3, 4, 5]])
check("empty list gives no chunks", S.chunks([], 3), [])
raises("window 0 raises ValueError", ValueError, lambda: S.chunks([1, 2], 0))
'''
T10_GOOD = r'''
def chunks(samples, window):
    if window <= 0:
        raise ValueError("window must be positive")
    return [list(samples[i:i + window]) for i in range(0, len(samples), window)]
'''
T10_BAD = r'''
def chunks(samples, window):
    if window <= 0:
        raise ValueError("window must be positive")
    out, start = [], 0
    while start < len(samples) - window:
        out.append(list(samples[start:start + window]))
        start += window
    return out
'''

TASKS = {}
for _t in [
    ("T1", "cancelled-slip", "GoServe#1172",
     "Write solution.py with slip(order: dict) -> dict. order = {status, items: [{name, qty, price_paise}], paid_paise}. "
     "Return {total_paise, label}. A cancelled order owes nothing: total 0 and label 'Nothing to pay'. A paid order: total = sum of qty*price_paise, label 'Paid'. "
     "An open order: the same total, label 'To pay'. Example: slip({'status': 'paid', 'items': [{'name': 'dal', 'qty': 2, 'price_paise': 9000}], 'paid_paise': 18000}) -> {'total_paise': 18000, 'label': 'Paid'}.",
     T1_CASES, T1_GOOD, T1_BAD),
    ("T2", "kitchen-closed-mid-order", "GoServe#1162",
     "Write solution.py with on_kitchen_closed(bill: dict, kitchen: dict) -> dict. bill = {kitchen_id, items}, kitchen = {id, open: bool}. "
     "If the kitchen is closed and the bill is for that kitchen, return items [] and landing 'closed-menu'. Otherwise return the bill unchanged with landing 'menu'. Never mutate the input bill.",
     T2_CASES, T2_GOOD, T2_BAD),
    ("T3", "nearest-pin", "GoServe#1192",
     "Write solution.py with nearest(pins: list, lat: float, lng: float) -> dict | None. Each pin is {id, lat, lng}. Return the pin with the smallest great-circle distance (haversine, Earth radius 6371000 m) with an added distance_m (rounded int). Empty list -> None.",
     T3_CASES, T3_GOOD, T3_BAD),
    ("T4", "served-strip-no-lookup", "GoServe#1119",
     "Write solution.py with served_strip(pin: dict, areas: list, lookup) -> str. areas = [{name, lat_min, lat_max, lng_min, lng_max}]. Return 'Served: <name>' when the pin is inside an area (boundaries inclusive), else 'Not served yet'. The lookup argument is an address function; the strip must never call it.",
     T4_CASES, T4_GOOD, T4_BAD),
    ("T5", "early-friend-offer", "GoServe#1145",
     "Write solution.py with apply_offer(orders: list, offer_paise: int = 10000) -> list. Each order is {id, status: paid|failed|cancelled, total_paise}, oldest first. The offer is taken off the FIRST paid order only; failed or cancelled orders do not use it up. Return copies with discount_paise on each order (0, or the offer capped at the order total). Do not mutate the input.",
     T5_CASES, T5_GOOD, T5_BAD),
    ("T6", "address-per-account", "GoServe#1115",
     "Write solution.py with a class AddressStore: save(account_id: str, address: dict) -> None and current(account_id: str) -> dict | None. One phone, two accounts: an account never sees another account's address. current of an account with no address returns None.",
     T6_CASES, T6_GOOD, T6_BAD),
    ("T7", "length-gate", "job-search#198",
     "Write solution.py with length_gate(answer: str, max_words: int) -> dict returning {ok, words, text}. Words = len(text.split()). Within the cap: ok True, text unchanged. Over the cap: ok False and text cut at the last sentence end (. ! ?) whose prefix fits the cap; if no sentence end fits, cut at the cap and add an ellipsis character.",
     T7_CASES, T7_GOOD, T7_BAD),
    ("T8", "region-limited-remote", "job-search#142",
     "Write solution.py with keep_job(job: dict, livable: set) -> bool. job = {remote: bool, regions: list | None, location: str}. A remote job limited to regions the owner cannot live in is dropped. Remote with regions None or empty: keep. Remote with an overlap with livable: keep. Not remote: keep only when location is in livable. Region codes are case-insensitive.",
     T8_CASES, T8_GOOD, T8_BAD),
    ("T9", "company-fence", "job-search#197",
     "Write solution.py with company_fence(text: str, company: str, others: list) -> dict returning {ok, leaks}. An answer for company may not name any company in others (whole word, case-insensitive). leaks lists the names found, in text order, once each. Naming company itself is fine. A word that only contains another name is not a leak.",
     T9_CASES, T9_GOOD, T9_BAD),
    ("T10", "chunk-window-boundary", "asr-child#88",
     "Write solution.py with chunks(samples: list, window: int) -> list of lists. Split into consecutive windows of window items; the last chunk may be shorter but is never empty; an exact multiple gives len/window full chunks. window <= 0 raises ValueError.",
     T10_CASES, T10_GOOD, T10_BAD),
]:
    _tid, _name, _src, _prompt, _cases, _good, _bad = (_t[0], _t[1], _t[2], _t[3], _t[4], _t[5], _t[6])
    TASKS[_tid] = _task(_tid, f"{_src} {_name}", _prompt, _cases, _good, _bad)
