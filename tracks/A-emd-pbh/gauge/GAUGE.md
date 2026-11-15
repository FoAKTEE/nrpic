# Gauge for the expanding-ball problem (A-pre-4, part 1)

Helper of A-emd-pbh, 2026-11-15. Candidate lapse and shift conditions, what the three
source papers found with them, what this repository's AthenaK already has, what needs new
source (written by core, decision 0010), and the criteria for choosing among them in the
expanding-ball problem of S1. Labels: [VERIFIED] read in the source at the locator given;
[BACKGROUND] standard, not re-checked here; [JUDGEMENT] my inference; [TO VERIFY] open.
Locators: `M` = `kb-data/raw/arxiv/2610.23218/v1/src/main.tex`, `P` =
`kb-data/raw/arxiv/2608.13206/v3/src/PRD.tex`, `Y` =
`kb-data/raw/arxiv/2609.14218/v1/src/MDPBH.tex` (line numbers); code paths relative to
the repository root; tests T1 to T4 and their run ids in `JOURNAL.md`.

## 1. What the papers found

### 2610.23218 (Munoz, Byrnes, Bruni, Hawke): dust fluid, Einstein Toolkit, matter era

Set-up: Einstein-de Sitter plus a sinusoidal curvature perturbation, peak density contrast
0.03 at the start, wavelength 4 initial Hubble radii, octant with symmetric boundaries,
64^3 base grid plus up to 8 refinement levels (M:59-78). BSSN (W form), fourth-order
differences (M:104-111, 175). [VERIFIED]

| What they tried | Outcome | Locator |
|---|---|---|
| Synchronous comoving gauge, alpha = 1, beta = 0 | crashes at the spherical-collapse time (shell focusing), with or without shock capturing | M:150, 161 |
| Puncture gauge: d_t alpha = -2 alpha (K + 2/tau), d_t^2 beta = 0.75 d_t Gamma - d_t beta | runs past collapse, then finite-difference noise | M:150-157 |
| + high-resolution shock capturing + Kreiss-Oliger dissipation (epsilon = 0.2) | needed for a stable evolution; lapse minimum about 0.55 without dissipation | M:159-179 |
| Bona-Masso family d_t alpha = -alpha^2 f(alpha) g(alpha, K): f = 2/alpha (1+log) and f = 1 + 1/alpha^2 (shock-avoiding) | similar; shock-avoiding lasts slightly longer but allows alpha <= 0 | M:190-202 |
| g = K | lapse rises to "alpha ~ 20" during the expansion before it collapses; too far to fall stably | M:208 |
| g = K - <K> (box mean) or K - K_edge | used by others; not available in their code (local only) | M:210-212 |
| g = K - K_FLRW, K_FLRW = -2/tau with tau the local proper time | three phases: oscillations to collapse time; lapse falls to about 0.5 up to delta^(1) ~ 2.7; then rises again (g oscillates about a negative value) | M:213-222 |
| g = K + sqrt(24 pi rho) | no lapse collapse before the crash | M:226-230 |
| g = exp(-alpha) K | lapse growth "from 20 to 2", still not stable | M:232-236 |
| alpha ~ (1 + delta)^-1 | CFL instabilities | M:238 |
| softplus g = (1/S) ln(1 + e^(S(K - T))) + T, S = 450, T = -max(-T, g) | best lapse: falls stably towards zero; run still crashes | M:240-250 |
| Gamma driver d_t beta = B, d_t B = 0.75 d_t Gamma - eta B, eta = 1 at first | best eta depends on the refinement level: 1 (level 8), 0.1 (level 6), 0.01 (level 4) | M:263-294 |
| eta from the conformal factor (Mueller-Bruegmann) | slower lapse, earlier end | M:296-300 |
| softplus on coarse levels | void regions with K -> 0^- enter the transition zone; the lapse falls everywhere; the box stops evolving | M:303 |
| advection terms in lapse and shift | effects depend on resolution, marginal | M:307 |
| Diagnostics: hoop ratio 2M/R along three directions, outgoing expansion along radial lines, Kretschmann scalar and its Weyl/Ricci split | a few points with Theta_out < 0; the horizon finder (AHFinderDirect) finds no horizon | M:313-440 |

Their conclusion: the lapse must be adapted to the expansion; the shift damping must vary
in space with the resolution of the focusing region; no stable run to a horizon (M:443-451).
[VERIFIED]

### 2608.13206 (radiation fluid, GRChombo): the time step in an expanding background

| Item | Content | Locator |
|---|---|---|
| Cosmic-time slicing | (d_t - beta.d) alpha = -2 alpha (K - K_b), K_b = -3H(t) analytic (or the box mean <K>) | P:237-246 |
| Lapse mode speed | sqrt(2)/a in cosmic time on FLRW | P:262 |
| Shift mode speeds | v_T = sqrt(b), v_L = sqrt(4b/3), not redshifted; damping limit eta dt <~ Q' (Schnetter) | P:264-307 |
| Scaled driver | b = b0 (a_i/a)^2, eta = eta0 a_i/a, with dt_0 = min(0.25 a dx_0, 0.02/H) | P:309-334 |
| Conformal-time slicing | (d_eta - beta.d) alpha = H_conf alpha - 2 a alpha (K - K_b); standard driver b = 3/4, eta = 1; differs from the scaled cosmic driver by a term -H beta | P:336-383 |
| Results | scaled and standard drivers give the same horizon masses; time step 0.520 t_H against a cap of 2.60e-3 t_H; 1092 against 102436 coarse steps (factor 94); zero shift breaks down at t/t_H = 74.87 with stronger coordinate stretching (horizon masses agree before); conformal and cosmic time agree | P:389-413 |
| Interior regularization | right-hand sides multiplied by exp[-s (1 - r^2/r_reg^2)^p] inside half the horizon radius, for the full periodic box | P:428-434 |
| Horizon mass | finder of GRChombo, M = (A/16 pi)^(1/2); late growth fitted to the Zel'dovich-Novikov law | P:228-231, 457-495 |

[VERIFIED]

### 2609.14218 (Yoo, Escriva, Harada, Kohri): dust and particles, matter era

| Item | Content | Locator |
|---|---|---|
| Slicing | (d_t - beta.d) alpha = -2 alpha (K + 3H) + (3/2) alpha H_k exp(-C^2 alpha_b^2 / a_k^2), C = 5, alpha_b the lapse at the box corner: e-folding time early, cosmic time near horizon entry | Y:401-461 |
| Shift | (d_t - beta.d) beta = (3/4) B, (d_t - beta.d) B = d_t Gamma - 3H B | Y:463-469 |
| Coordinates | non-Cartesian, centre enlarged by 1 + eta = 11 | Y:473-487 |
| Initial slice | constant mean curvature, K = -3H | Y:516, 545 |
| Dust | crashes where the density diverges unless the singularity is well inside a horizon; slices may touch the singularity before the horizon (locally naked) | Y:172, 777-830 |
| Particles | uniform cubic cloud per particle; runs do not crash; horizon for mu >= 0.05; constraint violation large where particles cross, localized | Y:1053-1186 |
| Check against LTB | areal radius against proper length on slices of matched K | Y:1455-1470 |

[VERIFIED]

## 2. What this code has

Lapse right-hand side (`athenak/src/z4c/z4c_calcrhs.cpp:687-710`), with
`chi = gamma^(-1/3)` and the Z4c variable `Khat` (not `K = Khat + 2 Theta`):

    d_t alpha = lapse_advect beta.d alpha
              - [lapse_oplog lapse_harmonicf + lapse_harmonic alpha + lapse_volume chi^(-1/2)] alpha Khat
              - lapse_kdriver alpha_ref alpha (Khat - <Khat>_vol)
              + slow_start_lapse term

with `alpha_ref` the largest lapse and `<Khat>_vol` the proper-volume mean, both from the
state of each stage (`z4c_calcrhs.cpp:46-70`). Shift right-hand side
(`z4c_calcrhs.cpp:712-757`), first-order integrated Gamma driver, no auxiliary B:

    d_t beta^i = (shift_Gamma + shift_alpha2Gamma alpha^2) Gamma^i + shift_advect beta.d beta^i
               - shift_eta beta^i + shift_H (harmonic-type term) + drift control

Time step: `dt = cfl_number * min dx` over the whole mesh, one global step, no
subcycling (`z4c_newdt.cpp:40-58`); particles may cut it further (`dt_expansion`,
`cosmo/README.md:34`). [VERIFIED]

| Condition | In the code as | Tested here | Status |
|---|---|---|---|
| geodesic (alpha = 1, beta = 0, or the initial shift frozen) | `lapse_oplog = 0`, `lapse_harmonic = 0`, `shift_Gamma = 0`, `shift_eta = 0`, `shift_advect = 0` | cosmology inputs use beta = 0 | exists |
| 1+log, d_t alpha = -2 alpha K | `lapse_oplog = 2` (default) | Oppenheimer-Snyder and all self-gravity tests (`problems/os/os_amr.athinput:73-79`, `paper/main.pdf`) | exists |
| harmonic, f = 1 | `lapse_harmonic = 1`, `lapse_oplog = 0` | no | exists |
| conformal time, d_t alpha = -(1/3) alpha^2 K | `lapse_harmonic = 1/3`, `lapse_oplog = 0` | cosmology production (`cosmo/README.md:21-23`); no singularity avoidance (`cosmo/TESTLOG.md:204-212`; T1) | exists |
| volume lapse, alpha - gamma^(1/6) fixed | `lapse_volume = 1/3` | fails like the conformal one (`cosmo/TESTLOG.md:496-506`; T1) | exists |
| conformal + driver to constant mean curvature | `lapse_harmonic = 1/3`, `lapse_kdriver = mu` | collapses the lapse at the overdensity; 64 cells do not resolve the collapse (`cosmo/TESTLOG.md:611-624`) | exists |
| cosmic-time 1+log with box mean, -2 alpha (K - <K>) | `lapse_oplog = 0`, `lapse_kdriver = 2`; carries the extra factor alpha_ref | not run; equals 2608.13206's slicing in the toy (T1) | exists [JUDGEMENT on the equivalence] |
| cosmic-time 1+log with analytic K_b(t) (2608.13206) | | | new source |
| reference field K_ref(t, x) of the unperturbed exact solution (generalizes K_b to the ball) | | | new source |
| K + 2/tau_local (2610.23218) | needs a stored local proper time | | new source |
| softplus (2610.23218) | needs a stored T field | | new source |
| shock-avoiding f = 1 + 1/alpha^2 | the 1/alpha term is missing | | new source (one term) |
| exp(-alpha) K (Elley) | | | new source |
| e-folding slicing (2609.14218) | needs H_k, a_k, the box-corner lapse | | new source; designed for super-horizon starts in a box |
| conformal-time cosmological 1+log (2608.13206) | H_conf alpha - 2 a alpha (K - K_b) | | new source |
| integrated Gamma driver, speed sqrt(4 b/3) | `shift_Gamma = 0.75`, `shift_eta` | Oppenheimer-Snyder (`problems/os/os_amr.athinput:77-79`) | exists |
| alpha^2-scaled driver | `shift_alpha2Gamma = 0.75` | unstable in conformal time once alpha > 2.64 at cfl 0.25 (T3) | exists, do not use with a growing lapse |
| B-form driver; damping -3H B (2609.14218) | auxiliary field omitted (`paper/sections/method.tex:229`) | | new source |
| shift coefficients scaled with a (2608.13206) | | | new source; only with a cosmic-time step |
| eta varying in space (resolution, conformal factor, horizon mass) | tracked-puncture eta profiles of the source paper omitted (`method.tex:229`) | | new source |
| time step growing with a (cosmic time) | | | new source; unnecessary with the conformal-time lapse |
| interior regularization of the right-hand sides inside a horizon (2608.13206) | particle excision by lapse or horizon radius exists (`athenak/src/particles/nrpic.cpp:397-490`) | | new source |

Core's interface proposal (`git show core/nrpic:tracks/core/interfaces/cosmo_gauge.md`,
section 2) reads the code the same way and lists a shift in an expanding background as
untested; T3 gives a likely cause of the one failed attempt (the alpha^2-scaled driver
outruns the time step once the conformal-time lapse exceeds 2.64 at cfl 0.25).

## 3. What the expanding ball demands

The Phase 0 problem (brief S1; `coord/INTERFACES/spherical_id_format2.md`): a dust ball,
FLRW inside and Schwarzschild outside, asymptotically flat, on a slice of
Painleve-Gullstrand type with lapse, radial shift and extrinsic curvature from table format
2; an overdense core or a deformation inside collapses after its turnaround. Two features
matter for the gauge and differ from a periodic universe:

1. There is no single background. The expanding interior has K = -3H; the
   Painleve-Gullstrand exterior of the time-reversed (expanding) solution has
   K = D_i beta^i = -(3/2)(2M/r^3)^(1/2), half the interior value at the surface, and
   tends to zero outward [JUDGEMENT, derived from beta^r = -(2M/r)^(1/2) with flat
   slices; to be confirmed by A-pre-1's tables, which continue KL, KT as r^(-3/2)].
   Consequences: a box mean <K> is dominated by the exterior, so `lapse_kdriver` raises
   the interior lapse and lowers the far-exterior lapse; an analytic K_b(t) of the
   interior makes K - K_b = +(3/2)H > 0 just outside the surface and collapses the
   exterior lapse [JUDGEMENT]. Subtraction needs a reference field K_ref(t, x).
2. The matter is particles. Particles have no shell-focusing singularity of the fluid
   kind: the density at a caustic is bounded by the cloud size, and 2609.14218's
   particle runs did not crash (Y:175, 1087, 1141). So the lapse need not avoid a fluid
   singularity, only the black-hole interior after formation; lapse excision (absolute
   `alpha_exc`, `nrpic.cpp:117, 482-485`) assumes a lapse that collapses inside the
   horizon, which a conformal-type lapse of order a does not do.

Criteria, each with the measurement that decides it:

| # | Criterion | How it is measured | Evidence so far |
|---|---|---|---|
| C1 | Bounded lapse where matter expands and in the vacuum exterior | largest/smallest lapse outside the collapsing region; lapse against ln of the local expansion | Plain 1+log with zero shift: alpha - ln gamma is constant at every point, so alpha = 1 + 6 ln(local expansion): 19.0 at a top-hat that expands 20-fold, 25.2 in a background that expands 56-fold (T1, run A-emd-pbh-20261115-113614-374a41a); 2610.23218 reports ~20 (M:208). Damped exp(-alpha)K: 3.0 (paper: 2). |
| C2 | Right reference for the subtracted conditions | lapse in the exterior and at the outer boundary staying near its initial value before the collapse | none run; section 3, item 1 |
| C3 | Avoid the black-hole singularity but do not freeze the slices before a trapped surface forms | proper time of the core and of the shells at freeze, against the exact proper time of horizon formation at the core boundary (`DIAGNOSTICS.md`, section 3) | Toy (T1): conformal-time and volume lapses reach the crunch (no avoidance); background-subtracted conditions freeze a uniform-lapse top-hat at or before turnaround; softplus at 0.85 of the maximum radius; plain 1+log late (4 percent of the maximum radius). T4 (run A-emd-pbh-20261115-113810-e02c969): the toy is off by a factor 5 in the lapse after its maximum against the 3D driver run, so these freezing epochs are qualitative only. |
| C4 | Coordinate and slice stretching at and after collapse | smallest chi and det gamma, largest Gamma^i, constraint norms near the core; horizon mass constant after accretion ends | Zero shift: run ended with det gamma <= 0 at the refined overdensity (`cosmo/TESTLOG.md:754-764`, bh1); 2608.13206's zero-shift run broke down with stronger stretching (P:389, 400). Best eta depends on resolution (M:294). |
| C5 | Time step | every coordinate speed v times cfl below the limit of the discretization: C v <= 0.618 (lapse, light) and 0.660 (shift) with `diss = 0.5`, 0.664 and 0.728 without (T2, run A-emd-pbh-20261115-113755-cac3c4b); cost in steps to the collapse | The alpha^2-scaled driver in the conformal-time slicing passes the limit at alpha = 2.64 (cfl 0.25); bh2's constraints separate from its zero-shift twin after its largest lapse crosses 2.642 at t = 1.203 and fail at t = 1.97 (T3, run A-emd-pbh-20261115-113921-ca3786e). At fixed dt = C dx, cosmic time needs 278.7 time units to a 56-fold expansion, conformal time 12.97: 21.5 times fewer steps (T1). In the conformal-time slicing all background speeds stay of order 1 (T1 figure, bottom right). |
| C6 | Comparison with the exact solution | invariants only (shell proper time, areal radius, Misner-Sharp mass, Kretschmann scalar); a gauge equal to the exact solution's slicing allows slice-by-slice checks | geodesic slicing with the initial shift is the exact solution's own gauge before collapse [JUDGEMENT] |
| C7 | Interplay with particle excision | particles removed only inside a found horizon; no removal outside | `alpha_exc` absolute; `ah_exc_factor` uses the finder's smallest radius (`nrpic.cpp:399-420`) |

## 4. Candidates for the expanding ball, ranked [JUDGEMENT]

| Rank | Lapse | Shift | Status | Use | Why |
|---|---|---|---|---|---|
| 1 | geodesic | initial (Painleve-Gullstrand) shift frozen, or zero | exists | spherical verification through expansion and turnaround, up to near horizon formation | exact slicing of the solution; nothing to tune; crashes only at the caustic or the black hole |
| 2 | 1+log (moving puncture, as verified for Oppenheimer-Snyder) | `shift_Gamma = 0.75`, `shift_eta` of order 2/M_BH (the usual choice, M:268) | exists | first runs through horizon formation | no new source; lapse grows as 1 + 6 ln(expansion) before collapse (C1), tolerable for moderate expansion (about 15 for a tenfold expansion); check C5 with v = (2 alpha)^(1/2)/b |
| 3 | 1+log with K - K_ref(t, x), K_ref of the unperturbed exact solution | as 2 | new source (small: one stored field or table, A-pre-1 supplies K_ref) | the target condition for the ball | keeps alpha = 1 wherever the solution is unperturbed (C1, C2); collapses where the core contracts faster than the reference |
| 4 | softplus of K (2610.23218), offset below the outer-boundary K | as 2 | new source (stored T) | alternative to 3 without a reference | geodesic while expanding; 1+log once contracting; known coarse-level failure (M:303) to be avoided by the offset |
| 5 | conformal time, `lapse_harmonic = 1/3` | `shift_Gamma = 0.75` (never the alpha^2-scaled driver) | exists | pre-collapse phase of long expansions; Phase 1 periodic runs | cheapest time step (C5); no singularity avoidance (C3) |
| 6 | conformal + `lapse_kdriver` or the conformal-time 1+log of 2608.13206 | `shift_Gamma = 0.75` | exists / new source | Phase 1 periodic box | reference by box mean or analytic background works only in a box (C2) |
| - | e-folding (2609.14218), exp(-alpha)K, K + 2/tau_local, K + sqrt(24 pi rho) | | new source | not proposed | designed for other set-ups or reported inferior (section 1) |

Shift damping: start with eta of order 2/M_BH on the levels around the forming black hole
and test the level dependence that 2610.23218 found (M:294); a damping that varies with
the refinement level or the conformal factor is new source. Shock-capturing is irrelevant
here (particles), and the existing Kreiss-Oliger dissipation lowers the time-step limit
(T2).

## 5. Runs that decide (pending; none started by this package)

| Id | Run | Decides | Needs |
|---|---|---|---|
| G-R1 | `cosmo/east_d0.05_n64_bh2` again with `cfl_number = 0.125`, and once with `shift_Gamma = 0.75`, `shift_alpha2Gamma = 0` | T3: time-step instability predicts the onset moves to alpha = 5.3 (t = 2.6) with the halved step and no early growth with the unscaled driver | about 0.15 card-hours each (bh2 took 505 s, `athena.log`) |
| G-R2 | spherical expanding ball, geodesic slicing, against the exact solution (C6) | that the initial data and the invariants agree before collapse | A-pre-1 tables, core's format-2 problem generator |
| G-R3 | the same ball with ranks 2, 3, 4 through horizon formation, at two resolutions | C1 to C5 on the real problem; replaces the toy's freezing epochs (T4) | ranks 3 and 4 need core; card time to be set by the owner |
| G-R4 | a non-rotating collapse with the finder centre offset | spurious spin of the finder in an expanding background (`DIAGNOSTICS.md`, section 2) | any run of G-R3 |
