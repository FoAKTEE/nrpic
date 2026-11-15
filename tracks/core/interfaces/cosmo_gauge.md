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
| `shift_eta_width` (wave 2) | absent = 2.0 | w_A in units of the smallest tracker mass (the paper's 4 m_min^2 is width 2) | section 7 (only 2 is tested) |
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
