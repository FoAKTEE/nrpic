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
