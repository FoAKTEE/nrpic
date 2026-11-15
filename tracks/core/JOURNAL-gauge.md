# JOURNAL of the work package "gauge" (owner core, branch core/gauge, wave 2)

Gauge conditions for expanding matter and for unequal black holes. Labels: [VERIFIED]
read in a source at the locator given or measured in a registered run; [BACKGROUND];
[JUDGEMENT]; [TO VERIFY]. Run ids are directories under `tracks/core/runs/`; outputs
under `/data/haiyangw/nrpic/scratch/core/<run_id>/`. Analysis and figures:
`tracks/core/analysis/gauge/`.

## 2026-11-15, entry 1: what was read, the design, and the predictions

### Read

`CLAUDE.md`; `coord/CHARTER.md` to the end of "Owners"; the rulings after wave 1 and
decisions 0010 to 0015; `tracks/core/HANDOFF.md`, `STATUS.md`, `stage/G2/OPEN.md` (items
7, 9, 12); brief lines 493-553, 688-706, 834-860; the requests
`track/D-bh-dress:tracks/D-bh-dress/outbox/20261115T1510Z__to-core__lapse-for-expanding-dust.md`,
`track/A-emd-pbh:.../20261115T1320Z__to-core__phase1-generator-and-gauge-options.md` and
`...__scouting-runs-ball.md`, `track/F-hills:.../20261115T1507Z__to-core__unequal-mass-gauge.md`;
Track A's gauge study (`track/A-emd-pbh:tracks/A-emd-pbh/gauge/GAUGE.md`); Track D's
Einstein-Straus package (`README.md`, `stage/G1/STATUS.md`); `coord/INTERFACES/cosmo_gauge.md`,
`multi_puncture.md` sections 4, 8, 9; `tracks/core/JOURNAL-id.md` entries 4 to 8 and the
lead entry (the lapse front); the gauge code (`athenak/src/z4c/z4c_calcrhs.cpp` lines
687-757 before this package, `z4c.cpp`, `compact_object_tracker.*`).

### The lapse: what causes the front, and the candidates

Facts the design rests on:

1. [VERIFIED, `JOURNAL-id.md` entry 5 (f), runs core-20261115-034331/034340/034341-c9aa6d2]
   With 1+log and zero shift the central lapse of the expanding ball follows
   1 + 6 ln a up to 3.08-3.39 at t = 5.25-5.75 M and then falls to 1.5-1.7 within 0.4 to
   1 M: a front that starts at the surface, where K jumps from -3H to -3H/2. The
   conformal-time lapse does the same, slower (entry 7, T3 (iii): arrival at t = 8 M for
   the bound ball). A lapse and shift held fixed are unstable for the bound ball with a
   sharp surface (entry 8, T2e: not-a-number at t = 4.9 M).
2. [JUDGEMENT, derivation] With zero shift, d_t alpha = -2 alpha K and
   d_t ln sqrt(gamma) = -alpha K give alpha - 2 ln sqrt(gamma) = const along every
   normal observer: the 1+log lapse is the logarithm of the volume element since the
   start. Two regions that expand at different rates (ball and exterior) therefore
   acquire a lapse difference that grows without bound, 3 ln a at the surface of the
   marginally bound ball, and the gauge wave equation (speed sqrt(2 alpha)) turns the
   growing step into the front.
3. [JUDGEMENT, derivation] Subtracting a reference K_ref(t, x) (Track A's rank 3, Track
   D's "driven towards a background K(t)") gives alpha = 1 + 2 ln(sqrt(gamma)/sqrt(gamma_ref)):
   - with the unperturbed solution as reference the lapse of an overdense region
     reaches zero when its volume element is exp(-1/2) = 0.61 of the reference, a
     density contrast of 1.65, long before turnaround (contrast 5.55 for a top hat in
     Einstein-de Sitter): the slices freeze before anything collapses. Track A's toy
     found the same (GAUGE.md, C3: "background-subtracted conditions freeze a
     uniform-lapse top-hat at or before turnaround");
   - with the exact perturbed solution as reference the lapse stays 1 up to the crunch:
     no singularity avoidance;
   - a reference in (t, x) is meaningful only while t is the proper time and x is
     comoving (lapse 1, zero shift); around a black hole it has to be blended to zero by
     hand, and in Track D's vacuum bubble the geodesic observers of the transition
     region fall into the hole within 245 M (D's prediction 3), so the reference ends
     there.
   The reference is exact for the verification of an unperturbed ball and nothing else.
4. [BACKGROUND + VERIFIED by T2e] A condition that does not react to K at all where the
   matter expands (the max(0, K) and softplus conditions of arXiv:2610.23218,
   `kb-data/raw/arxiv/2610.23218/v1/src/main.tex` lines 240-250; Track A's rank 4) is
   geodesic slicing there: the Bona-Masso function f vanishes, the system is only weakly
   hyperbolic, and this code's fixed-lapse runs showed the consequence (T2e). The
   authors report that their best run with it still crashes (line 250) and that the
   softplus transition makes the lapse fall everywhere on coarse levels (line 303).
5. [JUDGEMENT] What the tracks need is a lapse that (a) keeps the principal part of
   1+log everywhere, (b) forgets slow expansion instead of integrating it, (c) is the
   plain 1+log lapse wherever the lapse is at or below its asymptotic value, so that a
   collapsing region and an existing puncture are sliced exactly as in the verified
   isolated-system runs, and (d) needs no reference solution, no stored field and no
   knowledge of where the matter is.

Decision: relaxation of the excess of the lapse,

    d_t alpha = [existing right-hand side] - (alpha/T) max(ln(alpha/alpha_0), 0),

parameters `<z4c> lapse_leak = 1/T` (default absent: term off) and `lapse_leak_alpha =
alpha_0` (default 1). Properties [JUDGEMENT, derivation; the tests below can refute
each]:

- In ln(alpha) the condition reads d_t ln alpha = -2 (K - K_m) with the memory variable
  K_m = -ln(alpha/alpha_0)/(2T), d_t K_m = (K - K_m)/T: the lapse reacts to K minus its
  own running mean over the time T (a high pass). It is the "1+log relative to the local
  expansion" that Track D asks for, with the reference built by the lapse itself.
- Homogeneous expansion: alpha tends to exp(-2 T K) = exp(6 T H), bounded, falling back
  to alpha_0 as H falls; plain 1+log gives 1 + 6 ln a.
- A surface where K jumps by dK: the lapse difference saturates at about 2 T dK
  (3 T H at the ball surface) instead of growing as 3 ln a; gauge waves are damped at
  the rate 1/(2T) (dispersion omega^2 + i omega/T = 2 alpha k^2), so a disturbance from
  the surface decays before it reaches the centre if R/sqrt(2 alpha) >> 2T.
- No derivative enters: the principal part, hence the hyperbolicity, is that of 1+log.
  Wavelengths below about sqrt(2 alpha) T propagate as in 1+log; T should be several
  cells and many time steps (the term is stiff for T below about dt/2.8).
- Where alpha <= alpha_0 the term vanishes: contraction (K > 0) and black holes are
  sliced by plain 1+log. In a vacuum puncture run the lapse does not exceed 1 except in
  an outgoing gauge pulse, so the evolution is unchanged (test P).
- The term is continuous but has a kink at alpha = alpha_0.

Not chosen, and why: K_ref(t, x) (item 3); softplus/max (item 4); the conformal-time
lapse blended with 1+log by radius or chi (Track D's first candidate: a blend needs to
know where the hole is and is a front source at the blend radius, since the two
conditions give different lapses, a and 1 + 6 ln a, for the same expansion);
`lapse_kdriver` (box mean: dominated by the exterior of a ball, GAUGE.md section 3);
`lapse_volume` (alpha - gamma^(1/6) fixed: same unbounded step at the surface);
shock-avoiding f = 1 + 1/alpha^2 (reacts to K like 1+log; no bound on the lapse).

Open by design [TO VERIFY by Track A's long collapses]: after turnaround the condition is
plain 1+log started from alpha about alpha_0, whose lapse falls with the compression of
the normal observers' volume element. For collapses that compress far more than
Oppenheimer-Snyder from a few M (Track A: a factor 17 in radius before the first trapped
sphere, G1 STATUS section 3) whether the slices reach the trapped region before they
freeze is untested here; test L3 covers a compression of 3.1.

### What a puncture inside expanding dust needs (Track D)

[JUDGEMENT] (1) the lapse above with 1+log advection and the Gamma-driver: the puncture
region has alpha < 1 and is the standard moving puncture; the dust has alpha near
exp(6 T H), 1.07 for T = 2 M at D's H = 5.58e-3/M, instead of 4.9 at tau = 200 M;
(2) `lapse = precollapsed` or `table` and `shift = zero` at the start; (3) nothing else
in the source for a run of tens of M. Not addressed in this package: an outer boundary
for the Painleve-Gullstrand exterior (K_ij as r^(-3/2)); keep the boundary further than
the light travel time of the run (`problems/ball/ball.athinput`, header).

### The shift damping

The source paper gives the profile (`refs/arxiv_2611.12831/src/main.tex` lines 388-397
[VERIFIED]): eta(x, t) = eta_0 [1 + sum_A (M_ref/m_A - 1)/(1 + |x - x_A|^2/(4 m_min^2))],
"adapting the prescription in Ref. Muller:2010zze", x_A the tracker positions, m_min the
smallest mass, M_ref the unit mass; the same factor on kappa_1. Implemented as
`<z4c> shift_eta_profile = true`, `shift_eta_mref` (M_ref, default 1),
`shift_eta_width` (default 2: the paper's 4 m_min^2), `shift_eta_width_local` (width from
m_A instead of m_min; default false), masses from `<z4c> co_<n>_mass` (written by
`puncture_setup`). The factor on kappa_1 is not implemented (no test asked for it; it
would touch the damping lines that another branch may change).

### Source

New file `athenak/src/z4c/z4c_gauge_ext.hpp` (options, the two kernel functions, the
per-stage set-up from the trackers). Hooks: `z4c.hpp` (one include, one member `gext`),
`z4c.cpp` (one line after the `shift_eta` read), `z4c_calcrhs.cpp` (one include after
`tmunu.hpp`, five lines before `is_vacuum`, four lines after the `lapse_kdriver` block,
and the damping coefficient of the shift read through a local variable). The new
parameters are read only if present and are not added to the parameter list, so headers
of output files are unchanged. `python/nrpic/expanding_ball.py`: `ltb_radius` accepts
plain numbers (Track A's report, scouting-runs-ball item 5).

### Predictions, written before any run of this package

Reference for the centre of a homogeneous region (`analysis/gauge/lapse_ref.py`, no
simulation): d ln alpha/dt = -2K(tau) - max(ln alpha, 0)/T, d tau/dt = alpha.

**R (default unchanged).** `tracks/core/tools/regress_relativistic.py` with the release
processor executable `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` against this
branch's, cases geo, boris, dep, east, os; and one vacuum puncture input with trackers
(`problems/puncture/by_binary.athinput`, a few steps) compared file by file. Prediction:
every output file identical byte for byte. Refuted by any differing file other than the
never-set bytes of restart headers (OPEN.md item 15).

**L1 (marginally bound ball, R_b = 10 M, the set-up of `JOURNAL-id.md` test 2).**
Sharp surface and smooth edge (w = 2 M); dx = 1 and 1/2 M; gauges: old 1+log ("mp"),
new with T = 1 M and T = 2 M ("leak1", "leak2"); zero shift at the start, Gamma-driver
as in `problems/ball/ball.athinput`; t = 10 M.
(a) old: reproduces entry 5: central lapse above 3 at t = 5.25-5.5 M, then below 1.8.
(b) new: the central lapse equals the reference within 2 per cent at t = 2, 4, 6, 8,
10 M: 1.235, 1.236, 1.211, 1.187, 1.169 (T = 1 M); 1.366, 1.465, 1.450, 1.406, 1.362
(T = 2 M; within 3 per cent); the largest lapse on the mesh stays below 1.30 (T = 1 M)
and 1.55 (T = 2 M); no fall of the central lapse.
(c) new, sharp surface: largest |eps| (areal radius of the tracked shells against the
exact solution at equal proper time) over the whole run at most twice the numbers of
the conformal-time lapse of entry 5 in every group: core 6.6e-3 and 2.2e-3, mid 6.0e-3
and 2.8e-3, outer 9.0e-3 and 3.4e-3, surface 1.4e-2 and 8.0e-3 at dx = 1 and 1/2 M
(old 1+log: core 7.9e-2, 7.7e-2). Smooth edge: all groups below 3e-3 at dx = 1/2 M.
(d) new: largest coordinate speed of light at the ball particles below 1.4 (old 2.3).
Refuted by: a central lapse more than 5 per cent off the reference at any t <= 10 M
(a front), or a core error above 1e-2 at dx = 1/2 M, or a run that ends early.

**L2 (bound ball to its turnaround, R_b = 5 M, e0 = 0.16, sharp, `JOURNAL-id.md` test
3).** dx = 1/2 M (and 1/4 M if a card is free), t = 12 M, new lapse with T = 1 M.
Reference central lapse 1.246, 1.177, 1.098, 1.036, 0.979, 0.857 at t = 2 ... 12 M.
Prediction: central lapse within 3 per cent of the reference until t = 10 M (the
conformal-time run departs at t = 6 M, rising to 1.33 and falling to 0.69); largest
areal radius of every shell group within 1 per cent of 1.25 R_0 at dx = 1/2 M; largest
|eps| over the run below 2e-2 in every group at dx = 1/2 M (conformal time: core 0.20).
Refuted by a departure of the central lapse above 10 per cent before t = 10 M or a core
error above 5e-2.

**L3 (the same ball through its collapse; "still collapses at a forming black hole").**
Refined mesh (cells M/8 inside 3 M), new lapse T = 1 M, to t = 45 M; exact: surface at
R = 2M at tau = 25.408 M, crunch at 26.897 M (Track A's cross-check of three codes,
scouting-runs-ball item 5). Prediction: the central lapse falls below 0.05; an apparent
horizon is found; its mass is within 3 per cent of the ball mass M = 1 once the surface
shells are inside and constant to 1 per cent over the last 5 M; the tracked surface
shells follow the cycloid to R = 2.5 M with |eps| below 3 per cent, at tau = 24.6 M
exact. Refuted by: no horizon before t = 45 M, a horizon mass off by more than 10 per
cent, or shells off by more than 10 per cent at R = 2.5 M. The same with old 1+log for
comparison [JUDGEMENT: it also forms a horizon, with larger shell errors].

**P (puncture alone; Track D's smallest acceptable answer).** One vacuum puncture, cells
m/8, standard gauge, with and without `lapse_leak = 1`, 20 M on processors. Prediction:
the lapse never exceeds 1 by more than 1e-3, so the two runs agree: horizon masses equal
within 1e-6 at every search (identical files if the lapse never exceeds 1). Then the
500 M history of D-pre-4 (run D-bh-dress-20261115-121313-284ec4f) holds for the new
lapse by construction. Refuted by a horizon-mass difference above 1e-5.

**ES (Einstein-Straus data, Track D's generator; a few tens of M).** New lapse.
Prediction: (1) apparent-horizon mass constant: |M_AH(t)/M_AH(10 M) - 1| below 1e-3 for
10 M <= t <= end at cells M/8 (the exact statement is M_AH = M on every slice); (2) the
wall tracers follow the exact curve R_w(tau) to 5e-3; (3) the lapse in the dust plateau
equals the reference of `lapse_ref.py` within 3 per cent and stays below
exp(6 T H_0) + 0.02; (4) no dust particle enters the bubble. Refuted by a horizon-mass
drift above 3e-3 or a wall error above 2 per cent. Parameters of the data set and the
numbers of (2) are written into entry 2 before the run.

**E1 (shift damping, one hole).** Hole of unit mass with momentum; by scaling, a hole of
mass m with eta_0 in units of M_ref is the unit hole with eta m. Runs: (a) eta = 2
constant (reference); (c) eta = 20 constant (a heavy hole in the units of a light one;
wave 1 measured a tracker 9 times slower); (d) eta_0 = 20 with the profile and
M_ref = 0.1 (eta = 2 at the hole, 20 far away). Prediction: tracker speed of (d) within
20 per cent of (a) at t = 5 m, while (c) is at least 5 times slower; horizon mass of
(d) within 1e-3 of (a). Refuted by (d) more than 50 per cent off (a).

**E2 (unequal boosted pair, mass ratio 4, a few M).** m_1 = 1, m_2 = 0.25, Bowen-York
momenta, `puncture_setup`; constant eta = 2 (= 2/m_1), constant eta = 8 (= 2/m_2), and
the profile with eta_0 = 2, M_ref = 1 (eta = 8 at the light hole). Prediction: with the
profile the tracker speed of the heavy hole equals that of the eta = 2 run within 5 per
cent and that of the light hole equals that of the eta = 8 run within 15 per cent, at
the end of the run; both horizons are found in every search, masses within 2e-3 of the
constant-eta runs; constraint norms within a factor 1.5 of them. Refuted by a light
tracker more than 40 per cent off the eta = 8 run or a lost horizon.

## 2026-11-15, entry 2: set-up of the runs, and the numbers of prediction ES

Written before any result of this package was read (the first processor runs were
started at 15:46 UTC and had not finished).

Registration. `harness/bin/nrpic-run submit` (and `budget`) end with
`KeyError: 'outputs'` in `budget_state` -> `is_live` (line 163): the command reads the
hand-written manifests of wave 1 under `tracks/core/runs/`, which have no `outputs`
entry. Runs of this package are therefore registered by hand through
`tracks/core/analysis/gauge/grun.py` (a copy of `analysis/id/nrun.py` with UTC run ids
and a `--source-commit` option) and by `tracks/core/tools/run_registered.py` (the
regression). `harness/bin/nrpic-env create --no-kokkos` worked (venv hash 0279f117...).

Executables. `.work/build_cpu`, `.work/build_gpu` of this worktree, built from the
working tree whose `athenak/src` equals commit e41c24a (`git diff e41c24a HEAD --
athenak/src` is empty); copies pinned for the card jobs:
`/data/haiyangw/nrpic/scratch/core/gauge/exe/athena_{cpu,gpu}_e41c24a` (sha256
8ac29c06..., 6ce2268c...).

Processors. The serial processor executable does about 1.2e4 zone-cycles per second
(64^3 ball: 22 s per cycle), so processors carry only the 64-cell ball runs and the bound
ball at 80 cells (1.7 h); everything else waits for a card. The queue held six jobs of
other sessions when this was written. Two processor runs of the first batch
(`bound-mp-n080`, `bound-ct-n080`: old lapses on the bound ball, already measured in wave
1 as `t3-bound-ct-n080/-n160`, `t3-bound-mp-n160`) were stopped by process id after five
minutes to free two cores for input checks; their manifests record the non-zero exit.

Card plan (at most one card-hour): job 1 (`analysis/gauge/gpu_job1.sh`): L1 at cells
M/2 (five runs), L2 at M/4 (two runs), L3, ES; job 2 (`gpu_job2.sh`): E2 (three runs),
E1 (three runs), P (two runs), E1 under-damped side (two runs). Estimated 37 minutes of
card time in all [JUDGEMENT from 8e6 zone-cycles per second, `multi_puncture.md`
section 5].

Inputs written for the tests: `problems/ball/ball_leak.athinput` (L1, L2),
`problems/ball/ball_collapse.athinput` (L3: mesh, refinement, deposit rules, excision and
finder of `problems/os/os_amr.athinput` at this problem's scale),
`problems/puncture/by_eta.athinput` (P, E1), `problems/puncture/by_unequal.athinput`
(E2), `problems/es/es_gauge.athinput` (ES).

Test E1, amendment written before its runs: the under-damped side is added, (b) constant
eta = 0.2 (a light hole in the units of a heavy one: Track F's members at eta m = 0.1)
and (e) eta_0 = 0.2 with the profile and M_ref = 10 (eta = 2 at the hole). Prediction
[JUDGEMENT, weak]: the tracker of (b) is not slower than that of (a); (e) lies within
20 per cent of (a) at t = 5 m.

### Prediction ES, with numbers

Data set: Track D's generator at commit 3276791 of `track/D-bh-dress`
(`tracks/D-bh-dress/einstein_straus/make_es.py --Rb 56 --w_out 4 --hp 2.0 --tau_max 60`,
copied to `scratch/core/tmp/gauge/es_tools/`), output
`/data/haiyangw/nrpic/scratch/core/gauge/ic_es/` (`es.json`: M = 1, bare puncture mass
1.0239688282062387, wall (innermost dust) at 36 M, Schuecking radius 40 M, plateau
H = 5.5812e-3/M, outermost dust 60 M, total mass 2.7397 M, 87128 dust particles on a
lattice of 2 M, 140 tracers). This is the parameter set Track D names for ES-1 (G1
STATUS), with a lattice of 2 M instead of 1 M. Mesh of `es_gauge.athinput`: cells 2 M
over the whole mesh (half-width 96 M), halving to M/8 within 2 M of the puncture. Gauge:
1+log with advection, `lapse_leak = 0.25` (T = 4 M), Gamma-driver eta = 2, start lapse
psi^-2, zero shift. 30 M of coordinate time.

Exact references (`es_reference.csv`): wall tracers (tags 56-69, R_0 = 36 M) at
38.318, 40.574, 42.763 M at tau = 10, 20, 30 M; tracers at R_0 = 6 M (tags 0-13) reach
R = 2M near tau = 15.0 M (R = 1.855 M at tau = 15 M); tracers at 48 M (tags 84-97, in
the plateau) at 50.640, 53.221, 55.733 M. Reference lapse of the plateau (the equation of
`lapse_ref.py` with H(tau) of the plateau and the start value psi^-2 = 0.979 at
r = 48 M): 1.090, 1.121, 1.125, 1.123, 1.119, 1.114 at t = 5, 10, 15, 20, 25, 30 M
(plain 1+log: 1.153, 1.349, 1.565, 1.801, 2.055, 2.326).

Prediction: (1) |M_AH(t)/M_AH(10 M) - 1| below 1e-3 for 10 M <= t <= 30 M;
M_AH(10 M) within 5e-3 of M = 1 (Track D expects +1.5e-3 at cells M/8); (2) wall tracers
within 5e-3 of the exact radius at their proper time up to the end (cells of 2 M at a
wall of 36 M); the tracers at 48 M within 3e-3; (3) the lapse at the tracers at 48 M
within 3 per cent of the reference above, and the largest lapse on the mesh below 1.16;
(4) the smallest areal radius of a dust particle at t = 30 M is not below the wall
tracers' radius by more than one cell (2 M); (5) the tracers of the group at 6 M are
removed (lapse excision at 0.05) at a proper time between 13 and 16 M. Refuted by a
horizon-mass drift above 3e-3, a wall error above 2 per cent, a dust lapse above 1.3, or a
run that ends early.

## 2026-11-15, entry 3: outcome of R (first version refuted, source restructured), first outcome of L1

### Outcome of prediction R: REFUTED for the first version of the source, then met

First version (commit e41c24a: the two terms inside the main loop of `Z4c::CalcRHS`,
guarded by flags that are false by default). Processor runs, release executable
`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` against this branch's:

| case | baseline run | new run | outcome |
|---|---|---|---|
| geo | core-20261115-154506-e41c24a | -154507-e41c24a | identical (2 files) |
| boris | -154508-e41c24a | -154509-e41c24a | identical (2 files) |
| dep | -154510-e41c24a | -154516-e41c24a | identical (1 file) |
| east | -154521-e41c24a | -154530-e41c24a | 10 of 12 files differ |
| os | -154538-e41c24a | core-20261115-155025-63ad8eb | `os.nrpic.hst` and 4 restart files differ |

Size of the differences: east, relative 9.6e-11 in the constraint statistics after 20
steps (from the fourth step on); os, relative 3.8e-16 in one column of one record. So
the prediction failed: with both terms switched off the results were not bit-identical.
Check that it is this source and not the build: a processor build of the unchanged
source of main (`git archive 4ebb05f`, `.work/build_cpu_base`) reproduces the release
executable byte for byte on case east (runs core-20261115-155802/-155811-dc7406f) and
differs from the first version in the same ten files (-155744/-155753-dc7406f).
Cause [JUDGEMENT, not isolated further]: statements added inside the kernel change how
the compiler contracts or orders the floating-point operations of the neighbouring,
unchanged statements; the cases without Z4c (geo, boris, dep) were unaffected.

Second version (commit b4430da): the main loop of `Z4c::CalcRHS` is restored to the
text of main; the two terms are added to the right-hand sides of the lapse and the shift
in a loop of their own after it (`AddGaugeExt` in `z4c_gauge_ext.hpp`; for the shift
the loop subtracts (eta(x) - eta_0) beta^i), which runs only if a term is switched on.
Hooks now: `z4c_calcrhs.cpp` one include after `tmunu.hpp` and one call (four lines)
before the dissipation loop; `z4c.hpp`, `z4c.cpp` as before. Outcome: geo, boris, dep,
east identical byte for byte against the release executable (working tree of b4430da:
runs core-20261115-160007 ... -160030-dc7406f; committed source, executable
`scratch/core/gauge/exe/athena_cpu_b4430da`: table below when case os has finished).

Consequence for the runs: the card jobs submitted with the first version (4445, 4446)
were cancelled before they started and resubmitted with the executable of b4430da
(4449, 4450). The eight 64-cell ball runs of the first batch used e41c24a; the terms
are the same formulas there, so they stand as scouting results, and `leak05-n064` is
repeated with b4430da as a check of the second version.

### Processor versions of P, E1, E2 (set-up note written when they were started)

Twelve jobs of other sessions are ahead of the two card jobs. So that the puncture
tests do not depend on the queue they also run on processors on a small mesh
(`analysis/gauge/punc_cpu_runs.sh`: half-width 32 instead of 64, MeshBlocks of 8^3,
same root cells, levels and gauge; P to t = 10 M, E1 to t = 5 m, E2 to t = 2 M; tags
`g-p-*`, `g-e1-*`, `g-e2-*`). The predictions of entry 1 apply unchanged, read at the
end of these shorter runs (E1 at t = 5 m as written; E2 at t = 2 M, which is 8 masses
of the light hole and 2 of the heavy one). L3 and ES have no processor version: 14 h
and 11 h at 1.2e4 zone-cycles per second.

### Outcome of L1 at cells of 1 M (processors, executable e41c24a)

Runs: `mp-n064` core-20261115-154608-63ad8eb, `mp-edge2-n064` -154603-, `leak1-n064`
-154607-, `leak1-edge2-n064` -154610-, `leak2-n064` -154605-, `leak2-edge2-n064`
-154613-, `leak05-n064` -154612-, `leak4-n064` -154611- (14 minutes each). Analysis
`analysis/gauge/ball_analysis.py`, numbers `ball_numbers_g.json`, figures
`figs/ball_g_sharp_dx1.png`, `ball_g_sharp_lapse_profiles.png` (both looked at),
`ball_g_edge2_dx1.png`, `ball_g_edge2_lapse_profiles.png`.

(a) Old 1+log: central lapse 2.48 at t = 4 M, peak 3.08 near t = 5.3 M, 1.76 at t = 8 M,
1.68 at t = 10 M (reference without front 3.46, 4.47, 5.46): the front of wave 1.
Confirmed.

(b) New lapse, central lapse / reference at t = 2, 4, 6, 8, 10 M, sharp surface:

| T | t = 2 | 4 | 6 | 8 | 10 | largest deviation, t <= 10 M | largest lapse on the mesh |
|---|---|---|---|---|---|---|---|
| 0.5 M | 1.126/1.126 | 1.112/1.112 | 1.100/1.100 | 1.089/1.090 | 1.080/1.082 | 0.2 per cent | 1.127 |
| 1 M | 1.235/1.235 | 1.236/1.236 | 1.211/1.211 | 1.167/1.187 | 1.136/1.169 | 2.8 per cent (t = 10 M) | 1.245 |
| 2 M | 1.365/1.366 | 1.464/1.465 | 1.453/1.450 | 1.241/1.406 | 1.186/1.362 | 13 per cent (t = 8.75 M) | 1.469 |
| 4 M | 1.476/1.477 | 1.759/1.762 | 1.829/1.863 | 1.293/1.853 | 1.253/1.793 | 30 per cent (t = 8.25 M) | 1.864 |

Prediction (b) holds for T = 1 M up to t = 8 M and fails by 0.8 per cent at t = 10 M
(2.8 against the predicted 2 per cent; below the 5 per cent that would refute "no
front"); it FAILS for T = 2 M (13 per cent). The bounds on the largest lapse hold
(1.245 < 1.30, 1.469 < 1.55). What happens instead of a front (figure
`ball_g_sharp_lapse_profiles`): the lapse stays monotone in radius; the step at the
surface spreads inwards smoothly and the central plateau shrinks (to r = 6.5 M at
t = 2 M, 4 M at t = 4 M, gone at t = 6 M); the centre then relaxes towards the lower
exterior value. The disturbance scales with T: its size at the centre is 0.03, 0.17,
0.5 for T = 1, 2, 4 M. My estimate of the damping (rate 1/(2T) for waves) missed that
slow changes spread diffusively with the coefficient 2 alpha T. Smooth edge: the same
numbers within 0.002 (T = 1 M: 2.9 per cent at t = 10 M).

(c) Largest |eps| over the whole run, cells of 1 M, sharp surface:

| lapse | core | mid | outer | surface |
|---|---|---|---|---|
| old 1+log | 7.9e-2 | 8.5e-3 | 5.8e-3 | 9.7e-3 |
| conformal time (wave 1, entry 5 of JOURNAL-id) | 3.3e-3 | 3.0e-3 | 4.5e-3 | 7.2e-3 |
| new, T = 0.5 M | 1.7e-3 | 8.2e-4 | 2.8e-3 | 6.1e-3 |
| new, T = 1 M | 3.1e-3 | 1.3e-3 | 3.3e-3 | 6.7e-3 |
| new, T = 2 M | 7.1e-3 | 2.1e-3 | 3.9e-3 | 7.5e-3 |
| new, T = 4 M | 1.4e-2 | 2.9e-3 | 4.3e-3 | 8.2e-3 |

Prediction (c) at cells of 1 M holds for T = 1 M (all groups below twice the
conformal-time numbers; in fact at or below them) and for T = 0.5 M; for T = 2 M the
core (7.1e-3) is above the bound 6.6e-3. Smooth edge, T = 1 M: core 1.7e-3, mid 1.1e-3,
outer 1.9e-3, edge 4.2e-4 (old 1+log: core 2.6e-2).

(d) Largest coordinate speed of light at the ball particles: 1.07 (T = 0.5 M), 1.14
(T = 1 M), 1.24 (T = 2 M), 1.42 (T = 4 M); old 2.27. Confirmed for T <= 2 M.

Reading [JUDGEMENT]: the relaxation time has to be short compared with the light
crossing time of the expanding region and with 1/(6H): here T = 0.5 to 1 M for a ball
of 10 M with H = 0.045/M (6 T H = 0.13 to 0.27). T = 0.5 M is two time steps and half a
cell at this resolution and shows no instability in 10 M. The runs at cells of M/2
(card job 1, and `leak1-n128` on processors) and the bound ball decide the
recommendation.

### Amendment of prediction ES (3), written before the run (card job still queued)

The one-cycle check of the input (run core-20261115-155407-e41c24a) shows that the lapse
of the table is 1 in the flat dust region (1.0000000008 at the wall tracers; the regular
part of psi cancels the puncture term there), not psi^-2 = 0.979 as I assumed in
entry 2. The reference lapse of the plateau therefore starts at 1
(`es_collapse_analysis.ref_plateau`, H_0 = 5.5812e-3/M): 1.098, 1.123, 1.126, 1.123,
1.119, 1.114 at t = 5, 10, 15, 20, 25, 30 M for T = 4 M (plain 1+log: 1.178, 1.377,
1.598, 1.838, 2.096, 2.371); proper time of the plateau 10.86, 22.11, 33.29 M at
t = 10, 20, 30 M. The criterion (within 3 per cent, largest lapse below 1.16) is
unchanged. The analysis takes the start value from the tracers. (The first commit of
this paragraph, 30 seconds earlier, carried numbers typed before the script had printed
them; these are the printed ones.)

### Added run, with its prediction (written before it started)

`bound-leak025-n080`: the bound ball at cells of M/2 with T = 0.25 M (two time steps),
to see where short relaxation times stop working. A first look at the running bound-ball
jobs (not yet analysed) shows the central lapse below the homogeneous reference at
t = 4 M by 2 per cent (T = 0.5 M), 15 per cent (T = 1 M) and 35 per cent (T = 2 M): the
disturbance from the surface reaches the centre of this compact ball in about 3 M and
grows steeply with T. Prediction for T = 0.25 M [JUDGEMENT]: stable to t = 12 M; central
lapse within 1.5 per cent of its reference until t = 9 M; shell errors not larger than
with T = 0.5 M. Refuted by an instability (growth of the Hamiltonian residual by more
than ten between t = 2 M and t = 12 M, or not-a-number), which would mean that the
relaxation must not be faster than a few time steps.
