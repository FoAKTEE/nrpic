"""Old-style reference lists with no environment, under a 'References' heading (package ingest4,
wave 3 batch 11): an enumerate list of \\item, lines that start with [n], paragraphs started by a
macro of the paper (\\i\\Key with \\def\\Key{n}) or by a journal macro (A&A's \\ref), and their
citations by number ([n], or a macro that wraps its argument in brackets). Every snippet is
synthetic; the six papers of the store that need the rule are checked by the package's runs."""
import gzip
import json
import sqlite3

from kbtool import bib_parse as B
from kbtool import tex_macros as M
from kbtool import tex_structure as S
from test_papers_ingest import run


def parse(flat):
    macros = M.collect(flat)
    st = S.extract(flat, macros)
    return st, B.bibliography("/nonexistent-ingest4-test", "main.tex", flat, st, macros=macros, reached=[])


ITEMS = r"""\documentclass{article}
\begin{document}
Tensor modes are damped[1] and the effect was computed[2,3] before[1--3].
An interval $x\in[1,2]$ and a line break\\[2]
are no citations, nor is $$[3]$$ in display math.
\begin{center}
References
\end{center}
\begin{enumerate}
\item A. One, Phys. Lett. {\bf 1}, 1 (1981).
\item B. Two, astro-ph/0101001.
\item C. Three, Phys. Rev. D {\bf 3}, 3 (1983).
\end{enumerate}
\end{document}
"""


def test_item_list_under_a_centred_heading():
    st, bib = parse(ITEMS)
    assert bib["source"] == "heading"
    assert [e["cite_key"] for e in bib["entries"]] == ["1", "2", "3"]
    assert bib["entries"][1]["arxiv"] == "astro-ph/0101001"
    assert bib["entries"][2]["raw"].endswith("(1983).")
    assert bib["heading_list"]["style"] == "item" and bib["heading_list"]["heading"] == "References"
    assert [c["keys"] for c in bib["old_cites"]] == [["1"], ["2", "3"], ["1", "2", "3"]]
    assert bib["cited_keys"] == 3 and bib["cited_with_entry"] == 3


PLAIN = r"""\magnification=1200
\def\r#1{[#1]}
\def\Guth{1}
\def\Olive{2}
\def\Smoot{3}
Inflation\r{\Guth,\Olive} explains the data\r\Smoot\ and more\r{\Guth--\Smoot}.
\bigbreak
\centerline{\bf References}
\medskip
\def\i#1{\par\hang\indent\llap{[#1]\quad}\ignorespaces}
{\frenchspacing
\i\Guth    A. Guth, Phys. Rev. D {\bf 23}, 347 (1981).
\i\Olive   K. A. Olive, Phys. Rep. {\bf 190}, 307 (1990).
\i\Smoot   G. F. Smoot {\it et al.}, Astrophys. J. {\bf 396}, L1 (1992).
}
\vfil
\centerline{\bf Figure captions}
FIG.~1. A caption that is not an entry.
\bye
"""


def test_plain_tex_entry_macro_with_number_macros_as_keys():
    st, bib = parse(PLAIN)
    hl = bib["heading_list"]
    assert hl["style"] == "macro:\\i"
    assert [e["cite_key"] for e in bib["entries"]] == ["1", "2", "3"]
    assert bib["entries"][2]["raw"] == r"G. F. Smoot {\it et al.}, Astrophys. J. {\bf 396}, L1 (1992)."
    assert "caption" not in bib["entries"][2]["raw"]
    assert [c["keys"] for c in bib["old_cites"]] == [["1", "2"], ["3"], ["1", "2", "3"]]
    assert {c["cmd"] for c in bib["old_cites"]} == {"r"}


AA = r"""\input aa.cmm
\begref{References}
\ref
Bildhauer S., 1990, Prog. Theor. Phys. 84, 444
\ref
Buchert T., Ehlers J., 1997, A\&A 320, 1, astro-ph/9510056
\ref
Carfora M., Marzuoli A., 1988, Class. Quant. Grav. 5, 659
\endref
\vfill\eject
\appendix{A: more}
Text of the appendix.
\bye
"""


def test_aa_ref_paragraphs_without_definition_get_numbered_keys():
    st, bib = parse(AA)
    assert bib["heading_list"]["style"] == "macro:\\ref"
    assert [e["cite_key"] for e in bib["entries"]] == ["#1", "#2", "#3"]
    assert bib["entries"][1]["arxiv"] == "astro-ph/9510056"
    assert bib["entries"][2]["raw"] == "Carfora M., Marzuoli A., 1988, Class. Quant. Grav. 5, 659"
    assert bib["old_cites"] == []                    # author-year text: no citation by number


BRACKETS = r"""\documentclass{article}
\begin{document}
\begin{itemize}
\item[1] a body list item with an optional argument is no citation
\end{itemize}
The result [2] agrees with [1, 3].
\vskip 10pt\noindent
{\bf References}

\noindent
[1] Alinhac, S.: Op\'erateurs. InterEditions, Paris, 1991.
\next
[2] Bartnik, R.: The mass. Commun. Pure Appl. Math. 34, 661 (1986).
\next
[3] Binney, J., Tremaine, S.: Galactic dynamics. Princeton, 1987.
\end{document}
"""


def test_bracket_lines_and_separators():
    st, bib = parse(BRACKETS)
    assert bib["heading_list"]["style"] == "bracket"
    assert [e["cite_key"] for e in bib["entries"]] == ["1", "2", "3"]
    assert bib["entries"][0]["raw"] == r"Alinhac, S.: Op\'erateurs. InterEditions, Paris, 1991."   # \next dropped
    assert [c["keys"] for c in bib["old_cites"]] == [["2"], ["1", "3"]]


def test_latex_ref_lines_are_not_entries():
    flat = ("\\documentclass{article}\n\\begin{document}\nText.\n\\section*{References}\n"
            "\\ref{eq:a} is an equation.\n\\ref{eq:b} too.\n\\ref{eq:c} and more.\n\\end{document}\n")
    st, bib = parse(flat)
    assert bib["entries"] == [] and bib["heading_list"] is None


def test_a_heading_without_entries_gives_nothing():
    flat = "\\documentclass{article}\n\\begin{document}\nText.\n\\section*{References}\nNone.\n\\end{document}\n"
    st, bib = parse(flat)
    assert bib["entries"] == [] and bib["source"] is None and bib["old_cites"] == []


def test_thebibliography_wins_and_the_rule_stays_off():
    flat = ("\\documentclass{article}\n\\begin{document}\nText \\cite{k1} and [1].\n"
            "\\section*{References}\n\\begin{thebibliography}{1}\n\\bibitem{k1} K. One.\n"
            "\\end{thebibliography}\n\\end{document}\n")
    st, bib = parse(flat)
    assert bib["source"] == "thebibliography" and bib["heading_list"] is None and bib["old_cites"] == []
    assert [e["cite_key"] for e in bib["entries"]] == ["k1"]


def test_heading_text():
    assert B.heading_text(r"{\Large \noindent \bf References}") == "References"
    assert B.heading_text(r"\centerline{\rmm References}") == "References"
    assert B.heading_text(r"\vskip 0.5cm \begref{References}") == "References"
    assert B.heading_text(r"\begin{center}References\end{center}") == "References"


def test_end_to_end_list_is_not_body_text_and_citations_are_rows(store, monkeypatch, capsys):
    store.manifest([("1606.00003", "G01", "2")])
    store.add("1606.00003", gzip.compress(ITEMS.encode(), mtime=0), "v1")
    assert run(store, ["ingest", "arxiv", "--all", "--jobs", "1", "--no-meta"], monkeypatch) == 0
    capsys.readouterr()
    con = sqlite3.connect(store.layout.db_work)
    pj = json.loads(con.execute("SELECT parse_json FROM papers WHERE paper_id='1606.00003'").fetchone()[0])
    assert pj["bib_source"] == "heading" and pj["bib_heading_list"]["style"] == "item"
    assert pj["bib_cited_with_entry"] == 3
    keys = [r[0] for r in con.execute("SELECT cite_key FROM bib_entries WHERE paper_id='1606.00003' "
                                      "ORDER BY bib_id")]
    assert keys == ["1", "2", "3"]
    cit = con.execute("SELECT cite_key, bib_id, chunk_id, context FROM citations WHERE citing='1606.00003' "
                      "ORDER BY char_start, cite_key").fetchall()
    assert [c[0] for c in cit] == ["1", "2", "3", "1", "2", "3"]
    assert all(c[1] is not None and c[2] is not None for c in cit)
    assert "[cit.]" in cit[0][3]
    body = " ".join(r[0] for r in con.execute("SELECT text FROM chunks WHERE paper_id='1606.00003' "
                                              "AND kind='body'"))
    con.close()
    assert "Tensor modes" in body and "Phys. Lett." not in body       # the list is not body text
