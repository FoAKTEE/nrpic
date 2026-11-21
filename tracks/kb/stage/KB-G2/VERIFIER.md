# KB-G2: report of the independent verifier

Verifier: helper `verify_g2` of kb (wave 3; started 2026-11-20, finished in batch 2b on
2026-11-21). Given the artefacts and the criteria, not the conclusions. Until this file was
committed I did not open tracks/kb/stage/** (other than writing this file and its KB-G0 twin),
the lead's STATUS/HANDOFF/JOURNAL/RISKS/PLAN-wave3, kb/QA_REPORT.md, kb/STATE.json,
tracks/kb/{retrieval,pdf_meta,claims}/**, the outbox of kb or scratch/orch. The QA output of
the named run kb-20261119-161633-1d05960 was read only after my own retrieval and parse numbers
were committed (journal entry 10, commit c2ccdc3d), for C2.

Object: the frozen snapshot `kb-data/db/kb-20261119-a782f1e.sqlite`, opened with
`mode=ro&immutable=1` or passed as `--db`. Nothing was written to kb-data. All numbers come from
registered runs (run ids below; outputs under `scratch/kb/<run_id>/`); the working notes are
`tracks/kb/verify_g2/JOURNAL.md` (entries 0-13), the code `tracks/kb/verify_g2/scripts/`.

## Verdicts

| Criterion | Verdict | My numbers | Runs |
|---|---|---|---|
| C1 all papers and repositories ingested | **CONFIRMED** | 710 of 710 manifest ids (684 + 26 additions), 0 extra, group and priority equal; 64 of 64 repositories (63 + local/nrpic), each with a 40-hex commit and files | kb-20261121-080038-306bcdd |
| C3 parse success >= 95 % | **CONFIRMED** (narrowly, under my definition) | recorded status ok: 684/710 = 96.3 %; my definition (sections, equations, bibliography, abstract available; gaps read at the source subtracted): 679/710 = 95.6 %; strict variant (abstract chunk extracted from the source): 658/710 = 92.7 % | kb-20261120-223309-14e4cb6, kb-20261121-080834-6c50215, kb-20261121-080843-98907be, kb-20261120-223339-b842a8a |
| C4 retrieval >= 80 % of golden questions, right paper in top 10 | **CONFIRMED** | golden 32: text 27 (84.4 %), hybrid 28 (87.5 %), rerank 28 (87.5 %); my blind held-out 24: text 21 (87.5 %), hybrid 22 (91.7 %), rerank 21 (87.5 %). Location (not gating, 200-char slack): golden 65.6 / 71.9 / 78.1 %, held-out 54.2 / 62.5 / 58.3 % | kb-20261121-074940-08426cc, kb-20261121-080557-06d44ba, kb-20261120-222546-ea894c8, kb-20261121-075156-b84a189 |
| C2 the QA report meets C3 and C4 | **CONFIRMED** (with a remark) | the report of kb-20261119-161633-1d05960 gives 27/28/28 of 32 and locator 21/23/25, identical to my recomputation, and 26 papers not ok (684/710 = 96.3 %); it states no parse rate against the 95 % bar | as C3, C4 |
| C5 read-only by default; snapshots 0444 | **CONFIRMED** | 9 of 9 snapshot files 0444; readers default to db/current (help text, `open_for_read`, and a dynamic test in a fake data root); readers open `mode=ro` | kb-20261121-080038-306bcdd |
| C6a `kb snapshot` at the end of the stage, id recorded | **CONFIRMED** | sha256 of the file starts with a782f1e; taken as the last step of kb-20261119-161451-e15d1b8 (16:16:18Z), the QA run used it (16:16:34Z) and names it | kb-20261121-080038-306bcdd |
| C6b locators carry the snapshot id | **WRONG** (partly met) | the answer of `kb search`, `kb eq`, `kb code` names the database file once (text footer; JSON `info.database`); no hit carries it; `kb show` and `kb cites` print no snapshot id | kb-20261121-080038-306bcdd |
| C9 null results and failed runs on record | **CONFIRMED** (manifests) | 2 kb manifests with status failed (kb-20261115-182907-3f69615, kb-20261119-143242-737909d); ingest_log of the snapshot: 2 ingest-arxiv failed, 63 review, 5 skipped rows. Journal part: addendum below | kb-20261121-080038-306bcdd |
| Package documents, currency of STATUS | NOT CHECKED | the lead's | |

## Defects (most important first)

1. **parse_status "ok" does not mean the paper is usable for citations and locators.** 21 of the
   684 papers with status ok fail my definition (tally kb-20261121-080843-98907be): 13 have a
   bibliography in the source but none (or less than half) in the database, e.g. 0710.5073
   (REVTeX-3 `references` environment, 28 `\bibitem` at backreaction2prdrv.tex:587-705;
   database 0 entries), 1005.4054 (79 `\bibitem`, 17 entries), 1201.4794 (AAS `\reference{}`
   list, flat.tex:1022 ff.; 0), gr-qc/0304002 (`\def\bi{\bibitem}`, flat.tex:22; 0); 7 have
   fewer than half of the display equations I count (1408.1695, 1508.05610, 1709.00267,
   1901.04498, 2405.10692, 2410.17291, astro-ph/0702575); hep-ph/9809574 has five numbered bold
   headings (`{\bf I. Introduction}`, flat.tex:85-437) and no section row. Ten papers have
   citation rows but no bibliography entry at all (counts.json of kb-20261121-080624-467030c), so
   "who cites whom" cannot be answered from the entries for them. Conversely 13 review and 3 pdf
   papers are usable. The QA report's cause classes do not include "bibliography missing".
2. **Old styles lose their structure.** Five review papers in plain TeX or old macro sets have
   numbered headings and reference lists that the database lacks entirely (0 sections, 0
   bibliography entries): astro-ph/0306304 (`{\bf I. Introduction}` main.tex:56, `\item` list
   after main.tex:696), astro-ph/9306009, astro-ph/9510056 (A&A `\titlea`/`\titleb`,
   flat.tex:1897-2260; `\begref` with `\ref` entries from 2511), gr-qc/9604001, gr-qc/9906015
   (`{\rma 3.1. ...}` main.tex:599; 21 `\ref` lines after 1250); also astro-ph/9607124
   (numbered list after "References", flat.tex:421; 0 entries). With these, the C3 margin is
   4.5 papers.
3. **C6b**: per-hit locators (paper vN, `file:Lnn-mm`, chunk id, character range) do not carry
   the snapshot id; chunk ids and character ranges change with a re-ingest, so a note that
   copies a hit without the footer cannot be traced. `kb show` and `kb cites` print no id.
4. **Abstracts**: 25 papers have no abstract chunk (21 of the 23 review papers; e.g. 2009.08715
   `{\bf Abstract}` at HDR.tex:223, 2509.01320 `\section*{Abstract}` at line 108). The metadata
   abstract is served by `kb show --abstract` (8 of 8 tried, word recall 1.0), so a reader gets
   it, but the extracted-abstract check of brief 12.4 step 8 is not met for them.
5. **Retrieval misses**: golden q12 (2609.14218, eigenvalues of the deformation tensor) is
   missed in all three modes, q11 (same paper) in text and hybrid, q13 (2512.14649) in hybrid
   and rerank; held-out H20 (1204.2019) in all modes. Answer-location hits are 54-78 %.
6. **Code index**: 24 of the 64 repositories have a file inventory but no code chunks (no
   full-text code index; 19 of them have symbols, 5 none), e.g. kokkos/kokkos, AMReX-Codes/amrex,
   hannorein/rebound. C1 as worded (commit and files) is met; brief 12.7 asks for chunks.
7. Minor: the raw store is read-only by convention only (736 source.bin with mode 0664; one
   Unix user for all sessions); 26 directories of raw/arxiv are not in the snapshot (fetched
   after it; not examined).

## Test 1: blind held-out set (step 1)

24 papers drawn from the 710 of the snapshot with seed 20261120, one slot per group (21) and
three more by group size, priority quotas 4 x p3, 7 x p2, 13 x p1 (run
kb-20261120-222100-50182fe; 21 groups covered, one review paper). For each I read the source
and wrote one question in my own words whose answer is a specific passage (10 numbers, 11
methods, 2 definitions, 1 provenance), with the locator as file:line of the source:
`tracks/kb/verify_g2/heldout.yaml`, committed as **8fb37106** at 22:24:05Z on 2026-11-20,
before the first search (run kb-20261120-222546-ea894c8 started 22:25:46Z at ea894c8) and
before I opened kb/golden/questions.yaml. Nobody tunes retrieval on it.

## Test 2: retrieval (C4)

`kb search QUERY --db <snapshot> -k 10 --json` in `--text-only`, `--hybrid`, `--rerank`
(4 threads), called as a reader would (scripts/run_search.py); my own scorer
(scripts/score_search.py) and my own map from source lines to flat.tex characters
(scripts/locmap.py: each comment-stripped source line located verbatim in flat.tex). Paper hit
= expected id among the 10 hits. Location hit = a hit of the right paper whose
[char_start, char_end) overlaps the expected range widened by 200 characters on each side
(about two source lines); strict overlap is reported too. All 24 + 37 expected ranges were
mapped; my map and the tool's sourcemap.json agree on every start offset but one (golden q05,
15 characters); every flat.tex matches papers.flat_sha256 of the snapshot.

| set | mode | paper hit | rank 1 | location strict | location slack |
|---|---|---|---|---|---|
| held-out (24) | text-only | 21 (87.5 %) | 14 | 12 (50.0 %) | 13 (54.2 %) |
| held-out | hybrid | 22 (91.7 %) | 14 | 15 (62.5 %) | 15 (62.5 %) |
| held-out | rerank | 21 (87.5 %) | 14 | 13 (54.2 %) | 14 (58.3 %) |
| golden (32) | text-only | 27 (84.4 %) | 20 | 20 (62.5 %) | 21 (65.6 %) |
| golden | hybrid | 28 (87.5 %) | 17 | 23 (71.9 %) | 23 (71.9 %) |
| golden | rerank | 28 (87.5 %) | 19 | 25 (78.1 %) | 25 (78.1 %) |

The held-out rates equal or exceed the golden ones: no sign that retrieval was tuned on the
golden set (my prediction R2 expected the opposite and was refuted). Figure
`tracks/kb/verify_g2/figures/fig_ranks.png` (run kb-20261121-080624-467030c): rank of the right
paper and of the first location hit per question, three modes, both sets.

## Test 3: parse success (C3)

**Definition** (decided for the four kinds of question of brief 12.1). A paper is parsed
successfully when a reader can (S) give section locators: the database has >= 1 section, or the
source has no section headings of any form; (E) find its equations: >= 1 equation and at least
half of the display equations I count (environments, `\[ \]`, `$$`, shorthand macros), PDF-only
papers exempt; (B) answer "who cites whom": when the paper cites (by `\cite` or by a reference
list), the database has >= 1 bibliography entry, at least half of the entries of the source
(.bbl, else the cited keys of the .bib, else `\bibitem`), and >= 1 citation row; (A') read the
abstract: an abstract chunk, or the metadata abstract that `kb show --abstract` serves. The
strict variant replaces A' by A (an abstract chunk with >= 50 % of the metadata's words).
[JUDGEMENT] A letter whose only headings are run-in labels ("Introduction.--") has no sections
to lose; nine such letters count as parsed.

**Scan** of all 710 papers with my own regular expressions (kb-20261120-223309-14e4cb6; a first
scan, kb-20261120-222948-fcdd5e7, is superseded and kept: it counted uncited .bib entries and
missed biblatex). **Source check** of 15 papers drawn with seed 20261121, 5 not ok
(kb-20261120-223339-b842a8a), read at the source: every failure verdict was a real gap, but my
S and B passed two plain-TeX papers whose numbered headings and reference lists are not in the
database. **Leniency check** of all papers that pass only because they have no sectioning
command or no `\cite` (kb-20261121-080834-6c50215: 37 papers examined, 17 with headings or
lists): nine genuine gaps read at the source (defects 1 and 2). **Tally**
(kb-20261121-080843-98907be):

| measure | papers | rate |
|---|---|---|
| recorded parse_status ok | 684 | 96.3 % |
| ok or pdf | 687 | 96.8 % |
| mine (S, E, B, A'), gaps subtracted | **679** | **95.6 %** |
| the same with the nine letters counted as failures | 670 | 94.4 % |
| strict (abstract chunk), gaps subtracted | 658 | 92.7 % |

Components over 710 before the gap correction: S 709, E 701, B 696, A 680, A' 710. Cross-tab of
status against my definition: ok-pass 663, ok-fail 21, review-pass 13, review-fail 10, pdf-pass
3. The bar is 674.5 papers; under my definition it is passed by 4.5 papers, so the verdict is
CONFIRMED but fragile: a stricter reading of letters, or the strict abstract test, fails it.
Figure `tracks/kb/verify_g2/figures/fig_parse.png`: pass fractions of S, E, B, A, A' by status,
and my counts of display equations and bibliography entries against the database's.

## Test 4: counts (C1)

Run kb-20261121-080038-306bcdd (checks.json): kb/manifests/arxiv.tsv (684 rows) and
github.tsv (63) equal kb-data/manifests; their sha256 and the brief's equal SOURCE.json; each of
the 684 + 63 rows is found, by code, in the brief line SOURCE.json names (I did not read those
lines). Expected 684 + 26 = 710 papers: 710 present, none missing or extra, no duplicate,
group and priority equal for all; each has chunks and a raw source file, each of the 707 TeX
papers a flat.tex; 43 560 of 43 560 non-comment chunks have a vector
(bge-small-en-v1.5@5c38ec7). Repositories: 64 expected, 64 present, each with a 40-hex commit
and >= 46 files.

## Test 5: read-only access and snapshots (C5, C6)

Same run. Modes: the 9 snapshots kb-2026111{5,9}-*.sqlite are 0444, kb.sqlite 0644, `current`
-> kb-20261119-a782f1e.sqlite. Static: `kb search|show|eq|cites|code|frontier|export --help`
say "default db/current, else kb.sqlite"; kbtool/db.py `open_for_read` returns db/current when
it exists and `connect_ro` opens `mode=ro`. Dynamic, in a fake data root under the run
directory (KB_DATA_ROOT, KB_LOCK): `kb init`, a row with a marker word, `kb snapshot` (new file
0444, sha prefix = name), a second marker added to kb.sqlite only; `kb search` without --db
finds the first marker (1 hit) and not the second (0 hits; 1 hit with --db kb.sqlite), and the
snapshot's bytes are unchanged. Snapshots: the sha256 of all 9 files starts with the 7 hex
digits of the name; ingest_log of a782f1e holds the 8 earlier snapshot rows and, by design
(kbtool/db.py:192-195 writes it into kb.sqlite after the copy), not its own; its last row is
16:16:02Z inside the snapshot run. My searches left kb-data/db and kb-data/logs unchanged
(listing before and after the golden run, journal entry 10).

## Not checked

- The fidelity of arxiv.tsv to the manifest of brief section 17 beyond the id-in-line check
  (my task let me read only brief lines 1218-1461).
- Bibliography resolution (target ids, confidence), the citation graph and `in_corpus`; the
  correctness of equation content (tex_norm, tags); figure records.
- Section extraction beyond ">= 1 section" (one paper, 2209.06775, has fewer than half of its
  sectioning commands as sections; not read).
- The code index beyond counts (symbols, chunks, the params table).
- The working database kb.sqlite (not opened, as instructed); hence the snapshot's own
  ingest_log row.
- The 26 raw/arxiv directories that are not in the snapshot.
- The golden set's answer locators as answers (taken as given; only mapped).
- Whether tracks use the knowledge base read-only in practice (only the default and the modes).
- The package documents and the currency of STATUS (the lead's).

## Requests

To the kb lead:
1. Add "bibliography missing or under half of the source" and "citation rows without entries"
   to the parse quality and the QA report's cause classes; fix the four forms seen here:
   REVTeX-3 `references` environment, `\bibitem` aliases (`\def\bi{\bibitem}`), macros that
   emit `\bibitem` (`\sortbibitem`), AAS `\reference{}` lists.
2. Recognise headings of old styles (`{\bf I. Introduction}`, A&A `\titlea`/`\titleb`, plain
   TeX font headings) as sections, and numbered reference lists without `\cite`.
3. Print the snapshot id in `kb show` and `kb cites`, and put it into every JSON hit (or the
   locator string), so a copied locator stays traceable.
4. State the parse success rate and its definition against the 95 % bar in the QA report; my
   definition and counts are in tracks/kb/verify_g2/ (tally.json of kb-20261121-080843-98907be).
5. Use `tracks/kb/verify_g2/heldout.yaml` only as a held-out check; do not tune on it.

## C9 addendum (written after the verdicts were committed)

Pending: the journal part of C9 is read only after this file is committed.
