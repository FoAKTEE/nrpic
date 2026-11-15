# einstein_straus: exact-solution benchmark D-pre-1 (black hole in a vacuum bubble inside an expanding dust ball)

Helper package of owner D-bh-dress. A black hole of mass M sits in a vacuum bubble whose
wall is the innermost shell of a marginally bound, expanding dust ball (Einstein-Straus
type); Schwarzschild of the total mass outside the ball. While the wall is comoving the
mass inside it, hence the black-hole mass, is exactly constant: the exact reference of the
null test of "cosmological coupling" (brief S4, track sheet D-pre-1). Units G = c = 1.

## What is here

| File | Content |
|---|---|
| `DERIVATION.md` | the derivation (constraints in KT, KL; Misner-Sharp relation; slices KT = -f sqrt(2M/R^3); trapping and the conditions on f; puncture form; join to the wall; constancy of the mass), the disagreements with item 2 of `coord/notes/derivations_to_check.md`, and the checks with run ids |
| `sym/` | sympy scripts `s1_constraints.py`, `s2_schwarzschild_slices.py`, `s3_ltb_wall.py` (48 identities) and the helper `tensors.py` |
| `es_model.py` | the exact data on the slice (`EinsteinStrausBH`), the exact shell motion (`ltb_radius`), the format-2 table writer/reader and the evaluation rule of `nrpic_cf` (`Tab2`), the particle-file writer |
| `make_es.py` | generator of a data set: table, particles (tracers first), exact reference curves, input template, figures |
| `offline_check.py` | offline constraint check with measured convergence (1D radial, 3D generic 3+1 in sub-boxes, table interpolation) |
| `code_t0_check.py` | start-time check inside AthenaK: the code's own H, M_i, E at t = 0 on a uniform mesh (needs the format-2 reader of `core/id-extrinsic`) |
| `nrun.py` | registers a run: `tracks/D-bh-dress/runs/<run_id>/manifest.json`, outputs in `scratch/D-bh-dress/<run_id>/` |
| `figs/` | `es_profiles` (fields of the slice), `es_expansions` (null expansions on both sheets), `es_reference` (exact areal radii against proper time, constant mass), `es_particles` (lattice mass against m(R)), `check_1d`, `check_3d` (offline convergence), `code_t0` (code residuals at t = 0) |
| `JOURNAL.md` | predictions written before each test, and outcomes |

## The data set for a first run

Run `D-bh-dress-20261115-043445-b782009`, directory
`/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-043445-b782009/` (its table and
particle rows are identical to those of `D-bh-dress-20261115-042653-f3da881`, which the
offline and start-time checks used; only header comments differ):

- `es.tab`: format-2 table, 6096 rows, drbar = 0.02 M, to rbar = 121.9 M, no breaks,
  `exterior = pg` (exact here); columns u (regular part of psi), KL, KT, alpha = psi^-2,
  betar = alpha rbar KT / W (areal radius frozen at t = 0; unused with `shift = zero`).
- puncture component at the same centre with **bare mass m_p = 1.0239688282062387**
  (not M: M = m_p (1 + u(0)), u(0) = -0.023407771355917872; DERIVATION.md section 4).
- `es.nrp`: 140 massless tracers (tags 0-139: 10 radii x 14 directions, at rest in the
  slice; `es.json` lists radius, energy and fate of each group), then 4,746,224 lattice
  dust particles (spacing 1 M, sites at (k + 1/2) M, u_i = 0, m = rho h^3; lattice mass
  equals the continuum dust mass 14.592802 M to 2.8e-8).
- `es_reference.csv`: exact areal radius against proper time (0 to 400 M) of the wall
  (innermost dust, R = 36 M at the start), the Schuecking shell (40 M), the outermost dust
  (106 M) and each tracer group; scale factor of the plateau; mass inside the wall (= M).
- `es.athinput`: input template (mesh, refinement and gauge are a proposal, NOT RUN).
- `es.json`: all parameters and derived numbers, sha256 of the files.

Parameters and derived numbers (`es.json`): M = 1; f = 0 for R <= R0 = 4 M, C-infinity
step to f = 1 at R1 = 36 M; dust density rising over [36, 44] M (Schuecking radius
R_w = 40 M = 20 Schwarzschild radii), Einstein-de Sitter plateau rho_0 = 3.7182e-6 M^-2
(H = 5.5812e-3/M, Hubble radius 179.2 M) out to 94 M, falling over [94, 106] M; total
mass 15.5928 M; H R_b = 0.558 (surface centre), H R_out = 0.592, 2 M_tot/R_out = 0.294;
throat at rbar = 0.5243 M (R = 2M).

Why these numbers [JUDGEMENT, reasons from the derivation]:
- The wall tens of black-hole radii out (innermost dust at 18, Schuecking radius at 20
  Schwarzschild radii). Einstein-Straus matching ties the expansion rate to the wall,
  H^2 ~ 2M/R_w^3, so the expansion time 1/H = 179 M grows as R_w^(3/2): with the wall at
  ~20 r_s the scale factor grows by 1.84 within tau = 1/H (exact, `es_reference.csv`), a
  measurable expansion within a run of a few hundred M, while the black hole's own time
  scale (~10 M; the moving-puncture trumpet settles within some tens of M [BACKGROUND]) is much shorter, so its horizon mass is read on a
  quasi-stationary hole. The wide vacuum bubble keeps the dust off the finely refined
  region around the puncture (the track's main risk, particle resolution near the
  puncture) and gives the curvature transition room (|KL|, |KT| <= 0.02/M), so that the slice is
  time-symmetric around the horizon and comoving at the wall.
- The ball inside its Hubble radius (H R_out = 0.59 < 1): then 2m/R < 1 everywhere, no
  sphere of the slice is trapped or anti-trapped, the exterior is Schwarzschild of mass
  15.6 M with the surface at 3.4 times its Schwarzschild radius (weak field at the mesh
  boundary), and the ball is still large enough for a homogeneous (exactly EdS) plateau
  between the edges.
- Smooth edges (8 M and 12 M wide): core's test 2 (`tracks/core/JOURNAL-id.md` on
  `core/id-extrinsic`, entry 4) found non-convergent Hamiltonian residuals at a sharp dust
  surface; smooth edges keep the data C-infinity and fourth-order convergent (checks below).

Checks (DERIVATION.md section 8): offline fourth-order convergence in 1D and 3D (run
`D-bh-dress-20261115-042704-f3da881`); inside AthenaK at t = 0 the code's residuals fall at
order 5.8-5.9 in the transition and 3.2 at the inner dust edge between dx = 1 and 1/2 M and
its deposited density equals the exact one (runs `D-bh-dress-20261115-043002-d51c7f2`,
`D-bh-dress-20261115-043033-4df1e76`, analysis `D-bh-dress-20261115-043406-4df1e76`).

## How to rerun

From `tracks/D-bh-dress/einstein_straus/` (Python 3.10 with numpy, scipy, sympy,
matplotlib; `python/nrpic/figstyle.py` of the repository):

    python3 nrun.py --purpose "..." --tag sym -- bash -c "python3 $PWD/sym/s1_constraints.py && python3 $PWD/sym/s2_schwarzschild_slices.py && python3 $PWD/sym/s3_ltb_wall.py"
    python3 nrun.py --purpose "..." --tag dataset --cores 8 -- python3 $PWD/make_es.py --out {out} --hp 1.0 --tau_max 400
    python3 nrun.py --purpose "..." --tag check --cores 8 -- python3 $PWD/offline_check.py --out {out} --tab <dataset>/es.tab
    EXE=/data/haiyangw/nrpic/wt/core-id/.work/build_cpu/src/athena   # format-2 reader (core/id-extrinsic)
    python3 nrun.py --purpose "..." --tag code-t0-dx1 -- bash -c "python3 $PWD/code_t0_check.py prep --tab <dataset>/es.tab --dx 1.0 --half 48 --out {out} && $EXE -i {out}/es_t0.athinput -d {out}"
    python3 nrun.py --purpose "..." --tag code-t0-analysis -- python3 $PWD/code_t0_check.py analyse --runs <run dx=1> <run dx=1/2> --out {out}

Other models: `make_es.py --Rw --w_in --Rb --w_out --R0 --R1 --hp --drbar` (w_in = 0 or
w_out = 0 gives a sharp, exactly Einstein-Straus edge written as a table break).

## Using the data in a first run (not done here)

`es.athinput` is a template: `<problem> ncomp = 2`, `comp0_type = table` (the format-2
file), `comp1_type = puncture`, `comp1_mass = m_p`, `lapse = table` (psi^-2) or
`precollapsed` (the same from the full psi), `shift = zero` (dust at rest in the
coordinates). Measure: the apparent-horizon mass (fastflow) against the proper time of the
wall tracers (tags 56-69 at R = 36 M; proper time from `trajmet.bin`); the areal radius of
each tracer group (from the tangential metric at the particle) against
`es_reference.csv`; the Misner-Sharp mass inside the wall. The null result is "horizon
mass constant within the noise floor of D-pre-4 while R_wall/R_wall(0) grows".

## Requests

- core: merge or tag the format-2 reader of `core/id-extrinsic` (my start-time check
  passed with commit 408df57); the data set needs it. A lapse condition for a puncture in
  expanding dust: the 1+log lapse obeys d_t alpha = -2 alpha K with K = -3H in the dust,
  so alpha = 1 + 6 ln a along the dust (d tau = alpha dt; exp(6 H t) only while
  alpha ~ 1; lead's correction, run D-bh-dress-20261115-145950-23fa1c7: alpha ~ 4.9 at
  tau = 200 M in this data set) and core saw lapse fronts in its test 2, while the conformal-time lapse is not
  singularity-avoiding at the puncture; a blend (e.g. 1+log near the hole, conformal-time
  in the dust, switched by chi or radius) or a 1+log condition relative to the local
  expansion is needed before a long run. The outflow boundary of Z4c assumes 1/r fields;
  the Painleve-Gullstrand exterior has K_ij ~ r^(-3/2) (core noted it, T2b (iii)).
- orchestrator: correct item 2 of `coord/notes/derivations_to_check.md` as in DERIVATION.md
  section 7 (bare puncture mass m_p = M/a, throat at the bifurcation sphere inside the
  f = 0 region, condition f = 0 at R = 2M).
- lead of D-bh-dress: choose mesh, gauge and card-hours of the first run from the template;
  no card-hours were named for this package, so no card run was made. Pending: the first
  evolution of this data set.
