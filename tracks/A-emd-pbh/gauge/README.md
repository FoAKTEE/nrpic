# gauge: work package A-pre-4 (gauge and diagnostics) of A-emd-pbh

Helper package, 2026-11-15. Reading of 2610.23218, 2608.13206 and the method of
2609.14218 against the gauge and diagnostics of this repository's AthenaK, with four
small reference and analysis tests. No simulation was run and no source was changed.

## Contents

| File | Content |
|---|---|
| `GAUGE.md` | candidate lapse and shift conditions, what each paper found (with line locators), what the code has and what needs new source, criteria C1-C7 for the expanding ball, a ranking, and the runs that would decide (G-R1 to G-R4) |
| `DIAGNOSTICS.md` | plan for horizon mass and spin, invariant comparison with the exact solution, wave extraction; what exists, what is missing, who would write it |
| `JOURNAL.md` | predictions written before each test and the outcomes, including the refuted one (T4) |
| `scripts/lapse_toy.py` | T1: lapse of 11 slicing conditions in a homogeneous Einstein-de Sitter region and a closed dust top-hat, zero shift, uniform lapse per region |
| `scripts/vonneumann.py` | T2: largest stable Courant number of the lapse/light and shift modes under the code's discretization (sixth-order differences, Kreiss-Oliger, RK4) |
| `scripts/bh2_onset.py` | T3: constraint growth of the cosmology shift-driver run against its zero-shift twin, with the T2 limit |
| `scripts/kd_compare.py` | T4: the toy of T1 against the lapse at the overdensity of the 3D lapse-driver run |
| `figs/lapse_toy.png`, `figs/vonneumann.png`, `figs/bh2_onset.png`, `figs/kd_compare.png` | the figures of T1-T4 (copies from the run directories) |

Results in one line each (details and run ids in `JOURNAL.md`):
- T1: plain 1+log raises the lapse to 1 + 6 ln(local expansion), 19.0 in a 20-fold
  expanding top-hat (2610.23218: ~20); conformal-time and volume lapses do not avoid the
  crunch; conformal time needs 21.5 times fewer steps than cosmic time to a 56-fold
  expansion.
- T2: C v <= 0.618 (lapse, light) and 0.660 (shift) with `diss = 0.5`.
- T3: the cosmology run with the alpha^2-scaled shift driver went unstable after its
  lapse passed the T2 limit (2.64 at cfl 0.25); prediction confirmed, discriminating rerun
  pending (G-R1).
- T4: the uniform-lapse toy is a factor 5 off in the lapse collapse against the 3D run;
  its freezing epochs are qualitative only (prediction refuted).

## Rerun

From the worktree root, one core, about 90 s in total (OMP_NUM_THREADS=1):

    S=/data/haiyangw/nrpic/scratch/A-emd-pbh/rerun
    python3 tracks/A-emd-pbh/gauge/scripts/vonneumann.py --out $S/t2 --n 49
    python3 tracks/A-emd-pbh/gauge/scripts/lapse_toy.py --out $S/t1 --X 56
    python3 tracks/A-emd-pbh/gauge/scripts/bh2_onset.py --vn $S/t2/vonneumann.json --out $S/t3
    python3 tracks/A-emd-pbh/gauge/scripts/kd_compare.py --out $S/t4

T3 and T4 read (read only) `/data/haiyangw/nrpic/runs/cosmo/east_d0.05_n64_{bh1,bh2,kd}`
in the main checkout (untracked run directories of the cosmology extension). The
scripts need numpy, scipy and matplotlib (user site, so `python3` without `-I`; they read
no downloaded data) and `python/nrpic/figstyle.py`.

Registered runs: `tracks/A-emd-pbh/runs/A-emd-pbh-20261115-113614-374a41a` (T1),
`-113608-374a41a` and `-113755-cac3c4b` (T2), `-113807-43300e5` and `-113921-ca3786e`
(T3), `-113810-e02c969` (T4); outputs under `scratch/A-emd-pbh/<run_id>/`. The manifests
are on disk but not in git: the repository's ignore rule `runs/` also matches
`tracks/<ID>/runs/` (see Requests).

## Requests

To core (source in `athenak/src`, decision 0010):
1. Lapse options for the ball: 1+log against a reference field K_ref(t, x) supplied by
   the initial data (rank 3 of `GAUGE.md`), and the softplus condition of 2610.23218 with
   a stored T field (rank 4); optionally the 1/alpha term of the shock-avoiding slicing.
2. Finder spin with rotation vectors projected onto the surface (or the trace-free part
   of K_ij), so that the trace K = -3H of an expanding background does not enter
   (`DIAGNOSTICS.md` section 2); the history columns: angular momentum of excised
   particles, mesh integral of S_i phi^i sqrt(gamma), particle mass quadrupole and its
   rate.
3. Later: shift damping that varies with the refinement level or the conformal factor;
   Psi_4 with matter terms (Phase 1); a centre tracker for particle overdensities.

To the owner A-emd-pbh (lead):
4. Card time for G-R1 (two reruns of `cosmo/east_d0.05_n64_bh2`, about 0.15
   card-hours each): `cfl_number = 0.125`, and `shift_Gamma = 0.75` with
   `shift_alpha2Gamma = 0`. Predictions in `GAUGE.md` section 5.
5. From A-pre-1 (expball): K_ref(t, x) of the unperturbed ball in the slicing of the
   tables, and the per-shell exact references (R(tau), turnaround, tau at R = 2 M_s,
   rho_centre(tau)) for the invariant G2 comparison; confirm the exterior K of the
   tables, -(3/2)(2M/r^3)^(1/2) (`GAUGE.md` section 3).
6. From A-pre-2 (criteria): an expected horizon mass per parameter set for the finder
   settings, and the spin predictions with their sources.

To the orchestrator:
7. `.gitignore` line 12 (`runs/`) also ignores `tracks/<ID>/runs/`, so run manifests
   cannot be committed without `-f`, against CLAUDE.md's rule that nothing ignored is
   committed. Proposal: anchor it as `/runs/`.

To Track B:
8. Wave extraction in a periodic, matter-filled box (Phase 1) is theirs (B-pre-3); A
   needs the same Psi_4 with matter terms later.
