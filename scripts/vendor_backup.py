#!/usr/bin/env python3
"""Story #242: the offline vendor backup (ADR-012, docs/VENDOR_BACKUP.md). Stdlib only.

  --plan [--resolve]       print what is backed up (npm from the lockfile, Maven roots from vendor_pins.json;
                           --resolve also walks the POMs and Gradle module files, so it needs the network)
  --manifest-check <dir>   verify a backup folder against its MANIFEST.json
  --build <dir>            fetch and write the backup into <dir> (CI only; refuses on a Mac unless VENDOR_ALLOW_LOCAL=1)

Exit 0 when fine, 1 with one line per problem.
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "ui/tool/package-lock.json"
PINS = ROOT / "scripts/vendor_pins.json"
M3_DOC = ROOT / "docs/research/android-m3-api.md"
MAX_BYTES = 90 * 1024 * 1024  # GitHub refuses a file over 100 MB
PLATFORMS = {"androidJvm", "jvm"}
USAGES = {"java-api", "java-runtime"}
UNRESOLVED: list[str] = []  # transitive dependencies no repository has a POM for
# ponytail: a file over MAX_BYTES fails the build, no part-splitting; add .partNNN files if one ever nears it.


def sha(data: bytes, algo="sha256") -> str:
    return hashlib.new(algo, data).hexdigest()


def file_sha(path: Path, algo="sha256") -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cache_path(integrity: str) -> str:
    """npm's content-addressed cache path for an `sha512-<base64>` integrity string."""
    algo, b64 = integrity.split("-", 1)
    hexd = base64.b64decode(b64).hex()
    return f"npm-cache/_cacache/content-v2/{algo}/{hexd[:2]}/{hexd[2:4]}/{hexd[4:]}"


def npm_entries(lock: Path = LOCK) -> list[dict]:
    out = []
    for key, p in json.loads(lock.read_text())["packages"].items():
        if not key:
            continue
        out.append({"kind": "npm", "name": key.split("node_modules/")[-1], "version": p["version"],
                    "url": p.get("resolved", ""), "integrity": p.get("integrity", ""),
                    "license": str(p.get("license", "unknown"))})
    return out


def pins() -> dict:
    return json.loads(PINS.read_text())


def coord(s: str) -> tuple[str, str, str]:
    g, a, *v = s.split(":")
    return g, a, (v[0] if v else "")


def pinned_roots() -> list[tuple[str, str, str]]:
    """The Gradle roots: the BOM, then each root at its pinned version ('' = the BOM picks it)."""
    p = pins()
    return [coord(p["bom"])] + [(*coord(r)[:2], p["material3"] if r.endswith(":material3") else "") for r in p["roots"]]


def plan(resolve=False, repos=None, fetch=None) -> list[dict]:
    out = npm_entries()
    if resolve:
        r = resolve_maven(pinned_roots()[0], pinned_roots()[1:], repos or pins()["repos"], fetch or http_get)
        out += [{k: v for k, v in m.items() if k != "data"} for m in r]
    else:
        out += [{"kind": "maven", "name": f"{g}:{a}", "version": v or "(from the BOM)"} for g, a, v in pinned_roots()]
    return out


def drift_problems() -> list[str]:
    ver = pins()["material3"]
    if ver not in M3_DOC.read_text():
        return [f"vendor_pins.json says material3 {ver}, but {M3_DOC.relative_to(ROOT)} does not name it"]
    return []


# ---------- Maven resolution (a superset of what Gradle fetches; the offline restore proves it) ----------

def http_get(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except urllib.error.URLError as e:  # a missing file:// path, in tests
        if isinstance(e.reason, FileNotFoundError):
            return None
        raise


def mpath(g, a, v, name):
    return f"{g.replace('.', '/')}/{a}/{v}/{name}"


def find(repos, fetch, path):
    for r in repos:
        data = fetch(f"{r}/{path}")
        if data is not None:
            return r, data
    return None, None


def pom_info(xml: bytes) -> dict:
    root = ET.fromstring(re.sub(rb"""\sxmlns=(?:"[^"]*"|'[^']*')""", b"", xml, count=1))
    ver = (root.findtext("version") or root.findtext("parent/version") or "").strip()
    grp = (root.findtext("groupId") or root.findtext("parent/groupId") or "").strip()
    props = {c.tag: (c.text or "").strip() for c in root.findall("properties/*")}
    props.update({"project.version": ver, "version": ver, "project.groupId": grp})

    def sub(s):
        return re.sub(r"\$\{([^}]+)\}", lambda m: props.get(m.group(1), m.group(0)), s or "").strip()

    def dep(d):
        return sub(d.findtext("groupId")), sub(d.findtext("artifactId")), sub(d.findtext("version"))

    deps = [dep(d) for d in root.findall("dependencies/dependency")
            if (d.findtext("scope") or "compile").strip() in ("compile", "runtime")
            and (d.findtext("optional") or "false").strip() != "true"]
    lic = [f"{(x.findtext('name') or '').strip()} {(x.findtext('url') or '').strip()}".strip() for x in root.findall("licenses/license")]
    return {"packaging": (root.findtext("packaging") or "jar").strip(), "deps": deps, "licenses": lic,
            "managed": [dep(d) for d in root.findall("dependencyManagement/dependencies/dependency") + root.findall("dependencies/dependency")]}


def module_info(raw: bytes) -> dict:
    """Gradle module metadata: keep the Android and JVM variants only (never iOS or native klibs)."""
    files, deps, links = [], [], []
    for var in json.loads(raw).get("variants", []):
        at = var.get("attributes", {})
        if at.get("org.gradle.usage") not in USAGES or at.get("org.gradle.category") == "documentation":
            continue
        if at.get("org.jetbrains.kotlin.platform.type", "androidJvm") not in PLATFORMS:
            continue
        files += [f["url"] for f in var.get("files", [])]
        for d in var.get("dependencies", []):
            v = d.get("version", {})
            deps.append((d["group"], d["module"], v.get("requires") or v.get("strictly") or v.get("prefers") or ""))
        if "available-at" in var:
            x = var["available-at"]
            links.append((x["group"], x["module"], x["version"]))
    return {"files": files, "deps": deps, "links": links}


def _file(c, name, repo, data, lic) -> dict:
    g, a, v = c
    return {"kind": "maven", "name": f"{g}:{a}", "version": v, "file": f"maven/{mpath(g, a, v, name)}",
            "url": f"{repo}/{mpath(g, a, v, name)}", "data": data, "licenses": lic}


def resolve_maven(bom, roots, repos, fetch) -> list[dict]:
    """One entry per artifact file (pom, module, aar or jar) with its url, bytes and the POM's license text."""
    repo, pom = find(repos, fetch, mpath(*bom, f"{bom[1]}-{bom[2]}.pom"))
    if pom is None:
        raise SystemExit(f"BOM {bom} not found in any repository")
    info = pom_info(pom)
    managed = {(g, a): v for g, a, v in info["managed"]}
    out, seen = [_file(bom, f"{bom[1]}-{bom[2]}.pom", repo, pom, info["licenses"])], set()
    bmod = fetch(f"{repo}/{mpath(*bom, f'{bom[1]}-{bom[2]}.module')}")
    if bmod is not None:  # a Gradle platform lists its versions as constraints in the module file
        out.append(_file(bom, f"{bom[1]}-{bom[2]}.module", repo, bmod, info["licenses"]))
        for var in json.loads(bmod).get("variants", []):
            for d in var.get("dependencyConstraints", []) + var.get("dependencies", []):
                managed[(d["group"], d["module"])] = d.get("version", {}).get("requires", "")
    if not managed:
        raise SystemExit(f"BOM {bom} lists no versions; its POM starts: {pom[:600]!r}")
    todo = [(g, a, v or managed.get((g, a), "")) for g, a, v in roots]
    while todo:
        g, a, v = todo.pop()
        v = re.split(r"[,)\]]", v.strip("[]()"))[0] if v[:1] in ("[", "(") else v  # a range `[1.6.0]` or `[1.0,2.0)`: its lower end
        if (g, a, v) in seen:
            continue
        seen.add((g, a, v))
        if not v:
            raise SystemExit(f"no version for {g}:{a}; the BOM manages {len(managed)} entries, e.g. {sorted(managed)[:3]}")
        repo, pom = find(repos, fetch, mpath(g, a, v, f"{a}-{v}.pom"))
        if pom is None:
            if (g, a) in {(x[0], x[1]) for x in roots}:
                raise SystemExit(f"{g}:{a}:{v} has no POM in any repository")
            UNRESOLVED.append(f"{g}:{a}:{v}")  # not on Google Maven or Maven Central; named in the MANIFEST
            continue
        info = pom_info(pom)
        out.append(_file((g, a, v), f"{a}-{v}.pom", repo, pom, info["licenses"]))
        names, deps = [], list(info["deps"])
        mod = fetch(f"{repo}/{mpath(g, a, v, f'{a}-{v}.module')}")
        if mod is not None:
            out.append(_file((g, a, v), f"{a}-{v}.module", repo, mod, info["licenses"]))
            mi = module_info(mod)
            names, deps = mi["files"], deps + mi["deps"]
            todo += mi["links"]
        elif info["packaging"] != "pom":
            names = [f"{a}-{v}.{'aar' if info['packaging'] == 'aar' else 'jar'}"]
        for n in dict.fromkeys(names):
            data = fetch(f"{repo}/{mpath(g, a, v, n)}")
            if data is None:
                raise SystemExit(f"{g}:{a}:{v}: file {n} is listed but not in {repo}")
            out.append(_file((g, a, v), n, repo, data, info["licenses"]))
        # Gradle takes the higher of the declared version and the BOM's, so keep both; no version anywhere: Gradle skips it too
        todo += [(dg, da, ver) for dg, da, dv in deps for ver in {dv, managed.get((dg, da), "")} if ver and ver != "unspecified"]
    return out


# ---------- build (CI only) ----------

def verified(url: str, data: bytes, fetch) -> None:
    for algo in ("sha256", "sha1"):
        want = fetch(f"{url}.{algo}")
        if want:
            if want.decode().split()[0].strip().lower() != sha(data, algo):
                raise SystemExit(f"checksum mismatch ({algo}): {url}")
            return
    raise SystemExit(f"no .sha256 or .sha1 beside {url}; refusing an unchecked file")


def _write_license(d: Path, text: bytes | None, declared: str) -> str:
    d.mkdir(parents=True, exist_ok=True)
    name = "LICENSE" if text else "LICENSE.declared"
    (d / name).write_bytes(text or f"No license file ships in this package. {declared}\n".encode())
    return name


def build(dest: Path, repos=None, fetch=None) -> None:
    if not (os.environ.get("CI") == "true" or os.environ.get("VENDOR_ALLOW_LOCAL") == "1"):
        raise SystemExit("vendor_backup.py --build downloads packages: it runs on GitHub CI only (VENDOR_ALLOW_LOCAL=1 overrides)")
    fetch = fetch or http_get
    dest.mkdir(parents=True, exist_ok=True)
    mf = dest / "MANIFEST.json"
    old = {(e["name"], e["version"], e["file"]): e["date"] for e in json.loads(mf.read_text())["artifacts"]} if mf.exists() else {}
    entries = []
    # npm: npm itself fetches into the cache, checking each tarball against the lockfile integrity.
    with tempfile.TemporaryDirectory() as tmp:
        for f in ("package.json", "package-lock.json"):
            shutil.copy(LOCK.parent / f, tmp)
        # --force: also fetch the optional packages built for other systems (esbuild for macOS, and so on).
        subprocess.run(["npm", "ci", "--ignore-scripts", "--force", "--no-audit", "--no-fund", "--cache", str(dest.resolve() / "npm-cache")], cwd=tmp, check=True)
        for e in npm_entries():
            rel = cache_path(e["integrity"])
            lic = next(iter(sorted((Path(tmp) / "node_modules" / e["name"]).glob("LICEN[CS]E*"))), None)
            ldir = f"licenses/npm/{e['name']}@{e['version']}"
            lname = _write_license(dest / ldir, lic.read_bytes() if lic else None, f"package.json declares: {e['license']}")
            entries.append({**{k: e[k] for k in ("kind", "name", "version", "url", "license")}, "file": rel,
                            "sha256": file_sha(dest / rel), "license_file": f"{ldir}/{lname}"})
    repos = repos or pins()["repos"]
    net = set()

    def fetch_or_keep(url):  # a file already in the backup is not fetched again (it was checked when it was stored)
        for r in repos:
            kept = dest / "maven" / url[len(r) + 1:]
            if url.startswith(r + "/") and kept.is_file():
                return kept.read_bytes()
        data = fetch(url)
        if data is not None:
            net.add(url)
        return data

    for m in resolve_maven(pinned_roots()[0], pinned_roots()[1:], repos, fetch_or_keep):
        data, p = m.pop("data"), dest / m["file"]
        if len(data) > MAX_BYTES:
            raise SystemExit(f"{m['file']} is over {MAX_BYTES} bytes; GitHub would refuse it")
        if m["url"] in net:
            verified(m["url"], data, fetch)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        lic = "; ".join(m["licenses"]) or "unknown"
        ldir = f"licenses/maven/{m['name'].replace(':', '__')}@{m['version']}"
        lname = _write_license(dest / ldir, None, f"POM declares: {lic}")
        entries.append({**{k: m[k] for k in ("kind", "name", "version", "url", "file")}, "license": lic,
                        "sha256": sha(data), "license_file": f"{ldir}/{lname}"})
    today = datetime.date.today().isoformat()
    for e in entries:
        e["date"] = old.get((e["name"], e["version"], e["file"]), today)
    entries.sort(key=lambda e: (e["kind"], e["name"], e["version"], e["file"]))
    if UNRESOLVED:
        print("NOT BACKED UP (no POM in any repository):", ", ".join(sorted(set(UNRESOLVED))))
    mf.write_text(json.dumps({"made": today, "unresolved": sorted(set(UNRESOLVED)), "artifacts": entries}, indent=1) + "\n")


# ---------- manifest check ----------

def manifest_check(folder: Path, lock: Path = LOCK) -> list[str]:
    mf = folder / "MANIFEST.json"
    if not mf.exists():
        return [f"{mf}: no MANIFEST.json (no backup here)"]
    arts = json.loads(mf.read_text())["artifacts"]
    bad = []
    for e in arts:
        tag = f"{e.get('name')}@{e.get('version')}"
        miss = [k for k in ("name", "version", "sha256", "url", "date", "file", "license_file") if not e.get(k)]
        if miss:
            bad.append(f"{tag}: MANIFEST lacks {', '.join(miss)}")
            continue
        p = folder / e["file"]
        if not p.is_file():
            bad.append(f"{tag}: file missing: {e['file']}")
        elif file_sha(p) != e["sha256"]:
            bad.append(f"{tag}: sha256 does not match: {e['file']}")
        lp = folder / e["license_file"]
        if not (lp.is_file() and lp.stat().st_size):
            bad.append(f"{tag}: license file missing: {e['license_file']}")
    have = {(e["name"], e["version"]) for e in arts if e.get("kind") == "npm"}
    for e in npm_entries(lock):
        tag = f"{e['name']}@{e['version']}"
        if (e["name"], e["version"]) not in have:
            bad.append(f"lockfile entry not in the backup: {tag}")
            continue
        algo, b64 = e["integrity"].split("-", 1)
        p = folder / cache_path(e["integrity"])
        if not p.is_file() or file_sha(p, algo) != base64.b64decode(b64).hex():
            bad.append(f"{tag}: tarball missing or not the lockfile integrity")
    maven = {(e["name"], e["version"]) for e in arts if e.get("kind") == "maven"}
    for g, a, v in pinned_roots():
        if (f"{g}:{a}", v) not in maven if v else not any(n == f"{g}:{a}" for n, _ in maven):
            bad.append(f"pinned Gradle artifact not in the backup: {g}:{a}:{v or '(from the BOM)'}")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--manifest-check", metavar="DIR")
    ap.add_argument("--build", metavar="DIR")
    a = ap.parse_args(argv)
    if a.manifest_check:
        bad = manifest_check(Path(a.manifest_check))
        print("\n".join(f"FAIL {b}" for b in bad) or "ok   backup matches its MANIFEST")
        return 1 if bad else 0
    if a.build:
        build(Path(a.build))
        return 0
    if a.plan:
        for e in plan(a.resolve):
            print(json.dumps({k: e[k] for k in ("kind", "name", "version", "integrity", "url", "file") if e.get(k)}))
        bad = drift_problems()
        print("\n".join(f"FAIL {b}" for b in bad))
        return 1 if bad else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
