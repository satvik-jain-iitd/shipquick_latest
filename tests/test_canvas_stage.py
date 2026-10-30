# The canvas layout tool: every board once, no overlap, nothing outside its section's board, tiles under 8000, the same input gives the same layout.
import json, os, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import canvas_stage as cs


def board(): return {"x": 0, "y": 0, "w": 390, "h": 844, "title": "x"}


def canvas(names, notes=None):
    return {"v": 3, "boards": {n: board() for n in names}, "order": list(names), "notes": notes or {}, "pages": [], "title": "t"}


TINTS = {"sage": "#bfcfb4", "teal": "#cfd998", "yellow": "#ffde59"}   # fixture values only; a project's own come from its manifest


def manifest(rows, start=True):
    return {"start_here": "read me" if start else None, "tints": TINTS, "ink": "#263528", "remove_notes": ["old-title"], "sections": [
        {"id": "a", "title": "Section 1 · A", "purpose": "p", "prefix": "LIVE", "tint": "sage", "rows": rows[0]},
        {"id": "b", "title": "Section 2 · B", "purpose": "p", "prefix": "DESIGN", "tint": "teal", "rows": rows[1]},
        {"id": "c", "title": "Section 3 · C", "purpose": "p", "prefix": "IN TALK", "tint": "yellow", "rows": rows[2]}]}


class Layout(unittest.TestCase):
    def setUp(self):
        self.c = canvas(["A.dc.html", "B.dc.html", "C.dc.html", "D.dc.html", "E.dc.html", "F.dc.html"], {"n1": {"w": 360, "x": 9, "y": 9, "text": "one"}, "n2": {"w": 360, "x": 9, "y": 9, "text": "two"}, "cs-old": {"w": 360, "x": 0, "y": 0, "text": "mine"}, "old-title": {"w": 360, "x": 0, "y": 0, "text": "named"}, "owner-note": {"w": 360, "x": 5000, "y": 5000, "text": "his"}})
        self.m = manifest([[{"id": "1a", "title": "1a", "boards": ["A.dc.html", "B.dc.html"], "notes": ["n1"]}, {"id": "1b", "title": "1b", "boards": ["C.dc.html"], "notes": []}],
                           [{"id": "2a", "title": "2a", "boards": ["D.dc.html", "E.dc.html"], "notes": ["n2"]}],
                           [{"id": "3a", "title": "3a", "boards": ["F.dc.html"], "notes": []}]])

    def test_S1_every_board_placed_once_prefixed_and_nothing_overlaps(self):
        new, bg, problems = cs.layout(self.c, self.m)
        self.assertEqual(problems, [])
        self.assertEqual(new["boards"]["A.dc.html"]["title"], "LIVE · x")
        self.assertEqual(new["boards"]["D.dc.html"]["title"], "DESIGN · x")
        self.assertLess(new["boards"]["A.dc.html"]["y"], new["boards"]["C.dc.html"]["y"])     # row 1a above row 1b
        self.assertEqual(new["boards"]["B.dc.html"]["x"], 470)
        self.assertEqual(cs.check_existing(new), [])

    def test_S2_a_background_board_per_section_listed_first_and_holding_everything(self):
        new, bg, _ = cs.layout(self.c, self.m)
        bgs = [k for k in new["boards"] if k.startswith("bg/")]
        self.assertEqual(sorted(bgs), ["bg/section-1-1.dc.html", "bg/section-2-1.dc.html", "bg/section-3-1.dc.html", "bg/start.dc.html"])
        self.assertEqual(sorted(new["order"][:4]), sorted(bgs))
        s1 = new["boards"]["bg/section-1-1.dc.html"]
        for k in ["A.dc.html", "B.dc.html", "C.dc.html"]:
            e = new["boards"][k]
            self.assertTrue(cs.inside(cs.box(e["x"], e["y"], e["w"], e["h"], k), cs.box(s1["x"], s1["y"], s1["w"], s1["h"], "s1"), cs.PAD - 1), k)
        n1 = new["notes"]["n1"]
        self.assertTrue(cs.inside(cs.box(n1["x"], n1["y"], 360, 480, "n1"), cs.box(s1["x"], s1["y"], s1["w"], s1["h"], "s1"), cs.PAD - 1))
        self.assertIn("Section 1 · A", bg["project/bg/section-1-1.dc.html"])

    def test_S3_a_board_the_manifest_forgets_lands_in_the_unsorted_row_of_section_3(self):
        self.c["boards"]["G.dc.html"] = board()
        new, bg, problems = cs.layout(self.c, self.m)
        self.assertEqual(problems, [])
        self.assertEqual(new["boards"]["G.dc.html"]["title"], "UNSORTED · x")
        self.assertIn("Unsorted", bg["project/bg/section-3-1.dc.html"])   # the row title is painted on section 3's board

    def test_S4_a_board_in_two_rows_or_missing_is_a_problem_and_nothing_is_written(self):
        self.assertTrue(any("no sections" in p for p in cs.layout(self.c, {"tints": TINTS, "ink": "#263528", "sections": []})[2]))
        self.m["sections"][2]["rows"][0]["boards"].append("A.dc.html")
        self.m["sections"][2]["rows"][0]["boards"].append("Z.dc.html")
        _, _, problems = cs.layout(self.c, self.m)
        self.assertTrue(any("two rows" in p for p in problems) and any("not on the canvas" in p for p in problems))
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "project").mkdir(); (Path(d) / "project" / "canvas.json").write_text(json.dumps(self.c)); mp = Path(d) / "m.json"; mp.write_text(json.dumps(self.m))
            self.assertEqual(cs.main(["--manifest", str(mp), "--canvas", d, "--apply"]), 1)
            self.assertFalse((Path(d) / "project" / "bg").exists())

    def test_S5_a_section_taller_than_8000_splits_into_stacked_tiles(self):
        names = [f"T{i}.dc.html" for i in range(9)]
        c = canvas(names); rows = [[{"id": f"1{chr(97 + i)}", "title": "r", "boards": [names[i]], "notes": []} for i in range(9)], [{"id": "2a", "title": "2a", "boards": [], "notes": []}], [{"id": "3a", "title": "3a", "boards": [], "notes": []}]]
        new, bg, problems = cs.layout(c, manifest(rows))
        self.assertEqual(problems, [])
        tiles = sorted(k for k in new["boards"] if k.startswith("bg/section-1-"))
        self.assertGreaterEqual(len(tiles), 2)
        for t in tiles: self.assertLessEqual(new["boards"][t]["h"], 8000)
        self.assertEqual(new["boards"][tiles[0]]["y"] + new["boards"][tiles[0]]["h"], new["boards"][tiles[1]]["y"])   # stacked, no gap
        second = bg["project/" + tiles[1]]
        self.assertNotIn("<h1", second)   # a continued tile has no band, so its first row title cannot sit on one
        self.assertIn("<h2", second)      # but it carries the row titles of its rows

    def test_S6_the_same_input_gives_the_same_layout_twice(self):
        a, _, _ = cs.layout(self.c, self.m); b, _, _ = cs.layout(a, self.m)
        self.assertEqual({k: (v["x"], v["y"], v["title"]) for k, v in a["boards"].items()}, {k: (v["x"], v["y"], v["title"]) for k, v in b["boards"].items()})

    def test_S8_every_word_on_a_board_is_ink_on_its_fill_at_4_5_to_1_and_titles_live_on_the_board(self):
        for tint in TINTS.values(): self.assertGreaterEqual(cs.contrast("#263528", cs.tile_fill(tint)), 4.5, tint)
        new, bg, problems = cs.layout(self.c, self.m)
        self.assertEqual(problems, [])
        self.assertFalse([k for k, n in new["notes"].items() if n.get("kind") == "title1"])   # no title note: the editor picks its colour, we cannot
        self.assertIn(">1a<", bg["project/bg/section-1-1.dc.html"])
        self.assertIn("color: #263528", bg["project/bg/section-1-1.dc.html"])
        self.assertIn("read me", bg["project/bg/start.dc.html"])   # the start text is painted on its board too, not a sticky
        self.assertNotIn("start-here", new["notes"])

    def test_S9_the_colours_come_from_the_manifest_and_a_missing_or_low_contrast_one_stops_the_run(self):
        m = json.loads(json.dumps(self.m)); m.pop("tints"); m.pop("ink")
        _, _, problems = cs.layout(self.c, m)
        self.assertTrue(any("no tints" in p for p in problems) and any("no ink" in p for p in problems))
        m = json.loads(json.dumps(self.m)); m["ink"] = "#f0f0f0"   # light ink on a light fill
        _, _, problems = cs.layout(self.c, m)
        self.assertTrue(any("under 4.5:1" in p for p in problems))
        self.assertNotIn("#bfcfb4", open(cs.__file__).read())   # no project colour in the tool itself

    def test_S10_the_tool_removes_only_its_own_notes_and_the_ones_the_manifest_names(self):
        new, _, problems = cs.layout(self.c, self.m)
        self.assertEqual(problems, [])
        self.assertNotIn("cs-old", new["notes"]); self.assertNotIn("old-title", new["notes"])
        self.assertIn("owner-note", new["notes"])
        self.assertEqual(new["notes"]["owner-note"]["x"], 5000)   # an unnamed note of the owner keeps its place

    def test_S7_check_existing_finds_an_overlap(self):
        new, _, _ = cs.layout(self.c, self.m)
        new["boards"]["B.dc.html"]["x"] = new["boards"]["A.dc.html"]["x"] + 10
        self.assertTrue(any("overlaps" in p for p in cs.check_existing(new)))

    def test_S11_a_production_board_with_no_provenance_refuses_and_writes_nothing(self):
        self.m["sections"][0]["id"] = "production"   # section "a" becomes Production for this test
        _, _, problems = cs.layout(self.c, self.m)
        self.assertTrue(any("A.dc.html" in p and "no PR and approved date" in p for p in problems), problems)
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "project").mkdir(); (Path(d) / "project" / "canvas.json").write_text(json.dumps(self.c)); mp = Path(d) / "m.json"; mp.write_text(json.dumps(self.m))
            self.assertEqual(cs.main(["--manifest", str(mp), "--canvas", d, "--apply"]), 1)
            self.assertFalse((Path(d) / "project" / "bg").exists())

    def test_S12_a_production_board_with_pr_and_approved_is_fine_a_plain_string_outside_production_still_works(self):
        self.m["sections"][0]["id"] = "production"
        self.m["sections"][0]["rows"][0]["boards"] = [{"board": "A.dc.html", "pr": "#142", "approved": "2026-10-28"}]
        self.m["sections"][0]["rows"][1]["boards"] = [{"board": "C.dc.html", "pr": "#140", "approved": "2026-10-20"}]
        self.m["sections"][1]["rows"][0]["boards"] = ["B.dc.html", "D.dc.html", "E.dc.html"]   # section "b" is not Production: plain strings are fine
        _, _, problems = cs.layout(self.c, self.m)
        self.assertEqual(problems, [])

    def test_S13_a_production_board_entry_missing_only_approved_still_refuses(self):
        self.m["sections"][0]["id"] = "production"
        self.m["sections"][0]["rows"][0]["boards"] = [{"board": "A.dc.html", "pr": "#142"}, "B.dc.html"]
        self.m["sections"][0]["rows"][1]["boards"] = [{"board": "C.dc.html", "pr": "#140", "approved": "2026-10-20"}]
        _, _, problems = cs.layout(self.c, self.m)
        self.assertTrue(any("A.dc.html" in p and "no PR and approved date" in p for p in problems), problems)

    def test_S14_a_non_production_section_never_needs_provenance(self):
        new, _, problems = cs.layout(self.c, self.m)   # sections "b" and "c" in setUp, plain strings throughout
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
