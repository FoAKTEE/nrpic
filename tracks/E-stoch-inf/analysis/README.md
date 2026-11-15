# Analysis of AthenaK output for Track E (wave-2 helper package)

Reader and estimators for the scalar-field output of the release executable (core-v0.3):
the curvature perturbation R^NR, per-mode amplitudes against linear theory, shell spectra,
freezing drift and constraint ratios; their tests on synthetic fields and on real
output; the noise unit test at the base size with U9 on a card; a slow-roll scouting case
that the release can run without the perturbed initial slice. Predictions and outcomes:
`JOURNAL.md`. The lead's wave-1 scripts in `lead/` are not part of this package.

## Contents

| Path | What |
|---|---|
| `sfa.py` | the module: `read_dump`, `read_modes`, `read_history`, `read_bin_metric` (gt_ij, At_ij from a `bin` output, single precision); `Lattice` (hemisphere modes, coefficients, the code's alpha_n); `curvature_perturbation` (P-c of spec/SPEC.md 7.1, 2610.32592 appendix.tex:513-522); `expected_coefficients` (L^-3/2 W_q R_q alpha_n from a `.modes` record), `per_mode_ratio`, `shell_spectrum`, `drift`; `ham_norm_cells`, `mom_norm_cells`, `at_terms_of`, `constraint_ratios` |
| `tests/test_sfa.py` | synthetic tests T1-T5 (reader, R^NR to second order with controls, per-mode ratio, spectrum normalisation, constraint norms) |
| `scripts/plane_check.py` | constraint estimators on core's plane perturbation (N = 16, 32) against the code's history |
| `scripts/make_sr_case.py`, `run_sr.sh`, `analyse_sr.py` | slow-roll scouting case from a homogeneous slice (release executable), and its analysis |
| `scripts/make_u_inputs.py`, `inputs/u64/` | inputs of the noise unit test at the base size (N = 64, nmax2 = 256, 300 steps); `card_batch.list` for the card job |
| `scripts/proc_u2_u4.sh` | U2 and U4 of the base case on processors (A14 reference, A12) |
| `scripts/val_cf.py`, `scripts/u6_scaled.sh` | the track's noise validator with a cancellation-free window increment in the reference; scaled U6 with the release |
| `fig/` | figures and JSON summaries copied from the registered runs (all looked at) |

## How to rerun (from the worktree root, `.venv` made by `harness/bin/nrpic-env create --no-kokkos`)

    EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
    harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher local --cores 2 \
      --package tracks/E-stoch-inf/analysis --purpose "synthetic tests" -- bash -c \
      'python3 tracks/E-stoch-inf/analysis/tests/test_sfa.py --out "$NRPIC_RUN_DIR"'
    ... -- bash -c "python3 tracks/E-stoch-inf/analysis/scripts/plane_check.py --exe $EXE --out \"\$NRPIC_RUN_DIR\""
    ... -- bash -c "bash tracks/E-stoch-inf/analysis/scripts/run_sr.sh $EXE \"\$NRPIC_RUN_DIR\" 16 control"
    ... -- bash -c "bash tracks/E-stoch-inf/analysis/scripts/u6_scaled.sh $EXE \"\$NRPIC_RUN_DIR\""
    harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher batch --wall 00:20:00 \
      --list tracks/E-stoch-inf/analysis/inputs/u64/card_batch.list --package tracks/E-stoch-inf/analysis --purpose "..."

The local launcher passes its arguments without a shell: `$NRPIC_RUN_DIR` must sit inside
`bash -c '...'` (journal 17:08). Validation of the base case once the card job and the
processor run exist (CARD, PROC = their run directories):

    V=tracks/E-stoch-inf/noise/validate/validate_noise.py; I=tracks/E-stoch-inf/analysis/inputs/u64
    python3 $V --input $I/U1.athinput --run CARD/U1 --blocks8 CARD/U2 --blocks64 CARD/U3 \
      --res-lo CARD/U5a --res-hi CARD/U5b --res-lo-input $I/U5a.athinput --res-hi-input $I/U5b.athinput \
      --seed2 CARD/U8 --seed2-input $I/U8.athinput --out OUT/val_frozen
    python3 tracks/E-stoch-inf/analysis/scripts/val_cf.py --input $I/U6.athinput --run CARD/U6 --out OUT/val_u6_cf
    python3 $V --input $I/U7.athinput --run CARD/U7 --out OUT/val_u7
    python3 $V --input $I/U2.athinput --run PROC/U2 --restart PROC/U4 --card CARD/U2 --out OUT/val_a12_a14

## Results (run ids: `tracks/E-stoch-inf/runs/<run_id>/manifest.json`)

- Synthetic tests, all 15 pass (E-20261115-171445-36152c4): R^NR is recovered to second
  order in the amplitude (2.35e-4 of the rms at A = 1e-5, slope 1.00); without the gt term
  the error is first order (0.657, by construction of the slice); per-mode deviations,
  spectra and constraint norms exact to round-off. [VERIFIED by run]
- On real output (core's plane perturbation, E-20261115-171859-0b34449): mean |H| and
  rms H from the dumps equal the code's history to 2e-14; [H] per cell (with At At from
  the bin output) equals the code's [H] to 1e-14; the physical |M| needs gt^ab (with it
  2e-9, without it 5.5e-4: failed prediction of the first run E-20261115-171628-1737ebe);
  ratio orders 5.97 (H) and 5.66 (M) between N = 16 and 32. [VERIFIED by run]
- Markov-tanh noise of the release (scaled U6 on processors, E-20261115-172423-5234cce):
  A1 3.3e-15 and all tests pass with a cancellation-free reference; 9.8e-11 (fails 1e-11)
  with the reference as it is. The defect is in `noise/ref/noise_ref.py`, not in the
  code. [VERIFIED by run]
- Noise unit test at the base size (N = 64, nmax2 = 256, 300 steps) on one A100 with the
  release (card run E-20261115-170645-3b21217, 55 s, 0.0153 card-hours; validation
  E-20261115-180533-24a7781): frozen scheme passes A0-A11, A13, A15 (A1 9.8e-14; A11
  bit-identical for 1, 8, 64 MeshBlocks on the card; A13 3.5e-15); Markov-Heaviside passes
  (one crossing shell only at this output cadence); Markov-tanh passes with the
  cancellation-free reference (A1 4.0e-15) and fails A1 at 8.5e-10 with the reference as
  it is. [VERIFIED by run]
- Slow-roll scouting case, N = 16 and 32 (E-20261115-172349-0bdb97d,
  E-20261115-172347-a297a96): see below.

## What the release executable can and cannot do for the slow-roll case

Can [VERIFIED by runs E-20261115-172349-0bdb97d (N = 16, with control) and
E-20261115-172347-a297a96 (N = 32); one realisation each]: start from the homogeneous
slice (`id = flrw`) 1.5 e-folds before the lowest mode reaches the window (W(k_min) =
3.6e-7 there) and let the Mukhanov-Sasaki sources (level 0, stencil projector, geodesic
slicing) bring every mode in. At ln a = 7.8 the extracted R^NR equals the code's linear
prediction L^-3/2 W_q R_q alpha_n mode by mode to 8.3e-5 (N = 16) and 1.0e-4 (N = 32) for
k <= k_max/2 (3.9e-3 and 3.8e-3 for all modes); super-horizon modes freeze (largest drift
3.3e-4 and 3.4e-4 per e-fold from N_k + 4, against 2.5e-3 of SPEC 7.3 and -4 eps1 = -0.042
of an FLRW lattice); <|H|>/<[H]> peaks at 2.1e-8 (second order, R_rms ~ 1.5e-3) and the
negative control is 610 times larger (N = 16); rms M/rms [M] peaks at 2.2e-3 (first order
in R, as PRD_v2.tex:746 expects) and 0.3 in the control. The lockstep mode functions
differ from SciPy's integration of the same data by 7.3e-4 (N = 16) and 1.4e-3 (N = 32),
made while the modes are deep inside the horizon (half-step test: journal P8). The cost
of the workaround is the extra 1.5 e-folds of steps (about 20 percent of an 8-e-fold
run); N = 32 took 35 min on one core. This is a scouting statement at reduced N with a
quadratic potential in code units, not the 256^3 reproduction of 2512.14649.

Cannot (or not without help):
1. The perturbed initial slice at N* of SPEC 5.3 (request R8): the exact set-up of
   2512.14649 (lowest shell half in at t*) is not reproduced; the homogeneous start
   replaces it, with a difference of relative size W(t0) [JUDGEMENT: linearity argument;
   tested only through the per-mode agreement above].
2. R^NR from the double-precision dump alone: the dump has chi but not gt_ij, so the
   term (1/4) k_i k_j (gt_ij - delta_ij)/k^2 of Phi is missing. In the N = 16 SR run this
   makes every mode 0.48 percent low (a common offset; gt term / R = 4.9e-3). With the
   single-precision bin output of the z4c variables the term is recovered, but only
   because the amplitude was scaled up to Delta_R ~ 1e-6: at the physical Delta_R ~ 2e-9,
   gt - delta (~1e-7) is at the float32 resolution of numbers near 1.
3. The physical norm of M and P1's [M]: the dump's M_i are covariant; their physical norm
   needs gt^ab (5.5e-4 error without it in the plane test); [M] of P1 is not computed by
   the code; `sfa.mom_norm_cells` builds it from the dump without the At terms (a lower
   bound of the same order), with them when a bin output is given.
4. Level 2 of the stochastic backreaction (P1 ran with it on; its ablation changes the
   spectrum by <~ 1e-4, P1:520), several MPI ranks, a stencil k^2 in the mode equation.
5. Not understood yet: before the modes enter (ln a 0.27-0.78), rms M/rms [M] is 5e-6 to
   5e-5 while R_rms is 1e-8 to 1e-6, i.e. not second order in R [TO VERIFY; candidate:
   continuum k^2 of the mode equation against the stencil Laplacian].

## Pending (not done by this package; list for the lead)

- Processor run E-20261115-170727-d15df12 (U2 at the base size, about 98 min, then U4
  about 50 min): A12 on processors and the reference of A14.

## Requests

- core: (a) add gt_ij and At_ij (or Phi of P-c directly) to the double-precision dump, so
  that R^NR and the physical |M| do not need the single-precision bin output (evidence:
  0.48 percent offset of the dump-only R^NR, 5.5e-4 error of the physical |M|); (b) [M]
  of P1 (PRD_v2.tex:740-743) in the history and as a dump variable, and [H] per cell;
  (c) a look at the early first-order momentum residual (item 5 above); (d) the initial
  slice R8 is no longer needed for the slow-roll reproduction at linear order (the
  homogeneous start works, N = 16), but is still needed to reproduce P1's set-up exactly.
- E-stoch-inf noise package (owner): form the window increment of `noise/ref/noise_ref.py`
  (lines 155, 159) as sinh(s H dt)/(2 cosh x1 cosh x0), as the code does; `scripts/val_cf.py`
  shows that this alone makes U6 pass.
- E-stoch-inf lead (SPEC): P-e of SPEC 7.1 says the momentum violation is second order;
  PRD_v2.tex:541 and 746 say |M| is second order and |M|/[M] first order. The measured
  ratio (2.2e-3 at R_rms ~ 1e-3) follows the latter; A4 of SPEC 7.2 should be read so.
- orch (harness): the batch launcher checksums every deck at submission, so a restart
  file made by an earlier line of the same batch cannot be listed (U4 on a card needs a
  second job); and the local launcher's `-- <cmd>` is not run through a shell, so
  `$NRPIC_RUN_DIR` stays literal unless wrapped in `bash -c` (it created a directory of
  that name in the worktree root once; journal 17:08). A note in RULES.md would do.
