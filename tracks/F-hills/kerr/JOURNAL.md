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
