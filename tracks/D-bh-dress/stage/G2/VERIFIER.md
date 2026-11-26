# Verifier's report, gate G2 of Track D (checklist item C17)

Fresh verifier, batch 26, 2026-11-25 22:09-22:40 PST (decision 0016 item 4; decision 0044
item 1). Package: `stage/G2/verifier/` (journal with every prediction before its run and the
outcome after; README; own tools). Processors only, one core per run, no card time.

## 1. What I read, and what I did not read first

Read: CLAUDE.md; coord/CHARTER.md to "Owners" and the Track D sheet (9.7); decision 0044;
scope/SCOPE.md sections 3-5; g2long/JOURNAL.md entries 1-4, 6, 8, 10 (criteria N and G as
fixed before the runs, and the predictions); flux_tools/JOURNAL.md entries 4 and 7 (criterion
(iii), D1-D4) and flux_tools/README.md (the ES-F construction); stage/G2/EVIDENCE.md and
STAGE_REPORT.md for the claims; docs/FORMATS.md and the excision rule in
athenak/src/particles/nrpic.cpp (core-v0.6, lines 438-462). The lead's predictions were
committed before the runs (entry 1 at 53afc1a before R1; entry 6 at bd47394 before FK, FF4,
FE4, FV4; entry 10 at fdca920 before FN4; entry 15 at a2cbe28 with FNQ, FL16) [VERIFIED from
git log and run ids]. Not read before section 9 was started: the outcome entries 5 and 11-27 of
g2long/JOURNAL.md, stage/REVIEW-wave3.md, stage/G2/CHECKLIST.md. The STAGE_REPORT's Result
column was in view while reading its claims.

Readers and reference are my own (`verifier/tools/vio.py`, `ltb.py`); no script of the package
(g2long/tools, g2runs/tools, flux_tools) was run or imported. Inputs: the registered card
outputs under scratch/D-bh-dress/<run id>/ and the three particle files and the table of the
initial-data runs.

## 2. The exact reference (V1; runs D-20261126-061541-31e3b4e, -061848-ed8f297)

Shells with LTB energy E = -M/R0 in a Schwarzschild slice: (dR/dtau)^2 = 2m/R - 2M/R0,
cycloid from the expanding start to R = 2m. Tested on closed forms first: fall time from rest
(pi/2)(R_max^3/2m)^(1/2) to 2e-16, a quadrature to 4e-13, a DOP853 integration of
d^2R/dtau^2 = -m/R^2 to 3.6e-12 [VERIFIED]. Mass inside a shell from two independent sources:
the evolved table (K_T^2 = 2D/R^3, so m = M + R^3 K_T^2/2) and the particle lattice.
- The table continuum gives m(edge) = M + 2.7386556250 (= D_tot), the growth law M_LTB(tau)
  of criterion (iii) equal to the data maker's esf_growth.csv to 1.9e-8 at tau = 25-600 M
  (1.0062, 1.0218, 1.0655, 1.1168, 1.1711, 1.2263, 1.2815, 1.3904, 1.5990), tau_H monotonic,
  and the tracer crossings 15.869, 39.613, 156.333, 354.241, 727.735 M [VERIFIED]. The
  reference of record of criterion G is reproduced independently.
- The lattice sum of m E_K equals the data maker's lattice Misner-Sharp sum to 2e-12 (N),
  1e-11 (4N), 3e-13 (N/4) [VERIFIED]; but the mass inside a single particle's radius
  scatters about the continuum by up to 2.2e-3 (N), 1.7e-3 (4N), 7.6e-3 (N/4) (lattice point
  counting), i.e. 0.44, 0.24, 1.34 M rms in that particle's crossing time. A per-particle
  "exact crossing time" carries this uncertainty if the dynamics felt the lattice mass.
  My prediction (2e-4) failed.

## 3. Claims, one by one

| # | Claim (lead) | My number (run) | Verdict |
|---|---|---|---|
| N1 | Null test M/8: max /D_ES1L - D_V1L/ on 100-500 M = 2.28e-4 against 2 F_V(500) = 2.51e-4 | 2.283e-4 at 256.5 M; bound 2.506e-4 (F_V 1.253e-4) (D-20261126-062005-99c2399) | reproduced, 3 digits; N holds |
| N2 | M/16: 1.99e-4 on 100-300 M | 1.986e-4 at 243 M; bound 2.685e-4 (F_V16 1.342e-4) | reproduced, 3 digits; N holds |
| N3 | M/4 fails: 4.57e-3 | 4.572e-3 at 299 M; own bound 3.952e-3 (F_V4 1.976e-3) | reproduced; fails the pass condition by 16 per cent against its own floor; N's refutation clause (3 max(F_V, 5e-5) = 5.9e-3 over 50 M) is NOT met, because the M/4 vacuum control itself drifts by -2.0e-3 |
| N4 | No failed finder search after 20 M in 13 summaries (signature NaN or bit-identical repeat); made without the diagnostics | 0 after 20 M in all 13; repeats only at t <= 5 M (FF4 also 4 NaN masses at t <= 5 M) | reproduced; every horizon number here was made without the finder's diagnostics (no status files) |
| G1 | (iii) max /bin median/: ES-FL 0.620 (61 bins), FL16 0.485 (38), FK 0.249 (50), FN4 0.239 (50), FNQ 0.290 (50), FF4 0.685 (60) per cent | 0.620, 0.485, 0.249, 0.239, 0.290, 0.685 with my table M_LTB; 0.596, 0.472, 0.216, 0.235, 0.278, 0.703 with my lattice M_LTB; same bin counts (D-20261126-062152-b7144de) | reproduced, 3 digits; every bin within +-1 per cent (+-2 per cent N/4) |
| G2 | D2 at every sample: ES-FL 960, FK, FN4, FNQ 760, FL16 1120 (V-1L16), FF4 480 (V-1L4) | ES-FL 960, FK 760, FN4 760, FNQ 760, FL16 1120 all hold (smallest lower margin 2.1e-3, FNQ at 393 M); FF4: 280 samples to 299 M hold; the 480 hold only with V-1L4 held at its last value after its end at 299 M; with V-1L 207 of 480 violate (D-20261126-062830-e947a9a) | reproduced, with a reservation on FF4 (section 4.2) |
| G3 | Removed m E_K of N/4 against N: -0.86, +0.49, +0.47, +0.28 per cent at 100, 200, 300, 399.5 M | -0.861, +0.495, +0.465, +0.283 per cent; 4N within 0.64 per cent | reproduced |
| G4 | D3 fails at N/4 (8352 of 29984 after ~220 M) and at M/4 (early removals) | FNQ 8352, first at 221.6 M, none before 219 M; FF4 1704, all before 219 M (first 7.75 M); none in ES-FL, FK, FN4, FL16 | reproduced exactly |
| G5 | Mass at the end, removed sum, closure | ES-FL M_AH(499.5 M) 1.6090, removed m E_K(500) 0.6010, D1 raw +1.80e-2, control-subtracted +9.4e-3; FK +2.2e-3, FN4 +2.6e-3, FNQ +2.7e-4 at 399.5 M | computed; F2's 1.625-1.665 and F3's D1 in [0, 8e-3] fail as written (not refuted) |
| C2a | Particle ordering /M_4N - M_N/ <= /M_N - M_N/4/ at 100, 200, 300, 399.5 M; window rms ratio 1.9-3.1 against 2 | 4 of 4; differences reproduced to the digits of the ledger; +-25 M windows 3.12, 2.51, 2.51, 1.87 (D-20261126-062637-6fbe1c9, -062830-e947a9a) | reproduced; caveat: the sample noise (sd 1.1e-3 of N - N/4, 4.4e-4 of 4N - N) makes the four-time ordering weak evidence, the window ratio is the content |
| C2b | Mesh: /Delta M_16 - Delta M_8/ from 20 M = 4.4e-4, 1.2e-4, 8.6e-5 at 100, 200, 300 (299) M; own controls 3.6e-4 to 1.3e-5; M/4 outside the regime | 4.40e-4, 1.16e-4, 8.6e-5; with controls 3.6e-4, 2.9e-5, 1.3e-5; Delta M_8 - Delta M_4 = -1.24e-3, -9.4e-4, -1.22e-3 | reproduced at the named samples; but the difference reaches 1.0e-3 between them and averages +5.8e-4 over 250-299 M (still below the 3e-3 bound); two members, no order: agreed |
| C2c | Exterior constraint norms against particle number: FNQ/FN4 shells 3.2-5.2, [30, 60] M deterministic to 150 M | [1.2 r_AH, 6] 3.19-5.14 (median 4.05), [6, 12] 3.28-4.81 (4.07), [12, 30] 2.5 before 150 M then 4.1, [30, 60] 1.1 before 150 M (region.hst; 4 expected for N^(-1/2)) | reproduced for the inner shells |
| C2d | Plane norms N/4 over N 1.65-1.89, 4N over N 0.43-0.49 (XQ, XN) | not recomputed (needs the con slices) | not checked |
| X1 | The step of (iii) in ES-FL comes from horizon excision ending at 4 x initial_radius; FK = ES-FL to 219 M | ES-FL's last reason-3 dust removal 218.9 M, first reason-2 224.0 M, minradius >= 3.2 M first at 219.5 M (FL16 220.0, FF4 225.0); FK removes only by reason 3 to 400 M (minradius 4.53 < 6.4 M); FK's (iii) medians for tau_rem 285-500 M 0.16-0.24 per cent, ES-FL's 0.52-0.62; FK - ES-FL in M_AH at most 2.2e-7 on 20-219 M (3.7e-7 at t = 0; not bit-identical) | reproduced; the mechanism is supported by the code (nrpic.cpp:455, rr_min < 4 initial_radius) and by FK, in which it could have failed |
| E1 | Early removals in FK, FN4 [TO VERIFY] | FK 29.5 per cent of dust before the exact crossing (none before 219 M, min -0.36 M); FN4 34.5 (3.45 before 219 M, min -0.66 M); FNQ 41; ES-FL 0.23 | numbers reproduced; cause decided in section 4.1 |
| P | Cost predictions | FE4 0.826 (P6 0.5-0.8), FK 2.70 (P11 1.8-2.4) failed; the other ten held (manifests) | as the lead lists |
| F | Converged-finder null difference 6.53e-5 (ledger) | not recomputed (needs the FP probe outputs) | not checked |

## 4. Findings beyond reproduction

### 4.1 The early removals are early arrivals, not early excision (run D-20261126-062436-72c04d3)

Prediction before the run: journal entry 3. The excision rule removes a particle inside
0.8 times the minimum coordinate radius of the last found horizon (nrpic.cpp:455-459), so a
reason-3 removal is inside the horizon of the run. Two readings of the tracers decide the
rest:
- Clock: the code's proper time of the tracers equals my integral of alpha/W dt along the
  trajectory samples to 6e-7 relative at 250 M for R0 = 28 M (below 2e-4 M absolute up to the
  horizon). The comparison clock is not off.
- Dynamics: the areal radius from the tangential metric component (it gives R0 at t = 0 to
  2e-6 M) shows the R0 = 28 M tracers turning around 0.004-0.03 M below the exact R_max =
  37.55 M and reaching each areal radius on the way in earlier than the cycloid: by 0.78 M of
  proper time in ES-FL and FK, 0.55 M in FN4 (4N), 0.40 M in FL16 (M/16); at R0 = 20 M by 0.17,
  0.10, 0.045 M; at R0 = 10 M below 0.01 M. The offset builds up around turnaround and
  converges with both the cell size and the particle number.
So the dust removed "before the exact crossing" crosses the run's horizon early because the
numerical shells run ahead of the exact LTB solution by about 0.2 per cent of their proper
time; in ES-FL after 219 M the same is hidden because removal happens deeper (the R0 = 28 M
tracers are removed there by the lapse rule at only tau_H + 0.06 M). [VERIFIED for the
tracers; for the dust JUDGEMENT by the same timing, with the lattice noise of section 2.]
Effect on G: the (iii) ratio moves by dM/dtau x 0.7 M / M_AH ~ 6e-4 (0.06 per cent of a
+-1 per cent band) and D2 by ~6e-4 against margins >= 2.1e-3: G is not touched; D3 and D4
are. The growth law reading of G3 will need this convergence (M/16 and 4N reduce it).

### 4.2 FF4's D2 beyond the end of its control

V-1L4 ends at 299 M; FF4 runs to 499 M. "D2 at 480 samples with its own control" holds only
if the control is held at its last value for 300-499 M. Restricted to the control's range D2
holds on 280 samples; with V-1L it fails (207 of 480). M/4 is outside the regime and no G2
claim rests on it, but the ledger row should say so.

### 4.3 Single-sample numbers

The mesh agreement 8.6e-5 at 299 M and the particle ordering at four times are single
samples of noisy series; the envelopes (1.0e-3; sample sd 1.1e-3 and 4.4e-4) are the honest
size. They do not change a verdict.

## 5. Predictions and criteria that failed as written (my readings)

N at M/4 (pass condition; refutation clause not met); P5 and P2 (refuted); V3 (F_V(500)
1.25e-4 > 1e-4); E2 (2.28e-4 > 2e-4); H1 (V-1L16 offset -2.7e-4 < 0); H2 (1.34e-4 > 5e-5); F2 at
400 M (1.4920 < 1.497) and at 500 M (1.6090 < 1.625), not refuted; F3 (overall median +0.52 per
cent, D1 +9.4e-3); F4's "every removal by reason 3" (84496 by reason 2 after 219 M); D3 at N/4
and at M/4; P6 and P11 (cost). My own failed predictions: V1b (lattice within 2e-4 of the
continuum; it is 2e-3), the first reading of V1c (my reader mixed the two branches of the
areal radius inside the throat; fixed and rerun).

## 6. Not checked, and why

The converged-finder null difference (6.53e-5) and FP/FE readings (need the probe outputs,
not read here); the plane norms XC, XN, XQ (need the con slices); V2, E1, F1 (comparisons with
the older V-1B, ES-1, ES-F runs); the slice mosaic, schematics and note figures (C9, C12, C14,
C15); the gauge leg of C2 (only plain 1+log exists; OPEN.md section 2). `nrpic-stage verify
D-bh-dress G2 --full` was started at 22:09 PST (pid 1210002, export of a5bd88c; log
scratch/D-bh-dress/tmp/stage_verify_G2_full_20261125-220931.log); it had not ended when this
report was written.

## 7. Figures (each looked at)

`scratch/D-bh-dress/<run>/`: v1_reference.png (D-20261126-061848-ed8f297: growth law, lattice
against continuum), v2_null.png (D-20261126-062005-99c2399: null test at three meshes),
v3_growth.png (D-20261126-062152-b7144de: (iii) medians, D2 margins, D4 timing),
v6_tracers.png (D-20261126-062436-72c04d3: tracer radius against the cycloid, clock),
v4_conv.png (D-20261126-062637-6fbe1c9: particle and mesh differences, shell norms).

## 8. Verdict of the verifier (before the comparison)

Criterion N holds at M/8 and M/16 and fails at M/4, as claimed; criterion G holds at every
member and every sample, as claimed; the particle-number convergence of C2 behaves as
N^(-1/2) noise; the mesh pair M/8-M/16 agrees to 1e-3 in the growth with no order; the step in
(iii) of ES-FL is the end of horizon excision. The lead's open point is decided: the early
removals are an evolution error of the shells (about 0.2 per cent of proper time at R0 = 28 M,
converging with mesh and particle number), not an excision outside the horizon and not a
clock error, and G does not depend on it. Two reservations for the record: FF4's D2 uses a
control past its end, and the single-sample convergence numbers understate their envelopes.
I find no number of the claims that I could check and could not reproduce.
