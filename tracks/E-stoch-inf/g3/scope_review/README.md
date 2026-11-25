# Package g3/scope_review (Track E): independent review of the G3 scope before its runs

This is a review of SCOPE section 4d (`../../spec/scope/SCOPE.md`, commit cbe20398) by a helper who did not
write it (decision 0039 item 1). It used no card time. The deliverable is `SCOPE_REVIEW.md`: ranked findings
(blocking / should change / note), each with its evidence and run id, proposed wordings, and a verdict line.
The scope text itself is changed by the lead.

| Path | What |
|---|---|
| `SCOPE_REVIEW.md` | the review: verdict, B1-B3, S1-S7, N1-N6, requests |
| `JOURNAL.md` | predictions before each run (entries 1, 3, 5) and outcomes (2, 4, 5), including the refuted ones (BS3, SE4) |
| `ref_bins.py` | expected variance of the lattice-density variant of the one-patch reference, computed from its own bins (finds the top-bin defect) |
| `box_stats.py` | own reader (NRSFDMP2 parser, `.modes` parser, R^NR from its definition) on a mirrored 128^3 pair: one-point statistics, effective cells by Owen's T and by blocks, box-variance share, second order of R^NR |
| `sensitivity.py` | detection thresholds of the 4d.3 comparison (amplitude, skewness, kurtosis; reference against NR errors; seed counts) |
| `kcheck.py` | uniformity of K, chi and alpha on the geodesic slice at every dump (lever arm of the gauge leg) |

## Runs (all registered, processors, 1-2 cores, seconds to a minute each)

| Run | Command (from the worktree root, inside `nrpic-run submit --launcher local --package tracks/E-stoch-inf/g3/scope_review`) |
|---|---|
| E-20261125-130854-ef74ef8 | `python tracks/E-stoch-inf/g3/scope_review/ref_bins.py "$NRPIC_RUN_DIR" --npts 241` |
| E-20261125-131002-ceefa2f | `python tracks/E-stoch-inf/g3/scope_review/box_stats.py "$NRPIC_RUN_DIR" --plus <scratch>/E-20261120-222424-0eb754b/b_p --minus <scratch>/E-20261120-222424-0eb754b/b_m --dump 20 --workers 2` |
| E-20261125-131336-2b903fe | `python tracks/E-stoch-inf/g3/scope_review/sensitivity.py "$NRPIC_RUN_DIR" --box <scratch>/E-20261125-131002-ceefa2f/box_stats.json --ref tracks/E-stoch-inf/langevin/results/ref_inflection_n32.json --bins <scratch>/E-20261125-130854-ef74ef8/ref_bins.json --seeds 256 --nref 4e6` |
| E-20261125-131805-0806ef8 | `python tracks/E-stoch-inf/g3/scope_review/kcheck.py "$NRPIC_RUN_DIR" --run <scratch>/E-20261120-222424-0eb754b/b_p` |

`<scratch>` is `/data/haiyangw/nrpic/scratch/E-stoch-inf`. The exact commands, inputs and checksums are in
`../../runs/<run_id>/manifest.json`. Outputs (JSON, figures) are in `<scratch>/<run_id>/`.

## Results in one paragraph

The "six standard errors" deficit of the reference's lattice variant comes from its top bin. That bin is
normalised to e^0.05 NLAT but only holds shells up to NLAT, so the expected variance is 0.9778 against a
measured 0.9796 +- 0.0032. The deficit alone would move F_ref(3) by -7.6 combined standard errors (B1). At
nu = 3, a 1 per cent sigma error, the whole delta-N skewness and the bin defect each move F(3) by about 10
per cent, so the variance and the tail shape must be judged separately (B2). The zeta reader's two tests
cannot fail on the second order. Yet the second order is the signal: R^NR's quadratic coefficient is 2.8e-4
against delta N's 0.008-0.0095. The metric part of the curvature is 1e-6, so the non-Gaussianity of zeta
will come from the reader's map. From the definitions, zeta = -R^NR at linear order (B3). K is uniform to
4e-7 or better on the geodesic slice, so the kdriver gauge leg has no lever arm (S3). The power estimate's
effective cell count is confirmed within 16 per cent (4.6e5 against 5.5e5). Beyond 78 seeds (nu = 3) or 44
seeds (nu = 4) the reference dominates the error (S7).

## Requests

- To the lead of E: change B1-B3 and S1-S7 in SCOPE 4d (proposed wordings in `SCOPE_REVIEW.md`). Fix
  `lattice_factor_fn` in `langevin/scripts/ref_spec.py` (per-shell factor, or truncate the top bin at ln
  NLAT) before the 4e6 reference. Add the state (phi, varpi) at N_f to the reference output. Read the pilot's
  kdriver pair for the lever arm before queuing the gauge leg. Consider raising q0045 (G3P) to priority 2.
  Copy `SCOPE_REVIEW.md` to `g3/SCOPE_REVIEW.md` if the stage package wants it there (this package may only
  write `g3/scope_review/`).
- To core (only if the group wants a slicing test in this model): a lapse condition that depends on the
  field, such as a driver towards uniform phi. K-based conditions coincide with geodesic slicing here.
