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

## 2026-11-19T14:55Z  session F-hills lead (wave 2b)  commits f9422309..(this session)

Main merged (634a7882); decisions 0016 and 0017 read. The wave-2 lead was cut off on 2026-11-15
before writing anything (no REVIEW file, no uncommitted lead files; the only untracked file,
`eih/scripts/scan_figs.py`, belongs to the wave-3a helper eih, which works in this worktree at
the same time and commits its own files). Helper reports read: wave 2
(`scratch/orch/wave2_reports/F-hills.md`: newton3_fix, note, nr_first, second_check) and wave 2b
(nr_finish). Card queue at 14:49Z: our job 4640 (S2g) pending behind 12 jobs of other owners.

### Predictions of the lead's checks (written before any of them ran)

V8 (nr_finish, from the raw AthenaK files with a script of my own, `stage/review_wave2/
review_check.py`, not using `nrread.py`):
a. S3 and S2 logs: fatal "1632 ... exceeds max_nmb_per_rank = 1600"; last logged cycle and the
   tracker's last row give t = 21.97 m (S3, cycle 703) and 14.22 m (S2, cycle 455).
b. Horizon summaries: a row equal to its predecessor in columns 3-12 is a failed search; S3 has
   5 such rows (t = 1.0-3.0), S2 2 (t = 1.0-1.5); the first row with hrms < 1e-3 is t = 3.5,
   mass 1.00789 (S3) and t = 2.5, 1.00618 (S2); window medians (hrms < 1e-3) give the drift from
   t = 4-6 to 12-14 as +5.1e-4 (S3) and +8.5e-4 (S2), each within 0.3e-4.
c. Tracker speed ratio f = [x(14) - x(10)] / 4 / (P/M_ADM) with P/M_ADM = 0.25/1.039063: within
   0.01 of 0.468 (S3) and 0.757 (S2); |y|, |z| below 1e-14 throughout.
d. P1 smoke: 1716 MeshBlocks at the start and 1744 at cycle 400 in the log; zone-cycles per
   second / 16^3 = 2057 +- 1 MeshBlock-cycles per second; peak card memory 70847 MiB; the three
   trackers' first rows equal the input positions within 1e-8; horizon at t = 0: m1 0.12778,
   heavy 0.99607, m2 NaN; failed searches (NaN or repeated rows) 1, 2, 17 of 25.
   Refuted (for the helper's numbers) if any value differs beyond the stated tolerance.
V9 (GR reading of the start states; my own implementation of the test-particle invariants of a
Schwarzschild hole in isotropic coordinates, not `second_check/nr_invariants.py`):
a. q = 10 (`three_punctures/inputs/hills_q10_m8.athinput`), hole frame, M_h = M: reproduces the
   second check's centre-of-mass E = 0.99925, L = 4.19 M and turning point r_S = 5.77 M within
   0.01 M (refuted otherwise).
b. q = 4 (P1, `nr_first/inputs/p1_q4.athinput`): hole frame, M_h = M: E about 1.004 (unbound),
   L about 4.95 M, not captured, turning point r_S between 8.5 and 9.8 M (the Newtonian 9.81 M
   shrinks less than at q = 10 because L is further above the capture value 4 M); with the hole
   at rest or with M_h = M + m_b the centre of mass is bound (E < 1) with L/M_h about 3.96, at the
   capture boundary [JUDGEMENT; refuted if the hole-frame reading captures the centre of mass].
   Consequence planned: if (b) holds, P1 stays as prepared (both baselines start from the same
   state, so the comparison does not need a GR parabola); if the hole-frame reading captures the
   centre of mass, P1 is not submitted and the momenta are rebuilt first.
V10 (newton3_fix): the 15 unit tests pass at this commit; `results/passages.json` at q = 4 has
m1 ejected with +1.3119 units and m2 captured with a = 7.746, e = 0.2503 (README table).
V11 (note, second_check): the note helper's two differences hold: V4/V4b summaries show retrograde
D = 0.1 and 0.2 only in V4, with |dP| 0.0023 and 0.0063; the q = 4 m/16 trees at puncture radius
1.8 are 2514 / 2864 / 2568 in run F-hills-20261115-131933-907e5fe.

### Outcomes of V8-V11

V8, run F-20261119-145434-82c05f2 (`review_nr.json`, `fig_review_nr.png` of the run, read): all
met [VERIFIED].
a. Both logs end with "1632 ... exceeds max_nmb_per_rank = 1600"; trackers end at iteration 703,
   t = 21.969, x = 2.2034 (S3) and 455, t = 14.219, x = 2.2168 (S2).
b. Failed searches 5 (S3: t = 1.0-3.0) and 2 (S2: 1.0-1.5); first search with hrms < 1e-3:
   t = 3.5, 1.007886 (S3) and t = 2.5, 1.006176 (S2); t = 0: 0.999087 (hrms 4.6e-3, mean radius
   0.477 m) in both; drift of the window medians t = 4-6 to 12-14: +5.15e-4 (S3), +8.55e-4 (S2);
   spin at most 1.1e-4 m^2. The t = 0.5 search (0.98594, hrms 1.9e-2) is "found" by AthenaK's
   test and is a poor surface, as the helper says.
c. f over t = 10-14: 0.468 (S3), 0.758 (S2); |y|, |z| at most 2.5e-15.
d. P1 smoke: 1716 at the start, 1744 at cycle 400; 8.427e6 zone-cycles/s = 2057.4 MeshBlock-cycles/s;
   peak 70847 MiB; first tracker rows within 4.1e-9 of the input positions; t = 0 masses m1
   0.127780, heavy 0.996068, m2 NaN; failed searches 1, 2, 17 of 25; good searches (hrms < 1e-3)
   16, 16, 0 in t <= 1.56 M. Cost at 2057.4: 16.9 / 18.4 / 20.1 card-hours for 1744 / 1905 / 2080
   MeshBlocks, the helper's numbers.
V9, run F-20261119-145449-245e984 (`review_gr.json`, `fig_review_gr.png`, read): (a) met: q = 10 hole
frame E = 0.999253, L = 4.1944, turning point r_S = 5.775 M (second check: 0.99925, 4.19, 5.77).
(b) met: P1 (q = 4) hole frame E = 1.00420, L = 4.952 M, not captured, turning point r_S = 9.25 M
(Newtonian conic r_p = 9.809 M, e = 1.00023); hole at rest: E = 0.9917, L = 3.962, not captured,
turning point 4.66 M just outside the barrier top at 4.04 M; M_h = M + m_b: captured. So at q = 4
the GR reading moves the centre-of-mass turning point by 6 percent in the natural (hole-frame)
reading, against 28 percent at q = 10; the two other readings put it at the capture boundary.
Consequence as planned: P1 keeps its input (both baselines start from the same state, E6).
V10, run F-20261119-145509-fb91531: 15 of 15 newton3 tests pass at 82c05f2e: met. passages.json:
q = 4 m1 ejected +1.31191 units, m2 captured a = 7.7458, e = 0.25027, first pericentre t = 122.1;
q = 10 +1.61272, a = 7.547, e = 0.2474: met. These equal the wave-1 lead's own barycentric values
(V5b: 1.31187, 1.61267) from a different integrator, so the corrected definition is confirmed by
two codes; its derivation in the README was read, not re-derived.
V11: met. `stage/G0/checks/v4_summary.json`: retrograde D = 0.1 and 0.2 only in V4, |dP| 0.0023
and 0.0063, |dE|/E 0.004 and 0.012 (with 8 and 14 ambiguous samples not followed on); V4b covers
retrograde D = 0.3 and 0.38 only. So "all nine agree within 0.002 and 0.4 percent" (wave-1 lead,
EVIDENCE.md V4b row, G1 T1, STATUS) is WRONG for two points; corrected in the G1 package.
`mesh_count_b.json` of F-hills-20261115-131933-907e5fe: q = 4 m/16 at puncture radius 1.8 gives
2514 / 2864 / 2568.5 MeshBlocks and 44.8 card-hours (SCOPING section 9 printed the radius-1.2 row,
2416 / 2654 / 2348, 41): corrected in SCOPING.md section 9.
Small fix: `nr_first/results/e3_single_analysis.json` and `figures/fig_e3_single_gauge.png` were
made before the horizon reader was fixed; rerun F-20261119-145619-8246322 replaces them (found/
missed 39/5 and 27/2; figure read: failed searches no longer drawn as masses).

### P1: decision (lead) and prediction, written before submission

Did the single-puncture runs and the smoke pass their criteria (`nr_first/JOURNAL.md` E3, E7)?
- Smoke (E7): every run-health criterion met (tree 1716 -> 1744, rate 2057, memory 69.2 GiB of 80,
  trackers at the input positions, no non-finite value, H at t = 0 equal to the processor value);
  one prediction failed: the first-search horizon masses (m2 not found at t = 0, the heavy hole's
  first searches fail 17 of 25 times in 1.56 M). That is a finder limitation in the first
  0.5 M (members) to about 4 M (heavy hole), not a health failure: masses are read after it.
- S3, S2 (E3): what the passage depends on was met: tracker symmetric to 2.5e-15, settling with
  the members' damping of P1 (eta m = 0.25) measured (f = 0.76 by t = 4 m, flat), constraint norm
  flat (5e-5), no non-finite value, horizon drift with eta m = 0.25 1.7 times that of eta m = 2
  (inside the predicted factor two). Failed: the first-search mass (0.9991 instead of
  1.006-1.010), S2 reaching f = 0.8 (0.774), the cost (tree twice the prediction); and the runs
  stopped at t = 22 m and 14 m of 90 m, so the junk energy of a member is not measured. The stop
  is the single-puncture input's slot limit (1632 > 1600), explained block by block by E11 and
  confirmed by V8a; it does not carry over to P1, whose tree was measured on its own input (smoke,
  50 regrids) and along the Newtonian track (wave 1: at most 2080; with core's 11 percent AMR
  growth 2309) under its limit of 2700. The junk of the three-hole data is measured by P1 itself.
Verdict [JUDGEMENT]: the criteria that bear on running P1 are met; the failed predictions and
the missing junk measurement are recorded and do not block it. P1 is submitted.
Gauge [JUDGEMENT from S2/S3]: constant shift_eta = 2 (eta M = 2, eta m = 0.25), release core-v0.3
card executable behind the tracker wrapper: the members' trackers settle in 4 m with eta m =
0.25 but are still accelerating at 22 m with eta m = 2, and coordinate trajectories are what the
passage is read from; the price is a 1.7 times faster horizon-mass drift and a 25 percent smaller
coordinate horizon (7 cells). Core's mass-scaled profile is untested with three holes and its
single-hole test S2g (job 4640) is queued; it is not chosen.
Start state (V9): Newtonian conic r_p = 9.81 M; GR test-mass reading in the hole frame: turning
point r_S = 9.25 M; at the capture boundary in the other two readings.

Prediction for P1 (refuted where stated):
1. Health: three trackers to t = 280 M; tree between 1716 and 2400 MeshBlocks, never above the
   2700 slots (refuted if a segment stops on the slot limit); 1900-2200 MeshBlock-cycles/s; 17-20
   card-hours, 21-25 segments; no non-finite value; history Volume constant.
2. Outcome: the binary is separated by t = 200 M (member separation above 2 a_b = 10 M and growing;
   refuted if it is still bound at t = 200), one member leaves and one stays bound to the heavy
   hole. Which one is open: Newton ejects m1 with +1.312 units (4.96e-3 M per unit) and binds m2
   (a = 7.75, e = 0.25, pericentre 5.81 M at t = 122); HRNA ejects m2 with +0.970 and binds m1
   (pericentre 7.26 M at t = 121). No common horizon of a member with the heavy hole by t = 280
   (both baselines stay outside 5.7 M; refuted by a merger).
3. Horizons: member masses from t = 0.5 M at 0.1295 (smoke); if the single-puncture rate of
   0.6-1.1e-4 per m persists, they grow by 10-18 percent by t = 200 M [JUDGEMENT; refuted if the
   growth at t = 100 M is below 2 or above 25 percent]. Heavy-hole masses from about t = 4 M.
4. Radiation: the junk of the data passes the 40-90 M spheres by t = 150 M; its energy is between
   1e-6 and 1e-4 M [JUDGEMENT from core's single-hole scaling]; the passage burst is not resolved
   at the 2-4 M cells of the wave zone for member-scale modes.
The next session analyses P1 with `nr_first/scripts/p1_analysis.py` (E9) and these predictions.

### P1 submitted

Run F-20261119-150017-b45ec5f, Slurm job 4650 (first segment pending at 15:00Z; Slurm's estimate
of the start 2026-11-20 02:12 UTC), chain capped at 26 segments, release core-v0.3 card
executable behind `nr_first/scripts/athena_keep_trackers.sh`, input sha256 in the manifest.
Announced in STATUS.md before submission (commit b45ec5f1) and to orch
(`outbox/20261119T151430Z__to-orch__p1-submitted.md`).

### Session summary (lead, wave 2b)

did: inspected the worktree (the wave-2 lead left nothing); merged main; checked every helper of
waves 2 and 2b from their artefacts (V8 own parser of the raw AthenaK files, V9 own GR invariants,
V10 newton3 tests, V11 summaries; 22 figures read); replaced the stale E3 copies; corrected four
wave-1 statements (V4b nine points, the q = 4 m/16 tree, HRNA percentages as predictions, the
8.6 percent); judged the single-puncture runs and the smoke against their criteria and submitted
P1 with constant shift_eta = 2; brought G0 and G1 to the harness (collect, verify, report);
posted 7 outbox messages and acknowledged 7; rewrote STATUS, HANDOFF, RISKS.
found: every number of the helpers' reports that I recomputed agrees (V8-V10); two claims of the
wave-1 lead were wrong (V11); P1's start state turns at 9.25 M in the GR hole-frame reading,
6 percent inside its Newtonian pericentre, while the q = 10 input's turns at 5.77 M (28 percent);
G0 verify fails only on runs in flight and on three wave-2 run directories with moved-in,
unchecksummed outputs.
evidence: runs F-20261119-145434-82c05f2, F-20261119-145449-245e984, F-20261119-145509-fb91531,
F-20261119-145619-8246322, F-20261119-150017-b45ec5f; stage/G0/VERIFY_RESULTS.md (7a24d7e),
stage/G1/VERIFY_RESULTS.md (b95903f, --no-checksums); stage/REVIEW-wave2.md.
changed my mind about: the start state of P1 does not need rebuilding from a GR parabola at
q = 4 (it does at q = 10); the single-puncture runs' early stop is a configuration of their input
and not a warning for P1.
open: S2g's outcome (E10); P1's outcome and the junk energy; Kerr for F-pre-2; G1 schematics and
note sections; a verifier for G0/G1; orch's ruling on the three run directories.
failed predictions this session: none of V8-V11 failed; the P1 prediction is open.
card-hours used this session: 0 (P1 and S2g pending; 0.30 used by the package in total).

## 2026-11-21T06:35Z  session lead F-hills (wave 3, batch 2a)  commits 9ce19873..  runs (below)

Start: main merged (9ce19873, release core-v0.4 on main); pause flag absent. State found:
`verify_g0` finished (batch 1, VERIFIER.md committed and pushed); `eih` (wave 3a) finished and
not yet reviewed; the five other packages of round 1 were cut at 14:35 PST on 2026-11-20:
`note` (paused, committed), `junk_gauge` (committed to the J4 prediction), `p1` (journal entry 4
and README, figures, results uncommitted), `kerr` (everything uncommitted, predictions only),
`g2mesh` (one script uncommitted). P1's chain runs by itself: segment 14 (Slurm 4769) from
t = 231.9 M. p1's uncommitted journal entry 4 reports that the binary MERGED at t = 48.8 M,
before the passage.

### Predictions of the lead's checks (written before any of them ran)

L1 (P1 merger, own parser of the raw tracker and horizon files, not p1lib/nrread): the
coordinate separation of trackers 0 and 1 falls below 0.1 M first at t = 48.8 +- 0.3 M; finder
0 or 1 reports a horizon of mass 0.26-0.28 with hrms < 1e-3 from t = 48.8-49.2 M; before
t = 30 M the separation decreases monotonically. Refuted if the separation stays above 2 M to
t = 60 M or no finder reports a mass above 0.2 before t = 60 M.
L2 (verifier's WRONG items, own arithmetic and own reading): (a) the G2 items of SCOPING 9 sum
to 131 card-hours; (b) 70847 MiB at 2700 slots gives 26.2 MiB per slot and about 3100 slots on
81920 MiB; (c) in s1.npz the largest alpha = a/R_curv at any time at beta = 10 (HRNA) is
0.20 +- 0.01 while the ledger's 0.0056 is the bound-pair maximum; (d) 4 q^(2/3)/2.085 = 14.1
(q = 20) and 18.5 (q = 30); (e) SCOPING sections 3, 6 and 9 name q = 10 for the first passage.
L3 (eih): (a) the registered rerun of `tests/test_eih.py` passes 9 of 9 with the recorded numbers
to the printed digits; (b) my own 1PN two-body integration (relative EIH equation in harmonic
coordinates, Blanchet's form, written here) of a binary started with the Newtonian circular
speed at a = 30 m_b, nu = 1/4, gives a radial eccentricity 0.09-0.13 (eih T5: 0.12); refuted
outside; (c) my own test-mass check of T4 (1PN test-mass equation from its Lagrangian, E_1PN = 0,
J = L of the Schwarzschild parabola; exact Schwarzschild by quadrature; both from and to
r0 = 1e4 M) gives the error of the relativistic excess -0.27 +- 0.03 at areal r_p = 10 M and
-0.09 +- 0.02 at 20 M.

### Outcomes of L1-L3 (all figures read)

L1 [VERIFIED, run F-20261121-063449-4dcca98, `fig_review3_p1.png`]: tracker separation 4.952 M
at t = 0, below 2 / 1 / 0.5 / 0.1 M first at t = 39.16 / 44.07 / 46.34 / 48.79 M, 1e-6 M at
t = 60; finder 0 reports a horizon of 0.2686 at t = 48.81 M, finder 1 0.2693 at 49.06 M (median
0.2684 both), last separate members 0.1370 (t = 46.50) and 0.1390 (46.81); the heavy hole's
finder good from t = 2.375 (1.00002) to 236.06 (1.00736). MET, except the clause "monotonically
before t = 30 M": the separation rises by at most 3.0e-4 M in one sample (refuted as worded, a
wiggle 6e-5 of the separation). Beyond p1's t = 112 M: the remnant (mean of trackers 0 and 1) is
closest to tracker 2 at t = 154.6 M, 6.99 M coordinate distance, and at 16.9 M at t = 236.1 M,
receding. So p1's merger result stands from my own parser.
L2 [VERIFIED, run F-20261121-063504-00f0743, `fig_review3_g0.png`]: (a) 131 (134.8 with the
m/16 row of 44.8); (b) 26.24 MiB per slot, 3122 slots, and core-v0.4's interface now states
"about 3100 slots with three finders" (`coord/INTERFACES/multi_puncture.md:235-247`); (c) 0.1993
(prograde) and 0.0734 (retrograde) at any time, 0.0056 and 0.0038 while bound; (d) 14.14 and
18.52; (e) SCOPING lines 50, 114, 185 (and 6, 9 headings). All MET: the verifier's D3, D5, D6,
D7 and D4 hold.
L3 [VERIFIED]: (a) run F-20261121-063520-abab33e: 9 of 9, all 346 recorded values identical;
(b) e_r = 0.1217 at a = 30 m_b and 0.2080 at 20 m_b (eih 0.1217, 0.2080): MET; (c) first attempt
FAILED by method (run F-20261121-063527-b4453db): I imposed E_1PN = 0 at the pericentre, which
leaves a hyperbola at large r (excess error -1.5, the orbit deflects less than Newton); the
second attempt (run F-20261121-063646-d826df4) imposes E_1PN = 0 at r0 = 1e4 M and gives -0.3931,
-0.2682, -0.1963, -0.0881, -0.0351 at areal r_p = 8, 10, 12, 20, 40 M, equal to eih's T4 to
1e-9; my exact Schwarzschild angles equal eih's to 1e-12. MET. The failed first attempt is
itself a measure of the 1PN ambiguity near pericentre: where the parabola is defined matters at
order one inside 12 M.
Also: rerun of the verifier's ledger recomputation (run F-20261121-063712-25981e0): 56 of 57 rows
identical; row 57 ("about 3000 slots", `multi_puncture.md:229-230`) no longer agrees because
release core-v0.4 rewrote that paragraph (now lines 235-247, "about 3100"): a stale locator
of the note's ledger, not an error of the verifier.

### What the session did with the results (2026-11-21, lead)

- G0: every WRONG, PARTLY or NOT DONE item of `stage/G0/VERIFIER.md` checked at the source and
  answered in `stage/REVIEW-wave3.md`; `SCOPING.md` amended in place (D1 GR turning points, D2 V7
  construction, D3 G2 sum 131 -> plan of about 100, D4 q = 4, D5 slot limit vs card, D6 plunge
  bound, D7 alpha at pericentre, D8 KHSR plan); note text corrected (D7, D10) and its ledger
  corrections listed for the paused note package; novelty locator and attribution fixed (orch's
  brief-check message); C18 PASS; collect, verify, report. Judged complete for an independent
  review; asked of orch.
- p1's uncommitted intermediate analysis committed (finished work; merger confirmed by L1);
  kerr's and g2mesh's uncommitted files left alone (packages in progress), listed in HANDOFF.
- g2mesh's card run F-20261120-222810-e408386 finished in nrpic-run (status failed: its last case
  aborted, rc 134); its m/16 case at 3000 slots ran at 78785 MiB (read from the log).
- G1 re-judged: not met (T4 not met in substance after the merger; KHSR, Kerr, three-hole junk,
  note compile, verifier open).
- Outbox: orch (G0 review, waivers, errata row 1.5, chain rule for outside kills, P1 merger
  information), core (tracker files reminder, Bowen-York momenta vs 1PN). Six inbox messages
  acknowledged. STATUS, HANDOFF, RISKS (R15 new) rewritten.

### Session summary (lead, batch 2a)

did: reviewed verify_g0 and eih from their artefacts (own parser, own 1PN integrations, reruns of
their registered analyses); checked p1's merger from the raw files; corrected the G0 plan after
the verifier; brought G0 and G1 to the harness; posted 7 messages, acknowledged 6.
found: P1's binary merged at t = 48.8 M (no reference merges); the verifier's D3-D7 hold exactly
at the source; eih's T4 and T5 hold to 1e-9; 3000 MeshBlock slots fit one card.
evidence: runs F-20261121-063449-4dcca98, F-20261121-063504-00f0743, F-20261121-063520-abab33e,
F-20261121-063527-b4453db, F-20261121-063646-d826df4, F-20261121-063712-25981e0.
changed my mind about: P1 as the G1 passage (its binary does not survive to the encounter at m/8);
the 2700-slot limit as a card limit (it was the input's); the G2 compute (did not fit 120 as
listed).
open: cause of the merger (isolated binary at m/8 and m/16); P1 to t = 280 M; J4 and E10; kerr;
KHSR; note compile; G1 verifier.
failed predictions this session: L1 clause "separation decreasing monotonically before t = 30 M"
(a 3e-4 M wiggle); L3c first attempt (failed by my method, E_1PN imposed at pericentre). Carried
from earlier sessions and decided now: P1 item 2 (separation by t = 200 M) REFUTED by the merger.
card-hours used this session: 0 submitted by the lead; P1's chain ran on (segments 8-14, about
5.3 card-hours since the last lead session; 10.72 in total by sacct).

## 2026-11-21T15:55Z  session lead F-hills (wave 3, batch 4a)  commits 5b2ad0df..  runs (below)

Lead of F-hills after batches 2b (junk_gauge) and 3 (binary_conv, kerr). Main merged (release
core-v0.6 on main). Pause flag absent. Queue at 07:45 PST: two jobs of this owner pending
(binary_conv R16n segment 2, Slurm 4807; R12, Slurm 4809), so nothing may be submitted now
(CLAUDE.md, two jobs per owner). G0 is signed (coord/GATES.md, 2026-11-20); G1 is the gate.

### Predictions of my checks (written and committed before any check runs)

My script `stage/review_wave3/review4.py` (own parsers of AthenaK's raw tracker, horizon,
history and waveform files; own 1PN integration; it imports none of the packages' readers).

L4 binary_conv (runs F-20261121-130358-6cf186a R8, F-20261121-130351-04074e1 R16n, P1
F-20261119-150017-b45ec5f):
 a. Separations of the trackers at t = 2.5, 5, 7.5, 10, 15, 20 M equal the package's BC-3 table
    to 2e-4 M (P1, R8, R16n where present); largest |s_R8 - s_P1| on 0-20.94 M is 0.093 +- 0.002
    M, at t > 20 M. Refuted by any larger difference.
 b. My own integration of the ADM 1PN two-body Hamiltonian (momenta of the input read as
    canonical, positions as ADM coordinates; Hamilton's equations by complex-step gradients)
    gives separations within 0.005 M of the package's "EIH canonical" column at the same six
    times; my Newtonian integration (v = p/m) within 2e-4 M of its Newton column. Refuted
    outside (then "R16n follows the 1PN reference" depends on the reference's form).
 c. R16n stays within 0.01 M of my 1PN separation over 0-7.74 M; R8 is more than 0.05 M inside
    it at 7.5 M. Refuted otherwise.
 d. Horizons: R16n has no failed or repeated search with hrms < 1e-3 after t = 0.5 in either
    finder and masses 0.1273-0.1278 over 3-7.7 M; R8's masses rise by 0.8-1.6e-3 per M over
    5-20 M. The R8 history file holds H-norm2 above 1e3 at t = 0.5 and below 20 at t = 1.0.
 e. A rerun of the package's registered analysis (`binary_conv/scripts/analyze.py`, same
    command as F-20261121-154046-c99ccb9) gives the same numbers as
    `results/analysis_intermediate.json` (identical for every shared key: the chains have not
    advanced since). Refuted by any difference.
L5 junk_gauge (P1's waveforms, run F-20261119-150017-b45ec5f): my own fixed-frequency
    integration (omega_0 = 0.2/M, record cut at u = 14 M, 4 M cosine tapers, u = t - R*,
    R* = R + 2 M ln(R/(2 M) - 1), M = 1.25) gives the energy in u in [-35, 6] M at R = 70 and
    90 M within 20 percent of the package's 2.46e-6 and 2.52e-6 M, and an l >= 4 share in
    0.55-0.80. Refuted outside 20 percent (then the T3 number is method-dependent beyond its
    quoted FFI spread).
L6 kerr: (a) the registered T8 test rerun (`kerr/tests/t8_bks_chart.py`) repeats its JSON to
    1e-10 relative (processor, deterministic), in particular the 'cks' odd part 0.0398 against
    the leading-order 0.0412 at r = 50; (b) the registered analysis of the 2402 scan
    (`kerr/scripts/analysis_2402.py` on scan F-20261121-132131-326dfd1) repeats
    `kerr_2402_summary.json`. (c) My own estimate of the slicing pump: pairing the members at
    equal Kerr-Schild time displaces the separation by (2M/r) V (n . dx); for a circular binary
    the orbit-averaged work of the Newtonian pair force on that displacement gives
    |d ln|E_b|/dt| = (2M/r) omega_b |(n x V) . L_hat|, the same coefficient as the package's
    formula (2H, H = M/r) [JUDGEMENT: derivation on paper, written here before reading the
    package's derivation in detail; sign convention not checked]. Refuted by (a) or (b) differing.

L4 first outcome (run F-20261121-155018-620fe7f, `review4_bc.json`; figure read below) and a
new prediction L4f, written before its run:
- L4a MET: the separations equal the BC-3 table at all six times (P1, R8, R16n to 1e-4 M);
  largest |s_R8 - s_P1| = 0.0930 M at 20.94 M; Delta s ratios 0.670, 0.812, 0.865 (7.5, 15, 20).
- L4b FAILED: my ADM 1PN integration gives 4.9494, 4.9419, 4.9290, 4.9105, 4.8551, 4.7723 at
  2.5-20 M against the package's EIH-canonical 4.9503 ... 4.9302 (0.019 M apart at 7.5 M, 0.158
  at 20 M); my Newton equals the package's Newton column to 1e-4 (MET). An unregistered
  diagnostic of mine (scratch/F-hills/tmp/lead4a/diag.py, superseded by L4f) gave my own
  harmonic EIH with v = dH/dp (truncated) 4.9383 at 7.5 and 4.8408 at 20 M: a third value.
- L4c FAILED: R16n lies up to 0.019 M outside my ADM 1PN separation (at 7.5 M); R8 is 0.043 M
  inside it at 7.5 M (predicted more than 0.05).
- L4d: H-norm2 of R8 18292 at t = 0.5 and 10.9 at 1.0: MET. R16n: 58 and 41 searches after
  t = 0.5 have hrms >= 1e-3 (my criterion), FAILED as worded; but their masses lie within 1e-4 of
  the others (0.12736-0.12743, 0.12757-0.12768), so "found in every search" holds in substance.
  R8's absolute mass rise is 1.3e-4 and 1.9e-4 per M (fractional 1.0e-3, 1.4e-3 per M): my
  range 0.8-1.6e-3 per M FAILED because I read the package's fractional drifts as absolute; the
  package's README and BC-3 label fractional drifts "per M" (small defect).
L4f (prediction): the spread is the 1PN truncation ambiguity of a binary whose members move at
  0.11-0.33 c (centre of mass at 0.22 c). (i) My own harmonic EIH started with v from an exact
  inversion of the EIH-Lagrangian momenta (own fixed point) reproduces the package's
  EIH-canonical column within 3e-4 M at all six times; (ii) the four 1PN variants (ADM
  Hamiltonian; EIH with truncated v(p); EIH with exact v(p); each in the frame of the input)
  spread by more than 0.1 M at 20 M and by more than 0.01 M at 7.5 M; (iii) the same variants
  in the centre-of-mass frame (P_total removed from both momenta in proportion to the masses)
  spread less than in the input frame. Refuted if (i) fails (then the package's reference
  differs from mine for a reason not identified) or if (ii) fails.

L4e outcome (run F-20261121-155442-5f15a25): the rerun of binary_conv's registered analysis
equals `results/analysis_intermediate.json` in every key: MET.
L4f outcome (run F-20261121-155353-e4d3354, `review4_pn.json`, figure `fig_review4_pn.png`
read): (i) MET, my harmonic EIH with the exact v(p) equals the package's EIH-canonical column
within 5e-5 M at all six times; (ii) MET, the three 1PN variants in the input frame spread by
0.0187 M at 7.5 M and 0.158 M at 20 M (ADM 4.7723, EIH truncated 4.8408, EIH exact 4.9302);
(iii) MET narrowly (centre-of-mass frame 0.0171 and 0.125 M). So the package's reference is
reproduced exactly, but it is one of several 1PN-equivalent references that differ by more
than the R16n deviations being judged (the members move at 0.11-0.33 c).
L5 outcome (run F-20261121-155457-5f36517, `review4_junk.json`, figure `fig_review4_junk.png`
read): my own FFI energy in u in [-35, 6] M is 2.64, 2.48, 2.26, 2.35 e-6 M at 40, 48, 70, 90 M,
0.92-0.95 of the package's 2.84, 2.62, 2.46, 2.52; l >= 4 share 0.69-0.71: MET. But the figure
shows the cumulative energy rising quickly only over u of about -33 to -29 M and then steadily,
with no plateau, to the end of the window at every radius.
L5b (prediction, before its run): with the same integration, E over u in [-35, -28] M lies in
0.3-0.6e-6 M at all four radii, and the mean rate dE/du over [-20, 6] M is 3-8e-8 M per M, equal
within 30 percent at 70 and 90 M. If so, about two thirds of the window's energy is a steady
outgoing emission and not a burst of the initial data. Refuted outside these ranges.
L5b outcome (run F-20261121-155549-4359678): E over u in [-35, -28] M is 0.57, 0.63, 0.49,
0.40 e-6 M at 40, 48, 70, 90 M (FAILED at 48 M by 0.03e-6, met at the others); the mean rate
over [-20, 6] M is 5.3, 5.0, 5.2, 5.4 e-8 M per M (MET, equal within 8 percent at all radii).
So 75-83 percent of the window's 2.3-2.6e-6 M is a steady outgoing emission at a rate the
same at every sphere, and only 0.4-0.6e-6 M is the burst that arrives with the initial data.
What the steady part is (the binary's own emission while the m/8 members spiral in
numerically, the moving members crossing refinement boundaries, or else) is not identified
[JUDGEMENT: P1's separation falls from 4.95 to 3.36 M by t = 30 M, which raises the quadrupole
luminosity about sevenfold; a steady source that the m/8 artefact feeds is the likeliest].
L6 outcome: (a) T8 rerun (run F-20261121-155605-7d21f63) equals the registered JSON in all 232
values (MET; figure read: the 'cks' a = 0.9 retrograde binary runs away to ln|E_b/E_b0| of
about 8 near r = 20, 'bks' stays with 'sch'; odd part of 'cks' follows the leading order to
r of about 30). (b) Analysis rerun (run F-20261121-155614-7997653) equals
`kerr_2402_summary.json` in all 6772 values (MET; `fig_incld.png` read: L_z > 0 median 1-3
steps below the paper at beta = 0.52-0.68, the other panels within one step). (c) My
derivation gives the same coefficient 2M/r as the package's 2H (JUDGEMENT, on paper).

### P1b: decision of this session (decision 0022 item 4) and the rule for the next one

State (07:45-08:15 PST): the isolated m/16 binary (R16n, run F-20261121-130351-04074e1) has
reached t = 7.74 M of the about 100 M the passage needs (segment 1; segment 2 is Slurm 4807,
pending since 07:05 PST; segment 3 follows by itself). R12 (run F-20261121-153707-1eaa5d4,
Slurm 4809) has not started. Two jobs of this owner are queued, so nothing may be submitted.
Neither "has reached" nor "will reach by its trend" is shown: the m/16 binary does not decay
over 0-7.7 M, but the order of convergence that the extrapolation needs is not established
(review: the 1PN references spread by 0.019 M at 7.5 M, the deviations being judged are of the
same size; order anywhere above about 1.2). DECISION: P1b is NOT submitted in this session.

Pre-registered rule P1b-D for the session that reads R16n segments 2-3 and R12 (written now,
before the data; Delta s(t) = s(0) - s(t) of the tracker separation; R8 values VERIFIED in
run F-20261121-155018-620fe7f: Delta s_8(15) = 0.3054, Delta s_8(20) = 0.5766 M):
- D1 (three resolutions, needs R12 to 15 M and R16n to 15 M): fit Delta s_h(15) = Delta s_c +
  C h^p with h = 1, 2/3, 1/2 (cells in units of m/8). Submit P1b at m/16 if the sequence is
  monotone, p >= 2 and Delta s_c(15) lies in -0.02 to 0.12 M (the 1PN variants give 0.011-0.097
  M at 15 M, run F-20261121-155353-e4d3354). Then the m/16 merger time is at least 53 x 2^2 =
  210 M by the stretch model of BC-3 [JUDGEMENT].
- D2 (R16n alone, if R12 has not landed): submit if Delta s_16(20) <= 0.10 M (R8 reaches that
  decay at about t = 10 M, so the m/16 decay is at least twice slower: merger after about
  106 M or later) AND R16n's member masses stay flat (fractional drift below 1e-4 per M) AND
  its tracker separation has no step larger than 0.01 M.
- Not submitted if D1 gives p < 1.5, a non-monotone sequence, or D2 fails: then the next
  passage needs finer members than m/16 (m/16 at q = 4 already uses 2514 of 3000 slots on one
  card) or a wider binary; the lead decides with the R12 and R16n data.
- What is submitted under D1 or D2: `binary_conv/inputs/p1b_R16n.athinput`, chain command of
  binary_conv JOURNAL BC-4 item 6 with `--gpu-hours 32` (32 segments of 50 min, about 26.7
  card-hours, to 170-205 M), executable `athena_keep_trackers_bc.sh` running the byte copy of
  release core-v0.5's card build that R8 and R16n ran (`bc-ak05-gpu`), with main's
  `scripts/submit_chain.sh` of release core-v0.6 (resubmits after an outside kill), constant
  shift_eta = 2 as P1, R8, R16n. Announced in STATUS.md now (decision 0014): 32 card-hours,
  G1 allotment 50, used about 15.1 (P1 12.58 by sacct over its 16 jobs, S2g 0.52, wave 2 0.30,
  binary_conv 1.67), 3.3 more queued in binary_conv.

### What else this session did

- P1's chain ended DONE at t = 280 M (2026-11-21 01:19 PST); finished in nrpic-run (manifest
  commit eb0b2230; 267 files, 165 GB checksummed). Card-hours by sacct over its 16 jobs: 12.58.
- Stage G1 brought up to date: STATUS.md (T2 Kerr in part, T3 met with reservations, T4 not
  met), OPEN.md, EVIDENCE.md (batch 2b-4a runs), CHECKLIST C6 FAIL (KHSR only), C7 PASS with
  reservations, C8 FAIL, C20 PASS; REVIEW.md points to the batch-4a review.
- RISKS: R15 updated (cause settled at m/8), R17 new (no sharp 1PN reference), R18 new ('cks'
  slicing pump), R4, R6, R7, R8, R16 updated.
- Left alone: g2mesh's uncommitted `scripts/card_analysis.py` (package cut, in progress).

### Session summary (lead, batch 4a)

did: reviewed junk_gauge, binary_conv and kerr from their artefacts with my own parsers and
integrations (seven registered runs); closed P1 in nrpic-run; decided not to submit P1b and
wrote the rule P1b-D for the session that reads the queued chains; brought the G1 package up to
date; posted 6 messages, acknowledged 4.
found: binary_conv's numbers repeat exactly, but its 1PN reference is one of three equivalent
ones that differ by 0.019 M at 7.5 M and 0.158 M at 20 M, so the claimed order (>= 3.3) and the
"m/16 survives 100 M" extrapolation are not established; junk_gauge's window energy repeats
within 8 percent, but three quarters of it is a steady emission, not the junk burst
(0.4-0.6e-6 M); kerr's T8 and 2402 analysis repeat exactly.
evidence: runs F-20261121-155018-620fe7f, -155353-e4d3354, -155442-5f15a25, -155457-5f36517,
-155549-4359678, -155605-7d21f63, -155614-7997653; P1 finish eb0b2230.
changed my mind about: reading "follows EIH within 0.006 M" as accuracy (the 1PN form matters at
that level for members at 0.11-0.33 c); the three-hole junk number (mostly not junk).
open: R16n segments 2-3 and R12 (Slurm 4807, 4809) and rule P1b-D; KHSR; p1 analysis to 280 M;
note; g2mesh; G1 verifier.
failed predictions this session: L4b (my 1PN within 0.005 M of the package's: 0.158 M apart at
20 M), L4c (R16n within 0.01 M of my 1PN: 0.019; R8 > 0.05 M inside: 0.043), L4d in two clauses
(R16n hrms criterion; R8 drift range read from fractional values), L5b at 48 M (early energy
0.63e-6 against <= 0.6e-6). Met: L4a, L4e, L4f, L5, L6a-c, the rest of L4d and L5b.
card-hours used this session: 0 (no submission; two F-hills jobs queued throughout).

## 2026-11-21T20:25Z lead, batch 5 (cards first; decision 0025 items 4-5)

State at start (12:20 PST): both chains ended at their caps, no F-hills job queued (squeue);
R16n (F-20261121-130351-04074e1) reached t = 23.34 M (restart 7), R12 (F-20261121-153707-1eaa5d4)
t = 21.06 M (restart 6); the stray resubmissions (4820, 4822) ended by themselves with
"MAX_SEGMENTS reached".

Prediction before the analysis (L7, written before reading any R12 or R16n row past 7.74 M):
rule P1b-D as pre-registered above applies unchanged. I expect D2 to hold: Delta s_16(20) in
0.00-0.06 M (R8: 0.577), masses flat within 1e-4 per M, no step > 0.01 M; and D1 to give a
monotone sequence R8 > R12 > R16n at 15 M with Delta s_12(15) in 0.04-0.15 M. Refuted if
Delta s_16(20) > 0.10 M or the sequence is not monotone; the order p is the uncertain part
(I give p >= 2 an even chance, because the m/16 loss may already be at the 1PN floor).

L7 outcome (analysis run F-20261121-202021-3c4321e; figures `fig_orbit_conv.png`,
`fig_horizons_H.png` read): Delta s at 15 M = 0.3054 (R8), 0.0881 (R12), 0.0865 (R16n) M;
at 20 M 0.5766, 0.1970, 0.1959 M. R12 and R16n agree within 0.0017 M at every time to 21 M
(the m/12 curve lies under the m/16 curve), R8 does not. Member masses of R16n drift -3.9e-5
and -5.5e-5 per M, of R12 -5.0e-5 and -1.4e-4 per M (window 3-15 M); rms H 6e-4 (R8),
1.4e-4 (R12), 4.5e-5 (R16n). Prediction L7: monotone sequence MET; Delta s_12(15) in
0.04-0.15 MET (0.088); D2 FAILED (Delta s_16(20) = 0.196 M against <= 0.10 predicted
0.00-0.06): the m/16 binary shrinks by 0.2 M in 20 M although it is converged.

Rule P1b-D applied as written: R12 has landed, so D1 is the operative clause. D1: monotone
(0.305 > 0.088 > 0.0865), three-point order p = 12.0 (>= 2), Delta s_c(15) = 0.0864 M (inside
-0.02 to 0.12). D1 HOLDS: P1b at m/16 is submitted. D2 (only "if R12 has not landed") would
fail on its first clause (0.196 > 0.10 M; masses flat MET). Reading of the numbers
[JUDGEMENT]: p = 12 is not an order of convergence but the statement that m/12 and m/16 give
the same orbit within 0.002 M, i.e. both are in the converged regime and m/8 is not. The
rule's rationale ("then the m/16 merger time is at least 210 M") is REFUTED: the decay that
remains at m/12-m/16 does not shrink with resolution, and the stretch fit of R12 and R16n to
P1's shape gives a merger at 97 and 93 M (analysis.json "stretch"; it assumes P1's shape).
Two readings are open: (E) the start state (Bowen-York momenta of Newtonian circular
velocities) is eccentric in GR and the pair started near apocentre: s(t) then has a minimum
and rises again within one orbit (phase rate 0.035-0.039 rad/M, period about 170 M); (I) the
converged pair spirals in (coordinate or real) and merges near 95 M. Only a longer isolated
run separates them, so the isolated m/16 binary must run further. It does not run FIRST: it
runs beside P1b in the second card slot and stays ahead of it in simulated time (it starts at
23.3 M and advances about 7.8 M per segment, P1b about 5.5-6.4 M), so a later session can stop
P1b (`scripts/submit_chain.sh --stop`) as soon as the isolated binary merges before the
passage's pericentre; letting P1b wait would leave a card idle for one to two days.

### Card runs loaded in this session (decision 0025 items 4-5; predictions before submission)

A. P1b, m/16 (`binary_conv/inputs/p1b_R16n.athinput`, tlim 200), chain of 31 segments
   (--gpu-hours 31, about 25.9 card-hours; G1 has 31.6 left after R16n and R12 are closed),
   executable `athena_keep_trackers_bc.sh` -> bc-ak05-gpu (byte copy of release core-v0.5's card
   build, the series of R8/R12/R16n; same input options under v0.6, which changes nothing
   without id_solve). No lapse_leak (constant shift_eta = 2, 1+log lapse), as P1.
   Prediction: (A1) no common horizon of the two members before t = 60 M (P1 at m/8: 48.8 M);
   (A2) the members' separation follows the isolated R16n within 0.05 M to t = 20 M;
   (A3) by t = 200 M (or the chain's end, 170-205 M) the binary is separated: one member bound
   to the heavy hole, the other unbound (Newton: m1 ejected, m2 bound with pericentre 5.81 M at
   t = 122; HRNA: m2 ejected; stage/G1/STATUS.md); which member leaves I do not predict;
   (A4) member horizon masses drift below 1e-4 per M; no common horizon of a member with the
   heavy hole; (A5) the tree stays below 2864 MeshBlocks and the run fits 3000 slots.
   Refuted: a member merger before the pericentre (A1, A3), a separation that departs from
   R16n by more than 0.1 M by 20 M (A2), out of memory (A5).
   Criterion to STOP it early (later session): run B shows a common horizon of the isolated
   pair at a time before P1b has passed pericentre.
B. R16n extension (isolated binary, m/16) from R16n's restart 7 (t = 23.34 M) to tlim 120,
   13 segments (--gpu-hours 13, about 10.9 card-hours), new run directory, wrapper
   `athena_resume_bc.sh` (first segment `-r .../F-20261121-130351-04074e1/rst/hills.00007.rst`),
   same executable. Gate G2 (it is also the m/16 rung of the binary ladder; G1 has no room).
   Prediction (reading E, probability about 0.6): s(t) reaches a minimum between 40 and 100 M
   of 2.5-4.6 M and rises afterwards; no common horizon before 120 M; masses drift below
   1e-4 per M. Refuted (reading I): a common horizon before 120 M, or s(t) falling
   monotonically to below 2.5 M.
C. P1b, m/12 (`binary_conv/inputs/p1b_R12.athinput`, tlim 200), 25 segments (--gpu-hours 25,
   about 20.9 card-hours; model 25.1 segments to 200 M, an upper estimate), gate G2: the second
   resolution of the passage (R12 = R16n alone within 0.002 M). Submitted now and HELD
   (scontrol hold); a sequencer releases it when chain B has ended, so at most two F-hills jobs
   are eligible at any time. Prediction: the same outcome as A (A1-A5); the separations of A and
   C agree within 0.02 M to the pericentre; the ejected member's specific energy at infinity
   agrees within 10 percent. Refuted: a different member ejected, or energies apart by more
   than 25 percent.

### Session summary (lead, batch 5)

did: read R8/R12/R16n (registered analysis F-20261121-202021-3c4321e; figures read); applied
rule P1b-D (D1 holds); closed R16n and R12 in nrpic-run; submitted A (P1b m/16,
F-20261121-203144-b2cf16b), B (R16n extension to 120 M, F-20261121-203156-03efdd3) and C (P1b m/12,
F-20261121-203247-961801d, held) with predictions above; started the sequencer
(`binary_conv/scripts/seq_release.sh`, pid in scratch/F-hills/seq/seq.pid); took the digitized
2402 numbers out of git; updated stage G1 (T4 row, OPEN item 1), RISKS (R15, new R19), review.
found: m/12 = m/16 for the binary alone within 0.002 M to 21 M (converged); the converged pair
still shrinks by 0.196 M in 20 M and departs from EIH by 0.17 M; the stretch fit puts a merger
near 95 M. The extrapolation of batch 3 (m/16 survives 210-500 M) is refuted as reasoning.
evidence: F-20261121-202021-3c4321e; finishes of F-20261121-130351-04074e1, -153707-1eaa5d4.
changed my mind about: the decay at m/16 being a resolution effect (it is not: it no longer
changes between m/12 and m/16).
open: runs A, B, C (days of queue); the stop criterion on B; KHSR; p1 to 280 M; note; g2mesh
(its uncommitted card_analysis.py left alone); G1 verifier.
failed predictions this session: L7's D2 clause (Delta s_16(20) predicted 0.00-0.06 M, got
0.196); binary_conv BC-4 item 2 (R16n within 0.05 M of EIH by 20 M: 0.174) and its survival
extrapolation. Met: L7 monotone sequence and Delta s_12(15) range; BC-1 item 2.
card-hours used this session: 0 run; queued 57.7 (A 25.9 G1, B 10.9 G2, C 20.9 G2).

## 2026-11-24T12:55Z lead, batch 11 (analysis round after the card runs; decisions 0026, 0027, 0030)

State at start (04:51 PST, before any tracker, horizon or history row of A, B, C past what batch 5
saw was read): main merged (25684939); pause flag absent; one unacknowledged message (kb,
refutations 766-767). Chains (`scripts/submit_chain.sh --status`, segment logs, sacct):
- A, P1b m/16 (F-20261121-203144-b2cf16b): chain closed FAILED at "MAX_SEGMENTS=31 reached"
  after 32 jobs; newest restart `rst/hills.00023.rst` (t = 61.80 M, segment 15, 2026-11-23
  18:39); segments 9-12 and 16-31 were preempted before writing a restart (another user's
  partition `priority` jobs, 2026-11-22 19:00 to 2026-11-24 04:40, one every 5-30 min). sacct:
  11.77 card-hours over 32 jobs.
- B, isolated m/16 extension (F-20261121-203156-03efdd3): FAILED at "MAX_SEGMENTS=13 reached";
  newest restart `rst/hills.00034.rst` at t = 107.85 M (tlim 120 not reached); 9.28 card-hours.
- C, P1b m/12 (F-20261121-203247-961801d): released by the sequencer at 2026-11-23 14:58 when B
  ended; running (Slurm 5140, segment 21 of 25), newest restart `rst/hills.00006.rst`, last
  logged time 15.52 M; 4.26 card-hours so far; most segments preempted.
- Sequencer (pid 2550221): ENDED normally ("B ended (FAILED): released job 4837 of C",
  2026-11-23 14:58:02); nothing left for it to hold.
- Cause of the cut [VERIFIED by sacct and the segment logs]: preemption by partition `priority`
  (Slurm PreemptMode CANCEL, GraceTime 0) while the restart interval is dt = 5 M (about 45 min
  of wall time at m/16): AthenaK writes no restart on SIGTERM (no signal handler in
  athenak/src), so every segment shorter than one restart interval is lost.

### Predictions of my checks (written before reading the rows; refuted as stated)

- Q1 (B joined to R16n, isolated m/16, 0 to 107.85 M). Batch 5's predictions stand (reading E,
  p = 0.6: a minimum of s(t) of 2.5-4.6 M between 40 and 100 M, then a rise; no common horizon
  before 120 M; masses drift below 1e-4 per M). My own estimate now: reading I (the pair merges)
  has about even odds, because the converged pair lost 0.196 M in 20 M and the stretch fit put a
  merger at 93-97 M. Refuted for E: s(t) falls below 1 M (members' horizons touching, mean radius
  about 0.11 M each... a merger) or falls monotonically below 2.5 M; refuted for I: s(t) has a
  minimum above 2.5 M and rises by more than 0.1 M after it.
- Q2 (A to 61.8 M). A1 (no common horizon of the members before 60 M) MET; A2 (A's separation
  within 0.05 M of R16n to 20 M) MET, A's tidal perturbation by the heavy hole at about 40 M is
  1e-3 of the binary's binding; A4 (member horizon masses drift below 1e-4 per M; no common
  horizon of a member with M) MET; A5 (below 2864 MeshBlocks) MET. A3 cannot be judged (t < 122 M).
  Further: A's s(t) follows B's within 0.1 M to 61.8 M.
- Q3 (C to its newest time, about 15-20 M). C's separation agrees with A's within 0.02 M, as R12
  did with R16n (0.002 M), and C's member masses drift as R12's (-5e-5 to -1.4e-4 per M).
- Q4 (decision). If Q1 shows a merger of the isolated pair at t_m < 122 M (the Newtonian
  pericentre time of member 2; P1's remnant closest approach 154.6 M), A and C cannot test the
  passage: they are closed as stopped and a wider or lighter binary is designed. If not, A and C
  are continued from their newest restart files with a shorter restart interval.

### Outcomes of Q1-Q3 (registered analysis F-20261124-130009-33bef4d; figures fig_b11_binary.png, fig_b11_health.png read)

- Q1, isolated m/16 to 107.85 M: s(t) falls from 4.952 M to a minimum of 3.120 M at t = 73.9 M and
  rises to 4.585 M at 107.85 M (s = 3.977 at 40, 3.151 at 70, 3.712 at 90, 4.278 at 100); the
  orbital phase rate peaks at 0.090 rad/M at the minimum; one orbit of phase (6.47 rad) by 107.85
  M; no common horizon (both finders find their member at every search, 0 failed of 3452); largest
  step of s between rows 1.3e-4 M; member masses drift -1.0e-5 to -5.5e-5 per M; rms H 4.2e-5 to
  6.0e-5, flat. Reading E (eccentric start near apocentre) HOLDS: batch 5's prediction (minimum of
  2.5-4.6 M between 40 and 100 M, then a rise; masses below 1e-4 per M) MET, "no common horizon
  before 120 M" met to 107.85 M only (the chain was cut). My own Q1 estimate (reading I at even
  odds) is REFUTED: the pair does not spiral in; the batch-5 stretch fit (merger at 93-97 M) is
  refuted by the run; risk R19 is retired in its form "the converged pair merges before the
  pericentre". Rough eccentricity from the turning points (4.95, 3.12 M): e = 0.23 [JUDGEMENT:
  coordinate separation in the moving-puncture gauge; the rise after the minimum is faster than
  the fall before it, so the coordinate orbit is not a Kepler ellipse].
- R12 against the m/16 isolated run over the common window (0-21 M): within 0.0021 M (as batch 5).
- Q2, P1b m/16 (A) to 61.86 M: A1 MET (no common horizon of the members; s = 2.74 M at 61.86 M,
  still falling at about 0.05 M per M). A2 MET at the edge: A departs from the isolated m/16 run by
  0.027 M at 10 M and 0.042 M at 20 M (bound 0.05). A4 MET in its first clause for A (member
  horizon masses -5.1e-5 to +3.0e-6 per M in the windows 3-15, 15-40, 40-62 M; heavy hole -6.1e-6
  to +9.1e-6 per M), and no member near M (closest member at 19.98 M). A5 MET (2374-2584
  MeshBlocks, peak card memory 78787 MiB of 81920). A3 not judged (t < 122 M). My added clause "A
  follows B within 0.1 M to 61.8 M" REFUTED: A - B = -0.07 at 30, -0.10 at 40, -0.27 at 50,
  -0.53 at 60 M (largest -0.58 M): the binary closes faster while its centre of mass approaches M
  (r_cm 28.7 M at 20, 25.1 at 40, 21.2 at 60). Cause not named yet: a check in which it can fail
  follows (N1 below).
- Q3, P1b m/12 (C) to 22.30 M (live tracker of the running segment): C within 0.0023 M of A at
  every time (MET, bound 0.02 M). C's member masses drift -1.2e-4 to -1.7e-4 per M (windows 3-15,
  15-22 M): my Q3 range (-5e-5 to -1.4e-4, R12's) is exceeded by one member in one window
  (REFUTED in part), and A4's bound 1e-4 per M, which C was predicted to share, FAILS for C. rms H
  of C 5.1e-5 to 5.5e-5 (A 1.3e-5 to 2.6e-5; B 4.2e-5 to 6.0e-5: the volume norms differ with the
  domain, so only the trend is compared).
- Horizon finders: a band of failed-looking rows remains after the reader's filter (sawtooth of
  up to 4e-3 in m_AH in fig_b11_health); the drifts above are least-squares slopes through it
  [JUDGEMENT: a finder that alternates between two surfaces; not a mass change].

### Q4 decision and the follow-up runs (written before any of them is submitted)

The isolated pair does not merge before the pericentre (Q1), so A and C CAN test the passage: they
are continued, not stopped. Both chains were cut by preemption (state at start), not by physics.
Remedy: the continuations write restart files every 1.0 M (A2, B2) or 1.5 M (C2) instead of 5 M
(command-line `output4/dt`; restart time of the newest files 61.80, 107.85, 20.0 M), so that a
preempted segment loses at most about 10 minutes. Each continuation is a new registered run that
starts from the newest restart file of the cut run (`binary_conv/scripts/athena_resume_bc.sh`,
same byte copy of release core-v0.5's card build `bc-ak05-gpu`, same deck, cfl_number 0.25,
constant shift_eta = 2, no lapse_leak: decisions 0025 item 3 and 0027 item 2 are met). A
sequencer (`binary_conv/scripts/seq_b11.sh`) keeps at most two jobs eligible (A2 and B2 first,
C2 held until B2 ends) and continues a chain that the segment cap cut while its measured card
time (sacct) stays below the card-hours registered for it.

- A2: P1b m/16 from A's restart 23 (t = 61.80 M) to tlim 200, gate G1, 19.5 card-hours (all of
  G1's 19.8 left after A's 11.77). Predictions: (A2-1) the binary passes a minimum separation of
  2.0-2.7 M at t = 63-75 M (B's minimum 3.12 M at 73.9 M; A is 0.53 M closer at 60 M and still
  closing) and the members do not merge (s > 1 M throughout); (A2-2) the centre of mass of the
  pair passes its closest approach to M at t = 95-115 M and r = 8-11 M (Newton 9.81 M at 104.35 M;
  GR turning point 9.25 M, lead V9); (A2-3) by t = 170 M the binary is separated: one member at more
  than 30 M from M with a positive two-body energy with M, the other bound to M with a pericentre
  of 4-8 M; which member leaves I do not predict (Newton: m1; HRNA: m2; the GR binary is eccentric
  and its phase differs from both baselines); (A2-4) no common horizon of a member with M; (A2-5)
  member horizon masses drift below 1e-4 per M outside the encounter, the heavy hole's mass changes
  by less than 1e-3 to 200 M, below 2864 MeshBlocks and inside the card's memory, rms H below 1e-4.
  Refuted as stated in each item; a merger of the members before 115 M refutes A2-1 and A2-3.
- B2: the isolated m/16 binary from B's restart 34 (t = 107.85 M) to tlim 140, gate G2, 5
  card-hours. Prediction: s(t) reaches a maximum (the next apocentre) of 4.65-4.90 M at t = 115-140
  M, below the first one (4.955 M at 5.1 M) by 0.05-0.30 M [JUDGEMENT: Peters' decay of the
  quasi-Keplerian orbit, a about 4.0 M, e about 0.23, m1 = m2 = 0.127: da/dt about -1.2e-3, so
  about -0.16 M in a semi-major axis per orbit, plus a numerical part of unknown sign]; no common
  horizon; masses drift below 1e-4 per M. Refuted: no maximum before 140 M, an apocentre above
  4.95 M (no decay) or below 4.6 M.
- C2: P1b m/12 from C's restart 6 (t = 20.0 M) to tlim 200, gate G2, 24 card-hours, held until
  B2 ends. Prediction as for A2 (A2-1 to A2-4), and against A: separations within 0.05 M up to
  the centre of mass's closest approach (0.0023 M to 22 M so far), the same member ejected, the
  ejected member's energy at infinity within 10 percent. Its member masses drift up to 2e-4 per M
  (it already exceeds 1e-4). Refuted: a different member ejected, energies apart by more than 25
  percent, separations apart by more than 0.1 M before 100 M.

### N1, a reference for A - B (prediction before the run)

Newtonian three-body problem from the start state of the P1 deck (positions, momenta, bare masses;
`stage/G0/checks/lead_checks.py newton_full`) against the same members without M: the difference
of the separations Delta_N(t) = s_3body - s_2body. Prediction: Delta_N(60) between -0.15 and
-0.8 M, i.e. the departure of A from B is tidal at Newtonian order in size and sign. Refuted:
|Delta_N(60)| < 0.1 M or a positive sign; then the departure of A from B is not the Newtonian tide
(a relativistic tidal or a gauge effect would be the candidates, to be tested, not named).

### N1m, a second candidate for A - B (prediction before the registered run)

A test integration of N1 (scratch, not registered; values not used) showed the Newtonian tide
positive at 10-40 M and negative only after about 55 M, while NR's A - B is negative from the
start (-0.027 M at 10 M). Second candidate, from the analysis F-20261124-130009-33bef4d: the
members' horizon masses in A are larger than in B by a factor mu of about 1.015 (0.1295 against
0.1275 at t = 0) at the same bare masses and momenta, because the members sit in the conformal
factor of M (1 + M/2r of about 1.018 at r = 27 M); a binary with heavier members and the same
momenta is more bound and starts nearer its apocentre. Prediction for the Newtonian two-body
problem from the eccentric start of N1e with member masses times mu (N1em): Delta(60) between
-0.15 and -0.6 M, negative from the start; with the tide added (N1emt) within a factor two of
NR's A - B at 20-60 M. Refuted: |N1em(60)| < 0.1 M or positive; then the initial-data mass offset
is not the leading cause.

### Outcomes of N1 and N1m (run F-20261124-132934-375a163; fig_b11_n1_tide.png read)

mu (A's member horizon masses over B's at t = 0) = 1.01495. Delta at 10/20/30/40/50/60 M:
- NR (A - B): -0.027, -0.042, -0.070, -0.104, -0.270, -0.528 M.
- N1 (tide, deck start, Newton circular binary e = 0.033): +0.017, +0.075, +0.155, +0.192, +0.107,
  -0.175 M. N1e (tide, eccentric start, first pericentre 3.12 M, scale 0.866 of the relative
  velocity, e = 0.227): +0.016, +0.077, +0.164, +0.171, -0.064, -0.322 M.
- N1em (members' masses times mu, no M): -0.019, -0.078, -0.173, -0.261, -0.197, +0.004 M.
- N1emt (both): -0.003, -0.001, -0.009, -0.106, -0.311, -0.283 M.
Prediction N1 (Delta_N(60) between -0.15 and -0.8 M, negative) MET for both starts, but the
Newtonian tide is POSITIVE at 10-40 M where NR's A - B is negative, so the tide at Newtonian
order does not reproduce the history. Prediction N1m: "negative from the start" MET (N1em <0 to
50 M), "N1em(60) between -0.15 and -0.6" REFUTED (+0.004: the eccentric Newtonian orbit has
already turned), "N1emt within a factor two of NR at 20-60 M" REFUTED at 20 and 30 M (-0.001
and -0.009 against -0.042 and -0.070), met at 40-60 M (factor 1.0, 0.87, 0.54). Reading
[JUDGEMENT]: the departure of A from B is of the size of the two Newtonian effects together
(tide plus the members' heavier horizon masses in M's conformal factor) at 40-60 M; the early
part (-0.03 to -0.07 M at 10-30 M) is not explained by either; the Newtonian clock does not match
the NR coordinate clock (the NR pair's minimum is at 73.9 M, the Newtonian eccentric one at 50 M),
so a time-by-time comparison is weak. No cause is named. What the runs do establish: A - B is not
a resolution effect to 22 M (C at m/12 = A at m/16 within 0.0023 M, F-20261124-130009-33bef4d).

### L-K, the lead's rerun of khsr_note's check (prediction before the run)

`khsr_note/scripts/fig_khsr.py` on the registered scan F-20261121-212757-77cdc15 reproduces the
committed `khsr_note/results/khsr_checks.json` in every number (deterministic script, same
input). Refuted: any value different beyond 1e-12 relative.
L-K outcome (run F-20261124-133112-db7d6b8): 1268 values of khsr_checks.json, 0 differences: MET.
The figure `fig_khsr_ecc.png` (read): prograde ejection probability falls from about 0.98 to
0.53-0.55 between r_a/r_t = 500 and 100 at D <= 0.5, the primary/secondary preference falls to
0.08-0.15 at 100, the mean ejection energy falls with r_a/r_t; as ms.tex:756-769 states. K1 and K2
rederived by hand (STATUS T1): E_bar = -(m^2/(m1 m2)) (M/m)^(1/3) / (2 r_a/r_t) = -2.667 for
r_a the semi-major axis; times to pericentre from r0 at r_p = r_t: parabola from 15 r_t 29.98;
ellipse e = 0.9 (a = 10) E = 1.82, r0 = 12.22; hyperbola e = 1.1, H = 1.5635, r0 = 17.40.

### Card runs loaded in this session (predictions above, "Q4 decision and the follow-up runs")

- A, C closed in nrpic-run as stopped (finish F-20261121-203144-b2cf16b: 11.77 card-hours,
  147.6 GB checksummed in 66 min; F-20261121-203247-961801d: 176 files). B (F-20261121-203156-03efdd3)
  is closed after them (background finish; HANDOFF).
- B2 F-20261124-135408-1e6db58 (G2, --gpu-hours 5: 5 segments), Slurm 5171, from B's restart 34,
  tlim 140, output4/dt = 1.0.
- A2 F-20261124-141118-fbc6419 (G1, --gpu-hours 19.5: 19 segments, 18.7 card-hours; announced
  here and in STATUS.md, decision 0014), Slurm 5172, from A's restart 23, tlim 200, output4/dt = 1.0.
- C2 F-20261124-141842-d5263e9 (G2, --gpu-hours 24: 24 segments), Slurm 5173 HELD, from C's
  restart 6, tlim 200, output4/dt = 1.5.
- All three: `binary_conv/scripts/athena_resume_bc.sh` -> bc-ak05-gpu (byte copy of release
  core-v0.5's card build, as A, B, C), cfl_number 0.25, constant shift_eta = 2, no lapse_leak.
- Sequencer `binary_conv/scripts/seq_b11.sh` started 06:18:51 PST, pid 604718 (setsid nohup),
  table scratch/F-hills/seq/b11.table, log scratch/F-hills/seq/seq_b11.log: holds C2 until B2 has
  ended for good, then releases it; continues A2, B2, C2 in place when their segment cap cuts them
  while their sacct card time is below 19.5, 5.0, 24.0 card-hours. A dry pass on A, B, C (old
  chains) and on the new table logged the expected actions (scratch/F-hills/tmp/seqdry).
