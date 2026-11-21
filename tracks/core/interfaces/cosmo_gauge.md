# Interface: gauge, step limit and constraint damping (proposal for `coord/INTERFACES/cosmo_gauge.md`)

Status: sections 1 to 6 ACCEPTED as the state of release `core-v0.3` (decision 0011);
the entries marked "wave 2" (lapse relaxation, tracker-dependent shift damping, section
7) are a PROPOSAL of branch `core/gauge` (source commit b4430da), evidence in
`tracks/core/JOURNAL-gauge.md`. Sections 1 to 6 were written from the code at commit b7b431d:
`athenak/src/z4c/z4c.cpp` lines 125-166 (options), `z4c.hpp` lines 142-199,
`z4c_calcrhs.cpp` lines 40-69 and 607-729 (right-hand sides),
`particles/nrpic.cpp` lines 1295-1336 (step limit). Options are in `<z4c>` unless
marked `<particles>` or `<time>`. Tests: `docs/TESTLOG.md` (DT), `cosmo/TESTLOG.md`
(CT) by entry title.

**Executable caveat [VERIFIED, `JOURNAL.md` 11:21].** The processor executable
`.work/build_cpu_c1/src/athena` (built 2026-11-14 06:03 PST) does not contain
`damp_ch_chipow` and `damp_kappa_gam`; an input that sets them runs with the defaults
(exponent -1/4, no extra damping) without an error. The card executable
`.work/build_gpu_c3/src/athena` (08:31 PST) contains both.

## 1. Lapse

As implemented (`z4c_calcrhs.cpp` lines 681-710), with `chi = gamma^(-1/3)`:

    d_t alpha = lapse_advect beta^i d_i alpha
                - [lapse_oplog lapse_harmonicf + lapse_harmonic alpha
                   + lapse_volume chi^(-1/2)] alpha Khat
                - lapse_kdriver alpha_ref alpha (Khat - Khat_ref)
                - lapse_leak alpha max(ln(alpha/lapse_leak_alpha), 0)       (wave 2)
                + (slow-start term if slow_start_lapse)

| Option | Default | Meaning | Tests |
|---|---|---|---|
| `lapse_oplog` | 2.0 | 1+log slicing `-2 alpha Khat` with the defaults (the paper's `mu_L = 2/alpha`, main.tex L372, L380) | every isolated-system run (DT) |
| `lapse_harmonicf` | 1.0 | factor of the 1+log term | |
| `lapse_harmonic` | 0.0 | `-c alpha^2 Khat`; c = 1/3 with zero shift gives alpha = a on a homogeneous universe: t is conformal time, `a = (1 + t/2)^2` for dust with H_0 = 1 | CT "C0, first test: homogeneous dust universe" (alpha = a to 1.9e-7 at a = 4); CT "C6 preparation" (with Lambda, 1.8e-6) |
| `lapse_volume` | 0.0 | `-c gamma^(1/6) alpha Khat`; c = 1/3 (with `lapse_harmonic = 0`) also gives alpha = a, and keeps `alpha - gamma^(1/6)` constant, so the lapse reaches zero before the volume element where matter collapses | CT "E1, first step: a lapse condition for the collapsing overdensity" and its outcome |
| `lapse_kdriver` | 0.0 | driver towards constant mean curvature, strength mu; `alpha_ref` = largest lapse, `Khat_ref` = proper-volume mean of Khat, both from the state of each Runge-Kutta stage; vanishes on a homogeneous universe | CT "E1, second step: driver towards constant mean curvature" and "E1, second step: outcome" |
| `lapse_advect` | 1.0 | advection of the lapse (0 in the cosmological inputs) | |
| `lapse_leak` (wave 2) | absent = 0 | rate 1/T at which the excess of the lapse over `lapse_leak_alpha` relaxes; with 1+log the lapse of an expanding region tends to exp(-2 T Khat) = exp(6 T H) instead of 1 + 6 ln a; no effect where the lapse is at or below the reference (contraction, black holes). Read only if present in the input | section 7 |
| `lapse_leak_alpha` (wave 2) | absent = 1.0 | reference lapse | section 7 (only 1 is tested) |
| `slow_start_lapse`, `ssl_damping_amp`, `ssl_damping_time`, `ssl_damping_index` | false, 0.6, 20, 1 | AthenaK's slow-start term, not used here | none |

## 2. Shift

As implemented (lines 712-729):

    d_t beta^i = shift_Gamma Gamma^i + shift_advect beta^j d_j beta^i - eta(x) beta^i
                 + shift_alpha2Gamma alpha^2 Gamma^i
                 + shift_H alpha chi (alpha/2 d_j chi - d_j alpha) gamma~^ij

| Option | Default | Meaning | Production |
|---|---|---|---|
| `shift_Gamma` | 1.0 | Gamma-driver coefficient | 0.75 isolated systems; 0 cosmology |
| `shift_eta` | 2.0 | damping eta_0: constant, or the far value of the profile below | 2.0; 0 cosmology |
| `shift_eta_profile` (wave 2) | absent = false | eta(x) = eta_0 [1 + sum_A (M_ref/m_A - 1)/(1 + abs(x - x_A)^2/w_A^2)] over the compact-object trackers A with `co_<A>_mass` > 0 (at most 8): the paper's profile (main.tex L388-397). eta tends to eta_0 M_ref/m_A at black hole A and to eta_0 far away | section 7 |
| `shift_eta_mref` (wave 2) | absent = 1.0 | M_ref | section 7 |
| `shift_eta_width` (wave 2) | absent = 2.0 | w_A in units of the smallest tracker mass (the paper's 4 m_min^2 is width 2) | section 7 (width 2 on one hole and on a pair; 4 and 8 on one hole) |
| `shift_eta_width_local` (wave 2) | absent = false | true: w_A = `shift_eta_width` m_A | not tested |
| `shift_advect` | 1.0 | advection | 1; 0 cosmology |
| `shift_alpha2Gamma` | 0.0 | the paper's form `alpha^2 mu_S Gamma^i` (L376) | 0 |
| `shift_H` | 0.0 | harmonic-gauge term | 0 |

The `B^i` form of the Gamma-driver (paper L381-386) is not implemented; nor is the
paper's factor eta(x)/eta_0 on kappa_1 (L394-397). A shift driver
`0.75 alpha^2 Gamma^i - 2 beta^i` with advection in a refined cosmological box was
unstable within a few time units (CT "E1, third step: outcome of the shift-driver run").
Cosmological runs so far use zero shift. Moving black holes in an expanding background
need a shift; that combination has no test yet [JUDGEMENT: open item for Tracks A, B, D].

## 3. Constraint damping and relaxation

Terms (lines 611-660), with `kappa1' = damp_kappa1/alpha` if `damp_kappa1_over_alpha`,
else `damp_kappa1` (and the same for `damp_kappa_gam`):

    d_t Khat    += kappa1' (1 - kappa2) alpha Theta
    d_t Theta   += -(2 + kappa2) kappa1' alpha Theta
    d_t Gamma^i += -2 alpha (kappa1' + kappa_gam') (Gamma^i - Gamma^i(metric))
    d_t chi     += (c_H/2) chi^p H,   c_H = damp_ch + damp_ch_dx dx,  p = damp_ch_chipow,
                   H including -16 pi (E + Lambda/8 pi)

| Option | Default | Meaning | Tests |
|---|---|---|---|
| `damp_kappa1` | 0.0 | kappa1 | DT "Growing oscillation: constraint damping" (0, 0.02, 0.1: lapse history unchanged, constraint norm lower with 0.1) |
| `damp_kappa2` | 0.0 | kappa2 | all runs use 0 |
| `damp_kappa1_over_alpha` | false | rate per unit of coordinate time; needed in conformal time where alpha = a grows to 1000 (a constant coefficient became stiff, rate x step up to 2.3) | CT "C5, test C, larger box, 32 cells: outcome and a stiffness problem", "C5, test C: the late growth is the stiff damping" |
| `damp_kappa_gam` | 0.0 | extra damping of the connection constraint alone | CT "Open item: damping of the connection constraint alone, outcome" (moves the violation into the other constraints; kept, default off) |
| `damp_ch` | 0.0 | constant part of c_H (a length) | DT "Growing oscillation: parabolic relaxation" (c_H = 0.05: Hamiltonian norm 0.031 to 0.0145, lapse history unchanged to 1e-4) |
| `damp_ch_dx` | 0.0 | part of c_H proportional to the local cell size | CT "Open item of T1: relaxation of the Hamiltonian constraint, outcome" (0.3 cells, p = 0: power unchanged to 1e-5, measured constraint unchanged) |
| `damp_ch_chipow` | -0.25 | exponent p; p = 0 keeps the diffusion coefficient fixed in conformal time | as above |
| `diss` | 0.0 | Kreiss-Oliger dissipation (0.5 in all production inputs) | CT "T1/C5: outcomes ..." (0.1 against 0.5) |
| `use_z4c` | true | false: BSSN (Theta frozen) | none |
| `chi_div_floor` | -1000 | floor of chi where it is divided by (1e-5 in the isolated-system inputs) | |
| `excise_chi` | 0.0625 | constraint norms of `.z4c.user.hst` only over chi >= this (0 in cosmology, where chi = a^-2 falls) | |

No step restriction is derived from c_H automatically (`z4c_newdt.cpp` uses only the
cell size): the user keeps `c_H dt / dx^2` small; `z4c.hpp` lines 165-171 give
`damp_ch_dx` below 0.5 for a step of a quarter cell. Values in the paper: none
(`SECTION2_CORRECTIONS.md` 3.2).

Finding to carry into the tracks [VERIFIED, CT entries 05:35, 08:23, 08:35]: in the
cosmological runs the measured Hamiltonian-constraint level after the contrast has grown
is the connection constraint; damping rates above 0.5, extra connection damping and the
parabolic relaxation did not lower it; resolution of the second-order terms, the cubic
cloud, the compensation and the spline interpolation did.

## 4. Time step

| Option | Default | Meaning | Tests |
|---|---|---|---|
| `<time> cfl_number` | (required) | Z4c step `cfl_number x min dx` over all MeshBlocks; 0.25 in all inputs | |
| `<particles> dt` | float max | upper limit of the step | |
| `<particles> dt_expansion` | 0.0 (off) | step at most f x 3/abs(mean(alpha Khat)), the mean taken over cells with equal weight, computed after each deposit for the next step; with it the step varies, and the source extrapolation and the probe proper time use the ratio of successive steps | CT "Step limited by the expansion rate (03:43)" (homogeneous universe, 16 cells, a = 36: relative Hamiltonian constraint 2.5e-5 without, 6.0e-8 with f = 0.01); CT "C5, test C: step-limited runs ..." |

The global step is shared by all levels and by the particles (`pusher.md` section 2).

## 5. Configurations in use

| Problem | Lapse | Shift | Damping | Step | Input |
|---|---|---|---|---|---|
| isolated systems (collapse, clusters, black holes) | 1+log (`lapse_oplog = 2`), advected | `shift_Gamma = 0.75`, `shift_eta = 2`, advected | kappa1 = 0.02, kappa2 = 0, `diss = 0.5` | Courant 0.25 | `problems/os/os_amr.athinput`, `problems/st/*.athinput`, `problems/jeans/jeans.athinput` |
| expanding periodic universe | `lapse_oplog = 0`, `lapse_harmonic = 1/3`, not advected | zero | kappa1 = 0.5 with `damp_kappa1_over_alpha = true`, `diss = 0.5` | Courant 0.25 and `dt_expansion = 0.01` | `problems/cosmo/daverio_field.athinput`, `cosmo/README.md` lines 42-47 |

## 6. Proposed interface rules (JUDGEMENT)

1. A track that needs a new gauge condition specifies it as a right-hand side in the
   notation of section 1 or 2, with the homogeneous-universe check (alpha against a(t)
   to 1e-6 at a quarter-cell step, CT "C0") as its first test.
2. Every cosmological input states `damp_kappa1_over_alpha` and `dt_expansion`
   explicitly; every input that uses `damp_ch_chipow` or `damp_kappa_gam` names the
   executable it runs with until the processor build is current.
3. The tracker-dependent eta and kappa1 of the paper are a candidate capability for
   Track D and F (several black holes with a mass hierarchy), to be specified there.

## 7. Wave 2: lapse for expanding matter, shift damping for unequal masses (branch `core/gauge`)

Source: `athenak/src/z4c/z4c_gauge_ext.hpp` (new), hooks in `z4c.hpp` (one include, one
member `gext`), `z4c.cpp` (one line after the `shift_eta` read), `z4c_calcrhs.cpp` (one
include after `tmunu.hpp`, one call `AddGaugeExt(...)` between the main loop and the
dissipation loop). Both terms are added in a loop of their own after the main loop and
only if switched on; their parameters are read only if present, so inputs without them
run and write byte for byte as release core-v0.3 [VERIFIED, regression R: cases geo,
boris, dep, east, os (runs core-20261115-160056 ... -160129-b4430da,
core-20261115-160623-b6ea4a1) and a binary puncture with trackers (core-20261115-180234-
3f710a3 against -b4430da), every output file identical]. Journal:
`tracks/core/JOURNAL-gauge.md`; analysis and figures `tracks/core/analysis/gauge/`.

### 7.1 Lapse relaxation (`lapse_leak`)

    d_t alpha = [section 1] - (alpha/T) max(ln(alpha/alpha_0), 0),   1/T = lapse_leak,
                                                                    alpha_0 = lapse_leak_alpha

Why this one [JUDGEMENT, derivation in the journal, entry 1]. With 1+log and zero shift,
alpha - 2 ln sqrt(gamma) is constant along the normal observers, so two regions that
expand at different rates (a ball and its exterior) build a lapse step that grows
without bound (3 ln a at the surface of a marginally bound ball); the gauge wave carries
it inward as the front of wave 1. With the term, d_t ln alpha = -2 (K - K_m) with
K_m = -ln(alpha/alpha_0)/(2T) the running mean of K over the time T: the lapse reacts to
the change of the expansion, not to its integral; a homogeneous region tends to
alpha = exp(6 T H) (bounded) instead of 1 + 6 ln a. The term has no derivative (the
principal part, hence the hyperbolicity, stays that of 1+log), needs no reference
solution, no stored field and no knowledge of where the matter is, and vanishes where
alpha <= alpha_0: a collapsing region and a black hole are sliced by plain 1+log.
Not chosen: 1+log against a reference K_ref(t, x) (with the unperturbed solution as
reference the lapse of an overdensity of contrast 1.65 reaches zero, long before
turnaround; Track A's toy found the same, `GAUGE.md` C3); max(0, K) and softplus
(geodesic slicing where the matter expands: weakly hyperbolic; the fixed lapse of wave 1
was unstable, `JOURNAL-id.md` entry 8); a blend of conformal time and 1+log by radius or
chi (a front source at the blend radius); `lapse_kdriver` (a box mean, dominated by the
exterior of a ball); `lapse_volume` (the same unbounded step).

Tests [VERIFIED, runs in the journal, entries 3, 4, 6, 8 and 9]:

| test | set-up | old 1+log | new |
|---|---|---|---|
| L1 marginally bound ball, R_b = 10 M, sharp surface, cells M/2, t = 10 M | largest abs(R/R_exact - 1) of the core shells (invariant: areal radius at the shells' proper time) | 7.65e-2 (does not converge: 7.9e-2 at cells 1 M) | T = 1 M: 1.16e-3 (3.08e-3 at 1 M); T = 2 M: 2.07e-3 |
| L1, same | central lapse against the homogeneous value of the same condition | front: 3.24 at t = 5.6 M, then 1.76 (homogeneous 4.47 at 8 M) | within 2.8 per cent (T = 1 M), 0.2 per cent (T = 0.5 M), 13 per cent (T = 2 M) |
| L1, smooth edge (2 M), cells M/2 | core, mid, outer, edge abs(eps) | 1.2e-2, 1.3e-3, 1.4e-3, 3.6e-4 | T = 1 M: 5.9e-4, 3.0e-4, 5.1e-4, 1.7e-4 |
| L1, largest coordinate speed of light at the particles | | 2.32 | 1.13 (T = 1 M) |
| L2 bound ball R_b = 5 M, e0 = 0.16, cells M/4, t = 12 M | core, mid, outer, surface abs(eps) | conformal-time lapse of wave 1: 0.11, 2.6e-2, 1.7e-2, 1.3e-2 | T = 0.5 M: 9.2e-3, 2.5e-3, 4.3e-3, 6.4e-3; T = 1 M: 3.3e-2, 4.4e-3, 5.8e-3, 6.7e-3 |
| L2 turnaround | largest R/R_0 (exact 1.25) | | 1.2478 to 1.2496 (T = 0.5 M) |
| P puncture alone, cells m/8, 10 M (processors) and 20 M (card, full mesh) | | | identical to plain 1+log byte for byte: tracker, horizon shape, horizon summary (40 searches), constraint history (the lapse never exceeds 1) |
| H homogeneous dust universe (periodic, H_0 = 1, t = 2/H_0), rates 0, 5, 20 | lapse and scale factor against the exact ordinary differential equation | 1 + 6 ln a = 14.4 at a = 9.3, followed to 1.0e-5 | alpha = 1.26 (T = 0.2/H_0) followed to 6e-6; alpha = 1.07 (T = 0.05/H_0 = 1.6 steps) to 2.1e-4 in the first three steps and 5e-8 at the end; with a four times smaller step 5.0e-7 (414 times smaller) |
| L3 bound ball of L2 through turnaround and collapse, static mesh, cells M/8 within 4 M (and M/16 within 2 M), t = 45 M (card) | apparent horizon (exact mass M = 1) | first found at t = 18 M, then in every search; mass 0.9964 to 1.0002 | T = 0.5 M: first found at t = 29 M (28.25 M at M/16), then in every search; mass 0.9980 to 1.0003 at M/8, 0.9994 to 1.0006 at M/16 (0.99997 at t = 44.5 M) |
| L3, same | surface shells at the record where the exact areal radius reaches 2.5 M: median / largest abs(eps) | 1.6 / 10.1 per cent | 3.6 / 12.7 per cent at M/8 (shells slower than exact), 1.8 / 10.6 per cent at M/16 |
| L3, same | interior shells: outer group at 2.5 m(shell), mid group at 4 m(shell), median abs(eps) | 4.4, 4.9 per cent | 1.0, 0.73 per cent at M/8 (5.7, 9.0 per cent at M/16: granular source, see below) |
| L3, same | lapse at the centre after the collapse; horizon's mean coordinate radius at t = 44 M | 0.020; 2.34 M | 0.074 at M/8, 0.037 at M/16; 0.73 M |

Choice of T (from L1 and L2): the departure of the central lapse from the homogeneous
value is set by the ratio of T to the time a gauge wave needs to cross the expanding
region, t_c = R/sqrt(2 alpha): T/t_c <= 0.075 gave at most 1.4 per cent, 0.15 gave 2.8
to 3.9 per cent, 0.3 gave 13 to 20 per cent (a dip that arrives from the surface at
t ~ t_c, focused by the spherical geometry). Short T costs nothing measurable: T = dx/8
(rate x step = 2) ran as well as T = dx/2 on the marginally bound ball, and on the bound
ball at cells M/2 the core error falls monotonically with T (1.73e-2, 1.25e-2, 1.09e-2
for T = 0.5, 0.25, 0.125 M; the other shell groups do not depend on T). Rule
[JUDGEMENT]: **T <= 0.1 R/sqrt(2 alpha)** for the smallest expanding region of radius R
that should be followed, as short as the step allows, and lapse_leak x dt below about
2.7 (explicit fourth-order step; dt is the global step, set by the finest level). For
balls of 5 to 10 M: T = 0.125 to 0.5 M. In the limit of small T the condition is 1+log
with the lapse capped at alpha_0 where the matter expands. Untested: `lapse_leak_alpha`
other than 1.

Collapse to a black hole (L3; run core-20261119-140652-fd7e8d0, analysis
core-20261119-161350-929b6b3, journal entry 9). After the turnaround the condition is
plain 1+log started from a lapse near 1; the slices reach the trapped region and the
horizon has the right mass, as with plain 1+log [VERIFIED, table]. What changes is the
coordinate picture [VERIFIED, horizon summaries; reading JUDGEMENT]: without the front
of plain 1+log the ball collapses into a region three times smaller in coordinates
(horizon radius 0.73 M against 2.34 M), so at a fixed mesh the forming hole and the
surface layer near it have three times fewer cells. At cells M/8 that leaves the lapse
at the centre at 0.074 and the surface shells 3.6 per cent slow near R = 2.5 M; cells of
M/16 at the centre halve both. With the cloud at the finest level (the rule of
`problems/ball/ball_collapse.athinput`) cells of M/16 under a particle lattice of M/4
give a granular source and worse interior shells. Advice [JUDGEMENT]: for a collapse
with `lapse_leak` give the centre cells of M/16 or finer and a particle lattice (or a
cloud level, `deposit_max_level`) that matches them. The prediction that the surface
shells follow the exact solution to 3 per cent down to R = 2.5 M is refuted in every
run, with plain 1+log too (largest error 10.1 to 12.7 per cent). Not tested:
compressions far beyond this ball's (Track A's collapses), runs past 45 M.

### 7.2 Shift damping that follows the black holes (`shift_eta_profile`)

    eta(x) = shift_eta [1 + sum_A (M_ref/m_A - 1)/(1 + abs(x - x_A)^2/w_A^2)],
    w_A = shift_eta_width x (smallest m_A, or m_A with shift_eta_width_local)

over the trackers with `co_<A>_mass` > 0 (written by `puncture_setup`), positions of the
current stage; the main loop subtracts shift_eta beta^i, the extra loop
(eta(x) - shift_eta) beta^i. The paper's profile (main.tex L388-397, width 2); its factor
on kappa_1 is not implemented. Tests [VERIFIED, journal entries 5 and 8; processors on
a small mesh (half-width 32) and a card on the full mesh (half-width 64): the tracker
speeds of E1 agree to four digits between the two]:

| test | eta at the hole(s) | tracker speed relative to the hole's own-units reference (eta m = 2) | horizon mass |
|---|---|---|---|
| E1 one hole, m = 1, t = 4.9 m | constant eta m = 20 / profile to 2 with width 2 / width 8 | 0.22 / 0.55 / 0.86 | equal to 1e-5 in all runs |
| E1, same | constant eta m = 0.2 / profile to 2 with width 2 / width 4 / width 8 | 1.97 / 1.27 / 1.04 / 1.02 | equal to 1e-5 in all runs |
| E2 pair m = 1 and 0.25, t = 2 M (processors) | constant 2 / constant 8 / profile 2 and 8, width 2 | heavy: 1 / 0.43 / 0.997; light (reference eta = 8): 1.46 / 1 / 1.20 | both found in every search, equal to 5e-4 |
| E2, t = 4 M (card) | constant 2 / constant 8 / profile 2 and 8, width 2 | heavy: 1 / 0.33 / 0.992; light: 1.36 / 1 / 1.22 | both found in all 32 searches, equal to 2e-4 |

Reading [JUDGEMENT]: with the width of the paper the profile leaves the heavy hole
exactly as with its own eta and takes the light hole part of the way (in the logarithm
of the speed: 52 per cent at t = 2 M, 35 per cent at t = 4 M) from the constant-eta
value to that of its own units, because the shift that carries a puncture builds up
over a region of several m_A in which the profile has already relaxed towards
shift_eta. The width is what limits it [VERIFIED on one hole, E1]: with
`shift_eta_width` = 4 and 8 the under-damped hole follows its own-units reference to 4
and 2 per cent over the first 5 m, and width 8 brings the over-damped hole from 0.55 to
0.86. On a pair the wider profiles have no result yet: a card job with widths 4 and 8
on the pair of E2 (run core-20261119-143517-ec2f4fc, prediction in journal entry 8)
was still queued when this package closed.
None of the runs shows a loss of a horizon or a change of a horizon mass; the
constraint norm at the end is that of the constant-eta runs (E2 has one early spike at
t = 0.5 M in every run, 2.8 times larger with the profile). The speeds compared are
those of the first few m, before the shift has settled.

Answer to Track F (request 20261115T1507Z): use `shift_eta = 2/M` with
`shift_eta_profile = true`, `shift_eta_mref = M` (the heavy mass) and
`shift_eta_width = 4` [JUDGEMENT, from E1 on one hole]: the heavy hole keeps eta M = 2
and each member gets eta m = 2 at its puncture (input:
`problems/puncture/by_unequal.athinput`, which has width 2; add
`shift_eta_width = 4.0` to its `<z4c>` block). A wide profile also raises the damping
at a neighbour within a few widths: at separation D a member of mass m adds
(M_ref/m - 1)/(1 + D^2/(w m)^2) to eta/shift_eta there (0.18 at the heavy hole of the
pair of E2, D = 8 M, width 8). For Track F's input `hills_q10_m8.athinput` (members
m = 0.05 M at a separation of about 3 M, the binary's semi-major axis; periapsis 8 M from
the heavy hole) width 4 raises eta at
a member by 0.4 per cent through the other member and at the heavy hole by 2.4 per cent
through both members at periapsis (width 8: 1.7 and 9.5 per cent). Constant eta = 2/M
for q <= 10 [JUDGEMENT]: acceptable for the horizon masses and the constraints (E1:
eta m = 0.2 changes neither), not for the members' coordinate tracks in the first tens
of m (twice as fast as with eta m = 2 in E1); the effect on a Hills passage is not
tested here (Track F's R4). Untested: `shift_eta_width_local`, more than two holes, runs
longer than 6 m.

### 7.3 A puncture inside expanding dust (Track D)

[JUDGEMENT, from 7.1 and test P] What it needs: (1) the lapse of 7.1, 1+log with
advection plus `lapse_leak`: at the hole the lapse is below 1 and the term is exactly
zero, so the puncture is sliced as in every verified isolated-system run (test P: a
puncture alone with and without the term gives identical output files over 10 M; the
largest lapse of Track D's 500 M run D-bh-dress-20261115-121313-284ec4f is 0.9972,
`punc.nrpic.hst` column 30, so that history is what the term gives); in the dust the
lapse tends to exp(6 T H) (1.07 for T = 2 M at Track D's H = 5.58e-3/M) instead of
1 + 6 ln a (4.9 at tau = 200 M); (2) the Gamma-driver with `shift_eta` = 2/M and zero
shift at the start (dust at rest in the coordinates); (3) `lapse = table` (psi^-2) or
`precollapsed`; (4) an outer boundary further from the dust than the light travel
time of the run: the outflow condition is not transparent for the Painleve-Gullstrand
exterior, whose K_ij falls as r^(-3/2) (`JOURNAL-id.md` entry 5; no transparent
boundary is offered here). Nothing else in the source. Choice of T: the dust region of
Track D's data is 24 M thick (wall at 36 M, outer edge at 60 M), so T <= 2 M
(T/t_c <= 0.1 with t_c = 24 M/sqrt(2)); with 6 T H = 0.07 the lapse excess is small
anyway. Input: `problems/es/es_gauge.athinput` (T = 2 M, cells 2 M in the dust, M/8 at
the hole, boundary at 96 M, 30 M).

Test ES [VERIFIED, run core-20261115-202901-b4430da, card, 185 s; journal entry 8;
figure `tracks/core/analysis/gauge/figs/es_gc_es-leak2.png`]: Track D's data
(`make_es.py --Rb 56 --w_out 4 --hp 2.0`, M = 1, wall at 36 M, 87128 dust particles on a
lattice of 2 M) with that input, 30 M:

| quantity | exact or expected | run |
|---|---|---|
| apparent-horizon mass | M on every slice | 0.99997 at t = 10 M; 0.99989 to 1.00099 for 10 M <= t <= 30 M (drift 1.0e-3), flat at 1.00098 from 25 M on; 0.99966 to 1.00099 from 3 M on |
| the same drift without dust | | vacuum puncture on the same finest cells (test P, card): +8.6e-4 from 10 M to 19.5 M, against +9.1e-4 here: the drift is the puncture's at cells M/8 |
| wall tracers (R_0 = 36 M), areal radius at their proper time | 38.320, 40.572, 42.763 M at tau = 10, 20, 30 M | 38.321, 40.572, 42.762 M; largest relative difference 6.2e-5 |
| other tracer groups | exact curves | 7e-5 (20 M), 1.2e-4 (28 M), 4.6e-4 (40 M), 6.8e-5 (48 M), 2.4e-4 (56 M); 1.1e-3 for the group that falls into the hole (6 M, until R = 2.2 M) |
| lapse in the dust (tracers at 48 M) | homogeneous value 1.062 to 1.055 | 1.061 to 1.041 (within 1.3 per cent); 1.045 to 1.060 at the wall; plain 1+log would reach 2.37 |
| largest lapse on the mesh | | 1.109 at t = 5 M, 1.063 at 30 M, at areal radius 21 M inside the vacuum bubble (not in the dust) |
| lapse at the puncture | collapsed | 0.031 at the start, a bump to 0.23 at t = 5.75 M (start lapse psi^-2 and zero start shift adjusting), 0.053, 0.032, 0.038 at t = 10, 20, 30 M |
| dust and bubble | no dust inside the wall | innermost dust particle 0.2 M outside the wall tracers at t = 30 M |
| tracers falling in from 6 M | horizon crossing near tau = 15 M | all 14 removed (lapse below 0.05) at tau = 15.5 M |

Two items of the prediction written before the run failed without refuting it: the
horizon-mass drift (1.02e-3 against the bound 1e-3) and the largest lapse on the mesh
(1.109 against 1.09: I had bounded it by the dust plateau; the bubble's normal
observers expand faster). Nothing in the run shows a defect of the condition. Not
covered: runs longer than 30 M, a finer dust mesh, the outer boundary.

## 8. Reported by Track D: ES-1G to 200 M (added by the lead of core, 2026-11-21)

Track D ran ES with `<z4c> lapse_leak = 0.5`, T = 2 M, to 200 M on a card (run
D-20261119-142633-6f72922, 0.794 card-hours, card executable of core/gauge, sha256
c3560e53...; judged in D's `es_runs/JOURNAL.md` entry 9; D's recheck
D-20261121-063617-3f2036f; message `es1g-outcome-for-gauge-ready` of 2026-11-21). As D
reports it, not rerun by core:
- 0 to 30 M equal to core's ES test (core-20261115-202901-b4430da): horizon mass 1.9e-5
  apart at 10 M, the lapse at the same tracer 1e-5 apart, largest lapse 1.1086 in both.
- The dust is sliced on its exact curve: lapse at the R0 = 48 M tracers within 1.3e-2 of
  the homogeneous lapse_leak model over 10 to 200 M; wall tracers within 1.7e-4 of the
  exact curve to tau = 206 M (1+log: 2.2e-3); no lapse pulse into the hole.
- At the hole: the apparent horizon shrinks in coordinates from 1.40 M (t = 25 M) to
  0.78 M (6.2 cells of M/8) at 200 M; the smallest lapse on the mesh rises from 0.039
  (50 M) to 0.069 (200 M), above `alpha_exc = 0.05` from t = 108 M on; the horizon mass
  grows by 7.0e-3 over 100 to 200 M while the exterior mass is lost through the outflow
  faces (D's `boundary-benchmark-v1b`).
Open: whether the shrinking coordinate size and the rising puncture lapse belong to
`lapse_leak` with the Gamma-driver, and which `shift_eta` keeps the hole near 2 M
(no run of core; `REQUESTS_WAVE3.md` W14); the faces (core/z4c-faces, W13); a lapse
excision threshold that does not rest on an absolute `alpha_exc` (W15).

## 9. Second pass of the relaxed lapse: switch-off around tracked black holes (branch `core/gauge-2`)

Decision 0022 item 3. Journal `tracks/core/JOURNAL-gauge-2.md` (entries 1 to 11; every
number below has its run id there); scripts, lists, inputs, figures and numbers
`tracks/core/analysis/gauge2/`. Source: `athenak/src/z4c/z4c_gauge_ext.hpp` only (the
hooks of section 7 in `z4c.hpp`, `z4c.cpp` and `z4c_calcrhs.cpp` are untouched).

### 9.1 The defect and its cause

Section 7.1 says that the term "vanishes where alpha <= alpha_0: a collapsing region and
a black hole are sliced by plain 1+log", and section 7.3 that a puncture inside expanding
dust is "sliced as in every verified isolated-system run". That holds for a hole on a
slice with K = 0 around it (test P). It does not hold on the slice of the
Einstein-Straus data, whose vacuum bubble has diverging normal observers
(K_T = -f(R) sqrt(2M/R^3)): there the term acts on the whole bubble outside about 7 M
from the first M on and holds its lapse at 1.04 to 1.015, where plain 1+log lets it rise
to 1.4 to 1.7 and fall back.

[VERIFIED: Track D's runs V-1B, V-1GB and this package's jobs A and B] With the first
pass the horizon does not get the coordinate size that plain 1+log gives it on this slice
(1.4 M instead of 2.06 M at 20 M) and then shrinks without stopping (1.09 M at 100 M,
0.875 M at 200 M in vacuum; 1.06 M and 0.78 M inside dust), while the conformal factor
chi of the bubble falls. The horizon mass follows with a delay: within 1e-4 of the
control to 100 M, +1.3e-3 over 100 to 200 M in vacuum and +7e-3 with dust (Track D), when
the horizon is down to 7 cells of M/8.

[JUDGEMENT, consistent with every run of the package; tested by 9.3] Why: without shift
1+log keeps alpha - 2 ln sqrt(gamma) constant along the normal observers, so a lapse
that returns to its stationary value brings the volume element back with it. The
relaxation term breaks this on purpose,

    d(alpha - 2 ln sqrt(gamma))/dt = -(alpha/T) max(ln(alpha/alpha_0), 0),

so where the lapse is held above alpha_0 the volume element of the normal observers
grows by (1/2T) int ln(alpha/alpha_0) dt: in the dust the intended comoving expansion,
in the vacuum bubble a stretching of the coordinates. The normal observers drift
towards the puncture at the speed of the shift (0.06 at 5 M, 0.25 at 1 M) and carry the
stretched elements into the hole within 50 to 150 M.

Candidate causes that were tested and failed as causes [VERIFIED, journal entry 9]: the
kink of max(.,0) (a smooth onset changes the horizon radius by 1 per cent); the action of
the term within 6 M of the hole (switching it off there leaves the radius within 4 per
cent of the first pass); the overshoot of a settling puncture (zero on a K = 0 slice);
the horizon finder (Track D: the Misner-Sharp mass of the slice follows it).

### 9.2 The option

    <z4c> lapse_leak_hole = r_h      (absent or 0: the first pass, bit for bit)

    d_t alpha = [section 1] - (alpha/T) w_h(x) max(ln(alpha/alpha_0), 0),
    w_h = prod_A S(|x - x_A|/r_h - 1),   S(s) = s^2 (3 - 2 s) for 0 < s < 1, 0 below, 1 above

over all compact-object trackers A (`<z4c> co_<A>_type`; positions of the current
stage; at most 8): the term is off within r_h of every tracker and acts in full beyond
2 r_h. Without a tracker the option does nothing and the kernel runs the statement of
the first pass. A puncture that has no tracker needs one for this option: add
`co_0_type = BH` and `co_0_x, co_0_y, co_0_z` to `<z4c>` (a tracker alone changes no
other output). Example: `problems/es/es_gauge_hole.athinput` (Track D's
Einstein-Straus data, r_h = 16 M; give `particles/particle_file` and
`problem/comp0_file`).

Choice of r_h [JUDGEMENT from two radii, 6 and 16 M]: large enough that the normal
observers that start outside r_h do not reach the horizon during the run (the shift is
0.02 at 20 M: from 16 M the drift takes several hundred M; 6 M is not enough), and
small enough that 2 r_h stays inside the matter that needs the term. With the wall of
Track D's bubble at 33 M, r_h = 16 M puts the wall at the edge of the full term and
costs a factor 3 in the accuracy of the wall tracers (9.3); a smaller radius was not
tried.

### 9.3 Tests

Card runs with finest cells M/8 unless said; "first pass" is `lapse_leak` without the
option; ES-1G, V-1B, V-1GB are Track D's runs (D-20261119-142633-6f72922,
D-20261120-222625-63abd72, D-20261121-125909-06f856e).

| test | plain 1+log | first pass | `lapse_leak_hole = 16` |
|---|---|---|---|
| Einstein-Straus data, T = 2 M, 100 M (`es-hole`; mesh of `es_gauge_hole.athinput`): horizon radius at 25, 50, 75, 100 M | | ES-1G: 1.40, 1.33, 1.18, 1.06 M | 1.59, 1.61, 1.63, 1.65 M |
| same: horizon mass over 40 to 99.5 M | | ES-1G: 1.00098 to 1.00125, rising (2.7e-4) | 1.00085 to 1.00129 (4.4e-4): wiggles of 2e-4 between 33 and 78 M while the lapse front of the freed zone dies out, flat afterwards |
| same: wall tracers (R_0 = 36 M), areal radius at their proper time against the exact curve, until 30 / 60 / 100 M | Track D: 2.2e-3 at 200 M | 6.2e-5 / not run on this lattice / not run (Track D, lattice 1 M: 1.7e-4 at 206 M) | 2.1e-4 / 4.3e-4 / 6.3e-4 |
| same: tracers at 20, 28, 40, 48, 56 M until 30 M | | 7.0e-5, 1.2e-4, 4.6e-4, 6.8e-5, 2.4e-4 | 3.8e-4, 5.2e-5, 4.8e-4, 8.3e-5, 2.1e-4 |
| same: lapse at the dust tracers (48 M) off the homogeneous model; largest lapse on the mesh | | 1.3 per cent; 1.11 | 1.2 per cent; 1.62 at 15 to 20 M (the front inside r_h), 1.05 from 80 M |
| vacuum (the same slice without dust, reduced mesh `problems/es/v1_small.athinput`, faces at 64 M: valid until 50 to 70 M): horizon radius at 20, 30, 50, 65 M | 2.06, 1.91, 2.04, 2.09 M (V-1B) | 1.38, 1.42, 1.33, 1.24 M | 1.90, 1.39, 1.59, 1.75 M |
| same: horizon mass over 35 to 65 M | 1.7e-5 (V-1B) | 8.4e-5 | 8.2e-5 |
| vacuum, faces at 256 M, 200 M (`v8far-hole16`, cleaned card build): horizon radius at 50, 100, 160, 199.5 M | 2.04, 2.15, 2.19, 2.20 M (V-1B) | 1.33, 1.09, 0.93, 0.875 M (V-1GB) | 1.59, 1.64, 1.44, 1.31 M |
| same: drift of the horizon mass from its value at 100 M, 100 to 199.5 M | [-4.8e-5, +2.0e-5] | [-5.6e-4, +1.26e-3] | [0, +2.08e-4]: a step of 2e-4 until 116 M, then flat |
| same: horizon mass, largest minus smallest, 120 to 199.5 M / 40 to 199.5 M | 6.8e-5 / 6.8e-5 | 1.8e-3 / 1.8e-3 | 4.4e-5 / 3.7e-4 |
| vacuum at finest cells M/4, faces at 128 M, 100 M (`v4-ctl`, `v4-leak`): horizon mass, largest minus smallest, 40 to 99 M; radius at 99 M | 1.7e-3; 2.12 M (8.5 cells) | 3.1e-2; 1.04 M (4.2 cells) | not run |
| expanding ball L1, bound ball L2, collapse L3 (no tracker) | | section 7.1 | identical with the first pass byte for byte on processors: L1 at cells 1 M to 10 M (17 files), first 16 steps of L2 at cells M/2 (9 files), first 8 steps of L3 (7 files) |
| a radius beyond the mesh (`lapse_leak_hole = 1000`, coarse vacuum mesh, processors) | the same bytes | | |
| byte regression against release core-v0.6, option absent (twelve set-ups, processors) | | 75 of 75 items identical | |

Processor checks of the cleaned source (commit 984110c3) [VERIFIED, journal entry 10]:
with the switch-off active (8 M, coarse vacuum mesh) it writes the bytes of the build
that ran the card tests of the first three rows (commit 90f52f4d); the 200 M and M/4
rows ran with its own card build.

### 9.4 Tried and removed

Two more factors existed in commit 90f52f4d and were removed after their tests
[VERIFIED, journal entries 6 and 9]:
- a weight by the local matter density (`lapse_leak_rho`: the term only where matter
  is). In vacuum it is plain 1+log exactly (byte for byte, processors and a card). But
  the vacuum next to expanding matter has diverging normal observers too; with plain
  1+log there and a capped lapse in the matter, the whole lapse difference sits on the
  matter's surface: L2 (bound ball, cells M/4) shell errors 3 to 47 times those of the
  first pass (surface 0.30), L3 turnaround at 1.32 to 1.35 R_0 instead of 1.25 and a
  horizon mass 3 per cent high, Einstein-Straus wall off by 6e-2 and a horizon mass
  swinging by 4e-3. Decision 0022's first alternative ("the relaxation must act only
  where matter expands") is therefore not a correction.
- a smooth onset of the term (`lapse_leak_onset`): no effect on the defect.
An input that still carries these lines runs unchanged: the parameters are not read.

### 9.5 What the option does and does not do

[VERIFIED, journal entry 11] In vacuum with r_h = 16 M over 200 M: the dip and the late
rise of the first pass are gone (band over 100 to 200 M 2.1e-4 instead of 1.8e-3; flat
within 4.4e-5 from 120 M on), but the control's level (6.8e-5) is not reached: the
lapse front of the freed zone leaves transient wiggles of up to 2e-4 in the horizon
mass until about 116 M (78 M on the Einstein-Straus data), and the mass settles 2.5e-4
above the control. The horizon radius is steady near 1.6 M until about 110 M and then
falls again (1.31 M at 200 M, -3.5e-3 per M at the end): the zone beyond 2 r_h is still
held and its stretching reaches the hole about 100 M later than in the first pass. So
with r_h = 16 M the option is a mitigation for runs of up to about 200 M at cells of
M/8 (the horizon keeps 10 cells in its radius where the first pass keeps 7), not a
cure. On the Einstein-Straus data the price is a wall followed 3.4 times less closely
at 30 M (2.1e-4) than by the first pass.

Advice [JUDGEMENT]: for a black hole inside expanding dust (Track D) use
`lapse_leak_hole` with 2 r_h at the inner edge of the dust and a tracker at the
puncture; measure a null test of the horizon mass after the transient (from 80 to
120 M on); keep the horizon above 10 cells by resolution if the run is longer than
200 M. For a hole in vacuum with no expanding matter nearby do not use `lapse_leak` at
all. Cheapest set-up that shows the defect: `problems/es/v1_small.athinput` with
finest cells M/4 and the faces at 128 M, 100 M, 4 minutes on a card (first pass against
plain 1+log: horizon mass band 3.1e-2 against 1.7e-3).

### 9.6 Not tested, open

Einstein-Straus data beyond 100 M with the option, and the first pass to 100 M on the
same mesh; radii other than 6 and 16 M; more than one tracker, a moving hole, MPI;
holes that form during the run (no tracker before the collapse: the option does
nothing; Track A's horizon mass at first detection was not examined); a cure of the
stretching itself (a wider transition around matter for a density-tied term, or a
shift condition); the mechanism by which the stretching of the held zone reaches the
hole after about 100 M (the drift of the normal observers alone gives several hundred
M). The outer faces: an outflow face at 64 M changes the horizon mass by 2e-3 to 3e-3
after 53 M (plain 1+log) or 71 M (relaxed lapse).
