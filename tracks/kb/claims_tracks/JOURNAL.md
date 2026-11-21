# Journal of the claims_tracks helper (kb, wave 3 round 1)

Predictions are written before the run or the reading they concern; outcomes after it, also
when the prediction failed. Labels: [VERIFIED] (checked against a file, line or run named
here), [BACKGROUND], [JUDGEMENT], [TO VERIFY]. No paper text is copied here: reasons are in
my own words, with locators.

## 2026-11-20 22:17 UTC: start

State found: `tracks/kb/claims_tracks/` did not exist (no earlier session of this package);
kb/main at 346cb17c, main already merged, tree clean. Read: CLAUDE.md, CHARTER (to "Gates of the
knowledge base", sheets 9.4-9.9), harness/RULES.md, brief 12.8 (lines 1400-1405) and 1458,
kb/README.md, kb/kbtool/claims_db.py, claims_check.py, claims_cli.py, the wave-2 claims journal,
coord/REQUESTS.md "To kb", the two requests (B 20261115T191057Z, D 20261115T195105Z), kb journal
559-595.

Two tool facts that shape the work [VERIFIED, kb/kbtool/claims_cli.py and claims_db.py at
346cb17c]:
- `kb claim check --id N` acts only on claims of the wave-1 seed (it re-reads the notes and
  matches seed keys); the hand-added claims 689-700 (`manual-*`) are never re-checked by it.
  For a claim whose label a person set, it leaves label and status alone but deletes and
  rewrites the locator rows from the NOTE's locators (`upsert_seed`, else branch). So after a
  relocation it would put the old rows back under the new locator string (the wave-2b defect
  of claim 25 again). Rule I follow: after `verify --locator` or `relocate` I do not run
  `check` on that claim; I run it only on claims verified at their own locator. Reported to
  the lead (README, Requests).
- No kb command records an annotation without a label change: annotations go through my own
  script `scripts/annotate.py` (claim_events row, action 'annotate', inside the writer lock).

## B0 prediction (before the registered baseline run)

The working database kb.sqlite holds what the snapshot kb-20261119-a782f1e describes: 700
claims; to_verify 117 (A 15, B 4, C 5, D 18, F 52, core 23; located 63, partial 26, unlocated
27, unresolved 1); judgement 41; background 1; fulltext 541 = 39 checked + 502 located by
machine. (I looked at these counts once with an unregistered read-only query while planning;
the registered run is the record.) Refuted by any other count, e.g. claims added by the
claims_brief helper before my run (then I take its counts as the baseline and say so).

## B0 outcome (runs kb-20261120-222203-73ebf61 and, after moving the legends, kb-20261120-222240-f9db7eb; counts.json identical)

Held exactly [VERIFIED, scratch/kb/kb-20261120-222240-f9db7eb/counts.json]: 700 claims (max id
700); labels fulltext 541, to_verify 117, judgement 41, background 1; statuses located 583,
partial 34, checked 39, unlocated 43, unresolved 1; fulltext 39 checked + 502 machine-located;
queue by track A 17, B 15, C 14, D 28, E 7, F 54, core 24 (159). No claims_brief additions yet.
Figure `figures/fig_queue_baseline.png` read: bars agree with the table; the first drawing
had the legend over the F bar, redrawn.

## Q prediction (before processing the queue): shares of outcomes

Queue: 117 to_verify (source labels: TO VERIFY 60, VERIFIED or VERIFIED-implicit whose numbers
the machine did not find 36, UNLABELLED "NOT computed" lists 15, UNLOCATED 6), judgement 41,
background 1.
- The 36 VERIFIED-but-partial or unlocated: most carry the track's own numbers or paraphrases;
  I expect 25-32 verified (with or without a corrected locator), 0-2 refuted, the rest kept.
- The 60 TO VERIFY: these are open points the tracks could not settle at the source; I expect
  about 40 % verified (the passage settles them), about 45 % kept as to_verify with a recorded
  reason (the statement is an inference or needs a computation), up to 10 % refuted
  (the paper says otherwise), a few abstract-only.
- The 15 "NOT computed" absence lists: about 70 % verified after a full-text search of the
  paper finds none of the listed computations; the rest kept.
- The 6 unlocated: about half found by search.
Overall: 55-80 of 117 reach fulltext/checked, 2-8 refuted, 30-55 remain to_verify with a
reason, 0-5 abstract or title_only; all 42 judgement/background annotated with the evidence
that bears on them (none changes label). Refuted if fewer than 40 or more than 95 reach
fulltext, or more than 12 are refuted.

## A1 and B1 outcomes (runs kb-20261120-222903-226b273 and kb-20261120-223013-5330e45; written 2026-11-21 at the restart)

The session of 2026-11-20 applied both batches before the usage-limit cut, but did not write
their outcomes here. I reconstructed them from LEDGER.tsv (rows equal to the runs'
ledger_rows.tsv) and from a read-only recount of kb.sqlite on 2026-11-21 at 21:15 UTC:
- A1 (17 claims, the whole queue of A): 14 to_verify became fulltext/checked (5 with a
  corrected locator: 54, 169, 28, 166, 167). 1 stays to_verify with a recorded reason: claim 9,
  the boundary condition, which the paper does not state. 2 judgements were annotated (20, 170).
  None was refuted.
- B1 (14 of 15): 4 to_verify became fulltext/checked (219 and 226 with the abstract line added).
  10 judgements were annotated. Claim 186 cites 2403.15126, which ingest3 re-ingests, so it was
  left for the end of the package.
- Prediction Q so far: verified 18 of 19 to_verify in A and B (the predicted share was 55-80
  of 117 overall), refuted 0, kept 1. The A and B part runs above the predicted share. Q is
  judged over the whole queue at the end.

## 2026-11-21 21:15 UTC: restart (batch 6)

State found: kb/main at b6f59456 (main merged), A1 and B1 applied and committed. The
following were in the worktree, uncommitted: decisions/{C1,D1,E1}{,_annot}.tsv and
scripts/batch_{C1,D1,E1}.sh, written in the last minute before the cut and never run. No
run manifest exists for them, and the database still shows those claims in their
pre-batch states: C 14, D 28 and E 7 in the queue, and claim 345 fulltext/checked.

I re-read every decision of C1, D1 and E1 at its locator in the stored source before running
it (read_claim.py, terminal only). Each statement matched the text, and I checked the
arithmetic again:
- 610: 3.29993e-2/2.892 = 1.141e-2.
- 611: 0.355962 x 0.303616^2 / 3 = 1.094e-2.
- 612: 3.87808e-2/9.672 = 4.010e-3.
- 616: 25 sqrt(pi)/(32 sqrt 6) = 0.565; 25 pi/(32 sqrt 6) = 1.002.
- 604/605: the prefactors.
- 606: the Girsanov ratio, rederived.
- 608: the Friedmann factor.
- 697: I checked the corrected root of eq. lmax numerically. With Delta, R(x) = 0 holds to
  1e-12 for three (a, E, x) sets; with the printed a^2 - x(x-2) the square root has a
  negative argument. The check is registered below as part of run D1 (scripts/check_697.py).
- D's run values for 682: reference.json in scratch/D-bh-dress/D-bh-dress-20261115-145636-5259f48
  gives 2.5897 and 0.0922.
I changed no decision.

### Prediction CDE (before the runs of C1, D1, E1)
- Every kb command of the three scripts exits 0. Each batch run exits 0.
- C: 257, 258, 259, 303 and 308 become fulltext/checked. 303 gets the new locator 2105.05556v1
  paper.tex L75 and L88-89, which resolves (status checked). The 9 judgements keep their label
  and status and gain one annotate event each.
- D: 380, 408, 417, 418, 419, 420, 682 and 683 become fulltext/checked. 370 becomes fulltext
  with two resolved locators. 346, 381, 409, 412, 413, 414 and 416 stay to_verify with an
  annotate event each. 344, 379, 388, 398, 679 and 681 (judgement) and 415 (background) keep
  their label.
- 399 keeps the judgement label; its locator moves to L322-326, and the status becomes located.
- 697-700 change status from unlocated to located or partial; their labels do not change.
- 345 stays fulltext/checked and gains one event.
- E: 7 judgements annotated, labels and statuses unchanged.
Refuted by any FAILED line, a label change other than those listed, or a status of
'unresolved' after a relocation.

### Outcome CDE (runs kb-20261121-211743-d9dfe56 C1, kb-20261121-211759-c80bb03 D1, kb-20261121-211809-38a04d0 E1)
All three runs exited 0 with no FAILED line [VERIFIED, run.log of each]. check_697.tsv: the
corrected root gives R = 0 (|R| < 4e-12) in all six cases, and the printed root has a negative
argument in all six.
- C held as predicted: 5 to_verify became fulltext/checked. 303 now has 2 resolved locator
  rows. 9 judgements were annotated.
- D held, with one exception:
  - 9 to_verify became fulltext/checked (682, 683, 380, 408, 417-420, 370).
  - 7 stay to_verify with reasons.
  - 7 judgements and 1 background were annotated.
  - Refresh moved 697 to located and 698, 699 and 700 to partial. The numbers they quote are
    D's run values, which are not in the paper, so the machine check calls them missing.
  - Failed part of the prediction: 399 stayed judgement/partial after the relocation; I had
    predicted located. The new locator resolves, but the claim's derived numbers (-12,
    4 m^2 H^2) are not printed at L322-326. That is expected for a derivation, and the
    label is right.
- E held: 7 judgements were annotated, unchanged.
Ledger rows were appended from each run's ledger_rows.tsv.

## 2026-11-21 ~21:55 UTC: decisions F1a, F1b, K1, L1 (written after reading every claim at its source)

Read with read_claim.py and sed on the stored sources (terminal only).
- F (54): 0911.1136 and 1804.02911 (32 Hills reference numbers): every number of F's
  reference.py matches the printed text. 655 also needs the figure-caption line L649 for the
  mass ratios. 2404.16270 (686, 688, 635): 635's "alpha about 0.1" is in appendix L8, not at
  the cited article lines. 2402.02178 (687) is a to-do of the track. Novelty claims 421-452:
  2406.11985, 2308.07365, 2505.03934, 2505.01495 and 1203.6185 read at their tables and
  abstracts; 2605.22525, 2609.20338, 2608.22735, 2608.16986, 2610.27775, 2212.10891,
  1303.1540, 2602.06961 and 2610.20594 are not in the store. 658-662 (1201.4794, which ingest3
  re-ingests) are read and go into the last batch L1.
- core (24, all on 2611.12831v1): full-text searches with grep for cosmolog*, FLRW,
  collision, filter, pass, c_H, Courant/CFL and "other code"; counts of figure and table
  environments. Repository parts checked where they are cheap: docs/TESTLOG.md L46, L600,
  L650; deposit.md L100-101; os_amr.athinput L82.
- No refutation: no read passage contradicts a claim. The nearest case is 635. Its cited
  lines say alpha reaches 0.2, the appendix says 0.1 in the examples, so the claim holds.
F1 (49) was split into F1a (32) and F1b (17) to keep batches near the 20 the brief asks for.

### Prediction FK (before runs F1a, F1b, K1)
- F1a: 32 claims become fulltext/checked, no FAILED line.
- F1b: 10 claims become fulltext/checked (686, 688, 635, 423, 426, 428, 430, 432, 439, 448).
  5 stay to_verify with annotate events (687, 447, 449, 450, 452). 2 judgements (421, 425)
  are annotated.
- K1: 19 claims become fulltext/checked. 5 stay to_verify: 456, 538, 549, 601 (kept with
  reasons) and the judgement 559, annotated.
- Every verify_loc locator resolves (status checked, all locator rows resolved).
Refuted by any FAILED line or unresolved locator row. If kb claim verify refuses a claim
that had no locator before (core 467, 520, 525, 543, 548, 570), my belief that verify_loc
attaches a first locator was wrong.
