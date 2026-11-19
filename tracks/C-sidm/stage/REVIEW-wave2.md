# C-sidm lead review of wave 2 (and wave 2b)

Sections 1-5: lead session of 2026-11-15 (cut off by the account's usage limit after writing
them; its stage files were committed unchanged in wave 2b, commit 0559b367). Sections 6-8:
lead session of wave 2b, 2026-11-19 (box_rerun helper; the cluster runs; the wave-3a heat
package). Runs of the wave-2b review (processors, 0 card-hours): C-20261119-151502-cb831a8
(L13-L15, `review_wave2/run_review2b.sh`, 4 min on 2 cores) and C-20261119-151944-08f3220
(L16, `review_wave2/rv_cc_onset.py`, 10 s). Predictions L13-L16 in `../JOURNAL.md` before
the runs; outcomes there, failed clauses included.

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

## 6. box_rerun (wave 2b): core/collisions-2 with `coll_energy = particle`

Checked from the registered outputs with the lead's own readers (`review_wave2/rv_box2b.py`;
for T2 the lead's wave-2 function `rv_box.t2` pointed at the new runs), not from the helper's
scripts or JSON (run C-20261119-151502-cb831a8, figure `rv_box2b.png` looked at). Prediction
L13 held in every clause.

Confirmed:
- R1 (option absent, new executable, run C-20261119-141502-95f0200): 36 of 36 output files
  of the six T0b cases byte-identical to the release run C-20261115-170155-13ff01f.
- R2 (option present, run C-20261119-141711-7db7a6a): n_tested, n_coll, n_updated,
  max_nsub, n_trunc equal to R1 in all 25 records of all six cases; sum_P within 2.2e-16;
  n_noroot = n_balance = 0, max_dlam = 0; dumps of version 2 (NRPCOLD2). The helper's replay
  (6/6) was not rerun; the record-level identity with R1 is my independent part.
- R3 (run C-20261119-141806-af19c1c): integer columns identical to the release run
  C-20261115-165500-c67e036 in all 3200 steps; my T2(b) ratio 0.999906-1.000096 (z_b
  -2.20..+2.92), within 4.4e-16 of my recheck of the release; T1 at 1.05e-7 of the bound;
  n_trunc = n_noroot = n_balance = 0.
- R4 (run C-20261119-143041-f94e350): final particle records of 8 and 64 MeshBlocks and of
  the three restarts byte-identical to one MeshBlock; seed 8 differs in every particle;
  385554 collisions, as the release.
- R5, T12 (runs C-20261119-143049-0cf699a, C-20261119-145925-dbcfb9c): n_tested and n_coll
  of each curved run and its flat twin identical in all 200 steps of all four pairs, so the
  rate per coordinate time and volume is alpha0 psi0^6 = 1.4172488 times the twin's exactly;
  my analytic expectation (1/2) N^2 M sigma <v_Mol>(theta) alpha0 dt / psi0^6, theta from
  <W - 1> of u/psi0^2 of the first snapshot, gives 1.0000896, 0.9999717, 1.0000718,
  1.0000525 (|z| <= 2.35), equal to the helper's to 1e-6. [JUDGEMENT] The twin comparison is
  the sharp form of the T12 criterion (helper's suggestion): adopted as a note in TESTS.md
  section 2a below.
- R6, King threshold model (run C-20261119-141431-a351ac7), from coll.hst alone: particle mode
  changes the canonical energy by +1.73 to +1.99e-21 of sum M H_p per collision (all Kn, both
  steps: the systematic rounding residual the helper reports); cell mode at Kn = 0.01, both
  steps pooled, +9.1e-11 of sum M W_p per collision (helper, step 1 from cell sums:
  +8.0(3.4)e-11); columns 1-29 of the cell-mode Kn = 1 record identical to the release smoke
  run, columns 30-31 differ by 1.7e-14 and 1.3e-15 (summation order, as the helper found).
- Cost (run C-20261119-143146-226b0e0): collision part per tested pair, particle over cell,
  1.676 (1.57-1.81 over the repeat combinations).
- Figures of the helper looked at: t12_c2, king_defect_c2, paired_c2particle,
  compare_modes_c2, t10_repro_c2particle; consistent with the numbers. Cosmetic: in
  t10_repro_c2particle mb8 and rst2 share a colour; CC labels overlap in my rv_king_onset.

Not confirmed: the helper's cell-sum standard errors of R6 (I used the record sums; my
pooled values agree with its central values within its errors); the helper's replay R2 and
the flat-metric check of the version-2 dumps (not rerun); the T12 position bookkeeping
(whole-period differences before the modulo, not investigated by either of us).

Wrong: nothing. The helper's failed prediction clauses (R3(iv) positions 200 ulp, R3(v')
cost 1.68 > 1.5, R6(a) column 30) are on record in its journal and are not defects. The
failed first R2 attempt C-20261119-141614-e42b5ec has a manifest saying "completed" because
its driver exited 0 although all six AthenaK runs exited 1: kept as it is (the journal says
so); the T12 run C-20261119-143049-0cf699a is on record as failed (figure crash after the
JSON), its numbers come from C-20261119-145925-dbcfb9c.

Open (from the helper): the cell-mode defect of the King model is 0.46 of the pair-model
prediction (z = -2.8; the card runs gave 0.70); not explained, and no longer relevant to
production runs once `coll_energy = particle` is used. Card runs with collisions-2: none
(see `G1/OPEN.md` item 7). T3-T5, T9, T11 not repeated with the option; T12 with a modulated
metric not run; MPI variant of T10 not run.

Fixed here: `collide/TESTS.md` section 2a gets the T12 twin clarification (below).

## 7. The first collisional cluster runs: what can and cannot be concluded

Runs (wave 2, release core-v0.3, cell-mode pair energy): card jobs C-20261115-171058-c26cfad,
C-20261115-171059-4b70228, C-20261115-171059-35441e3 (CC1 = King y0 = 0.334032, the
collisionless threshold; CC2 = King y0 = 0.314, collisionless-stable; Kn = inf, 10, 1;
N = 1e5, one seed, static mesh with M/4 cells over the cluster, 300 M). Rechecks L10 (wave 2),
L14, L16 and the reference L15 (this session); figures `rv_cc.png`, `rv_cc_onset.png`,
`rv_king_onset.png` (runs C-20261119-151502-cb831a8, C-20261119-151944-08f3220), looked at.

Established [VERIFIED, from these runs]:
1. All four collisional runs reach alpha_min < 0.3 (72.5, 77.75, 184.25, 206.75 M for
   cc1_kn1, cc2_kn1, cc1_kn10, cc2_kn10); the controls keep every particle for 300 M but
   drift outward (alpha_c +0.033 for CC1, +0.018 for CC2 by about 200 M).
2. Relative to its control, the central lapse of each collisional run falls steadily from
   the start: by 0.01 at 44-46 M (Kn = 10, after 0.35 collisions per particle) and 20-21 M
   (Kn = 1, 1.6 collisions per particle) (L16).
3. The energy injected by the release operator's defect (sum of dE_particles) is 0.013-0.016
   of the binding margin E_b(CC1) - E_b(CC2) = 1.0e-4 M0 at that time (Kn = 10; 0.11-0.12 at
   Kn = 1) and reaches the margin only at 180 and 202 M (Kn = 10), 54 and 59 M (Kn = 1): it
   grows 8-18 times per collision while the core deepens. Before alpha_min < 0.3 it totals
   1.9 and 2.3 margins at Kn = 10, 17-19 at Kn = 1 (L14).
4. Neither a fixed number of collisions per particle (13.4 and 15.3 against 2.5 and 2.9, ratio
   5.3-5.4) nor a fixed injected energy (ratio 8-9) nor a fixed time (ratio 0.38-0.39) marks
   the collapse.
5. Reference (L15, `tmb` at b = 1, checked against the King JSON to 3e-10): the radial-
   pulsation onset with the Juttner Gamma_1 (the track's Kn -> 0 anchor) lies at y0 = 0.32143
   (alpha_c = 0.6707), between CC2 (0.314, alpha_c = 0.6762) and CC1 (0.334, alpha_c =
   0.6614); with F21's gamma = 1 + p/u at y0 = 0.37206; the collisionless binding-energy
   maximum at 0.33403. So CC1 is fluid-unstable and collisionless-marginal; CC2 is stable at
   both ends of Kn by the linear criteria, 0.0055 in alpha_c from the fluid onset.

What can be concluded:
- The defect of the release operator does not start the contraction (item 3); it may
  accelerate the late phase, where it becomes comparable to the margin [JUDGEMENT].
- For CC1 a collapse with collisions is the physically expected outcome (beyond the fluid
  onset) [JUDGEMENT on applying the linear criterion at finite Kn].
- Leading hypothesis for both [JUDGEMENT, not tested]: collisions carry heat out of the King
  core (its velocity dispersion falls outward), the core contracts (gravothermal), and a
  model within 0.006-0.015 in alpha_c of the onsets crosses the relativistic threshold after a
  small contraction. The per-collision efficiency being lower at Kn = 1 than at Kn = 10
  (item 4) fits the suppression of conduction as the mean free path approaches the core
  size, but is not a test.

What cannot be concluded:
- That CC2's collapse is physical, or the threshold_scan reading "the collisional threshold
  lies below y0 = 0.314": the controls' numerical drift (0.018-0.033 in alpha_c) is larger
  than CC2's distance from the fluid onset (0.0055) and than the CC1-CC2 separation (0.0148),
  so this mesh does not hold the equilibrium to the precision of the stability margin.
- Anything from a single seed: card runs are not byte-reproducible, and the scatter of the
  collapse time between seeds is unmeasured.
- Collapsed masses: the excised fractions are proxies; the static M/4 mesh cannot hold the
  black hole (non-finite state after the collapse, exit status 0).
- The earlier statement "the positive energy defect heats the cluster and is not the collapse
  trigger" (threshold_scan) is now supported for the trigger (item 3) but was not then.

Runs that decide (all scouting, N = 1e5, the same particle files, 300 M; about 0.3 card-hours
each at 3.45 s per M, M/4 runs):
- D1, the defect: cc1_kn10 and cc2_kn10 with `coll_energy = particle` (collisions-2 card
  executable, once core states its card tests usable), seeds 1 and 2, plus cc2_kn10 in cell
  mode with seed 2 for the seed scatter (5 runs, about 1.5 card-hours). Prediction to write
  before: the relative lapse drop of the first 100 M unchanged within the seed scatter; a
  collapse-time shift of CC2 beyond the scatter would make the defect a cause of the late
  phase.
- D2, the mesh: cc2_kninf and cc2_kn10 (particle mode) with one more refinement level
  (M/8 finest cells) and `coll_cell_factor = 2`, so that the collision cells and their
  statistics stay those of D1 while gravity is resolved twice as finely (2 runs; cost to
  measure, estimated 4-8 times per M, so 2-5 card-hours [JUDGEMENT]). Decides whether the
  controls' drift is numerical (it should fall by about four if second order) and whether
  CC2 still collapses.
- D3, the physics: a King model on the stable side of the fluid onset by more than the
  controls' drift (y0 = 0.25-0.28; new particle files with the existing generator) at Kn = 10
  and 1 in particle mode with its control (3 runs, about 0.9 card-hours). Under the
  gravothermal hypothesis it contracts relative to its control at a rate comparable to CC2's
  and collapses later in proportion to its distance from the onset; no relative contraction
  would refute the hypothesis.
- Order: D1 first (cheapest; also gives the seed scatter every later comparison needs), then
  D2 and D3. About 4-8 card-hours of the 41.4 left toward G2. Pending conditions: core's
  statement on the collisions-2 card executable (outbox 20261119T151725Z), and the owner's
  limit of two queued card jobs (the heat helper holds both slots on 2026-11-19).

## 8. heat (wave-3a helper, same worktree): not reviewed

The heat-conduction package `heat/` (T6-T8) belongs to the second workflow of 2026-11-19
(`coord/digests/wave-3a-plan.md`); it was running while this review was written (five
processor runs, two queued card jobs) and commits its own files. Not reviewed here; its
outcome decides G1 criterion C6 and goes to the next lead.
