# Journal: second fresh verifier of gate KB-G3 (kb helper, batch 15)

## Entry 0 (2026-11-25 04:05 UTC): set-up

Fresh session; I wrote none of the packages checked (claims3, lead_b13, lead_b15). Read: CLAUDE.md,
coord/CHARTER.md to the end of "Owners" and its section "Gates of the knowledge base", brief
lines 1400-1461 (12.8 to 12.10), the KB-G3 package (CHECKLIST, STAGE_REPORT, EVIDENCE, OPEN,
SCOPE, REVIEW), the first verifier's summary table only (VERIFIER.md lines 1-34) and its README
for the layout, claims3/README.md row 3 and the docstring and query of
claims3/scripts/weak_class.py (to rebuild the weak class from its written definition). I have
not read REVIEW-wave3.md, the claims3 LEDGER or the verdict notes of either sample.

Database: `kb-data/db/kb-20261125-2f97258.sqlite`, opened `mode=ro&immutable=1` (target of
db/current at start, by readlink). Own code in `scripts/` (v2lib, show, draw, queue_check,
tally); `figstyle.py` copied unchanged from python/nrpic (equal to harness/style). No card time.

## Entry 1 (2026-11-25 04:12 UTC): definitions and predictions, before any draw or reading

Seed for the draw: 20261126 (`SEED`), committed with this entry before the draw.

Item 1 list (61 claims, `scripts/v2lib.py` ITEM1): A new claims 862-881 (20); B superseded and
withdrawn (25: 29, 81, 84, 85, 126, 171, 179, 187, 192, 213, 277, 290, 314, 424, 431, 482, 549,
572, 619-623, 625, 682); C the four siblings that received a `--to` supersession (289, 313, 430,
624); D seeds and named claims 803, 805, 790, 409, 447, 449, 450, 452, 781, 804, 714, 809.
Verdicts: SUPPORTED (as worded, at its locators), NOT SUPPORTED, LOCATOR WRONG (the text is
right but the locator does not hold it), and for B: TAKEN OUT RIGHTLY (old text not right as
worded, successor or withdrawal justified) or TAKEN OUT WRONGLY. A label reservation is noted
separately (e.g. fulltext on an abstract reading).

Item 2 strata (disjoint; population = live claims with label fulltext/abstract/title_only and
status checked/located/partial, minus item 1, the first verifier's verdict files and claims3's
30 sampled claims):
- W (weak class) = label set by a pipeline step (label_set_by auto, kb-claims_tracks,
  kb-claims_brief, kb-claims_brief (12.8 map)) and no event of a person's reading (the audit,
  the leads' readings, kb-lead-b13, kb-claims3) and not in the first verifier's files.
- M "located by machine" = W with label_set_by auto (claims3's WA).
- Q "rest of the weak class" = W minus M (claims3's WQ, WB, WM: labels set while answering a
  queue question or by a join, never read against the claim's own wording).
- P "checked by a person" = status checked and not in W.
Allocation P 14, M 13, Q 13. "Right as worded": every statement of the text is said by the
source at the locators (a cut sentence that changes nothing still counts right; a fragment with
no statement, a number or attribution the source does not give, or a judgement stored as a
supported reading count NOT right). Rates with Clopper-Pearson 95 %; W and the whole
population weighted by stratum sizes.

Predictions (what would refute each in brackets):
- P1 item 1: at least 54 of 61 SUPPORTED or TAKEN OUT RIGHTLY; at most 3 LOCATOR WRONG. 870-881
  and 865-868 right as worded; 805 still to_verify (an instruction). 409, 447, 449, 450 right
  as worded but with the label reservation of OPEN O4 (fulltext on abstract lines).
  [Refuted by 7 or more failures, or by any superseded claim whose old text was right as worded
  while its successor is not.]
- P2 item 2: P at least 13/14; M 10-12 of 13 (WA carried all four errors of claims3's sample);
  Q at least 11/13; W weighted within claims3's interval 69.3-96.2 %. [Refuted by P <= 11/14, or
  a W point estimate outside 69.3-96.2 %.]
- P3 counts: claims3's own query rebuilt on today's snapshot gives 548 (its README and the
  lead's run kb-20261125-033530-5a1ac43), and the unread class after claims3 is 543 +- 5 by my
  definition (the extra exclusion of kb-claims3 events). [Refuted by a difference above 10.]
- P4 C1: the to_verify claims without an event verify/refute/annotate/relocate/check/
  supersede/supersedes/withdraw are exactly 806, 807, 810, 811, 812. [Refuted by any other.]
- P5 C2/C3: db/current points at kb-20261125-2f97258.sqlite, whose sha256 starts 2f97258c.
  [Refuted otherwise.]
- P6 C4, C6, C7: package documents present; the failed run kb-20261124-233445-89478ae has a
  manifest with status failed; STATUS/JOURNAL/HANDOFF last changed in the batch-15 lead commit.
  [Refuted by a missing document, manifest or a stale file.]
