# Journal of the fresh verifier of gate G2, Track B (batch 35, 2026-11-27)

Fresh context (decision 0016 item 4, 0046 item 2, 0048 item 3; checklist C18). Claims taken
from: the end of `stage/G2/OPEN.md` ("what to recompute first"; the file is 49 lines and I
read it whole, so its top paragraph, which carries the lead's states, was read too: noted
here as a limit of the freshness), `stage/G2/REPRODUCE.md`, note section VI and Tables VII
and VIII of `note/tables/ledger.tex`, Table V (waves), `scope/SCOPE.md` sections 4-7, the
track sheet (charter 9.5). Not read before VERIFIER.md is written: the outcome entries of the
journals, `stage/REVIEW-wave3.md`, the verdict column of `stage/G2/CHECKLIST.md` (item texts
only, extracted with a filter), `STAGE_REPORT.md`, `VERIFY_RESULTS.md`.

Definitions taken from the lead's scripts (only what a quantity IS, so that my number is the
same quantity; no code of theirs is imported or run): band rms of `compare_legs.py`
(`band_rms2`: sum over integer shells n = 1..8 of spec[n]/n^2, spec = per-shell
k^2-weighted TT power, shells nk = rint(|k|/k_f)); halos of `analyze.py` (friends-of-friends,
b = 0.2 of the mean spacing, at least NMIN particles; common limit 100 m_N with
m_N = rho_c L^3/64^3); a = (1 + t/2)^2; particle snapshot format of `docs/FORMATS.md`;
mesh dump format of `athenak/src/outputs/binary.cpp`.

## Entry 1 (18:05 PST): predictions, written before any recomputation

Readers first (V0): my mesh-dump reader, particle reader, TT projector and FoF are tested on
analytic cases before any claim is touched. Prediction V0: the TT projector returns a random
TT field to rounding (< 1e-12 relative) and removes a pure-gauge field d_i xi_j + d_j xi_i to
rounding; FoF recovers the membership of synthetic, well-separated Plummer clumps exactly.
Refuted if any of these fails.

V1 (waves; my exact solutions: the forward combination W = h + i h'/|k| of the t = 0 dump
carried by e^{-i|k|t} for the flat wave F; for the standing mode X of the matter era the
combination of j1(x)/x and y1(x)/x, x = k (t + 2), fitted to h = 0 and h' of the t = 0 dump).
Claims (ledger Table V): F amplitude error -1.41e-4, -1.72e-6, -3.1e-8 and phase error
2.53e-4, 1.22e-5, 7.07e-7 at N = 16, 32, 64, t = 4/sqrt 3; X cross polarization amplitude
-7.05e-5, 1.32e-6, 1.4e-7 and phase 8.3e-5, 3.06e-6, 2.76e-7 at N = 16, 32, 64, t = 10.
Prediction: I reproduce |error| to within 5 per cent at N = 16 and 32 and within 15 per cent
at N = 64 (my exact solution starts from the dump, theirs from the closed form; my TT
projection is spectral). The sign of the phase may differ by convention (stated, not counted).
Refuted if a magnitude differs by more than these bounds.

V2 (population, GM2): band rms |k| <= 8 k_f of the TT metric strain, 256^3 over 128^3, Gamma
driver. Claim: within 1.1 per cent to a = 64 and 2.8 per cent to a = 132 (corrected strain).
Prediction: (a) from the two analysis files with my own band sum I get the same largest
deviations to two digits; (b) my raw recomputation from the dumps (own reader, own TT) at
t = 4, 8, 14, 21 gives the files' raw band rms to 1e-3 relative on each mesh; (c) the gauge
piece in the shifted gauge is below 1 per cent of the band rms, so raw and corrected ratios
agree to 0.3 per cent; (d) the 128^3 dumps lie 0.0082 later in t than the 256^3 dumps; a
time interpolation of the 128^3 raw band rms to the 256^3 times changes the ratio by less
than 0.5 per cent. Refuted if (a) differs in the second digit, (b) by more than 1e-3, (c) or
(d) exceed their bounds.

V3 (population, high-k): TT measure above 16 k_f, zero shift over Gamma driver, 128^3,
a = 121: claim 946. Prediction: my raw recomputation from the two dumps gives the same ratio
within 10 per cent (raw against corrected differ in the zero-shift run by the gauge piece,
whose size the file records; I report both). Refuted if my raw ratio is below 500 or above 2000.

V4 (halos, equal masses): claim at a = 121, counts of FoF halos with at least 100 particles
108 (zero shift), 98 (Gamma driver), 106 (Newtonian mode); 256^3 against 128^3 Gamma driver:
counts above the common limit below the 128^3 counts at every epoch (0.484 to 1), largest
mass ratio 0.987 to 1.32, 1.32 and 1.13 at a = 64, 121. Prediction: my FoF on the same
snapshots gives counts within +-2 of each claimed count and the largest masses within
0.5 per cent (a different union order cannot change FoF groups; only the snapshot time and
the mass convention can). Refuted if a count differs by more than 2 or a largest mass by more
than 1 per cent. If 256^3 FoF does not fit in memory or time, it is stated as not checked.

V5 (constraints, C3): claims: 64^3 over 128^3 at eight particles per cell, zero shift,
Hr_mean 1.32 to 2.34 over 25 <= a <= 141, at least 1.64 for a >= 49; Mr_mean 1.71 to 2.16
for a >= 49; one particle per cell 128^3 over 256^3 Hr_mean 1.05 to 1.37 (Table VIII) or
1.11 to 1.36 (Table VII, both gauges); particle leg at a = 141 (128^3, 1 over 8 per cell):
Mr 2.93, Hr 1.58; continuation repeats the cut run to 4.2e-12. Prediction: my own
interpolation (log-linear in t onto a common grid; the lead's method is unknown to me) gives
each extreme within 3 per cent, the continuation difference below 1e-11. Refuted if an
extreme differs by more than 5 per cent, or the 8-per-cell pair falls below 1.2 for
a >= 49 in my reading.

V6 (stop at 256^3, zero shift): claims: largest K turns positive at a = 79.9, last record
before the non-finite stop a = 101, largest K there 0.0224. Prediction: from pop.cstat.hst
and the guard file I get these to three digits. Refuted otherwise.

V7 (shearing dust, series 7, beta = 0.125, HL = 4): claims Delta = 0.053749, 0.053800,
0.053821 at N_y = 64, 128, 256; ratio of differences 0.401 (order 1.3); finest minus
Richardson -1.38e-5; t_A = 4.12; no stream crossing before t_A, smallest neighbour spacing
0.699 of the lattice spacing; first crossing at t = 9.25, 9.25, 9. Also my own evaluation of
the closed-form cos(theta_lin) (SPEC section 4) against the files' cos_lin. Prediction: Delta
and Richardson reproduce from the rays.json values to all printed digits (arithmetic); my
crossing check from the particle snapshots finds no crossing up to t_A on all three meshes,
a smallest spacing within 0.02 of 0.699, and a first crossing snapshot within one snapshot
interval (0.25) of the claim; my closed form gives cos_lin to 1e-8 relative. Refuted if a
crossing appears before t_A, or cos_lin differs by more than 1e-6.
V7b (L2 as run, beta = 0.5, HL = 4, 4 per cell): Delta at N_y = 64, 128, 256 moves away from
CosmoGRaPH's -0.8183 with each refinement (claim). Prediction: |Delta + 0.8183| grows
monotonically with N_y; and the streams of L2 cross before t_A (the note says so), which my
crossing check must find. Refuted if the distance shrinks, or no crossing before t_A.

V8 (what G2 can claim): judged after V1-V7 against the scope text and decisions 0013, 0046,
0048, written into VERIFIER.md before reading the lead's verdicts.
