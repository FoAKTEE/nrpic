"""Numbers of equations, sections, figures and tables computed by kbtool.tex_structure,
compared with the numbers LaTeX itself writes into the .aux file for the same synthetic
documents. The documents are written by this test (never a download) and compiled with
pdflatex -no-shell-escape in the test's temporary directory."""
import os
import re
import shutil
import subprocess

import pytest

from kbtool import tex_files as F
from kbtool import tex_structure as S

PDFLATEX = shutil.which("pdflatex")

BODY = r"""
\begin{document}
\title{Numbering test}
\author{A. Author}
\begin{abstract}
An abstract of a test document for the numbering of equations, sections, figures and tables.
\end{abstract}
\maketitle
\section{Introduction}\label{sec:intro}
Text \cite{k1}.
\begin{equation} a = b \label{eq:one} \end{equation}
\begin{equation*} c = d \end{equation*}
\[ e = f \]
\begin{align}
x &= 1 \label{eq:al1} \\
y &= 2 \nonumber \\
z &= 3 \label{eq:al3}
\end{align}
\subsection{Sub}\label{sec:sub}
\begin{subequations}\label{eq:subparent}
\begin{align}
p &= 1 \label{eq:suba} \\
q &= 2 \label{eq:subb}
\end{align}
\end{subequations}
\begin{gather}
g = 1 \label{eq:g1} \\
h = 2 \label{eq:g2}
\end{gather}
\begin{multline}
m = 1 + 2 \\ + 3 \label{eq:mult}
\end{multline}
\begin{eqnarray}
u &=& 1 \label{eq:ea1} \\
v &=& 2 \nonumber
\end{eqnarray}
\begin{equation} w = 0 \tag{T} \label{eq:tagged} \end{equation}
\begin{eqnarray}
a &=& 1, \label{eq:ena1} \\
b &=& 2, \nonumber \\ \label{eq:enaw2}
\end{eqnarray}
\begin{eqnarray}
d &=& 4 \label{eq:end4} \\
\end{eqnarray}
\begin{equation} e = 5 \label{eq:afterempty} \end{equation}
\begin{align}
f &= 6 \label{eq:alf6} \\
\end{align}
\begin{equation} g = 7 \label{eq:afterempty2} \end{equation}
\begin{figure}\centering\caption{First.}\label{fig:one}\end{figure}
\begin{table}\caption{A table.}\label{tab:one}\end{table}
\section*{Unnumbered}
\section{Second}\label{sec:second}
\begin{equation} k = 1 \label{eq:sec2} \end{equation}
\subsection{Second sub}\label{sec:sub2}
\subsubsection{Deep}\label{sec:deep}
\begin{figure}\centering\caption{Second.}\label{fig:two}\end{figure}
\appendix
\section{First appendix}\label{sec:appA}
\begin{equation} r = 1 \label{eq:appA1} \end{equation}
\begin{equation} s = 1 \label{eq:appA2} \end{equation}
\subsection{Appendix sub}\label{sec:appAsub}
\section{Second appendix}\label{sec:appB}
\begin{equation} t = 1 \label{eq:appB1} \end{equation}
\begin{thebibliography}{1}
\bibitem{k1} A. B., arXiv:1234.56789.
\end{thebibliography}
\end{document}
"""

DOCS = {
    "article": "\\documentclass{article}\n\\usepackage{amsmath}\n" + BODY,
    "article_numberwithin": "\\documentclass{article}\n\\usepackage{amsmath}\n\\numberwithin{equation}{section}\n" + BODY,
    "revtex": "\\documentclass[aps,prd,nofootinbib]{revtex4-2}\n\\usepackage{amsmath}\n" + BODY,
}


def aux_labels(aux_text):
    out = {}
    for m in re.finditer(r"\\newlabel\{([^{}]*)\}\{\{([^{}]*)\}", aux_text):
        if not m.group(1).endswith("@cref"):
            out[m.group(1)] = m.group(2)
    return out


def compile_doc(tmp, name, text):
    d = os.path.join(tmp, name)
    os.makedirs(d)
    with open(os.path.join(d, "doc.tex"), "w") as f:
        f.write(text)
    for _ in range(2):
        r = subprocess.run([PDFLATEX, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "doc.tex"],
                           cwd=d, capture_output=True, timeout=120, stdin=subprocess.DEVNULL)
    assert r.returncode == 0, r.stdout[-2000:]
    return aux_labels(open(os.path.join(d, "doc.aux")).read())


def roman_to_int(s):
    vals = {"I": 1, "V": 5, "X": 10}
    n = 0
    for k, c in enumerate(s):
        v = vals[c]
        n += -v if k + 1 < len(s) and vals[s[k + 1]] > v else v
    return n


@pytest.mark.skipif(PDFLATEX is None, reason="pdflatex not installed")
@pytest.mark.parametrize("name", sorted(DOCS))
def test_numbers_equal_latex_aux(tmp_path, name):
    truth = compile_doc(str(tmp_path), name, DOCS[name])
    flat = F.strip_comments_text(DOCS[name])
    st = S.extract(flat)
    mine = {k: v["number"] for k, v in st["labels"].items()}
    compared = 0
    for label, num in truth.items():
        if not label.startswith(("eq:", "sec:", "fig:", "tab:")):
            continue                                # class-internal labels (FirstPage, LastPage, ...)
        if label.startswith("tab:") and name == "revtex":
            num = str(roman_to_int(num))            # REVTeX numbers tables I, II, ...
        if label.startswith("sec:") and name == "revtex":
            # REVTeX prints section numbers as roman numerals (I, II) and letters: compare the
            # top level only, converted
            if label in ("sec:intro", "sec:second"):
                assert mine[label] == str(roman_to_int(num)), (label, num, mine.get(label))
                compared += 1
            continue
        assert label in mine, (label, num)
        assert mine[label] == num, (name, label, "latex", num, "kbtool", mine[label])
        compared += 1
    assert compared >= (15 if name == "revtex" else 20)


@pytest.mark.skipif(PDFLATEX is None, reason="pdflatex not installed")
def test_equation_rows_of_the_test_document():
    st = S.extract(F.strip_comments_text(DOCS["article"]))
    rows = [(e["env"], e["number"], tuple(e["labels"])) for e in st["equations"]]
    # equation*, \[ \] give rows without numbers; align gives 2 rows (the \nonumber line joins the first)
    assert ("equation*", None, ()) in rows and ("\\[", None, ()) in rows
    assert [r for r in rows if r[0] == "align"][:2] == [("align", "2", ("eq:al1",)), ("align", "3", ("eq:al3",))]
    assert ("multline", "7", ("eq:mult",)) in rows
    assert st["abstract"] and "numbering" in st["abstract"]["tex"]
    assert [s["number"] for s in st["sections"]] == ["1", "1.1", None, "2", "2.1", "2.1.1", "A", "A.1", "B"]
    assert [c["keys"] for c in st["cites"]] == [["k1"]]
