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

## Outcome P3 (runs kb-20261121-213423-d6e666c re-ingest, kb-20261121-213521-2b80ade tags/vectors/resolve, kb-20261121-213832-67fadc6 state and claim check; outputs read)

Held, with two arithmetic slips in my prediction. TeX papers without an entry: 6 (the old styles),
none ok; ok 684, review 23, pdf 3 unchanged; strict rate = recorded rate = 684/710 = 0.96338 (was
0.95070). Every citation row of the 20 now has an entry (citations_with_entry = citations). Entries
64968 -> 65648 (+680: the per-paper counts equal the dry run's; my "+746" was a wrong sum).
Citation rows 104995 -> 105082 (+87 = 58 rows of gr-qc/0304002 from 55 commands with several keys +
29 of 2602.00155; my "+84" counted commands, not rows); in corpus 14208 -> 14274. Vectors after
`kb embed`: 796 chunks and 935 equations embedded, 836 and 935 orphans deleted; `kb embed --check
--work`: 0 missing, 0 stale, 0 orphaned (43520 chunks, 54502 equations). Tags: 935 equations
re-tagged.

Claims: flat.tex byte-identical for the two papers with claims (remap reports identical_flat True);
2403.15126: 16 claims, 15 locator rows moved to the new chunk ids (186 has no row, untouched);
1201.4794: 5 claims, 5 rows. `kb claim check --id 171..186`: "checked: same 16", and its locator
rows, chunk ids and quote ranges equal the remap's for all 21 claims (0 differences; the check
resolves independently through claims_check.Store). Flat ranges equal those before the re-ingest
for all 21. 0 claims and 0 locator rows point at a missing chunk. Six claims (183, 658-662) changed
label or status between my baseline (21:20) and the re-ingest (21:34): claim_events show `verify`
by kb-claims_tracks at 21:30, not by this package; the remap events carry no label or status.

## Entry 3 (2026-11-21 21:45 UTC): provenance of the 24 additions (download records and reports)

From kb-data/meta/arxiv/<key>.json (fetched_utc) and the wave-3a report scratch/orch/wave3a_reports/kb.md
with the packages' own files on kb/brief-check and track/F-hills (git grep):
- F-hills, 2026-11-19 14:25: 1312.1289 v3 (EIH equations, tracks/F-hills/eih/README.md:43),
  1805.07240 v5 (2.5PN Hamiltonian, tracks/F-hills/binary_conv/scripts/refs.py:10).
- kb brief check s31_32, 14:26: 2602.01830 v2, 2505.00286 v3 (dGREM/TEGR hyperbolicity; s31_32/JOURNAL.md:69).
- kb brief check s37_38, 15:20-15:23 (open question 20, EdS stability; s37_38/CHECK.md:19-20):
  2606.16879, 2607.09326, 2306.17774, 2107.00457, 2012.14241, 2604.14911, 2512.19454, 1402.7085,
  1904.13290, 2402.08544, 2609.14755, 1007.0184 (12).
- kb brief check s5_s6, 15:37: 2403.03470, 2402.17530 (Burnett without symmetry; report line 602).
- kb novelty, 15:38-15:42: 2009.08968, 2404.07659, 2406.11417, 2606.26532, 2607.09285, 2508.13294
  (S5 free streaming and S7 Burnett; novelty/NOVELTY.md:11).
Metadata present before this package: arXiv API for 5 (2306.17774, 2402.17530, 2403.03470,
2606.16879, 2607.09326), INSPIRE for 4 (2306.17774, 2606.16879, 2607.09326, 2609.14755).

## Prediction P4 (metadata fetch for the 24, one call, --meta --service both)

The command skips what is stored: arXiv API requests for the 19 without a record (one batch of 19)
and INSPIRE for the 20 without one (two batches of 10). All 19 arXiv records ok. INSPIRE: most ok;
a paper of 2026 may have no record yet (status not-found) [JUDGEMENT]. Refuted by an arXiv failure
or by a fetch of an id that already had a record.

## Outcome P4 (run kb-20261121-214115-b07a4a7; out.txt and the records read)

Held: exit 0; afterwards all 24 have an arXiv-API record (status ok) and an INSPIRE record (status
ok), including the 2026 papers. Groups (my judgement, from title and use; alternatives in the note
column): G03 15, G13 3, G21 2, G01 1, G04 1, G09 1, G18 1. Appended to kb/manifests/arxiv_additions.tsv
(commit 02c76737; meta_manifest.check_additions: no problem, 50 rows).

## Prediction P5 (ingest of the 24 additions, then tags, vectors, check)

- 24 ingested, papers 710 -> 734; grp and priority from the additions file; titles from the arXiv
  API (title_source arxiv-api) through the metadata load at the end of `kb ingest arxiv`.
- Status: at least 20 ok; a few review possible (a long review chapter, 2406.11417; a math paper
  without abstract environment) [JUDGEMENT]. None failed.
- Every one of the 24 has bibliography entries and no cited key without an entry for more than 10
  per cent of its keys; the TeX papers without an entry stay 6.
- `kb embed --check --work` afterwards: 0 missing, 0 stale, 0 orphaned.
Refuted by: a failed parse, a paper without entries, a grp other than the file's, or vectors missing.
