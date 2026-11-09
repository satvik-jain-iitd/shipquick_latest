"""Story #181: rule 38 "Library first" exists and points at its full rule, its ADR and its request template."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")


def rule(n):
    m = re.search(rf"^{n}\. (.+)$", CLAUDE, re.M)
    assert m, f"CLAUDE.md has no rule {n}"
    return m.group(1)


def test_s181_rule_38_is_library_first_and_links_its_docs():
    r = rule(38)
    assert "Library first" in r
    for link in ("docs/COMPONENT_LIBRARY.md", "docs/decisions/ADR-012.md", "docs/templates/component-request.md"):
        assert link in r, link
        assert (ROOT / link).is_file(), link


def test_s181_rule_numbers_37_and_38_stay_in_order():
    nums = [int(n) for n in re.findall(r"^(\d+)\. ", CLAUDE, re.M)]
    assert nums == sorted(nums) and len(nums) == len(set(nums))
    assert nums[-2:] == [37, 38]


def test_s181_request_template_has_every_field():
    t = (ROOT / "docs/templates/component-request.md").read_text(encoding="utf-8")
    for field in ("Screen:", "What is missing:", "Tried:", "Picture:", "Platform twin:", "component-approved"):
        assert field in t, field


def test_s181_template_has_no_owner_yes_field_for_the_coder():
    """The coder writes the issue body, so an Owner yes there proves nothing (S8, #186 reads a reviewer comment)."""
    t = (ROOT / "docs/templates/component-request.md").read_text(encoding="utf-8")
    assert not re.search(r"^\s*Owner yes:", t, re.M), "Owner yes must not be a body field"
    assert "issue comment" in t and "reviewer account" in t


DOCS = {p: (ROOT / p).read_text(encoding="utf-8") for p in ("CLAUDE.md", "docs/COMPONENT_LIBRARY.md", "docs/decisions/ADR-012.md")}


def test_s181_compose_multiplatform_appears_only_as_dropped():
    for path, text in DOCS.items():
        for line in text.splitlines():
            if "Compose Multiplatform" in line and not line.lstrip().startswith("| (b)") and "| (b)" not in line:
                assert re.search(r"not used|dropped|Nothing", line), f"{path}: {line}"


def test_s181_third_party_kit_ban_is_native_only():
    for path in ("CLAUDE.md", "docs/COMPONENT_LIBRARY.md"):
        for line in DOCS[path].splitlines():
            if "third-party" in line:
                assert re.search(r"native|Android or iOS", line), f"{path}: ban must name native only: {line}"


def test_s181_rule_says_the_reviewer_checks_by_hand_until_the_tools_land():
    assert "until S3 to S7 land, the reviewer checks by hand" in rule(38)
    assert re.search(r"until S3 to S7 land, the reviewer checks by hand", DOCS["docs/COMPONENT_LIBRARY.md"], re.I)


def test_s181_owner_yes_counts_only_from_a_reviewer_comment():
    for path in ("CLAUDE.md", "docs/COMPONENT_LIBRARY.md"):
        assert "reviewer account" in DOCS[path], path


def test_s181_library_doc_has_the_web_row_and_never_twice():
    lib = DOCS["docs/COMPONENT_LIBRARY.md"]
    assert re.search(r"^\| Web \|.*@astryxdesign/core.*pinned.*astryx doctor --built", lib, re.M)
    assert "an approved component joins the library and is never built twice" in lib.lower()


def test_s181_trace_row_is_last_and_names_the_pr():
    rows = [l for l in (ROOT / "docs/process-trace.md").read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    assert "Story #181" in rows[-1] and "PR #195" in rows[-1]


def test_s181_adr_012_names_the_verdict_and_the_copy_policy():
    a = (ROOT / "docs/decisions/ADR-012.md").read_text(encoding="utf-8")
    for word in ("Jetpack Compose Material 3", "SwiftUI", "@astryxdesign/core", "Compose Multiplatform", "MIT",
                 "Copyright (c) Meta Platforms, Inc. and affiliates."):
        assert word in a, word
