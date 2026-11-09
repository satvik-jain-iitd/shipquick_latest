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
    for field in ("Screen:", "What is missing:", "Tried:", "Picture:", "Platform twin:", "Owner yes:", "component-approved"):
        assert field in t, field


def test_s181_adr_012_names_the_verdict_and_the_copy_policy():
    a = (ROOT / "docs/decisions/ADR-012.md").read_text(encoding="utf-8")
    for word in ("Jetpack Compose Material 3", "SwiftUI", "@astryxdesign/core", "Compose Multiplatform", "MIT",
                 "Copyright (c) Meta Platforms, Inc. and affiliates."):
        assert word in a, word
