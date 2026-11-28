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
