# Verification ladder of core (C3), re-verified on the current source

The rows of brief section 10 marked CORE (coord/CHARTER.md, section 10), each with the
existing evidence, the measured numbers and the criterion of the core sheet (C3 of
brief section 9.3: "order and conserved quantities of geodesics on a fixed Kerr
background; Oppenheimer-Snyder collapse with a horizon-mass error of the same order as
in the paper; prolate collapse; stability of relativistic clusters").

Sources of numbers. "Paper" is Wu & Most, arXiv:2611.12831, read in
`refs/arxiv_2611.12831/src/main.tex` (untracked, line numbers given). "Earlier" numbers
come from `docs/TESTLOG.md` (line numbers), the tables
`paper/sections/tables/tab_outcomes.tex` and `tab_setups.tex`, and the run directories
under `/data/haiyangw/nrpic/runs/` (untracked). The self-gravitating numbers below were
re-read from the run files by `ladder_measure.py` (analysis run
`core-20261115-032826-45e1779`, output `scratch/core/core-20261115-032826-45e1779/
ladder_numbers.json`, figure `figs/ladder_overview_core-20261115-032826-45e1779.png`,
inspected); every number they share with the tables agrees with the tables to the
printed digits. "Regression" means a rerun today with the release executables
(`regress/`, run ids below; verdicts in `JOURNAL.md`).

Verdict labels: PASS (criterion met, evidence named), PARTIAL (part met, the rest open
and named), OPEN (not done).

## Summary

| Row of section 10 | Core-sheet criterion | Verdict | Re-run today |
|---|---|---|---|
| 1. Geodesics on a fixed background | order and conserved quantities on fixed Kerr | PASS | G: `core-20261115-032625-45e1779`, 104 of 104 checks |
| 2. Oppenheimer-Snyder collapse (CORE part) | horizon-mass error of the order of the paper's | PASS at 9328 lattice particles; random samples at 10^4 larger (0.3 to 0.5 percent) | O: `core-20261115-032614-45e1779`, 13 of 13 checks |
| 3. Oblate and prolate collapse (CORE part) | prolate collapse | PARTIAL: horizon at the paper's time at two resolutions (32.00 M at M/16, 32.25 M at M/8); mass deficit 3.3 and 4.3 percent, falling with resolution; oblate blocked (needs an oblate component in `nrpic_cf`) | wave 2: `core-20261115-152845-5728b1d` (M/8), comparison `-162509-c691fb8` |
| 4. Einstein-Vlasov steady states and stability threshold (CORE part) | stability of relativistic clusters | PARTIAL: fates of the five models as in the paper; wave-2 bisection at M/4: no collapse, the fixed rule gives no bracket; members below the turning point y_c* = 0.6796 migrate to their equal-binding partner, those above stay (threshold between 0.66 and 0.70 on that reading); growing oscillation unexplained; round 2 and control pending | wave 2: `core-20261115-152842-5728b1d`, `-152843-5728b1d`, analysis `-160501-ee15e0f` |

## Row 1. Geodesics on a fixed background

What it checks: order and conservation of the pusher. Reference named in section 10:
arXiv:1801.02378, arXiv:1710.09164 (not used for a comparison so far [TO VERIFY]); the
comparison made is with the paper's Kerr test.

Evidence.
- `docs/TESTLOG.md` lines 6-21 (kernels, standalone build) and 23-28 (mesh path);
  `docs/results_geodesic.md` sections C (passage), D (processor against card), E (mesh);
  `problems/kerr/results/kerr_summary.json`; table tab:outcomes (rows "Fixed black hole");
  runs `runs/geodesic/kerr_passage/`, `kerr_passage_cpu/`, `kerr_bl/`, `kerr_mesh/`.
- Regression G today (processor release executable, 11 runs):
  `core-20261115-032625-45e1779`, figure `figs/regress_geodesic_core-20261115-032625-45e1779.png`
  (inspected).

Numbers (Kerr a = 0.9 M, e = 0.99 Kerr-Schild passage, dt = 0.01 M to 230 M, largest
relative errors of E, L_z, Q):

| Pusher, metric | Paper (main.tex 824-833) | Earlier | Regression G today |
|---|---|---|---|
| midpoint, analytic | 2.8e-8, round-off, 1.3e-7 | 2.781e-8, 0, 1.254e-7 | 2.781e-8, 0, 1.254e-7 |
| Boris symmetric, analytic | 9.0e-8, 1.1e-8, 7.8e-7 | 9.046e-8, 1.136e-8, 7.825e-7 | 9.046e-8, 1.136e-8, 7.825e-7 |
| midpoint, Hermite lattice | 2.2e-6, 5.3e-6, 5.1e-5 | 2.162e-6, 5.304e-6, 5.060e-5 | 2.162e-6, 5.304e-6, 5.060e-5 |
| Boris Cholesky, Hermite lattice | 2.0e-6, 3.8e-6, 5.3e-5 | 2.046e-6, 3.788e-6, 5.289e-5 | 2.046e-6, 3.788e-6, 5.289e-5 |

- Order in dt of the final position error, analytic metric, pairwise between 0.005,
  0.01, 0.02 M: 2.0001 and 2.0003 (midpoint), 1.9998 and 1.9991 (Boris symmetric),
  1.9997 and 1.9989 (Boris Cholesky), equal to the earlier values to 6e-7. Paper: "Both
  methods are second-order accurate" (main.tex line 837).
- Pericentre 1.898325 M at 98.95 M against the exact 1.898327 M at 98.948 M
  (`docs/TESTLOG.md` line 20); regression equal to the earlier value to 1e-11.
- The two passage runs that exist from the earlier processor build are reproduced
  bitwise (largest difference of position and momentum 0).
- On the mesh (not in the regression): circular orbit at 8 M in a 96^3 Kerr-Schild
  mesh, r within [8.0000, 8.0012] M over 300 M (`docs/TESTLOG.md` line 26); inclined Kerr
  orbit on the mesh, order in h of the position and E errors 2.89 and 3.29 (table
  tab:outcomes).

Verdict: PASS [VERIFIED by regression G]. Open: comparison with the integrators of
arXiv:1801.02378 and arXiv:1710.09164 named in section 10.

## Row 2. Oppenheimer-Snyder collapse

What it checks: horizon formation (the time reverse, expanding-ball data, belongs to
Track A). Criterion: horizon-mass error of the order of the paper's. Paper: "relative
error of Delta M/M_ADM <~ 10^-3" (main.tex line 945); RMS over five seeds at t = 60 M,
Monte Carlo sampling, 1.25e5, 1e6, 8e6 particles: 2.061e-3, 9.362e-4, 7.347e-4 (main.tex
line 1484; table at lines 1425-1435).

Evidence.
- `docs/TESTLOG.md` lines 600-633 (the published lattice rule carries 1.2 percent too
  much mass at 10^4 particles; surface correction), 660-688 (finder against slice mass),
  718-763 and 849-937 (deposition rules); table tab:outcomes_dust; runs
  `runs/os/nocap_sc` (corrected masses, cloud at the finest level, the reference),
  `runs/os/nocap_v4` (published lattice rule), `runs/os/adapt_*`, `runs/os/mc_*`.
- Re-read today (`ladder_numbers.json`): first apparent horizon 16.3894 M, mass
  1.000353; largest |M_AH/M - 1| from formation to 60 M 1.34e-3; 1.000093 at 20 M,
  0.998762 at 40 M, 0.998670 at 60 M; all 9328 particles removed by 19.74 M.
- Regression O today (card release executable, initial data regenerated bitwise
  identical, to 25 M): `core-20261115-032614-45e1779`, 13 of 13 checks; first horizon
  16.3894 M, mass 1.000352575670864 (earlier ...862); central lapse equal to the earlier
  run to 2.4e-15 before the horizon; largest |M_AH/M - 1| to 25 M 6.3e-4; deposition
  identity 1.0e-15; figure `figs/regress_os_core-20261115-032614-45e1779.png` (inspected).

| Quantity | Paper | Earlier (`runs/os/nocap_sc`) |
|---|---|---|
| central proper time at which the central lapse leaves the lapse bound by 1e-2 | tau_c about 3.5 M (main.tex lines 926, 943) | 3.53 M |
| first apparent horizon | not given in text | 16.39 M |
| M_AH/M at formation; largest deviation 16-60 M; at 60 M | <~ 1e-3 (fiducial, 60 M) | 1.0004; 1.34e-3; 0.9987 |
| same with the published lattice mass rule (`runs/os/nocap_v4`) | | 1.0114; 1.19e-2; 1.0099 (the particles carry 1.18 percent more mass than the initial metric) |
| Monte Carlo sample of 9328 particles, M_AH/M over the last 2 M (table tab:outcomes_dust) | 0.997943 +- 0.000140 at N = 1.25e5 (A1) | 1.0000, 1.0013 (capped clouds, to 41-43 M); 0.9973, 0.9946 (one level fewer, to 60 M) |

Verdict: PASS for the lattice at 9328 particles with consistent masses: the error at
formation (3.5e-4) and its largest value to 60 M (1.3e-3) are of the order of the
paper's 1e-3 at 107 times fewer particles (the paper's fiducial lattice: n_lat = 124,
998,592 particles, main.tex line 917) [VERIFIED, run files]. The random samples at
this particle number reach 0.3 to 0.5 percent at 60 M, larger than the paper's 2e-3 at
1.25e5 particles; consistent with the paper's trend in N (main.tex 1484) but the trend
is not measured here [JUDGEMENT]. Open: a particle-number sequence with five seeds as in
the paper's appendix (main.tex 1413-1435) is not done.

## Row 3. Oblate and prolate collapse

What it checks: three-dimensional caustics and horizons. Criterion of the core sheet:
"prolate collapse" (no number). Paper: focusing at 20.5 M, spindle at 27.75 M, apparent
horizon detected at 32 M (main.tex line 971); first-horizon detection times vary by less
than 0.1 M across resolutions M/32 to M/128 and 5e5 to 8e6 particles (line 975); no
number for the horizon mass of this test appears in the prolate section (lines 955-992)
[VERIFIED by reading]. Correction to `docs/TESTLOG.md` lines 1541-1542, which attribute
"agreement of the horizon mass with the initial mass to 1e-3 for this test" to the
paper: that statement is about the dust collapse (main.tex 945, 1371-1373).

Evidence: `docs/TESTLOG.md` lines 1149-1170, 1329-1345, 1527-1616; table
tab:outcomes_prolate; run `runs/prolate/e09_v8` (10^4 Monte Carlo particles, finest
cells M/16, four filter passes with compensation; the paper uses 2e6 particles and
cells down to M/64, main.tex lines 967 and 969).

| Quantity | Paper | Earlier (`runs/prolate/e09_v8`, re-read today) |
|---|---|---|
| first apparent horizon | 32 M | 32.00 M (searches every 0.25 M), M_AH 0.929 |
| largest Kretschmann scalar | spindle at 27.75 M, maxima near the ends | 27.75 M, on the axis at abs(z) = 0.66 M |
| largest M_AH; at the last search | -- | 0.9666 (33.75 M); 0.9489 (44.75 M), falling 0.0016 per M |
| slice Misner-Sharp mass at the horizon; at large radius (45 M) | -- | 0.920 +- 0.027; 0.999 |
| macroparticles removed | -- | all 10^4, between 33.78 and 38.80 M |

Verdict: PARTIAL. The horizon forms at the paper's time; its mass is 3 to 5 percent
below M and still falling at the end, with the missing mass outside the horizon as
field content (`docs/TESTLOG.md` lines 1580-1593); only one resolution and one particle
number, so neither the paper's 0.1 M robustness of the formation time nor the source of
the deficit is tested. Oblate collapse: not done (shared with Track A).

### Row 3, wave 2: second resolution on release core-v0.3 (`verify/JOURNAL.md` 15:30Z, 16:28Z)

Same particles and input as `e09_v8` with one level fewer (finest cells M/8), card
release executable: run core-20261115-152845-5728b1d (0.344 card-hours); comparison
core-20261115-162509-c691fb8; figures `figs/prolate_resolution.png`,
`figs/prolate_mosaic.png` (energy density at y = 0, t = 27.75 M, four nested windows
+-10, 4, 1.5, 0.6 M, both resolutions).

| quantity | M/16 (e09_v8) | M/8 |
|---|---|---|
| first apparent horizon | 32.00 M (searches every 0.25 M) | 32.25 M (every 0.5 M) |
| M_AH: first, largest, at 44.75 M | 0.9291, 0.9666, 0.9489 | 0.9249, 0.9570, 0.9444 |
| largest Kretschmann scalar 20-31 M | 1203 at 27.75 M, z = -0.66 M | 101 at 26.25 M, z = +0.81 M |
| largest sqrt(H-norm2) | 6.31 (27.5 M) | 5.43 (32.0 M) |

Verdict: PARTIAL. The horizon forms at the paper's time (32 M, main.tex line 971) at
both resolutions, within one search interval; the peak curvature grows with resolution
(an unresolved caustic, as the paper says, line 975); the horizon-mass deficit falls
with resolution (4.3 to 3.3 per cent at its largest) but two resolutions give no order
and 3 per cent remains at M/16. Open: a third resolution (M/32 needs more than the 80 GB
of one card at 10^4 particles, `docs/TESTLOG.md` 1329-1345), a particle-number pair, the
oblate collapse (source work: README.md, request 2; reference potential
`oblate/oblate_reference.py`, run core-20261115-154359-d74357f).

## Row 4. Spherically symmetric Einstein-Vlasov steady states and stability threshold

What it checks: long-time phase-space fidelity; the stability threshold (shared with
Track C). Criterion of the core sheet: "stability of relativistic clusters". Paper:
monoenergetic models y_c = 0.900, 0.819 stable to 300 M; 0.605 and 0.500 collapse with
horizons at about 109 M and 73 M; 0.283 expands (main.tex lines 1017-1030 table
tab:st-suite, 1138, 1140); migration of the unperturbed y_c = 0.5 model to a late mean
central lapse 0.833530 (line 1199); 2e6 particles.

Evidence: `docs/TESTLOG.md` lines 72-80, 91-156, 225-281, 387-598, 765-848, 882-904,
939-957, 983-1059, 1095-1148, 1171-1242, 1284-1328, 1346-1370, 1461-1526; tables
tab:outcomes_clusters and tab:outcomes_migration; runs `runs/st/` (10^4 stratified
particles unless named).

| Quantity | Paper | Earlier (re-read today) |
|---|---|---|
| y_c = 0.900, one-percent inward kick: central lapse range over 300 M; particles kept | about 0.89 (figure) | 0.886-0.892; all (`st/yc0900_v4`) |
| y_c = 0.819, same | 0.81-0.82 (figure) | 0.787-0.819; all (`st/yc0819_v4`) |
| y_c = 0.605: first apparent horizon; M_AH/M at the end | 109 M; consistent with M | 191.0 M; 1.0000 (`st/yc0605_v5`) |
| y_c = 0.500: same | 73 M; consistent with M | 104.3 M; 1.0001 (`st/yc0500_v5`) |
| y_c = 0.283: central lapse at the end | approaches 1, expands | 0.976 at 270 M, all particles kept (`st/yc0283_v5`) |
| migration y_c = 0.5, unperturbed: late mean central lapse | 0.833530 (line 1199) | 0.814 over 1500-2500 M (`st/migration_yc0500_v4`) |
| near-critical y_c = 0.756, unperturbed, 800 M | -- | range 0.696-0.772, all kept (`st/yc0756_unpert`) |

Verdict: PARTIAL. The fate of every model of the sequence agrees with the paper (two
stable, two collapsing with M_AH = M to 1e-4, one expanding). Open: the collapse times
are 1.75 and 1.43 times the paper's (the paper calls its own collapse times dependent on
particle number and initial noise, line 1138; not tested here at 2e6 particles); the
migration target is 2.3 percent below the paper's; the threshold itself is bracketed
(stable at 0.756 unperturbed and above, collapsing at 0.605 kicked and below) but not
located as a number on the binding-energy curve; the stable y_c = 0.819 model shows a
growing central-lapse oscillation (half swing 0.005 to 0.018 between 100 and 500 M,
saturating at 0.015-0.022; table tab:outcomes_clusters) whose cause is not determined
(`docs/TESTLOG.md` lines 897-904).

### Row 4, wave 2: bisection on release core-v0.3 (`verify/JOURNAL.md`, 15:30Z onwards)

Protocol of the earlier sequence (`runs/st/yc0605_v5`: 10^4 stratified particles, seed
1, one-percent inward kick, equilibrium table, `st_cluster_amr.athinput`) with the mesh
capped at the initial nest (finest cells M/4, `mesh_refinement/num_levels=7`), to 300 M,
card release executable `.work/build_gpu_v03`. Turning point of the sequence (first
maximum of E_b/M_0, `python/nrpic/st_cluster.binding_energy_maximum`, recomputed in run
core-20261115-152805-47d8f25): y_c* = 0.6796, z_c = 0.4553, E_b/M_0 = 0.036058.
Analysis run core-20261115-160501-ee15e0f, figure `figs/cluster_threshold.png`.

| y_c | run | horizon | mean central lapse 200-300 M (alpha_c) | rule of 15:30Z | equal-binding target |
|---|---|---|---|---|---|
| 0.72 | core-20261115-152843-5728b1d | none | 0.7079 (0.7207) | STABLE | -- |
| 0.70 | core-20261115-152842-5728b1d | none | 0.6920 (0.7039) | STABLE | -- |
| 0.66 | core-20261115-152842-5728b1d | none | 0.7005 (0.6713) | STABLE (offset 0.029 of 0.03) | 0.7034 |
| 0.64 | core-20261115-152843-5728b1d | none | 0.7221 (0.6554) | UNDECIDED | 0.7205 |
| 0.69, 0.67 | job 4439, run core-20261115-154726-37450f2 | PENDING (queued) | | | |
| 0.605 control | job 4447, run core-20261115-155617-06f844b | PENDING (queued) | | | |

Verdict of the bisection: by the rule fixed before the runs it does NOT locate the
threshold (no model collapses at M/4; the prediction that 0.64 collapses is refuted).
Read after the runs [JUDGEMENT]: the members below y_c* migrate outward to the member of
equal binding fraction (within 0.003 and 0.002 in central lapse), those above stay, so
the stability threshold at this mesh and particle number lies between 0.66 and 0.70 and
brackets the turning point; the direction of departure (migration, not collapse, for a
one-percent inward kick) differs from the earlier finer-mesh run of 0.605, which the
pending control at M/4 tests. Unexplained: the central-lapse oscillation (period about
50 M) grows to +-0.05 to +-0.08 after 200 M in every run, stable ones included.
Row 4 stays PARTIAL.

## Supporting checks of the C2 steps (earlier, not re-run today)

| Step | Number | Source |
|---|---|---|
| deposition identity on refined meshes, flat space, 10^4 particles crossing three levels | mesh integrals equal particle sums to 16 printed digits (card), 4e-13 (processor) | `docs/TESTLOG.md` lines 30-36 |
| deposition identity in the dust collapse | 1.1e-15 throughout (also in regression O) | line 62; regression O |
| restart, asymptotically flat | positions to 9e-16, momenta 3e-16, history identical | lines 64-70 |
| restart, periodic | every compared quantity identical | `cosmo/TESTLOG.md` lines 847-862 |
| apparent-horizon finder (vacuum puncture, M/8) | corrected finder 1.0003; slice mass 1.0006 | table tab:outcomes, `docs/TESTLOG.md` lines 191-224, 310-386 |
| Kretschmann scalar (Brill-Lindquist) | 5e-3, 2e-4, 1e-5 relative in three radial bands | lines 38-42 |
