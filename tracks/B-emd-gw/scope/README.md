# scope: G0 scoping material of Track B (helper package)

| File | Content |
|---|---|
| `SCOPE.md` | problem statement, check of item 3, choice of the first GW source, parameter ranges, measured quantities, exit criteria, test plan mapped to brief section 10, risks (noise quantified from `cosmo/TESTLOG.md`), compute estimate |
| `REFERENCES.md` | the eleven key references read at the source: what each computes, approximation, GW scaling, `file:line` locators |
| `JOURNAL.md` | predictions written before each check, outcomes after (also the failed part of 3B) |
| `scripts/check_item3.py` | sympy: TT projector along x, rotation invariance, the harmonic TT mode of a plane-symmetric slice, its projection, the flat-transverse growing-mode test |
| `scripts/crossed_waves_tt.py` | numpy: quasi-static second-order TT strain of crossed sine waves on a Fourier grid (weak-field equation of arXiv:1604.06065) |
| `scripts/regime_estimates.py` | scipy: junk-TT decay ODE in the matter era, virial GW frequency against box modes, card-time table from measured throughput |
| `results/*.json`, `results/*.txt` | outputs copied from the scratch directories of the runs below |
| `figs/crossed_waves_tt.png`, `figs/regime_estimates.png` | figures (style `python/nrpic/figstyle.py`), inspected |

Runs (manifests in `../runs/<run_id>/manifest.json`, outputs in
`/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/`; all analysis runs on processors, no
card time):
- `B-emd-gw-20261115-113102-bc5e082` check 1 (item 3);
- `B-emd-gw-20261115-113148-4e5c33b` check 2 (earlier version `-113120-bc5e082`);
- `B-emd-gw-20261115-113632-2960145` check 3 (earlier versions `-113151-4e5c33b`,
  `-113246-50c684b`).
`harness/bin/nrpic-run verify <run_id>` passes for the three.

## Rerun

From the worktree root, each in a few seconds, with numpy, scipy, sympy and matplotlib:

    python3 tracks/B-emd-gw/scope/scripts/check_item3.py OUTDIR
    python3 tracks/B-emd-gw/scope/scripts/crossed_waves_tt.py OUTDIR [--n 32 --L 4 --delta 0.01]
    python3 tracks/B-emd-gw/scope/scripts/regime_estimates.py OUTDIR

Register new runs with `harness/bin/nrpic-run submit --kind scouting --gate G0 --purpose
"..." -- python3 tracks/B-emd-gw/scope/scripts/<script>.py` (the helper did not exist on
this branch when these runs were made; their manifests were written by hand in its fields).

## Requests

To core:
1. In-situ output of the TT-relevant Fourier modes: gamma_ij (or the conformal metric and
   chi) and K_ij (or A_ij, K) at the lowest box wave vectors (|n| up to 3 or 4) every few
   cycles, so that the first-source runs need no full dumps (a full 128^3 dump series is
   about 67 GB a run; SCOPE.md risk 7). The specification comes from package `gw_diag`.
2. Confirm or enable thin periodic boxes for z-independent data (for example 256 x 256 x
   16 cells, one meshblock in z) with Z4c and particles; this cuts a 256-cell convergence run
   of the first source from 5.8 to 0.36 card-hours (delta = 0.01).
3. Initial data with a non-flat conformal metric in `nrpic_cosmo` (`id = file`): the
   second-order TT part, to remove the junk TT of conformally flat data (SCOPE.md
   risk 2), or a statement that subtracting the junk in the analysis is preferred.
4. AthenaK's Newtonian mode for identical particles and clouds (decision 0010); until it
   exists, confirmation that `cosmo/newton/` is the sanctioned Newtonian counterpart.
5. A jitter option for the lattice of `cosmo/ic/make_east.py` (random displacement in the
   directions transverse to the wave, fixed seed), for the noise-floor null run.

To the lead of B-emd-gw (for the orchestrator):
6. Correct item 3 of `coord/notes/derivations_to_check.md`: it holds, but (a) it needs the
   rotation part of plane symmetry (or T_yy = T_zz, T_yz = 0), (b) on the torus the
   covariant TT part keeps one global harmonic mode (anisotropic mean expansion) that is
   not radiation, (c) the `cosmo/` single-wavelength data have amplitudes (1, 0.9, 1.1),
   not equal ones, and equal amplitudes radiate at mixed wave vectors as well.
7. The brief's pancake row (line 848) cites the Newtonian exactness of the Zel'dovich
   solution; the GR reference needs an x-dependent transverse metric (check 1E). Needs an
   owner and a source (plane-symmetric Szekeres-type dust).

To Track A (A-emd-pbh):
8. The black-hole end of the amplitude range (delta = 0.05 fails at a = 17.2 in `cosmo/`)
   waits for a slicing that passes collapse in the matter era; B would reuse A's gauge
   choice (2610.23218, 2608.13206). The Szekeres row of section 10 is shared.

To kb:
9. Index the eleven sources of `REFERENCES.md` (already under `kb-data/raw/arxiv/`) and
   fetch 2212.00425, 2312.12499, 1704.03500, 2012.14016, 1708.09143 for the next step.
