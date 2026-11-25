# What G2 of D-bh-dress still lacks (2026-11-25 04:00 PST, lead of batch 17)

The two track criteria are met at the meshes and particle numbers run so far (checklist C7, C8). New in
batch 17 (g2long/JOURNAL.md entries 18-19): FK closed and judged, P7-P10 hold: keeping horizon excision on
(initial_radius_0 1.6 M) removes the step of the (iii) medians at tau_rem ~285 M (ES-FL 0.6 per cent, FK
0.16-0.25 per cent) and leaves the horizon mass unchanged (2.2e-5 at 399.5 M); FN4 (4N) ran to 400 M and
agrees with FK (N2, N3 hold on a reading made before its close; criterion G for FN4 in entry 19).

## 1. Item by item, and the queue entry that serves it

| Item | State | What is missing | Served by |
|---|---|---|---|
| C1 ladder tests (§10 rows D owns) | OPEN | the G2 verifier (C17). FE4 (M/4 null test) closed and judged: P5 REFUTED, the null difference grows to 4.6e-3 by 300 M at M/4 (M/8, M/16: 2e-4; g2long entry 21) | none |
| C2 three-way convergence | OPEN | particle number: N = FK done, 4N = FN4 done (closing), N/4 = FNQ running (125 M of 400 in complete segments); mesh of the growth: M/4 FF4 done (to close and judge, P12-P14), M/8 ES-FL done, M/16 FL16 waits; mesh of the null test: FE4 (above); boundary: done (faces 192/384/768 M, boundary_gauge D-20261124-131657-89cd963). Gauge: carried by the boundary axis ("gauge or boundary"); the relaxed lapse cannot serve (section 2) | q0010 D-FNQ (N/4), q0011 D-FL16 (M/16) |
| C3 constraints | OPEN | volume and z = 0 plane norms done (D-20261123-021027-e3af9b8, D-20261124-134211-c6fce88); region (sphere) norms: FN4's esflk4n.region.hst now complete (XN to judge), FNQ (XQ), FL16 (L5) | q0010, q0011 |
| C4 first full-GR kinetic run | PASS | - | - |
| C5 verification report | OPEN | written when C1-C3 close | - |
| C6 reproducibility package | OPEN | one rerun script for every G2 number (processors; card runs by manifest) | no card run |
| C7 null test (vacuum bubble) | PASS at M/8 and M/16; FAILS at M/4 (P5 refuted) | a ruling on whether the coarsest member may sit outside the convergent regime | none |
| C8 growth against the flux | PASS (reservations) | particle and mesh members (C2); the D4 timing seen in FK (entry 19, [TO VERIFY]) | q0010, q0011 |
| C9 ladder schematic | PASS | redraw when the runs are read | - |
| C10 convergence figures | OPEN | particle number: np_partial.png (D-20261125-115729-011d028) is partial; mesh of the growth needs FL16 | q0010, q0011 |
| C11 constraint norms against time | OPEN | region-sphere norms of FN4/FNQ/FL16 | q0010, q0011 |
| C12 slice mosaic | PASS | - | - |
| C13 package documents | OPEN | REVIEW.md for G2 (the lead reviews are stage/REVIEW-wave3.md sections 13-19) | - |
| C14 data figures in the note | OPEN | the G2 figures are drawn and looked at but not yet in the note | - |
| C15 schematics (architecture, gate timeline) | OPEN | G2 update of note/figures/schem_* | - |
| C16 working note | OPEN | note v3: long runs, FP/FE, XC, FK, particle sequence, ladder, mosaic | - |
| C17 verifier (fresh context) | OPEN | VERIFIER.md for G2 | - |
| C18 null results on record | PASS | - | - |
| C19 STATUS/JOURNAL/HANDOFF | PASS | - | - |

Queue entries of this owner: q0008 D-FK done, q0009 D-FN4 done, q0010 D-FNQ running (job 5279), q0011
D-FL16 waiting (effective priority 1). Each open entry serves C2, C3, C10, C11; none is removed. No new
entry is added: every missing item above is either served by q0010/q0011 or is processor and writing work.

## 2. The relaxed lapse and `lapse_leak_hole` (core-v0.7, a mitigation): item by item

Every G2 run of D slices with plain 1+log and the Gamma-driver shift, no `lapse_leak` (g2long entries 6
and 10; decision 0025 item 3: "null tests and long runs around an existing black hole run without the
relaxed lapse"). So no G2 item depends on the relaxed lapse, and none needs the mitigation. Whether an item
COULD be judged with it, read from coord/INTERFACES/cosmo_gauge.md section 9.3 and 9.5 (core's runs; numbers
there):

| Item | Judgeable with `lapse_leak_hole = 16`? | Control that would show the drift |
|---|---|---|
| C1, C7 null test | No. The mitigated vacuum horizon mass moves by 2.1e-4 over 100-200 M and settles 2.5e-4 above plain 1+log (9.5), ten times the converged-finder vacuum drift (1.8e-5, FP) and as large as criterion N's bound (2.5e-4); its radius falls again after ~110 M | the same slice without dust and the same gauge (V-1L with `lapse_leak_hole`, tracker at the puncture) beside plain V-1L: their difference is the gauge drift, to be subtracted before any null test |
| C2 gauge axis | Only to ~100 M at M/8 (radius steady near 1.6 M to ~110 M, wiggles of 2e-4 until ~116 M; 9.3, 9.5) | the same mitigated vacuum control; the first pass of G1 (ES-1G, V-1GB) shows the drift unmitigated (+1.3e-3 over 100-200 M) |
| C3 constraints | Yes in principle (norms do not read the horizon mass), but not needed | plain-1+log twin of the same deck |
| C4, C8 growth | Not beyond ~100 M: the first pass gave +7e-3 with dust over 100-200 M (Track D), comparable to the 1 per cent of (iii); the mitigation is not measured with dust beyond 100 M | the mitigated bubble without dust (ES-1L with `lapse_leak_hole`) subtracted from the dusty run, as D2 subtracts V-1L |
| C5, C6, C9-C19 | not gauge-dependent | - |

So G2 stays on plain 1+log; the mitigation enters only at G3, where a hole inside expanding dust on a slice
with diverging normal observers may need the relaxed lapse, and there with the vacuum control above
(cosmo_gauge.md 9.5 advice: tracker at the puncture, 2 r_h at the inner edge of the dust, null test after the
transient, horizon above 10 cells).

## 3. Also open

- Horizon excision ends at 4 x initial_radius (nrpic.cpp:451-455): FK shows that this end is what moved
  the (iii) medians and D3 in ES-FL; core request ah-excision-growth-guard stays (outbox 2026-11-24). Finder
  stopping rule: request finder-stopping-rule to core.
- `nrpic-stage verify D-bh-dress G2` with checksums of the restart files runs for hours: use
  `--no-checksums` until the card runs are all closed, then the full verify detached.
- G1 gate reviewer's run D-20261121-165420-5d1c245 (changed scratch input): orch to say whether it is
  marked superseded (request of batch 11b, still open).
