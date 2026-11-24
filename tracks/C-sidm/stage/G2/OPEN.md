# C-sidm G2: what the gate still lacks

State at the end of the lead session of batch 11 (2026-11-24). G2 is NOT met and the package
is not ready for review. Seven items pass (C3, C4, C8, C12, C14, C19, C20), four fail (C1, C2,
C7, C9) and nine are open.

## What blocks the gate

1. The collisionless threshold (C7, C9, and the brief's row "Einstein-Vlasov steady states and
   their stability threshold" in C1). On the M/8 mesh at N = 1e5 the unkicked controls of the
   threshold model (y0 = 0.334032) and of y0 = 0.344 collapse on their own at 534.8 and
   549.3 M; by the refutation written before block A, this mesh and N are unfit for the scan
   over 600 M. Which of the two readings holds decides the next scan:
   - relaxation by particle noise (run (v) points this way on M/4 by the letter of N.4 and
     N.6, with a phase confound): then N >= 1e6, or collapse times against controls of equal N;
   - a secular error of the scheme on this mesh: then M/16, the gauge leg and a question to core.
   Queued: N6c (N = 1e6 control), N4c (N = 1e4 control), M16 (D2 on M/16).
2. Three-way convergence (C2): particle number on M/8 waits for N6c and N4c; mesh waits for
   M16 (and, for the collisionless control, an M/16 control not yet queued: about 2.5
   card-hours for 300 M); no gauge or boundary leg exists. Proposal for that leg (not
   queued, card-hours): the D2 control and f = 2 on M/8 with the outer boundary at 256 M
   instead of 512 M, or with `shift_eta` 1.0 instead of 2.0, 300 M each.
3. Figures and note (C10, C11, C13, C15, C16, C17): to be drawn once items 1 and 2 have data.
4. Verifier (C18): not started.

## What a G2 verifier must cover (G1 reservation 4 and this round)

- Recompute from the raw histories, with readers of its own: the collapse times and alpha_c
  changes of block A (15 runs) and D2 (5 runs), and the collision counts per particle and per
  M; the lead's own recheck (run C-20261124-132113-52c2abe) shares no code with the package
  readers but is the same agent.
- The count test of the collision rate before t_c (z = -3.39 at f = 4, n_balance and n_noroot
  growing with the cell; REVIEW-wave3 section 14): is it the pair sampling of large cells, and
  must n_balance be added back?
- The conductivity series: f per case from the reduced snapshots, the zero-cell extrapolation
  and the k lambda -> 0 combination (1.020 +- 0.004), against the relativistic Chapman-Enskog
  reference of verify_g1 V1a.
- Run (v): N.4 and N.6 with a trend estimator that separates the pulsation (period 310 M at
  N = 1e4, 355 M at 1e5) from a secular contraction.
- The resume of the cut chains: that a continued run equals an uninterrupted one within the
  card noise (compare A334s1c, never cut, with a continued control of the same model once the
  seeds 2 and 3 exist; restart exactness of the particle state, decision 0027 item 3).
- The block A noise model as written before the runs and as applied (ripple window, partial
  windows), and every failed prediction of JOURNAL 2026-11-24T13:12Z.
- When N6c, N4c and M16 end: their verdicts against NS.1-NS.3 and M16.1-M16.2.

## Reservations of G1 and where they stand

| G1 reservation | State |
|---|---|
| 1 conductivity at the per-cent level | answered: series H.1-H.4 hold; kappa/kappa_1 = 1.020 +- 0.004 at zero cell and k lambda |
| 2 threshold from collapse times or contraction against a control, three seeds | partly: every kicked run has its control; seeds 2 and 3 cut by preemption, being continued; controls collapse (item 1 above) |
| 3 quantities named after the data | the block A ripple window was changed after the data (labelled in the reader and in the journal) |
| 4 card tests without a second check | open: verifier above |
| 5 M/4 mesh does not hold the equilibrium | M/8 does not either over 600 M at N = 1e5 (item 1) |
