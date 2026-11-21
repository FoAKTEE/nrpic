# JOURNAL of package kerr (track F-hills, wave 3 round 1)

F-pre-2 for Kerr: reproduce or refute a statement of arXiv:2402.02178 with the HRNA of
`../geodesic_binary/hrna.py`; test HRNA's spurious self-acceleration (R3). Predictions are
written before the runs; outcomes are appended, failed predictions included.

## Entry 0 (2026-11-20 22:30 UTC): sources, statements, model differences, choice

Read: `CLAUDE.md`, `harness/RULES.md` (nrpic-run), `geodesic_binary/README.md`, `hrna.py`,
`analysis_kerr.py`, `tests/t2_geodesic_limit.py`, `stage/G1/STATUS.md` row T2, `stage/G1/OPEN.md`
item 3, `stage/G0/SECOND_CHECK.md` SC0d (l. 226-244), run F-20261115-175620-df20ffe
(`flat_binary.json`), `python/nrpic/kerr.py` (invariants, carter_q, radial_roots), `geodesic.py`,
and the source of arXiv:2402.02178 (`kb-data/raw/arxiv/2402.02178/v1/src/main.tex`, all 970
lines; figure files parsed as data with `scripts/digitize_2402.py`, rendered once to PNG in
`scratch/F-hills/tmp/kerr/paperfig/` to look at them, never committed).

Environment [VERIFIED]: the worktree `.venv` has no numba (`import numba` fails), which
`hrna.py` needs. All runs use `/data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python`
(numba 0.68.1, scipy 1.18.1, numpy 2.5.4), the interpreter of the geodesic_binary runs and of
SC0d; nrpic-run records its checksum. Request to the lead: numba into the track's requirements.

### The model of 2402.02178 [VERIFIED, main.tex]

- Outer orbit: Kerr geodesic in BL coordinates, E = 1, given r_p and L_z; Q from Eq. (rp)
  (l. 357-362), L_z range from Q >= 0, Eq. (Lz) (l. 368-372). CM starts in the equatorial plane
  at r_ini = 100 M (l. 495-502); L_z uniform in the allowed range (l. 491-494).
- Binary: in the Fermi frame of that geodesic, Newtonian self-gravity plus PN terms to 2.5PN plus
  the gravito-electric tidal force -m R_0i0j x^j (Eqs. eom, F, E; l. 309-341); gravito-magnetic
  forces neglected (l. 401-411). CM on the geodesic by construction.
- Fiducial: M = 4e6 Msun, s = 0.9, m1 = 15, m2 = 10 Msun (l. 486), a0 = 20000 m12, circular
  (l. 504-509), beta = r_t/r_p = 0.6786 (l. 513-515) [VERIFIED by arithmetic: m12 = 6.25e-6 M,
  a0 = 0.125 M, r_t = (M/m12)^(1/3) a0 = 6.786 M]. iota = angle of the binary's angular momentum
  to the rotation axis of the local inertial frame (l. 516-518); retrograde = iota > pi/2.
- Not given: the binary's node and phase ("keeping the other parameters fixed", l. 925-931), the
  sign of u_theta at release, the outcome criterion (a_fin = 0 for a disrupted binary in Fig. afin).

### Checkable statements

| id | statement | locator | quantities | HRNA can test |
|---|---|---|---|---|
| K1 | survival boundary iota_c(beta) for four families: s = 0.9 equatorial L_z > 0, L_z < 0, s = 0.9 L_z = 0 (polar), s = 0 (shaded); beta = 0.34-1.13 via r_p = 20..6 M at fixed a0 | Fig. InclD, l. 582-605 | digitized marker positions (iota on a pi/6 grid) | yes, after the extension (inclined binary; polar CM orbit needs Q) |
| K2 | "good agreement [with the Newtonian criterion, Eq. cosiN] in most cases; significant deviation when beta > 0.9 for s = 0.9, L_z < 0: the relativistic BBH is more stable than the Newtonian one" | l. 586-593 | sign of the departure from Eq. cosiN (l. 572-577) | yes (same runs as K1) |
| K3 | at r_p = 10 M survivors reside mostly at iota >~ pi/2; L_z plays a minor role; near L_z = 4 M and -5 M more binaries are disrupted | Fig. afin, l. 524-526, 540-541, 558-562 | survival map 48 L_z x 36 iota (a_fin/a0 from cell colours) | yes, after the extension (inclined CM orbits, Carter constant) |
| K4 | e_fin > 0.5 near iota = pi/2; e_max >= 0.4 for most survivors | Figs. efin, emax, l. 623-653 | eccentricities | yes, but phase-dependent; colour map of those figures not identified; not chosen |
| K5 | 54 % shorter lifetimes, 3 % longer, 12 % (4 %) shortened by 10 (1e4); f_m = 0.17 %, f_i = 24.1 % | l. 684-690, 716-718 | needs a random orientation sample and GW timescales; f_m needs PN | partly; not chosen |
| K6 | 4 % of survivors with chi_eff <= -0.5 | l. 898-903 | orbit flips | partly; not chosen |

Digitization (development run, numbers into `results/paper_2402_digitized.json` by the
registered analysis later) [VERIFIED as read from the vector content]:
- InclD iota_c/pi at r_p = 20..6 M: L_z > 0: 0 (r_p >= 14), 1/3, 1/2, 1/2, 2/3 (r_p <= 10);
  L_z < 0: 0 (>= 13), 1/3, 1/2, 1/2, 2/3, 2/3, 1, 1 (r_p = 7, 6); L_z = 0: 0, 1/6, 1/3, 1/3,
  1/2 (10-7), 2/3 (6); s = 0: 0 (>= 14), 1/6, 1/3, 1/2, 1/2, 2/3 (<= 9). The red line equals
  Eq. cosiN with F^-1 = 1/F: 0.5186 pi at r_p = 10 (my own evaluation: 93.4 deg = 0.519 pi),
  0.6185 pi at r_p = 6.
- afin: the cell colours match the YlGnBu map to 7e-11 (so a_fin/a0 is read exactly to the
  map's 256 levels); 56.3 % of the 1728 cells survive; retrograde half 99.5 %, prograde half
  13.1 %; the first surviving iota per L_z row is 0.43-0.49 pi.

Two internal inconsistencies of the paper [JUDGEMENT, from the digitized data]:
(i) K2's text says the L_z < 0 binaries at beta > 0.9 are MORE stable than the Newtonian
criterion, but the figure's L_z < 0 line sits at iota_c = pi there (no survivor below pi)
against the criterion's 0.60-0.62 pi: LESS stable, under the figure's own reading rule
("survivors lie above a line", l. 584-585). (ii) At r_p = 10 Fig. InclD puts L_z > 0
(equatorial) at iota_c = 2/3 pi, while Fig. afin's top row (L_z = 4.80 = the equatorial
maximum) survives from 0.486 pi on. Both can only be reconciled if the unknown node and phase
differ between the figures, or the text is wrong.

### HRNA against the paper's model

| item | 2402.02178 | HRNA (`hrna.py`) |
|---|---|---|
| pair force | Newtonian + PN to 2.5PN in Fermi coordinates, proper time | Newtonian in coordinate distance at equal coordinate time, times 1/Gamma_i^2 per member (2404 Eq. CoordtEqs) |
| tide | linear (quadrupole) gravito-electric only | all orders, gravito-magnetic and frame dragging included implicitly |
| CM | on the geodesic exactly | each member on its own worldline; CM not geodesic; carries the R3 self-acceleration |
| coordinates | proper (Fermi) | Cartesian Kerr-Schild (or Schwarzschild form at a = 0): O(M/r) and O(v^2) distortions of the pair force, about 0.1-0.2 at r = 10 M [JUDGEMENT: 2H = 2M/r and v^2 = 2M/r for E = 1] |
| initial binary | circular in the Fermi frame | circular in coordinates; internal angular velocity divided by the CM's Gamma ('gamma', main), or not (2404 'coord', variant) |

What a comparison can say [JUDGEMENT]: PN terms are 5e-5 of the pair force at a0 = 20000 m12
(v_b = 0.007), negligible for survival. HRNA's coordinate distortions at r_p = 6-10 M are 0.1-0.3
of the self-gravity, below the tidal perturbation there (beta^3 (1 + 3K/2r_p^2) = 0.4-3) but
not negligible; so HRNA can test the sign and the rough size of the relativistic departures
(K1 ordering of the families, K2 sign, K3 boundary near pi/2), not the paper's cells one by one.
The coordinate dependence is measured directly by running s = 0 in both coordinate forms.

Chosen: K1 with K2 (the claim the geodesic_binary README named, l. 592-597), and K3.

## Entry 1 (22:40 UTC): predictions of the tests before use

T5 rotation (Schwarzschild, both coordinate forms, M = 1): an encounter built coplanar and then
rotated as a whole by a rotation R equals the coplanar encounter rotated by R. Prediction:
identical outcomes, final states equal to 1e-9 relative (DOP853's error norm is per 3-vector and
rotation invariant, so the step sequences coincide and only rounding differs); and the new
initial-data module at iota = 0, Omega = 0 reproduces `hrna.initial_state` (sense +1) to rounding,
at iota = pi with phase -phi reproduces sense -1. Refuted by any outcome difference or a
trajectory difference above 1e-7 r_g.

T6 single body in Kerr a = 0.9 on inclined parabolic orbits (r_p = 10, L_z = 2.2 (Fig. compF12),
0, -3, and the paper's two extremes), pair force off, against `python/nrpic/geodesic.integrate('cks')`.
Prediction: positions within 1e-6 r_g over the passage (T2 of geodesic_binary had 3e-8);
E, L_z, Q (from `kerr.invariants`) conserved to 1e-9 relative; the measured pericentre (BL r) equals
the requested r_p to 1e-6 (checks Eq. rp and my Q); Q = 0 at the extremes of Eq. (Lz) to 1e-12.

T7 spin to zero: (i) a = 1e-6 against a = 0 in CKS: outcomes equal, final states within 1e-4 r_g;
(ii) at a = 0 in CKS the spacetime is spherically symmetric, so for one binary orientation
relative to the orbit plane the outcome and the final a, e do not depend on the orbit's
inclination (L_z = +L, 0, -L at the same r_p): a_fin equal to 1e-8; at a = 0.9 they differ.
(iii) a = 0 CKS against Schwarzschild form: survival over 64 orientations at r_p = 10 differs in
at most a few cases (S3 found 0.005 in s.f. for 2404's binaries) [JUDGEMENT].

R3 (flat space, M = 0): (a) the SC0d set-up (m1 = m2 = 0.05, a0 = 3, V = 0.28 in the binary plane,
T = 300) gives a fitted sideways acceleration of 1.065e-4 again (run F-20261115-175620-df20ffe:
-1.0647e-4 with hrna.py). (b) Derivation (this entry): in flat space each member's pair
acceleration is multiplied by 1/Gamma_i^2 = 1 - v_i^2, so the total force is
F (v2^2 - v1^2) with F the force on member 1; with v_i = V + u_i and u2 - u1 = -w (relative
velocity), v2^2 - v1^2 = -2 V.w + u2^2 - u1^2. Orbit-averaged over a Kepler orbit of semi-latus
rectum p and period P the first term gives the CM acceleration
a_s = -(2 pi m1 m2 / (mb p P)) (L_hat_b x V), magnitude (m1 m2/mb)(omega/a0) |V_par| for a
circle (V_par: the component of V in the binary plane; the term u2^2 - u1^2 averages to zero on a
circle). HRNA also weakens the relative attraction by (1 - V^2 - ...), so the started-circular
binary becomes eccentric with e = 1/(1 - V^2 - u^2...) - 1 [leading order], starting at
pericentre; then p = a0 (1 + e), P = P0 (1 - e)^(-3/2) (1 + e)^(1/2) and
a_s = (m1 m2/mb)(omega0/a0) V ((1 - e)/(1 + e))^(3/2). For SC0d (V^2 = 0.0784, u^2 = 0.0083 per
member): e = 0.095 and the factor is 0.751, so a_s = 1.42e-4 x 0.751 = 1.067e-4 [prediction of
the earlier measurement's size, which SC0d left at 1.42e-4]. Prediction: for q = 1 the
leading-order formula holds to 2 % over V = 0.02-0.5 and a0/mb = 30-1000; for any q the
orbit form a_s = 2 pi m1 m2 V_par/(mb p P) with p, P measured from the relative orbit holds to
5 % (for q != 1 the factor 1 - v_i^2 has a term in V.w that the leading-order e omits, and
u2^2 - u1^2 adds a force along the apse line of relative size ~ w e/V [estimate]);
a_s is proportional to cos(psi), psi the angle of V to the binary plane, and vanishes for V
perpendicular to the plane. Control V = 0: no sideways acceleration above 1e-3 of the V = 0.28
value for q = 1.
(c) Effect on a coplanar encounter: dL_cm/dt = r x a_s = -k L_hat_b (r . v) with
k = |a_s|/V, so inbound from r0 to r_p, Delta L_cm = (k/2)(r0^2 - r_p^2) L_hat_b: a prograde
binary gains angular momentum (larger pericentre), a retrograde one loses it.
Predicted sizes (k = (m1 m2/mb)(omega/a0)): 2404's binary (mb = 1e-6, a0 = 1.013, q = 1):
k = 2.4e-10, at r0 = 50 r_t = 5065: Delta L = 3.1e-3, Delta L/L = 2e-4 (beta = 1) to 6e-4
(beta = 10), Delta beta/beta = 2 Delta L/L <= 1.2e-3; at 70 r_t twice that. 2402's binary:
k = 6.8e-7, r0 = 100 M: Delta L = 3.4e-3, Delta L/L = 7e-4. So R3 changes 2404's and 2402's
separation fractions by (d sf/d beta) Delta beta <~ 1e-3 [prediction], too small to explain C2's
0.025. F's own binary is tested with its parameters in the run (q = 10, released at 4 and 20 r_t).

## Entry 2 (2026-11-21 13:20 UTC): restart; development runs; a defect of 'cks'; chart 'bks'; predictions for the registered tests

Restart. The session of 2026-11-20 was cut at 14:35 PST with `hrna_incl.py`, T5, T6, the
digitizer and entries 0-1 uncommitted; committed now unchanged (2be3eba7). Its development runs
(`scratch/F-hills/tmp/kerr/dev_t5`, `dev_t6`, unregistered) passed: T5 (a) six inclined vs rotated
coplanar encounters with equal step counts and matched-time position differences 1e-10 to 2.5e-9
r_g, at the level of the rounding control (4e-11 to 1.3e-9); (b) `hrna_incl` reproduces
`hrna.initial_state` to 5e-14 a0; (c) the Kerr mirror a = +-0.9 to 1.1e-9 (control 8e-10). T6:
positions within 3.8e-8 r_g (r_p = 6) and 1.4e-9 (r_p = 10) of python/nrpic, E to 1e-12, L_z to
3e-12, Q to 9e-11, pericentre to 1e-11, Q at release equal to Eq. (rp). They are rerun registered
with unchanged code (deterministic: the same numbers are expected).

T7 development run (`dev_t7`, the T7 of entry 1, all in 'cks'). FAILED predictions:
- (iii) 'cks' against 'sch' at a = 0: survival differs in 17, 20, 23 of 64 orientations at
  r_p = 7, 10, 13 (predicted: a few); survival fraction 0.41 vs 0.63 at r_p = 10, 0.59 vs 0.92
  at r_p = 13; median |Delta a_fin| 0.4-0.7 a0 among common survivors.
- (i) slope of |Delta E_b| against a 0.64-0.68 instead of 1 (a noise floor, below); (ii) slope 0
  of |Delta L_b|: my error, the mirror orbit's binary must be rotated by pi about x before the
  comparison (corrected in the test).

Trace (development, `hrna.run_encounter` itself, so not an error of `hrna_incl`): 2402's binary,
retrograde coplanar, r_p = 10, a = 0, `ic_gamma`: in 'cks' it hardens all the way in (E_b/E_0 =
1.03 at r = 100, 1.08 at 69, 1.22 at 37, 2.4 at 11.6), runs away to E_b = 6000 E_0 (separation
1e-4 a0) at t = 642 M, and the close pair ejects a member into the hole (outcome 6). In 'sch' the
same binary ends with a = 0.956 a0, e = 0.023.

Mechanism [derived here; tested by T8 (d)]. In Eq. CoordtEqs the pair force enters as
(g^{ij} - g^{0j} v^i) A_j / Gamma^2. In 'cks' g^{0j} = 2 H n_j (H = M/r at a = 0), so each member
gets an extra acceleration -2H (n.A_i) v_i along its own velocity, and the relative orbit the
shear delta a_rel = 2 H m_b (n.d) V / |d|^3 with V the CM velocity. It is not symmetric; its
orbit average is
    d ln|E_b|/dt = -2 H omega_b (n x V) . L_hat_b = -2 (M/r) omega_b v_t cos(iota),
prograde binaries are pumped (unbind), retrograde ones drained (harden), and because omega_b
grows with |E_b| it runs away: |E_b|/|E_0| = (1 + 3K/2)^(-2/3) with
K = int 2 H omega_0 v_t cos(iota) dt = 4 M omega_0 cos(iota) [arctan sqrt((r0 - r_p)/r_p) -
arctan sqrt((r - r_p)/r_p)] on a Newtonian parabola. In words: 'cks' slices are tilted against
the static ones by dt = (2 M r/Delta) dr, so HRNA takes the partner at a different time and
displaces it by V (2M/r)(n.d). At fixed omega_b it does not depend on a0: it is not a tide but an
equivalence-principle defect of HRNA in a non-static slicing. Size: 2402's binary has
M omega_b = 0.0566, K = 0.28 cos(iota) at pericentre from r0 = 100 M; 2404's binary has
M omega_b = 9.8e-4, 58 times less, which is why geodesic_binary S3 ('cks' vs 'sch' within 0.005
in s.f.) did not see it. Consequence: HRNA in 'cks', the only Kerr chart of `hrna.py`, cannot be
used for 2402's binary.

New chart 'bks' (`hrna_bks.py`): Boyer-Lindquist time with the Cartesian Kerr-Schild space,
t' = t_KS - F(r), F' = 2 M r/Delta. At a = 0 it is the Schwarzschild form 'sch' (metric equal to
1e-17 in development); at a != 0 only the frame dragging remains in g'^{0i} (0.02 at r = 10 for
a = 0.9, against 2H = 0.2 in 'cks'; falls like r^-2). `hrna`'s `accel_one`, `rhs`, `integrate`,
`energy_lz` are recompiled from their own code objects with `metric` replaced, so the equations
and the integrator are hrna's, not a copy. Development check (`dev_t8`): g g^-1 = 1 to 2e-15,
derivatives against differences 8e-11, single body at a = 0.9 within 3e-9 r_g of python/nrpic,
a = 0 encounters equal to 'sch' with the same step counts. Energy drift on the way in, odd part
in iota of ln|E_b| ((iota = pi minus iota = 0)/2), 'cks' minus 'sch', at r = 50, 30, 15:
0.040, 0.064, 0.113 against the leading-order prediction 0.041, 0.091, 0.235; 'bks' (a = 0.9)
minus 'sch': 0.000, -0.007, 0.000.

Predictions for the registered tests (re-runs of what development showed, for the record; not
blind):
- T5, T6: the development numbers, to the last digit.
- T7, now in 'bks' for (i) and (ii); (iii) keeps 'cks' against 'sch' as the record of the defect:
  |Delta L_hat_b| proportional to a (slope 0.8-1.2) in (i) and (ii); |Delta E_b|/|E_b| and
  |Delta e| below 1e-3 for a <= 1e-3 (the final elements carry a noise floor of about 1e-4 from
  the step at which the run stops; seen in development); at a = 0.9 the mirror pair differs by
  1e-2 or more in E_b or e. (iii) 17-23 of 64 outcomes differ (the defect; no pass rule).
- T8: (a) identities < 1e-12, derivatives < 1e-7, equality with 'sch' < 1e-12; (b) equal step
  counts and matched-time positions < 1e-8 r_g; (c) < 1e-6 r_g, E to 1e-9, Q to 1e-8; (d) the odd
  part 'cks' minus 'sch' within 10 percent of the leading-order prediction at r = 50 and below it
  at r <= 30 (higher orders; refuted if above), 'bks' minus 'sch' below 20 percent of 'cks''s.

R3 development (`scripts/r3_selfacc.py`, unregistered):
- (a) The SC0d call and fit give -1.06473294303476e-4, equal to F-20261115-175620-df20ffe to all
  digits. But that fit is biased: y = a t^2/2 without a linear term over T = 300 (2.4 relative
  periods). The force is perpendicular to the CM velocity, so V turns at constant size (by 0.86
  rad over 23 periods) and the CM moves on a circle of radius V^2/a_s (about 730 r_g for SC0d's
  binary). Measured by the turning rate of the in-plane CM velocity: a_s = 1.0660e-4 at V = 0.28,
  a0/m_b = 30, against entry 1's leading order 1.0671e-4 (0.1 percent); 0.01 percent at
  a0/m_b = 1000; proportional to cos(psi) to 0.2 percent, zero at psi = 90 deg; the start phase
  changes it by 0.3 percent. The agreement of 1.0647e-4 (biased fit) with 1.067e-4 (entry 1) was
  partly luck.
- FAILED (entry 1: the orbit form within 5 percent for any q): q12 = 0.5 gives 0.83-0.89 of it,
  q12 = 0.1 gives 0.71 and -0.05. The unequal-mass binary's eccentricity grows (0.23-0.62 in the
  window against 0.01-0.1 at the start) and the CM speed changes by up to 32 percent: the terms
  2 (m2 - m1)/m_b (V.w) in the relative force and (m1^2 - m2^2)/m_b^2 w^2 in the CM force are not
  small. Another HRNA artefact, for unequal masses; measured in the registered run for 2402's
  mass ratio.
Predictions for the registered R3 run: (a) as development; (b) q = 1: leading order within 1
percent over V = 0.02-0.5, a0/m_b = 30-1000; V = 0 gives no turning (< 1e-3 of V = 0.28); psi
and phase as development; q12 = 2/3: e grows by less than 1e-3 per period at a0/m_b = 20000
[JUDGEMENT: the unequal-mass terms scale with w ~ (m_b/a0)^(1/2), 0.007 there against 0.18 at
a0/m_b = 30]. (c) The CM pericentre of 2404's binary, HRNA minus Newton, mean over four phases:
the R3 shift Delta r_p/r_p = L Delta L (r_p - 2)^2/(r_p^2 (r_p - 4)) with
Delta L = (k/2)(r0^2 - r_p^2), positive prograde, negative retrograde; within 30 percent where it
exceeds 3e-4 (beta = 3; beta = 1 at 50 and 70 r_t), right sign everywhere [JUDGEMENT on the
tolerance: tidal coupling of the CM orbit differs between the laws]. Its effect on the
separation fraction through the slope of S1's curve: below 2e-3 everywhere; at beta = 4.7
retrograde it RAISES the s.f. with r0 (Delta beta > 0), by about 1e-3 from 20 to 70 r_t, while
C2 found 0.6975 -> 0.68: R3 is not the cause of C2 (wrong sign, 17 times too small).

## Entry 3 (2026-11-21 13:40 UTC): the reproduction scan, prediction before the run

Design (`scripts/scan_2402.py`, analysis `scripts/analysis_2402.py`). The paper's fiducial binary
(m2/m1 = 2/3, a0 = 0.125 M, m_b = 6.25e-6 M; main.tex:486, 504-515) on E = 1 orbits from BL r = 100 M
in the equatorial plane (main.tex:491-502), sigma_theta = +1, binary circular in the CM proper
time, outcome when the CM is back at r = 100 M (main.tex:610-611); survived = no member captured and
E_b < 0 (Gamma-corrected relative velocity). The paper gives neither node nor phase (entry 0), so
every cell is run for several orientations:
- Scan A (K1, K2; Fig. InclD): families pos / neg / zero (s = 0.9 in 'bks'), s0 (a = 0, 'sch'),
  s0cks (a = 0, 'cks': the defect, for the record), newt (Newtonian point mass); r_p = 6..20 M;
  iota = k pi/12; 6 nodes x 4 phases = 24 orientations per cell; 28080 encounters.
- Scan B (K3; Fig. afin): s = 0.9, r_p = 10, 'bks', the paper's 48 L_z x 36 iota cells, 4 nodes x
  2 phases; 13824 encounters.
- The paper's numbers are digitized inside the registered analysis from the vector content of
  InclD.pdf and afin10M2e4.pdf (parsed as data; never rendered into the package, never committed).
Reading rule for InclD (main.tex:584-585: survivors lie above a line): for each orientation the
lowest surviving iota on the paper's pi/6 grid; median and range over the 24 orientations, and the
lowest pi/6 iota where the survival fraction reaches 1/2.

Tolerance and why [JUDGEMENT]: one grid step (pi/6) of InclD. The paper's markers are on that grid,
its node and phase are unknown (the spread over orientations measures how much that matters), and
HRNA differs from the paper's Fermi-frame model at O(M/r_p) = 0.1-0.17 in the binary's self-gravity
(coordinate distance, slicing; T8: 'bks' keeps a frame-dragging residual of -0.005 to -0.007 in
ln|E_b| on the way in) while the PN terms the paper adds are 5e-5 of the pair force (entry 0).

Predictions (before the run):
- P1 (pipeline control): the Newtonian law's boundary (survival >= 1/2) is within one grid step of
  Eq. (cosiN) at every r_p, and the s0 family is within one step of the paper's shaded s = 0
  region at every r_p (refuted at more than 2 of 15 r_p).
- P2 (K1): for pos, neg, zero the paper's marker lies within the HRNA range over orientations, and
  within one step of the HRNA median, at >= 12 of 15 r_p each.
- P3 (K1 ordering at r_p <= 8): iota_c(neg) >= iota_c(pos) >= iota_c(zero) in the HRNA medians, as in
  the paper's figure [reason: the retrograde equatorial orbit at r_p = 6-7 lies just outside its
  marginally bound radius 5.66 M and whirls (T6: 1.85 turns at r_p = 6 against 1.07 prograde), so
  the binary stays longer in the strong tide].
- P4 (K2): at r_p = 6 and 7 (beta = 1.13, 0.97) the neg family's HRNA boundary lies ABOVE Eq. (cosiN)
  (0.60-0.62 pi), i.e. less stable than Newton, as the paper's figure shows (iota_c = pi) and against
  its text ("more stable", main.tex:586-593). Refuted if HRNA's boundary is at or below the criterion.
- P5 (K3): the HRNA survival map at r_p = 10 has its boundary near pi/2 in every L_z row: the median
  lowest surviving iota within pi/12 of the paper's in >= 70 percent of the 48 rows; survival
  fraction 0.563 (paper) reproduced within 0.08; retrograde half >= 0.95 and prograde half <= 0.25
  in both; survivors' median a_fin in the retrograde half within 0.1 a0 of the paper's.
- P6 (the defect): s0cks differs from s0 by more than one grid step at several r_p <= 13 (entry 2).

## Entry 4 (2026-11-21 13:35 UTC): outcomes of the registered tests T5-T8 and of R3

T5 (F-20261121-131507-d9da8f1; figure `figures/t5_rotation.png`, read): passes as in development:
inclined = rotated coplanar with equal step counts, matched-time positions 1.1e-10 to 2.5e-9 r_g
against the rounding control 4e-11 to 1.3e-9; `hrna_incl` reproduces `hrna.initial_state` to
5e-14 a0; the Kerr mirror to 1.1e-9. [VERIFIED]

T6 (F-20261121-131516-34d8c26; `figures/t6_kerr_single.png`, read): passes; positions within
3.8e-8 r_g (r_p = 6 retrograde whirl), <= 1.4e-9 at r_p = 10; E to 1e-12, Q to 6e-11. [VERIFIED]

T7 (F-20261121-131522-058291d; rerun with the renamed output key F-20261121-132010-a654642,
`figures/t7_spin_limit.png`, read). (i), (ii) in 'bks': |Delta L_hat_b| slopes 0.9998-1.0000
against a; energies and e within 1e-3 of a = 0 for a <= 1e-3 (floor 4e-8 to 1.8e-4, non-monotonic:
the stop step); at a = 0.9 the mirror pair differs by 0.04 / 0.26 in E_b and 0.50 in e (survivor).
Prediction holds. (iii) 'cks' vs 'sch' at a = 0: 17, 20, 23 of 64 outcomes differ (the defect, as
in development; the first run's key `pass_iii` = false is entry 1's rule, no longer a criterion).

T8 (F-20261121-131539-417caed; rerun with the odd-part figure F-20261121-132028-86ae5d0,
`figures/t8_bks_chart.png`, read). (a) g g^-1 = 1 to 1.9e-15, derivatives 7.8e-11, equal to 'sch'
at a = 0 to 1.1e-15; (b) equal step counts, matched-time positions 8.8e-11 to 4.2e-10 r_g; (c)
single body at a = 0.9 within 3.0e-9 r_g of python/nrpic (r_p = 6 and 10, L_z of both signs and
0), E to 5e-13, Q to 9e-11. (d) odd part in iota of ln|E_b|, 'cks' minus 'sch': 0.0398 / 0.0636 /
0.1127 at r = 50 / 30 / 15 against the leading order 0.0412 / 0.0911 / 0.2352: within 3.5 percent
at r = 50, below it further in (holds); the curve oscillates about the prediction down to r = 20
and rises steeply at r < 12 (figure). 'bks' (a = 0.9) minus 'sch': -0.0054 / -0.0069 / -0.0002,
i.e. 0.20 / 0.13 / 0.002 of 'cks' (a = 0.9) at the same radii: the prediction "below 20 percent"
holds at r <= 30 and is met only at the boundary at r = 50 (0.202). The frame-dragging residual of
'bks' is a few 1e-3 in ln|E_b|, of opposite sign. [VERIFIED for (a)-(c); (d) measures the defect]

R3 (F-20261121-131555-91aa063, 4 cores, 5 min; its figure step failed on a mathtext symbol after
the JSON was written, run marked failed; figure from that JSON: F-20261121-132235-7df540a,
`figures/r3_selfacc.png`, read):
- (a) -1.06473294303476e-4, equal to F-20261115-175620-df20ffe to all printed digits. Holds.
- (b) q = 1: the turning-rate measurement agrees with the leading order within 0.8 percent for
  V <= 0.4 at every a0/m_b and within 0.03 percent at a0/m_b = 1000; FAILED at V = 0.5,
  a0/m_b = 30: +2.3 percent (prediction 1 percent; +0.6 percent at a0/m_b = 100). V = 0: zero.
  psi = 30, 60 deg: 0.1-0.2 percent; 90 deg: zero; start phase: 0.2 percent. The CM speed stays
  constant to 8e-3 (a0/m_b = 30) and 2e-4 (1000): the force turns V and does not slow it.
- q != 1 and 2402's mass ratio: FAILED prediction (entry 2: e grows by less than 1e-3 per period
  at a0/m_b = 20000): at q12 = 2/3, a0/m_b = 20000 the eccentricity grows from 0.022 to 0.052 over
  24 periods at V = 0.14 (1.25e-3 per period) and from 0.261 to 0.353 at V = 0.45 (3.8e-3 per
  period). Mechanism [JUDGEMENT, from the algebra of entry 2]: for unequal masses the relative
  force carries the factor 1 - V^2 - 2 (m2 - m1)/m_b (V.w) - ..., a modulation at the orbital
  frequency that pumps e resonantly; its size goes with |m2 - m1|/m_b, V and w. For 2402's binary
  (8.5 periods per passage at V = 0.14-0.45) this is Delta e of order 0.01-0.03 per passage from
  HRNA alone [estimate from these rates]. a_s itself at a0/m_b = 20000 is 0.9986 (V = 0.14) and
  0.95 (V = 0.45) of the leading order.
- (c) CM pericentre of 2404's binary, HRNA minus Newton (mean of 4 phases) against the R3
  prediction: r0 = 70 r_t: +7.1e-4 / -7.2e-4 (beta = 1, pred +-8.6e-4) and +1.46e-3 / -1.59e-3
  (beta = 3, pred +-1.53e-3): within 18 percent, right sign. r0 = 50 r_t: beta = 3 prograde
  +7.8e-4 (pred 7.8e-4) but retrograde -4.0e-4 (pred -7.8e-4), beta = 1 +7.4e-4 / -2.6e-4 (pred
  +-4.4e-4): the phase spread (3.6e-4 to 1.7e-3) is of the size of the signal; 3 of 8 cases above
  the 30 percent tolerance: FAILED as stated, the tolerance ignored the phase scatter of four
  phases. r0 = 20 r_t: signal (7e-5 to 1.3e-4) below the spread; beta = 3 prograde has the wrong
  sign (-2e-5, spread 1.7e-3). The r0^2 growth and the sign are confirmed where the signal exceeds
  the scatter.
- Effect on separation fractions (slope of S1's curve, geodesic_binary/results/s1_summary.json):
  |Delta s.f.| <= 3.2e-3 (beta = 10, 70 r_t), <= 1.1e-3 at beta <= 5; at beta = 4.7 retrograde the
  local slope of the 400-phase curve is zero, and the sign of the R3 shift (beta up for
  retrograde) would raise the s.f. with r0 while C2 found 0.6975 -> 0.68. R3 is not the cause of
  C2 (holds). Leading-order sizes (`c_pred` of the run): 2402's binary from r0 = 100 M:
  Delta L/L = 5e-4 to 8e-4, Delta r_p/r_p = 1.1e-3 (r_p = 20) to 3.2e-3 (r_p = 6), small next to
  the slicing defect. F's binary (m1 = m2 = 0.05, a0 = 3, M = 1): from 4 r_t Delta L/L = 0.023 to
  0.036 (Delta r_p/r_p = 0.06-0.12 for r_p = 13-7); from 20 r_t Delta L/L = 0.76-0.95, i.e. the
  perturbative estimate breaks down, consistent with SC0d (CM never closer than 30-44 M).

## Entry 5 (2026-11-21 13:35 UTC): outcome of the reproduction scan; spin trend; verdict

Runs: scan F-20261121-132131-326dfd1 (41904 encounters, 122 s on 5 cores; status 0: 41791, CM not
back at 100 M before t_max: 34, step underflow: 13, both members captured: 66; no errors);
analysis F-20261121-132346-b3b6c0e (first), superseded by F-20261121-132817-eacfe46 after a bug
of mine: digitized markers at iota = 0 read -2e-5 and at pi read pi + 1e-5, and the range test had
a 1e-6 tolerance, so markers sitting on the grid were counted "out of range" (fixed: 0.05 step).
Figures `figures/fig_incld.png`, `fig_incld_sf.png`, `fig_afin.png`, `fig_afin_sf.png` (all read);
numbers `results/kerr_2402_summary.json`, digitized paper values `results/paper_2402_digitized.json`.
The digitization reproduces entry 0 (InclD markers on the pi/6 grid; afin colours to 7.4e-11,
survived fraction 0.5631).

Outcomes against entry 3 (iota in units of pi/6 below):
- P1 FAILED in part. The s0 family (a = 0, 'sch') lies within one step of the paper's shaded
  s = 0 boundary at 15 of 15 r_p and the paper's value is inside the HRNA orientation range at
  15 of 15 (holds). The Newtonian law against Eq. (cosiN): within one step at 12 of 15; at
  r_p = 12, 13, 14 (beta = 0.57-0.48) the Newton law keeps at least half the orientations at every
  iota (boundary 0) where the criterion gives 1.6-2.5 steps: refuted by my rule (at most 2).
  Eq. (cosiN) is an approximate criterion; at those beta the paper's relativistic markers (1-2
  steps) also lie above both HRNA and the Newton law of this set-up.
- P2 holds for L_z < 0 and L_z = 0, FAILED for L_z > 0. Paper inside the HRNA range: 14 / 14 / 15
  of 15 (pos / neg / zero); within one step of the HRNA median: 11 / 15 / 15. The pos misses are
  r_p = 10-13 (beta = 0.68-0.52): HRNA median 0-1 step, paper 2-4 steps; HRNA is more stable there.
- P3 holds at r_p = 7, 8 (neg >= pos >= zero), not at r_p = 6 (zero 4.5 > pos 4).
- P4 (K2) holds: neg at r_p = 6 and 7 has HRNA boundary 5 (median and survival >= 1/2), above
  Eq. (cosiN) (3.71, 3.62): less stable than the Newtonian criterion, as the paper's FIGURE shows
  (6) and against its TEXT ("more stable", main.tex:586-593). The paper's 6 is one step above the
  HRNA median; at r_p = 7 it is outside the HRNA range [3, 5], at r_p = 6 inside [4, 6].
- P5 (K3) FAILED except for the retrograde half. Survival 0.718 (HRNA, 8 orientations) vs 0.563
  (paper); prograde half 0.48 vs 0.13; retrograde half 0.953 vs 0.995; a_fin of retrograde
  survivors median 0.995 vs 1.012 (10-90 percent: 0.90-1.10 vs 0.93-1.11). The paper's empty
  prograde half is reproduced by no single orientation (prograde survival 0.23-0.63 over the 8),
  and the Newton law of scan A at r_p = 10 (equatorial, 24 orientations) also keeps 0.17-0.33 at
  iota <= 5 pi/12. The lowest surviving iota per row is within pi/12 of the paper's in 0 of 48 rows
  (HRNA 0.05-0.24 pi: isolated low-iota survivors; a poor statistic, kept as predicted). L_z
  bands, prograde-half survival HRNA / paper: L_z < -3: 0.34 / 0.12; [-3, 0): 0.46 / 0.17;
  [0, 3): 0.57 / 0.15; >= 3: 0.57 / 0.06. HRNA has more prograde survivors at L_z > 0; the paper
  has fewer near L_z = 4 (main.tex:561-562).
- P6 partly: 'cks' at a = 0 differs from 'sch' by more than one step at r_p = 13-17 (3 vs 0 at
  r_p = 13; 2 vs 0 at 14-17) and in survival fraction at every r_p (0.58 vs 0.92 at r_p = 13,
  0.44 vs 0.62 at 10); at r_p <= 12 the boundaries agree within one step. The slicing pump
  disrupts prograde binaries where the tide alone would not.

Spin trend (development `dev_spin.py` in scratch first, then registered F-20261121-132821-5610cdb,
`figures/spin_trend.png`, read; same numbers): equatorial orbits at r_p = 10, 'bks', 24
orientations: survival at iota = pi/6 rises monotonically from 0.08 (a = -0.9, retrograde orbit)
through 0.33 (a = 0) to 0.67 (a = 0.9); at pi/2 from 0.50 to 0.875; at pi/3 0.13 -> 0.42. The
factor 1 + 3K/(2 r_p^2) of the radial tidal eigenvalue, K = (a - L_z)^2, falls from 1.57 to 1.23
over the same range [JUDGEMENT: Schwarzschild's -(M/r^3)(2 + 3L^2/r^2) with L^2 -> K; TO VERIFY].
Reading [JUDGEMENT]: HRNA's L_z > 0 family is more stable than s = 0 at beta = 0.57-0.68 because a
prograde Kerr orbit has the weaker tide at the same r_p; the paper's InclD shows the opposite
order there (pos 4, s0 3 at r_p = 10), and its own Fig. afin top row (L_z = 4.80, the equatorial
L_z > 0 orbit) survives from 0.486 pi = 2.9 steps on, closer to HRNA's s0 than to its own InclD
marker. Which of HRNA and the paper is right at beta ~ 0.6 is not decided here; a Fermi-frame
tidal model (the paper's model) as a reference would decide it [TO VERIFY].

Verdict for the Kerr part of T2 [JUDGEMENT, on the evidence above]:
- Reproduced within the paper's pi/6 grid: the Schwarzschild boundary (15/15 r_p), the L_z < 0
  and L_z = 0 boundaries (15/15 within one step of the HRNA median), and K2 as drawn (L_z < 0 at
  beta > 0.9 less stable than Eq. (cosiN)); K2's text is refuted.
- Not reproduced: the L_z > 0 boundary at beta = 0.52-0.68 (HRNA 2-3 steps more stable,
  consistent with the tidal constant K) and Fig. afin's empty prograde half (orientation-
  dependent in HRNA and in the Newton law of the same set-up; the paper's node and phase are not
  given).
- Condition: HRNA must be run in a static slicing ('sch'; for Kerr 'bks'). In Kerr-Schild slicing
  ('cks', hrna.py's only Kerr chart) it pumps the binary at first order in M/r and is unusable at
  2402's binary frequency. HRNA's own artefacts at 2402's parameters are small for the outcome:
  R3 (Delta r_p/r_p <= 3.2e-3) and the unequal-mass eccentricity pump (Delta e ~ 0.01-0.03 per
  passage, estimate).
