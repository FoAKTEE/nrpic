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

### Outcomes of V1-V6

- V1 (run F-hills-20261115-144857-b5b0bce): 10 of 10 newton3 tests pass. Confirmed.
- V2 (runs F-hills-20261115-144919-b5b0bce T1, -144922- T2, -144927- T3, -144935- T4, all
  -b5b0bce): T1 identities 4.4e-16, derivatives 1.0e-10, Kerr-Schild metric equal to
  python/nrpic to 2.2e-16; flat-space binary eccentric at 5.0e-7 (mb = 1e-6) as the helper
  found; T2 positions within 3.5e-9 to 3.4e-8 r_g; T3 1.09e-4; T4 4.2e-8 and 4.3e-8 a0.
  Confirmed.
- V3 (run F-hills-20261115-144954-b5b0bce): 905 numbers of the novelty scale estimate
  identical to the helper's JSON. Confirmed. By hand: r_t/r_g = (a_b/r_gb) q^(-2/3) from
  r_t = a_b q^(1/3) and r_g = q r_gb; Peters (5/256) a^4/(m1 m2 (m1+m2)) with m1 = m2 = m_b/2
  gives (5/64)(a_b/r_gb)^4 G m_b/c^3 = 6328 GM/c^3 at a_b = 30 r_gb, q = 10.
- V4 (run F-hills-20261115-145246-090f5dc, figure fig_v4_restricted): prograde P_dis within
  0.002 and phase-averaged |E| within 0.2 percent at all five D; retrograde within 0.009 at
  D = 0.1-0.3, but at D = 0.38 P_dis 0.172 against 0.193 and |E| 8 percent off. Prediction
  REFUTED at retrograde D = 0.38 (|E| also beyond 2 percent at D = 0.3: 2.0 percent). My
  classification left 49 of 600 samples "bound but wider than half the Hill radius" at 30 r_t
  and counted them as survivors; newton3 reruns such samples to 300 r_t. Test V4b below.
- V5 (run F-hills-20261115-145251-090f5dc): the input file's state has total momentum 1e-10,
  barycentre at the origin to 2e-11, centre-of-mass conic e = 1.00006 and r_p = 7.9965
  (q = 4: 1.0002, 9.809), binary a = 3.036, e = 0.029. Outcome m1 ejected, m2 bound with
  a = 7.55, e = 0.247, pericentre 5.68, closest approach 5.64; E2 = -1.845 units (helper
  -1.845). But E1 = +1.663 units at t = 1500 against the helper's +1.754: prediction REFUTED
  for E1 (q = 4: 1.640 against 1.53, also refuted). Candidate cause, to be tested in V5b: the
  two-body energy of the ejected member with M alone oscillates because M orbits the
  barycentre of (M, captured member).
- V6 (same run, figures fig_v5v6_q10, fig_v5v6_q4): the geodesic baseline disagrees with the
  Newtonian one on the fate of the members. q = 10 from the NR coordinate state: HRNA sends
  m1 into the hole (r < 2.5 M at t = 97, the first pericentre) and ejects m2 with +1.16 units;
  the fixed-hole Newtonian law ejects m1 (+1.89) and keeps m2 bound (pericentres 5.9 M). The
  2404 construction (CM on the Schwarzschild parabola r_p = 8, release at 4 r_t, the NR
  binary orientation) gives the same: m1 plunges, m2 ejected with +0.69. Phase scan of 180
  release phases: Newton (hole fixed) separates 0.889 (newton3 full three-body 0.878), no
  member below 2.5 M; HRNA separates 1.0 and in 0.944 of the phases a member crosses 2.5 M.
  q = 4 (r_p = 9.82): from the NR state HRNA keeps m1 bound (pericentre 7.3) and ejects m2
  (+0.97), the 2404 construction plunges m1; scan: 0.933 of the phases lose a member below
  2.5 M. My prediction that the captured member plunges was right in direction but the member
  that plunges is the one Newton ejects; "HRNA separates more than Newton" holds. The
  prediction is CONFIRMED for the plunge and the separated fraction, REFUTED for "the
  ejected member's energy within 30 percent of Newton" (0.69-1.16 against 1.89).
  [JUDGEMENT] Reason to expect it: a parabolic member needs L >= 4M to avoid the plunge; the
  CM has L = 4.62 M at r_p = 8 and the binary's internal speed (0.09 c per member) changes a
  member's L by about r_p x 0.09 = 0.7 M, so one member falls below 4 M in most phases.

### Predictions of V4b and V5b (before the runs)

- V4b: rerunning my 600-phase retrograde samples at D = 0.3 and 0.38 to an end radius of
  300 r_t, P_dis is within 0.01 of newton3 (0.372, 0.193) and |E| of the disrupted within
  2 percent. Refuted otherwise.
- V5b: in the q = 10 and q = 4 Newtonian runs from the input files, the two-body energy of
  the ejected member with M oscillates after t = 300 with the radial period of the captured
  member (about 120 M) and an amplitude of 0.05 to 0.2 units, so that the helper's value
  (read on the outbound conic at 30 r_t) and mine (t = 1500) both lie inside its band; its
  energy against the barycentre of M and the captured member, mu' (|v - v_cm|^2/2 -
  (M + m_c + m_e)/r), is constant within 0.01 units after t = 300. Refuted if the two-body
  energy with M is constant to 0.02 units after t = 300.

### Outcomes of V4b and V5b

- V4b (run F-hills-20261115-145544-a314517): with the 22 and 49 wide-bound samples rerun to
  300 r_t, retrograde P_dis 0.373 and 0.193 against newton3's 0.372 and 0.193; |E| of the
  disrupted 0.2797 / 0.2807 and 0.1170 / 0.1174. CONFIRMED: newton3's restricted scan is
  reproduced by independent code at all nine (sense, D) points; the V4 difference was my
  classification. One SciPy step-size warning (a near-collision sample) is on record.
- V5b (run F-hills-20261115-145559-a314517, figure fig_v5b_energy): the two-body energy of
  the ejected member with M oscillates with the captured member's period (about 125 M)
  between 1.47 and 1.85 units (q = 10) and between 0.99 and 1.72 units (q = 4); against the
  barycentre of M and the captured member it is constant to 3e-5 (q = 10) and 2e-4 (q = 4)
  units after t = 300, at +1.613 and +1.312 units. CONFIRMED for q = 10; for q = 4 the
  amplitude (0.37 units) exceeds my predicted 0.2. Consequence (a defect of newton3, not of
  the integration): `threebody._pair_energy` reports each member's energy against M alone;
  at finite M/m with one member captured this is not conserved, so the helper's E1 = +1.75
  (q = 10) and +1.53 (q = 4) depend on the read-out time; the conserved values are +1.613
  and +1.312. newton3's finite-mass-ratio energies (fig_finite_q, P3 at M/m <= 100, the
  three_punctures phase scans) need the barycentric definition; outcome classes (sign of the
  energies) are affected only near E = 0.

### Prediction of V7 (pericentre scan for the first passage), before the run

V6 showed that at the helper's first configuration (q = 10, a_b = 3 M, r_p = 8 M) the
geodesic baseline sends a member below 2.5 M in 94 percent of the phases, where the
Newtonian baseline has none. V7 scans r_p = 7-13 M (q = 10, a_b = 3) and 9.82-16 M (q = 4,
a_b = 5), prograde, 180 phases, start 4 r_t, with newton3's full three-body driver and with
geodesic_binary's hole-fixed newton and hrna laws. Prediction: the HRNA plunge fraction falls
with r_p and is below 0.3 at r_p = 12 M for q = 10; the full Newtonian separated fraction
stays above 0.5 up to r_p = 12 M (D = 1.86); so a window with both exists at q = 10 between
r_p = 10 and 12 M. Refuted if no scanned r_p has HRNA plunge fraction < 0.3 together with
Newtonian separated fraction > 0.5.

### Outcome of V7 (run F-hills-20261115-145915-71abf93, figure fig_v7_rp_scan)

q = 10, a_b = 3 M, prograde, start 4 r_t, 180 phases (r_p = 7, 8, ..., 13 M):
full-Newton separated fraction 0.90, 0.88, 0.83, 0.76, 0.70, 0.59, 0.22 (member inside 4 M:
0.62 at r_p = 7, 0.06 at 8, <= 0.03 beyond); fixed-hole Newton 0.91 ... 0.47, 0.00; HRNA
separated 0.97-1.00 at every r_p, a member below 2.5 M in 0.96, 0.94, 0.89, 0.86, 0.78,
0.69, 0.30, one-ejected-one-bound in 0.03 ... 0.27, 0.66. q = 4 (a_b = 5, r_p = 9.82-16):
full Newton 0.84 to 0.54, HRNA separated 0.94-0.99 with plunges 0.94 to 0.67. Prediction
REFUTED: no scanned r_p has an HRNA plunge fraction below 0.3 with a Newtonian separated
fraction above 0.5; at r_p = 13 M (q = 10) HRNA separates 0.98 of the phases where full
Newton separates 0.22. [JUDGEMENT] HRNA is outside its own consistency condition here
(a_b/r_p = 0.23-0.43 against about 0.1 in 2404's examples, appendix.tex:8 per the helper;
the hole is held fixed although q = 10), so it is a frame, not a truth; but both reasons
for its plunges (members with L < 4 M; stronger relativistic tides) are physical and the
NR passage will tell. Decision for the G1 run: keep the helper's configuration r_p = 8 M,
where both baselines are robust over phase and disagree in kind (Newton: no member inside
4 M in 94 percent of phases; HRNA: a member below 2.5 M in 94 percent).

Correction to the V7 entry above (checked at the source): 2404.16270 defines its consistency
parameter as alpha = a / R_curv with R_curv = (r/r_g)^(3/2) r_g (article.tex:272-274), and
reports alpha up to about 0.1 at pericentre in its own examples (appendix.tex:8). For
a_b = 3 M this is 0.13 at r = 8 M and 0.064 at 13 M, i.e. the same as the paper's own peak
values, not "0.23-0.43" (that was a_b / r_p). HRNA's main limitation for our runs is the
fixed hole at q = 10 (and 4), not alpha.

### Session summary (lead, wave 1)

did: checked the four helper packages from their artefacts (V1-V3 re-runs, V4/V4b independent
restricted problem, V5/V5b independent integration of the G1 inputs, V6/V7 geodesic baseline of
the G1 configuration and an r_p scan); looked at the figures relied on (newton3: skr_curves,
bkrs_and_h1, finite_q, general_pdis_energy, full_vs_restricted, start_distance;
geodesic_binary: s1_sepfrac, strong_rp, c2_r0; three_punctures: newton_choice, mesh_count,
mesh_count_b, junk; novelty: scale_plane, cost; lead: fig_v4_restricted, fig_v5v6_q10,
fig_v5v6_q4, fig_v5b_energy, fig_v7_rp_scan); wrote the G0 package (stage/G0/SCOPING.md,
EVIDENCE.md, OPEN.md), stage/G1/STATUS.md with the named passage P1, 14 outbox files, STATUS,
HANDOFF, RISKS.
found: the helpers' central claims hold where checked; newton3's finite-q member energies are
not conserved (V5b); the geodesic and Newtonian references disagree in kind at q = 10,
r_p = 7-12 M (member captured in 69-96 percent of phases against none; V6, V7).
evidence: runs F-hills-20261115-144857-b5b0bce, -144919-, -144922-, -144927-, -144935-,
-144954-b5b0bce, -145246-090f5dc, -145251-090f5dc, -145544-a314517, -145559-a314517,
-145915-71abf93; helper journals novelty/JOURNAL.md, newton3/JOURNAL.md,
geodesic_binary/JOURNAL.md, three_punctures/JOURNAL.md.
changed my mind about: the first passage is no longer expected to be a clean "eject and capture"
Hills event; it is a test between Newtonian capture and relativistic plunge. The novelty
helper's cost (24 card-hours) is replaced by three_punctures' measured 39.
open: OPEN.md of G0 (stage check, second agent, allotment, mass ratio, release of
core/multi-puncture, newton3 energy fix, unverified locators).
failed predictions this session: V4 (retrograde D = 0.38, my classification), V5 (E1 values,
newton3's energy definition), V6 (ejected-member energy within 30 percent), V7 (no plunge-free
window), V5b amplitude at q = 4.
