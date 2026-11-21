"""kbtool.claims_brief: the brief's labelled statements as seeds (brief 12.8), the CHECK.md
join of the brief check, defect claims. A synthetic brief and CHECK.md written here; no test
reads the real brief or touches the real kb-data."""
import json
import os

import pytest

from kbtool import claims_brief as cb
from kbtool import claims_check as ck
from kbtool import claims_db as cdb

BRIEF = """# Title

## 0. How to use this document

| Label | Meaning |
|---|---|
| [VERIFIED] | read from an abstract |

## 1. Bottom line first

- **Recommendation.** Do the thing first, because it is cheap. [JUDGEMENT]

## 2. Starting point

**Bibliographic data [VERIFIED].** The paper arXiv:2611.12831 has 37 pages. More text here.

### 2.2 State of the public code [VERIFIED]

The coupling is absent (arXiv:2611.12831) [VERIFIED]. Whether the text discusses it is [TO VERIFY].

## 3. Landscape

### 3.1 The ladder of methods

| Route | Code |
|---|---|
| Weak field | gevolution (arXiv:1604.06065) |
| Constrained | GRAMSES (arXiv:1905.08890) [BACKGROUND; defer to the original] |

The characterizations in this table are [BACKGROUND]; defer to the originals.

### 3.3 Late universe

Simulations give a backreaction of about 1e-8 (arXiv:1807.01711) [VERIFIED]. Averaged on other slices it is small, e.g. in sub-volumes (arXiv:2408.03049) [VERIFIED].

Ray tracing [all VERIFIED]:

- one code (arXiv:2603.24838);
- another code (arXiv:2606.05479).

### 3.11 Hills mechanism (background for Track F)

- **Classic picture [BACKGROUND].** Hills (1988) predicted ejection (arXiv:0911.1136).
- **Related work [titles VERIFIED].** Three-body runs (arXiv:2406.11985), Kozai (arXiv:1703.10543).

## 5. Ranking

### S1 Primordial black holes

The threshold drops [JUDGEMENT + TO VERIFY] under pressure.

```
[VERIFIED] inside a code block is not a label
```

## 11. Harness

- The worktree command is documented [VERIFIED].

## 15. Items for the agents to verify or complete

1. **Full text.** Read it.
2. **Bias.** Background claim (arXiv:1707.03595) [BACKGROUND].

## 16. References

- [VERIFIED] nothing here counts
"""


@pytest.fixture
def brief(tmp_path):
    p = tmp_path / "brief.md"
    p.write_text(BRIEF, encoding="utf-8")
    return str(p)


def _db(tmp_path):
    con = cdb.connect(str(tmp_path / "kb.sqlite"))
    con.executescript(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")).read())
    cdb.ensure(con)
    return con


def test_label_families():
    assert cb.label_of("VERIFIED")[1] == "abstract"
    assert cb.label_of("VERIFIED: abstracts or search snippets")[1] == "abstract"
    assert cb.label_of("titles VERIFIED")[1] == "title_only"
    assert cb.label_of("title only verified")[1] == "title_only"
    assert cb.label_of("BACKGROUND; titles VERIFIED")[1] == "background"
    assert cb.label_of("JUDGEMENT + TO VERIFY")[1] == "judgement"
    assert cb.label_of("TO VERIFY; novelty search before starting")[1] == "to_verify"
    assert cb.label_of("all VERIFIED")[1] == "abstract"
    assert cb.label_of("see section 4") is None


def test_extract_main_text_only_and_counts(brief):
    st, info = cb.extract(brief)
    secs = {s.section for s in st}
    assert secs <= cb.MAIN_SECTIONS and 0 not in secs and 11 not in secs and 16 not in secs
    # sections 0, 11 and 16 still counted in the record of all labels
    assert info["labels_by_section"][0] == 1 and info["labels_by_section"][11] == 1
    assert info["labels_by_section"][16] == 1
    labels = [(s.line, s.ordinal, s.label) for s in st]
    assert len(st) == 15, labels
    # the code block holds no label
    assert all("inside a code block" not in s.text for s in st)


def test_statement_boundaries(brief):
    st = {(s.line, s.ordinal): s for s in cb.extract(brief)[0]}
    lines = BRIEF.split("\n")

    def at(fragment):
        return next(i for i, l in enumerate(lines, 1) if fragment in l)
    rec = st[(at("Recommendation"), 1)]
    assert rec.label == "judgement" and rec.rule == "after-stop" and "cheap" in rec.text
    assert rec.text.startswith("Recommendation.")          # after the stop: the whole block
    bib = st[(at("Bibliographic data"), 1)]
    assert bib.rule == "lead-in" and "37 pages" in bib.text and bib.ids == ["2611.12831"]
    head = st[(at("2.2 State"), 1)]
    assert head.rule == "heading" and head.label == "abstract" and head.tracks == []
    two = at("The coupling is absent")
    a, b = st[(two, 1)], st[(two, 2)]
    assert a.text.startswith("The coupling is absent") and "Whether" not in a.text
    assert b.label == "to_verify" and b.text.startswith("Whether")
    sims = at("Simulations give")
    s1, s2 = st[(sims, 1)], st[(sims, 2)]
    assert s1.ids == ["1807.01711"] and "Averaged" not in s1.text       # "e.g." is no sentence end
    assert s2.ids == ["2408.03049"] and s2.text.startswith("Averaged") and "sub-volumes" in s2.text
    tab = st[(at("GRAMSES"), 1)]
    assert tab.rule == "row" and tab.label == "background" and tab.ids == ["1905.08890"]
    this = st[(at("in this table"), 1)]
    assert this.rule == "sentence+table" and this.line_start == at("| Route")
    ray = st[(at("Ray tracing"), 1)]
    assert ray.rule == "colon+list" and ray.line_end == at("another code") and ray.ids == ["2603.24838", "2606.05479"]
    kp = st[(at("Related work"), 1)]
    assert kp.label == "title_only" and kp.ids == ["2406.11985", "1703.10543"]
    mix = st[(at("threshold drops"), 1)]
    assert mix.label == "judgement" and mix.bracket == "JUDGEMENT + TO VERIFY"
    item1 = st[(at("**Full text.**"), 1)]
    assert item1.label == "to_verify" and item1.bracket == cb.IMPLICIT_BRACKET
    item2 = st[(at("**Bias.**"), 1)]
    assert item2.label == "background" and item2.ids == ["1707.03595"]


def test_tracks_from_section_and_from_cited_ids(brief):
    st, _ = cb.extract(brief)
    usage = {"1807.01711": {"B-emd-gw"}}
    cb.assign_tracks(st, usage, {"2408.03049": {"A-emd-pbh"}})
    by_text = {s.text[:12]: s for s in st}
    assert by_text["Bibliographic"[:12]].tracks == ["core"]          # section 2
    assert by_text["Classic pict"].tracks == ["F-hills"]              # 3.11 names Track F
    assert by_text["The threshol"].tracks == ["A-emd-pbh"]           # S1
    assert by_text["Simulations "].tracks == ["B-emd-gw"]            # from the claims of the tracks
    assert by_text["Averaged on "].tracks == ["A-emd-pbh"]           # from a track sheet


def test_seed_idempotent_and_protected_from_rebuild(brief, tmp_path):
    st, info = cb.extract(brief)
    cb.assign_tracks(st, {}, {})
    con = _db(tmp_path)
    got = [cb.upsert(con, s, info["brief_sha256"], "test")[1] for s in st]
    con.commit()
    assert got == ["new"] * len(st)
    again = [cb.upsert(con, s, info["brief_sha256"], "test")[1] for s in st]
    assert again == ["same"] * len(st)
    assert con.execute("SELECT count(*) FROM claims").fetchone()[0] == len(st)
    r = con.execute("SELECT c.origin, c.label, m.seed_key, m.status, m.label_set_by FROM claims c JOIN claim_meta m "
                    "USING(claim_id) ORDER BY claim_id").fetchone()
    assert r[0].startswith("brief v2 L") and r[2].startswith("brief:v2:L") and r[3] == "unlocated"
    assert r[4] != "auto"                     # `kb claim seed --rebuild` refuses (rebuild_refused)
    from kbtool import claims_cli

    class L:
        db_current = str(tmp_path / "no-snapshot")
    assert "label set by a person" in claims_cli.rebuild_refused(L, con)
    # a judgement seed cannot be verified; a refuted one stays refuted
    jid = con.execute("SELECT claim_id FROM claims WHERE label='judgement' LIMIT 1").fetchone()[0]
    with pytest.raises(ValueError):
        cdb.verify(con, jid, "x", "y", "2611.12831v1:main.tex:L1")


def test_annotate_only_own_claims(brief, tmp_path):
    st, info = cb.extract(brief)
    con = _db(tmp_path)
    cid, _ = cb.upsert(con, st[0], info["brief_sha256"], "test")
    other = cdb.add_claim(con, "hand", "result", None, None, "to_verify", "me", "o", "A")
    assert cb.annotate(con, cid, "t", "CHECK s33 row 1: CONFIRMED") is True
    assert cb.annotate(con, cid, "t", "CHECK s33 row 1: CONFIRMED") is False        # idempotent
    with pytest.raises(ValueError):
        cb.annotate(con, other, "t", "not mine")
    ev = con.execute("SELECT action FROM claim_events WHERE claim_id=? ORDER BY event_id", (cid,)).fetchall()
    assert [e[0] for e in ev] == ["seed", "annotate"]


CHECK = """# Check

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | {sims} | "Simulations give a backreaction of about 1e-8" | [VERIFIED] | CORRECTED | `1807.01711/v2/src/INCA.tex:106, 524-525` | body says 1e-9 |
| 2 | {sims} | "it is small, e.g. in sub-volumes" | (unl.) | CONFIRMED (precision) | `2408.03049/v1/src/main.tex:12`; `meta:inspire/2408.03049` | ok |
| 3 | {gev} | "gevolution" | [BACKGROUND] | CONFIRMED | `1604.06065/v2/src/c.tex:152` | a | b |
| 4 | 9999 | "nothing" | (unl.) | CONFIRMED | `gr-qc_9804040/v1/src/rrs98.tex:53` | x |

| Q | Brief line | Question | Status | Locator | Open |
|---|---|---|---|---|---|
| Q1 | 5 | other table | OPEN | - | - |
"""


def test_parse_check_and_join(brief):
    lines = BRIEF.split("\n")
    sims = next(i for i, l in enumerate(lines, 1) if "Simulations give" in l)
    gev = next(i for i, l in enumerate(lines, 1) if "| Weak field" in l)
    md = CHECK.format(sims=sims, gev=gev).replace("| a | b |", "| a `x|y` b |")
    rows, problems = cb.parse_check(md, "pkg")
    assert [r.n for r in rows] == [1, 2, 3, 4] and not problems
    assert rows[0].verdict == "CORRECTED" and rows[1].verdict == "PRECISION" and rows[2].verdict == "CONFIRMED"
    assert rows[0].label == "abstract" and rows[1].label == "" and rows[2].label == "background"
    assert rows[0].tex_locators() == [("1807.01711", "v2", "INCA.tex", 106, 106), ("1807.01711", "v2", "INCA.tex", 524, 525)]
    assert rows[3].tex_locators()[0][0] == "gr-qc/9804040"
    st, _ = cb.extract(brief)
    j = cb.join_rows(rows, st)
    s1 = j[0][1]
    assert s1 is not None and s1.ids == ["1807.01711"]
    assert j[1][1] is not None and j[1][1].ids == ["2408.03049"]          # unlabelled, inside the statement
    assert j[2][1] is not None and j[2][1].rule == "sentence+table"       # a table row: the table's label
    assert j[3][1] is None and j[3][2] == "no seed on the line"


def test_defect_claims_refuted_superseded_and_recheck(tmp_path):
    raw = tmp_path / "raw" / "arxiv"
    src = raw / "2609.14218" / "v1" / "src"
    src.mkdir(parents=True)
    (src / "MDPBH.tex").write_text("\n".join(f"line {i}" for i in range(1, 20)) + "\n")
    raw = str(raw)
    con = _db(tmp_path)
    d = cb.Defect(key="t1", row="BRIEF_ERRATA 5.x", paper_id="2609.14218",
                  printed="As printed: the abstract says ten.", printed_loc="2609.14218v1:MDPBH.tex:L8",
                  evidence="run kb-20261119-000000-abcdef0", right="The body says nine.",
                  right_loc="kb-data/raw/arxiv/2609.14218/v1/src/MDPBH.tex:L8", right_label="fulltext")
    store_ = ck.Store(raw, os.path.join(str(tmp_path), "build", "tex"), con)
    res = cb.add_defect(con, d, store_, "t")
    p, r = res["printed"][0], res["right"][0]
    assert con.execute("SELECT label FROM claims WHERE claim_id=?", (p,)).fetchone()[0] == "refuted"
    assert con.execute("SELECT supersedes, label FROM claims WHERE claim_id=?", (r,)).fetchone() == (p, "fulltext")
    # the paper is not in the papers table: its locators stay unresolved
    assert con.execute("SELECT status FROM claim_meta WHERE claim_id=?", (r,)).fetchone()[0] == "unresolved"
    assert cb.add_defect(con, d, store_, "t")["printed"][1] == "same"                      # idempotent
    con.execute("INSERT INTO papers(paper_id, title, version, main_tex) VALUES ('2609.14218', 't', 'v1', 'MDPBH.tex')")
    out = cb.recheck_defects(con, store_, "t")
    assert any(x[0] == r and x[2] == "checked" and x[3] for x in out)
    det = json.loads(con.execute("SELECT status_detail FROM claim_meta WHERE claim_id=?", (r,)).fetchone()[0])
    assert det["row"] == "BRIEF_ERRATA 5.x"
    tex, other = cb.parse_any_locator("kb-data/raw/arxiv/gr-qc_0601112/v1/src/ssevnum7.tex:L694; meta:inspire/x")
    assert tex[0][:5] == ("gr-qc/0601112", "v1", "ssevnum7.tex", 694, 694) and other == ["meta:inspire/x"]


def test_cli_dry_run_and_seed(brief, tmp_path, monkeypatch):
    from kbtool import claims_cli
    data = tmp_path / "kb-data"
    (data / "db").mkdir(parents=True)
    monkeypatch.setenv("KB_LOCK", str(tmp_path / "kb-writer.lock"))
    con = _db(data / "db")
    con.close()
    out = tmp_path / "seeds.tsv"
    assert claims_cli.main(["--data-root", str(data), "claim", "seed-brief", "--brief", brief, "--dry-run",
                            "--tsv", str(out)]) == 0
    assert len(out.read_text().strip().split("\n")) == 1 + 15
    con = cdb.connect(str(data / "db" / "kb.sqlite"))
    assert con.execute("SELECT count(*) FROM claims").fetchone()[0] == 0             # dry run wrote nothing
    con.close()
    for _ in range(2):
        assert claims_cli.main(["--data-root", str(data), "claim", "seed-brief", "--brief", brief]) == 0
    con = cdb.connect(str(data / "db" / "kb.sqlite"))
    assert con.execute("SELECT count(*) FROM claims").fetchone()[0] == 15            # second run added nothing
    con.close()
