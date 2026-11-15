# C-sidm lead review of wave 2

Lead session of 2026-11-15 (19:20Z-), after the five helpers of wave 2 (box_tests, models,
threshold_scan, note, verifier) finished. Each package was checked from its registered
outputs, not from its conclusions: own readers of the AthenaK files and own Maxwell-Juttner
functions (`review_wave2/rvlib.py`), the verifier's independent operator for the fluid
onsets, reruns of the helpers' analysis where an independent route would only re-implement
the same arithmetic. Predictions L8-L12 were written into `../JOURNAL.md` before the runs;
all held.

Runs of this review (processors, 0 card-hours):

| Run id | What | Wall |
|---|---|---|
| C-20261115-193332-48771b4 | `review_wave2/run_review.sh`: L8 box tests (`rv_box.py`), L9 models and fluid onsets (`rv_models.py`), L10 card-run histories (`rv_scan.py`), L11 claims and locators (`rv_note.py`), rerun of the verifier suite with a byte comparison | 30 min, 2 cores |
| C-20261115-193751-d3872ff | `review_wave2/rv_kn.py`: K = 1/(rho0_c H_c) of the 13 wave-2 models (L12) | 3 s |

Figures made and looked at: `rv_box.png`, `rv_models.png`, `rv_scan.png`, `rv_note.png`,
`rv_kn.png` (in the run directories). Figures of the helpers looked at in this session:
box_tests 9 of 14 (t1t2_summary, t0b_replay, relax_T345_th1.0_s1, t4_zoom, t9_unequal,
t11_drift, t10_repro, cost_gpu, and the summary panels), models 4 of 4, threshold_scan 5 of
9 (the card-run figures), note 3 of 6 (both schematics, fig_sequences), verifier 1 of 7
(fig_v5_knudsen). Development runs of the review scripts on parts of the data
(`scratch/C-sidm/tmp/rvdev/`) were not registered; the registered run repeats them.

## 1. box_tests (collision operator of core-v0.3 in the Minkowski box)

Confirmed (recomputed from the registered outputs, run C-20261115-193332-48771b4):
- T2 rate, 16 runs (run C-20261115-165500-c67e036): mean sum_P per step over
  (1/2) N rho0 sigma <v_Mol>(theta of the first snapshot) dt = 0.999906-1.000096, z_b from
  -2.20 to +2.92; accepted collisions against summed sum_P z_a from -2.10 to +1.58; theta of
  the last snapshot equal to the first to 3.3e-13; n_trunc 0; mean n_sub 2.36-3.23 in the
  sub-cycled runs. Same numbers as the helper's. With the nominal temperature the ratio
  moves by up to 1e-3 (as the helper reports).
- T1: largest |dE|/sum M W per step 2.8e-19, |dP_i| 9.4e-20 (all T2 runs); the exactly
  rounded sum M W of first and last snapshot is bit-identical in all 16 T2 runs, all four
  T3-T5 runs and at all 11 snapshots of both 1e4-step runs (1.559e7 and 1.560e7 collisions;
  run C-20261115-170741-248af65).
- T10 (run C-20261115-165902-f9b1c8f): the particle records of the final snapshots of 8
  and 64 MeshBlocks and of the restarts from cycles 0, 37, 74 are byte-identical to 1
  MeshBlock; seed 8 differs in every particle (385554 collisions).
- T3-T5 (run C-20261115-170539-28432c3): my quadratic fit gives T4 slope/exact 0.9924,
  0.9792, 0.9959, 1.0088 with the window 0.15 tau_rel of the sample, as the helper; KS p of
  the final |u| against MJ(theta_eq) 0.084, 0.77, 0.987, 0.917; sum M W exact.
- T9 (run C-20261115-170814-8a54b43): class temperatures equal within |z| <= 1.16 in all 8
  seeds; mean energy drift +0.18(7) percent of the kinetic energy, z = 2.42 (helper: same).
- T11 (run C-20261115-174651-0ad8612): accepted vs sum_P z = +0.52, -0.21 (a, b) and
  -1.78, -0.15 (c); T1 per step 1.4e-19. The lab-frame expectation of T11(a) was not
  recomputed.
- T0b (run C-20261115-170155-13ff01f): the helper's replay rerun on the six registered
  dumps passes again with the same numbers (5045/27, 5042/26, 15153/459, 15423/512 tested
  and accepted; momenta within 4.4e-16). This reruns the helper's code; it is independent
  of core's twin because the helper wrote it from the interface text; core's own replay
  passes on seven cases (run core-20261115-145545-3629622).
- Cost: processor 5.8e-7 and 6.4e-7 s per tested pair at one sub-step, 3.4-3.5e-7
  sub-cycled (from the wall times of the T2 runs). The card cost (3.4-3.9e-9 s) was not
  recomputed.
- Figures: consistent with the numbers.

New in the recheck: T4 depends on the window edge. With the design tau_rel the window holds
16 snapshots instead of 15 and the ratios become 0.9963, 0.9826, 1.0003, 1.0088 (shifts of
0.5-1.4 se). The criterion passes either way; the low theta_2 = 1e-3 seed 2 stays low
(about -3.3 se from 1.0025). Open item O3 stands.

Not confirmed: the T11(a) lab-frame expectation and the D1/D2 diagnostics (not
recomputed); the card numbers of T10b and the cost (not recomputed).

Wrong: nothing in the operator or the tests. Findings of format, not of physics: F1
(`nrpic.hst` sum_mW is 0 without deposit), F2 (dump and key use step c, histories label
c + 1), F3 (snapshot header cycle lags by one), and F4 found here: the snapshot carries N
float64 of proper time after the species (`nrpic_io.cpp:943-944`), which `docs/FORMATS.md`
line 123 does not list. Request to core (outbox).

Fixed: `collide/TESTS.md` section 2a (T1 read from snapshots, T2(b) sample temperature,
T11(c) numeric criterion, precision limit of rate checks, T10b open for T4).

Open (large): T6-T8 heat conduction (the C-pre-1 item "heat conduction at both the long and
the short mean-free-path end": card runs), T12 (G2; core offers `metric_kind =
static_conformal`), the MPI variant of T10 (no MPI build), T10b for T4, O3, O4.

## 2. models (F21 b = 0.1 particle models, Juttner fluid onset, growth pipeline)

Confirmed:
- The 13 particle files at N = 1e5 (run C-20261115-170742-84990ed), read with my own
  readers and cubic table interpolation: sum m W/psi - M = -2.15e-5 to -2.39e-5 (F21) and
  -3.45e-5 to -3.95e-5 (King), equal to the JSON values to the printed digits; E/E0 < 1 for
  every particle; equal masses; |sum m u_i| <= 2.5e-17; the count inside the core radius
  equal to the JSON (to one particle).
- Fluid onsets for b = 0.1 with the verifier's Rayleigh-Ritz operator (not the helper's
  finite elements) and my own Juttner functions: F21 gamma 0.63482, Juttner Gamma_1 at the
  energy-matched temperature 0.53306, at theta = p/n 0.53170, at the Tolman temperature
  0.41253, Juttner 1 + p/u at the Tolman temperature 0.54038, fixed 5/3 0.77927; eps maximum
  0.54041. 10-term bases agree to 7e-5 (to 3e-4 for 5/3). All agree with the helper's
  values (0.6348, 0.5331, 0.5317, 0.4125, 0.5404).
- growth.py validation: the rerun of `validate_growth.py` gives a JSON identical to the
  committed `results/growth_validation.json`; G1 recovers 18 of 18 published numbers.
- Figures fig_fluid_onset, fig_models, fig_growth, fig_smoke agree with the JSON.

Not confirmed: my E/E0 maxima (0.99997 for tmb01_Z0p5404) differ from the JSON's 0.99992;
both below 1, cause not chased. The AthenaK read test A1 (run -174557-8978b36) was not
repeated. The J_pu onset coincides with the eps maximum to 3e-5 in Z(0); not explained.

Wrong (helper's own failed predictions, all on record in its journal): G2 (fit bias +2-4
percent on synthetic signals; cause found, D1), G4 (r10 rates 14-33 percent off), G5
partly; M3 three TOV-residual checks above 1e-6 (T1: the check's own h^2 error); A1 sum-m
bound 1e-13 too tight (1.1e-12).

Decided by the lead [JUDGEMENT]: the Kn -> 0 anchor becomes the Juttner Gamma_1 onset at
the energy-matched temperature, Z(0) = 0.5331 (b = 0.1); F21's 0.6348 stays the comparison
with F21's model; theta = p/n (0.5317) gives the systematic of the temperature
definition; the Tolman variant is not a local kinetic temperature and is dropped
(`G0/REPORT.md` decision 3, revised). Consequence: the fluid anchor lies 0.0074 below the
collisionless eps maximum; the G3 design "one model on each side" needs models in
0.50-0.533 (both stable), 0.533-0.540 (fluid-unstable only) and above 0.540.

Open: fold the `tmb` family into `equilibria/evstatic.py` (not done: two solvers stay;
King bit-identical); the radius KS test of `equilibria/check_equilibria.py` is not
independent (same CDF as the sampler): flagged here, the check stays reported as a
consistency check only; the growth-pipeline fix (boxcar = one core oscillation period,
departure from the equilibrium alpha_c) is untested on runs; no N = 1e6 models; no
perturbed models (core now has `perturb_gamma`, message of 19:16Z).

## 3. threshold_scan (six card runs CC1/CC2 at Kn = inf, 10, 1)

Confirmed from the histories (run C-20261115-193332-48771b4, `rv_scan.png`):
- alpha_min < 0.3 first at 72.5 M (cc1_kn1), 77.75 M (cc2_kn1), 184.25 M (cc1_kn10),
  206.75 M (cc2_kn10); first excision at 83.25, 88.75, 193.75, 216.5 M; excised rest-mass
  fraction 20 M later 0.823, 0.816, 0.910, 0.897; collisions per particle before
  alpha_min < 0.3: 13.4, 15.3, 2.48, 2.88.
- Controls keep 1e5 particles; alpha_c rises by 0.0334 (cc1_kninf, at 201.5 M) and 0.0185
  (cc2_kninf, 206.75 M); mean Lorentz factor changes by 0.0134 and 0.0072.
- Rest mass: sum_m bit-identical before excision; sum_m + m_excised + m_escaped within
  7.3e-15; n_trunc 0; collision counts against sum_P |z| <= 2.37; first-step sum_P 244.167,
  24.4163, 236.944, 23.696.
- Non-finite state at 204.25 M (cc1_kn1), 162.25 M (cc2_kn1), 289.5 M (cc1_kn10), and every
  run exits 0: confirmed (core G2 OPEN item 11).

Not confirmed: the energy defect per collision in the early window and the cell-size scaling
(not recomputed); the evaporation fractions (snapshots not read).

Wrong or overstated: the reading "both King models lie beyond the first mass maximum of
their sequence (y0 = 0.0982), so collisions find both unstable" is a [JUDGEMENT] resting on a
turning-point argument for thermally relaxed clusters that nobody has checked here; the King
family is not a sequence of constant entropy, and the collisional runs relax towards a
different (isothermal, evaporating) state on a few collision times. Recorded as an open
hypothesis, not a result. The positive energy defect (heating at the particles' metric,
+1.2e-10 of sum M W per collision early, 1.6e-3 accumulated at Kn = 1 before collapse) is
not ruled out as a contributor: core's `coll_energy = particle` (message of 19:16Z) removes
it, and the CC runs must be repeated with it before the collapse times are used.

Open (large): the controls' slow outward excursion (alpha_c +0.033 at the threshold model)
is unexplained and bears on the G2 threshold; collapsed mass as an apparent-horizon mass
(the static M/4 mesh fails after collapse; adaptive-mesh decks prepared, collisions on an
adaptive mesh untested by core); single seed, N = 1e5, 2.3 particles per collision cell on
average (16 in the core) against core's advice of about 100.

## 4. note (working note v0, schematics, ledger, G0 package)

Confirmed (L11): the three differences of `note/tables/claims.md` hold in the run outputs:
(a) F21 Table 1: B 2.43e-4 and eps 1.33e-4 at `main.tex:503` exceed 1.1e-4; also eps_c(0)
1.32e-4 (at `:498`, not `:503` as the helper wrote), E and E_rest 1.11e-4, and C 2.5e-3 (F21
computes C from its rounded R); (b) the fastest gravothermal phase lasts at least 8.5e4
t_dyn, not 1e5; (c) for Z(0) = 0.40-0.80, R/M = 19.8-28.1 and r_core/M = 1.27-2.56.
Corrected in `G0/REPORT.md` sections 1 and 3 and `G1/STATUS.md` item 2.

Not wrong: the "locator correction" 2601.17117 `SIDM_MS.tex:476` -> `:481`. Both lines of v2
carry M_BH ~ 200 M_sun, 3e-8 and 580 t_0 (my search: 200 at 476 and 481; 3e-8 at 68, 476,
481; 580t_0 at 476); the REPORT keeps 476 and adds 481. The kb's statement that the
astro-ph/0111176 row lacks a file name was right: it is `SMBH_SIDM_Xiv2.tex:289-291` (v3),
added to the REPORT.

Not checked: the 39 ledger rows one by one (the note helper's `ledger.py` reads them from
the registered JSON; I recomputed the three that differed); the PDF pages (the helper read
all 10).

Open: the note lacks the wave-2 results (box tests, models, card runs, Juttner anchor);
the architecture schematic shows "thermal-core particle models" and "collisions checked in
the box (T0b-T11)" as to be ported, both now done except T6-T8; the reviewer step of the
paper-writing skill was not done.

## 5. verifier (fresh-context check of the G0/G1 material)

Rerun: the verifier's suite (`G0/verifier/run_all.sh`) rerun inside the review run gives
byte-identical JSON for all five parts (mono, king, puls, rate, costs). Its operator was
then used for my independent onsets (section 2).

What the track does about each WRONG or NOT CONFIRMED item:

| Finding | Action |
|---|---|
| V4b WRONG: SCOPE.md section 1 uses the trial root 0.750 as the fluid threshold | Fixed: SCOPE.md section 1 now gives the exact onset 0.6348 (window 0.540-0.635) and a dated note that with the Juttner Gamma_1 the anchor is 0.5331 and the window closes |
| V5 NOT CONFIRMED: "one Knudsen number" (four values of sigma~ for "Kn_c = 1") | Fixed: track definition written into `collide/SPEC.md` section 1 and `equilibria/CONVERSION.md` section 5 (K for all 13 wave-2 models, run C-20261115-193751-d3872ff); SCOPE.md section 4 points to it; the CC runs used K = 168.895 and 186.081 (track definition) |
| V4 unit label: tmb.pulsation omega^2 in surface-observer time | Fixed: note in `gravothermal/README.md` (multiply by 1 - 2C for the time at infinity; onsets unaffected) |
| V8 mis-described locator 2105.05556:581 | Fixed: SCOPE.md section 3.4 (small i near the polytrope; for 100 <= i <= 250 the onset is unrelated to the extrema, paper.tex:599) |
| V1 note: no stability theorem for the monoenergetic family | Added to SCOPE.md section 3.1; the family stays verification only |
| V7: sub-step estimates conservative by 1.6-1.9 | Recorded; the measured costs of the box tests replace the estimates (card 3.4-3.9e-9 s per pair) |
| Weak point 2: the fluid end is not pinned | Partly closed: Juttner onset computed twice (sections 2 and 5); the GR-hydro view (core: `dyn_grmhd` needs a Synge equation of state, two to three core sessions) is a decision for the orchestrator |
| Weak point 3: the collisionless threshold of the core-halo family has no anchor; budget | Open: the G2 scan (SCAN.md, 26-28 card-hours) must cover Z(0) up to about 1 for b = 0.1 |
| C18: VERIFIER.md instead of VERIFIER_REPORT.md; the note's ledger not recomputed by a fresh verifier | Lead's reading: VERIFIER.md is the verifier's report (decision 0012 names the documents a session can write; the verifier states this in its section 3). The ledger was not recomputed by a fresh verifier; asked of the orchestrator |
