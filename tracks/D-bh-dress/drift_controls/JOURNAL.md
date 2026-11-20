# JOURNAL of drift_controls (helper package of D-bh-dress, wave 3)

Question: what causes the late drift of the apparent-horizon mass after t ~ 165 M that
the Einstein-Straus run ES-1 (D-20261115-172726-60ba4c2) and its vacuum control V-1
(D-20261115-172730-c6d151b) share (risk R13), so that the null-test floor of the ES
set-up (G2) can be stated. Predictions are written here before each test runs and never
changed afterwards; outcomes, also of failed predictions, are appended.

Numbers quoted as context in this entry come from `es_runs/JOURNAL.md` entries 4, 6, 7
and `puncture_drift/JOURNAL.md` (run ids there); every number of an outcome below comes
from a run of this package.

## Entry 1 (2026-11-20, 22:20 UTC): step 1, processor analysis of the existing outputs, predictions

Hypotheses for the late drift (V-1: -1.37e-4 at t = 199.5 M from t0 = 100 M, after
staying within [-4.2e-5, +2.1e-5] over 100-165 M):
- HF finder: the search (16 Gauss-Legendre points in theta, l_max = 8, stopping when the
  mass changes by less than 1e-5 per flow step, warm start from the last radius) returns
  a mass whose error changes in time.
- HB outer boundary: a disturbance made at the outflow faces at +-192 M reaches the hole.
  The Painleve-Gullstrand data have K_ij ~ r^(-3/2) at the faces, which the Sommerfeld
  condition of the `outflow` boundary does not hold, so the faces can emit from t = 0 on;
  at the coordinate light speed alpha/psi^2 ~ 1.3 (lapse 1.3-1.4 outside 10 M, entry 4)
  the faces' signal needs about 150 M to reach the hole, about 330 M from the corners
  [JUDGEMENT]. (A reflection of the gauge pulse that leaves the hole at t ~ 0 would come
  back only after 192/1.5 + 192/1.3 ~ 280 M.)
- HR resolution at the hole: truncation error of the M/8 nest around the trumpet.
- HG gauge: slow evolution of lapse and shift near the hole (the horizon's coordinate
  radius grows from 2.15 M at 100 M to 2.25 M at 200 M in V-1).

Tests of step 1 (one registered analysis run of `tools/step1.py`, a second of
`tools/slice_profiles.py`, a third of `tools/probe_finder_es.py`):

A. Decomposition from the finder summaries and histories (V-1, ES-1, D-pre-4 M/8 and M/16).
- A1 [certain from the formula, fastflow.cpp:821]: M = (M_irr^2 + S^2/(4 M_irr^2))^(1/2)
  with |S| ~ 5e-9: the spin term changes the mass by less than 1e-15, so the drift is the
  drift of the area, dM/M = dA/(2A). Refuted by a spin term above 1e-12.
- A2 [JUDGEMENT]: the finder's residuals do not change at t ~ 165 M: hrms (mean square
  expansion) stays within a factor 2 of its 100-165 M level after 165 M, hmean/area
  likewise, and the asphericity (mean radius - minimum radius) stays below 1e-5 M.
  Refuted (HF moves to the front) by a jump or trend of any of them that starts with the
  drift. The summaries carry no flow-iteration count (column 1 is the Runge-Kutta stage
  passed to Write, z4c_tasks.cpp:353-354), so iterations are not available.
- A3 [JUDGEMENT]: the angular grid resolves the horizon equally well before and after
  165 M: the coordinate radius changes by 5 per cent between 100 and 200 M, the point
  spacing r pi/16 stays near 0.44 M (3.5 cells of M/8), and the surface lies deep in the
  M/8 region (+-6 M). Refuted if the radius or the asphericity changes at 165 M by more
  than 5 per cent of its 100 M value.
- A4 [JUDGEMENT, weak]: the global constraint norms of z4c.user.hst do not show a change
  of slope at 165 M (they are volume norms dominated by the puncture region, so they are
  a weak test). If they do, that is a hint for HB or HG, not a test.
- A5: the D-pre-4 runs (boundary at +-128 M, time-symmetric data, K = 0 at the faces) have
  a plateau from 100 to 210 M and excursions at 220-255 M and 300-340 M; under HB with
  emission from the faces at t = 0, a K = 0 exterior emits much less, so I expect no
  feature in D-pre-4 at t ~ 128/1.3 ~ 100 M+; their excursions belong to a different path
  (reflected outgoing pulse) [JUDGEMENT].

B. Finder-independent mass and localisation (Misner-Sharp mass m(R) of the slices in the
restart dumps at t = 0, 50, 100, 150, 200 M, `analysis/diag/slicemass.py`).
- B1: the slice's horizon mass M_H = R_H/2 moves with the finder: M_H(200) - M_H(100)
  agrees with the finder's change over the same slices within 3e-5. Refuted (HF implicated)
  if it differs by more than 5e-5.
- B2 [JUDGEMENT, even odds between HB and HR/HG]: under HB, m(R) - M changes between the
  dumps at 150 and 200 M first at large R, and at 200 M the change reaches inward to the
  hole with a front that moved inward between 150 and 200 M; under HR or HG, the change
  between 150 and 200 M is confined to R < 10 M and m(R) is flat outside. Which of the two
  pictures the profiles show decides the order of the card runs.

C. Finder re-search on the slices of the dumps (processor executable of the same release,
`.work/build_cpu_v03`, one cycle from each dump with find_every = 1, three horizons per
run: h0 production settings from the stored radius; h1 stopping 1e-9, 4000 iterations,
start at 2 M; h2 production stopping, start from outside at 3 M; grids A16 = ntheta 16,
l_max 8 and A32 = ntheta 32, l_max 12). Dumps at t = 100, 150, 200 M of V-1 and ES-1.
- C1 (pre-flight of card run a): h0 on the A16 grid at t = 150 M reproduces the card's
  summary row at t = 150 M (same cycle 4800, same slice) to 1e-9 relative, and the A32
  run writes a summary with the new grid (the restart accepts the changed fastflow
  parameters). Refuted by a difference above 1e-8 (then the restart is not the same
  slice, or the processor and card builds differ) or a failed search.
- C2: on the A32 grid the mass is offset from A16 by a constant (D-pre-4: 1.8e-4) and the
  change 100 -> 200 M differs from the A16 change by less than 1e-5. Refuted (HF
  implicated) by a difference of the change above 3e-5.
- C3: the tight search h1 changes the drift 100 -> 200 M by less than 1e-5 (D-pre-4 P6:
  at most 1e-5); refuted above 3e-5.
If C2 and C3 hold, the finder is ruled out on the very slices where the drift is
largest, without a card; card run (a) would then only add the time profile between 150
and 200 M.
