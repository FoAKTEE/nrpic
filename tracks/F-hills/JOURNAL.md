# JOURNAL of F-hills

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T14:55Z  session F-hills lead (wave 1, after the four helpers)  commits 1e2c30f..(this session)

Helpers' journals: `novelty/JOURNAL.md`, `newton3/JOURNAL.md`, `geodesic_binary/JOURNAL.md`,
`three_punctures/JOURNAL.md` (predictions and outcomes of their 60 registered runs).

### Predictions of the lead's checks (written before the runs)

- V1, rerun of newton3's unit tests (`newton3/scripts/run_tests.py`): all 10 pass, as in
  F-hills-20261115-133436-8bfc259. Refuted by any failure.
- V2, rerun of geodesic_binary T1-T4 (`geodesic_binary/tests/t{1,2,3,4}_*.py`): T1 metric
  identities <= 1e-15 and finite-difference derivatives <= 1e-9; T2 positions within 4e-8 r_g;
  T3 proper period within 2e-4 of the tide-corrected value for r_mid >= 13.4; T4 relative
  orbit within 5e-8 a0. Refuted by any number larger than these.
- V3, rerun of `novelty/scripts/scale_estimate.py`: bounds 4 q^(2/3) = 18.57, 86.18, 400.0;
  r_mb = 4.000000 M; Peters time 6328 GM/c^3 at a_b = 30 r_gb, q = 10. Refuted by any digit
  that differs.
- V4, independent restricted parabolic problem (my own code from SKR prp.tex:229-259 and the
  energy of prp.tex:350-357, SciPy DOP853, 600 phases, start 10 r_t, survival = bound with
  apocentre inside half the Hill radius at f = 0.98 pi): P_dis within 0.01 and the
  phase-averaged |E| within 2 percent of newton3's `coplanar.npz` (run
  F-hills-20261115-130237-cbfaf6b) at prograde D = 0.1, 0.5, 1.0, 1.5, 2.0 and retrograde
  D = 0.1, 0.2, 0.3, 0.38. Refuted by a larger difference at any D (the phase grids differ, so
  0.01 allows about six phase cells at each of two edges).
- V5, independent full Newtonian integration (my own code) of the start state in
  `three_punctures/inputs/hills_q10_m8.athinput` and `hills_q4_m8.athinput`: total momentum
  below 1e-9, barycentre at the origin within 1e-8; centre-of-mass orbit of the binary about
  M has pericentre 8.0 +- 0.1 (9.82 +- 0.1 for q = 4) and eccentricity 1.00 +- 0.01; outcome
  m1 ejected / m2 bound to M with E1 = +1.75 +- 0.05 and E2 = -1.84 +- 0.05 units
  (q = 4: +1.53, -1.63), closest approach of m2 to M 5.6 +- 0.2. Refuted otherwise.
- V6, geodesic baseline of the same two configurations (geodesic_binary `hrna.py`, hole fixed,
  members start at the NR positions relative to M with the Newtonian velocities relative to M
  read as coordinate velocities): the binary is separated in HRNA as in Newton; the captured
  member's Schwarzschild orbit has a pericentre below 6 M and plunges (r < 2.5 M) within two
  radial periods, at most 400 M after the start [JUDGEMENT from the three_punctures caveat
  (ii)]; the ejected member's energy is within 30 percent of the fixed-hole Newtonian value.
  Also a scan of 180 release phases at r_p = 8, a0 = 3, mb = 0.1, prograde, with law = newton
  and hrna (2404 conventions): separated fractions within 0.1 of newton3's full three-body
  0.878 (start 4 r_t; run F-hills-20261115-130342-0471114) for Newton with a fixed hole, and
  HRNA higher than Newton. Refuted if HRNA keeps the captured member bound for more than two
  radial periods, or if its separated fraction is lower than Newton's.
