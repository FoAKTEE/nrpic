# G0 scoping document of F-hills (S12: the Hills mechanism with NRPIC)

This is the G0 package's main document (the task asked for it as `REPORT.md`; the write tool of
the session refused that file name, so it lives here). Owner F-hills, branch `track/F-hills`,
written by the lead on 2026-11-15 after four helper packages (`novelty/`, `newton3/`,
`geodesic_binary/`, `three_punctures/`) and the lead's own checks (`checks/`, runs V1-V7 in
`../../JOURNAL.md`). Artefacts and run ids: `EVIDENCE.md`; what the gate still lacks:
`OPEN.md`. Units G = c = 1; M is the mass of the heavy hole (r_g = M), m_b the total binary
mass, q = M/m_b, a_b the binary separation, r_t = a_b q^(1/3) the tidal radius,
D = r_p/r_t. Labels: [VERIFIED] read at the locator given or measured in the registered run
given; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY]. "Lead-checked": re-run or re-derived by the
lead from the artefacts.

**Amended 2026-11-21 (lead, batch 2a) after the verifier's report `VERIFIER.md`.** Every
WRONG or PARTLY item of its sections 1 and 3 was checked at the source (`../REVIEW-wave3.md`,
lead runs F-20261121-063504-00f0743, F-20261121-063712-25981e0) and is corrected in place,
marked "[amended: D<n>]": D1 GR turning points beside every r_p (sections 3, 6); D2 the V7
percentages only with their construction (section 4); D3 the G2 sum (section 9); D4 q = 4 for
the first passage (sections 3, 6, 9; decision 0013); D5 slot limit against card capacity
(section 9); D6 the plunge bound is a condition for deep encounters (section 4); D7 the
geodesic model's consistency parameter (sections 4, 11); D8 KHSR (sections 5, 7). Section 6
also records the outcome of the first passage P1 (the binary merged at t = 48.8 M).

## 1. Problem statement

A bound binary on a near-parabolic orbit passes a heavier black hole with pericentre r_p of
a few to about fifteen r_g, comparable to its tidal radius. With this repository's AthenaK
(decision 0010: vacuum Z4c with several moving punctures for object (a), NRPIC particles for
object (b)) we compute whether the binary is separated, the energy given to the ejected and
to the captured member, the fate of the captured member (bound, or plunging into the heavy
hole), the gravitational-wave burst, and for matter members their stripping and heating.
Each run is compared with two reference solutions of ordinary differential equations that
live outside the source tree: the full Newtonian three-body problem at the same masses
(F-pre-1, `newton3/`) and the "exact Schwarzschild or Kerr acceleration plus Newtonian pair
force" model of arXiv:2404.16270 (HRNA, F-pre-2, `geodesic_binary/`). The minimum publishable
unit (brief l. 487) is one scan line in r_p at q of order 10 for objects (a) and (b), with
separation boundary, energy split and waveform against both references.

Novelty (F-pre-5, `novelty/NOVELTY.md`, search of 2026-11-15 with its limits): no full-NR
calculation was found in which a heavier hole (q > 1) separates a binary on a near-parabolic
orbit with pericentre at or inside r_t, and no full-GR calculation of a matter binary
passing a black hole. Three-hole NR exists for equal masses (0710.0879, 0711.1165,
2505.03934) and for binaries bound to a 4 or 9 times heavier hole outside its tidal radius
(2406.11985). [JUDGEMENT on an absence; checked by two further agents: `SECOND_CHECK.md` (31 INSPIRE
queries, forward-citation lists) and `VERIFIER.md` K1 (12 kb queries, candidates read at the
source); both confirm it within their limits. Nearest full-NR work to cite as well: 2605.20320,
three holes from rest, non-disruptive by construction (orch, `coord/FRONTIER.md`)]

## 2. Objects (decision 0005) and what the lead proposes

| object | needs from core | state | proposal |
|---|---|---|---|
| (a) binary black hole + heavy hole, vacuum | Bowen-York punctures with momentum, N trackers and finders | `core/multi-puncture`, interface PROPOSED, tests 1-3 run, not on `main`, not listed in `CLAUDE.md` | first passage at G1 (section 6) |
| (b) binary of collisionless clumps + heavy hole | moving equilibrium clump data (momentum curvature), the puncture of (a) | spherical extrinsic-curvature tables on `core/id-extrinsic`; moving clumps not started | first (b) passage right after the first (a) passage, not after the (a) scan [JUDGEMENT: cheaper per passage and the regime only NRPIC reaches] |
| (c) dressed binary | Track D's dressed data | not started | after (b) |

Keep 0005 as written ((a), then (b), then (c)), with the change of timing above.

## 3. Parameter ranges

| parameter | range | first values | basis |
|---|---|---|---|
| q = M/m_b | 4 to 10 | 4 for the first passage, the convergence study and the first scan line; 10 when the mesh fits [amended: D4] | brief l. 487, 806; decision 0013; cost section 9 |
| member masses | equal | m1 = m2 | the references scan equal members |
| a_b/r_gb | above the plunge bound 4 q^(2/3): 10.1 (q = 4), 18.6 (q = 10), 38.6 (q = 30) | 30 (q = 10, a_b = 3 M, r_t = 6.46 M); 20 (q = 4, a_b = 5 M, r_t = 7.94 M) | run F-hills-20261115-045435-f62d553, lead-checked (V3) |
| r_p | from 4 M (plunge of the centre of mass) to about 2.1 r_t (Newtonian prograde edge) | q = 10: 7 to 13 M (D = 1.08 to 2.01); q = 4: 9.8 to 16 M (Newtonian conic; every value is reported with its GR turning point, below) | 0911.1136 prp.tex:846-847; lead scan V7 |
| orientation | coplanar prograde first; then retrograde; one inclined later | prograde | retrograde survives more (prp.tex:740-742) |
| phase | one per run, inside a phase window that is robust in both references | 130 deg effective phase (q = 10, r_p = 8) | three_punctures run F-hills-20261115-130342-0471114; V6, V7 |
| start | 4 r_t (tidal over binding 0.031); a start at 10 r_t keeps 95-97 percent of outcomes against 40 r_t, 5 r_t only 90 percent | 4 r_t, with the Newtonian state integrated from 10 r_t; the NR data and BOTH references of a scan line start from this same state [amended: D2] | newton3 P4, run F-hills-20261115-131801-907e5fe |
| spin of the heavy hole | 0, later +-0.6 | 0 | deliverable 5 |
| domain, wave spheres | +-204.8 M (q = 10), +-256 M (q = 4); spheres 40, 48, 70, 90 M | as in `three_punctures/inputs/` | three_punctures PLAN section 4 |

Definition of r_p [JUDGEMENT]: a parameter of the initial data (pericentre of the Newtonian
centre-of-mass conic of the start state), reported together with the Schwarzschild
pericentre of the same E and L; tracker distances are gauge-dependent diagnostics.
[amended: D1] The GR reading used is that of the puncture data (isotropic coordinates,
u_i = P/m, the heavy hole's static frame): the q = 4 start state (conic 9.81 M) turns at
areal 9.25 M (D_GR = 1.17), the q = 10 state (conic 8.00 M) is bound to M (E = 0.99925) and
turns at 5.77 M (D_GR = 0.89, not 1.24) [VERIFIED: lead V9 run F-20261119-145449-245e984,
verifier R1 run F-20261121-030100-b88c2d3, second check SC7]. A scan line meant to be equally
spaced in depth is built from a GR parabola, L = (2 r_p^2/(r_p - 2))^(1/2) M, in this reading,
and the q = 10 input is rebuilt that way before it is run (RISKS R9).

## 4. The scale estimate of brief l. 275, its correction, and what is new

Lead-checked (V3: run F-hills-20261115-144954-b5b0bce reproduces the helper's 905 numbers;
algebra redone by hand): r_t/r_g = (a_b/r_gb) q^(-2/3); separation before the plunge of a
parabolic Schwarzschild orbit (r_mb = 4 M) needs a_b/r_gb > 4 q^(2/3) = 18.57, 86.18, 400.0
for q = 10, 100, 1000; the Peters time (5/64)(a_b/r_gb)^4 G m_b/c^3 is 6328 GM/c^3 at
a_b = 30 r_gb, q = 10, against a passage of 160 to 290 GM/c^3. [VERIFIED] Correction (outbox
to orch): the box "q = 10-30 and a_b = 20-60 r_gb" of l. 275 is partly below the plunge
bound (a_b >= 38.6 r_gb at q = 30, >= 29.5 at q = 20). [amended: D6] That bound, r_t > 4 M,
is the condition for deep (D <= 1) encounters outside the plunge radius of the centre of mass,
not for separation: restricted encounters separate binaries out to D = 2.085 (prograde), so
with the centre of mass outside 4 M separation is possible down to a_b/r_gb = 4 q^(2/3)/2.085
(14.1 at q = 20, 18.5 at q = 30) [VERIFIED arithmetic, lead run F-20261121-063504-00f0743].
The whole box of l. 275 lies above that weaker bound (its corner q = 30, a_b = 20 at the edge);
the member-plunge result below is the stronger reason why its shallow part gives few clean
separations. Errata row 1.5 is to be reworded (outbox to orch, 2026-11-21).

New at this gate (lead runs V6, V7): the plunge bound applies to the centre of mass, but each
member carries the binary's internal speed (0.09 c at a_b = 30 r_gb). In the geodesic
reference a member crosses r = 2.5 M in 94 percent of the phases at r_p = 8 M and still in
69 percent at 12 M (q = 10, prograde, 180 phases), where the full Newtonian problem has no
member inside 4 M in 94 percent of the phases at 8 M. At r_p = 13 M (D = 2.0) HRNA separates
98 percent of the phases, Newton 22 percent. [VERIFIED as model outputs, run
F-hills-20261115-145915-71abf93, figure `checks/figures/fig_v7_rp_scan.png`; JUDGEMENT on what
NR will do] [amended: D2] These percentages hold for V7's construction only: a fresh circular
binary released at 4 r_t, the geodesic model with the centre of mass on the Schwarzschild
parabola (the verifier reproduced them that way within 2 sigma, runs F-20261121-040103-6b9074c,
F-20261121-040112-d429b4c). With the start rule of section 3 (state integrated from 10 r_t) the
numbers at r_p = 12-13 M change by factors 2 to 10 (plunge fraction 0.22 or 0.65 at 12 M, 0.02 or
0.16 at 13 M, Newtonian separated 0.42 at 13 M; runs F-20261121-030146-34ad97e,
F-20261121-031920-5e6425e, F-20261121-034434-0113a18), so near the separation edge they are
properties of the construction; the result "the two references disagree in kind" (a member
plunging in the geodesic model, none inside 4 M in Newton) holds at r_p = 7-8 M (q = 10) and
9.82 M (q = 4) in every construction tried. They are not to be quoted for r_p >= 12 M without
the construction. HRNA's own consistency parameter a_b/R_curv is 0.13 at r = 8 M and 0.06 at
13 M for the binary as released (2404.16270 article.tex:272-274), as large as in the paper's own
examples (appendix.tex:8); [amended: D7] at the pericentre of a deep encounter, when the pair is
coming apart, it reaches 0.2 (S1 scan, beta = 10, lead run F-20261121-063504-00f0743), so the
geodesic reference is at the edge of its validity in exactly the regime of the first passages;
its other weak point here is the fixed hole at q = 10. So the strong-field Hills regime at q = 10
is, in the geodesic reference, mostly "one member ejected, the other plunging", and the two
references disagree in kind: the first NR passage tests exactly this.

## 5. Exit criteria

- G0 (this package): verdict of the novelty search with limits; parameters; test plan;
  key references checked at the source (section 8); risks; compute estimate; the lead's
  check of the helper packages (section 10). Decision 0005 confirmed with the timing change
  of section 2; the allotment question put to the orchestrator.
- G1 (track sheet l. 818, made concrete; state in `../G1/STATUS.md`): (i) F-pre-1 reproduces
  0911.1136 and 1804.02911 (P_dis(D) within binomial and digitising error, energies within
  2 percent, both orientations); (ii) F-pre-2 reproduces 2404.16270 (separation fraction
  within 0.03 of its figure, mean v_inf within 2 percent); (iii) three-puncture data at
  t = 0: Hamiltonian residual for `approx`, `none` and plain sum, and the junk energy of a
  member-like puncture (P/m = 0.28) at R >= 40 m, two radii agreeing within 20 percent;
  (iv) one complete vacuum passage (section 6): all horizons found in every search until a
  merger, trackers until t = 200 M, outcome (separated, plunged, captured) stated with the
  constraint norm. [amended: D8] The track sheet's F-pre-1 also names 1201.4794 (KHSR); no
  KHSR result is reproduced yet (only its energy combination is used, newton3/README.md:46-50).
  Plan: reproduce one KHSR result at G1 (the dependence of the ejection on the eccentricity of
  the centre-of-mass orbit, ms.tex:1140-1152, newton3 driver with `e_orb`, processor minutes);
  until then (i) is met for 0911.1136 and 1804.02911 only.
- G2: the passage at large pericentre (D >= 2.2 at q = 4) returns to both references
  (survival; internal energy change within the difference of two resolutions); three
  resolutions (m/8, m/12, m/16) of one passage at q = 4; the rerun of 0710.0879's 3BH1
  (radiated energy (6.06 +- 0.02)e-3 M, first.tex:291) within 5 percent; for (b), the
  numerical relaxation time of one isolated clump at least ten times the passage time
  (about 200 M), measured on the passage mesh.
- G3: two scan lines (a) and (b) of 5 to 6 r_p each, three-way convergence (particle
  number, mesh, gauge or boundary) at one r_p per line, the separation boundary as an
  interval, the energy split, the fate of the captured member and the waveform.

## 6. The first vacuum passage (named for G1; full specification in `../G1/STATUS.md`)

[amended: D4] Decision 0013 moved the first passage to q = 4: P1 is
`nr_first/inputs/p1_q4.athinput` (M = 1, m1 = m2 = 0.125, a_b = 5.111, e_b 0.033, conic r_p 9.81 M,
GR turning point 9.25 M, start 31.75 M = 4 r_t, members at m/8), run F-20261119-150017-b45ec5f.
Outcome so far [VERIFIED: p1 run F-20261120-223252-ca18a81 and the lead's own parser, run
F-20261121-063449-4dcca98]: the binary MERGED at t = 48.8 M, 24.9 M from M and long before the
pericentre (common horizon 0.268 M from t = 48.8); the remnant passes M at 7.0 M coordinate
distance at t = 155 M. No reference has a merger (Newton, HRNA and EIH keep the binary at
3.7-7 M separation; the gravitational-wave inspiral time is about 3400 M); the cause is most
likely the members' resolution at m/8 [JUDGEMENT, TO VERIFY with the isolated binary at m/8 and
m/16]. The paragraph below is the wave-1 plan of the q = 10 passage, kept as the record; that
input turns at 5.77 M in GR and is rebuilt from a GR parabola before any q = 10 run (D1).

Input `three_punctures/inputs/hills_q10_m8.athinput` (helper; lead-checked V5): M = 1,
m1 = m2 = 0.05 bare, a_b = 3.036 (e = 0.029 after the tidal approach from 10 r_t), coplanar
prograde, centre-of-mass conic r_p = 7.9965 and e = 1.00006, start at 4 r_t = 25.85 M,
effective phase 130 deg; `corr = approx`, `puncture_setup`, members at m/8 (cells 0.00625,
level 10 of 11), domain +-204.8. Predictions: full Newton from the same state: m1 ejected
with +1.613 units (2.90e-3 M; unit (m1 m2/a_b)(M/m_b)^(1/3) = 1.795e-3 M), m2 bound to M with
a = 7.55, e = 0.247, pericentre 5.68 M; HRNA from the same state relative to M: m1 crosses
r = 2.5 M at t = 97 M (its first pericentre), m2 ejected with +1.16 units (+0.69 in the 2404
construction). [VERIFIED as model outputs, runs F-hills-20261115-145251-090f5dc,
-145559-a314517] Cost 32 to 36 card-hours to t = 200 M.

## 7. Test plan mapped to the rows of brief section 10 held by F (l. 857-859)

| row | reference | test and acceptance | state |
|---|---|---|---|
| Hills scattering in the restricted three-body problem | 0911.1136, 1804.02911 (and 1201.4794) | coplanar P_dis(D), max and mean energy against SKR text and figures; isotropic P_dis against the BKRS fit; full three-body limit; start-radius and tolerance convergence | done (newton3 P0-P8); independently reproduced by the lead at nine (sense, D) points (V4, V4b); open: retrograde disruption criterion (edge 0.41 against SKR 0.44, reproduced only with SKR-like counting H1), eccentric binaries, KHSR non-parabolic orbits |
| Geodesic binary passing a Schwarzschild black hole | 2404.16270 (Kerr: 2402.02178) | single-body limit against `python/nrpic`; time-dilation test of 2404 appendix B; six printed encounters; separation fraction and v_inf curves; coordinate independence; tolerance and release radius | done for Schwarzschild and equatorial Kerr (geodesic_binary T1-T4, S1-S4, C1-C2; T1-T4 re-run by the lead, V2); open: 2402.02178 not reproduced (needs inclined orbits), 1PN law, cause of the r0 dependence |
| Three-puncture vacuum evolution | 0710.0879, 1004.1353 | (i) t = 0 residual, three variants (R0, processors); (ii) junk of one member-like puncture at R = 40-80 m (R2) and the member gauge (R4); (iii) the first passage (section 6); (iv) G2: rerun of 0710.0879's 3BH1 (data table first.tex:156-179; same kind of approximate data as `corr = approx`, 0711.1165) | not started: needs `core/multi-puncture` released (outbox to core and orch) |
| added: two-body and single-member limits | the binary alone; one light puncture on the parabola | eccentricity drift of the binary without the heavy hole; deflection of one member against the Schwarzschild geodesic | G2 |
| added: clump in isolation (object b) | equilibrium model of Track C or core | relaxation time >= 10 passage times | G2, after core's moving-clump data |

Figures exist for every test that ran (`newton3/figures/`, `geodesic_binary/figures/`,
`three_punctures/figures/`, `novelty/figures/`, `checks/figures/`); the lead looked at each
one relied on here.

## 8. Key references: statements verified at the source by the lead

| statement | locator (kb-data/raw/arxiv/...) |
|---|---|
| r_t = a (M/m)^(1/3) | 0911.1136/v1/src/prp.tex:85-88 |
| restricted parabolic equations and f(t) | prp.tex:229-259 (implemented independently in `checks/lead_checks.py`, V4) |
| member energy in units (G m1 m2/a)(M/m)^(1/3), E2 = -E1 | prp.tex:345-357 |
| start at 10 r_t "sufficient for convergency" | prp.tex:597-599 (newton3 P6: converged only at 40 r_t; up to 2.2 points off at 10 r_t) |
| radial survival 19 percent; survival windows | prp.tex:748-749, 784-785 |
| D_max 2.1 / 0.44; E_max 27.3 / 1.8; most disruptive D = 0.15 | prp.tex:846-854 |
| isotropic plateau 88 percent; P_dis fit coefficients; accuracy 1 percent for D <~ 1 | 1804.02911/v1/src/mnras.tex:368-379 |
| relativistic effects for r_p below about 100 r_g | 2404.16270/v1/src/article.tex:194 |
| HRNA equation of motion in coordinate time (1/(m Gamma^2) on the pair force) | article.tex:244-256 |
| HRNA consistency alpha = a/R_curv, R_curv = (r/r_g)^(3/2) r_g; alpha about 0.1 at pericentre in the paper's examples | article.tex:272-274; appendix.tex:6-8 |
| full NR "intractable" for the binary-plus-Kerr problem | 2402.02178/v1/src/main.tex:224-225 |
| 8:1:1 and 18:1:1 bound triples; "could be continued ... until 128:1:1" | 2406.11985/v1/src/TBH3.tex:703-711; `massratio_table.tex` (q = 4.0, 9.0; a_b = 9.9 r_gb; D/r_t = 4.1, 5.8 by the lead's arithmetic) |
| three equal holes, 11 levels, h = M/80, boundary 640 M; E_rad = (6.06 +- 0.02)e-3 M for 3BH1 | 0710.0879/v2/src/first.tex:141-146, 291 |
| approximate data: finite error that does not converge; solving the constraint can change the evolution "dramatically"; junk differences ten times larger | 1004.1353/v2/src/Punc_N.tex:185-194, 1238-1261 |
| one global time step, dt = cfl x finest cell | athenak/src/mesh/mesh.cpp:595-666, athenak/src/z4c/z4c_newdt.cpp:45-58 |

Further locators used by the helpers (not re-read by the lead) are in
`newton3/hills3/reference.py`, `geodesic_binary/README.md`, `three_punctures/PLAN.md`
section 2 and `novelty/NOVELTY.md`. [The statements of this table were re-read at the source by
the verifier (VERIFIER.md K2, K3, K5, K17, K19); the helpers' further locators are not.]

## 9. Compute estimate on this machine

Measured basis [VERIFIED]: vacuum Z4c on one A100 runs 2022 to 2310 MeshBlock-cycles per
second with 16^3 blocks and RK4 (novelty run F-hills-20261115-045438-f62d553; core's three-hole
run 2140); one global step dt = 0.25 h_min (section 8); MeshBlock trees of the Hills meshes
measured with the processor executable (three_punctures runs F-hills-20261115-131109-634fb86,
-131348-634fb86; core's 1100 MeshBlocks of `by_triple` reproduced exactly); card memory about
22 MB per MeshBlock slot plus 2 MB per finder, about 3000 slots per card (core interface,
section 5); no MPI in the build (`scripts/README.md` l. 4).

| case | MeshBlocks start / max / mean | card-hours |
|---|---|---|
| (a) q = 10, m/8, 240 M | 1800 / 2332 / 2006 | 38.9 (37.0-42.3); +11 percent if the AMR adds blocks as in core's test 3 |
| (a) q = 10, m/8, to t = 200 M (the G1 run) | as above | 32-36 [JUDGEMENT: 200/240 of the above] |
| (a) q = 10, m/16 | 2654-4544 | 99-156; no margin on one card |
| (a) q = 4, m/8, 270 M | 1716 / 2080 / 1744 | 15.2 (14.5-16.5) |
| (a) q = 4, m/16 | 2514 / 2864 / 2568 (radius 1.8 of the inputs; corrected 2026-11-19, run F-hills-20261115-131933-907e5fe; the first print, 2416 / 2654 / 2348 and 41, was the radius-1.2 row) | 44.8; [amended: D5] 2864 is above the slot LIMIT 2700 of the smoke input, not above the card: 26.2 MiB per slot with three finders gives about 3100 slots on 81920 MiB (core-v0.4 `coord/INTERFACES/multi_puncture.md:235-247`), so it may run on one card with `max_nmb_per_rank` near 2950-3000 [TO VERIFY by a short card run, package g2mesh] |
| (a) P1, q = 4, m/8, measured | 1016-1870 (the members merged at t = 48.8 M) | 0.835 per 50-min segment, 13-18 M of evolution each; about 13 card-hours to 280 M (p1 ledger, run F-20261120-223252-ca18a81) |
| (b) q = 10 clump binary, one passage | about 1000 (model) | 1.8-3.7 (model); 2.8-9 with the tree correction and cluster-run cells [JUDGEMENT] |
| R0 (t = 0, three variants) | 1800 | processors, minutes, about 70 GB of host memory each |
| R2, R4 (one puncture, P/m = 0.28) | about 1200 | about 1 each [JUDGEMENT] |

The novelty helper's model (23.6 card-hours for q = 10 at m/8) is superseded: its MeshBlock
counts were 1.5-2.4 times low (three_punctures runs above). Programme [JUDGEMENT]: G1 about
36-40 card-hours (fits the 40 of decision 0006 with no margin) [amended: D4, D3: stale; the
first passage is P1 at q = 4, about 13 card-hours, and decisions 0014 and 0016 allot 50 to G1
and 120 toward G2]; G2 as first listed (q = 4 resolution triple 15 + 28 + 41, two large-r_p
passages 30, the 3BH1 rerun about 12, clump relaxation about 5) sums to 131 card-hours (135 with
the m/16 cost of 44.8) BEFORE contingency, not "about 120" [VERIFIED arithmetic, lead run
F-20261121-063504-00f0743]. Corrected G2 plan [JUDGEMENT]: the q = 4 triple (about 12 + 22 + 45
with P1's measured m/8 cost), one large-r_p passage (15), clump relaxation (5): about 100,
leaving about 20 for contingency inside the 120; the second large-r_p passage and the 3BH1
rerun move to G3. P1's merger (section 6) may change the member resolution of the whole ladder
(m/8 may not hold a binary): the triple is re-costed once the isolated-binary test has run.
G3 about 500 for two lines at one phase per r_p with one
convergence triple each, several times more with phase sampling. G2 and G3 exceed the
allotment 3 to 12 times: request in the outbox to orch. Wall time: one card gives at most
24 card-hours a day; the G1 passage needs about two days of one card in one-hour chained
jobs.

## 10. Lead's check of the helper packages (details: `../../JOURNAL.md`, lead session)

| package | confirmed by the lead | not confirmed | wrong (fixed or listed) |
|---|---|---|---|
| novelty | scale estimate and Peters time (V3, algebra redone); 2406.11985 configurations and the 128:1:1 sentence at the source; 2402.02178 "intractable" at the source | the verdict itself (a search cannot be re-run identically; second agent needed); the Roche-lobe factor 0.38 (from memory, BACKGROUND) | cost model 1.5-2.4 times low in MeshBlocks (superseded, listed); its fiducial r_p = 6 M rejected (a member inside 4 M in 87 percent of phases) |
| newton3 | 10/10 tests (V1); restricted coplanar P_dis and energies at nine (sense, D) points by independent code (V4, V4b); SKR and BKRS locators of section 8 | P2-P8 numbers beyond those nine points (not re-run); BKRS collision probabilities | member energies at finite q are two-body energies with M alone and are not conserved when the other member stays bound: E1 oscillates by +-0.19 units (q = 10) and +-0.37 (q = 4) (V5b); the conserved values of the chosen configurations are +1.613 and +1.312, not +1.75 and +1.53. Affects the energies (not the outcome classes) of `fig_finite_q`, P3 at M/m <= 100 and the three_punctures scans; listed for the next wave. Cosmetic: legend typo "retgrade" in `fig_skr_curves` |
| geodesic_binary | T1-T4 re-run with the same numbers (V2); HRNA equation at the source; the model reused by the lead for V6 and V7 | S1-S4, C1, C2 (not re-run); the digitised comparisons (third-party curves stay in scratch) | none found; open items as the helper lists them (2402.02178, 1PN, r0 dependence, the rotation reversal of article.tex:424-425) |
| three_punctures | the start state of both inputs (momentum 1e-10, conic r_p 7.9965 and 9.809, binary a 3.036) and the Newtonian fate (m2 bound, pericentre 5.68, closest 5.64) by independent integration (V5); the cost arithmetic (MeshBlocks x cycles / rate); one global step in the source | MeshBlock trees (not re-run; an emulation with `athena -m`); the junk-energy analysis of core's runs (factor-ten disagreement with core stays open) | E1 values from newton3's energy (above); commit 0fae693 carries two sibling manifests (contents unchanged, listed); `fig_junk` y-labels clipped (cosmetic) |

The lead's new results V6 and V7 (section 4) change the expected outcome of the first passage
from "Hills ejection and capture" to "a test between capture (Newton) and plunge (HRNA)".

## 11. Risks (full table in `../../RISKS.md`)

Compute (G2 and G3 beyond the allotment; q = 10 convergence not on one card); the core
capability not released; the member gauge (eta m = 0.1) and the tracker lag; a 20:1 merger at
m/8 if a member plunges; approximate data changing the outcome (1004.1353); chaos near outcome
boundaries (2505.03934); HRNA and Newton disagreeing in kind, so neither is a truth at q = 10;
competition (RIT towards 128:1:1). [amended] Added 2026-11-21: the binary of the first passage
merged before the passage at m/8 (section 6; probably resolution); the geodesic reference is at
the edge of its own validity at the pericentres of the first passages (D7); the reference
percentages near the separation edge depend on the start construction (D2).
