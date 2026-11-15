"""K9: the independent equation counter on documents whose numbering is known by
construction (the counts follow amsmath's rules; LaTeX is not run)."""
from kbtool import qa_eqcount as q

DOC = r"""\documentclass{article}
\def\be{\begin{equation}}
\def\ee{\end{equation}}
\newcommand{\bea}{\begin{eqnarray}}
\newcommand\eea{\end{eqnarray}}
\begin{document}
\begin{equation} a=b \end{equation}            % 1
\begin{equation*} c \end{equation*}            % 0
\begin{align} x&=1 \\ y&=2 \nonumber \\ z&=3 \\ \end{align}   % 3 (the empty last line is numbered)
\begin{align} M=\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} \\ {a \\ b} \end{align}   % 2: inner rows not split
\be f \ee                                      % 1 through the shorthand
\bea p &=& q \\ r &=& s \notag \eea            % 1
\[ u \]                                        % display, 0
$$ v $$                                        % display, 0
\begin{align*} w \tag{A} \\ t \end{align*}     % 1 (tag)
\begin{multline} long \\ longer \end{multline} % 1
% \begin{equation} commented out \end{equation}
50\% of cases \begin{gather} g \\ h \end{gather}    % 2, escaped percent keeps the line
\begin{comment} \begin{equation} no \end{equation} \end{comment}
\iffalse \begin{equation} no \end{equation} \fi
\end{document}
\begin{equation} after the end \end{equation}
"""


def test_counts():
    r = q.count_document(DOC)
    assert r["numbered"] == 1 + 0 + 3 + 2 + 1 + 1 + 1 + 1 + 2
    assert r["tagged"] == 1
    assert r["displays"] == 11
    assert set(r["shorthands"]) == {"be", "ee", "bea", "eea"}


def test_split_rows_and_alignat():
    assert len(q._split_rows(r" a \\ b \\[2pt] c \\* d ")) == 4
    assert len(q._split_rows(r" a \\ b \\ ")) == 3          # empty last row kept (numbered by amsmath)
    r = q.count_document(r"\begin{document}\begin{alignat}{2} a&=b & c&=d \\ e&=f \end{alignat}\end{document}")
    assert r["numbered"] == 2


def test_nested_same_environment_counts_once():
    r = q.count_document(r"\begin{document}\begin{equation}\begin{equation}x\end{equation}\end{equation}\end{document}")
    assert r["displays"] == 1


def test_source_choice(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.tex").write_text("\\documentclass{x}\\begin{document}\\input{sec}\\end{document}")
    flat = tmp_path / "flat.tex"
    flat.write_text("\\begin{document}\\begin{equation}a\\end{equation}\\end{document}")
    t, which = q.source_for(str(src), "main.tex", str(flat))
    assert which == "flat.tex"
    (src / "main.tex").write_text("\\documentclass{x}\\begin{document}% \\input{sec}\n\\end{document}")
    t, which = q.source_for(str(src), "main.tex", str(flat))
    assert which == "raw main file"


def test_adjacent_inline_maths_are_not_a_display():
    """Found on 1706.09896 (audit P3): "$\\sim 1-3$$\\Gpc^{-3}$" is two inline maths; reading
    it as $$ swallowed every equation up to the next $$."""
    doc = (r"\begin{document} rate $\sim 1 - 3$$\Gpc^{-3}$ and 5\$ \begin{equation} a \end{equation}"
           r" again $x$$y$ \begin{equation} b \end{equation} $$ c $$ \end{document}")
    r = q.count_document(doc)
    assert r["numbered"] == 2 and r["displays"] == 3
