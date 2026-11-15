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

## P2 outcome

Runs: initial data D-bh-dress-20261115-123734-25227d4 (10.7 s); run A
D-bh-dress-20261115-123755-25227d4 (12 CPU processes, 1151 s, 3.8 core-hours, 48000
particles x 400000 steps); run B D-bh-dress-20261115-123801-25227d4 (94 s); run B2
D-bh-dress-20261115-123936-72cd01e (154 s); analyses D-bh-dress-20261115-125739-a18d74d
(A), -124246-aa9dee7 (B), -124249-aa9dee7 (B2), -124257-aa9dee7 (B vs B2); a first analysis
of A, D-bh-dress-20261115-125724-464611f, FAILED (empty-array reduction when no species-1
particle is present; fixed in a18d74d and rerun). No card-hour used. Figures looked at:
`figs/stationarity_profile.png`, `figs/stationarity_time.png`, `figs/invariants_losscone.png`,
`figs/losscone_dt0.05.png`, `figs/losscone_dt0.025.png`, `figs/crossing_dt.png`.
Sampler checks (ic_summary.json): no envelope violation in 192000 orbit trials and in the
phase sampling; 52 of 52800 grid nodes had no orbit (E at the ISCO or lambda at the circular
end) and carry weight 0; converted states reproduce E and L to 4e-16 and 1.1e-15.

P2a confirmed: chi^2/dof = 1.48 at t = 0 (dof 23, band 0.12-1.89).
P2b confirmed: chi^2/dof over the 81 snapshots median 0.98, range 0.44-1.69, no trend.
    Counts in 4-6 / 6-10 / 10-20 / 20-50 Gm (expected 207 / 1983 / 9114 / 26365) stayed
    within -2.9 ... +2.7 sigma, -2.7 ... +1.6, -2.2 ... +1.3, -1.8 ... +1.3 sigma at every
    snapshot; late-half means 0.976 (sigma 0.070), 0.994 (0.022), 0.999 (0.011),
    0.998 (0.006) of the expected value. The binned profile stays on the reference for
    20000 M, i.e. 9 radial periods of the widest orbits and about 100 of orbits with a
    semi-major axis of 10 Gm.
P2c: |dE/E| (max over snapshots) median 8.5e-9, 99th percentile 6.5e-7, max 1.3e-6
    (confirmed; the error grows steeply towards small pericentre, 1.3e-6 at r_p = 4.2 Gm,
    1e-11 at 80 Gm). |dL/L| median 1.6e-12, p99 3.6e-11, max 1.9e-10: the prediction
    "< 1e-10" FAILED by a factor 2 for particles with pericentres of 4-5 Gm; L_z is a
    quadratic invariant of the implicit midpoint rule, so I expect this to be the
    accumulation of the fixed-point tolerance (1e-12) over 4e5 steps [JUDGEMENT, not tested].
P2d confirmed: none of the 48000 species-0 particles reached r < 2 in 20000 M.
P2e confirmed: all 1200 loss-cone probes (q < 0) crossed r = 2, none of the 1200 probes
    outside (q > 0) did, for |q| from 1e-4 to 1e-1, in both B and B2. No particle came back
    out of r < 2 and no snapshot record was non-finite. Crossing time measured from the last
    snapshot outside (exact remaining infall time with the particle's own E, L): every probe
    crosses EARLIER than the exact geodesic, by -0.024 M (median) and at most -0.75 M with
    dt = 0.05, by -0.0060 M and at most -0.19 M with dt = 0.025; the ratio is 3.997 (median;
    3.98 / 4.00 / 4.00 in the |q| decades 1e-4, 1e-3, 1e-2), and the offset scales as 1/|q|
    (`figs/crossing_dt.png`): a second-order phase error of the pusher, amplified by the
    whirl near the unstable circular orbit. With the coarse 2 M snapshots the first-inside
    test was within [t_pred - 1, t_pred + 2) for all probes, as predicted.

## P3 outcome (run D-bh-dress-20261115-123848-72cd01e, 17.5 s)

Total equal-mass N for 100 (400) particles in each of 8 log bins in 5-20 Gm, DF truncated
at E <= E_cut (largest apocentre in brackets): 1 - E_cut = 1e-2 (113 Gm): 3.0e4 (1.2e5);
1e-3 (1.0e3 Gm): 2.8e5 (1.1e6); 1e-4 (1.0e4 Gm): 1.5e6 (6.1e6); 1e-5 (1.0e5 Gm): 7.4e6
(3.0e7); 1e-6 (1.0e6 Gm): 3.5e7 (1.4e8). Fraction of the particles inside 20 Gm: 0.236,
0.025, 0.0047, 0.00097, 0.00021. The predicted 3e4 for E_cut = 0.99 is confirmed; the
growth per decade of apocentre is 9.5x, 5.4x, 4.8x, 4.7x: the first decade is outside the
predicted 3-7x (FAILED there; the truncation at E_cut = 0.99 removes part of the density
inside 20 Gm itself, see the full-DF curve of `figs/stationarity_profile.png`), the later
ones approach the asymptotic (10)^(2/3) = 4.64 as predicted.
Deposit noise for a self-gravitating run (scaling of docs/results_cluster_test.md 2(d):
relative L2 noise 0.24-0.28 at 1.1 particles per occupied cell, N^-1/2): 6.4e7 particles
inside 20 Gm for 5 % noise on cells of 0.25 Gm [JUDGEMENT, extrapolated].

# Wave 2: the Kerr spike baseline (helper kerr_spike, 2026-11-15)

Reference: Ferrer, da Rosa & Will 2017, arXiv:1707.06302 ("FdRW"), fetched again with
nrpic-fetch-arxiv (v2, `kb-data/raw/arxiv/1707.06302/v2/src/kerrdm.tex`, 1709 lines).
Method read at the source: currents eqs. (397)-(413) (lines 394-416), capture criteria
(lines 462-473), adiabatic invariants (lines 525-549), constant f and MC (lines 709-765),
Hernquist (lines 840-920), planar orbits (appendix B, lines 1318-1703).

## Development (not registered, scratch/D-bh-dress/tmp/kerr_dev/), seen before the predictions

- `kerr_lib.py`: the capture boundary is computed as C_crit(E, Lz; r) = min over
  r_+ < r' <= r of C_V(r') = P/Delta (R is linear in C, so "R < 0 somewhere inside r" is
  exactly FdRW's two criteria); integration variables l = Lz/sin(theta) (cosine-mapped),
  phi with C = C_U + (C_V - C_U)(1 - cos phi)/2, E = E_min + (1 - E_min) s^2.
- Bugs found and fixed in development: (i) the endpoint test of the C_crit search was
  fragile (a minimum at r itself passed as interior: E_min(4.2 Gm) came out 0.9775 instead
  of SFW's 0.97996); (ii) the first grid in r' (log-spaced from r_+) was too coarse near r;
  (iii) composite Gauss-Legendre in l converged slowly at the inner edge (1/sqrt edges):
  replaced by l = l_mid - l_half cos(psi).
- After the fixes, a = 0: E_min equals SFW eq. (3.17) to 2e-8 for 4.05 <= r <= 6 and 5e-7
  beyond; constant-f density equals spike_lib.rho_constf_rel to 2e-4 at 4.05-20 Gm;
  Hernquist density equals SpikeModel.rho_rel (canonical) to 3e-4 at 5-20 Gm.
- a = 0.8, equator, constant f: rho(10 Gm) = 0.8889e8 GeV/cm^3 at two resolutions
  (7e-5 apart); E_min(10 Gm) full phase space 0.928463, planar orbits 0.928462.
- A coarse dry run of kerr_reference.py (--nr 6, 62 s) showed: E_min(10 Gm) against the
  digitized figemin to 6e-5; the planar-orbit curves of figequator1 are 0.2507-0.2510 of
  eq. (584) as printed (a factor 1/4); peak ratios (coarse grid, peaks unresolved):
  constant f 1.221 (a = 0.8 / 0), Hernquist 1.35 (0.8 / 0.5), 1.55 (0.8 / 0).

## K1 prediction (before the registered run of kerr_reference.py --nr 44)

1. a = 0 through the Kerr code: constant-f and Hernquist densities equal the wave-1
   Schwarzschild references (spike_lib) to < 1e-3 for 4.05 < r < 40 Gm. Refuted above 1e-3.
2. Constant f, equator, a = 0.5 and 0.8 (fig_rho_a): within 2 % of the digitized curves
   where they exceed 10 % of their peak (FdRW's MC: "<~ 1 %", line 758); peaks
   0.926e8 at 7.25 Gm and 1.058e8 at 6.53 Gm (digitized) within 1.5 % and 0.3 Gm.
3. Constant f, a = 0.8, theta = 0 and pi/3 (fig_rho_theta): within 3 %.
4. Hernquist (m = 4e6 Msun, M = 1e12 Msun, r_s = 20 kpc), equator a = 0.5, 0.8
   (fig_rho_hern) and a = 0.8 at theta = 0, pi/3 (fig_angle_hern): within 3 %; peaks
   2.81e18 at 7.11 Gm and 4.08e18 at 5.07 Gm within 3 % and 0.3 Gm.
5. Inner edge at the equator equals r_mb+ = 2 - a + 2 sqrt(1 - a) (FdRW eq. mborbit) to
   1e-4: 2.9142 (a = 0.5), 2.0944 (a = 0.8). Refuted above 1e-3.
6. E_min(10 Gm, equator) vs a: within 2e-4 of figemin for 0.1 <= a <= 0.99.
7. C_crit(a = 0.75, E = 0.97, Lz = 2) = 10.3 (crit_orbit caption, line 498): ours in
   [10.25, 10.35].
8. The general routine on the axis equals FdRW's closed form eq. (825) to 1e-3.
9. Planar orbits (figequator1, a = 0, 0.5, 0.8): after one constant scale factor the
   shapes agree within 3 %; the factor is the same for the three spins (about 1/4).
10. Text claims: constant f, peak a = 0.8 / a = 0 = 1.20-1.24 ("20 %", line 213); Hernquist
    peak ratios equal the digitized ones within 2 % (1.45 for 0.8 / 0.5, 1.67 for 0.8 / 0),
    so the text's "approximately 35 %" (line 929) is not what the figure shows, its
    "around 70 %" (line 199) is.

## K1 outcome (runs D-bh-dress-20261115-171134-38634d6, 103 s, and the rerun with the
## deviations taken at our own nodes, D-bh-dress-20261115-171615-8adbbdd, 105 s, 8 cores)

Numbers from `scratch/D-bh-dress/D-bh-dress-20261115-171615-8adbbdd/kerr_reference.json`;
figures `figs/kerr_ref_constf.png`, `figs/kerr_ref_hernquist.png`, `figs/kerr_ref_checks.png`
(looked at). The first run compared on a dense grid interpolated linearly in our curve,
which put a sawtooth of up to 1 % on the residuals beyond 20 Gm; the rerun compares at our
nodes with FdRW's drawn polyline (the PGF curve is what they plotted).
1. Confirmed: a = 0 equals the wave-1 references to 8.9e-4 (constant f, largest at
   4.07 Gm next to the edge) and 3.8e-4 (Hernquist) on 4.07-40 Gm.
2. Confirmed: constant f, equator: a = 0.5 within 0.88 %, a = 0.8 within 0.95 % (median
   0.12-0.15 %); peaks 0.9271e8 at 7.31 Gm (FdRW 0.9256e8 at 7.25) and 1.0604e8 at 6.61 Gm
   (FdRW 1.0585e8 at 6.53).
3. Half confirmed: theta = 0 within 0.78 % (peak 0.9691e8 at 7.02 Gm, FdRW 0.9669e8 at
   7.00). theta = pi/3 FAILED inside 8 Gm: FdRW's curve rises 1-1.5 Gm further out than ours
   (ours/FdRW = 2.0 at 3.6 Gm, 1.06 at 6 Gm) and lies 1-2.7 % above ours at 8-17 Gm; the
   peak values agree (1.0374e8 vs 1.0352e8). No single polar angle of ours reproduces their
   curve (scratch probe: theta = pi/6, pi/4, 0.4 rad tried; their inner part is near
   theta ~ pi/5, their outer part near the equator). Their Hernquist theta = pi/3 curve does
   not show this shift. [JUDGEMENT] a problem of that one FdRW curve; unresolved.
4. FAILED for the Hernquist DF at a != 0 off the axis: a = 0 within 1.4 %, theta = 0 within
   1.5 %, but ours is lower than FdRW by 0.5 % at 20 Gm, 1 % at 12 Gm, 4 % at the a = 0.8
   peak (3.922e18 at 5.06 Gm against 4.083e18 at 5.07 Gm) and 6-18 % at the inner edge
   (2.4-3 Gm); a = 0.5: peak -0.9 %, up to -6 % at the edge; a = 0.8, theta = pi/3: peak
   -2.3 %, up to -12 %. Checks made after the failure (development probes, scratch): the
   Kerr radial and polar actions equal independent scipy quadratures (numpy roots) and the
   turning points of nrpic.kerr.radial_roots (mpmath) to 1e-10 at five orbits; doubling
   all quadrature orders changes rho by 1e-4 at 3, 5.07 and 8 Gm; replacing
   L = |Lz| + I_theta/2pi by sqrt(C) changes rho by 0.1 %. Constant f (same capture domain,
   same currents) agrees to 1 %, so the difference sits in f, i.e. in the action matching
   of orbits with Lz != 0 and a != 0. Cause not identified [TO VERIFY]; FdRW's own text
   ratio "approximately 35 %" (a = 0.8 over 0.5) lies between ours (1.406) and their figure
   (1.451), their "around 70 %" (over a = 0) is their figure (1.674), ours is 1.609.
5. Confirmed: inner edge at the equator 2.91431 (a = 0.5) and 2.09525 (a = 0.8) against
   r_mb+ = 2.91421 and 2.09443 (FdRW eq. mborbit): 1e-4 and 8e-4 [the prediction said 1e-4;
   the bisection on E_min < 1 is limited by the E grid near E = 1, so 8e-4 FAILS the stated
   1e-4 but passes 1e-3]. Off the plane: r_min = 2.2410 (theta = pi/3), 3.6398 (axis) at
   a = 0.8; 3.0282, 3.8697 at a = 0.5. The counter-rotating edges r_mb- = 4.949, 5.483 are
   visible as kinks of the planar curves (figs/kerr_ref_checks.png).
6. Confirmed: E_min(10 Gm, equator) within 5.9e-5 of figemin for 0.1 <= a <= 0.99.
7. FAILED: C_crit(a = 0.75, E = 0.97, Lz = 2) printed by the script is 7.09 at r = 30 Gm,
   not 10.3. This is a mistake of the check, not of the library: at r = 30 Gm and E = 0.97
   the point lies beyond the outer maximum of C_V, so the minimum over (r_+, 30] is the
   endpoint (C_V(30) = 7.09 < C_V(r_unst)); FdRW's 10.3 is the local minimum of C_V at the
   unstable orbit. To be rechecked with r inside the bound region (open).
8. Confirmed: on the axis (a = 0.8) the general routine equals FdRW eq. (825) to 3.6e-5
   (4.5 Gm), 4.2e-5 (7 Gm), 3.5e-5 (15 Gm).
9. Confirmed: one constant factor 0.2500-0.2505 for a = 0, 0.5, 0.8 maps our eq. (584)
   onto figequator1; shapes then agree within 3.3 % (a = 0, 0.5, largest at the inner edge)
   and 1.4 % (a = 0.8). So FdRW's figure was drawn with 1/4 of the prefactor printed in
   their eq. (584) (8 f/sqrt(r)) [VERIFIED as a property of figure and equation].
10. Constant f: 1.2192 (ours) against 1.2190 (figure) for a = 0.8 over 0: "20 %" confirmed;
    a = 0.8 over 0.5: 1.1438 / 1.1436. Hernquist: see item 4 (ours 1.406 and 1.609; the
    prediction "within 2 % of the digitized ratios" FAILED: 3.1 % and 3.9 % below).
Also: viterate caption (line 1508), Lz^max = 4.829 at x = 10, E0 = 0.9997: eq. (lmax) as
printed (a^2 - x(x-2) under the root) has no real value at x = 10 for any a < 1; with
a^2 + x(x-2) = Delta(x) it gives 4.8753, 4.8328, 4.8287, 4.8226, 4.8125 for a = 0.5, 0.7,
0.72, 0.75, 0.8, i.e. the caption fits a ~ 0.72 (the spin is not stated). [VERIFIED: a sign
typo in eq. (lmax); eq. (lmaxe1) has the + sign.]
Probe after item 7 (development, scratch): with r inside the bound region (8, 12, 15, 20 Gm)
C_crit(a = 0.75, E = 0.97, Lz = 2) = 10.3209 at r_unst = 2.834 Gm, FdRW's 10.3 confirmed.

## K2 setup (development, not registered, scratch/D-bh-dress/tmp/kerr_dev/)

- Slice subtlety found while writing the sampler: f is the density per d^3x d^3p_i on a
  slice of the time coordinate whose Hamiltonian is used, so a sample drawn on t_BL = const
  and placed at t_KS = 0 (what sample_spike.py of wave 1 did, uniform in Schwarzschild time
  along each orbit, then u_r shifted to KS) carries the weight 1/(1 + delta_t' v^r_BL) with
  respect to the stationary state on the KS slice (delta_t' = 2r/Delta): ingoing particles
  are over-weighted by a few per cent inside ~10 Gm. The r histogram at t = 0 is not
  affected (the factor is odd in u_r at first order), the evolution is. sample_kerr.py
  includes the Jacobian (option --slice bl leaves it out, for a control).
- Sampler dry run (3000 particles): acceptance 6.3 %, no envelope violation (largest
  weight/envelope 0.56), conversion BL -> CKS reproduces E, Lz, Q to 4e-16, 3e-15, 4e-14;
  pericentres >= 2.37 Gm, apocentres <= 92 Gm, 17.8 % inside 16 Gm, mean Lz = +0.37.
- Smoke test of the release processor executable (build_cpu_v03, kerr_geodesic.athinput,
  a = 0.8) on 1500 particles for 200 M: 1.31e6 particle updates per second per core;
  max |dE/E| 4.8e-6, |dLz| 8.7e-12, |dQ|/max(Q, 1) 5.4e-6 at t = 200 M.

## K2 prediction (before the registered runs)

Main run: 48000 particles from the Hernquist-grown Kerr DF (a = 0.8, E <= E_cut = 0.99,
KS-slice sampling, seed 20261116), 12 processes of the release processor executable,
midpoint pusher, dt = 0.05 M, t = 0 ... 20000 M, snapshots every 100 M. Reference: the
coordinate density n(r, theta) of kerr_lib with E <= 0.99, integrated over bins of
ln r (2.2-100 Gm) x |cos theta| ([0, 1/3), [1/3, 2/3), [2/3, 1]).
K2a (sampler) at t = 0 the binned counts follow the reference: chi^2/dof within
    1 +- 3 sqrt(2/dof) (bins with > 20 expected); the mean Lz in the r ranges below equals
    the reference number-weighted <Lz> within 3 sigma.
K2b (stationarity) chi^2/dof stays in that band at every snapshot without trend; counts in
    r ranges [r_min, 4), [4, 6), [6, 10), [10, 16), [16, 40) Gm within 3.5 sigma (Poisson)
    at every snapshot (201 snapshots x 5 ranges) and their late-half means within
    3 sigma; the equator/pole contrast (|cos| < 1/3 over |cos| > 2/3, r < 16 Gm) constant
    within 3 sigma. Refuted by a drift or trend in any of these.
K2c (invariants) max over snapshots |dE/E|: median < 1e-7, max < 1e-4; |dLz| < 1e-8
    (quadratic invariant of the implicit midpoint rule, up to the 1e-12 iteration
    tolerance); |dQ| / max(Q, 1): max < 1e-4. Refuted above.
K2d no particle comes within r_+ = 1.6 Gm, and no particle goes below its predicted
    pericentre by more than 1e-3 Gm (orbits within the capture boundary were not drawn).
K2e the mean Lz (net prograde rotation from frame dragging and capture of retrograde
    orbits) stays at its t = 0 value in each r range within 3 sigma.
Control (after the main run): 48000 particles each, same seed, KS-slice and BL-slice
(uncorrected) samples, 3000 M, snapshots every 10 M. Prediction [JUDGEMENT]: the KS sample
stays within Poisson noise of its t = 0 counts; the BL sample shows a coherent transient
of the counts inside 10 Gm (excess first, then oscillation damped by phase mixing) of
1-3 %, i.e. 1-2 sigma per snapshot, visible as a correlated excursion over ~100-300 M.
Refuted (in the sense that the slice matters below the noise of these tests, so wave 1's
Schwarzschild test is not affected at its precision) if the BL run shows no excursion
above 2 sigma in the running mean over 100 M.

## K2 runs so far

- IC D-bh-dress-20261115-172335-9e5ccf9 (145 s, 4 cores): 48000 particles, acceptance
  6.25 %, 1 envelope violation in 8e5 proposals (largest ratio 1.03), 13 of 209 cells
  without a pilot hit (weight 0: their content is checked by the t = 0 chi^2 below);
  invariants of the CKS states equal the drawn ones to 1.1e-15 (E), 4e-15 (Lz), 6e-14 (Q);
  pericentres >= 2.283 Gm, apocentres <= 95.2 Gm, 17.7 % inside 16 Gm, mean Lz +0.436.
- Reference grid D-bh-dress-20261115-172646-ed6a510 (207 s, 4 cores): n(r, theta) on
  73 x 10 nodes, 2.05-100 Gm; no density at 100 Gm.
- Main run D-bh-dress-20261115-172611-1e40191 started (12 processes). A development pass
  of analyze_kerr.py over its first 39 snapshots (to test the script, scratch tmp) showed
  chi^2 = 51.4 / 47 at t = 0, the equator/pole contrast 1.209 +- 0.033 at t = 0 against
  the reference 1.127 (a 2.5 sigma draw; later snapshots 1.08-1.20), and 5 particles below
  their predicted pericentre by up to 3e-3 Gm (energy error 1e-5 near r_p = 2.3 Gm).

## K3 prediction (before the registered run of kerr_budget.py)

Criteria in kerr_budget.py's docstring (8 log bins in 4-16 Gm x 3 bands of |cos theta|;
deposit noise 0.26 at 1.1 particles per occupied cell, N^-1/2, docs/results_cluster_test.md
(d)). Prediction [JUDGEMENT, scaled from wave 1's 3.0e4 for 8 bins in 5-20 Gm without
angular bins]: for E_cut = 0.99 the counting criterion needs N_total = 1e5-3e5 (10 %) and
x4 for 5 %, set by the polar band in the innermost bin; it grows by 4-6x per decade of the
largest apocentre beyond the first decade. The deposit criterion at dx = 0.25 Gm needs
3e7-3e8 particles inside 16 Gm, i.e. 1e8-2e9 in total for E_cut = 0.99, and 8x that at
dx = 0.125 Gm. Refuted if the numbers fall outside these ranges (then the scaling from
wave 1 does not carry over).
