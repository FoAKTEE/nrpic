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
