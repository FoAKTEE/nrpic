# Package ingest3 (kb, wave 3 batch 6): bibliography formats, claim-safe re-ingest, additions

Helper package of kb, 2026-11-21 (21:14-22:30 UTC). Brief: tracks/kb/PLAN-wave3.md round 1 as
restated in the batch-6 task. Predictions and outcomes: `JOURNAL.md` (P1-P11). No card was used.
Numbers below carry their run id; outputs are under `scratch/kb/<run_id>/`.

## What is here

| Path | What |
|---|---|
| `ids/zero20.txt`, `ids/additions24.txt`, `ids/frontier11.txt`, `ids/redo31.txt` | the paper lists of the package (redo31: papers the definition-skip and alias changes alter, from the all-paper dry run) |
| `scripts/kbstate.py` | read-only counts per paper and over the database, and every claim touching the listed papers (`--tag`) |
| `scripts/fig_before_after.py` | the two figures and `BEFORE_AFTER.tsv` from kbstate outputs |
| `scripts/compare_dry.py` | a dry-run parse of every paper against the database rows: what a re-ingest would change |
| `scripts/figstyle.py` | byte copy of harness/style/figstyle.py |
| `BEFORE_AFTER.tsv` | per paper of the 20: status, source, entries, citation rows (all and with an entry), sections, equations, chunks, claim rows, before and after; then the 35 additions after |
| `figures/fig_bib_before_after.png` | entries and citation rows per paper of the 20, before and after |
| `figures/fig_parse_status.png` | parse-status counts and success rates at three states, with the 95 % bar |
| `JOURNAL.md` | predictions P1-P8 and outcomes |

Code (committed in kb/, commits 776288ad and d67628eb; tests in the full suite):

| File | Change |
|---|---|
| `kb/kbtool/tex_structure.py` | `command_aliases`: macros that stand for `\bibitem` or `\cite`, found from their definitions (bare `\def\bi{\bibitem}`; a body passing argument k as the key: `\bib[1]{\bibitem{#1}}`, `\sortbibitem[2]{...\bibitem{#1} #2...}`, `\refto[1]{Ref.~\cite{#1}}`); `xparse_macros` reads `\NewDocumentCommand` with mandatory arguments (pandoc's `\citeproc`); citation commands through aliases; `references`, `thereferences`, `CSLReferences` start the bibliography region when they hold entries; `scan_math` skips macro definitions written inside the document body (d67628eb: `\newcommand\be{\begin{equation}}` in the body had opened an equation inside its own definition) |
| `kb/kbtool/bib_parse.py` | entries `\bibitem`, `\harvarditem[.]{authors}{year}{key}`, AASTeX `\reference` (keys `#1`, `#2`, ...); reference-list environments as above; alias expansion; a `.tex` the main file does not reach, used only when the paper cites and has no entry (`parse_json.bib_unreached_file`); cited keys and keys with an entry |
| `kb/kbtool/papers_ingest.py` | review rule: a paper with `\cite`-family commands and no entry gets `parse_status` review, reason in `parse_json.review_reasons`; `store(..., remap_claims=True)` runs the remap in the paper's lock hold and transaction (build files restored on rollback) |
| `kb/kbtool/claims_remap.py` (new) | after a re-ingest, each locator row of the paper gets its flat range from (file, line_start, line_end) through the new source map and its chunk ids from that range (as `claims_check.Store` resolves); the old range is kept only when the lines do not map and flat.tex is byte-identical; claims.chunk_id and the quote range follow the first resolved row (rule of `claims_db.upsert_seed`); a claim with a chunk in the paper and no row is carried through the old and new source maps; one `claim_events` row (action `remap`) per claim; labels and statuses untouched |
| `kb/kbtool/papers_cli.py` | `kb ingest arxiv ... --remap-claims [--out DIR]` (report `remap.json`), `--dry-run --out DIR` (per-paper summaries, no database or build write) |
| `kb/tests/test_bib_formats.py`, `kb/tests/test_claims_remap.py` (new) | 14 and 2 tests on synthetic snippets: each format, aliases, xparse, unreached file, review rule end to end, dry run; remap through a shifted flat.tex checked against an independent resolution, the identical-flat case, and the control that a plain re-ingest leaves a dangling chunk |

Also `kb/manifests/arxiv_additions.tsv`: 35 rows (commits 02c76737, 070308fa) and the message
`tracks/kb/outbox/20261121T220221Z__to-orch__additions-wave3.md`.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
(cd kb && .venv/bin/python -m pytest -q tests/test_bib_formats.py tests/test_claims_remap.py)
S="python3 -I tracks/kb/ingest3/scripts/kbstate.py --db /data/haiyangw/nrpic/kb-data/db/kb.sqlite"
$S --ids tracks/kb/ingest3/ids/zero20.txt --out <dir> --tag state           # read-only
ids=$(sed 's/^/--id /' tracks/kb/ingest3/ids/zero20.txt | tr '\n' ' ')
kb/.venv/bin/python -I kb/bin/kb ingest arxiv $ids --jobs 4 --dry-run --out <dir>   # nothing written
kb/.venv/bin/python -I kb/bin/kb ingest arxiv $ids --jobs 4 --remap-claims --out <dir>
kb/.venv/bin/python -I kb/bin/kb eq --apply-tags && kb/.venv/bin/python -I kb/bin/kb embed --threads 4
kb/.venv/bin/python -I kb/bin/kb embed --check --work
kb/.venv/bin/python -I kb/bin/kb claim check --id 171 172 ... 186     # seeds only; served: rows are not checked
python3 -I tracks/kb/ingest3/scripts/fig_before_after.py --before B.json --reingest R.json --final F.json --dry <dry dir> --out <dir>
```
Every command above ran under `harness/bin/nrpic-run submit --package tracks/kb/ingest3` (runs below).

## Results

| Step | Run | Result |
|---|---|---|
| 1 baseline | kb-20261121-212037-0b37880 | 710 papers: ok 684, review 23, pdf 3; 20 TeX papers without an entry (11 ok); ok with citation rows and no entry 9 (not 10: gr-qc/0304002 cites through `\ct`); recorded rate 96.34 %, strict 95.07 %; 21 claims touch the 20 (171-186 on 2403.15126, 658-662 on 1201.4794) |
| 2 dry run | kb-20261121-213314-f5e7cc2 | entries equal the lead's item counts (1201.4794 46, 2507.01095 103, gr-qc/0304002 38, gr-qc/9703066 18, 2602.00155 28) and zero_bib.tsv's REVTeX-3 counts; 2403.15126 117; every cited key has an entry in all 14; 6 stay at zero |
| 4 re-ingest of the 20 | kb-20261121-213423-d6e666c | 11 ok, 9 review as before; entries +680, citation rows +87 (58 gr-qc/0304002, 29 2602.00155); remap: 21 claims, 20 locator rows moved to new chunk ids, flat.tex byte-identical |
| 4 tags, vectors, resolve | kb-20261121-213521-2b80ade | 935 equations re-tagged; 796 chunks, 935 equations embedded, orphans deleted; check 0 missing/stale/orphaned |
| 4 claim check | kb-20261121-213832-67fadc6 | `kb claim check --id 171..186`: "same 16"; rows, chunk ids, quote ranges equal the remap's for all 21 claims; 0 dangling chunk references; zero-bibliography TeX papers 6, none ok; strict rate = recorded = 96.34 % |
| 5 metadata of the 24 | kb-20261121-214115-b07a4a7 | arXiv-API and INSPIRE records ok for 24 of 24 |
| 5 ingest of the 24 | kb-20261121-214253-c459325, kb-20261121-214344-a576394 | 24 ok, all with entries; vectors check 0/0/0; 734 papers, ok 708 (96.46 %) |
| 6 frontier 11 | kb-20261121-215209-964397e, kb-20261121-215402-46415c8 | 11 sources and metadata ok; 11 ingested ok; 745 papers |
| 7 QA | kb-20261121-215613-421a104 | 745 of 745 manifest ids ingested; ok 719, review 23, pdf 3: recorded rate 96.51 %, strict ("ok, cites, no entry" a failure) 96.51 %, with pdf 96.91 %; golden questions (32): hybrid paper 28/32 (87.5 %), location 23/32 (71.9 %); rerank 28/32 and 25/32; text 27/32 and 21/32 (unchanged); 67821 entries, 109207 citation rows, 14704 in corpus |
| 8 figures (first) | kb-20261121-220205-1dbcd51 | superseded by the final figures below |
| all-paper dry run | kb-20261121-220637-9f109de | 33 of 725 papers not re-ingested today would change: 14 gain cited keys (citation macros), 3 gain entries (`\bibitem` aliases), 13 lose 1-3 equation rows each (27 rows, every one macro-definition text, which had taken numbers 1-3 and shifted the later numbers); none loses entries or sections (the 3 PDF-only papers are not handled by `kb ingest arxiv`, an artefact of the comparison) |
| redo of 31 | kb-20261121-221427-6d5b50d, kb-20261121-221440-2fd53d7 | 30 papers above and astro-ph/0003278 re-ingested with --remap-claims: equal to the dry run for all 31; astro-ph/0003278 review -> ok (13 sections, 33 equations, 33 entries); claims 407, 606, 607 remapped, `kb claim check` "same 3"; 0 dangling; vectors 0/0/0 |
| final QA and state | kb-20261121-222222-28b1c1b | 745 papers: ok 720, review 22, pdf 3; recorded rate 96.64 %, strict 96.64 %, with pdf 97.05 %; golden hybrid paper 28/32 (87.5 %), location 23/32 (71.9 %); rerank 28/32, 25/32; text 27/32, 21/32; 67865 entries, 109730 citation rows, 14810 in corpus; 0 dangling chunk references |
| final figures | kb-20261121-222623-32b3c1e | `figures/`, `BEFORE_AFTER.tsv` (both PNGs looked at) |

The database is updated (kb.sqlite); no snapshot was taken (the lead takes it). Readers on
`db/current` still see kb-20261119-a782f1e until then.

## Failed predictions (all in JOURNAL.md)

- P1: 9, not 10, ok papers with citation rows and no entry (strict rate 95.07 %, not 94.93 %); 21
  claims touched the 20, more than the 0-10 I guessed.
- P2: 2602.00155 has 29 `\citeproc` commands for 28 keys (I wrote 28 citations).
- P3: sums: +680 entries (I wrote +746, a wrong addition) and +87 citation rows (I counted commands, 84).
- P7: the explicit `kb resolve-bib` after the QA changed nothing: `kb ingest arxiv` already ends
  with the corpus resolution.
- P8: 12, not 14, papers cite (two have entries but no `\cite`).
- P9 held only narrowly: 33 of 725 other papers change (4.6 % against my 5 % bound).

## Open items

1. Six old-style papers without any recognised list (astro-ph/0306304, astro-ph/9306009,
   astro-ph/9510056, astro-ph/9607124, gr-qc/9604001, gr-qc/9906015): "References" headings with
   `\item`, `\ref`, `\refh` paragraphs and no `\cite`; plain-TeX `\eqno` numbers and `{\bf I. ...}`
   headings. Status review; not done in this package (optional in the brief).
2. Done after all: astro-ph/0003278 (definitions in the body made the whole body math); fixed
   (d67628eb) and re-ingested with the 30 other papers the change alters.
3. The QA report (qa_*.py, not this package's code) states no rate against the 95 % bar; the
   rates are above and in fig_parse_status.
4. Claims of the `served:` kind (658-662) are not reached by `kb claim check`; their remap was
   checked only through the remap's own rule and the equality of their rows with an independent
   resolution in the test, not by a check command on the live rows.
5. Snapshot (lead), then the C6b item (snapshot id in `kb show`, `kb cites`, JSON hits), which
   waited for this package's papers_cli.py.

## Requests

- kb lead: `kb/tests/test_meta_papers.py::test_additions_file_is_valid` hard-codes the additions
  (`len(rows) == 26`, `684 + 26`, `710`); with the 35 rows of this package it fails. Change to 61,
  `684 + 61` and 745 (that file is outside this package's files, so I did not edit it). Every other
  test of the kb suite passes.
- kb lead: take the snapshot; carry the six old-style papers into a later package (item 1); add the
  parse rate against the bar to `kb qa run` (item 3, qa_report.py).
- orch: information message on the 35 additions (outbox 20261121T220221Z__to-orch__additions-wave3.md);
  a reply only if a group should change.
