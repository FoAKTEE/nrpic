"""Reference-list formats beyond thebibliography + \\bibitem (package ingest3, wave 3): REVTeX-3
and AASTeX `references`, AASTeX `\\reference`, macros standing for \\bibitem or \\cite (found
from their definitions), `\\harvarditem`, pandoc's CSLReferences, a reference list in a file
the main file does not reach, and the review rule for a paper that cites and has no entry.
Every snippet is synthetic."""
import gzip
import json
import sqlite3

from conftest import make_tar
from kbtool import bib_parse as B
from kbtool import tex_macros as M
from kbtool import tex_structure as S
from test_papers_ingest import run


def parse(flat, root=None, main="main.tex", reached=None):
    macros = M.collect(flat)
    st = S.extract(flat, macros)
    return st, B.bibliography(root or "/nonexistent-ingest3-test", main, flat, st, macros=macros, reached=reached)


REVTEX3 = r"""\documentstyle[aps,prd]{revtex}
\begin{document}
\section{Intro}
Alpha \cite{a1,a2} and beta \cite{a3}.
\begin{references}
\bibitem{a1} A. One, Phys. Rev. D {\bf 1}, 1 (2001), astro-ph/0101001.
\bibitem{a2} B. Two, arXiv:1101.0001.
\bibitem{a3} C. Three, J. Synth. {\bf 3}, 3 (2003).
\end{references}
\end{document}
"""


def test_revtex3_references_environment():
    st, bib = parse(REVTEX3)
    assert [e["cite_key"] for e in bib["entries"]] == ["a1", "a2", "a3"]
    assert [e["arxiv"] for e in bib["entries"]] == ["astro-ph/0101001", "1101.0001", None]
    assert bib["source"] == "thebibliography" and bib["cited_keys"] == 3 and bib["cited_with_entry"] == 3
    assert any("references environment" in n for n in bib["notes"])
    # the list starts the bibliography region, so it is not body text
    assert st["bibliography_at"] == REVTEX3.index(r"\begin{references}")


def test_references_environment_without_items_is_body():
    flat = "\\documentclass{article}\n\\begin{document}\n\\begin{references}\nNo items here.\n\\end{references}\n" \
           "\\end{document}\n"
    st, bib = parse(flat)
    assert st["bibliography_at"] is None and bib["entries"] == []


AAS = r"""\documentclass[preprint]{aastex}
\begin{document}
\section{Results}
Text without citation commands.
\begin{references}
\reference{} Alpha, A. 2001, ApJ, 1, 1
\reference{} Beta, B. 2002, ApJ, 2, 2, astro-ph/0202002
\reference{} Gamma, C. 2003, Synth. J., 3, 3
\end{references}
\end{document}
"""


def test_aastex_reference_items_get_numbered_keys():
    st, bib = parse(AAS)
    assert [e["cite_key"] for e in bib["entries"]] == ["#1", "#2", "#3"]
    assert bib["entries"][0]["raw"].startswith("Alpha, A. 2001")
    assert bib["entries"][1]["arxiv"] == "astro-ph/0202002"
    assert st["bibliography_at"] == AAS.index(r"\begin{references}")


ALIAS_DEF = r"""\documentclass{article}
\def\bi{\bibitem}
\def\ct{\cite}
\begin{document}
\section{One}
As shown in \ct{k1}, and also \ct{k2,k3}.
\begin{thebibliography}{9}
\bi{k1} First, gr-qc/9901001.
\bi{k2} Second.
\bi{k3} Third, arXiv:1202.0002.
\end{thebibliography}
\end{document}
"""


def test_def_aliases_of_bibitem_and_cite():
    st, bib = parse(ALIAS_DEF)
    assert [e["cite_key"] for e in bib["entries"]] == ["k1", "k2", "k3"]
    assert bib["entries"][0]["arxiv"] == "gr-qc/9901001" and bib["entries"][2]["arxiv"] == "1202.0002"
    cites = [c for c in st["cites"] if not c["nocite"]]
    assert [c["keys"] for c in cites] == [["k1"], ["k2", "k3"]]
    assert {c["cmd"] for c in cites} == {"cite"} and {c["alias"] for c in cites} == {"ct"}
    assert bib["cited_with_entry"] == 3


ALIAS_ARG = r"""\documentclass{article}
\newcommand{\bib}[1]{\bibitem{#1}}
\newcommand{\sortbibitem}[2]{\global\@namedef{bibitem@#1}{\bibitem{#1} #2}}
\newcommand{\refto}[1]{Ref.~\cite{#1}}
\begin{document}
\section{One}
See \refto{m1} and \cite{m2}.
\begin{thebibliography}{9}
\bib{m1} Macro one, arXiv:1303.0003.
\sortbibitem{m2}{Macro two, Synth. Lett. {\bf 2} (2014)}
\end{thebibliography}
\end{document}
"""


def test_newcommand_aliases_with_key_argument():
    al = S.command_aliases(M.collect(ALIAS_ARG), B.BIBITEM_TARGETS)
    assert al == {"bib": ("bibitem", 1, 1), "sortbibitem": ("bibitem", 2, 1)}
    st, bib = parse(ALIAS_ARG)
    ents = {e["cite_key"]: e for e in bib["entries"]}
    assert set(ents) == {"m1", "m2"} and ents["m1"]["arxiv"] == "1303.0003"
    assert "Macro two" in ents["m2"]["raw"]
    assert sorted(k for c in st["cites"] for k in c["keys"]) == ["m1", "m2"]


def test_no_alias_from_a_macro_that_only_mentions_the_name():
    macros = M.collect(r"\newcommand{\bibitemfont}{\small}\def\x{\bibitemsep}\newcommand{\cf}[1]{cf. #1}")
    assert S.command_aliases(macros, B.BIBITEM_TARGETS + ("cite",)) == {}


HARVARD_BBL = r"""\begin{thebibliography}{xx}
\harvarditem{Alpha et~al.}{2020}{Alpha:2020} Alpha, A., 2020, Synth. J., arXiv:2001.00001
\harvarditem[Beta]{{Beta} and Gamma}{2021}{Beta:2021} Beta, B. and Gamma, C., 2021, doi:10.1000/xyz.1
\end{thebibliography}
"""


def test_harvarditem_key_is_the_third_argument():
    ents = B.parse_bbl(HARVARD_BBL)
    assert [e["cite_key"] for e in ents] == ["Alpha:2020", "Beta:2021"]
    assert ents[0]["label"] == "Alpha et~al. 2020" and ents[1]["label"].startswith("Beta ")
    assert B.bbl_entry_ids(ents[0])[0] == "2001.00001" and B.bbl_entry_ids(ents[1])[1] == "10.1000/xyz.1"


CSL = r"""\documentclass{article}
\begin{document}
\section{Software}
A code \citep{ref-one} and another \citep{ref-two}.
\begin{CSLReferences}{1}{0}
\bibitem[\citeproctext]{ref-one}
One, A. 2021. arXiv:2101.00001.
\bibitem[\citeproctext]{ref-two}
Two, B. 2022.
\end{CSLReferences}
\end{document}
"""


def test_pandoc_csl_references():
    st, bib = parse(CSL)
    assert [e["cite_key"] for e in bib["entries"]] == ["ref-one", "ref-two"]
    assert bib["entries"][0]["arxiv"] == "2101.00001"
    assert st["bibliography_at"] == CSL.index(r"\begin{CSLReferences}")


def test_unreached_file_used_only_when_the_main_file_cites_and_has_no_entry(tmp_path):
    main = "\\documentclass{article}\n\\begin{document}\n\\section{A}\nText \\cite{u1}.\n\\end{document}\n"
    refs = "\\begin{thebibliography}{1}\n\\bibitem{u1} Unreached, arXiv:1404.00001.\n\\end{thebibliography}\n"
    other = "\\begin{thebibliography}{1}\n\\bibitem{zz} Not cited.\n\\end{thebibliography}\n"
    (tmp_path / "main.tex").write_text(main)
    (tmp_path / "refs.tex").write_text(refs)
    (tmp_path / "other.tex").write_text(other)
    st, bib = parse(main, root=str(tmp_path), reached=["main.tex"])
    assert [e["cite_key"] for e in bib["entries"]] == ["u1"] and bib["unreached_file"] == "refs.tex"
    assert bib["files"] == ["refs.tex"] and any("does not reach" in n for n in bib["notes"])
    # a file the flattening read is never taken as unreached
    st, bib = parse(main, root=str(tmp_path), reached=["main.tex", "refs.tex"])
    assert bib["entries"] == [] and bib["unreached_file"] is None
    # with its own entries the main file's list wins
    main2 = main.replace("\\end{document}", refs + "\\end{document}").replace("{u1}", "{u1}", 1)
    st, bib = parse(main2, root=str(tmp_path), reached=["main.tex"])
    assert bib["unreached_file"] is None and [e["cite_key"] for e in bib["entries"]] == ["u1"]


def test_plain_thebibliography_unchanged():
    flat = "\\documentclass{article}\n\\begin{document}\nX \\cite{p}.\n\\begin{thebibliography}{1}\n" \
           "\\bibitem[P(1)]{p} P, arXiv:1505.00001\n\\end{thebibliography}\n\\end{document}\n"
    st, bib = parse(flat)
    assert [(e["cite_key"], e["label"], e["arxiv"]) for e in bib["entries"]] == [("p", "P(1)", "1505.00001")]
    assert bib["notes"] == []


LONG = " ".join(["word"] * 1200)
NOBIB = ("\\documentclass{article}\n\\begin{document}\n\\title{A paper that cites without a list}\n"
         "\\begin{abstract}" + " ".join(["abstract"] * 30) + "\\end{abstract}\n"
         + "".join(f"\\section{{S{k}}}\n{LONG}\n\\begin{{equation}}x_{k}=1\\end{{equation}}\n"
                   f"\\begin{{equation}}y_{k}=2\\end{{equation}}\n" for k in range(3))
         + "See \\cite{gone1,gone2}.\n\\end{document}\n").encode()


def test_review_rule_end_to_end(store, monkeypatch, capsys):
    store.manifest([("1606.00001", "G01", "2"), ("1606.00002", "G01", "2")])
    store.add("1606.00001", gzip.compress(NOBIB, mtime=0), "v1")
    withbib = NOBIB.replace(b"\\end{document}", b"\\begin{thebibliography}{2}\n\\bibitem{gone1} G1.\n"
                            b"\\bibitem{gone2} G2.\n\\end{thebibliography}\n\\end{document}")
    store.add("1606.00002", make_tar([("main.tex", withbib)]), "v1")
    assert run(store, ["ingest", "arxiv", "--all", "--jobs", "1", "--no-meta"], monkeypatch) == 0
    capsys.readouterr()
    con = sqlite3.connect(store.layout.db_work)
    rows = {r[0]: (r[1], json.loads(r[2])) for r in con.execute(
        "SELECT paper_id, parse_status, parse_json FROM papers")}
    con.close()
    st1, pj1 = rows["1606.00001"]
    st2, pj2 = rows["1606.00002"]
    assert pj1["quality"]["score"] >= 0.75 and pj2["quality"]["score"] >= 0.75   # both would be 'ok' by score
    assert st1 == "review" and pj1["review_reasons"] and "no bibliography entry" in pj1["review_reasons"][0]
    assert st2 == "ok" and pj2["review_reasons"] == [] and pj2["bib_cited_with_entry"] == 2


def test_dry_run_writes_nothing(store, monkeypatch, capsys, tmp_path):
    store.manifest([("1606.00001", "G01", "2")])
    store.add("1606.00001", gzip.compress(NOBIB, mtime=0), "v1")
    out = tmp_path / "dry"
    assert run(store, ["ingest", "arxiv", "--id", "1606.00001", "--jobs", "1", "--dry-run", "--out", str(out)],
               monkeypatch) == 0
    assert "nothing written" in capsys.readouterr().out
    d = json.load(open(out / "1606.00001.json"))
    assert d["status"] == "review" and d["bib_entries"] == 0 and d["cites"] == 1 and d["cited_keys"] == 2
    import os
    assert not os.path.exists(store.layout.db_work)            # not even created
    assert not os.path.exists(os.path.join(store.data, "build", "tex", "1606.00001"))


CITEPROC = r"""\documentclass{article}
\NewDocumentCommand\citeproctext{}{}
\NewDocumentCommand\citeproc{mm}{\begingroup\def\citeproctext{#2}\cite{#1}\endgroup}
\begin{document}
\section{Software}
A code {[}\citeproc{ref-one}{1}{]} and more {[}\citeproc{ref-two}{2}{]}.
\begin{CSLReferences}{1}{0}
\bibitem[\citeproctext]{ref-one}
One, A. 2021.
\bibitem[\citeproctext]{ref-two}
Two, B. 2022.
\end{CSLReferences}
\end{document}
"""


def test_pandoc_citeproc_is_a_cite_through_its_xparse_definition():
    assert S.xparse_macros(CITEPROC)["citeproc"]["nargs"] == 2
    st, bib = parse(CITEPROC)
    assert [c["keys"] for c in st["cites"]] == [["ref-one"], ["ref-two"]]
    assert {c["alias"] for c in st["cites"]} == {"citeproc"}
    assert bib["cited_with_entry"] == 2
