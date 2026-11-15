# Journal of the scope package (A-emd-pbh, G0)

Helper: scope (G0 scoping material). Entries in time order; predictions are written
before the calculation they predict, outcomes after it, failed predictions stay.

## 2026-11-15, reading (no run)

Read at the source the twelve key references of brief S1 (paths under
`kb-data/raw/arxiv/<id>/<version>/src`, all already in the store; the fetch helper printed
the paths without downloading again). Statements with line locators are in
`REFERENCES.md`. Measured costs taken from `docs/TESTLOG.md`, `cosmo/TESTLOG.md` and the
chain logs of `runs/jeans/n1e4_v19` (main checkout, read only).

Two observations from the reading that shape the scope, both [JUDGEMENT] until tested:
1. In arXiv:2609.14218 the particle runs at e = 0.2 are plotted to 250 t_H (file
   `alpha.pdf` of the source), and the smaller the amplitude, the later the lapse
   collapses. A pressureless overdensity that nothing halts collapses after roughly the
   top-hat collapse time of its compaction shell, which grows as mu^(-3/2). The reported
   particle threshold (0.045 < mu_c <= 0.05) may therefore be the amplitude whose collapse
   time equals the run length, not a physical threshold. Test T2 below checks whether the
   numbers allow this reading.
2. arXiv:2507.18312 states that for a typical (Gaussian-curvature) profile spherical
   shell crossing halts the collapse unless delta ~ 1 (its Sec. 2, lines 238-242), while
   arXiv:2609.14218 forms black holes with particles at mu = 0.05 (e = 0.2). Both cannot
   hold for the same profile unless the anisotropy or the numerics make the difference.

## 2026-11-15, predictions for the semi-analytic tests of `scope_calc.py` (before the run)

T1. Hoop criterion of arXiv:2609.14218 (its eqs. for (alpha, beta, gamma) and h-hat, MDPBH.tex
lines 905-919). Prediction: (a) the eigenvalues of -grad D at r = 0 computed by finite
differences of ln Psi agree with the closed form (2 mu/15)(k^2/a^2H^2)(1+3e+p, 1-2p,
1-3e+p) to a relative 1e-6 (step-size limited); (b) the paper's h-hat equals the h of
arXiv:1609.01588 (eq. s_3, apj_nonsphericalpbh.tex line 604) with mu k^2/(a^2H^2) = 6 to
round-off; (c) h-hat(e, 0) agrees with the blue line of the paper's `thre_p0.pdf` read by
eye at e = 0.05, 0.10, 0.15, 0.20, 0.25, 0.30 (0.22, 0.34, 0.41, 0.45, 0.47, 0.48) within
0.02. Refuted if (a) or (b) differs by more than 1e-4, or (c) by more than 0.03 at any
point (that would mean a different elliptic-integral convention or normalisation).

T2. Collapse times in arXiv:2609.14218 `alpha.pdf` (particles, e = 0.2). Read by eye,
time at which the central lapse falls to half its plateau, in t_H: mu = 0.3: 24;
0.15: 46; 0.10: 74; 0.075: 106; 0.06: 144; 0.05: 199 (+-3, +-10 for 0.05); mu = 0.045
never halves before 250. Reference model: linear growth delta ~ a, mean contrast inside
radius r at horizon entry deltabar(r) = deltabar(0) exp(-k^2 r^2/6), deltabar(0) =
(12/5) mu (derived here from D = (4/5)(aH)^-2 grad ln Psi and k^2/(a^2H^2) = 6 at
entry; to be checked numerically in the run), top-hat collapse when the linear contrast
reaches 1.686: t_c(r)/t_H = (1.686/deltabar(r))^(3/2). Prediction: every read-off time
lies between t_c(0) and t_c(r_m) (r_m = sqrt(6)/k), and the slope d ln t / d ln mu of the
read-offs for mu <= 0.15 is -1.5 +- 0.3. Consequence if it holds: the amplitude whose
t_c(r_m) equals 250 t_H is mu_fd ~ 0.048, inside the paper's bracket (0.045, 0.05].
Refuted if two or more read-offs fall outside the interval or the slope is outside
[-1.8, -1.2]; then the finite-run-length reading of observation 1 is unsupported.

T3. Ball geometry (phase 0, expanding ball in vacuum). Prediction: with the ball radius
three times the compaction radius and the ball at most 0.9 of its Hubble radius at the
start, the start is at a_i/a_H >= 11, and requiring the mean contrast inside r_m to be at
most 0.3 at the start limits the ball to mu <= 0.03 (deltabar_ent <= 0.027); with the
ball twice the compaction radius, mu <= 0.07. Amplitudes of the fluid runs of
arXiv:2609.14218 (mu >= 0.3) then need the periodic set-up (phase 1). Refuted if the
computed limits differ by more than 20 percent from these.

T4. Velocity-dispersion axis. With s = sigma_v R / (2M) (conserved by Liouville once the
dispersion is shared, arXiv:2211.13950 eq. sigma_v(t), MD_threshold10.tex line 333), the
non-formation condition of arXiv:2211.13950 (line 358) is s > 3/2; the virial estimate
with the 5/3 coefficient of arXiv:2507.18312 (Main.tex line 542) gives s > 0.55.
Prediction: the critical s lies in [0.5, 1.5] for every amplitude (independent of
delta at this order), so the scan axis s in {0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0} brackets
it. Refuted if the two estimates, written consistently, do not both fall in [0.4, 2].

T4b. Particle-number floor. arXiv:2507.18312 measures (Newtonian, top-hat at rest) a
halting compression b_min ~ 1.2 N^(-1/3) for random positions (Main.tex line 489) and
estimates b_min ~ N^(-4/9) for a lattice at rest (line 523). A black hole needs the
compression b_BH = 2M/R_ta = (5/3) deltabar_ent (line 316). Prediction: for the
noise floor to sit a factor 10 below b_BH at deltabar_ent = 0.04 (the amplitude of the
particle threshold of arXiv:2609.14218), a lattice needs N >~ 1e5 particles in the
perturbation and a random sample N >~ 5e6; at deltabar_ent = 0.01 a lattice needs
N >~ 2e6. Refuted if the computed numbers differ by more than a factor 2 (arithmetic
check only; the O(1) coefficients of the two estimates are themselves uncertain).

T5. Compute estimate. Measured: run `jeans/n1e4_v19` (two overdensities, 10^4 particles,
eight levels, 100 M, 25600 cycles) took 5.41 card-hours (sum of "cpu time used" over its
13 segments). Prediction for the ball scan: one threshold-scan run at 10^6 particles
costs 1 to 3 card-hours; the first scan (about 65 runs) 100 to 200 card-hours, above the
60 card-hours that decision 0006 gives Track A to the next gate. Refuted (estimate
wrong by more than a factor 3) only by the first production runs; recorded here so that
they can refute it.

## 2026-11-15, first run of `scope_calc.py` and what changed before the second

- `A-emd-pbh-20261115-112500-61acbec`: failed at start (`python3 -I` hides the user
  site-packages, numpy not found). No output. The script reads only this repository's
  files and run logs, not downloads, so it is run without `-I`.
- `A-emd-pbh-20261115-112505-61acbec` (commit 61acbec, 2.6 s on one core): all pass flags
  true. Looking at the figures showed three things to fix before relying on them:
  (i) the T2 interval check had left out the mu = 0.3, e = 0.2 read-off (24 t_H) that the
  prediction names; with it, that point lies OUTSIDE the interval (t_c(r_m) = 16.1 t_H,
  read-off 24 +- 3): one point outside, so by the stated criterion (two or more) the
  prediction still holds, but the large-amplitude anisotropic case collapses later than
  the top-hat shell; the check now includes it and the slope is fitted to mu <= 0.15 as
  predicted; (ii) the cost model let halo runs with t_c > 250 t_H run to the halt while
  the label said "to 250 t_H": now every halo run is followed to the halt plus 0.3 t_c,
  stated in the label; (iii) layout (legends over data, clipped label, log tick labels).
  The second run supersedes this one for figures and numbers; it stays on record.
