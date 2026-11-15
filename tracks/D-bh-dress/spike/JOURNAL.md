# Journal of work package D-pre-2 (spike in the probe limit)

Helper of D-bh-dress. Predictions are written before each registered run; outcomes after,
also when a prediction failed. Units G = c = m_BH = 1 unless stated; R_S = 2 G m.

## 2026-11-15 Setup and development probes (not registered)

- Source fetched: arXiv:1305.2619 v1 (SFW), `kb-data/raw/arxiv/1305.2619/v1/src/SFWpaper.tex`;
  Kerr sequel arXiv:1707.06302 v2 (FdRW) already in `kb-data/raw/arxiv/1707.06302/v2/src/`.
- [VERIFIED] SFW eq. (3.19) (SFWpaper.tex lines 412-418) and its dimensionless form (4.13)
  (lines 660-663) use oint sqrt(V) dr, i.e. u^r, not the canonical u_r = sqrt(V)/(1-2Gm/r);
  their Kerr form (line 349) has the factor r^2/Delta. FdRW say so in a footnote
  (kerrdm.tex line 919: "the Schwarzschild limit of the radial invariant in Eq. (3.19) in
  SFW is missing a factor of r^2/Delta = 1/(1-2Gm/r)"). `spike_lib.py` computes both.
- [VERIFIED] SFW Fig. 3 does not state the black-hole mass; the only value in the paper is
  m = 4e6 M_sun in Sec. V (line 808). The halo is M = 1e12 M_sun, a = 20 kpc (line 124).
- Development probes of `spike_lib.py` (unit checks, not results): E_min of SFW eq. (3.17)
  equals a brute-force scan of the non-captured region to the grid spacing (1e-5) at
  r = 4.05 ... 20; the Hernquist action table inverts to 1e-5 in delta = 1 - eps against
  direct bisection; Kepler limit of the relativistic radial action at E = 1 - 1e-4,
  L = 50: 130.34 vs 130.13 (relativistic correction), period 2.2223e6 vs 2.2214e6.
- Seen during development, before the predictions below (so not a test): with
  m = 4e6 M_sun our relativistic Hernquist spike peaks at 2.44e18 GeV/cm^3 near r = 7.6 Gm,
  while the digitized SFW Fig. 3 peaks at 10^19.40 = 2.5e19 GeV/cm^3; the digitized FdRW
  Schwarzschild curve (fig_rho_hern.pgf) peaks at 2.44e18 at r = 7.68 Gm. The red
  "initial Hernquist profile" line of SFW Fig. 3 (10^10.892 GeV/cm^3 at r = 2 R_S, slope -1)
  implies R_S = 9.7e-8 pc, i.e. m = 1.0e6 M_sun if a = 20 kpc and M = 1e12 M_sun.

## P1 Reference calculation against the printed numbers and curves (prediction)

Run: `spike_reference.py` (registered as D-bh-dress-<time>-<commit>, kind scouting).

Predictions, each with what refutes it:
1. Constant f (SFW Fig. 1): relativistic rho vanishes at r = 4 Gm, GS at 8 Gm; our
   relativistic peak 0.87e8 GeV/cm^3 at r = 7.6 +- 0.3 Gm and GS peak 0.336e8 at 15.9 Gm
   (digitized SFW Fig. 1). Refuted if our peak values differ from the digitized ones by
   more than 2 %. SFW text (line 443): GS peak "a factor of three smaller"; GS with
   8 -> 4 Gm peaks "about 15 % higher" than the relativistic result. Refuted if our
   ratios are outside 2.5-3.5 and 10-20 %.
2. Hernquist, m = 4e6 M_sun, canonical action: our curve equals the FdRW Schwarzschild
   curve (blue dash-dot of fig_rho_hern.pgf) within 3 % at 5 < r/Gm < 40. Refuted if not.
   FdRW say the spike meets the Hernquist profile at 12.4 pc (kerrdm.tex line 1053):
   refuted if our crossing is outside 11-14 pc.
3. Hernquist, m = 1.0e6 M_sun, SFW action (as printed): our relativistic and
   non-relativistic (GS) curves reproduce SFW Fig. 3 within 0.1 dex for
   0.45 < log10(r/R_S) < 4; refuted if the offset exceeds 0.2 dex anywhere there.
   Expected peaks: relativistic 10^19.40 at log10(r/R_S) = 0.58, GS 10^18.86 at 0.94.
4. The canonical action lowers the inner spike relative to the SFW action by a few per
   cent at the peak (5 % at r = 7.6 Gm in the development probe), less than 1 % beyond
   100 Gm. Refuted if the difference exceeds 10 % at the peak or changes sign.
5. Relativistic/GS ratio at the peak (Hernquist): SFW text (line 124) "2-3 times higher";
   at r > 50 R_S the two agree "with standard results". Refuted if our peak ratio is
   outside 2-4 or the curves differ by more than 5 % beyond 100 R_S.

## P1 outcome (run D-bh-dress-20261115-123029-4df1e76, 132 s, 4 cores)

Numbers from `scratch/D-bh-dress/D-bh-dress-20261115-123029-4df1e76/reference.json`;
figures `figs/ref_constf.png`, `figs/ref_hernquist.png` (looked at).
1. Constant f [VERIFIED against SFW Fig. 1]: our relativistic peak 0.8699e8 GeV/cm^3 at
   r = 7.579 Gm, digitized 0.8699e8 at 7.580 Gm; GS peak 0.3359e8 at 16.00 Gm, digitized
   0.3359e8 at 16.02 Gm. Largest deviation from the digitized curves 0.26 % (relativistic,
   8.5-95 Gm) and 2.2 % (GS, only at its steep edge 8.5-9 Gm); 0.38 % against the FdRW
   Schwarzschild curve (fig_rho_a). Zero points 4 Gm and 8 Gm (by construction of the
   limits; E_min checked by brute force). Peak ratio relativistic/GS 2.59: inside the
   predicted 2.5-3.5 (SFW text: "a factor of three"). GS with 8 -> 4 Gm peaks 9.2 % above the
   relativistic curve, not "about 15 %" (SFW line 443): this prediction FAILED. Since our
   curves reproduce SFW's own Fig. 1 to 0.3 %, the 15 % of the text does not follow from
   their figure [JUDGEMENT].
2. Hernquist, m = 4e6 M_sun, canonical action [VERIFIED against FdRW fig_rho_hern]:
   largest deviation 1.0 %, median -0.07 % at 5-39 Gm; peak 2.437e18 GeV/cm^3 at
   7.75 Gm (digitized 2.439e18 at 7.73 Gm). The spike meets the initial Hernquist profile
   at 12.42 pc (FdRW: 12.4 pc). With the SFW-printed action the curve is 3-10 % higher
   than FdRW's: FdRW's Schwarzschild curve uses the corrected (canonical) action.
3. SFW Fig. 3 [VERIFIED to 0.04 dex]: with m = 1.0e6 M_sun our relativistic curve (SFW
   action) agrees with the digitized SFW Fig. 3 to 0.039 dex at most (median 0.010) for
   0.45 < log10(r/R_S) < 4, our canonical curve to 0.030 dex, our GS curve with the
   non-relativistic one to 0.033 dex. Peaks: SFW 10^19.399 at log10(r/R_S) = 0.591; ours
   10^19.412 at 0.583 (SFW action), 10^19.390 at 0.588 (canonical). So SFW Fig. 3 was drawn
   for m = 1e6 M_sun (or a Schwarzschild radius of 9.6e-8 pc), not the 4e6 M_sun of their
   Sec. V [JUDGEMENT from the fit; the red Hernquist line of Fig. 3 gives the same m
   independently]. The digitization cannot tell which action SFW used (difference 0.02 dex
   at the peak). Beyond log10(r/R_S) = 4 SFW's curves bend to a slope of about -1.9 while
   ours keep -7/3 = -(9-2 gamma)/(4-gamma) for gamma = 1 [BACKGROUND formula]; the
   relativistic and Newtonian curves of SFW bend alike, so this is a feature of their
   numerics, not of relativity [JUDGEMENT].
4. Canonical vs printed action: the printed (SFW) action gives +6.9 % at 6 Gm, +5.2 % at
   7.7 Gm, +4.3 % at 10 Gm, +1.9 % at 95 Gm, +1.1 % at 210 Gm, +0.3 % at 1e3 Gm. The
   prediction "below 1 % beyond 100 Gm" FAILED (it is 1.9 % at 95 Gm and falls below 1 % only
   beyond about 250 Gm); the peak value (5 %) was as predicted.
5. Hernquist peak ratio relativistic/GS: 3.39 (canonical), 3.57 (SFW action), inside the
   predicted 2-4 (SFW text: "2-3 times"). Beyond 100 R_S the canonical and GS curves differ
   by 0.92 % at most (predicted < 5 %).
Checks: E_min (SFW eq. 3.17) = brute-force scan to 1e-5 at 9 radii; Hernquist table
delta error median 7e-6, max 1e-4 (11 of 400 test points outside the table, none of the
density evaluations was); Kepler limit at E = 1 - 1e-6, L = 300: I_r 2557.97 vs 2557.93,
T_r 2.22145e9 vs 2.22144e9.

## P2 AthenaK probe test (prediction, written before the registered runs)

Development probes (unregistered, `scratch/D-bh-dress/tmp/`, 2400 + 200 particles, 500 and
1500 M) showed: CPU executable 1.2-1.4e6 particle updates per second per core; in the
analytic Kerr-Schild mode there is NO excision (`NrpicExcise` acts only for metric = mesh,
athenak/src/particles/nrpic.cpp:627): a particle that crosses r = 2 continues to r ~ 0.004,
its push turns non-finite, it is flagged (PGID = -2) and keeps its last finite state, but it
is never removed; so "removed" is measured here as "KS r < 2 in a snapshot". In the probe all
100 predicted plungers crossed and none of the 100 bound near-separatrix probes did; four
plungers with |q| = 1.4e-4 ... 1.5e-2 crossed up to 0.36 M EARLIER than the exact geodesic
(checked with an ODE solution to 1e-8 M), which I attribute to the pusher's energy error
near the unstable circular orbit (to be tested by halving dt, P2e).

Setup: initial data `sample_spike.py` (seed 20261115): species 0, 48000 particles from the
final DF (canonical action, m = 4e6 M_sun, M = 1e12, a = 20 kpc) with E <= E_cut = 0.99
(apocentres <= ~92 Gm), 12 files; species 1, 2400 loss-cone probes (E in [0.95, 0.99],
L^2 = L_c^2 (1 +- q), q log-uniform in [1e-4, 1e-1]). Run A: 12 CPU processes, species 0,
dt = 0.05 M, t = 0 ... 20000 M (9 radial periods of the widest orbit, ~100 of an orbit with
semi-major axis 10 Gm), snapshots every 250 M. Run B: species 1, dt = 0.05, 1500 M,
snapshots every 2 M. Run B2: as B with dt = 0.025.

Predictions and refutation criteria:
P2a (sampler) at t = 0 the binned species-0 counts (log bins 4-92 Gm, bins with more than 20
    expected) agree with the reference dN/dr = 4 pi r^2 rho / sqrt(1-2/r) of the truncated DF:
    chi^2/dof within 1 +- 3 sqrt(2/dof). Refuted otherwise.
P2b (stationarity) chi^2/dof stays within the same band at every snapshot, with no trend;
    the counts in 4-6, 6-10, 10-20 and 20-50 Gm stay within 3 sigma (Poisson) of the
    expected value at every snapshot, and their late-half means within 3 sigma/sqrt(1)
    (snapshots are correlated, no averaging gain is assumed). Refuted by a drift in any range.
P2c (invariants) max over snapshots of |dE/E|: median < 1e-8, max < 1e-5 (pericentres down
    to 4.2 Gm); |dL/L| < 1e-10 (midpoint rule conserves L_z exactly for a = 0). Refuted above.
P2d (empty loss cone) no species-0 particle reaches r < 2 (orbits within lambda < 1e-8 of the
    separatrix were not drawn). Refuted by any crossing.
P2e (loss-cone boundary) every species-1 particle inside the loss cone (q < 0) crosses r = 2,
    none outside (q > 0) does, for |q| >= 1e-4; the first snapshot inside lies in
    [t_pred - 1 M, t_pred + 2 M); with dt halved (B2) the early crossings shrink by about
    4x (second order). Refuted by any misclassified particle, or by offsets that do not
    shrink with dt.

## P3 particle budget (prediction, before the run of particle_budget.py)

Equal-mass particles drawn from the truncated DF: from the P2 initial data (r quantiles: 10 %
inside 13.2 Gm, 50 % inside 32.6 Gm, E_cut = 0.99) about 30 % lie inside 20 Gm; the
innermost of 8 log bins in 5-20 Gm holds the fewest. Prediction: for E_cut = 0.99 about
3e4 particles in total give 100 per bin (10 %); the requirement grows like
N(<r_apo)/N(<20) ~ (r_apo/20)^(2/3) (number profile of a rho ~ r^-7/3 spike), i.e. about
4.6x per decade of the largest apocentre. Refuted if the growth per decade is outside 3-7x.
