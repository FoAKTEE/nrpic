# Derivations by the orchestrator, to be re-derived independently before use

Status: [JUDGEMENT]. Each item is a hypothesis for the track named; the track re-derives it
(symbolically where possible), checks it numerically, and records agreement or the
correction in its own notes. Units G = c = 1. Sign: expansion has K < 0.

## 1. Expanding dust ball, marginally bound (Track A, brief S1 "derivation to be checked")

Lemaitre-Tolman-Bondi dust with E = 0 in the coordinates (tau, R): tau the proper time of
the dust, R the areal radius:

    ds^2 = -dtau^2 + (dR - v dtau)^2 + R^2 dOmega^2,   v = + sqrt(2 m(R,tau) / R)  (expanding),

m the Misner-Sharp mass, constant along dust world lines. On a slice tau = const:
- the 3-metric is flat (psi = 1), the lapse is 1, the shift is beta^i = -v n^i;
- K_ij = -d_(i v_j) = -[ (v/R) (delta_ij - n_i n_j) + v' n_i n_j ], so KT = -v/R, KL = -v';
- the normal observers are the dust observers, so the dust has u_i = 0, S_i = 0, E = rho;
- homogeneous interior, m = M (R/R_b)^3: v = H R, K_ij = -H delta_ij, and the Hamiltonian
  constraint K^2 - K_ij K^ij = 6 H^2 = 16 pi rho is the Friedmann equation; at the surface
  2M/R_b = (H R_b)^2;
- vacuum exterior, v = sqrt(2M/R): KT = -v/R, KL = +v/(2R), K^2 - K_ij K^ij = 0, and
  D_j (K^ij - delta^ij K) = 0;
- no anti-trapped surface on the slice while H R_b < 1 (the ball is inside its Hubble radius).
A marginally bound ball expands for ever. Turnaround and collapse need a bound region:
E(r) < 0 in a core (a top-hat or a smooth profile inside the Einstein-de Sitter ball). Then

    ds^2 = -dtau^2 + (dR - v dtau)^2 / (1 + 2E) + R^2 dOmega^2,   v = sqrt(2m/R + 2E),

the slice tau = const is curved, still conformally flat by spherical symmetry
(dR^2/(1+2E) + R^2 dOmega^2 = psi^4 (drbar^2 + rbar^2 dOmega^2), one radial integration),
the dust is still at rest with respect to the normal observers, and KT = -v/R,
KL = -(dv/dR) (to be checked with E depending on R at fixed tau). Such data fit table
format 2 (`coord/INTERFACES/spherical_id_format2.md`). In the evolution code the gauge is
not this one (1+log lapse, Gamma-driver shift), so comparisons with the exact solution use
invariants: areal radius of a shell against the proper time of its particles, Misner-Sharp
mass, time of horizon formation in proper time of an observer.

### Checked (2026-11-15, wave 1)

Re-derived independently by Track A and by core; both confirm the item, including its open
point: KL = -dv/dR at fixed tau also when E depends on R (dv/dR the total derivative along
the slice; in the coordinates (tau, R) the Christoffel term of the shift is cancelled by the
time dependence of E at fixed R).

**Track A** (`track/A-emd-pbh:tracks/A-emd-pbh/expball/DERIVATION.md`, section 9 point by
point, section 8 for the brief's two statements; symbolic checks
`expball/sym/sym_ltb_4d.py`, `sym_slice.py`, `sym_growing.py`; offline residuals runs
A-emd-pbh-20261115-121654-6bfb707, -122121-aa1c84d, -122117-aa1c84d; the generator agrees
with core's `python/nrpic/expanding_ball.py` to 5e-15, run A-20261115-130257-a7374a4).
Verdict: agreement with every statement of the item, with these qualifications.
1. A top-hat in E is not admissible (velocity jump, delta function in KL, shells separate at
   once); the top-hat goes into the density (or Delta), and with a simultaneous bang time E
   is then continuous.
2. The data fit table format 2 if the core is compensated (E = 0 at and beyond the last row,
   psi = 1 there); otherwise the `exterior = pg` continuation is not exact.
3. With a bound core the anti-trapping criterion is max 2m/R < 1 (independent of E), not
   H R_b < 1.
4. Needed for the table and not in the item: betar = -v/(psi^2 sqrt(1 + 2E)) in the isotropic
   coordinate, alpha = 1.
5. The KL jump at the ball surface (and at the edges of a sharp top-hat) gives an O(jump/h)
   momentum residual on a mesh; a C^4 edge taper (`edge_width`) removes it while keeping
   E = 0 and the exact solution.
6. The bang time must be chosen: simultaneous bang time is the pure growing mode; a density
   top-hat in an unperturbed Hubble flow carries a decaying mode and another turnaround time.
7. The brief's "time-reversed Oppenheimer-Snyder solution" is the marginally bound case; the
   code's Oppenheimer-Snyder test (collapse from rest at finite R_0) time-reversed is a ball
   that decelerates to rest.

**core** (`core/nrpic:tracks/core/JOURNAL-id.md`, entry 1 line 43 and entry 2 line 153;
`core/nrpic:tracks/core/analysis/id/check_derivation.py`, 15 sympy statements, all pass).
Verdict: confirmed, with one addition: KL jumps at a sharp dust surface (from -H to +H/2,
a jump of 3H/2; KT continuous with a kink); the continuum momentum constraint has no
surface term, but on a Cartesian mesh the two differentiated terms that carry the jump
cancel only on average over the surface cells [JUDGEMENT, tested in core's test 1]. Exact
shell evolution: R(tau) = (R_0^(3/2) + (3/2) sqrt(2m) tau)^(2/3), no shell crossing while the
mean density inside decreases outwards.

Track D used the dust-side KT, KL of this item without disagreement
(`track/D-bh-dress:tracks/D-bh-dress/einstein_straus/DERIVATION.md`, end of section 7).

## 2. Black hole in a vacuum bubble inside the expanding ball (Track D, D-pre-1)

In vacuum and spherical symmetry the momentum constraint for K^i_j = diag(KL, KT, KT) is
d KT / d ln R = KL - KT (R areal), and the Hamiltonian constraint fixes the 3-geometry
through the Misner-Sharp mass, (dR/dl)^2 = 1 - 2m/R + R^2 KT^2 (l proper radial distance).
So any KT(R) gives a slice of Schwarzschild. A Painleve-Gullstrand slice with outgoing
flow (KT = -sqrt(2m/R^3) all the way in) enters the white-hole region and holds no
future horizon: unsuitable. Take instead KT = -f(R) sqrt(2m/R^3) with f = 1 at and beyond
the bubble wall (so the slice joins the dust region of item 1 with the wall comoving) and
f = 0 inside some radius: there the slice is the time-symmetric slice of Schwarzschild,
that is, a puncture, psi = 1 + m/(2 rbar) in isotropic coordinates, which the code already
evolves. Between, the throat sits where dR/dl = 0. The data are a format-2 table (regular
part of psi, KL, KT) plus a puncture component. While the wall is comoving the mass inside
is constant: the exact reference of the null test. To check: regularity of the join,
absence of anti-trapped surfaces between throat and wall for the chosen f, the offline
constraint residuals.

### Checked (2026-11-15, wave 1)

Re-derived by Track D (`track/D-bh-dress:tracks/D-bh-dress/einstein_straus/DERIVATION.md`,
sections 1-6, disagreements in section 7, checks in section 8; symbolic scripts
`einstein_straus/sym/s1_constraints.py`, `s2_schwarzschild_slices.py`, `s3_ltb_wall.py`,
48 identities, run D-bh-dress-20261115-042626-f3da881, lead's rerun -065141-5fdc744 48/48).
Verdict: the construction holds (momentum constraint d KT/d ln R = KL - KT, the
Misner-Sharp relation, a format-2 table plus a puncture component, the constant mass inside
the comoving wall), with four corrections:
(a) With psi = 1 at infinity and wherever f = 1, the time-symmetric region has
    psi = a + b/rbar with a < 1, so the bare puncture mass is m_p = M/a, not M: for Track D's
    data set a = 0.9765922286441, m_p = 1.023968828206 M (lead's own quadrature, equal to
    `es.json` to 1e-13); m_p = M would give a black hole of 0.9766 M.
(b) The throat is the bifurcation sphere R = 2M inside the f = 0 region
    (rbar = M/(2a^2) = 0.5243 M), not in the transition; a throat inside the transition
    (f > 0) sits at R < 2M and is anti-trapped.
(c) The condition f(2M) = 0 must be added ("f = 0 inside some radius" becomes f = 0 on
    [2M, R0] with R0 > 2M, to sufficient order for the time-symmetric second sheet).
(d) "Any KT(R) gives a slice" holds along one sheet only: KT must be smooth along the slice
    and W^2 > 0 away from the throat.
Agreed with precisions: the outgoing Painleve-Gullstrand slice is unsuitable because it
reaches R = 0 (white-hole singularity) and all its spheres with R < 2M are anti-trapped;
f = 1 at and beyond the wall (necessary f(R_in) = 1). Not in the item: the table's u carries
-m_p/(2 rbar) outside R1, and psi = 1 outside the ball, so a mass read from the 1/r tail of
psi is zero; masses are read as Misner-Sharp or horizon masses (the exterior mass shows only
in K_ij ~ r^(-3/2)).
Offline residuals of the data are fourth order in seven sub-boxes (run
D-bh-dress-20261115-042704-f3da881); inside AthenaK at t = 0 (format-2 reader at 408df57)
they fall at order 5.8-5.9 in the curvature transition and 3.2 at the inner dust edge, and
the deposited density equals rho to 1.1e-13 (runs D-bh-dress-20261115-043002-d51c7f2,
-043033-4df1e76, analysis -043406-4df1e76). Track D asks for an artefact-only second check
of DERIVATION.md sections 3-4 (outbox `20261115T1510Z__to-orch__brief-and-notes-corrections.md`
item 6); not yet done.

## 3. Plane symmetry and gravitational waves (Track B)

An exactly plane-symmetric collapse radiates no gravitational waves: its stresses are
longitudinal plus isotropic in the transverse plane, and the transverse-traceless
projection of such a source vanishes for wave vectors along the symmetry axis. The
plane-symmetric pancake is therefore a test of the multi-stream region (brief section 10),
not a source. A gravitational-wave signal needs broken plane symmetry: a finite or
transversely modulated pancake, crossed waves of unequal amplitude, or a triaxial
perturbation. With three equal crossed waves (the single-wavelength problem of `cosmo/`)
cubic symmetry removes the quadrupole but leaves transverse-traceless modes at mixed wave
vectors. Track B states at G0 which configuration it takes as the first source.

### Checked (2026-11-15, wave 1)

Re-derived by Track B (`track/B-emd-gw:tracks/B-emd-gw/scope/SCOPE.md`, section 2; script
`scope/scripts/check_item3.py`; runs B-emd-gw-20261115-113102-bc5e082 (sympy,
`results/check_item3.json`) and -113148-4e5c33b (Fourier, `results/crossed_waves_tt.json`,
`figs/crossed_waves_tt.png`); the lead's independent code, run -131027-03b1119, checks b-d).
Verdict: the claim holds, with the amendment that decision 0013 accepts:
(a) The argument needs the rotation part of plane symmetry, E(2) (T_yy = T_zz, T_yz = 0):
    with the two translations alone, plane waves along x with h_+ = h_yy - h_zz are allowed
    and would be sourced by anisotropic transverse stress. On the mesh the 90-degree
    rotation of the lattice suffices for the modes along x; the TT part of the plane wave is
    exactly 0.0 numerically (check 2A).
(b) On the torus the covariant (York) TT part keeps one global mode,
    A^i_j = c Y^-3 diag(1, -1/2, -1/2) for gamma = diag(X^2, Y^2, Y^2)(x); its overlap with K
    is -c d/dt of the integral of X/Y over x: an anisotropic mean expansion, zero at first
    order, not radiation, to be reported apart from the modes at nonzero wave number.
(c) The single-wavelength data of `cosmo/` have amplitudes delta (1, 0.9, 1.1), not equal ones
    (`cosmo/ic/make_east.py:7, 51, 211`); equal amplitudes carry the TT modes at mixed wave
    vectors with the same TT fraction 0.5 (check 2C).
(d) With a transverse metric independent of x, dust at rest admits only the decaying mode
    (D = const or 1/t), so the growing-mode pancake in GR needs an x-dependent transverse
    metric; the brief's "Zel'dovich exact in plane symmetry" (pancake row) is Newtonian only
    (`coord/BRIEF_ERRATA.md` row 1.12).
First source chosen at G0 (SCOPE.md section 3): two crossed waves of unequal amplitude
(1, eps, 0) in the box of four initial Hubble radii, with eps = 0, the plane-symmetric
pancake, as the in-family null; the real-space strain at K = (k, k, 0) before shell crossing
is h_+ = -(5/6) phi_x phi_y cos(K.x) (lead's check d, run -131027-03b1119).
