# Journal of package ingest3 (kb helper, wave 3 batch 6)

Package brief: tracks/kb/PLAN-wave3.md round 1 "ingest3" as restated in the batch-6 task. A session of
2026-11-20 14:22-14:35 UTC (cut by the usage limit) left `ids/`, `scripts/kbstate.py`,
`scripts/figstyle.py` (a byte copy of harness/style/figstyle.py, checked with cmp) and an incomplete
private copy `scratch/kb/ingest3/dev/kb` (its papers_cli.py was empty). Nothing was committed. This
session (2026-11-21, from 21:14 UTC) keeps ids/ and kbstate.py, replaced the private copy by a fresh
`cp -a` of kb/ at b6f59456, and starts here.

## Entry 1 (2026-11-21 21:20 UTC): what the sources show before any code

Read with grep from outside the store (python3 -I and grep only; nothing executed there):

- REVTeX-3 `\begin{references}` ... `\end{references}` with `\bibitem`: 0710.5073 (28 bibitem lines),
  1109.2484 (113, file is ISO-8859), 1302.5308 (89), 1304.7791 (41), gr-qc/0107076 (16),
  gr-qc/9402041 (13), hep-ph/0011159 (11), astro-ph/0003278 (33). The parser looks only for
  `thebibliography`, so these lists are body text today.
- 1201.4794 (aastex): `\begin{references}` with 46 `\reference{}` lines, no key, no `\cite` at all.
- gr-qc/0304002: `\def\bi{\bibitem}` and `\def\ct{\cite}`: entries AND citations go through
  aliases, so the citation rows are missing too (zero_bib.tsv says 0 cited keys).
- gr-qc/9703066: `\newcommand{\bib}[1]{\bibitem{#1}}` inside thebibliography.
- 2403.15126: `\newcommand{\sortbibitem}[2]{... \bibitem{#1} #2 ...}` (124 occurrences of bibitem in
  the file; the macro takes key and text).
- 2507.01095: main.bbl with 103 `\harvarditem[..]{authors}{year}{key}`, inside thebibliography.
- 2602.00155: the lead's cause "a file the main file does not reach" does NOT hold: arXiv_paper.tex
  line 348 has `\input{paper.tex}` and parse_json lists no unresolved input. paper.tex is pandoc
  output: `\begin{CSLReferences}{1}{0}` with `\bibitem[\citeproctext]{ref-...}` (28). Cause:
  pandoc's CSLReferences environment. [VERIFIED by reading the two files]
- Old styles with a "References" heading and no environment: astro-ph/0306304 (`\item` list),
  astro-ph/9306009 (`\centerline{\bf References}`), astro-ph/9607124 (`{\Large \bf References}`),
  gr-qc/9604001 (`{\bf References}`), gr-qc/9906015 (`\centerline{\rmm References}` + `\ref`),
  astro-ph/9510056 (`\refh`, which look like numbered notes). None cites with `\cite`.

## Prediction P1 (baseline, before run 1)

On the working database (read-only), with tracks/kb/ingest3/scripts/kbstate.py:
- 710 papers; parse_status ok 684 (96.3 %, KB-G2/OPEN.md), the rest review/pdf/failed.
- The TeX papers without a bibliography entry are exactly the 20 of zero_bib.tsv, 11 with status ok;
  10 of those 11 have citation rows (all but 1201.4794), so the strict rate is (684-10)/710 = 94.9 %.
- Few claims touch the 20 papers (0 to 10 locator rows) [JUDGEMENT].
Refuted by: a zero-bibliography list other than those 20, an ok count other than 684, or a strict
rate other than 674/710.
