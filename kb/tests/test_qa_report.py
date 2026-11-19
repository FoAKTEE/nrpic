"""K9: the quality report on a synthetic database and store (no real kb-data)."""
import json
import os
import sqlite3

from kbtool import paths, qa_golden, qa_report

SCHEMA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")
MIGR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript(open(SCHEMA).read())
    for n in sorted(os.listdir(MIGR)):
        if n.endswith(".sql") and n[:4] in ("0002", "0003"):
            con.executescript(open(os.path.join(MIGR, n)).read())
    return con


def test_report_on_synthetic_store(tmp_path, monkeypatch):
    data = tmp_path / "kb-data"
    raw = data / "raw" / "arxiv" / "2611.12831" / "v1" / "src"
    raw.mkdir(parents=True)
    (raw / "main.tex").write_text("\\documentclass{revtex4-2}\\begin{document}\n\\begin{equation}a\\end{equation}\n"
                                  "\\begin{align}b\\\\c\\end{align}\\end{document}\n")
    (data / "db").mkdir(parents=True)
    (data / "meta" / "arxiv").mkdir(parents=True)
    con = make_db(str(data / "db" / "kb.sqlite"))
    con.execute("INSERT INTO papers(paper_id, title, abstract, version, main_tex, source_kind, parse_status, "
                "parse_score, parse_json, sha256, flat_sha256) VALUES ('2611.12831','A title of twenty chars or more',"
                "'abs','v1','main.tex','tex','ok',0.9,'{}','s1','f1')")
    con.execute("INSERT INTO papers(paper_id, title, abstract, version, main_tex, source_kind, parse_status, "
                "parse_score, parse_json, sha256, flat_sha256) VALUES ('2009.08715','',NULL,'v1','HDR.tex','tex',"
                "'review',0.7,?, 's2','f2')",
                (json.dumps({"quality": {"components": {"title": 0.0, "abstract": 0.0, "sections": 1.0},
                                         "body_words": 73298}, "class": "article"}),))
    con.execute("INSERT INTO sections(paper_id, level, number, title) VALUES ('2611.12831', 1, '1', 'Intro')")
    for i in range(3):
        con.execute("INSERT INTO equations(paper_id, env, number, tex_raw) VALUES ('2611.12831','align',?, 'x')",
                    (str(i + 1),))
    con.execute("INSERT INTO bib_entries(paper_id, cite_key, target_arxiv, source) VALUES ('2611.12831','k1','2111.05282','bbl')")
    con.execute("INSERT INTO bib_entries(paper_id, cite_key, source) VALUES ('2611.12831','k2','bbl')")
    con.execute("INSERT INTO citations(citing, cited_arxiv, in_corpus) VALUES ('2611.12831','2111.05282',0)")
    con.execute("INSERT INTO downloads(paper_id, in_manifest, status, versions_present_json, checked_at) "
                "VALUES ('2611.12831',1,'ok','[\"v1\",\"v2\"]','t')")
    con.commit()
    con.close()
    lay = paths.Layout(home=str(tmp_path), data=str(data), lock=str(tmp_path / "lock"))
    c = sqlite3.connect(str(data / "db" / "kb.sqlite"))
    r1 = qa_report.c1_counts(c)
    assert r1["papers_total"] == 2 and not r1["agree"]           # the synthetic base lacks most of the manifest
    r2 = qa_report.c2_abstract_sections(c)
    assert r2["without_abstract"] == ["2009.08715"] and r2["without_sections"] == ["2009.08715"]
    r3 = qa_report.c3_failures(c)
    assert r3["not_ok"] == 1 and "no \\title" in r3["papers"][0]["causes"] and \
        "thesis or long document" in r3["papers"][0]["causes"]
    r4 = qa_report.c4_inspire_sample(c, str(data / "meta" / "arxiv"), n=30)
    assert r4["blocked"] and len(r4["sample"]) == 2
    (data / "meta" / "arxiv" / "2611.12831.inspire.json").write_text(json.dumps(
        {"metadata": {"titles": [{"title": "A title of twenty chars or more"}], "authors": [{"full_name": "Wu, J."}]}}))
    r4 = qa_report.c4_inspire_sample(c, str(data / "meta" / "arxiv"), n=30)
    row = [r for r in r4["rows"] if r["metadata"]][0]
    assert row["title_ratio"] == 1.0
    r5 = qa_report.c5_bibliography(c)
    assert r5["entries"] == 2 and r5["rate_any_id"] == 0.5 and r5["in_corpus_fraction"] == 0.0
    r6 = qa_report.c6_duplicates(c)
    assert r6["several_versions_stored"] == [{"paper_id": "2611.12831", "versions": ["v1", "v2"]}]
    r8 = qa_report.c8_equations(c, lay, n=5, must=("2611.12831",))
    row = [r for r in r8["rows"] if r["paper_id"] == "2611.12831"][0]
    assert row["input"] == "raw main file" and row["independent_numbered"] == 3 and row["diff"] == 0
    md_rep = {"at": "t", "database": "d", "snapshot_current": None, "C1": r1, "C2": r2, "C3": r3, "C4": r4,
              "C5": r5, "C6": r6, "C8": r8, "C9": {"claims": 0}, "C10": {"error": "x"},
              "C7": {"k": 10, "questions": 1, "modes": {"text": {"rows": [], "paper_hits": 0, "locator_hits": 0,
                                                                     "paper_hit_rate": 0, "locator_hit_rate": 0,
                                                                     "mrr_paper": 0}}},
              "seconds": 0}
    monkeypatch.setattr(qa_golden, "QUESTIONS", [])
    text = qa_report.markdown(md_rep)
    assert "## C8." in text and "Blocked" not in text


def test_compare_meta():
    tr, ar = qa_report.compare_meta("Dynamical Instability of Collapsed Dark Matter Halos", ["Wei-Xiang Feng", "Hai-Bo Yu"],
                                    "Dynamical instability of collapsed dark matter halos", ["Feng, Wei-Xiang", "Yu, Hai-Bo",
                                                                                            "Zhong, Yi-Ming"])
    assert tr == 1.0 and abs(ar - 2 / 3) < 1e-12


def test_golden_set_and_hit_levels():
    qs = qa_golden.questions()
    assert len(qs) >= 30 and len({q["id"] for q in qs}) == len(qs)
    q = {"paper": "2611.12831", "file": "main.tex", "lines": [[680, 686]]}
    hits = [{"rank": 1, "paper_id": "2609.14218", "source": "MDPBH.tex:L1-20"},
            {"rank": 2, "paper_id": "2611.12831", "source": "main.tex:L100-140"},
            {"rank": 3, "paper_id": "2611.12831", "source": "main.tex:L689-700"}]
    assert qa_golden.hit_level(q, hits) == (2, 3)                 # 689 is within the slack of 5 lines
    assert qa_golden.parse_source("a.tex:L5-b.tex:L9") == ("a.tex", 5, 10 ** 9)
    assert "questions:" in qa_golden.golden_yaml()
