# baseline: semi-analytic GW baseline of Track B (B-pre-4 under decision 0010)

The collapse of a homogeneous ellipsoid (Zel'dovich pancake of finite extent) in an
Einstein-de Sitter background as ordinary differential equations, its quadrupole moment
and the quadrupole-formula gravitational-wave signal; the scalings stated by
arXiv:2403.15126 and arXiv:2605.04487 reproduced with locators; how the same quantity is
to be obtained from this repository's AthenaK (Newtonian reference mode and full
relativity with `gw_diag`). No simulation code: ODEs, closed forms, Fourier sums.

| File | Content |
|---|---|
| `BASELINE.md` | the deliverable: equations, results, code path (i) Newtonian mode and (ii) GR with gw_diag, run pairs, the dropped gevolution comparison, open items |
| `JOURNAL.md` | predictions (written before the runs) and outcomes, including the two that failed |
| `scripts/ellipsoid.py` | library: ZA ellipsoid, shape coefficients (Carlson R_D), models A (embedded), B (literal 2605.04487), C (static, 2403.15126), crossing events, Q and its derivatives, P_GW, spectra |
| `scripts/run_baseline.py` | checks T1-T8; writes `baseline_results.json` and the figures |
| `results/baseline_results.json` | copy of the output of run `B-emd-gw-20261115-115752-840e994` |
| `figs/t*.png` | copies of its figures (each inspected) |

Runs (manifests in `tracks/B-emd-gw/runs/`): `B-emd-gw-20261115-115529-58c7f50` (first
run; figure labels and one JSON key wrong, numbers identical) and
`B-emd-gw-20261115-115752-840e994` (cited). Each took 40 s on 4 processor cores; no card
time used.

Rerun (from the worktree root, about 40 s):

    OMP_NUM_THREADS=4 python3 tracks/B-emd-gw/baseline/scripts/run_baseline.py scratch/B-emd-gw/<run_id> [T1 T2 T3 T45 T6 T7 T8]

Needs numpy, scipy (>= 1.8 for `elliprd`), mpmath, sympy, matplotlib (all present on
anta) and `python/nrpic/figstyle.py`. Register the run (`tracks/B-emd-gw/runs/<run_id>/
manifest.json`) before citing a number.

## Requests

- R1 to core (Newtonian mode, `core/newton`): a history diagnostic of the particles of a
  chosen species at synchronized states: time, a, selected mass, centroid, Q_ij, Q'_ij,
  Q''_ij in physical coordinates relative to the centroid, Q'''_ij (jerk or centred
  difference of Q''), P_GW (specification: `BASELINE.md` section 4.2). Acceptance tests
  N1-N3 with numbers from run `B-emd-gw-20261115-115752-840e994`.
- R2 to core (low priority): an isolated-patch option of the Newtonian mode in comoving
  coordinates with the EdS background force, with and without the field of the uniform
  ellipsoid of density rho_b subtracted, so that the two readings of 2605.04487 (models B
  and A) can be run with particles.
- R3 to the lead of B-emd-gw: schedule the delta_N field of a compensated ellipsoidal
  patch for `cosmo/ic/make_field.py` (linear start), the common initial data of run pairs
  P2-P5; and the driven linear tensor equation of comparison G2 (with the gw_diag helper).
- R4 to the lead of B-emd-gw / verify_cosmo helper: compare with the published results of
  arXiv:2003.08014 (source in `kb-data/raw/arxiv/2003.08014/v2/src`). The task statement
  of this package says `cosmo/` already did; I find no such comparison under `cosmo/`.
- R5 to kb: locators for the homogeneous-ellipsoid equations (Lin, Mestel & Shu 1965;
  Icke 1973; White & Silk 1979; Bond & Myers 1996), now [BACKGROUND] here.
- R6 to the gw_diag helper: confirm that `gw_spectrum` returns energy per unit physical
  volume in the cosmological gauge of `cosmo/` (needed for a E_box = int P a dt, comparison
  G3).
