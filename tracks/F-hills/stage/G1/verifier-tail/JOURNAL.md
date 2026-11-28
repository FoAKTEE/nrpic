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
