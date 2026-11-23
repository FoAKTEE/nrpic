# JOURNAL of package repro/scope (Track E, batch R1, 2026-11-22)

Reproduction of arXiv:2512.14649 (P1 = `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`, read whole,
791 lines): map of every figure, table and quantitative statement to our runs (`REPRO_MAP.md`), audit
of the set-up (`SETUP_AUDIT.md`), the missing card runs (`queue.txt`, `CARD_PLAN.md`), the request for
backreaction level 2 (`outbox_draft/`). Predictions are written here before each run.

## Entry 0 (2026-11-22 18:10 PST): processor smoke test of the two decks "as in the paper"

Decks `inputs/sr_paper.athinput` and `inputs/usr_paper.athinput` differ from the decks of the
registered runs P256 / P256v6 (`ladder/inputs/sr_base.athinput`) and U256ap
(`g2prod/inputs/usr_prod.athinput`) only in output options (diff in the deck headers): dump cadence,
`dump_magnitudes = true`, a restart output (SR), `con_signed` (SR). Before any card time, a 32^3
processor run of each (nmax2 = 64, 8 cycles, release processor build core-v0.6).

Prediction S0: both runs end with exit status 0; each writes two NRSFDMP2 dumps (t = 0, t = 0.25 or
0.26) whose variable list holds the 27 names phi, Pi, chi, K, alpha, gt_ij (6), At_ij (6), H, Mx, My,
Mz, E, Hmag, Mmag, MBx, MBy, MBz; Hmag > 0 everywhere; the record `.sf.con.hst` has a line per cycle.
Refuted by: a parse error, a missing variable, a dump layout other than NRSFDMP2, or Hmag <= 0 at a cell.

Outcome S0 (run E-20261123-020506-a459085, release processor build, 1 core, 41 s): PASS. Both decks
parse; two NRSFDMP2 dumps each with the 27 variables (no name missing); Hmag min 11.90-12.00 (positive;
at t = 0 it is (2/3) K^2 + 16 pi E = 6 + 6 in code units, as expected); 9 record lines. The dump falls
at the first cycle after each multiple of dump_dt (t = 0.2945 at cycle 6 for dump_dt = 0.25 and 0.26):
the dump cadence does not change the time steps, so the 256^3 runs below repeat the steps of P256v6
and U256ap exactly. `smoke.json` in the run directory.

## Entry 1 (2026-11-22 18:25 PST): predictions of the card runs, written before any submission

Queue `queue.txt` (release card build core-v0.6, seed A = rng_seed 20261115, s = +1, level 0 unless
stated). Reference values come from registered runs (named). "Record" = `.sf.con.hst` every cycle.

P1 (USF256 vs U256ap, E-20261121-211214-0377aab; RSF256 vs P256v6, E-20261121-202935-31520bc): the
decks differ only in output, the steps are the same (S0), and a card run without particle deposition
is deterministic on one card. At every recorded time the two runs share (|dt| <= 1e-9), phi, Pi, chi,
K, gt_ij, At_ij are bit-identical; the records agree to the last digit. Refuted by a relative
difference above 1e-12 in any field at a common time (above 1e-10: a defect to report to core).

P2 (constraint levels, P1:538-541): RSF256 record max of <|H|/[H]> during the entry (cN <= ln 64 =
4.16) in [3e-11, 1e-10] (ladder P256: 4.7e-11-5.1e-11, ladder/README A4 row); <|M|/[M]> max in
[3e-4, 5e-4] (P256: 3.3e-4-4.0e-4). USF256: <|H'|/[H]> (con_signed) max 2.9e-12 and <|M|/[M]> max
2.5e-2 within 10 percent (U256, SCOPE 4c U-A4'(c)). Per cell: the 99th percentile of |H|/[H] over the
lattice stays below 1e-9 at every dump of either run. Refuted by any value outside these bands.

P3 (sign flip, P1:541; RNC256, noise_pi_sign = -1, to t = 4.5): the record <|H|/[H]> exceeds that of
RSF256 at the same cycle by at least 1e3 at every cycle with cN in [0.5, 4.16]; <|M|/[M]> reaches 0.1-0.3
(ladder NC64/NC128: 0.20-0.22; P1 "~1"). Refuted by a ratio below 1e3 or M/[M] below 0.05.

P4 (ablation, P1:520, 777-790; UL1 and RL1 at noise_level = 1 against U256ap / P256v6, same seed):
shell power of R^NR at N_f, |Delta_L1/Delta_L0 - 1| per shell: SR below 1e-6 at every shell (box means
equal the Friedmann background within 2e-12, ladder A1); USR below 1e-4 at every shell with k <= k_max/2
(P1's level 2 bound "<~ 1 per ten thousand"; its level 1 curves lie below). Refuted by any shell above
these bars. Level 2 is not run (not implemented; outbox_draft/core_noise_level2.md).

P5 (Fig. 1 at 64 cells, M64S, M64U; k_max = 16 dk): box means against the Friedmann references
(ladder/usr reference runs E-20261115-135532-3f958a1 for SR, E-20261119-143905-f2bcde3 for USR):
SR |dV/V| < 1e-8, |d eps1/eps1| < 1e-6, |d eps2| < 1e-5 at every record line; USR |dV/V| < 1e-6 and
|d eps2| < 1e-2 at every line, eps2 at N_f = -0.0276 +- 0.002 (reference table, P1:534 "-2.8e-2").
Refuted by any line outside.

P6 (convergence series, k_max/dk = 8, N = 32, 64, 128 in SMALL, 256 in CL256S/CL256U; P1 Figs. 7-8):
(a) during the entry (cN <= ln 8 = 2.08) the record <|H|/[H]> falls from N = 32 to 64 at an order
between 4 and 6 (ladder A5: odd part 4.2-5.8) in both cases, and the 128 and 256 values agree within a
factor 2 (the second-order part does not depend on N; scalar_field_2.md ladder row); (b) after the entry
both decay; (c) SR shell power of R^NR at N_f against the MS reference, max over shells of
|1 - Delta_NR/Delta_MS|, decreases monotonically 32 -> 64 -> 128 -> 256 and is below 1e-5 at 256
(ladder A2: 8.8e-5 at L32 to 1.7e-6 at L256 per mode). Refuted by an order outside [4, 6], a 256/128
ratio outside [0.5, 2] in the entry, or a non-monotone (c).

P7 (USR amplitudes, P1:534-536, USF256 at N_f): one-point rms of R^NR 0.894 within 5e-3 (lattice value,
usr/results/usr_reference.json); max |R^NR| over the 256^3 cells between 3 and 8 (Gaussian tail of
1.7e7 correlated cells; P1 says "~10" for the furthest outliers, which our realisation need not reach);
shell Delta[R] at 64 dk near 1 (reference 1.017). Refuted by an rms outside 0.889-0.899 or a max above 10.

Figure of S0 (run E-20261123-021741-5d89f8f, `fig/fig_smoke.png`, looked at): SR: [H] smooth near
11.92 with a 1e-5 relative modulation, |H|/[H] about 1e-12 in the mid-plane (a ring where H changes
sign), records <|H|/[H]> 1-3e-12 and <|M|/[M]> 6e-6-1.6e-5 over the 8 cycles. USR: <|H|/[H]> jumps to
5e-9 after the first step and reaches 1.6e-8 at cycle 8, and the mid-plane |H|/[H] is uniform to five
digits (log10 = -7.816): the uniform residual H0 of the time integration of the background at the
32^3 step (dt = 0.049), known from `usr/README.md` (U-A4 row: "H record = background time residual,
1.1e-7 of [H] at Courant 0.25" on 32^3); at 256^3 the step is 8 times smaller, H0 about 8^4 = 4096
times smaller, consistent with the U256 record 2.9e-12 (SCOPE 4c). Not a defect; the S0 verdict stands.
It means the USR constraint percentiles of Fig. 4 must be read with the box mean of H removed
(con_signed columns, or H - <H> per dump), as SCOPE 4c already does [JUDGEMENT].
