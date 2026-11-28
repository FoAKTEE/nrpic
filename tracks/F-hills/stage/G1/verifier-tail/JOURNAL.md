# JOURNAL of stage/G1/verifier-tail (second part of the fresh verification of G1, F-hills)

Helper package of batch 34 (2026-11-27), processors only, 0 card-hours. Readers: the first
verifier's scripts in `../verifier/scripts/`, run unchanged, and small readers of my own here for
what those scripts do not read (status files, the waveform amplitude after the capture).

## Entry 1, 2026-11-27 16:37 PST: what I saw before writing, and predictions

Seen before these predictions (stated so that nothing below counts as blind where it is not):
- the subject lines of the lead's commits da850964a and 3c43374a0 (`git log`): "one complete
  vacuum passage to 186.0 M (C8 met); m1 captured by M with a common horizon at 137.5 M, m2's
  horizon to 186 M; F1 decided in part". I have not read the lead's journal entries of batch 34,
  `stage/REVIEW-wave3.md`, the current CHECKLIST or STAGE_REPORT.
- decision 0044 item 2 (fates read from tracker positions to 133 M: break-up between 120 and
  133 M, one member falls into M, the other passes at 8.7 M with marginal energy; Newton gives the
  opposite assignment; A2-2 and the heavy-hole clause of A2-5 refuted).
- the last three rows of `hills.horizon_summary_2.txt` and `hills.horizon_status_2.txt` of A2
  (t = 186 M, mass 1.12291, found = 1, reason 0, 5 flow iterations) and the file times (summary
  and status of finder 0 last written 2026-11-26 14:00, the others 2026-11-27 04:17); the chain's
  STATUS is FAILED after an sbatch I/O error; the lead's `nrpic-run finish` of A2 is still running
  (A2's manifest still says "submitted").
- criterion (iv) of `../../G0/SCOPING.md` l. 139-141 and the text of A2-1..A2-5
  (`../../../JOURNAL.md` l. 828-839), C8's wording at the first verifier's commit 57c7a67dc.

Predictions for the unchanged rerun of `../verifier/scripts/run_all.sh` on the completed passage
(PT = prediction of the tail; refuted as stated in each):

- PT1 (join). Every tracker file of A and A2 (kept copies and the live file) joins to one record
  0-186.0 M with every step 2^-9 M (n_steps_not_2^-9 = 0) and no gap; overlaps of recomputed
  stretches agree to below 1e-11 M in every class (A-A, A-A2, A2-A2). Refuted: a gap, a step other
  than 2^-9 M, an overlap above 1e-11 M, or a last time other than 186.0 M.
- PT2 (pair). The pair's closest approach stays 2.1096 M at 76.37 M (the cut result); no later
  minimum of s goes below it. Refuted: any minimum below 2.1096 M after 96.2 M.
- PT3 (centre of mass). The minimum of the reader's d_cm lies outside the A2-2 box (95-115 M and
  8-11 M together); I expect it after 115 M (in 115-140 M). Refuted: a minimum inside the box.
  [The quantity is a mass-weighted point of a pair that breaks up, so its minimum is a reading,
  not a pericentre of a bound pair.]
- PT4 (fates from positions). One member's tracker comes within 1 M of M's tracker between 130
  and 140 M and stays within 1 M to the end (capture); the other member's distance to M passes a
  minimum of 7.5-10 M and is 12-25 M at 170 M and growing [parabola about 1.13 M from 8.7 M needs
  about 100 M to reach 30 M]. So A2-3 fails as written: no member is beyond 30 M at 170 M, and the
  captured member is not "bound with a pericentre of 4-8 M". Refuted: a member beyond 30 M at
  170 M, or no member within 1 M of M after 140 M.
- PT5 (fates from horizons, status files from 133 M). Finder 2 (M) is found at every search from
  133 M; its mass jumps by 0.10-0.13 between 136 and 139 M to 1.11-1.13 (common horizon of M and
  the captured member) and stays within 1e-3 of 1.1229 after the jump. The captured member's
  finder stops being found (or stops writing) after the common horizon. The other member's finder
  is found in every search from 133 to 186 M with mass 0.1294 +- 2e-4. Refuted: a not-found
  search of finder 1 or 2 after 133 M (other than within 1 M of the jump), or no jump.
- PT6 (F1). From 133 M to the jump the status file marks both branches of the heavy hole found
  (if both persist), so the found flag alone does not pick a branch; flow iterations or the
  residual may. Refuted: rows of one branch marked not found.
- PT7 (Newton). The Newtonian reference from the same deck integrates to max(200, 186) = 200 M,
  as in the first part: every number of `newton` in vpassage.json equals the first part's to all
  digits (m1 = comp0 ejected, m2 bound). Refuted: any digit differs.
- PT8 (masses). A2's medians: members 0.1294 +- 2e-4; the heavy finder's median moves from
  1.00385 by less than 1e-3 (fewer than half of its searches are after the jump), while its
  max - min becomes 0.11-0.13 (the jump), so the reader's A2-5 heavy-hole number now measures the
  capture, not a drift.
- PT9 (constraints). rms H = sqrt(H-norm2/Volume) of A2 stays below 1e-4 to 186 M, with its
  largest value after 96 M at the capture (130-145 M). Refuted: a value above 1e-4.
- PT10 (waveforms). A2's waveform files hold every 0.25-M sample from 62 to 186 M at all four
  radii and both parts; joined with A: 745 samples 0-186 M at each radius, none missing; A-A2
  common samples agree to 1e-11. Refuted: a missing sample, or a last time other than 186 M.

## Entry 2, 2026-11-27 16:55 PST: outcomes of the unchanged rerun (run F-20261128-003721-95f3c15)

`../verifier/scripts/run_all.sh`, unchanged, 1 core, about 1 minute; outputs in
`scratch/F-hills/F-20261128-003721-95f3c15/`. Correction to entry 1: the file of finder 0 last
written on 2026-11-26 14:00 is `hills.horizon_shape_0.txt`, not its summary or status file (both
written to 186 M); I misread the listing.

- PT1 REFUTED in one class. 77 files per tracker, joined 0-186.0 M, 95233 times, every step
  2^-9 M, no gap (MET); overlaps A-A <= 1.13e-12 M, A-A2 <= 4.8e-14 M (MET), but A2-A2 up to
  1.25e-9 M (tracker 0), 1.1e-10 M (tracker 1), 1.5e-16 M (tracker 2): above my 1e-11 bound.
  Where they come from is read in entry 3 (vtail).
- PT2 MET. Pair minima: only the start-up wiggles below 1 M and 76.3727 M, s = 2.109626 M; s at
  186 M is 17.53 M.
- PT3 MET for the A2-2 box, REFUTED on my own window: the reader's single minimum of d_cm is
  4.5251 M at 140.585 M (not in 95-115 M, not in 8-11 M; my window 115-140 M missed by 0.6 M).
- PT4 in part (from the reader's end state): tracker 0 ends 1.3e-9 M from M's tracker (the two
  punctures' trackers coincide), tracker 1 ends 17.53 M from M. Timing and minimum: entry 3.
- PT7 MET: the `newton` block equals the first part's to every digit (dict equality), and
  `vtest.json`, `vjunk.json` are byte-identical; `vmesh.json` differs only in the A + A2 horizon
  blocks.
- PT8 in part: medians 0.129487 (finder 0), 0.129508 (finder 1), 1.004220 (finder 2); finder 2's
  max - min is 0.1207 (MET). But finder 0 now has 1340 failures by the signature (from 139.56 M)
  and a largest "accepted" mass of 1.0602: the signature reader counts as accepted rows that are
  not physical member horizons (entry 3 with the status file). The reader's `heavy_A2_branches`
  now splits at 1.063 (before/after the capture), so it no longer measures F1: F1 is redone in
  entry 3 on 86.6 M to the jump only.
- PT9 MET: rms H of A2 at most 6.19e-5, at 135.5 M; 1.51e-5 at 186 M.
- PT10 MET: every 0.25-M sample 62-186 M in A2 at all radii and parts (542 raw rows, 497 times);
  joined A + A2 745 samples 0-186 M, none missing; A-A2 common samples agree to 1.4e-12.

Predictions for my own reader `scripts/vtail.py` (status files, overlaps by time, fates with the
remnant mass, (2,2) amplitude). Its self-test failed once on a bug of the synthetic writer (the
time column written as an integer), not of the reader; it passes after the fix.

- PT11 (overlaps). The A2-A2 overlaps above 1e-11 M all belong to segment pairs that start at or
  after 133 M (the restart with the diagnostics input and the capture). Refuted: one before 133 M.
- PT12 (status vs signature). Finders 1 and 2: found at every search from 133 M, signature
  agrees everywhere. Finder 0: the status file's not-found searches outnumber the signature's
  failures (some failures write a row that is not a repeat), so the signature undercounts.
  Refuted: equal counts for finder 0, or a not-found search of finder 1 or 2.
- PT5/PT6 as in entry 1 (jump of finder 2 at 136-139 M to 1.11-1.13; finder 0's last found
  search at the capture; both F1 branches found where the status file covers them).
- PT13 (finder 0 after the capture). Any "found" surface of finder 0 after the jump of finder 2
  has a mass far from 0.129 (the finder centred on m1's tracker, now at M, finds the common or
  M's horizon or a spurious one); none has 0.129 +- 1e-3. Refuted: a found 0.129 surface of
  finder 0 after the jump.
- PT14 (m2's energy). With the remnant mass at M's tracker, m2's coordinate two-body energy at
  186 M lies within +-0.3 units of zero and below the reader's +0.12 units (heavier central mass);
  m2 is marginal in coordinates, neither clearly ejected nor clearly bound. Refuted: |E| > 0.3.
- PT15 (waves). The (2,2) amplitude at r = 40 M rises above three times its 60-130 M median
  after t_jump + r* - 10 M; at 70 and 90 M nothing of the capture arrives before 186 M.
  Refuted: no rise at 40 M before 186 M.
