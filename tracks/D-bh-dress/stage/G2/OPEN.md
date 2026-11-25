# What G2 of D-bh-dress still lacks (2026-11-25 08:20 PST, lead of batch 20)

Batch 20 (g2long entries 23-24, no card run): horizon searches rechecked (decision 0040 item 3: no failed
search after 20 M in any G2 summary; no D run has the diagnostics), FN4/FNQ region norms read (particle
noise), D4 split at 219 M, rerun script written (C6 PASS), mesh leg of the null test stated with two
members and no order (ruling 0039 item 4).

The two track criteria are met at the meshes and particle numbers run so far (checklist C7, C8). New in
batch 17 (g2long/JOURNAL.md entries 18-19): FK closed and judged, P7-P10 hold: keeping horizon excision on
(initial_radius_0 1.6 M) removes the step of the (iii) medians at tau_rem ~285 M (ES-FL 0.6 per cent, FK
0.16-0.25 per cent) and leaves the horizon mass unchanged (2.2e-5 at 399.5 M); FN4 (4N) ran to 400 M and
agrees with FK (N2, N3 hold on a reading made before its close; criterion G for FN4 in entry 19).

## 1. Item by item, and the queue entry that serves it

| Item | State | What is missing | Served by |
|---|---|---|---|
| C1 ladder tests (§10 rows D owns) | OPEN | the G2 verifier (C17). FE4 (M/4 null test) closed and judged: P5 REFUTED, the null difference grows to 4.6e-3 by 300 M at M/4 (M/8, M/16: 2e-4; g2long entry 21) | none |
| C2 three-way convergence | OPEN | particle number: N = FK, 4N = FN4 done; N/4 = FNQ running (353 M of 400; region shells read to 350 M, FNQ/FN4 = 3.5-3.9, particle noise); mesh of the growth: M/4 FF4, M/8 ES-FL done, M/16 FL16 waits; mesh of the null test: M/8 and M/16 at the floor, stated with two members and NO order (ruling 0039 item 4; no M/12 member, g2long entry 23); M/4 outside the regime; boundary: done. Gauge: the boundary axis; the relaxed lapse cannot serve (section 2) | q0010 D-FNQ (N/4), q0011 D-FL16 (M/16) |
| C3 constraints | OPEN | volume, plane and region-sphere norms read (region_norms D-20261125-160355-bda7e38: R1-R3 hold, FN4 and FNQ to 350 M); XQ at FNQ's end; L5 with FL16 | q0010, q0011 |
| C4 first full-GR kinetic run | PASS | - | - |
| C5 verification report | OPEN | written when C1-C3 close | - |
| C6 reproducibility package | PASS | stage/G2/rerun_g2.py (tested: rerun of xc_plane byte-identical, D-20261125-160651-29a730e) | - |
| C7 null test (vacuum bubble) | PASS at M/8 and M/16; M/4 outside the convergent regime (ruling 0039 item 4) | - ; horizon searches rechecked (hz_check D-20261125-160142-b1c51b5): no failed search after 20 M, plateaus found, N unchanged; runs made without `<fastflow> diagnostics` | none |
| C8 growth against the flux | PASS (reservations) | particle and mesh members (C2); D4: before 219 M FK = ES-FL (none early), FK's early removals after 235 M only (d4_timing D-20261125-160450-9326390); why excision removes up to 0.66 M before the exact crossing late on: [TO VERIFY], no bound | q0010, q0011 |
| C9 ladder schematic | PASS | redraw when the runs are read | - |
| C10 convergence figures | OPEN | particle number: np_partial.png (D-20261125-115729-011d028) is partial; mesh of the growth needs FL16 | q0010, q0011 |
| C11 constraint norms against time | PASS | region_norms.png added (D-20261125-160355-bda7e38); FL16's when it runs | q0011 |
| C12 slice mosaic | PASS | - | - |
| C13 package documents | OPEN | stage/G2/REVIEW.md now points to the lead reviews (REVIEW-wave3.md sections 13-22); closes with the package | - |
| C14 data figures in the note | OPEN | the G2 figures are drawn and looked at but not yet in the note | - |
| C15 schematics (architecture, gate timeline) | OPEN | G2 update of note/figures/schem_* | - |
| C16 working note | OPEN | note v3: long runs, FP/FE, XC, FK, particle sequence, ladder, mosaic | - |
| C17 verifier (fresh context) | OPEN | VERIFIER.md for G2 | - |
| C18 null results on record | PASS | - | - |
| C19 STATUS/JOURNAL/HANDOFF | PASS | - | - |

Queue entries of this owner (08:20 PST): q0008 D-FK done, q0009 D-FN4 done, q0010 D-FNQ submitted (chain at 353 M;
its next job 5293 pending, the cards held by another partition), q0011 D-FL16 waiting (effective priority 1). Each open entry serves C2, C3, C10, C11; none is removed. No new
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
