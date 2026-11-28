# JOURNAL of package claims5 (owner kb, helper; batch 35, 2026-11-27)

Fifth claims package: the machine-located claims that a track cites and nobody had read (class T
of claims4; decision 0048 item 7). Processors only, no card time.

## Entry 1, 2026-11-27 18:32 PST: population, order, verdict rules, predictions (before any reading)

Population: class T of package claims4 (order run kb-20261128-003945-e1d65ba, `order.tsv`, seed
20261127): 144 claims, label fulltext, status located, label set by the automatic seeder, not C (no
cut at either end), cited by a track (id named on a 'kb' line, or a locator overlapping a TeX
locator in a file of the track's branch). claims4 read k = 35..47 (13). The 131 unread members are
k = 48..178 of order.tsv; checked at 18:31 PST on kb.sqlite (922 claims, last event
2026-11-28T00:49:53Z): all 131 still fulltext / located / auto. By track: C 45, A 40, F 17, D 13,
B 12, core 4. I read them in that seeded order, k = 48 first, as many as the time allows, so that
what is read is a seeded random part of the 131.

Reading: every stored locator row, with `tracks/kb/claims4/scripts/show.py` (source lines as text,
nothing under kb-data/raw executed); a whole-file grep where a number or word is not in the cited
lines; the citing line of the track (order.tsv `cited_by`) where the text reads like a track's own
statement.

Verdict rules: those of claims4 entry 1, unchanged, so the rates compare: right; right_locator
(relocated, counted right); fragment; wrong; part_unsupported; wrong_label (a track's judgement,
verdict or reading, or a brief inference, stored as fulltext). Borderline cases are marked and the
rate is given both ways. Actions: right -> verify (relocate or extend the locator first where
needed); not right -> supersede by a whole-sentence claim read at the source with the correct label
(a track's own judgement or reading gets label judgement, with the track named), or withdraw when
the text holds no checkable statement and no sibling carries it. A wrong text is never verified.

Predictions (measured: claims4 T 10/13 = 76.9 %, CP 95 % 46.2-95.0 %; machine-located random
samples pooled 46/61 = 75.4 %, CP 62.7-85.5 %):
- Q1 (rate). Right as worded about 75 %: of n read, about n/4 not right (n = 50: about 12,
  binomial 95 % range for p = 0.25 is 7-19; n = 40: 5-16; n = 30: 3-12). Refuted if the CP 95 %
  interval of the measured rate of this package excludes 75 %.
- Q2 (kind of error). In a cited class the commonest error is a track's own reading or judgement
  stored as fulltext (wrong_label), not a cut fragment (the cut class C was removed): wrong_label
  at least as frequent as fragment among the not-right verdicts. Refuted if fragments outnumber
  wrong_label.
- Q3 ('lower' flag, claims4 P3). Texts beginning with a lower-case word are right less often than
  the others. Refuted if their right rate is not lower (judged on what is read; small numbers).
- Q4 (writes). Dry run and real run of the plan give the same new claim ids and identical
  before/after tables; the hash of all other claim rows agrees before and after in both. Refuted by
  any difference.
- Q5 (whole class, [JUDGEMENT: extrapolation]). With claims4's 13, about 25 % of the 144 are not
  right as worded, 25-45 claims; refuted if the stratified estimate falls outside 20-50.

## Entry 2, 2026-11-27 18:45 PST: reading, writes, rates (outcomes)

Read: all 131 unread members of T (k = 48..178 of order run kb-20261128-003945-e1d65ba, in that
order), each at every stored locator row in the raw TeX with `scripts/show.py`, plus a whole-file
grep where a word, number, author or absence was not in the cited lines (the grep is named in the
verdict note). With claims4's 13, class T is now a census (144 of 144). Verdicts:
`work/verdicts_T.tsv`; ledger `LEDGER.tsv` (successor ids). One slip caught before any verdict: I
typed two ids (342, 285) from memory instead of from the order list; both are already checked and
outside the population; they got no verdict and no action.

| | n | right (incl. right_locator) | not right | CP 95 % | borderline both ways |
|---|---|---|---|---|---|
| claims5 T (seeded part k = 48-178) | 131 | 114 = 87.0 % | 17 | 80.0-92.3 % | 61.8-90.1 % |
| T census (claims4 13 + claims5 131) | 144 | 124 = 86.1 % | 20 | 79.4-91.3 % | 61.1-88.9 % |

Not right (17): wrong_label 6 (C 329, 230, 242; A 19; F 451; core 484), fragment 6 (B 182, 193;
A 87, 33; D 352; C 252), wrong 3 (C 234 and 306: the hedge 'may not be necessary' of
2108.11967 L283 dropped; C 248: 'quasi-static treatment' where the paper finds the core can be
approximated as quasi-static), part_unsupported 2 (D 684, 685: the other paper's attribution and a
corpus remark outside the locator). Borderline: 33 counted right (noun phrases, locator or note
debris, glosses), 4 counted not right (234, 306, 248, 242).
By track of the claim (n, not right): A 40/3, B 12/2, C 45/7, D 13/3, F 17/1, core 4/1.

Predictions:
- Q1 REFUTED, on the good side: 87.0 % right, CP 95 % 80.0-92.3 % excludes the predicted 75 %
  (17 not right of 131; the binomial range for p = 0.25 at n = 131 is far above). The cited class
  is cleaner than the pooled machine-located samples. As far as the reading shows, the reason is
  that C (cuts) was removed from it first and a track citing a claim tends to cite its well-formed
  rows; but with the 33 borderline rows counted not right the rate falls to 61.8 %, so the result
  depends on the claims4 rule that a readable noun phrase or a row with debris is right.
- Q2 HELD at the margin: wrong_label 6 = fragment 6 (refuted only if fragments outnumber).
- Q3 HELD, not significant: lower-case starts 49/57 = 86.0 % against 65/74 = 87.8 %.
- Q4 HELD: dry run kb-20261128-024311-9e8af45 and real run kb-20261128-024327-81f35d6 give the same
  new claims (923-936; 638 and 910 reused as targets), identical before.tsv, after.tsv, others.json
  and result.json; the hash of the 789 other claim rows is unchanged in both.
- Q5 HELD at its edge: 20 of 144 not right (predicted 25-45, refuted outside 20-50).
New stratified estimate for claims4's 389 (C census 16, T census 20, R sample 5/13 scaled to 211):
about 117 not right (s.e. 29), right as worded 69.9 % (s.e. 7.4 %) [JUDGEMENT: R still rests on 13
read claims]; 41 of them are now corrected.

Writes (plan `plans/P1_claims5.json`, committed in 9e8af45 before its runs; 132 actions): 114 verify
(7 with an extended locator: 324, 173, 639, 334, 445, 32, 80), 13 supersede by new whole-sentence
texts read at the source (923-927, 929-936; 926 and 932 labelled judgement with the track named),
4 supersede to existing claims (684, 685 -> 910; 451 -> 638; 306 -> 924), 1 add (928, C's
reproduction run split off 230, judgement; status unlocated as in claims4's add). Rates run
kb-20261128-024430-2b76f58; its rerun kb-20261128-024452-cfc4954 changed only two figure labels
(rates.json identical by cmp). Figure looked at: `figures/fig_claims5_rates.png`; the label of the
prediction line touches the verifier2 marker.

## Entry 3, 2026-11-27 18:47 PST: snapshot and QA, prediction (before the run)

The run repeats claims4's kb-20261128-005138-5cef2a2 (verify-downloads, `kb qa run --hybrid`,
`kb snapshot`, status). Expected: verify-downloads exit 1 for the known gr-qc/9412071 row only;
C1 counts agree; C3 not ok 25; C8 40/41; C7 rows unchanged (no chunk changed); C9: 936 claims,
labels fulltext 672, judgement 84, refuted 127; statuses checked 452, located 279, superseded 85;
locators 1223, all resolved; a new snapshot with a new hash. Refuted by any other C1/C3/C7/C8 value
or a C9 count different from these.

Outcome (run kb-20261128-024540-477cbc9): HELD in every predicted value. verify-downloads exit 1
(gr-qc/9412071 only; 683 of 684 arXiv ok, 63 GitHub ok); C1 counts agree; C3 not ok 25; C8 40/41;
C7 section identical to claims4's run by diff (text 27/32, hybrid 28/32 locator 23, rerank 28/32
locator 25); C9: 936 claims, fulltext 672, judgement 84, refuted 127, checked 452, located 279,
superseded 85, locators 1223 resolved 1223 (also: claims with a chunk 689, labels set by a person
659, which I had not predicted). Snapshot db/current -> kb-20261128-bd57a33 (sha256 bd57a33b...).
Copy of the QA report: work/QA_REPORT_after_P1.md.

## Entry 4, 2026-11-27 18:53 PST: notes to owners

Run kb-20261128-025251-f8edef3 (`scripts/notes.py`; its first run kb-20261128-025231-adeb3f4 lacked
the section for claims seeded from an owner's files, which only core needed): one note per citing
owner in `notes/` (A 4 superseded, B 2, C 7, D 3, F 1; core: its seeded 484, cited by A). Each
superseded claim with the places where the owner's files cite it (claims4's classifier, branch
state 2026-11-27 17:05 PST). By hand afterwards: one line in NOTE_C-sidm.md naming 928, the
judgement split off 230. The notes are for the kb lead to post to tracks/kb/outbox (I write only
in this package).
