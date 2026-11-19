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

### Second amendment of test ES, written before the run (card job 4449 still queued)

The first look at the bound-ball runs shows where the disturbance of the new lapse
comes from: it reaches the centre at t = 3 to 4 M, the travel time of a gauge wave from
the surface at speed sqrt(2 alpha), as one dip (central lapse 1.42 -> 0.85 -> 1.34 at
t = 3, 4, 5 M for T = 2 M; 1.228 -> 1.005 for T = 1 M; 1.105 -> 1.056 for T = 0.5 M).
It is the start-up of the relaxation: the run starts with lapse 1 everywhere, the
lapse rises to its local equilibrium within about T, and where the equilibrium differs
(across the surface) a pulse leaves, of a size that grows faster than linearly with T.
For the Einstein-Straus run I therefore halve the relaxation time: T = 2 M
(`lapse_leak = 0.5` in `problems/es/es_gauge.athinput`, T H = 0.011; tag `gc-es-leak2`).
The queued job reads the input when it starts. Reference lapse of the plateau for T = 2 M
(`ref_plateau`): 1.062, 1.064, 1.062, 1.060, 1.057, 1.055 at t = 5, 10, 15, 20, 25, 30 M,
largest 1.064; proper time 10.53, 21.15, 31.72 M at t = 10, 20, 30 M. Prediction (3)
becomes: lapse at the tracers at 48 M within 2 per cent of these values, largest lapse
on the mesh below 1.09. The other items of prediction ES are unchanged.

### Amendment of test L3, written before the run

For the same reason the collapse run uses T = 0.5 M instead of 1 M (`lapse_leak = 2.0` in
`problems/ball/ball_collapse.athinput`; tag `gc-collapse-leak05`). Its prediction is
unchanged. Card job 4449 keeps the script text of its submission, which names T = 4 M
for ES and T = 1 M for L3; those two steps are disabled through
`analysis/gauge/skip_tags.txt` (read by `grun.py`), and ES and L3 run in a third job
(`gpu_job3.sh`) with the relaxation time on the command line.

### Two more runs at cells of 1 M, with their prediction (written before they started)

`leak025-n064` and `leak0125-n064`: the marginally bound ball with T = 0.25 M and
0.125 M (rate times step 1 and 2; the explicit fourth-order Runge-Kutta step is stable
for a pure decay up to 2.78). They probe how short the relaxation time may be relative
to the cell (T = dx/4, dx/8): for T -> 0 the lapse is pinned to 1 where the matter
expands, which is the fixed-lapse gauge that failed in wave 1 (T2e: surface-shell
errors 1.9e-2 at cells of M/2, instability for the bound ball). Prediction [JUDGEMENT]:
T = 0.25 M runs to t = 10 M with the central lapse within 1 per cent of its reference
and shell errors not above those of T = 0.5 M; T = 0.125 M runs to the end but its
surface and outer shells are worse than with T = 0.5 M (above 1e-2), the signature of
the fixed-lapse gauge. Refuted for T = 0.125 M if its errors equal those of T = 0.5 M
(then there is no lower limit of T at this resolution other than the step).

## 2026-11-15, entry 4 (new session, 17:56 UTC): card jobs, outcomes of L1 at M/2 and L2

### Card jobs 2 and 3 never ran; resubmitted

Job 4449 (job 1) ran 3 min 17 s and did L1 at cells of M/2 and L2 at M/4. Jobs 4450
(job 2: E1, E2, P) and 4457 (job 3: ES, L3) ended within one second: `grun.py` stopped
with "unrecognized arguments: -t 00:05:00" (argparse reads the athena wall-clock option
`-t` inside the `--athinput` list as an option of its own). Fix: `grun.py --walltime
HH:MM:SS`, passed to athena as `-t`; job scripts changed accordingly. Resubmitted at
17:58 UTC as 4477 (job 3) and 4478 (job 2), behind 15 jobs of other sessions. Card time
used so far by this package: 0.055 card-hours (manifests of job 1).

The repeated `leak05-n064` with the executable of b4430da (run
core-20261115-160343-b4430da) agrees with the first version's run
(core-20261115-154612-63ad8eb) to 2e-12 relative in the constraint statistics; the only
other differences are the momentum sums of `ball.nrpic.hst`, which are zero to 1e-17 in
both. So the two source versions give the same physics, as entry 3 assumed.

Analysis runs: core-20261115-175857-3f710a3 (processor runs, `ball_numbers_g.json`),
core-20261115-175934-3f710a3 (card runs, `ball_numbers_gc.json`); figures
`figs/ball_gc_sharp_dx0p5.png`, `figs/ball_gc_bound_dx0p25.png` (both looked at).

### Outcome of L1 at cells of M/2 (card; runs core-20261115-170439/-170456/-170513/-170529/-170546-b4430da)

(a) Old 1+log (`mp-n128`): central lapse 2.485 at t = 4 M, peak 3.24 near t = 5.6 M, 1.76
at t = 8 M (reference without front 4.47); the front of wave 1. Confirmed.

(b) Central lapse / reference at t = 2, 4, 6, 8, 10 M: T = 1 M 1.235/1.235,
1.236/1.236, 1.210/1.211, 1.165/1.187, 1.136/1.169 (largest deviation 2.8 per cent at
t = 10 M); T = 2 M 1.366/1.366, 1.464/1.465, 1.450/1.450, 1.223/1.406, 1.186/1.362
(13 per cent at t = 8 M). The same numbers as at cells of 1 M within 0.002: the
departure is a property of the gauge (the slow inward spreading of the lower exterior
lapse, entry 3), not of the resolution. Prediction (b): fails by 0.8 per cent at
t = 10 M for T = 1 M (2.8 against 2), FAILS for T = 2 M; no front in either (no fall of
the central lapse below its value at the surface; largest lapse 1.245 and 1.468, below
the bounds 1.30 and 1.55).

(c) Largest |eps| over the run at cells of M/2 (bounds of the prediction in brackets:
twice the conformal-time numbers of wave 1):

| run | core | mid | outer | surface |
|---|---|---|---|---|
| old 1+log, sharp | 7.65e-2 | 2.74e-3 | 3.63e-3 | 5.62e-3 |
| new T = 1 M, sharp | 1.16e-3 (2.2e-3) | 5.81e-4 (2.8e-3) | 2.02e-3 (3.4e-3) | 4.12e-3 (8.0e-3) |
| new T = 2 M, sharp | 2.07e-3 | 8.62e-4 | 2.46e-3 | 4.48e-3 |
| old 1+log, edge 2 M | 1.20e-2 | 1.26e-3 | 1.44e-3 | 3.55e-4 |
| new T = 1 M, edge 2 M | 5.93e-4 | 2.97e-4 | 5.11e-4 | 1.69e-4 |

Prediction (c) holds for T = 1 M in every group, and for the smooth edge (all below
3e-3). The new lapse converges: core 3.08e-3 -> 1.16e-3 from cells of 1 M to M/2 (T = 1
M), 1.73e-3 -> 5.9e-4 with the smooth edge; the old 1+log does not (core 7.9e-2 ->
7.65e-2: the error is made by the front).

(d) Largest coordinate speed of light at the ball particles: 1.134 (T = 1 M), 1.244
(T = 2 M), 2.32 (old). Confirmed.

### Outcome of L2 (bound ball to turnaround, cells of M/4, card; runs core-20261115-170602-b4430da (T = 0.5 M), -170659- (T = 1 M))

Prediction (T = 1 M): central lapse within 3 per cent of the reference until t = 10 M;
largest areal radius of every group within 1 per cent of 1.25 R_0; largest |eps| below
2e-2 in every group. Outcome for T = 1 M: the central lapse dips from 1.21 to 0.93 at
t = 4.2 M and returns to 1.13 at t = 5.8 M (largest deviation 20 per cent): REFUTED (the
refutation threshold was 10 per cent). Turnaround: largest R/R_0 1.2463 (core), 1.2476,
1.2478, 1.2489 (surface), within 0.3 per cent of 1.25: confirmed. Largest |eps|: core
3.26e-2 (FAILS 2e-2), mid 4.38e-3, outer 5.84e-3, surface 6.70e-3.
With T = 0.5 M: largest deviation of the central lapse 3.9 per cent (t = 4.4 M), a step
of 5 per cent instead of a dip; turnaround 1.2478 to 1.2496; |eps| core 9.22e-3, mid
2.50e-3, outer 4.33e-3, surface 6.41e-3. For comparison, the conformal-time lapse of
wave 1 at the same resolution (`JOURNAL-id.md` entry 7): core 0.11, mid 2.6e-2, outer
1.7e-2, surface 1.3e-2. So T = 0.5 M improves the invariant errors of the bound ball by
a factor 2 to 12 over the best lapse of wave 1, and T = 1 M is too long for a ball of
5 M: the start-up pulse of the relaxation (entry 3, second amendment) reaches the
centre at t = 4 M, focused by the spherical geometry, and leaves the core 3.5 times
worse than with T = 0.5 M.

### Outcome of the short relaxation times (processors)

- `bound-leak025-n080` (core-20261115-161021-b4430da, T = 0.25 M, cells M/2, t = 12 M):
  stable (mean |H| 7.1e-4 at t = 2 M, 1.65e-3 at t = 12 M: growth 2.3, below the 10 of the
  refutation); central lapse within 1.4 per cent of its reference until t = 9 M (predicted
  1.5): confirmed; |eps| core 1.25e-2, mid 8.9e-3, outer 1.19e-2, surface 1.09e-2;
  turnaround 1.2434 to 1.2469. "Not larger than with T = 0.5 M" cannot be judged: no
  T = 0.5 M run at this resolution (added below).
- `leak025-n064` (core-20261115-163712-b4430da) and `leak0125-n064`
  (core-20261115-161716-b4430da), marginally bound ball, cells of 1 M: central lapse
  within 0.04 and 0.7 per cent of its reference; |eps| core 9.1e-4 and 8.3e-4, mid 8.3e-4
  and 1.0e-3, outer 2.82e-3 and 2.34e-3, surface 5.50e-3 and 6.00e-3 (T = 0.5 M: 1.67e-3,
  8.2e-4, 2.78e-3, 6.05e-3). T = 0.25 M: confirmed (equal to T = 0.5 M within 2 per cent
  in the outer group, better in the core). T = 0.125 M: my prediction (outer and surface
  above 1e-2, the fixed-lapse signature) is REFUTED: the errors equal those of T = 0.25
  to 0.5 M. At this resolution and with the Gamma-driver shift, there is no lower limit
  of T other than the stiffness of the step (rate x step = 2 here). The fixed-lapse
  failure of wave 1 (T2e) had a fixed shift as well; the relaxation keeps the 1+log
  principal part, which a fixed lapse does not.

### Predictions for two more bound-ball runs (written before they started)

`bound-leak05-n080` and `bound-leak0125-n080` (processors, cells M/2, t = 12 M), so that
the bound ball has T = 0.125, 0.25, 0.5 M at one resolution. [JUDGEMENT] T = 0.5 M:
central lapse deviation up to t = 9 M 3 to 5 per cent (3.9 at cells M/4: the deviation
does not depend on the resolution, as in L1); core |eps| above that of T = 0.25 M
(1.25e-2), between 1.3e-2 and 2.5e-2. T = 0.125 M: stable (mean |H| grows by less than
10 from t = 2 to 12 M), central lapse within 1 per cent of the reference up to t = 9 M,
core |eps| within 20 per cent of T = 0.25 M. Refuted if the core error of T = 0.5 M is
below that of T = 0.25 M (then the core error at cells M/2 is set by the resolution,
not by the start-up pulse).

### Outcome of R, last part: vacuum binary with trackers (prediction of entry 1)

`problems/puncture/by_binary.athinput` (two Bowen-York punctures, trackers and horizon
finder from `puncture_setup`; small mesh: half-width 32, 32 root cells, MeshBlocks 8^3,
five levels, 12 cycles, every output written every cycle): release processor executable
(run core-20261115-180234-3f710a3) against this branch's `athena_cpu_b4430da`
(core-20261115-180234-b4430da). All 19 output files identical byte for byte (14 lapse
dumps, both tracker files, both horizon summaries, the constraint history). Confirmed:
with the new parameters absent, the tracker path of `MakeGaugeExt` and the extra loop
change nothing.

### Outcome of P on processors (half-width 32, cells m/8, t = 10 M)

Runs core-20261115-160341-b4430da (`g-p-leak1`, T = 1 M) and -160344- (`g-p-plain`).
The tracker file, the horizon summary (19 searches, mass 1.0000 to 1.000174 in both),
the horizon shape and the constraint history are identical byte for byte; the four lapse
and constraint dumps differ in one byte each, the value of `lapse_leak` in the parameter
dump of the header (offsets 1593-1599; the data parts are identical). So the lapse never
exceeded 1 anywhere in 10 M and the term never acted. Prediction P: confirmed.
For Track D's 500 M history (run D-bh-dress-20261115-121313-284ec4f): its `punc.nrpic.hst`
column 30 is the largest lapse over all active cells of the mesh
(`athenak/src/particles/nrpic_io.cpp` lines 205-238) [VERIFIED]; over 1601 records from
t = 0 to 500 M it lies between 0.99530 and 0.99722. Since the term is exactly zero for
alpha <= 1, that run is what `lapse_leak` would give [JUDGEMENT: the records are 0.3125
M apart; between them the lapse would have to rise by 2.8e-3 above every recorded value].

## 2026-11-15, entry 5: outcome of E1 on processors; the width of the damping profile

### Outcome of E1 (one boosted hole, m = 1, small mesh, t = 4.9 m; analysis run core-20261115-183240-4a9b0b8, figure `figs/punc_g_e1.png`, looked at)

Runs: (a) eta = 2 core-20261115-160350-b4430da, (c) eta = 20 -160351-, (d) eta_0 = 20
with the profile and M_ref = 0.1 -160349-, (b) eta = 0.2 -160355-, (e) eta_0 = 0.2 with
the profile and M_ref = 10 -160346-. Tracker speed (ratio to (a)) at t = 1.6, 3.0, 4.9 m:

| run | eta at the hole / far away | 1.6 m | 3.0 m | 4.9 m |
|---|---|---|---|---|
| (a) | 2 / 2 | 0.0514 | 0.0843 | 0.1069 |
| (c) | 20 / 20 | 0.0060 (0.12) | 0.0153 (0.18) | 0.0231 (0.22) |
| (d) | 2 / 20, width 2 m | 0.0325 (0.63) | 0.0486 (0.58) | 0.0587 (0.55) |
| (b) | 0.2 / 0.2 | 0.1011 (1.97) | 0.1748 (2.07) | 0.2109 (1.97) |
| (e) | 2 / 0.2, width 2 m | 0.0551 (1.07) | 0.0986 (1.17) | 0.1357 (1.27) |

Horizon mass at the end 1.01108 to 1.01110 in all five (20 searches each), Hamiltonian
norms within 20 per cent of each other. Prediction: (d) within 20 per cent of (a):
FAILS (45 per cent slower; not refuted by the 50 per cent threshold); (c) at least 5
times slower than (a): fails narrowly (4.6 times at 4.9 m, 8.6 times at 1.6 m); horizon
mass of (d) within 1e-3 of (a): confirmed (1e-5); (b) not slower than (a): confirmed
(twice as fast); (e) within 20 per cent of (a): FAILS narrowly (27 per cent at 4.9 m,
7 and 17 per cent at 1.6 and 3 m). Reading [JUDGEMENT]: the profile of the paper (width
2 m) moves the tracker speed most of the way from the constant-eta value towards the
value of the hole's own units, but not all the way: the shift that carries the puncture
builds up over a region of several m, where the profile has already risen (falling)
towards eta_0 (at r = 2 m the factor is half-way). None of these speeds has settled at
t = 5 m (all still rising; the physical speed of this hole is about 0.3), so the
comparison is of the transient, which is what slowed the heavy tracker in wave 1.
Case (e) is Track F's light member scaled to its own units (eta m = 0.2 far away, 2 at
the hole: Track F's q = 10 input with shift_eta = 2/M, M_ref = M): constant eta leaves
it 97 per cent off the eta m = 2 reference, the profile 27 per cent.

### Prediction for wider profiles (written before the runs)

Processor runs as (d) and (e) with `shift_eta_width` = 4 and 8 (tags `g-e1-prof02-w4`,
`g-e1-prof02-w8`, `g-e1-prof20-w8`), t = 5 m. [JUDGEMENT] The ratio to (a) at 4.9 m
moves towards 1 monotonically with the width: (e) w = 4: 1.10 to 1.20, w = 8: 1.02 to
1.10; (d) w = 8: 0.75 to 0.92. Horizon masses as in (a) within 1e-4. Refuted if a
wider profile is not closer to 1 than width 2 (then the width is not what limits the
profile, and a factor on kappa_1 or the Gamma coefficient would be the next candidate).

### A coarse processor version of ES (prediction written before the run)

Card job 4477 (ES, L3) has about ten jobs of other sessions ahead. As insurance, ES runs
on one processor with the dust region at cells of 4 M instead of 2 M (refined region 1
shrunk to the puncture nest; the nest to M/8 within 2 M unchanged), T = 2 M, to
t = 10 M (tag `g-es-leak2-coarse`). Prediction [JUDGEMENT]: (1) |M_AH(t)/M_AH(5 M) - 1|
below 1e-3 for 5 <= t <= 10 M (same nest as the card run); (2) wall tracers (R_0 = 36 M)
within 1e-2 of the exact radius at their proper time (cells of 4 M at the wall); (3) lapse
at the tracers at 48 M within 2 per cent of the reference 1.062 and 1.064 at t = 5 and
10 M, largest lapse on the mesh below 1.09; (4) no dust particle inside the wall
tracers' radius by more than one cell. Refuted by a horizon-mass drift above 3e-3 or a
dust lapse above 1.3.
Outcome: not run. The static refinement makes 440 MeshBlocks (1.8e6 cells) whatever
the size of region 1, because with three root MeshBlocks per direction the nest around
the centre forces level 1 nearly everywhere; at 1.2e4 zone-cycles per second that is
about 13 h for 10 M. Stopped by process id after 107 s (run
core-20261115-183458-b4430da, exit -15). ES stays with card job 4477.

### Outcome of the two bound-ball runs at cells M/2 (analysis run core-20261115-190224-2bd57ac, the first registered by `nrpic-run submit`; figure `figs/ball_g_bound_dx0p5.png`, looked at)

| T | run | central lapse: largest deviation, t <= 9 M | core | mid | outer | surface | mean abs(H) t = 12 M / t = 2 M | largest R/R_0 (core ... surface) |
|---|---|---|---|---|---|---|---|---|
| 0.125 M | core-20261115-180421-b4430da | 0.17 per cent | 1.09e-2 | 8.8e-3 | 1.27e-2 | 1.03e-2 | 2.29 | 1.2437 ... 1.2479 |
| 0.25 M | core-20261115-161021-b4430da | 1.4 per cent | 1.25e-2 | 8.9e-3 | 1.19e-2 | 1.09e-2 | 2.32 | 1.2434 ... 1.2468 |
| 0.5 M | core-20261115-180422-b4430da | 3.6 per cent (t = 4.6 M) | 1.73e-2 | 9.4e-3 | 1.11e-2 | 1.16e-2 | 2.23 | 1.2419 ... 1.2455 |

Prediction: T = 0.5 M deviation 3 to 5 per cent: confirmed (3.6; 3.9 at cells M/4, so
independent of resolution as in L1); core above T = 0.25 M, between 1.3e-2 and 2.5e-2:
confirmed (1.73e-2). T = 0.125 M stable (growth 2.29 < 10), deviation within 1 per
cent: confirmed (0.17); core within 20 per cent of T = 0.25 M: confirmed (13 per cent
lower). Not refuted: the core error falls monotonically as T falls, at fixed
resolution; the other groups do not depend on T (they are set by the resolution: the
same groups at cells M/4 are 2 to 3 times smaller). After the turnaround (t > 10 M) the
central lapse of the shortest T falls below its homogeneous reference (0.878 against
0.919 at t = 12 M): from there on it is plain 1+log in a contracting region.
Recommendation unchanged and sharpened: the shortest T that the step allows is the
safest; T <= 0.1 R/sqrt(2 alpha) is enough for 2 per cent.

### Outcome of E2 on processors (unequal pair, m = 1 and 0.25, small mesh, t = 1.99 M; analysis run core-20261115-193519-5437872; figure `figs/punc_g_e2.png`, looked at)

Runs: constant eta = 2 core-20261115-160342-b4430da, constant eta = 8 -160347-, profile
(eta_0 = 2, M_ref = 1: 2 at the heavy hole, 8 at the light one, width 0.5) -160353-.

| run | heavy tracker speed | light tracker speed | heavy M_AH | light M_AH | H norm at the end / largest |
|---|---|---|---|---|---|
| eta = 2 | 0.00619 | 0.1426 | 1.01818 | 0.26817 | 1.28 / 2.53 |
| eta = 8 | 0.00269 | 0.0978 | 1.01766 | 0.26814 | 2.49 / 3.36 |
| profile | 0.00617 | 0.1173 | 1.01820 | 0.26814 | 1.42 / 9.50 |

Prediction: heavy tracker of the profile run equal to eta = 2 within 5 per cent:
confirmed (0.3 per cent; the two curves lie on each other); light tracker equal to
eta = 8 within 15 per cent: FAILS (20 per cent faster; not refuted by the 40 per cent
threshold; constant eta = 2 is 46 per cent faster); both horizons found in all 16
searches of every run, masses within 2e-3: confirmed (5e-4 heavy, 3e-5 light); H norm
within a factor 1.5 of the constant-eta runs: confirmed at the end (1.42 against 1.28
and 2.49), FAILS at its largest value: every run has a one-record spike at t = 0.5 M
(2.53, 3.36, 9.50; back to 0.7 to 0.96 at t = 0.75 M) and the profile's is 2.8 times
the larger of the others. [JUDGEMENT, not isolated] The spike is in the light hole's
neighbourhood early on, when its chi crosses the excision threshold of the norm
(`excise_chi` 0.0625); it does not grow and the run ends with the lower norm. The
same picture as E1: the profile of width 2 m_min recovers about half of the
logarithmic distance between the constant-eta value and the value of the hole's own
units (here ln(1.20)/ln(1.46) = 0.48 left), and leaves the heavy hole exactly as with
eta = 2. Both horizon masses do not depend on the damping (the early plateaus of the
horizon masses are the same in all three runs: a property of the small mesh).

## 2026-11-15, entry 6: test H, the relaxation in a homogeneous universe (prediction written before the run)

The ball tests compare the lapse with the homogeneous reference only at the centre and
mix the term with the dynamics of the surface. An exact check of the term itself: the
homogeneous dust universe of `problems/cosmo/flrw.athinput` (periodic box of side 4,
H_0 = 1, 32 cells, zero shift) with the 1+log lapse and `lapse_leak` = 0, 20, 5
(`problems/cosmo/flrw_leak.athinput`, driver and comparison
`analysis/gauge/flrw_leak.py`, t = 2/H_0). There the condition is the ordinary
differential equation d ln(alpha)/dt = 6 H(tau) - lapse_leak max(ln alpha, 0),
d tau/dt = alpha, H = H_0/(1 + 3 H_0 tau/2), a = (1 + 3 H_0 tau/2)^(2/3); lapse_leak = 0
gives alpha = 1 + 6 ln a. Prediction [JUDGEMENT]: the lapse (alpha_max of the history)
and a from the proper volume agree with that solution to 1e-5 relative over the run for
all three rates (wave 1 matched alpha = a to 1.9e-7 with the conformal-time lapse, CT
"C0"); alpha_max - alpha_min below 1e-10 (homogeneity is kept). Refuted by a relative
error above 1e-4 (a wrong factor or sign in the term would show at order 1e-1).

### Outcome of test H (run core-20261115-193831-7598fd6, the first package run registered by `nrpic-run submit` with a simulation)

| lapse_leak | alpha at t = 2/H_0 (exact) | a (exact) | largest relative error alpha / a | alpha_max - alpha_min |
|---|---|---|---|---|
| 0 | 14.384007 (14.384045) | 9.306095 (9.306138) | 1.04e-5 / 1.34e-5 | 1.2e-13 |
| 20 | 1.0718012 (1.0718011) | 2.6886180 (2.6886185) | 2.06e-4 / 1.06e-5 | 9e-16 |
| 5 | 1.2624374 (1.2624373) | 3.1443117 (3.1443130) | 6.3e-6 / 7.3e-7 | 0 |

Plain 1+log reaches alpha = 1 + 6 ln a = 14.4 at a = 9.3; the relaxed lapse stays at
1.07 and 1.26. Prediction (1e-5 for every rate): met for rate 5, met to 1.3e-5 for
rate 0 (the largest error is at t = 0.25, where the lapse grows fastest; 2.7e-6 at the
end), FAILS for rate 20 at the start: 1.8e-4 to 2.1e-4 at t = 0.03 to 0.09 (the first
three steps), 5.7e-7 at t = 0.5 and 4.9e-8 at the end. The relaxation time of rate 20
is 1.6 steps and the term has a kink at alpha = 1, where every run starts. Not refuted
(threshold 1e-4 is exceeded only in the first three steps; a wrong factor would show at
1e-1 for the whole run). Homogeneity is kept to round-off. Check of the reading, written
before it runs: rate 20 with a step four times smaller (`time/cfl_number=0.0625`): the
error of the first 0.1/H_0 falls by at least 8 (below 2.6e-5); refuted if not.

## 2026-11-19, entry 7 (wave 2b, resumed 14:00 UTC): state after the cut-off; L3 did not run; its retest

### What was found

The session of 2026-11-15 was cut off after entry 6. Since then: card job 4477 (ES and
L3) and card job 4478 (card versions of E2, E1, P) finished; the three processor runs of
E1 with wider profiles finished (8020 to 8151 s each); the step check of test H ran
(core-20261115-194634-6d1e401, registered and committed; its figure and numbers were
untracked). The fifteen manifests written by `grun.py` after the cut-off and the figure
and numbers of the step check are committed in 6ffb5fa9 (hand-written manifests of wave
2 count as registered: decision 0016, item 3). `git diff b4430da HEAD -- athenak/src`
is empty: the published executables are the current source. Main is merged (b6039c88);
decision 0016 read. From here on runs are registered with `harness/bin/nrpic-run
submit`.

### L3 produced no result: the run stopped at its first regrid

Run core-20261115-203207-b4430da (tag `gc-collapse-leak05`, job 4477) ended after 2.4 s
and 8 cycles (t = 0.5 M) with [VERIFIED, its `athena.log`]

    FATAL ERROR in .../mesh/mesh_refinement.cpp at line 495: Number of MeshBlocks in
    this rank on new tree = 1632 on rank = 0 exceeds <mesh_refinement>/max_nmb_per_rank
    = 1024

The start mesh had 232 MeshBlocks (cells M/4 within 8 M); the input used the adaptive
mesh of `problems/os/os_amr.athinput` (Loehner indicator of alpha psi^7, six levels).
This is a defect of the test's input, not of the lapse condition: nothing of prediction
L3 was tested. Which MeshBlocks the indicator flagged was not looked at (the run wrote
no mesh output) [JUDGEMENT: the sharp surface, where the lapse and K have a step from
the first step on; in Oppenheimer-Snyder collapse from rest the same rule starts
quietly].

### Retest of L3: set-up, written before the run

Mesh as prediction L3 of entry 1 names it ("cells M/8 inside 3 M"), static:
`problems/ball/ball_collapse.athinput` now has `refinement = static`, root cells 2 M,
cells M/4 within the cube of half-width 8 M, cells M/8 within 4 M (288 MeshBlocks,
checked with `athena -m`), and a third region that adds cells M/16 within 2 M when
`refined_region3/level=5` is given (344 MeshBlocks). Everything else as written on
2026-11-15: the bound ball R_b = 5 M, e0 = 0.16, sharp surface, lattice of M/4
(`scratch/core/id/ic_ball/t2_bound_h0p25.*`, 26422 particles), cloud at the finest
local level (the published rule of the collapse runs, `docs/TESTLOG.md` "Dust collapse:
cloud coarsening limited to one level", decision at its end), lapse excision at 0.1,
horizon finder from t = 14 M every 16 cycles, T = 0.5 M (`lapse_leak = 2.0`, amendment
of entry 3), `tlim` 45 M as the prediction says (the file had 40). Executable: the
published card executable of b4430da. With cells M/8 the particles inside 4 M sit one
per eight cells until the ball has contracted: the source is granular there (in the
Oppenheimer-Snyder runs of `docs/TESTLOG.md`, "cloud at the finest level against
adaptive cloud level", the centre did not notice this).

Three runs in one card job (estimated 0.22 card-hours from 9.4e6 zone-cycles per
second, the ES run):

1. `collapse-leak05` (T = 0.5 M, cells M/8): prediction L3 of entry 1, unchanged: the
   central lapse falls below 0.05; an apparent horizon is found; its mass is within 3
   per cent of M = 1 once the surface shells are inside and constant to 1 per cent over
   the last 5 M; the surface shells follow the cycloid to R = 2.5 M with |eps| below 3
   per cent. Refuted by: no horizon before t = 45 M, a horizon mass off by more than 10
   per cent, or shells off by more than 10 per cent at R = 2.5 M.
2. `collapse-mp` (old 1+log, `lapse_leak = 0`, cells M/8): the comparison of entry 1
   [JUDGEMENT: it also forms a horizon, with larger shell errors (the front of L2
   reaches the core at t = 3 M)].
3. `collapse-leak05-fine` (T = 0.5 M, cells M/16 within 2 M), added now. Prediction
   [JUDGEMENT]: a horizon is found, first within 0.5 M of coordinate time of run 1; its
   mass at the end is within 1 per cent of M (the Oppenheimer-Snyder runs gave 0.3 to
   0.5 per cent low at M/13, `docs/TESTLOG.md` "Monte Carlo dust ball", conclusion 4)
   and the two resolutions differ by less than 1.5 per cent at the end. Refuted by a
   horizon mass off by more than 2 per cent at M/16 or a difference between the two
   runs above 3 per cent.

What the lapse condition could show here and nowhere else in the package: after the
turnaround the excess of the lapse is gone and the condition is plain 1+log started
from a lapse near 1 at t = 10 M instead of at t = 0. If that late start left the slices
unable to reach the trapped region before they freeze, run 1 would end without a
horizon while run 2 finds one: that outcome would be a defect of the condition.

## 2026-11-19, entry 8: outcomes of the runs that finished after the cut-off (H step check, ES, card P, E1, E2, E1 with wider profiles)

Each is judged by the prediction written before it ran (entries 1, 2, 3, 5, 6); no new
criterion. Analysis runs of this session (all `nrpic-run submit`, local): ES
core-20261119-140835-00b3754 and -140932-2241a73 (the second adds the lapse of each
tracer group); card P, E1, E2 core-20261119-140943-8b9c2aa (figures redrawn in
-141047-b42eb4e); processors with the wider profiles core-20261119-141015-586d2cd
(redrawn in -141043-49275d1). The subject line of commit 49275d1b names a run
"core-20261119-141003": no such run exists, the analysis is -141015-586d2cd. Card time
of the package up to here: 0.422 card-hours (sum of `card_hours` of its nineteen card
manifests).

### Test H, step check (run core-20261115-194634-6d1e401; figure `figs/flrw_leak_cfl0p0625.png`, looked at)

Prediction (entry 6): with a step four times smaller the error of rate 20 in the first
0.1/H_0 falls by at least 8, below 2.6e-5; refuted if not. Outcome: largest relative
error of the lapse 4.97e-7 (2.06e-4 at the standard step: a factor 414; a fourth-order
step gives 256), of a 2.75e-8 (1.06e-5); the lapse at t = 2/H_0 is 1.071801120644
against 1.071801120560 exact. The error peaks at t = 0.06/H_0 and falls to 1e-10 by the
end. Confirmed: the start-up error of entry 6 is the truncation error of the explicit
step when the relaxation time is 1.6 steps, and it converges away. The two figures of
test H had the label of the right axis cut off; `flrw_leak.py` now breaks the label and
both runs were repeated for the figures (core-20261119-141114-851f288, three rates;
core-20261119-141928-69cb509, step check; processor runs are reproducible: both
numbers files came out unchanged; both figures looked at again).

### Test ES (run core-20261115-202901-b4430da, card, 185 s, 0.051 card-hours; figure `figs/es_gc_es-leak2.png`, looked at; numbers `es_numbers_gc.json`)

Track D's Einstein-Straus data (M = 1, wall at 36 M, plateau H = 5.58e-3/M), T = 2 M,
cells 2 M in the dust and M/8 at the hole, 30 M of coordinate time, 960 cycles; the run
ended at `tlim`. Against prediction ES (entry 2, items 1 to 5, with the amendments of
entry 3):

| item | prediction | outcome |
|---|---|---|
| 1 horizon mass at t = 10 M | within 5e-3 of M | 0.999971: confirmed |
| 1 drift, 10 M <= t <= 30 M | abs(M_AH(t)/M_AH(10 M) - 1) below 1e-3; refuted above 3e-3 | 1.02e-3 (0.99989 to 1.00099): FAILS by 2 per cent of the bound; not refuted |
| 2 wall tracers (R_0 = 36 M) | within 5e-3 of the exact radius at their proper time; refuted above 2e-2 | largest 6.2e-5 (42.7615 against 42.7628 M at tau = 30 M): confirmed |
| 2 tracers at 48 M | within 3e-3 | 6.8e-5: confirmed |
| 3 lapse at the tracers at 48 M | within 2 per cent of the homogeneous reference (1.062, 1.064, 1.062, 1.059, 1.057, 1.055 at t = 5 ... 30 M) | 1.061, 1.054, 1.049, 1.046, 1.043, 1.041: largest deviation 1.3 per cent (at the end): confirmed |
| 3 largest lapse on the mesh | below 1.09; refuted by a dust lapse above 1.3 | 1.109 at t = 5.25 M, 1.093, 1.074, 1.063 at t = 10, 20, 30 M: FAILS; not refuted |
| 4 dust and bubble | no dust particle inside the wall tracers by more than one cell (2 M) | smallest coordinate radius of the 87128 dust particles at t = 30 M 36.56 M, wall tracers at 36.34 M: confirmed |
| 5 tracers at 6 M | removed at a proper time between 13 and 16 M | all 14 removed at tau = 15.52 M, R = 1.51 M: confirmed |

All other tracer groups: largest abs(R/R_exact - 1) 1.1e-3 (6 M, while R_exact > 2.2 M),
9.6e-4 (10 M), 7e-5 (20 M), 1.2e-4 (28 M), 4.6e-4 (40 M), 2.4e-4 (56 M), 4.5e-5 (66 M),
1.3e-3 (78 M, in the vacuum outside the dust, growing towards the end).

Where prediction 3 failed: the largest lapse on the mesh is not in the dust. It equals
the lapse at the tracers of R_0 = 20 M, inside the vacuum bubble (1.1085 at t = 5 M at
both; 1.093, 1.073, 1.062 at the tracers at t = 10, 20, 30 M) [VERIFIED,
`es_numbers_gc.json`, `alpha_t` of group 20 against `alpha_max_t`]. The normal observers
of the bubble between the hole and the wall expand faster than the plateau; my reference
was the plateau only. In the dust the lapse is 1.045 to 1.060 at the wall, 1.041 to
1.061 at 48 M, 1.034 to 1.044 at 56 M. With plain 1+log the plateau would be at 2.37 at
t = 30 M (entry 3).

Where prediction 1 failed: the horizon mass is 0.99981 at t = 5 M, 0.99997 at 10 M,
1.00048 at 15 M, 1.00091 at 20 M, 1.00097 at 25 M and 1.00098 at 29.5 M; between t = 3 M
and the end it stays between 0.99966 and 1.00099. The vacuum puncture alone on the same
finest cells (test P on the card, below) does the same: 0.99986, 1.00019, 1.00076,
1.00105 at t = 5, 10, 15, 19.5 M, a rise of 8.6e-4 from 10 M to 19.5 M against 9.1e-4
in the ES run. So the drift is that of a puncture at cells M/8 in this code, not of the
dust or of the lapse relaxation (Track D expected +1.5e-3 at this cell size, entry 2).

Lapse at the puncture (probe at the origin, equal to the smallest lapse on the mesh):
0.031 at the start (psi^-2 of the table), a rise to 0.233 at t = 5.75 M (0.202 at 5 M),
0.053 at 10 M, 0.032 at 20 M, 0.038 at 30 M: the hole stays collapsed; the bump is the
adjustment of the start lapse and zero start shift to the moving-puncture gauge.

Answer for Track D: with `lapse_leak` the Einstein-Straus data evolve for 30 M with a
horizon mass constant to 1.0e-3 (the resolution-limited drift of the puncture itself),
the wall on the exact curve to 6e-5, a dust lapse of 1.04 to 1.06 and a largest lapse
of 1.11 (in the bubble), no dust in the bubble. Nothing in this run shows a defect of
the condition. Not covered: more than 30 M, a finer dust mesh, the boundary (at 96 M
here, outside the light travel time).

### Test P on the card (full mesh, cells m/8, 20 M; runs core-20261115-204400-b4430da plain, -204609- T = 1 m; figure `figs/punc_gc_p.png`, looked at)

Prediction (entry 1): horizon masses equal within 1e-6 at every search (identical files
if the lapse never exceeds 1); refuted by a difference above 1e-5. Outcome: the tracker
file, the horizon shape, the horizon summary (40 searches to t = 19.5 M) and the
constraint history are identical byte for byte; no file differs. Confirmed, now over
20 M on the full mesh.

### Test E1 on the card (full mesh, t = 6 m; figure `figs/punc_gc_e1.png`, looked at)

Runs (a) eta = 2 core-20261115-203939-b4430da, (c) eta = 20 -204106-, (d) eta_0 = 20
with the profile -204233-, (b) eta = 0.2 -204818-, (e) eta_0 = 0.2 with the profile
-204945-. Tracker speed (ratio to (a)):

| run | 1.6 m | 3.0 m | 4.9 m | 5.0 m | horizon mass at the end |
|---|---|---|---|---|---|
| (a) | 0.0514 | 0.0843 | 0.1069 | 0.1071 | 1.011091 |
| (c) | 0.0060 (0.12) | 0.0153 (0.18) | 0.0231 (0.22) | 0.0243 (0.23) | 1.011093 |
| (d) | 0.0325 (0.63) | 0.0486 (0.58) | 0.0587 (0.55) | 0.0576 (0.54) | 1.011091 |
| (b) | 0.1011 (1.97) | 0.1748 (2.07) | 0.2109 (1.97) | 0.2100 (1.96) | 1.011097 |
| (e) | 0.0551 (1.07) | 0.0986 (1.17) | 0.1357 (1.27) | 0.1328 (1.24) | 1.011089 |

The speeds up to 4.9 m equal those of the small mesh on processors (entry 5) to four
digits. Against the prediction at t = 5 m: (d) within 20 per cent of (a): FAILS (46 per
cent slower; the refutation threshold is 50); (c) at least 5 times slower: fails
narrowly (4.4 times); horizon mass of (d) within 1e-3 of (a): confirmed (1e-7); (b) not
slower than (a): confirmed; (e) within 20 per cent of (a): FAILS narrowly (24 per
cent). Horizon found in all 24 searches of every run. The same outcome as on
processors.

### Test E2 on the card (full mesh, t = 3.99 M; figure `figs/punc_gc_e2.png`, looked at)

Runs: constant eta = 2 core-20261115-203440-b4430da, constant eta = 8 -203710-, profile
(2 at the heavy hole, 8 at the light one, width 0.5 M) -203210-.

| run | heavy tracker speed | light tracker speed | heavy M_AH | light M_AH | H norm at the end / largest |
|---|---|---|---|---|---|
| eta = 2 | 0.02569 | 0.1385 | 1.016896 | 0.268707 | 1.18 / 2.53 |
| eta = 8 | 0.00852 | 0.1018 | 1.016718 | 0.268579 | 1.17 / 3.36 |
| profile | 0.02548 | 0.1245 | 1.016894 | 0.268583 | 1.26 / 9.49 |

Prediction (entry 1): heavy tracker of the profile run equal to eta = 2 within 5 per
cent: confirmed (0.8 per cent); light tracker equal to eta = 8 within 15 per cent:
FAILS (22 per cent faster; not refuted by the 40 per cent threshold; constant eta = 2
is 36 per cent faster); both horizons found in all 32 searches of every run, masses
within 2e-3 of the constant-eta runs: confirmed (1.8e-4 heavy, 1.3e-4 light); H norm
within a factor 1.5: confirmed at the end (1.07), FAILS at its largest value (the
one-record spike at t = 0.5 M of entry 5, the same three numbers as on the small mesh).
At t = 4 M the profile of width 2 m_min has recovered 35 per cent of the logarithmic
distance from the constant-eta value to the value of the light hole's own units (52
per cent at t = 2 M on processors): the light tracker of the profile run keeps rising
towards the eta = 2 curve (figure), so the narrow profile helps less the longer the run.

### E1 with wider profiles (processors, small mesh, t = 4.9 m; figure `figs/punc_g_e1.png`, looked at)

Runs: (e) width 4 core-20261115-183402-b4430da, (e) width 8 -183403-, (d) width 8
-183400-. Tracker speed relative to (a) at 1.6, 3.0, 4.9 m:

| run | width 2 (entry 5) | width 4 | width 8 |
|---|---|---|---|
| (e) eta m = 0.2 far away, 2 at the hole | 1.07, 1.17, 1.27 | 1.02, 1.05, 1.04 | 1.005, 1.014, 1.017 |
| (d) eta m = 20 far away, 2 at the hole | 0.63, 0.58, 0.55 | not run | 0.95, 0.89, 0.86 |

Prediction (entry 5): the ratio at 4.9 m moves towards 1 monotonically with the width:
confirmed; (e) width 4 between 1.10 and 1.20: outside, on the better side (1.04); (e)
width 8 between 1.02 and 1.10: 1.017, just below; (d) width 8 between 0.75 and 0.92:
confirmed (0.86); horizon masses as in (a) within 1e-4: confirmed (1.011085 to 1.011093
against 1.011093). Not refuted: the width is what limits the profile of the paper. With
`shift_eta_width = 8` an under-damped hole follows its own-units reference to 2 per
cent and an over-damped one to 14 per cent over the first 5 m; horizon mass and
constraint norm do not change.

### One more card test, with its prediction (written before the run): E2 with wider profiles

The recommendation to Track F rests on E1 (one hole) for the width; the pair was run
with width 2 only, where the light tracker is 22 per cent off its own-units reference
at t = 4 M. Two card runs as `gc-e2-profile` with `shift_eta_width` = 4 and 8 (tags
`e2-profile-w4`, `e2-profile-w8`; widths 1 M and 2 M around the light hole, separation
8 M). The wider profile also reaches the heavy hole: its damping becomes
2 [1 + 3/(1 + 64/w^2)] = 2.09 (width 4) and 2.35 (width 8) instead of 2. Prediction
[JUDGEMENT] at t = 3.99 M: light tracker relative to the eta = 8 run 1.03 to 1.12
(width 4) and 1.00 to 1.08 (width 8), against 1.22 with width 2; heavy tracker relative
to the eta = 2 run 0.95 to 1.00 (width 4) and 0.85 to 0.96 (width 8); both horizons
found in every search, masses within 2e-3 of the constant-eta runs; H norm at the end
within a factor 1.5 of them. Refuted if the light tracker with width 8 is not closer
to the eta = 8 run than with width 2, or if a horizon is lost.
