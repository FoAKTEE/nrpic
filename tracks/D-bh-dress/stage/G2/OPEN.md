# What G2 of D-bh-dress still lacks (2026-11-25 22:15 PST, lead of batch 25)

Batch 25 (g2long entries 25-27, no new card run): FNQ (q0010) and FL16 (q0011) closed and judged; every
prediction made for them holds (Q1-Q3, XQ; L1-L5); the three-way convergence of item C2 is read (conv3
D-20261126-055249-505b079); note v3 written (section V, ledger part 11, schematics on release core-v0.7;
build D-20261126-055502-fbb1bec). Every horizon number of the package was made without `<fastflow>
diagnostics` and is rechecked by the failure signature (decision 0041 item 4; D-20261125-160142-b1c51b5,
D-20261126-055208-4e0fd0e).

## 1. Item by item

Every item of CHECKLIST.md is PASS except C17. What remains is of two kinds only:

| Kind | Item | State |
|---|---|---|
| fresh-context verifier of the whole gate | C17 | to be sent by the orchestrator (decision 0016 item 4); package otherwise complete |
| failure on record, with its ruling | C1, C2, C7 | P5: the null test fails at M/4 by a factor 20 (judge_conv D-20261125-122227-3eb563a); ruling 0039 item 4: M/4 outside the convergent regime, labelled so; mesh leg of the null test stated with two members and no order (ruling 0041 item 4) |
| failure on record | C8 | D3 fails at M/4 (FF4) and at N/4 after ~220 M (FNQ, 8352 of 29984 removals; entry 26); no ruling needed (D3 is not part of criterion G), stated in the note |
| failure on record | C3 | XC2's expected fall (factor 1.05), R1 'every column finite' (NaN at t = 0) |
| failure on record | C2 | conv3's first reading dropped 300 M (D-20261126-055207-0137c53); reader changed after it, labelled post hoc (entry 27) |
| decided by the verifier (2026-11-26), no criterion | C8 | why excision removes some dust up to 0.67 M of proper time before the exact crossing late on (FK, FN4, FNQ): early ARRIVAL, not early excision - the shells run ahead of the exact LTB solution by about 0.2 per cent of proper time at R0 = 28 M (0.78 M at M/8 and N, 0.55 M at 4N, 0.40 M at M/16), converging (VERIFIER.md section 4.1, run D-20261126-062436-72c04d3; VERIFIED for the tracers, JUDGEMENT for the dust). Carried to G3 as a bias of profiles read from removal times (scope/SCOPE_G3.md section 6) |
| gap stated, not a failure | C2 gauge axis | plain 1+log only; the relaxed lapse cannot serve (section 2); the third axis is the boundary (three face distances) |

No queue entry of this owner is open: q0008-q0011 are done. Nothing is queued for G2.

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
