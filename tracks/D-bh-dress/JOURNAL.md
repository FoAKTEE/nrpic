# JOURNAL of D-bh-dress

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T14:55Z  session lead-wave1 (Opus)  predictions of the lead's re-checks, written before they run

Helpers' journals: `scope/JOURNAL.md`, `einstein_straus/JOURNAL.md`, `spike/JOURNAL.md`,
`secondary_infall/JOURNAL.md`, `puncture_drift/JOURNAL.md`. The lead re-checks each package
from its artefacts; scripts under `analysis/lead_checks/`, runs registered.

Already run before this entry was written (recorded honestly, no prediction on file):
the 48 symbolic identities of D-pre-1 (rerun D-bh-dress-20261115-065141-5fdc744, local-time
stamp, see below) and my own quadrature of a, m_p (scratch/D-bh-dress/tmp/lead/es_check_a.py).

- L1 (D-pre-4, `analysis/lead_checks/drift_recheck.py`, own code on the raw
  `punc.horizon_summary_0.txt`): the drift of a 20 M running mean between 50 and 490 M is
  +3.0e-4 (M/8) and +3.7e-5 (M/16) within 20 per cent; at M/16 max |D| on [50, 210] M is
  below 2.5e-5; the 5 M running mean swings about 9e-5 peak to peak in 220-255 M at BOTH
  resolutions (within 30 per cent of each other); |S|/M^2 after 5 M below 3.3e-7 / 5.7e-9.
  Refuted by: a drift that differs by more than 20 per cent, or excursions that differ by
  more than 30 per cent between resolutions (then the boundary attribution weakens).
- L2 (scope): rerunning `scope/scoping_estimates.py` reproduces every number of
  `scoping_table.txt` of run D-bh-dress-20261115-120304-795eee9 to all printed digits
  (deterministic code). Refuted by any differing digit.
- L3 (D-pre-2): rerunning `spike/spike_reference.py` reproduces the peaks 0.8699e8 GeV/cm^3
  at 7.58 Gm (constant f) and 2.44e18 at 7.75 Gm (Hernquist, canonical action) to 4 digits.
- L4 (D-pre-3, own closed form, `analysis/lead_checks/infall_recheck.py`): cold dust in
  the unperturbed Hubble flow around a seed M in EdS, shell energy E = -M/r_i, enclosed
  mass mu = M + eps^2 r_i^3/2, radial Kepler cycloid. Predicted: M_ta/M = 1.525 and 2.628
  at a/a_i = 2, 4 for every eps (to 1e-3); the mass that has reached r = 0 by a/a_i = 2 lies
  within 2 per cent below the helper's absorbed mass 1.193 (absorption at 2 M_bh happens
  slightly earlier than arrival at r = 0); coefficient (M_ta - M)/(M a/a_i) -> 0.5648.
  Refuted by: M_ta off by more than 1e-3, or the collapse mass more than 2 per cent away.
- L5 (analytic, second-agent check of `secondary_infall/RUNS.md` section 1): the LTB
  mapping E(r) = -M/r, M(r) = M + (4 pi/3) rho_i r^3 satisfies the Hamiltonian and
  momentum constraints on the dust's synchronous slice and gives K_ij = -H_i gamma_ij in
  the dust. I expect it to hold only if dust reaches r = 0 or the hole carries the mass
  of the removed core (an "over-massive" hole), otherwise E differs from -M/r.
- L6 (analytic, second-agent check of `scope/REFERENCES.md` section 2): McVittie apparent
  horizon at 1 - 2m/R = H^2 R^2, so d ln M_AH / d ln a = -12 (mH)^2 in EdS.
