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

### Outcome of part A (run D-20261120-222107-cc4937b, `tools/step1.py`; figures `figs/step1_decompose.png`, `figs/step1_finder.png`, `figs/step1_constraints.png`, `figs/step1_gauge.png`, `figs/step1_dpre4.png`, each looked at; numbers in `results/step1.json`)

- A1 HELD. The spin term M - M_irr stays below 1.0e-15 (V-1) and 1.7e-14 (ES-1) after
  5 M, |S| below 9e-8 and 3.7e-7; the drift of the mass equals the drift of
  (A/A(t0))^(1/2) to 9e-16. The late drift is a drift of the horizon area.
- Drift windows from t0 = 100 M (finder summaries): V-1 [-4.21e-5, +2.11e-5] over 100-165 M,
  -1.368e-4 by 199.5 M, slope over 165-200 M -4.1e-6/M; ES-1 [-4.96e-5, +9.35e-5] and
  -3.400e-4, slope -9.5e-6/M. ES-1 - V-1 falls from +0.5e-4 at 165 M to -2.0e-4 at 199.5 M,
  so the late drift is 2.5 times larger with the dust than without it.
- A2 residual part HELD, asphericity part FAILED. hrms over 165-200 M / over 100-165 M
  (medians): 1.03 (V-1), 1.00 (ES-1); mean expansion hmean/A: 1.01, 1.00; nothing in the
  residuals changes at 165 M (figure, top two panels). The asphericity (mean - minimum
  coordinate radius) exceeds my 1e-5 M after t0: maximum 1.48e-5 M (V-1, near 190-195 M)
  and 3.40e-5 M (ES-1), and in ES-1 it rises from ~2e-6 to 1-3e-5 M from t ~ 155 M on,
  together with the drift (bottom panel). The surface the finder returns becomes
  non-round when the drift starts; the finder itself converges as before.
- A3 HELD as written, with an unpredicted finding. Mean coordinate radius (V-1) 2.147,
  2.187, 2.202, 2.252 M at 100, 150, 165, 199.5 M: +4.9 per cent over 100-200 M; point
  spacing r pi/16 = 0.42 M = 3.4 cells of M/8 at t0 (ES-1: 2.45 M, 0.48 M). Not predicted:
  the growth rate of the coordinate radius (5 M running mean, median) rises at 165 M:
  V-1 8.0e-4 -> 1.44e-3, ES-1 4.5e-4 -> 2.25e-3 (5 times), whereas D-pre-4 at M/8 falls
  1.12e-3 -> 0.82e-3. The coordinates near the horizon start to move faster when the
  drift starts (a gauge response near the hole, or the arrival of a disturbance).
- A4: H-norm2 and M-norm2 are flat (dominated by the puncture region, as expected).
  NOT expected: the Theta norm (volume integral of Theta^2) of V-1 grows by four orders of
  magnitude from t ~ 20 M to 200 M (8.5e-2 at 100 M, 0.59 at 150 M, 1.20 at 200 M; ES-1
  0.31, 2.09, 4.12), whereas both D-pre-4 runs stay at 1.6e-4 to 2.7e-4 from 100 to 500 M;
  Z-norm2 and C-norm2 of V-1 and ES-1 are 100 times those of D-pre-4 and peak near
  150 M. The two set-ups share the puncture and the near-hole resolution; they differ in
  the slice (Painleve-Gullstrand, K != 0 out to the faces, against K = 0), the boundary
  distance (192 against 128 M) and the nest. A constraint violation that fills the
  volume in V-1 and not in D-pre-4 points to the exterior, i.e. to HB [JUDGEMENT].
- A5 HELD. D-pre-4 over 100-200 M: [-1.75e-5, +1.91e-5] (M/8), [-1.36e-5, +6.3e-6] (M/16);
  no feature at 165 M. Its excursions (220-255 M, 300-340 M) are oscillations of both
  signs (+-5e-5 about the level), not a monotonic fall like V-1's: a different shape and
  timing, so I do not attribute them to the same mechanism.
- The lapse near the hole (probes at x = 1 and 4 M, mesh minimum; `figs/step1_gauge.png`)
  changes smoothly through 165 M; at x = 4 M it has a shallow minimum at 160-165 M and
  rises after (V-1 0.7985 at 165 M, 0.8044 at 200 M; ES-1 0.8550, 0.8742).

Ranking after part A [JUDGEMENT]: HB first (a constraint violation, Theta, fills the
volume only in the set-up whose slice has K != 0 at the faces; the horizon turns
non-round, as a front with the cube's symmetry would make it, exactly when the drift
starts); HG second (the faster coordinate motion of the horizon can be the response of
the gauge to the same arriving signal, or its own cause); HR third (the same M/8 nest
resolution in D-pre-4 shows nothing at 165 M; the nest differs); HF last (residuals
unchanged; still to be tested on the slices, part C).

Added prediction B3, written before `tools/theta_map.py` first ran: the z = 0 slices
of z4c (every 10 M) and con (every 25 M) of V-1 and ES-1 locate Theta. Under HB, |Theta|
on the +x axis is largest near the face x = 192 M at early times and the region of
large |Theta| moves inward at 1-1.6 M per M, reaching r < 10 M between t = 140 and 175 M;
in the z = 0 plane the pattern is a shrinking square (fronts parallel to the faces).
Refuted if |Theta| at r > 50 M stays below its value at r < 10 M at every time, or if the
large-|Theta| region moves outward from the hole; then HR or HG move to the front.

### First look at the Theta slices of V-1 (development pass of `tools/theta_map.py`, not registered; the registered run on V-1 and ES-1 follows and its numbers replace these)

The space-time diagram of log10|Theta| on the +x axis and the z = 0 maps show (i) a
region of large |Theta| that starts at the faces in the first 10-40 M and moves inward
along r ~ 192 - 1.3 t, (ii) the outgoing pulse from the hole (r ~ 50 M at t = 10 M,
~110 M at 50 M), (iii) after they meet, Theta fills the domain from outside in: the clean
region around the hole shrinks to the +-96 M box by t ~ 100 M, to about +-15 M by 150 M and
is gone by 200 M; on the axis the median |Theta| at r = 3-10 M is ~1e-6 to 3e-6 until
160 M and 5.5e-6, 1.8e-5, 3.7e-5, 6.6e-5 at 170, 180, 190, 200 M. The arrival at the hole
coincides with the start of the drift. Whether the faces (HB) or the coarse outer levels
inside +-192 M make this Theta is exactly what card run (b) decides: its mesh inside
+-192 M is block for block that of V-1 (checked below), only the faces move to +-384 M.

## Entry 2 (2026-11-20, 22:55 UTC): order of the card runs, and prediction for card run (b)

Order changed: (b) the boundary test goes first, (a) the finder test after it. Reason:
step 1 makes HB the leading hypothesis (Theta from outside reaches the hole when the
drift starts; the horizon turns non-round then), and nothing in step 1 implicates the
finder (residuals unchanged, A2). The finder question on the very slices where the drift
is largest is answered without a card by part C (processor re-search of the dumps at
100, 150, 200 M); card run (a) then adds only the time profile from 150 to 200 M and runs
after (b) if the cap allows.

Input `inputs/v1b_bnd384.athinput` (basename v1b): V-1 with one coarser root level added
(dx = 8 M on +-384 M); the old levels move up by one. `athena -m 1` (release processor
executable): V-1 344 MeshBlocks (56 per physical level 0-4, 64 at level 5); V-1B 400
(56 per level 0-5, 64 at level 6). The block bounds of V-1B inside +-192 M equal those
of V-1 as sets (344 = 344, compared from the two mesh_structure.dat files). Same finest
dx = M/8, so the same time step; same release card executable as V-1.

Prediction for V-1B [JUDGEMENT; HB at about 3:1 after step 1]:
- Pb1 (the decisive one): drift of the horizon mass from t0 = 100 M stays within
  +-5e-5 over 100-200 M, and D(199.5 M) is above -5e-5 (V-1: -1.37e-4). Refuted if
  D(199.5 M) < -1.0e-4 (the drift persists at 3/4 of V-1's or more): then the cause lies
  inside +-192 M (the coarse levels, the refinement interfaces, the near-hole gauge), and
  run (c) or a gauge test is next. Between -5e-5 and -1e-4: partial (the faces explain
  part of it).
- Pb2: V-1B and V-1 horizon masses agree to 1e-6 until the signal from V-1's faces
  reaches the hole and separate (> 1e-6) between t = 110 and 165 M. Refuted if they
  separate before 100 M (then the difference is not the faces' signal, e.g. card
  non-reproducibility or a fast gauge signal), or never by 200 M (then the faces carry
  no signal to the hole).
- Pb3: median |Theta| on the +x axis at r = 3-10 M stays below 1e-5 to t = 200 M (V-1:
  6.6e-5 at 200 M); the clean region still holds r < 100 M at 200 M.
- Pb4: the coordinate-radius rate of the horizon does not rise at 165 M (median over
  165-195 M within 30 per cent of that over 100-165 M), and the asphericity stays below
  5e-6 M.
- Pb5: cost 0.78 card-hours (400/344 of V-1's 0.672) within 10 per cent.
