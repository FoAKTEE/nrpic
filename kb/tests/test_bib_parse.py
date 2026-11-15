"""K3: identifiers in bibliography entries; .bbl (natbib/REVTeX and biblatex), .bib, choice of source."""
import os

import pytest

from kbtool import bib_parse as B
from kbtool import tex_structure as S


@pytest.mark.parametrize("text,ids", [
    ("A. B., arXiv:2611.12831 [gr-qc]", ["2611.12831"]),
    ("\\Eprint {http://arxiv.org/abs/1702.00786} {arXiv:1702.00786 [astro-ph.IM]}", ["1702.00786"]),
    ("Phys. Rev. D 58, 064002 (1998), gr-qc/9804040v2", ["gr-qc/9804040"]),
    ("astro-ph.CO/0601001 and hep-th/9711200", ["astro-ph/0601001", "hep-th/9711200"]),
    ("arXiv:0704.0001", ["0704.0001"]),
    ("1501.00001 [astro-ph.CO]", ["1501.00001"]),
    ("arXiv:1412.12345", []),               # 5 digits before 2015: not an id
    ("arXiv:1513.0001", []),                # month 13
    ("pages 1234.56789, vol 12", []),       # bare number without context
    ("https://doi.org/10.48550/arXiv.2401.00001", []),   # arXiv DOI: handled by arxiv_from_doi
])
def test_arxiv_ids(text, ids):
    assert B.arxiv_ids(text) == ids


def test_dois_and_arxiv_doi():
    t = "\\href {\\doibase 10.1103/PhysRevD.95.084034} {Phys. Rev. D} and doi:10.1093/mnras/stx\\_123."
    assert B.dois(t) == ["10.1103/PhysRevD.95.084034", "10.1093/mnras/stx_123"]
    assert B.arxiv_from_doi("doi = {10.48550/arXiv.2401.00001}") == "2401.00001"


REVTEX_BBL = r"""%apsrev4-2.bst
\begin{thebibliography}{3}%
\makeatletter
\providecommand \@ifxundefined [1]{\@ifx{#1\undefined}}%
\bibitem [{\citenamefont {Wu}\ and\ \citenamefont {Most}(2026)}]{Wu2026}%
  \BibitemOpen
  \bibfield  {author} {\bibinfo {author} {\bibfnamefont {J.}~\bibnamefont {Wu}}},\ \bibinfo {title}
  {{Numerical-relativity particle-in-cell simulations}},\ \Eprint {https://arxiv.org/abs/2611.12831}
  {arXiv:2611.12831 [gr-qc]} \BibitemShut {NoStop}%
\bibitem [{Old(1998)}]{old}%
  \bibinfo {journal} {Phys. Rev. D}\ \textbf {\bibinfo {volume} {58}},\ \href {\doibase
  10.1103/PhysRevD.58.064002} {\bibinfo {pages} {064002}} \BibitemShut {NoStop}%
\bibitem{noid} A. Nobody, Some book (Press, 1970).
\end{thebibliography}%
"""


def test_parse_revtex_bbl():
    es = B.parse_bbl(REVTEX_BBL)
    assert [e["cite_key"] for e in es] == ["Wu2026", "old", "noid"]
    ids = [B.bbl_entry_ids(e)[:2] for e in es]
    assert ids == [("2611.12831", None), (None, "10.1103/PhysRevD.58.064002"), (None, None)]
    assert B.entry_title(es[0]) == "Numerical-relativity particle-in-cell simulations"


BIBLATEX_BBL = r"""\refsection{0}
  \datalist[entry]{nty/global//global/global}
    \entry{smith20}{article}{}
      \field{title}{A title}
      \field{eprint}{2001.07968}
      \field{eprinttype}{arXiv}
      \verb{doi}
      \verb 10.1093/mnras/staa123
      \endverb
    \endentry
  \enddatalist
\endrefsection
"""


def test_parse_biblatex_bbl():
    es = B.parse_bbl(BIBLATEX_BBL)
    assert len(es) == 1 and es[0]["cite_key"] == "smith20"
    arx, doi, eprint, n = B.bbl_entry_ids(es[0])
    assert (arx, doi, eprint) == ("2001.07968", "10.1093/mnras/staa123", "2001.07968")


BIB = r"""
@string{prd = "Phys. Rev. D"}
@comment{ignored @article{fake, title={x}} }
@article{East:2019,
  author = {East, William E. and Wojtak, Rados{\l}aw},
  title = "{Relativistic simulations of {Large} scale structure}",
  journal = prd # " 100",
  eprint = {1908.05683},
  archivePrefix = {arXiv},
  doi = {10.1103/PhysRevD.100.064029}
}
@ARTICLE(Old97,
  title = {Old style}, eprint = "gr-qc/9703066", year = 1997)
@misc{web, howpublished = {\url{https://arxiv.org/abs/2111.05282v3}}, title={Web}}
@book{nobook, title = {A Book}, publisher = {P}}
"""


def test_parse_bib():
    es = {e["cite_key"]: e for e in B.parse_bib(BIB)}
    assert set(es) == {"East:2019", "Old97", "web", "nobook"}
    assert es["East:2019"]["fields"]["title"] == "{Relativistic simulations of {Large} scale structure}"
    assert B.bib_entry_ids(es["East:2019"])[:2] == ("1908.05683", "10.1103/PhysRevD.100.064029")
    assert B.bib_entry_ids(es["Old97"])[0] == "gr-qc/9703066"
    assert B.bib_entry_ids(es["web"])[0] == "2111.05282"
    assert B.bib_entry_ids(es["nobook"])[:2] == (None, None)


def test_bib_agrees_with_bibtexparser():
    bp = pytest.importorskip("bibtexparser")
    lib = bp.parse_string(BIB)
    theirs = {e.key: {k.lower(): v for k, v in e.fields_dict.items()} for e in lib.entries}
    mine = {e["cite_key"]: e for e in B.parse_bib(BIB)}
    assert set(theirs) == set(mine)
    for k in theirs:
        for f in ("title", "eprint", "doi"):
            if f in theirs[k]:
                v = theirs[k][f].value
                assert str(v).strip("{}\"") == mine[k]["fields"][f].strip("{}\""), (k, f)


def _write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)


def test_source_preference(tmp_path):
    # \bibliography + .bbl present: the .bbl; .bib only cited entries otherwise; inline thebibliography
    r = str(tmp_path / "a")
    flat = r"\begin{document}\cite{Wu2026}\bibliography{refs}\end{document}"
    _write(r, "main.tex", flat)
    _write(r, "main.bbl", REVTEX_BBL)
    _write(r, "refs.bib", BIB)
    st = S.extract(flat)
    b = B.bibliography(r, "main.tex", flat, st)
    assert b["source"] == "bbl" and len(b["entries"]) == 3
    os.remove(os.path.join(r, "main.bbl"))
    flat2 = r"\begin{document}\cite{East:2019,web}\bibliography{refs}\end{document}"
    b = B.bibliography(r, "main.tex", flat2, S.extract(flat2))
    assert b["source"] == "bib" and sorted(e["cite_key"] for e in b["entries"]) == ["East:2019", "web"]
    flat3 = r"\begin{document}\cite{old}" + REVTEX_BBL + r"\end{document}"
    b = B.bibliography(r, "main.tex", flat3, S.extract(flat3))
    assert b["source"] == "thebibliography" and len(b["entries"]) == 3
