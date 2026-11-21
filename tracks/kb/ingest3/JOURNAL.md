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

## Outcome P1 (run kb-20261121-212037-0b37880, before.json and out.txt read)

Mostly held, one count failed. 710 papers: ok 684, review 23, pdf 3; recorded rate 0.96338. The
zero-bibliography TeX papers are exactly the 20, 11 of them ok. FAILED: only 9 of the 11 ok papers
have citation rows, not 10: gr-qc/0304002 cites through `\def\ct{\cite}`, so it has 0 citation rows
as well as 0 entries (1201.4794 has no `\cite` at all). The verifier's "10 papers with citation rows
but no entry" counts the 9 plus 2403.15126 (status review, 122 rows). Strict rate (ok minus ok with
citation rows and no entry) = 675/710 = 0.95070, not 674/710. Database: 64968 bibliography entries,
104995 citation rows (14208 in corpus), 700 claims (627 with a chunk, 0 dangling), 0 dangling chunk
references in claim_locators.

Claims touching the 20: 21 (more than my 0-10 guess [JUDGEMENT failed]): 171-186 on 2403.15126
(seeds of tracks/B-emd-gw/scope/REFERENCES.md; 178 and 181 human-verified, 186 unlocated) and 658-662
on 1201.4794 (`served:` rows of F-hills, not seeds: `kb claim check` does not reach them). None has a
relocate or verify --locator event (claim_events read), so `kb claim check --id 171..186` is safe
(HANDOFF trap).

## Entry 2 (2026-11-21 21:50 UTC): parser and remap code (commit 776288ad)

Written in the private copy scratch/kb/ingest3/dev/kb, full kb suite green there and again in the
worktree before the commit. What changed: tex_structure.command_aliases finds macros that stand for
\bibitem or \cite from their definitions (bare `\def\bi{\bibitem}`, or a body passing argument k as
the key: `\bib[1]{\bibitem{#1}}`, `\sortbibitem[2]{...\bibitem{#1} #2...}`, `\refto[1]{Ref.~\cite{#1}}`),
plus xparse `\NewDocumentCommand` (pandoc's `\citeproc{mm}{...\cite{#1}...}`); the reference-list
environments `references`, `thereferences`, `CSLReferences` count (when they hold entries) and start
the bibliography region, so their text is no longer body chunks; entries `\harvarditem[.]{a}{y}{key}`
and AASTeX `\reference{}` (keys `#1`, `#2`, ...); a .tex the main file does not reach, only when the
paper cites and has no entry, recorded as parse_json.bib_unreached_file; parse_json also gets
bib_cited_keys, bib_cited_with_entry, review_reasons; the review rule; claims_remap and the options
--remap-claims, --dry-run --out of `kb ingest arxiv`.

Correction of the lead's cause list [VERIFIED, entry 1]: 2602.00155 is CSLReferences, not an
unreached file; 2403.15126 is `\sortbibitem` (lead's list: "none found"); gr-qc/0304002 also cites
through `\ct`. An exploratory dry run from the private copy (not registered; its numbers are not
used) showed the counts below; the registered run with the committed code is the evidence.

## Prediction P2 (registered dry run of the 20 with commit 776288ad; nothing written)

- Entries equal the lead's item counts: 1201.4794 46, 2507.01095 103, gr-qc/0304002 38,
  gr-qc/9703066 18, 2602.00155 28; the eight REVTeX-3 papers the counts of zero_bib.tsv (28, 104, 87,
  38, 16, 13, 11, 33); 2403.15126 117 (the live `\sortbibitem` lines; grep -c gives 117).
- Every cited key of these 14 has an entry (cited_with_entry = cited_keys); gr-qc/0304002 gets 55
  citation commands through `\ct`; 2602.00155 gets 28 `\citeproc` citations.
- Zero entries remain for exactly six: astro-ph/0306304, astro-ph/9306009, astro-ph/9510056,
  astro-ph/9607124, gr-qc/9604001, gr-qc/9906015 (old styles without an environment, no \cite).
- Status: the 11 ok papers stay ok; nothing becomes review by the new rule (each paper that cites
  now has entries).
Refuted by: any count above that differs, a cited key without entry, or a seventh zero.

## Outcome P2 (run kb-20261121-213314-f5e7cc2; dry/*.json and out.txt read)

Held, with one count off by one. Entries: 1201.4794 46, 2507.01095 103, gr-qc/0304002 38,
gr-qc/9703066 18, 2602.00155 28, 0710.5073 28, 1109.2484 104, 1302.5308 87, 1304.7791 38,
gr-qc/0107076 16, gr-qc/9402041 13, hep-ph/0011159 11, astro-ph/0003278 33, 2403.15126 117. Every
cited key has an entry in all 14 (cited_with_entry = cited_keys). gr-qc/0304002: 55 commands through
`\ct`. 2602.00155: 29 `\citeproc` commands for 28 keys (I predicted "28 citations": one key is cited
twice; the prediction confused keys and commands). Zero entries for exactly the six old-style
papers. Status: 11 ok, 9 review, as before; the review rule fires for none. Not predicted:
astro-ph/0003278 has 33 entries but 0 citation commands and 0 sections although its source has
`\section` and `\cite` (zero_bib.tsv counted 33 cited keys): a structure defect beyond the
bibliography (optional item of the brief), left for later in this package if time remains.

## Prediction P3 (re-ingest of the 20 with --remap-claims, then tags, vectors, resolve-bib, claim check)

- Bibliography entries per paper as in the dry run (P2); TeX papers without an entry in the whole
  database: 6 (the old styles), none with status ok. parse_status overall unchanged: ok 684, review
  23, pdf 3 (the 11 ok stay ok, the 9 review stay review). Strict rate = recorded rate = 0.96338.
- Bibliography entries +746 in all (the 14 sums: 46+103+38+18+28+28+104+87+38+16+13+11+33+117);
  citation rows +84 (gr-qc/0304002 55 commands, 2602.00155 29) give new rows; keys of other papers'
  rows get bib_id now.
- flat.tex byte-identical for all 20 (tex_files is unchanged), so every remap says identical_flat;
  the 21 claims keep their locator ranges, their chunk ids move to the new rows, no dangling
  reference anywhere; statuses and labels unchanged (171-185 located/checked, 186 unlocated, 658-662
  located). `kb claim check --id 171 ... 186` then reports "same" for all 16 and writes locator rows
  equal to the remapped ones (an independent resolution through claims_check).
- `kb embed --check --work` afterwards: 0 missing, 0 stale, 0 orphaned.
Refuted by: a dangling chunk reference, a changed status or label, a claim-check row that differs
from the remap, a status change, or entry counts other than the dry run's.
