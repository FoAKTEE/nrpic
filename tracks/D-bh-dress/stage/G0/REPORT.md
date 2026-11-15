# G0 scoping package of D-bh-dress (S4: black-hole growth and dark-matter dress)

Date 2026-11-15, lead session of wave 1, branch `track/D-bh-dress`. Units G = c = 1, M the
initial black-hole mass, eps = H_i M. Labels: [VERIFIED] (source with locator, or run id),
[BACKGROUND], [JUDGEMENT], [TO VERIFY]. Detailed material: `../../scope/SCOPE.md`
(helper, reviewed by the lead) and `../../scope/REFERENCES.md`; artefacts:
`EVIDENCE.md`; what the gate still lacks: `OPEN.md`; checklist: `CHECKLIST.md`
(`nrpic-stage collect`). Decision 0010 applies throughout: every simulation runs in this
repository's AthenaK; outside `athenak/src/` Track D keeps only exact and semi-analytic
references, analysis and notes.

## 1. Problem statement

Brief S4 (lines 394-405), sheet 9.7 (766-783), criteria N1, N4, K1, K3 (line 304).

1. Growth law: how does a black hole grow by accreting collisionless matter in a
   matter-dominated (Einstein-de Sitter) background? Observable: apparent-horizon mass
   M_AH against the scale factor measured by distant dust (areal radius against particle
   proper time) and against the matter that crossed the horizon.
2. Spike: the density of the bound, non-captured matter in the strong field (r < 10-50 M),
   where the probe-limit results (arXiv:1305.2619, 1707.06302) and the Newtonian
   self-similar dress (1901.08528, 2106.07480) stop applying.
3. Null test of "cosmological coupling": does the horizon mass of an ordinary (vacuum,
   puncture) black hole change with a beyond accretion? Worded in SCOPE.md section 3:
   k_eff = Delta ln(M_AH - Delta M_in) / Delta ln a with two definitions of Delta M_in.
   An upper limit shows that the method creates no spurious coupling and that a vacuum
   hole behaves as Birkhoff and the exact solutions require. It shows nothing about
   non-vacuum interiors (the object of the claim), the averaging argument, or observed
   black holes. [VERIFIED] the claim's own paper assigns k = 0 to Kerr (arXiv:2302.07878
   `paper_couple_rev.tex:132`, re-read by the lead), so a null result for a puncture does
   not test the observational claim.
4. Later (after G3, with F): dressed binaries; initial data for dressed holes.

Novelty [JUDGEMENT]: dress calculations read so far are Newtonian N-body or
semi-analytic (1901.08528, 1805.09034 GADGET), full-NR growth calculations use fluids or
scalar fields (2608.13206, 2109.04896); a 3+1 run with collisionless particles and a hole
in an expanding medium was not found (brief line 235 stays [TO VERIFY] until kb searches).

Regime finding that shapes the plan [JUDGEMENT, from computed numbers]: at affordable eps
(0.01-0.03) the turnaround radius after one doubling of a is 16-33 M (scoping run
D-bh-dress-20261115-120304-795eee9), and every particle with L < 4 M_bh is captured
(1305.2619 `SFWpaper.tex:118-121`, re-read by the lead). Cold dust (L = 0) therefore
forms no dress in full relativity: cold runs measure the growth law; a surviving dress
needs tangential speeds of 0.1-0.2 c at turnaround (warm-dust shells: 74 per cent still
captured at sigma_i = 0.2, run D-bh-dress-20261115-125613-248fdaf).

## 2. Parameter ranges

| Parameter | G2 | G3 scan | Source |
|---|---|---|---|
| eps = H_i M | 0.03 (matter); 0.0056 (Einstein-Straus data set, R_w = 40 M) | 0.003-0.1 | cost; 2109.04896 `:58`, `:99` (H M ~ 1e-2 for a hole formed in a matter era) |
| a_f/a_i | 2 | 4 (8 only at eps = 0.1) | cost, section 7 |
| dx at the puncture | M/8, M/16 | M/16, M/32 (M/64 check) | D-pre-4 floor |
| dx over the dust | 2 M (1 M check) | 1-2 M | core test 2 (`core/id-extrinsic` 1311b8e): areal-radius error 3.3e-3, 1.1e-3, 4.6e-4 at dx = 1, 1/2, 1/4 M |
| Dust region | Einstein-Straus shell to 60 M (vacuum bubble); filled from 3 M (matter) | turnaround ball R_ball(T) = 1.2 r_i(M_ta - M) a_f | Birkhoff; `secondary_infall/RUNS.md` section 2 |
| Particles | 1e5-7e5 (hp = 1-2 M) | up to 4e6 | memory and cost; relaxation control N vs 4N |
| Velocity dispersion | 0 | 0.03-0.2 (spike) | capture cone, section 1 |
| Spin a/M | 0 | 0.5, 0.9 | 1707.06302 |
| Lapse | to be set with core (risk R2) | | core `JOURNAL-id.md` entry 8 |
| Finder | `fastflow/metric_drvts = interpolant`, production settings of D-pre-4 | same | default on main is the defective one (`athenak/src/z4c/fastflow.cpp:89`) |
| Removal | `particles/ah_exc_factor = 0.8` | same | off by default (`athenak/src/particles/nrpic.cpp:118`) |

Closed-form scales [VERIFIED, run D-bh-dress-20261115-120304-795eee9 and the lead's own
code, run D-bh-dress-20261115-145610-5259f48]: M_ta/M = 1.525, 2.628, 4.871 at
a/a_i = 2, 4, 8 for every eps; mass that has reached the centre 1.190, 1.828, 3.215 M;
coefficient (M_ta - M)/(M a/a_i) 0.263 at a/a_i = 2, 0.558 at 100, limit
(4/(3 pi))^(2/3) = 0.5648; r_ta(a/a_i = 2) = 33.4 M (eps 0.01), 16.1 M (eps 0.03).

## 3. Exit criteria

- G0: this package, reviewed by the orchestrator; the items of `OPEN.md` closed.
- G1 (sheet line 779), as measured now (`../G1/STATUS.md`): D-pre-1 derivation re-derived
  symbolically, data constraint-checked at fourth order offline and inside AthenaK at
  t = 0 (met); D-pre-2 Schwarzschild spike reproduced to 1 per cent of FdRW and stationary
  in AthenaK (met), Kerr (open); D-pre-3 self-similar profile, growth curves and run
  parameters (met semi-analytically), reproduction in AthenaK's Newtonian mode once
  `core/newton` is on main (open); D-pre-4 noise floor at M/8 and M/16 (met).
- G2: (a) Einstein-Straus run: |M_AH(t)/M_AH(t0) - 1| over 50 <= t <= 200 M not above
  the floor of a matched vacuum control (same table without dust, same mesh and gauge) at
  M/8 and M/16, converging; wall tracers on the exact R(tau) to 3e-3 (dx = 1 M) and 1e-3
  (dx = 1/2 M); no dust particle inside the bubble; the two inner tracer groups removed
  after their exact arrival at R = 2M (dust proper time 15.0 M and 34.6 M, run
  D-bh-dress-20261115-145950-23fa1c7). (b) With matter (cold dust from 3 M, eps = 0.03,
  a x 2-4): M_AH(t) - M_AH(t0) equal to the accreted energy within max(3 floor, 1 per
  cent), both definitions; rest-mass bookkeeping to 1e-12; hole mass against the exact
  LTB reference (`secondary_infall/RUNS.md` section 1, with the over-massive hole of
  JOURNAL.md L5). (c) Relaxation control: capture rate unchanged between N and 4N.
- G3: three-resolution convergence of the growth law and of the spike profile (warm dust,
  spin); the null-test upper limit k_95 with the wording of SCOPE.md 3.6.

## 4. Test plan against brief section 10

Rows Track D holds:

| Row (brief line) | Test | Reference | State |
|---|---|---|---|
| Self-similar secondary infall (854) | (i) semi-analytic self-similar solution and shell calculations (`secondary_infall/`); (ii) AthenaK Newtonian mode with a point-mass seed: slope -9/4 +- 0.05 on [2 dx, r_ta/2] once a/a_i >= 30 (eps = 0.1); (iii) low-eps full-NR run against the LTB reference | own fixed point (run D-bh-dress-20261115-123813-97afeea: slope of m 0.741 on [1e-4, 1e-3] r_ta, outermost caustic 0.355 r_ta); printed numbers of 1901.08528 and 2106.07480 (run D-bh-dress-20261115-122051-bf0d6b1); Bertschinger 1985 [TO VERIFY, not on arXiv] | (i) done; (ii) waits for `core/newton` on main; (iii) waits for format 2 and a lapse condition |
| Black hole in a vacuum bubble (855) | D-pre-1 data set evolved in AthenaK, with a matched vacuum control | exact: mass inside the comoving wall constant (LTB; `einstein_straus/DERIVATION.md` section 6; 48 symbolic identities, runs D-bh-dress-20261115-042626-f3da881 and lead rerun -065141-5fdc744); Birkhoff inside | data and t = 0 check done; evolution waits for the merge |

Rows Track D depends on: geodesics on a fixed background (840, CORE; D-pre-2 used it:
|dE/E| at most 1.3e-6, |dL/L| at most 1.9e-10 over 20000 M, run
D-bh-dress-20261115-123755-25227d4); Oppenheimer-Snyder and its time reverse (841,
CORE/A: expanding-ball data and gauge, core test 2); LTB (850, A: the bubble's dust
shell is marginally bound LTB); Einstein-Vlasov steady states (843: long-time fidelity,
relaxation of a dress); FLRW and linear growth (845-846, B: the periodic version).

## 5. Key references verified at the source (`kb-data/raw/arxiv`)

The 18 sources with locators: `scope/REFERENCES.md`. Re-read by the lead in this session:

| Statement | Locator | Use |
|---|---|---|
| k = 0 expected for Kerr; k = 3 for vacuum-energy interiors | 2302.07878 v1 `paper_couple_rev.tex:132` | wording of the null test |
| L = 4Gm is the unstable circular orbit for E = 1; the spike vanishes at 4 Gm | 1305.2619 v1 `SFWpaper.tex:118-121` | regime argument; D-pre-2 |
| GS spike "a factor of three smaller at its peak"; the 8Gm -> 4Gm sentence | 1305.2619 `SFWpaper.tex:443` | the curves give 2.59 and 9.2 per cent (runs D-bh-dress-20261115-123029-4df1e76, -145636-5259f48) |
| SFW eq. (3.19) misses r^2/Delta = 1/(1 - 2Gm/r) | 1707.06302 v2 `kerrdm.tex:918-919` | D-pre-2 uses the canonical action |
| r^(-9/4) from spherical collapse in EdS, citing Fillmore-Goldreich 1984 and Bertschinger 1985 | 1901.08528 v2 `PBH-UCMH-ArXiv-v2.tex:235` | D-pre-3 |
| Halo profile "first determined analytically" by Bertschinger as a power law (3/2 there) | 1805.09034 v3 `main.tex:195` | attribution conflict, kb request |
| McVittie apparent horizon 1 - 2m/R = H^2 R^2: d ln M_AH / d ln a = -12 (mH)^2 in EdS | derived from 2308.07374 v2 `:322-326` by the scope helper, re-derived by the lead (JOURNAL.md L6) | definitional drift of the area mass in a non-vacuum neighbourhood; absent inside the vacuum bubble |

Brief statements found wrong or imprecise (outbox to orch): the Kerr spike reference is
1707.06302, not 1305.2619 (sheet line 773); "public AthenaK" in D-pre-4 means this
repository's AthenaK; the 3/2 vs 9/4 attribution to the same 1985 paper; D-pre-2's profile
comes from action matching, geodesic integration is the stationarity check; item 2 of
`coord/notes/derivations_to_check.md` (bare puncture mass m_p = M/a, throat at the
bifurcation sphere, f(2M) = 0; `einstein_straus/DERIVATION.md` section 7).

## 6. Risks (full table: `../../RISKS.md`)

R1 the release card executable pushes massless tracers wrongly (run
D-bh-dress-20261115-143918-a5c125a): no particle push on cards is trusted until core
explains it. R2 no lapse condition yet for a puncture inside expanding dust (core
`JOURNAL-id.md` entry 8: 1+log and conformal-time lapse send fronts from a surface; along
the dust 1+log gives alpha = 1 + 6 ln a, about 4.9 at tau = 200 M). R3 the D-pre-4 floor
belongs to another configuration (asymptotically flat, boundary at 128 M): a matched
vacuum control is needed. R4 particle resolution and noise next to the puncture. R5
numerical relaxation of a dress. R6 the format-2 reader is only on `core/id-extrinsic`.
R7 outer boundary with K_ij ~ r^(-3/2) (Painleve-Gullstrand exterior). R8 over-claiming
the null result. R9 cost of large dust regions.

## 7. Compute estimate on this machine (two A100, one-hour jobs, chained)

Model of `scope/scoping_estimates.py` from measured throughput (vacuum puncture 9.27e6
zone-cycles/s, matter AMR run 6.4e6, particles 1.2e-7 s per particle-step; run
D-bh-dress-20261115-120304-795eee9), evaluated for the first runs in run
D-bh-dress-20261115-145950-23fa1c7. Used so far: 2.18 card-hours (D-pre-4) of 30.

| Item | Card-hours |
|---|---|
| D-pre-4 noise floor (done) | 2.18 |
| G2 (a) Einstein-Straus, outer dust edge 60 M, 200 M: M/8 / M/16 | 1.4 / 2.9 |
| G2 (a) matched vacuum controls, M/8 / M/16 [JUDGEMENT: the same without particles] | about 1.2 / 2.6 |
| boundary control for the D-pre-4 excursions (M/16, boundary 256 M, 500 M) | about 1.8 (helper's estimate) |
| G2 (b) matter, eps = 0.03, a x 4, M/16 + M/32 (SCOPE.md section 7) | 4.2 |
| G2 (c) relaxation control, 4N | 2.3 |
| Total to G2 | about 19 of 30, model uncertainty a factor 1.5 |

The Einstein-Straus data set as generated (dust to 106 M) would cost 11.3 card-hours at
M/16 for 200 M; it is to be regenerated with the outer dust edge at 60 M
(`make_es.py --Rb 56 --w_out 4`) before the first run.

## 8. Stage timeline [JUDGEMENT]

G0: this package. G1: complete when the Kerr spike baseline and the Newtonian-mode run
exist (the latter needs `core/newton` on main) and a fresh verifier has checked the
packages. G2: starts with the merge of `core/id-extrinsic`, an explanation of R1 and a
lapse condition from core; about 19 card-hours. G3: warm dust, spin, three resolutions.
