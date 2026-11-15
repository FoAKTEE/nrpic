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
