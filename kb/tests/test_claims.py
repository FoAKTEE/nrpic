"""K8: parsing of the tracks' notes, the locator and number check, the claims tables.

Synthetic notes in the five locator styles of wave 1 and a synthetic store; nothing here
reads the real kb-data."""
import json
import os
import sqlite3

import pytest

from kbtool import claims_check as ck
from kbtool import claims_db as cdb
from kbtool import claims_parse as cp

NOTE_A = """# Key references

Labels: [VERIFIED] read at the locator, [JUDGEMENT] our reading, [TO VERIFY] not settled.

## arXiv:2609.14218 v1, Yoo et al., "Simulation" (`MDPBH.tex`)

- Set-up [VERIFIED]: BSSN with a background scale factor (L3-4); data on a constant-mean-
  curvature slice (L5). Resolution 80 points (L6). Particle number not stated; one per cell
  is implied by L7 [JUDGEMENT: 80^3 = 5.1e5 in the octant].
- Results [VERIFIED]: threshold around mu ~ 0.045 (L1101-
  1103), an order of magnitude below the analytic estimate (abstract L2).
- Boundary conditions not stated (L8) [TO VERIFY: reflective octant symmetry assumed].
"""

NOTE_B = """# Key references of B

Every statement below was read at the locator.

### 2403.15126 (`main.tex`)
- Abstract: lines 12-13. Turnaround time: 40-60.
- N up to 1e4 equal-mass particles (66-67); quadrupole formula (75); criterion (1).
"""

NOTE_D = """## 1. Spikes

### arXiv:1305.2619 v1, Sadeghian et al., "Dark matter" (`SFWpaper.tex`)
- [VERIFIED] The density vanishes at r = 4Gm: `:3`, `:5-6`; reason: capture (`:7`).
"""

NOTE_C_ROW = """## 6. Key references verified at the source

| Statement | Locator |
|---|---|
| eps_max = 0.0352 at Z(0) = 0.548 | 2108.11967 `main.tex:4` |
| Seed fraction 1e-8 to 1e-6 (helper) | astro-ph/0111176 `:2-3` |
"""

NOTE_S2 = """# Corrections

**Labels.** [VERIFIED] read; [BACKGROUND] standard; [JUDGEMENT] mine; [TO VERIFY] open.

| Test | Brief | Verdict | Source |
|---|---|---|---|
| OS | error 1e-3 | correct [VERIFIED] | "Delta M <~ 10^-3" (L5); within 10^-3 (L6) |
| merger | t ~ 64.16 M | inconsistent | L7: t_m = 64.15625 M; L8: roughly 64.175 M |
| pages | 37 pages | not in the source [TO VERIFY by kb] | brief lines 99-106 |
"""

NOTE_F = """## Closest papers

- **arXiv:2406.11985** (Ficarra 2024). The closest work (`TBH3.tex` lines 3-5); a prompt
  disruption closer than 30 M (lines 7-8).
"""


def spec(track, **kw):
    return cp.SourceSpec(track, "ref", f"tracks/{track}/note.md", **kw)


def test_units_and_labels_style_a():
    cl = cp.parse_note(NOTE_A, spec("A"), "ref")
    texts = [c.text for c in cl]
    assert not any("Labels" in t for t in texts), "the legend of the labels is not a claim"
    first = cl[0]
    assert first.paper_id == "2609.14218" and first.label == "VERIFIED"
    assert [(l.file, l.line_start, l.line_end, l.version) for l in first.locators] == [("MDPBH.tex", 3, 4, "v1")]
    # the inline judgement after L7 is a claim of its own
    j = [c for c in cl if c.label == "JUDGEMENT"]
    assert len(j) == 1 and "5.1e5" in j[0].text
    # a line break inside a range is joined
    r = [c for c in cl if "0.045" in c.text][0]
    assert (r.locators[0].line_start, r.locators[0].line_end) == (1101, 1103)
    tv = [c for c in cl if c.label == "TO VERIFY"]
    assert len(tv) == 1 and tv[0].locators[0].line_start == 8


def test_bare_numbers_style_b():
    cl = cp.parse_note(NOTE_B, spec("B", default_label="VERIFIED", bare_numbers=True), "ref")
    locs = [(l.file, l.line_start, l.line_end) for c in cl for l in c.locators]
    assert ("main.tex", 12, 13) in locs and ("main.tex", 40, 60) in locs and ("main.tex", 66, 67) in locs
    assert ("main.tex", 75, 75) in locs and ("main.tex", 1, 1) not in locs, "(1) is an item number"
    assert all(c.label == "VERIFIED-implicit" for c in cl)


def test_colon_style_d_and_table_rows_c():
    cl = cp.parse_note(NOTE_D, spec("D"), "ref")
    assert [(l.file, l.line_start, l.line_end) for l in cl[0].locators] == [
        ("SFWpaper.tex", 3, 3), ("SFWpaper.tex", 5, 6)]
    cl = cp.parse_note(NOTE_C_ROW, spec("C", default_label="VERIFIED"), "ref")
    assert len(cl) == 2
    assert (cl[0].paper_id, cl[0].locators[0].file, cl[0].locators[0].line_start) == ("2108.11967", "main.tex", 4)
    assert cl[1].locators[0].paper_id == "astro-ph/0111176"


def test_fixed_paper_prefix_locators_and_brief_lines():
    cl = cp.parse_note(NOTE_S2, spec("core", default_label="VERIFIED", lines_word=False,
                                     fixed_paper=("2611.12831", "v1", "main.tex")), "ref")
    by_line = {c.locators[0].line_start: c for c in cl if c.locators}
    assert set(by_line) == {5, 6, 7, 8}
    assert "64.15625" in by_line[7].text and "64.175" not in by_line[7].text      # prefix style L7: ...
    assert "64.175" in by_line[8].text
    tv = [c for c in cl if c.label == "TO VERIFY"]
    assert tv and not tv[0].locators, "brief lines are not paper locators"


def test_lines_word_inherits_file_style_f():
    cl = cp.parse_note(NOTE_F, spec("F", default_label="VERIFIED"), "ref")
    locs = [(l.paper_id, l.file, l.line_start, l.line_end) for c in cl for l in c.locators]
    assert locs == [("2406.11985", "TBH3.tex", 3, 5), ("2406.11985", "TBH3.tex", 7, 8)]


def test_repository_files_are_not_paper_locators():
    md = "## arXiv:2611.12831 v1 (`main.tex`)\n- [VERIFIED] the filter (L5); code (`nrpic.cpp` lines 3-9), " \
         "`paper/sections/method.tex` line 151.\n"
    cl = cp.parse_note(md, spec("x"), "ref")
    locs = [(l.file, l.line_start) for c in cl for l in c.locators]
    assert locs == [("main.tex", 5)]


def test_seed_key_stable_and_distinct():
    a = cp.parse_note(NOTE_A, spec("A"), "ref")
    b = cp.parse_note(NOTE_A, spec("A"), "other-ref")
    assert [x.seed_key() for x in a] == [x.seed_key() for x in b]
    assert len({x.seed_key() for x in a}) == len(a)


# ---------------------------------------------------------------- numbers
@pytest.mark.parametrize("claim, tex, want", [
    ("error 1e-3", r"$\Delta M/M \lesssim 10^{-3}$", "exact"),
    ("N = 998,592 particles", r"$N_p = 998{,}592$", "exact"),
    ("N = 2 x 10^6", r"$N_p = 2\times 10^6$", "exact"),
    ("mass 0.383 M", r"$M_{\rm AH}=0.38326\,M$", "rounded"),
    ("t = 64.16 M", r"t_m = 64.15625", "rounded"),
    ("C = 1.41053e-2.", r"1.41053\times10^{-2}", "exact"),
    ("y_c = 0.900", r"y_c = 0.9", "exact"),
    ("mu ~ 0.045", r"$\mu\sim0.05$", ""),
])
def test_number_matching(claim, tex, want):
    nums = ck.claim_numbers(claim)
    assert nums, claim
    got = ck.number_found(nums[-1], ck.tex_numbers(tex), tex)
    assert got == want, (claim, nums[-1], got)


def test_claim_numbers_ignore_ids_locators_runs_and_remarks():
    t = ("Threshold 0.045 (L1101-1103), arXiv:2609.14218v1, run A-emd-pbh-20261115-112625-e854f12, "
         "[JUDGEMENT: 80^3 = 5.1e5], 2024, 3D, A1, brief line 130, `MDPBH.tex:12`")
    assert [n.text for n in ck.claim_numbers(t)] == ["0.045"]


# ---------------------------------------------------------------- store and database
@pytest.fixture
def store(tmp_path):
    raw = tmp_path / "raw" / "arxiv"
    src = raw / "2609.14218" / "v1" / "src"
    src.mkdir(parents=True)
    lines = ["\\documentclass{article}", "abstract one order below", "BSSN with scale factor",
             "decomposition", "constant mean curvature", "80 grid points", "one particle per cell",
             "boundaries", ""]
    lines += [f"filler {i}" for i in range(9, 1100)]
    lines += ["threshold around $\\mu\\sim 0.045$", "for e=0.2", "no horizon", "end"]
    (src / "MDPBH.tex").write_text("\n".join(lines) + "\n")
    (src / "sub").mkdir()
    (src / "sub" / "app.tex").write_text("a\nb\n")
    build = tmp_path / "build" / "tex" / "2609.14218"
    build.mkdir(parents=True)
    # flat.tex = lines 2..8 of MDPBH.tex, one entry per line
    off, smap = 0, []
    for i in range(2, 9):
        smap.append([off, "MDPBH.tex", i, 0])
        off += len(lines[i - 1]) + 1
    (build / "sourcemap.json").write_text(json.dumps(smap))
    (build / "flat.tex").write_text("x" * off)
    con = sqlite3.connect(":memory:")
    con.executescript(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")).read())
    con.execute("INSERT INTO papers(paper_id, title, version, main_tex) VALUES ('2609.14218','T','v1','MDPBH.tex')")
    con.execute("INSERT INTO chunks(paper_id, kind, text, char_start, char_end) VALUES ('2609.14218','body','t',0,40)")
    con.execute("INSERT INTO chunks(paper_id, kind, text, char_start, char_end) VALUES ('2609.14218','comment','c',0,40)")
    con.commit()
    return ck.Store(str(raw), str(tmp_path / "build" / "tex"), con), con


def test_check_located_partial_unresolved(store):
    st, con = store
    cl = cp.parse_note(NOTE_A, spec("A"), "ref")
    res = {c.text[:20]: ck.check_claim(c.text, c.locators, st) for c in cl}
    status = {k: v[0] for k, v in res.items()}
    first = [v for k, v in res.items() if k.startswith("Set-up")][0]
    assert first[0] == "located"
    lr = first[2][0]
    assert lr.file == "MDPBH.tex" and lr.flat_start == 25 and lr.chunk_ids == [1], "comment chunks are excluded"
    thr = [v for k, v in res.items() if "0.045" in k or k.startswith("Results")][0]
    assert thr[0] == "located" and thr[1]["found"] == ["0.045"]
    loc = cp.Locator("2609.14218", "v1", "MDPBH.tex", 5000, 5001, "L5000", 0)
    s, d, _ = ck.check_claim("x (L5000)", [loc], st)
    assert s == "unresolved" and "beyond end of file" in d["unresolved"][0]
    loc = cp.Locator("9999.99999", "", "a.tex", 1, 1, "", 0)
    assert ck.check_claim("x", [loc], st)[0] == "unresolved"
    loc = cp.Locator("2609.14218", "", "app.tex", 1, 2, "", 0)          # found by base name in sub/
    s, d, r = ck.check_claim("x", [loc], st)
    assert s == "located" and r[0].file == "sub/app.tex"
    loc = cp.Locator("2609.14218", "v3", "MDPBH.tex", 3, 3, "", 0)       # version the store lacks
    s, d, r = ck.check_claim("x 0.777", [loc], st)
    assert s == "partial" and d["missing"] == ["0.777"] and any("store has v1" in n for n in d["notes"])
    assert status


def test_db_seed_verify_refute_and_judgement_rule(store, tmp_path):
    st, _ = store
    db = tmp_path / "kb.sqlite"
    con = cdb.connect(str(db))
    con.executescript(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")).read())
    cdb.ensure(con)
    cl = cp.parse_note(NOTE_A, spec("A"), "ref")
    ids = {}
    for c in cl:
        cid, what = cdb.upsert_seed(con, c, "abc1234def", ck.check_claim(c.text, c.locators, st), "test", "tool")
        ids[c.text[:12]] = (cid, c.label)
        assert what == "new"
    con.commit()
    labels = dict(con.execute("SELECT label, count(*) FROM claims GROUP BY 1").fetchall())
    assert labels.get("fulltext", 0) >= 3 and labels.get("judgement") == 1 and labels.get("to_verify") == 2
    # re-seeding is idempotent
    for c in cl:
        assert cdb.upsert_seed(con, c, "abc1234def", ck.check_claim(c.text, c.locators, st), "test", "tool")[1] == "same"
    assert con.execute("SELECT count(*) FROM claims").fetchone()[0] == len(cl)
    jid = [cid for cid, lab in ids.values() if lab == "JUDGEMENT"][0]
    with pytest.raises(ValueError):
        cdb.verify(con, jid, "someone", "read it")
    tid = [cid for cid, lab in ids.values() if lab == "TO VERIFY"][0]
    cdb.verify(con, tid, "kb-helper", "read MDPBH.tex:8", locator="2609.14218v1:MDPBH.tex:L8")
    assert con.execute("SELECT label FROM claims WHERE claim_id=?", (tid,)).fetchone()[0] == "fulltext"
    # a person's label survives an automatic re-check
    for c in cl:
        cdb.upsert_seed(con, c, "abc1234def", ("unresolved", {}, []), "test", "tool")
    assert con.execute("SELECT label FROM claims WHERE claim_id=?", (tid,)).fetchone()[0] == "fulltext"
    first = min(cid for cid, _ in ids.values())
    assert cdb.refute(con, first, "kb-helper", "counter-example") == ["A"]
    assert con.execute("SELECT label FROM claims WHERE claim_id=?", (first,)).fetchone()[0] == "refuted"
    ev = [r[0] for r in con.execute("SELECT action FROM claim_events WHERE claim_id=? ORDER BY event_id", (first,))]
    assert ev[0] == "seed" and ev[-1] == "refute"
    # a claim that left its note becomes stale, never deleted
    n = cdb.mark_stale(con, "tracks/A/note.md", {cl[0].seed_key()}, "test")
    assert n == len(cl) - 1
    assert con.execute("SELECT count(*) FROM claims").fetchone()[0] == len(cl)
    cid = cdb.add_claim(con, "hand", "result", "2609.14218", None, "to_verify", "me", "o", "A")
    with pytest.raises(ValueError):
        cdb.add_claim(con, "hand", "result", "2609.14218", None, "fulltext", "me", "o", "A")
    assert cid > 0


def test_label_mapping():
    assert cdb.label_for("VERIFIED", "located") == "fulltext"
    assert cdb.label_for("VERIFIED-implicit", "partial") == "to_verify"
    assert cdb.label_for("JUDGEMENT", "located") == "judgement"
    assert cdb.label_for("BACKGROUND", "unlocated") == "background"
    assert cdb.label_for("UNLABELLED", "located") == "to_verify"
