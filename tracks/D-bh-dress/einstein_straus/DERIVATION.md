# D-pre-1: a black hole in a vacuum bubble inside an expanding dust ball

Independent re-derivation of items 1 (the part used here) and 2 of
`coord/notes/derivations_to_check.md` (orchestrator, [JUDGEMENT]). Every identity marked
[VERIFIED: sym] is checked symbolically by `sym/s1_constraints.py`,
`sym/s2_schwarzschild_slices.py`, `sym/s3_ltb_wall.py` (48 identities, all pass, run
`D-bh-dress-20261115-042626-f3da881`, log `scratch/D-bh-dress/<run>/log.txt`). Numbers
come from runs named next to them. Units G = c = 1; the code's sign
`K_ij = -(1/2alpha)(d_t gamma_ij - D_i beta_j - D_j beta_i)`, so expansion has K < 0.
Notation: areal radius R, proper radial length l, isotropic radius rbar,
`K^i_j = diag(KL, KT, KT)`, ' = d/dl unless stated.

## 1. Constraints of a spherically symmetric slice in KT, KL

3-metric `dl^2 + R(l)^2 dOmega^2`. [VERIFIED: sym, s1]

- Ricci scalar `(3)R = (2/R^2)(1 - R'^2 - 2 R R'')`; `K^2 - K_ij K^ij = 4 KL KT + 2 KT^2`.
- Hamiltonian constraint `(2/R^2)(1 - R'^2 - 2RR'') + 4 KL KT + 2 KT^2 = 16 pi rho`.
- Momentum constraint: the angular components vanish identically; the radial one is
  `D_j K^j_l - D_l K = 2[(KL - KT) R'/R - KT'] = 8 pi S_l`. With S_l = 0 (vacuum, or dust at
  rest in the slice): `dKT/d ln R = KL - KT`, i.e. **`KL = d(R KT)/dR`** wherever R is a
  good coordinate. (Item 2 states the same; agreement.)
- Misner-Sharp mass. With `Lie_n R = -R KT` (from `K_ij = -(1/2) Lie_n gamma_ij`; checked in
  4D in s2), `m = (R/2)(1 - grad R . grad R) = (R/2)(1 - R'^2 + R^2 KT^2)`, i.e.
  **`(dR/dl)^2 = 1 - 2m/R + R^2 KT^2`** (item 2: agreement). Identity
  `dm/dl = 4 pi R^2 (rho R' - S_l R KT) + (R^2 R'/4) Ham - (R^3 KT/2) Mom`
  holds for arbitrary R(l), KL, KT, rho, S_l [VERIFIED: sym, s1]. Hence on a constraint-
  satisfying slice with S_l = 0: `dm/dR = 4 pi R^2 rho`; in vacuum m is constant.
- Conformally flat form `psi^4 (drbar^2 + rbar^2 dOmega^2)`: `(3)R = -8 psi^-5 Lap psi`,
  `R = psi^2 rbar`, `dl = psi^2 drbar`, `dR/dl = 1 + 2 d ln psi/d ln rbar = d ln R/d ln rbar`,
  and the momentum constraint reads `KT_,rbar = (KL - KT)(1/rbar + 2 psi_,rbar/psi)`
  [VERIFIED: sym, s1]. So on a sheet where R grows outward, `d ln rbar = dR/(R W)` with
  `W = dR/dl`.

## 2. Slices of Schwarzschild and the family KT = -f(R) sqrt(2M/R^3)

Schwarzschild in static coordinates, slice `t = T(R)`, future unit normal. For every T(R)
[VERIFIED: sym, s2]: `(dR/dl)^2 = 1 - 2M/R + R^2 KT^2` and `KL = d(R KT)/dR`, i.e. every
spacelike slice obeys the vacuum constraints of section 1 with m = M (Birkhoff, in reverse:
any vacuum data of section 1 are a slice of the Kruskal extension). The family

    KT = -f(R) sqrt(2M/R^3),   W^2 = (dR/dl)^2 = 1 - 2M (1 - f^2)/R,
    KL = d(R KT)/dR = -f' sqrt(2M/R) + f sqrt(2M/R)/(2R),

is the slice with `T'(R) = f sqrt(2M/R) / ((1 - 2M/R) W)` (R > 2M) [VERIFIED: sym, s2].
For the stationary slicing that moves this slice along the Killing vector, the lapse is
`alpha = -n.xi = W` and the shift `beta^R = alpha R KT`, `beta^rbar = rbar KT`
[VERIFIED: sym, s2]. f = 1 everywhere is the outgoing Painleve-Gullstrand slice (W = 1,
flat, rbar = R).

Precision on item 2's "any KT(R) gives a slice of Schwarzschild": R is not a coordinate at
the throat, so KT must be given as a smooth function along the slice (of l or rbar), W^2 > 0
must hold away from the throat, and the parameterization by R covers one sheet only.

## 3. Trapping, the throat, and the conditions on f

Null normals of a sphere, `k_pm = n pm s`: `theta_pm = (2/R)(pm R' - R KT)`,
`theta_+ theta_- = -(4/R^2)(1 - 2m/R)`, `theta_+ + theta_- = -4 KT` [VERIFIED: sym, s2,
numerically at three points for the square-root branches; the product rule with m from
section 1 symbolically]. Hence a sphere is trapped or anti-trapped iff R < 2m; anti-trapped
(both expansions positive) iff R < 2m and KT < 0; R = 2m is marginal.

Throat (R' = 0) of the f family: `R_th = 2M (1 - f(R_th)^2)`. Conditions for a regular
slice without anti-trapped spheres between throat and wall [derivation; sym for the
pieces]:

- (F1) Join: `f(R_in) = 1` at the wall R_in (KT continuous, so that the dust at the wall is
  at rest in the slice and marginally bound, `dR/dtau = sqrt(2M/R)`), and f = 1 throughout
  the dust if the dust is to be marginally bound (flat slice there). f = 1 on a
  neighbourhood inside the wall is not required, only convenient (no kink in KL).
- (F2) `W^2 = 1 - 2M(1 - f^2)/R > 0` for R > R_th: automatic for R > 2M.
- (F3) No anti-trapped sphere: KT >= 0 (f <= 0) wherever R < 2M on the slice. With f >= 0
  this means the slice never enters R < 2M, i.e. **f(2M) = 0 and the throat is the
  bifurcation sphere R = 2M**. If f > 0 at the throat, the throat moves to
  R_th = 2M(1 - f^2) < 2M and is itself anti-trapped (white-hole region). (A slice with
  f < 0 near the throat would dip into the black-hole interior, with a trapped throat; not
  used.)
- (F4) Continuation through the throat to a time-symmetric second sheet (K = 0 near the
  puncture, which the puncture form of the code needs): near the throat R - 2M ~ l^2/(8M),
  so `f = O((R - 2M)^k)` gives KT of class C^(2k-1) in l across the throat. The simplest
  choice, used here, is **f = 0 on [2M, R0] with R0 > 2M**; then the slice is the
  time-symmetric Schwarzschild slice from rbar(R0) on the outer sheet through the throat to
  the second asymptotic end.
- f need not be monotonic and may exceed 1 (W > 1); neither is used.

Used: `f(R) = S((R - R0)/(R1 - R0))` with the C-infinity step
`S(x) = 1/(1 + exp(1/x - 1/(1-x)))` on (0, 1), R0 = 4M, R1 = R_in = 36M. The expansions
along the whole slice (both sheets) are in `figs/es_expansions.png`: theta_+ and theta_-
are never both positive; both vanish only at the throat; `R^2 theta_+ theta_-/4` lies on
`-(1 - 2m/R)` everywhere (run `D-bh-dress-20261115-043445-b782009`).

## 4. The time-symmetric interior and the conformally flat (puncture) form

Where K = 0 in vacuum, psi is harmonic, `psi = a + b/rbar` with Misner-Sharp mass
`M = 2ab`, throat at `rbar = b/a` with R = 4ab = 2M, and the inversion
`rbar -> (b/a)^2/rbar` an isometry [VERIFIED: sym, s1]. Integrating inwards from the flat
region (psi = 1, rbar = R for R >= R1):

    ln(rbar/R) = - int_R^{R1} (1/W - 1) dR'/R'     (R0 <= R <= R1),
    a^2 = r_iso(R0)/rbar(R0),  r_iso(R) = (R - M + sqrt(R^2 - 2MR))/2,  b = M/(2a).

**a < 1 whenever f is not identically zero** [derivation]: W >= sqrt(1 - 2M/R) with strict
inequality where f > 0, so `rbar(R0) > R1 r_iso(R0)/r_iso(R1)` and
`a^2 < r_iso(R1)/R1 = (1 + M/(2 r_iso(R1)))^(-2) < 1`.

In the code's form `psi = 1 + u(rbar) + m_p/(2 rbar)` with u regular:

    m_p = 2b = M/a,   u = a - 1 for rbar <= rbar(R0),   u = -m_p/(2 rbar) for rbar >= R1,
    M = m_p (1 + u(0)),   rbar_throat = m_p/(2(1 + u(0))) = M/(2a^2)   [VERIFIED: sym, s1]

(the standard puncture-mass relation). For the data set: a = 0.976592, m_p = 1.023969 M,
u(0) = -0.023408, rbar_throat = 0.524256 M, rbar(R0) = 3.055588 M; the time-symmetric form
and the quadrature agree to 3e-16 below R0 (run `D-bh-dress-20261115-043445-b782009`,
`es.json`). Beyond the table the code continues u as `u_N rbar_N/rbar = -m_p/(2 rbar)`
(exact, psi = 1) and KL, KT as rbar^(-3/2) (exact for the Painleve-Gullstrand exterior),
so `exterior = pg` is exact for these data.

## 5. The dust region and the join to the comoving wall

Marginally bound Lemaitre-Tolman-Bondi dust on a slice of constant dust proper time, in
areal coordinates `ds^2 = -dtau^2 + (dR - v dtau)^2 + R^2 dOmega^2`, `v = sqrt(2m(R)/R)`:
lapse 1, flat 3-metric, `KT = -v/R`, `KL = -dv/dR`, `KL = d(R KT)/dR` (S_i = 0), and
`4 KL KT + 2 KT^2 = 4 m'/R^2 = 16 pi rho` with `rho = m'/(4 pi R^2)` [VERIFIED: sym, s3].
This is the f = 1 member of section 2 with m(R) in place of M; in vacuum `KL = +v/(2R)`,
in a homogeneous region `KL = KT = -H`, `H^2 = 8 pi rho_0/3` [VERIFIED: sym, s3]
(item 1: agreement for the pieces used).

Join at the wall: m continuous (`dm/dR = 4 pi R^2 rho` bounded) and KT continuous (F1); KL
jumps only with the density: for a sharp wall `[KL] = 4 pi rho_0/KT = -(3/2) H`
(Einstein-Straus matching `M = 4 pi rho_0 R_w^3/3`, `H^2 R_w^3 = 2M`) [VERIFIED: sym, s3].
The data set uses smooth edges instead (core's test 2 on `core/id-extrinsic`,
`tracks/core/JOURNAL-id.md` entry 4, found the Hamiltonian residual non-convergent at a
sharp surface); with `rho_0` fixed by `m(R_w + w_in) = 4 pi rho_0 (R_w + w_in)^3/3` the dust
between the edges is exactly Einstein-de Sitter.

## 6. The mass inside the comoving wall is constant

LTB in comoving coordinates, `ds^2 = -dtau^2 + R_r^2/(1 + 2E(r)) dr^2 + R^2 dOmega^2`
[VERIFIED: sym, s3]: `G^tau_r = 0` identically; `m = (R/2)(Rdot^2 - 2E)`;
`dm/dtau = -(R^2 Rdot/2) G^r_r = -4 pi R^2 Rdot p_r`; `dm/dr = 4 pi R^2 R_r rho`. Dust has
p_r = 0, so m is constant along every dust world line (equivalently Hayward's
`u^a grad_a m = 4 pi R^2 (T_a^b - delta_a^b T) u^a grad_b R = 0` for dust). The innermost
dust shell (the wall) has m = M for all tau before shell crossing, and by Birkhoff the
vacuum bubble inside it is Schwarzschild of mass M: **the black-hole mass is exactly
constant while the wall is comoving**, whatever the expansion outside. The wall follows
`R_w(tau) = (R_in^(3/2) + (3/2) sqrt(2M) tau)^(2/3)` [VERIFIED: sym, s3]; every shell
follows the same law with its own m(R0); since R0 and m(R0) increase outward, no shell
crossing occurs for tau > 0. A particle at rest in the slice at R0 inside the transition
has `2E = -(1 - f^2) 2M/R0 < 0` and follows the cycloid (rises to `R0/(1 - f^2)`, then falls
into the hole) [VERIFIED: sym, s3, the parametric solution].

## 7. Disagreements with item 2 (and precisions)

1. **Puncture term.** Item 2: "f = 0 inside some radius: ... psi = 1 + m/(2 rbar)". With
   psi = 1 at infinity (the code's normalization) and psi = 1 wherever f = 1, the
   time-symmetric region has `psi = a + b/rbar` with a < 1 (section 4). In the code's form the
   bare puncture mass is **m_p = M/a = 1.0240 M**, and u(0) = a - 1 = -0.0234 (data set);
   `M = m_p (1 + u(0))`. Putting m_p = M would give a black hole of mass 0.9766 M.
2. **Throat location.** Item 2: "Between, the throat sits where dR/dl = 0". With the
   required f the throat is not in the transition but inside the f = 0 region, at the
   bifurcation sphere R = 2M (rbar = M/(2a^2) = 0.5243 M). A throat inside the transition
   (f > 0 there) sits at R < 2M and is anti-trapped.
3. **"f = 0 inside some radius"** must say: f = 0 at R = 2M, to sufficient order for the
   time-symmetric second sheet (F3, F4); in practice f = 0 on [2M, R0] with R0 > 2M.
4. **"Any KT(R) gives a slice"**: only along one sheet; KT must be smooth along the slice
   and W^2 > 0 away from the throat (section 2).
5. **Outgoing PG slice "holds no future horizon: unsuitable"**: agreed; the decisive defect
   is that it reaches R = 0, the white-hole singularity (Kretschmann 48 M^2/R^6), and all its
   spheres with R < 2M are anti-trapped.
6. **"f = 1 at and beyond the bubble wall"**: agreed; the necessary condition is f(R_in) = 1
   (F1) and f = 1 throughout marginally bound dust.
7. **Format-2 table plus puncture**: agreed, with the table's u carrying -m_p/(2 rbar)
   outside R1 (the table's own "mass" `2 rbar_N u_N = -m_p` is negative) and the puncture
   component of bare mass m_p (not M).
8. Not in item 2, but needed by whoever reads the run: psi = 1 outside the ball, so a mass
   read from the 1/r tail of psi is zero; the exterior mass M_tot shows only in K_ij ~
   r^(-3/2) (the Painleve-Gullstrand exterior is not asymptotically flat in the ADM sense).
   Masses must be read as Misner-Sharp or horizon masses.

No disagreement found with: the momentum constraint, the Misner-Sharp relation, the use
of a format-2 table, the constancy of the mass inside the comoving wall, and the dust-side
KT, KL of item 1.

## 8. Checks of the data (numbers with run ids)

- Offline, run `D-bh-dress-20261115-042704-f3da881` (`offline_check.json`; figures
  `figs/check_1d.png`, `figs/check_3d.png`): 1D radial momentum residual of fourth order
  (orders 3.80, 3.95, 3.99 in the curvature transition; 3.44 to 3.85 at the inner edge;
  3.60 to 3.93 at the outer edge, spacings 0.8 to 0.1 M); the 1D Hamiltonian residual is at
  round-off in the flat region (pointwise there) and in the puncture region (the radial
  fourth-order Laplacian is exact for psi = a + b/rbar), fourth order in the transition.
  3D generic 3+1 residuals (no conformal-flatness identity used), fourth order in all seven
  sub-boxes (throat, puncture region, start and middle of the transition, inner and outer
  dust edge, end of the table): measured orders between the two finest spacings 3.85 to
  4.07, between the two coarsest 3.49 (inner-edge momentum) to 4.14; where the exact
  residual is at round-off (flat dust, exterior) it stays there. Fields evaluated through
  the table as `nrpic_cf` evaluates it give the same residuals (largest difference 11 per
  cent, momentum, start of transition, h = 1/16 M), except that in the flat region the
  table-evaluated H sits at a round-off floor of 1e-13 (cancellation of u against
  m_p/(2 rbar) under second differences) instead of 1e-19.
  Table interpolation at drbar = 0.02 M: largest relative error 1.0e-9 (KL), 6.5e-13 (u);
  lapse column 4.5e-6 (absolute, next to rbar = 0, where alpha = psi^-2 ~ rbar^2).
- Inside AthenaK at t = 0 (nrpic_cf of `core/id-extrinsic`, commit 408df57, processor
  build of `wt/core-id`, sha256 7d1292d0...): runs `D-bh-dress-20261115-043002-d51c7f2`
  (dx = 1 M), `D-bh-dress-20261115-043033-4df1e76` (dx = 1/2 M), analysis
  `D-bh-dress-20261115-043406-4df1e76` (`code_t0.json`, `figs/code_t0.png`). In the
  offline box "mid transition" the code's max |H| is 8.4e-9 then 1.4e-10 and max |M| 2.4e-8
  then 4.4e-10 (order 5.9 and 5.8: the code's stencils are of higher order than my
  fourth-order check, whose values at the same spacings are 1.5e-6, 8.9e-8 and 5.9e-7,
  3.8e-8); at the inner dust edge the code's max |M| is 1.1e-5 then 1.1e-6 (order 3.2;
  offline at h = 1/2 M: 2.4e-6); the deposited E equals rho at the cell centres to 1.1e-13
  (relative 3e-8, the float32 of the dump). Near the puncture (r < 3 M) the code's H is
  O(1) and does not converge at these spacings (throat not resolved), as predicted.
