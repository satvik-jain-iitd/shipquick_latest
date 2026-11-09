"""Story #242: the offline vendor backup. The plan and the manifest check, on fixtures (no network)."""
import base64
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import vendor_backup as vb  # noqa: E402

TARBALL = b"fake tarball bytes"


def make_backup(tmp_path, *, with_license=True, break_sha=False, drop_lock_entry=False):
    """A tiny backup: one npm package and the pinned Gradle roots, with a matching lockfile."""
    integ = "sha512-" + base64.b64encode(hashlib.sha512(TARBALL).digest()).decode()
    lock = tmp_path / "lock.json"
    lock.write_text(json.dumps({"packages": {"": {}, "node_modules/foo": {"version": "1.0.0", "integrity": integ, "resolved": "https://r/foo.tgz"}}}))
    b = tmp_path / "backup"
    arts = []

    def add(kind, name, version, rel, data):
        (b / rel).parent.mkdir(parents=True, exist_ok=True)
        (b / rel).write_bytes(data)
        lic = f"licenses/{name.replace(':', '_')}/LICENSE"
        if with_license:
            (b / lic).parent.mkdir(parents=True, exist_ok=True)
            (b / lic).write_text("MIT")
        arts.append({"kind": kind, "name": name, "version": version, "file": rel, "url": "https://r/x", "date": "2026-11-09",
                     "sha256": "0" * 64 if break_sha else hashlib.sha256(data).hexdigest(), "license_file": lic})

    if not drop_lock_entry:
        add("npm", "foo", "1.0.0", vb.cache_path(integ), TARBALL)
    for g, a, v in vb.pinned_roots():
        add("maven", f"{g}:{a}", v or "1.0", f"maven/{a}.pom", b"<project/>")
    (b / "MANIFEST.json").write_text(json.dumps({"artifacts": arts}))
    return b, lock


def test_s242_a_complete_backup_passes(tmp_path):
    b, lock = make_backup(tmp_path)
    assert vb.manifest_check(b, lock) == []


def test_s242_no_manifest_fails(tmp_path):
    assert "no MANIFEST.json" in vb.manifest_check(tmp_path, tmp_path / "x")[0]


def test_s242_a_changed_file_fails_the_sha256(tmp_path):
    b, lock = make_backup(tmp_path, break_sha=True)
    assert any("sha256 does not match" in p for p in vb.manifest_check(b, lock))


def test_s242_a_missing_license_file_fails(tmp_path):
    b, lock = make_backup(tmp_path, with_license=False)
    assert any("license file missing" in p for p in vb.manifest_check(b, lock))


def test_s242_a_lockfile_entry_missing_from_the_backup_fails(tmp_path):
    b, lock = make_backup(tmp_path, drop_lock_entry=True)
    assert any("lockfile entry not in the backup: foo@1.0.0" in p for p in vb.manifest_check(b, lock))


def test_s242_a_tarball_that_is_not_the_lockfile_integrity_fails(tmp_path):
    b, lock = make_backup(tmp_path)
    next(p for p in (b / "npm-cache").rglob("*") if p.is_file()).write_bytes(b"swapped")
    assert any("not the lockfile integrity" in p for p in vb.manifest_check(b, lock))


def test_s242_a_missing_pinned_gradle_artifact_fails(tmp_path):
    b, lock = make_backup(tmp_path)
    m = json.loads((b / "MANIFEST.json").read_text())
    m["artifacts"] = [e for e in m["artifacts"] if "material-icons-core" not in e["name"]]
    (b / "MANIFEST.json").write_text(json.dumps(m))
    assert any("pinned Gradle artifact not in the backup: androidx.compose.material:material-icons-core" in p for p in vb.manifest_check(b, lock))


def test_s242_plan_lists_every_lockfile_package_with_its_integrity():
    entries = [e for e in vb.plan() if e["kind"] == "npm"]
    lock = json.loads(vb.LOCK.read_text())["packages"]
    assert len(entries) == len(lock) - 1
    assert all(e["integrity"].startswith("sha512-") for e in entries)


def test_s242_plan_lists_the_gradle_roots_and_the_pins_match_the_research_doc():
    names = [e["name"] for e in vb.plan() if e["kind"] == "maven"]
    assert "androidx.compose:compose-bom" in names and "androidx.compose.material3:material3" in names
    assert vb.drift_problems() == []


def _pom(deps="", pkg="aar"):
    return f'<project xmlns="x"><groupId>g</groupId><artifactId>a</artifactId><version>1</version><packaging>{pkg}</packaging>' \
           f'<licenses><license><name>Apache-2.0</name><url>u</url></license></licenses><dependencies>{deps}</dependencies></project>'.encode()


def test_s242_resolve_walks_poms_and_skips_test_scope_and_ios_variants():
    bom = b"<project><dependencyManagement><dependencies><dependency><groupId>g</groupId><artifactId>a</artifactId><version>1</version></dependency></dependencies></dependencyManagement></project>"
    dep = "<dependency><groupId>g</groupId><artifactId>b</artifactId><version>2</version></dependency>" \
          "<dependency><groupId>g</groupId><artifactId>t</artifactId><version>3</version><scope>test</scope></dependency>"
    mod = json.dumps({"variants": [
        {"attributes": {"org.gradle.usage": "java-api", "org.jetbrains.kotlin.platform.type": "androidJvm"}, "files": [{"url": "a-1.aar"}]},
        {"attributes": {"org.gradle.usage": "kotlin-api", "org.jetbrains.kotlin.platform.type": "native"}, "files": [{"url": "a-1.klib"}]}]}).encode()
    files = {"r/g/bom/1/bom-1.pom": bom, "r/g/a/1/a-1.pom": _pom(dep), "r/g/a/1/a-1.module": mod, "r/g/a/1/a-1.aar": b"A",
             "r/g/b/2/b-2.pom": _pom(pkg="jar"), "r/g/b/2/b-2.jar": b"B"}
    got = vb.resolve_maven(("g", "bom", "1"), [("g", "a", "")], ["r"], lambda u: files.get(u))
    names = sorted(m["file"].rsplit("/", 1)[1] for m in got)
    assert names == ["a-1.aar", "a-1.module", "a-1.pom", "b-2.jar", "b-2.pom", "bom-1.pom"]


def test_s242_build_refuses_off_ci(tmp_path, monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("VENDOR_ALLOW_LOCAL", raising=False)
    try:
        vb.build(tmp_path)
    except SystemExit as e:
        assert "CI only" in str(e)
    else:
        raise AssertionError("build ran off CI")
    assert not (tmp_path / "MANIFEST.json").exists()


def test_s242_an_unchecked_download_is_refused():
    try:
        vb.verified("u", b"x", lambda url: None)
    except SystemExit as e:
        assert "unchecked" in str(e)
    else:
        raise AssertionError("passed with no checksum")


def test_s242_a_pom_with_single_quoted_namespace_is_read():
    xml = b"<?xml version='1.0'?><project xmlns:xsi='i' xmlns='http://maven.apache.org/POM/4.0.0'><dependencyManagement><dependencies>" \
          b"<dependency><groupId>g</groupId><artifactId>a</artifactId><version>1</version></dependency></dependencies></dependencyManagement></project>"
    assert vb.pom_info(xml)["managed"] == [("g", "a", "1")]


def test_s242_a_version_range_in_a_pom_means_its_lower_end():
    dep = "<dependency><groupId>g</groupId><artifactId>b</artifactId><version>[2]</version></dependency>"
    bom = b"<project><dependencyManagement><dependencies><dependency><groupId>g</groupId><artifactId>a</artifactId><version>1</version></dependency></dependencies></dependencyManagement></project>"
    files = {"r/g/bom/1/bom-1.pom": bom, "r/g/a/1/a-1.pom": _pom(dep, pkg="jar"), "r/g/a/1/a-1.jar": b"A",
             "r/g/b/2/b-2.pom": _pom(pkg="jar"), "r/g/b/2/b-2.jar": b"B"}
    got = vb.resolve_maven(("g", "bom", "1"), [("g", "a", "")], ["r"], lambda u: files.get(u))
    assert "b-2.jar" in [m["file"].rsplit("/", 1)[1] for m in got]


def test_s242_a_bom_that_lists_versions_only_in_its_module_file_is_read():
    mod = json.dumps({"variants": [{"dependencyConstraints": [{"group": "g", "module": "a", "version": {"requires": "1"}}]}]}).encode()
    files = {"r/g/bom/1/bom-1.pom": b"<project/>", "r/g/bom/1/bom-1.module": mod,
             "r/g/a/1/a-1.pom": _pom(pkg="jar"), "r/g/a/1/a-1.jar": b"A"}
    got = vb.resolve_maven(("g", "bom", "1"), [("g", "a", "")], ["r"], lambda u: files.get(u))
    assert "a-1.jar" in [m["file"].rsplit("/", 1)[1] for m in got]
