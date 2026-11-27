# Gate review: C-sidm G2 (independent reviewer, batch 34)

Reviewer session of batch 34, 2026-11-27 (from 23:20 UTC). Decision 0019 item 3. I produced none
of this work. DRAFT: this commit holds only the predictions of my own check, written before it
ran; the review follows in the next commit.

## Reviewer's own check R: predictions (written and committed before the run)

Reader of my own (`scratch/C-sidm/tmp/gate_review_g2/review_check.py`, registered with
`nrpic-run`, inputs checked against each run's `sha256sums.txt`): comment lines skipped; restart
rule (a row whose time is not later than the last kept row replaces every kept row from its time
on); marker crossing = first record with alpha_min (column 16 of `cc.nrpic.hst`) below 0.3,
linear between it and the record before. I looked at the lead's `fig_g2_threshold.png` and the
verifier's `fig_v2_fates.png` before writing these, so R1 repeats numbers I have seen; R2 and R3
are quantities neither of them states.

- R1 (fates). Crossings 252.31, 217.97, 252.41, 229.79, 295.78, 534.81 M for N6b344, A16b344,
  N6b344e1, A344s1i, N4c, A334s1c, each within 0.05 M; no crossing for N6b324, A16b324,
  N6b324e1, N6c, A324s1i, whose last kept record is at 600 M or later (to 0.25 M). Refuted by
  any crossing off by more than 0.05 M, a crossing in a stable member, or a stable member that
  ends before 599.75 M.
- R2 (what "holds" means). For each of N6b324, A16b324, N6b324e1 the 20 M block means of
  alpha_c - alpha_c(0) (alpha_c = column 13, alpha_probe at the origin) have an interior minimum
  followed by an interior maximum, the maximum between 300 and 500 M: the inward kick is reversed
  and the core re-expands (a stable oscillation, not a slow drift), and every block mean lies
  within +-0.03. For N6b344, A16b344, N6b344e1 the block means fall from 40 M to the last block
  before the crossing with no rise above 0.002 from one block to the next. Refuted by a stable
  member without an interior maximum in (300, 500) M or with a block mean outside +-0.03, or an
  unstable member with a block-to-block rise above 0.002 before its crossing.
- R3 (constraints in the members of the legs; column 4 `H-norm2` of `cc.z4c.user.hst`, the
  volume integral of H^2). (a) N6b324e1 against N6b324, mean over 100-200 M: equal within 5 per
  cent (the shift damping does not change the deposit noise). (b) A16b324 against N6b324 (cells
  of M/16 inside |x| < 1.95 M, same particles): ratio between 1.2 and 10 (fewer particles per
  cell where the mesh is finer; the lead reports 9.3 for M/4 to M/8). (c) No growth in the
  stable members: mean over 500-600 M divided by mean over 100-200 M within 0.7 to 1.4 for
  N6b324, A16b324, N6b324e1 and N6c. Refuted by any ratio outside its range.

Each failed prediction stays on record in this file with the number that refuted it.
