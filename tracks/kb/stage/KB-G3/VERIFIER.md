# VERIFIER report: gate KB-G3 of the knowledge base (kb), 2026-11-24

Verifier: a fresh kb helper session (batch 11) that did not write any of the packages checked.
Gate criterion (brief 12.10): "every statement in the evidence queue that bears on G1 of the
six tracks has been processed". Material checked: the claims of packages `claims_tracks` and
`claims_brief`, ingest3's bibliography, the code index (`code_kb`), and the parse rate, all on
the frozen snapshot `kb-data/db/kb-20261121-aa0a2ae.sqlite` (the target of `db/current` on
2026-11-24). Own code in `verifier/scripts/`, predictions committed before any draw
(`verifier/JOURNAL.md` entry 1, commit 2e05c967, seed 20261124), registered runs listed per item.
Verdict words: CONFIRMED (my own reading or computation agrees), NOT CONFIRMED (I could not
reproduce it, or it holds only in part), WRONG (my reading contradicts it), NOT CHECKED.
Independence: I read the lead's batch-9 review section (REVIEW-wave3.md from L105) for the
list of what is claimed; it also carries the lead's "Confirmed" lines, which I saw. Every
number below is recomputed by my scripts or read by me at the source.

## Summary

| Item | What was checked | Result | Verdict |
|---|---|---|---|
| 1 | 60 claims, stratified by status and track, re-read at their locators | 54/60 correct = 90 % (95 % CP 79.5-96.2 %); population estimate weighted by cell sizes 93.8 % (s.e. 3.5 %) of the 810 claims in the four strata | CONFIRMED for the tracks' queue; NOT CONFIRMED for the brief's open to_verify seeds |
| 1a | S1 fulltext/checked (18) | 17 supported; 682 misworded (one number given to the wrong distribution) | CONFIRMED (one WRONG claim text) |
| 1b | S2 fulltext/located by machine (18) | 17 supported; 85 a fragment with no statement | CONFIRMED |
| 1c | S3 to_verify (12) | 8 processed correctly; 4 brief seeds left untouched although the store settles them (781, 714, 809, 804) | NOT CONFIRMED |
| 1d | S4 judgement/background (12) | 12 correct; every annotation I followed says what it claims | CONFIRMED |
| 2 | refutations: 11 brief seeds, 24 printed defects, 20 superseding claims | seeds 10 confirmed (5 qualified), 1 not confirmed (737); defects 19 confirmed, 5 not checkable here; superseding 12 confirmed, 2 partly, 6 not checked; 0 wrong | CONFIRMED, except 737 |
| 3 | ingest3's twenty papers, ten cited keys each (140) | entry present 140/140, same reference 140/140; printed identifiers resolved 33/54 (61 %, CP 47-74 %), 21 missed, 0 wrong; 6 papers have a reference list the parser misses | entries CONFIRMED; identifiers NOT CONFIRMED |
| 4 | code index at 47ab19ab: 10 parameter reads, 10 paper-code links | 10/10 and 10/10 | CONFIRMED |
| 5 | parse rate by my own definition | 714/744 = 95.97 % (recorded "ok" 719/744 = 96.64 %) | CONFIRMED above the 95 % bar, by a margin of 7 papers |

Runs: draws kb-20261124-130442-e69c2e8; parse rate kb-20261124-130450-578a535; arithmetic and
bibliography tally <RUN_BIB>; tally and figures <RUN_TALLY>. Figures (looked at):
`verifier/figures/fig_sample.png`, `fig_refutations.png`, `fig_bib.png`, `fig_parse.png`.

## 1. Stratified sample of 60 claims

Population (snapshot, 861 claims): S1 fulltext+checked 225, S2 fulltext+located 464,
S3 to_verify 38, S4 judgement or background 83; not sampled: refuted 35 (item 2 takes them
all) and abstract 16. Allocation 18/18/12/12, by track in proportion with at least one per
track (`allocation.json` of the draw run). Each claim was read at every locator row in the
raw source (`scripts/show_claim.py`), the full line where the stored one was cut; one row per
claim with the deciding lines in `verifier/verdicts/sample_verdicts.tsv`.

| Stratum | correct / n | 95 % CP | N |
|---|---|---|---|
| S1 fulltext, checked | 17/18 | 72.7-99.9 % | 225 |
| S2 fulltext, machine-located | 17/18 | 72.7-99.9 % | 464 |
| S3 to_verify (processing right) | 8/12 | 34.9-90.1 % | 38 |
| S4 judgement/background (processing right) | 12/12 | 73.5-100 % | 83 |
| all | 54/60 | 79.5-96.2 % | 810 |

Findings:
- **682 (D, S1) WRONG as worded.** 1305.2619 SFWpaper.tex L443 says the Gondolo-Silk spike is a
  factor of three below the relativistic one and that the *4Gm variant* peaks about 15 per
  cent above it; the claim gives the 15 per cent to the Gondolo-Silk distribution, and says D
  read 2.59 and 9.2 per cent off Fig. 1, which the kb's own verify event contradicts (computed
  in run D-bh-dress-20261115-145636-5259f48). The label fulltext/checked endorses this text.
- **85 (A, S2)** is the fragment "and L550-563"; the kb's audit had named it.
- **S3: the tracks' to_verify claims are processed well** (9, 413, 414, 416, 687, 538: each
  reason confirmed: no boundary condition in MDPBH.tex by my search; the D commits are
  ancestors of main; the run file holds slope -2.25033; etc.). **Four of the six drawn brief
  to_verify seeds are unprocessed although the store answers them**: 781 (2611.12831
  main.tex L75 "Particles and fields share a common global time step"), 714 (no "cosmolog" or
  "periodic" in 2611.12831 main.tex; FLRW only as the OS interior, L867, L877), 809 (INSPIRE
  records stored for 4 of the 8 ids), 804 (an umbrella item whose parts are located in claims
  370 and 854/855). claims_brief says these 30 seeds have no CHECK.md row; that is accurate,
  but for KB-G3 they are not processed. Scaled to the 19 open brief to_verify seeds, about
  13 would be settleable from the store [JUDGEMENT; 4/6 has a wide interval, 4-18].
- **S4:** every annotation I followed is accurate (425: a_b = 9.9 is d/M of
  massratio_table.tex L21 over the binary mass, derived rather than printed).
- Label strength: three S1 claims (448, 753, 765) are fulltext on an abstract or title line
  inside the TeX source; they are supported, but "fulltext" there means less than its name.

## 2. Claims that refute a statement of the brief or of a cited paper

All 35 refuted claims and the 20 claims that supersede them; each rederived from the source
(`verifier/verdicts/refutations.tsv`, arithmetic in <RUN_BIB> `arith_checks.json`).
No claim in 1-700 is labelled refuted (claims_tracks refuted none; my sample found none it
should have refuted except 682's wording).

- Brief seeds, 10 of 11 CONFIRMED: 742 (2508.10070 L80, L767: beta ~ sigma^5 with sigma a
  standard deviation, so the variance to the 5/2, not the 5th power), 749 (2505.21885 L65,
  L125, L147, L181: the two GW peaks do not result from the accretion; EMD by a scalar, PBHs
  subdominant), 752 (1706.09501 L76, L109, L112: no proof of Burnett's conjecture), 756 and
  802 (2611.12831 L42-44: full NR of black holes forming and merging in a collisionless
  envelope), 718 (three table characterizations: gevolution has a hyperbolic h_ij equation,
  1604.06065 L487; 2003.08014 compares four codes of different kinds, L285-327; 1611.03437
  is a fluid scheme, L41, L248, L330), 738 (r_crit >~ 5.6e-6, a factor 5.6 above "about 1e-6",
  which the paper's own abstract prints), 766, 767 (one misfiled id each), 782 (1505.02959 does
  numerical work on the averaged limit). Qualified: 738, 766, 767, 782, 802 refute a long
  statement for one item; the claim text alone does not say which part is wrong (718 is
  the table's disclaimer sentence).
- **737 NOT CONFIRMED as a refutation**: 2606.02712 L205, L559, L798: z0 = -0.4 (+0.8/-0.9)
  per cent is compatible with zero, as the brief says, and also with the void value 0.84 per
  cent; the sentence is incomplete and misleading, not false. A correction, not a refutation.
- Printed defects, 19 of 24 CONFIRMED by my own derivation or reading: 813 (C = M/R misprinted
  twice, 1.141e-2 and 4.010e-3), 815 (the printed e^{2 Phi} has a positive exponent without the
  factor 2), 816 (g_tt = -alpha^2 at L231, so 1 + Z = 1/alpha(0)), 818, 820, 822, 824 and 826
  (the two lines of the printed FFT normalisation disagree: dk^(3/2) against
  dk^(3/2) (2 pi)^(-3/4)), 828 (likelihood ratio of the biased Langevin process has the
  opposite sign), 830 (3 Mpl^2 missing), 836 (the canonical radial action divides by
  1 - 2Gm/r), 842, 843, 846, 848, 850, 852, 854 (15 M_sun at 100 MeV, not 1), 856.
  NOT CHECKED: 829, 832, 834, 838, 840 (they rest on a track's computation or a figure).
- Superseding claims: 12 CONFIRMED, 823 and 837 partly (the defect confirmed, the stated size
  of its effect not recomputed), 825, 827, 833, 835, 839, 841 NOT CHECKED.

## 3. Bibliography of ingest3's twenty papers

Ten cited keys per paper from my own reading of the raw source (aliases \ct, \bib,
\sortbibitem, \citeproc found from their definitions; AASTeX keys #k by my count of
\reference), drawn with the seed (draw run, `bib/`); verdicts in
`verifier/verdicts/bib_verdicts.tsv`.
- 14 papers have entries, 6 none, as ingest3 states. For the 140 drawn keys the entry exists
  (140/140) and its text is the source's entry (140/140).
- Identifiers: of the 54 drawn entries that print an arXiv id or a DOI, 31 carry that id,
  2 carry the right arXiv paper found by title, **21 carry nothing**: hep-ph/0011159 prints
  "[HEP-PH 9610477]" (8 of 10 drawn), 2403.15126 uses \arXiv{id}{class} (8 of 10),
  2602.00155 prints DOIs in \url{https://doi.org/...} (5 of 10). No drawn target is wrong.
- Over the whole snapshot by the same test (<RUN_BIB>): 67861 entries; 52725 print an
  identifier; 4538 of them (8.6 %) carry no target, 2 a different one. A seeded sample of
  20 of the 4538 is 20/20 genuine (DOIs in \href{http://dx.doi.org/...}, \doibase; ids as
  bare numbers, \arXiv{}, \eprint{}). Largest: 2610.32592 (518), 2504.01669 (255),
  2006.15122 (166), 1201.5118 (164).
- The six papers without entries all have a reference list in the source (\ref paragraphs,
  \i macro, enumerate, \noindent[n]): their zero is a parser gap, which ingest3 states.

## 4. Code index

At the indexed commit 47ab19ab (`git show`), drawn with the seed (draw run, `code/`;
`verifier/verdicts/code_verdicts.tsv`): 10 of 10 parameter rows have the right block, name,
type, line and default (one default is stored as the expression it is). 10 of 10 links of
`kb/curated/paper_code_links.tsv` name a symbol at the stated lines that does what the paper
lines say: M01, M02, M03, M05, M08, M14, M15 (verified) and M18, M19, M25 (claimed; content
right, no test, so "claimed" is the right status).

## 5. Parse rate by my own definition

Definition written before the scan (JOURNAL entry 1): TeX source; body chunks >= 1500 words or
>= 50 % of my flattening; an abstract chunk >= 20 words; section rows >= 70 % of my
\section/\subsection count; equation rows >= 70 % of my display count; >= 80 % of my cited
keys with an entry. Result 714/744 = 95.97 % (run kb-20261124-130450-578a535). Failures: no
abstract chunk 25, PDF only 3, sections 1 (2209.06775: 12 rows for 36), equations 1
(gr-qc/0404056: 54 rows for 96 displays, and 41 % of my word count). Recorded "ok" but failing
mine: 7 (5 without an abstract chunk: 4 of them have no abstract environment in the source,
2505.00286 uses a bare \abstract). Counting a metadata abstract where the source has none
gives 718/744 = 96.5 %. A bug in my own cited-key extractor was found and fixed in the smoke
test, before the registered run (JOURNAL entry 2).

## What could not be checked

- The 5 refuted defects and 6 superseding claims that rest on a track's recomputation or on
  reading a figure (829, 832/833, 834/835, 838/839, 840/841, 825, 827).
- Targets of entries that print no identifier: resolving them needs INSPIRE, which this
  package may not query; I judged only that the stored rows are consistent (no target).
- The claims outside the sample: item 1 is statistical. The CHECK.md packages of the brief
  check beyond their corrected rows. The tests that the "verified" code links cite (not rerun).
- Parts of the brief statements other than the corrected ones (I read only the seed lines the
  claims carry, per the instruction to read the brief by named ranges).

## The three weakest points

1. **Open brief to_verify seeds are not processed.** Four of six drawn are settled by the
   store (781, 714, 809, 804) and carry no event beyond the seed. If the brief's seeds belong
   to "the evidence queue that bears on G1" (804 names items of A, C, D, F; 781 and 714 bear
   on core and B), KB-G3 is not met for them.
2. **Identifiers of the bibliography.** 21 of 54 printed identifiers in the drawn entries
   and 4538 of 52725 in the whole snapshot are not taken, in a few recognisable formats; the
   citation graph misses those edges, and the resolution rate of the QA report counts
   entries, not printed identifiers.
3. **What "fulltext/checked" guarantees.** A checked claim can carry a misworded text (682),
   rest on an abstract or a title line (448, 753, 765), and a machine-located one can be a
   fragment (85); the label says a passage was read, not that the text is right.

## What the track should do (requests to the kb lead)

1. Reword 682 (the 15 per cent belongs to the 4Gm variant; the 2.59 and 9.2 per cent are
   computed in run D-bh-dress-20261115-145636-5259f48).
2. Process the 30 brief seeds without a CHECK.md row: at least 781 (L75), 714 (no cosmology in
   2611.12831), 809 (INSPIRE records for 4 of 8), 804 (pointers to 370, 854/855).
3. Teach the bibliography parser \arXiv{id}{class}, "[HEP-PH 9610477]" (capitals, space),
   bare trailing ids, \eprint{}, and DOIs inside \url/\href/\doibase; then re-resolve. The
   seeded list is in <RUN_BIB> `whole_missed_sample.tsv`.
4. Give 2505.00286 its abstract chunk (bare \abstract) and decide whether a metadata abstract
   should count where the source has none (4 papers).
5. Relabel 737 as a correction (true but incomplete), or add to its claim text what is missing.
