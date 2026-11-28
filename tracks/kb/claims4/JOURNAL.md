# JOURNAL of package claims4 (owner kb, helper; batch 34, 2026-11-27)

Second pass over the claims located by machine and never read (KB-G3 OPEN.md item O7; HANDOFF of
kb, item 1 and 2). Processors only, no card time.

## Entry 1, 2026-11-27 ~17:10 PST: population, classes, verdict rules, predictions (before the draw and before any reading)

Population (scripts/population.py, `count`, read-only on kb.sqlite at 17:05 PST, no draw yet):
M = claims labelled fulltext/abstract/title_only, status located or partial, label set by the
automatic seeder and locator check (label_set_by = 'auto'): 420. Minus those already read or
handled by name (events of audit P2, the wave-2/2b leads, the leads of batches 13, 15, 17,
claims3; the verdict files of both KB-G3 verifiers and claims3's sample; the eight leftovers of
the second verifier and claims3's named fragments): **389 unread**. By track A 118, core 95, C 71,
D 53, B 27, F 25.

Reading classes, disjoint, read in this order:
- C, text begins or ends in a cut (a connector word first: and, i.e., which, see, at, for, so, ...;
  punctuation first; or an open end: last word a connector, trailing punctuation, unbalanced
  bracket or backtick): 34.
- T, not C and cited by a track: its id named with 'kb' on the line, or a locator row overlapping a
  TeX locator written in a file of the track's own branch other than the claim's origin file
  (TeX file name unique to the paper, or the paper id on the citing line): 144.
- R, the rest: 211.
A text that only starts with a lower-case noun (a list item of a note) is not C; it is flagged
'lower' (C 23, T 60, R 80) and its rate is reported apart.
Within each class the order is a permutation by random.Random(SEED), SEED = 20261127 (file SEED,
committed with this entry, before the order run). Reading stops when the time is used up; what
is read of a class is then a seeded random part of it. Plan: all of C, then T and R alternately in
their seeded orders, about 13 each.

Verdict rules (the same categories as claims3 entry 1, so that the rates compare):
- right: every factual part (numbers, attributions, what the statement is about) is supported at
  the stored locators as worded; a connector word at the start ("and", "i.e.") that leaves a
  readable statement does not make it not right (claims3 counted 373 and 467 right);
- right_locator: as right, but a supported part sits outside the stored locator (relocated; right);
- fragment: the text has no statement a reader can check: subject or predicate cut away, so that
  one cannot tell what the paper is said to state (claims3: 29, 572; verifier2: 462); not right;
- wrong: the text says something the source does not say, or of another object; not right;
- part_unsupported: one part is not supported (an addition of the track's); not right;
- wrong_label: a judgement, a track's verdict or a brief inference stored as fulltext; not right.
Borderline cases are marked; the rate is given with them counted right and counted not right.
Actions: right -> verify (relocate first where right_locator); not right -> supersede by a
whole-sentence claim with the correct label read at the source (claims3's supersede), or withdraw
when the text holds no statement and no sibling carries it. A wrong text is never verified.

Predictions (measured rate of the class: machine-located pooled 28/35 = 80.0 %, CP 95 % 63.1-91.6 %,
VERIFIER2.md section 2; claims3 WA 18/22, verifier2 M 10/13):
- P1 (T and R, random within class). Right as worded about 80 %; of 26 read, about 5 not right.
  Refuted if fewer than 1 or more than 10 of 26 are not right (outside the binomial 95 % range
  for p = 0.2), or, for another n, if the CP 95 % interval of the read rate excludes 80 %.
- P2 (C, the cuts). Higher error than the base rate, because every error of claims3's sample was
  a seeder's cut or mislabel: 30-60 % not right, so 10-20 of 34. Refuted if fewer than 7 (the cut
  flag says nothing beyond the base rate) or more than 27.
- P3 ('lower' flag). Texts starting with a lower-case noun are fragments more often than the
  rest of T and R (judged on what is read; refuted if their not-right rate is not higher).
- P4 (whole M, stratified C census + T + R samples). Right as worded 72-82 %; about 70-110 of the
  389 not right [JUDGEMENT: extrapolation].
- P5 (writes). The dry run and the real run of the plan give the same new claim ids and the same
  after-state; apply.py's hash of all other claim rows agrees before and after (others unchanged).
  Refuted by any difference.
- P6 (leftovers of the second verifier). 741: the 'large, near-extremal spin' wording sits at
  L1206 of Spin_PBH.tex, not at L64-67 (relocate). 428: the paper's author order is Ciarfella
  first (supersede). 804 and 805 are both instructions of the brief, not statements: one rule
  (to_verify, annotate). 313 carries a note's locator debris ('| 2601.17117 `SIDM_MS.tex:476`'),
  430 is cut at both ends: both superseded by whole sentences. 864: 'Jena' is an affiliation, not
  an author (supersede). 877: a paper statement and F's run result in one fulltext claim: split
  into a fulltext claim and a judgement claim. Refuted per claim if the source says otherwise.

## Entry 2, 2026-11-27 ~16:55 PST: reading, writes, rates (outcomes)

Order run kb-20261128-003945-e1d65ba (seed 20261127, classes C 34, T 144, R 211). Read: all 34 of C
(census) and the first 13 of T and of R in their seeded orders, 60 claims, each at every stored
locator in the raw TeX (plus a whole-file grep where a word or number was not in the cited lines).
Verdicts: work/verdicts_C.tsv, work/verdicts_TR.tsv; LEDGER.tsv.

| Class | Read | Right (incl. right_locator) | Not right | CP 95 % of the right rate |
|---|---|---|---|---|
| C cut | 34 of 34 | 18 | 16 (10 fragment, 3 part_unsupported, 2 wrong_label, 1 wrong) | 35.1-70.2 % |
| T cited | 13 of 144 | 10 | 3 (2 wrong_label, 1 fragment) | 46.2-95.0 % |
| R rest | 13 of 211 | 8 | 5 (4 fragment, 1 wrong_label) | 31.6-86.1 % |
| T+R (random within class) | 26 | 18 = 69.2 % | 8 | 48.2-85.7 % |

Borderline: 10 counted right (cut start, table debris, noun phrase, gloss), 2 counted not right
(564, 301). With all borderline cases flipped the C rate runs 35.3-58.8 %, T 53.8-76.9 %, R 53.8-61.5 %.
Stratified estimate for the 389 unread (C census + T, R samples, finite-population s.e.):
right as worded 66.5 % (s.e. 8.5 %), about 130 not right (s.e. 33) [JUDGEMENT: extrapolation from
26 sampled claims in T and R]; 24 of them are corrected here. Pooled with the earlier random
machine-located samples (claims3 WA 18/22, verifier2 M 10/13): 46/61 = 75.4 % (CP 62.7-85.5 %).
Run kb-20261128-005107-c2d924a (rates.json, figure).

Predictions:
- P1 HELD in its refutation clause (8 of 26 not right; refuted only beyond 10), but on the high
  side: expected about 5. The T+R rate 69 % is below the pooled 80 %, inside its interval.
- P2 HELD: 16 of 34 cut texts not right (predicted 10-20).
- P3 HELD on few claims: T+R texts starting lower-case 5/9 right (56 %) against 13/17 (76 %).
- P4 FAILED: the stratified rate 66.5 % is below the predicted 72-82 %, and 130 not right is above
  the predicted 70-110. Cause, as far as the reading shows: R carries many note fragments (heading
  rows, locator-only rows, noun phrases) that the cut flag does not catch; the earlier samples
  counted cut-but-readable texts right, and so do I, so the difference is not a stricter rule.
- P5 HELD: dry run kb-20261128-004850-7a66cfe and real run kb-20261128-004951-4e8871c give the same
  new claims (896-922; 862 reused) and identical before/after tables; others hash unchanged in both.
- P6: 741 relocated to Spin_PBH.tex L1205-1209 (held: L64-67 has no spin statement); 428 author
  order Ciarfella, Ficarra, Lousto (TBH.tex L37-47, held) -> 916; 804 superseded by a to_verify
  claim 917 with the same eight locators, 805 annotated with the rule (one rule held); 313 -> 918
  (I did not re-read 'citing 2108.11967' and 'dispersion approaches c': not carried); 430 -> 919
  (also its '~10^3 scatterings' understates the paper's 'hundreds of thousands or millions', L108);
  864 -> 920 ('Jena' is the affiliation, L80; held); 877 -> 921 (paper) + 922 (F's run, judgement).

Writes (plan plans/P1_claims4.json, 72 actions): 36 verify (5 with an extended locator), 32
supersede (26 new successor texts 896-921, 5 to a sibling's successor, 339 -> 862), 1 withdraw (583,
a table heading), 1 relocate (741), 1 annotate (805), 1 add (922). Successors are read at the
source: every new text states only what its locator lines say; track judgements kept are labelled
judgement (909, 911, 922). One wrinkle: the added judgement 922 has status unlocated although its
locator row resolves (apply.py's add path; claims3's 'add' did the same).

## Entry 3, 2026-11-27 ~17:15 PST: snapshot and QA

Run kb-20261128-005138-5cef2a2 (as lead b17's kb-20261125-124304-2790a38): verify-downloads exit 1
(the known gr-qc/9412071 row); `kb qa run --hybrid`: C1 counts agree, C3 not ok 25, C8 equations
40/41, C7 hybrid paper hits 28/32 (locator 23), rerank 28/32 (25); `kb snapshot`: db/current ->
kb-20261128-fcd969d (sha256 fcd969d6...); 762 papers, 922 claims. Copy of the QA report:
work/QA_REPORT_after_P1.md (kb/QA_REPORT.md is the lead's to commit). Not compared line by line
with the QA report of snapshot 56c4b53: no QA check was predicted to change except the claim
counts (C9), so I state the numbers without a verdict on the retrieval rows.
