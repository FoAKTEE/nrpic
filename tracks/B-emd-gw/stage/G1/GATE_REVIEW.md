# GATE_REVIEW.md: independent gate review of G1 of B-emd-gw

Reviewer of batch 6 (decision 0019 item 3), fresh context, 2026-11-21 from 21:14 UTC. I
produced none of the work under review. No tag `stage/B-emd-gw/G1-pass-*` existed when I
started (`git tag -l 'stage/B-emd-gw/*'`: only `stage/B-emd-gw/G0-pass-20261119`). Worktree
after `git merge --no-edit main`: 43834604.

**Read.** `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and sheet 9.5 (G1 of Track B: "the two
diagnostics agree on analytic linear waves; the Newtonian baseline reproduces the scaling of
the literature; background error and constraint convergence with the stand-in matter");
brief lines 674-686 (G1: "baseline results obtainable without the NRPIC coupling; the
analysis pipeline validated on them; interface proposals submitted"); decisions 0013 (Track B:
stand-in item struck, N-body baseline in the Newtonian mode, multi-code row by shearing dust
and GR against the Newtonian mode), 0016, 0023 item 2, 0024 item 3, 0025 item 2, 0026; the
package `stage/G1/` (STAGE_REPORT, CHECKLIST, EVIDENCE, OPEN, REVIEW, VERIFIER, VERIFIER-C18,
VERIFIER-C18b, verifier3/VERIFIER.md sections 4 and 6-7); `waves/README.md` (Results),
`newton_tests/README.md` (N1, N3), `baseline/BASELINE.md` sections 1-3; the source of the
literature scaling, arXiv:2403.15126 v1 `pII_GW_Vir_C2_Arx.tex` lines 998-1008, 1028-1033,
1070-1078 (kb-data, read only).

**Opened as evidence** (named at each criterion): the manifests of 13 runs of the track; the raw
double-precision dumps of test F at N = 16, 32, 48, 64 and of the amplitude scan; the raw
Newtonian-mode histories of seven ellipsoid runs; `newton_tests/results/ellipsoid.json`; the
note's ledger `note/tables/ledger.tex` and claims check `note/tables/claims.md`;
`note/main.log`; six figures looked at with the Read tool (section 4).

**Ran.** (1) `harness/bin/nrpic-stage verify B-emd-gw G1` (with output checksums) on
43834604 (section 3; output kept in `scratch/B-emd-gw/gate_review_G1/VERIFY_RESULTS.{md,json}`
and `verify.log`; the stage copies were restored to their committed state, so this review
changes no package file but this one). (2) My own checks, registered with `nrpic-run`:
**B-20261121-212222-3260317** (checks F and N, 2 cores, 0.5 min, exit 0) and
**B-20261121-212429-7812339** (check A, 2 cores, 0.5 min, exit 0); predictions committed
first in 47140ad2 and 78123393. Scripts `scratch/B-emd-gw/gate_review_G1/review_checks.py`,
`review_ascan.py` (inputs of the manifests, with sha256). Before the first registered run I
ran the script once by hand on N = 16 and one Newtonian case to debug it (an indexing error
in the history reader, fixed); its numbers are not used. No card-hours used.

## 0. Verdict

**Recommendation: PASS WITH RESERVATIONS.** The two track criteria that stand (the third is
struck by decision 0013) and the three common criteria are met by evidence I opened. My own
reading of test F from the raw dumps, with AthenaK's upstream reader and my own projector,
basis and Weyl tensor, reproduces every error the track states for criterion 1 to <= 0.8 per
cent (amplitude) and <= 0.16 per cent (phase), the local orders to 0.02, and puts the
fourth-order Weyl route on its stencil symbol to 1e-7 of the deviation. The two routes do not
agree "to rounding" after evolution: with the full nonlinear Weyl tensor they differ by
1.3e-10 of the wave at t_end at every N, and I showed (check A) that this is a third-order
effect, exactly proportional to A^2 (ratio 100.01 for a tenfold amplitude) and growing as
t^2; the package's numbers for this difference (1.2e-11 in the ledger, <= 6.4e-11 in the
report) are construction-dependent at that level. For criterion 2 the literature statements
are in the source as cited, the code reproduces the single-patch (2 alpha)^(7/2) law exactly
(spread 7.5e-15 and 3.1e-14, mine) and the crossing time converges at order 2.28 to within
5e-5 of the ODE; the energy constant converges only at first order (9.7 per cent low at 128
cells). The harness verify fails one check, `runs`, only on one G2 card chain still in flight
(flrw_conv J3), which is not G1 evidence. No science item blocks the gate.

## 1. My own check: predictions (written before the run)

Script `scratch/B-emd-gw/gate_review_G1/review_checks.py` (own code; it imports AthenaK's
upstream reader `athenak/vis/python/bin_convert.py` and a copy of
`harness/style/figstyle.py`, nothing of the track). To be registered with `nrpic-run`.

### Check F: criterion 1 on test F (oblique flat wave k = 2 pi (1,1,1), elliptic)

Data: the raw double-precision dumps of runs B-20261119-142016-ee73a03 (N = 16, 32),
B-20261119-142233-70d5043 (N = 48), B-20261119-142124-feb2daf (`flatN64`). Own TT projector
at +k, own helicity basis (m = (e1 + i e2)/sqrt 2, e_R = m m, e_L = conj), forward
combination W = h + i hdot/omega with hdot = -2 alpha K_ij, omega = 2 pi sqrt 3; own Weyl
route W_R = (2/|k|^2)(E_R - i B_R), W_L = (2/|k|^2)(E_L + i B_L) with E = R_ij + K K_ij -
K_ik K^k_j (full nonlinear 3-Ricci) and B = eps_(i^kl D_k K_l j), once with spectral and once
with fourth-order centred derivatives. Time of each dump from the history file (the last
dump is at t = 2.3094 by the history, not at 4/sqrt 3 = 2.30940108; the difference is
1.17e-5 rad of phase, so the track's phase errors test which time it used).

| # | Prediction | Refuted if |
|---|---|---|
| F0 | t = 0: the +k mode of h has the normalization-free ratio abs(H:H)/(H:conj H) = 0.73948 (generator formula with amp 1e-6, amp_cross 5e-7, phase 1 rad) at every N; H:conj H = 6.25e-13 if the generator's e+ has e+:e+ = 2 | ratio off by more than 1e-6 |
| F1 | amplitude error abs(W(t_end))/abs(W(0)) - 1, both helicities equal to 1e-3 of themselves and equal to the track's -1.409e-4, -1.717e-6, -1.574e-7, -3.10e-8 (N = 16, 32, 48, 64; `waves/README.md` item 1) | any N off by more than 2 per cent of the value |
| F2 | phase error arg(W(t_end)/W(0)) + omega t_end = +2.531e-4, +1.218e-5, +2.273e-6, +7.067e-7 (positive: the discrete wave lags) | off by more than 2 per cent, or of the opposite sign |
| F3 | local orders of F1: 6.36, 5.89, 5.65; of F2: 4.38, 4.14, 4.06 | any order off by more than 0.05 |
| F4 | spectral Weyl route equals the TT route, abs(W_E/W_TT - 1) <= 1e-10 at t = 0 and t_end, every N, both helicities (track: 1.1e-11 to 1.2e-11, verifier3 6.0e-11 to 6.4e-11) | above 1e-9 |
| F5 | fourth-order Weyl route: W_E4/W_TT - 1 = (s^2 + s)/2 - 1, s = (8 sin th - sin 2 th)/(6 th), th = 2 pi/N: -1.1671e-3, -7.398e-5, -1.465e-5, -4.639e-6 (N = 16, 32, 48, 64), at t = 0 and t_end; order 4 | off by more than 5 per cent of the deviation at N >= 32 (15 per cent at N = 16) |
| F6 | polarization ratio W_L/W_R constant over the dumps read to <= 1e-8 in modulus and argument (track: W_x/W_+ = 0.5 e^i to <= 1.1e-9) | a drift above 1e-8 |

### Check N: criterion 2 on AthenaK's Newtonian mode (N1, N3)

Data: the raw `newton.newton.hst` of runs B-20261115-163620-5b286c1 (N = 32, alpha = 0.05,
0.1, 0.2), B-20261115-163621-0ae44f1 (N = 64, same alphas), B-20261115-163613-790095f
(`ell32`), -163615-7bc8b30 (`ell64`), -163617-085c093 (N = 128) for alpha = 0.11122237. Own
estimator: Q = traceless part of I_ij, P = (1/5) Q'''_ij Q'''_ij from the d3I columns at
their own times, trapezoid from t_turn to t_x, t_x the first zero of dI_xx (records after a
remainder step below half the median step dropped).

| # | Prediction | Refuted if |
|---|---|---|
| N1 | F_raw = E/(M (2 alpha)^(7/2)) = 0.062059 (N = 32), 0.077205 (N = 64) | off by more than 1 per cent |
| N2 | F_raw and tau_x = t_x/t_turn the same for the four alphas at each N to <= 1e-10 (track: 7e-15, 3e-14; tau_x 2.524849, 2.506970) | spread above 1e-8 |
| N3 | t_x of the benchmark at N = 32, 64, 128: 24.0659, 23.8955, 23.8604; order 2.28 +- 0.05; Richardson 23.851 against the ODE 23.8524 (`newton_tests/README.md` N1) | t_x off by more than 1e-4 relative or order outside the range |

### Check A (added after run B-20261121-212222-3260317, before its own run)

Run B-20261121-212222-3260317 gave a spectral-Weyl against TT difference of 1.29e-10 to
1.30e-10 at t_end at every N (F4 as written, <= 1e-10, failed; not refuted at 1e-9), and
2.1e-13 at t = 0. It does not change with N, so it is not truncation. Hypothesis: it is of
third order in the amplitude, the coupling of the second-order non-TT field (which grows as
t^2 to 1.44e-4 of the wave, `waves/README.md` item 3) to the wave, which the TT projection
of h and the nonlinear Weyl tensor treat differently. Test on the amplitude scan of test F at
N = 16 (run B-20261119-153637-02c822f: `flat_s10` amplitude x10, `flat_s0p1` x1/10) and the
x1 run above, every dump:

| # | Prediction | Refuted if |
|---|---|---|
| A1 | the difference at t_end scales as A^2: 1.3e-8 at x10 (ratio to x1 within 100 +- 10) | ratio below 50 or above 200 |
| A2 | at x1/10 it is <= 1e-11 (A^2 gives 1.3e-12; rounding may hold it higher) | above 3e-11 |
| A3 | at x10 it grows with time roughly as t^2 (Delta/t^2 over the second half of the run constant within a factor 2) | a factor above 3 |
| A4 | the forward-combination amplitude and phase errors at N = 16 are the same for the three amplitudes to <= 6e-4 of themselves (track: `waves/README.md` item 4) | above 1e-3 |

## 2. My own check: outcomes

Outputs `review_checks.json`, `fig_review_checks.{pdf,png}` in
`scratch/B-emd-gw/B-20261121-212222-3260317/` and `review_ascan.json`,
`fig_review_ascan.{pdf,png}` in `scratch/B-emd-gw/B-20261121-212429-7812339/` (both figures
looked at; the second is the clean one: (a) my errors of both helicities sit on the track's at
every N, (b) the fourth-order Weyl route on its symbol line, the spectral route flat at 1.3e-10
at t_end and 2.1e-13 at t = 0, (c) the spectral difference two decades apart per decade of
amplitude and on a t^2 line). R, L are the two helicities.

| # | Mine | Track | Outcome |
|---|---|---|---|
| F0 | ratio 0.73948158346 (N = 16) to 0.73948158349 (64); H:conj H = 6.2500e-13 at every N | generator formula 0.73948158348 | holds (the generator's e+ has e+:e+ = 2) |
| F1 | N = 16: -1.40923e-4 / -1.40924e-4 (R / L); 32: -1.71727e-6 / -1.71784e-6; 48: -1.57312e-7 / -1.57567e-7; 64: -3.11373e-8 / -3.12487e-8 | -1.409e-4, -1.717e-6, -1.574e-7, -3.10e-8 | holds (largest departure 0.8 per cent, N = 64, L); the side condition "R and L equal to 1e-3 of themselves" **failed** at N = 48 (1.6e-3) and 64 (3.6e-3): absolute differences 2.5e-10 and 1.1e-10 of the amplitude, the rounding level (the track's x10 run shows the same floor for X) |
| F2 | 2.53096e-4; 1.21762e-5; 2.27288e-6 / 2.27244e-6; 7.0720e-7 / 7.0560e-7 | 2.531e-4, 1.218e-5, 2.273e-6, 7.067e-7 | holds (<= 0.16 per cent; positive). With t = 4/sqrt 3 instead of the dump time 2.3094 the phases would be 2.648e-4, 2.389e-5, 1.399e-5, 1.243e-5: the track used the right time |
| F3 | amplitude 6.359, 5.895, 5.631; phase 4.378, 4.140, 4.058 | 6.36, 5.89, 5.65; 4.38, 4.14, 4.06 | holds (largest 0.019) |
| F4 | t = 0: 2.1e-13 at every N; t_end: 1.29e-10 to 1.30e-10 at every N, both helicities | 1.1e-11 to 1.2e-11 (ledger), verifier3 6.0e-11 to 6.4e-11 | **failed as written** (<= 1e-10), not refuted (< 1e-9); explained by check A |
| F5 | t = 0: -1.16714e-3, -7.39757e-5, -1.46500e-5, -4.6395e-6; t_end the same to 1.2e-10 absolute; orders 3.98, 3.99, 4.00 | symbol -1.16714e-3, -7.39757e-5, -1.46500e-5, -4.6395e-6 | holds (to 1e-7 of the deviation) |
| F6 | largest drift of W_L/W_R over nine dumps: modulus 9.6e-10 (N = 16) to 2.3e-10 (64); argument 4.0e-10 to 1.6e-9 | <= 1.1e-9 (plus/cross basis) | holds |
| N1 | F_raw 0.0620591 (N = 32), 0.0772053 (64); 0.0854604 at 128 (benchmark only) | 0.062059, 0.077205 | holds (to all printed digits: same estimator definition) |
| N2 | spread over alpha = 0.05, 0.1, 0.11122237, 0.2: F_raw 7.5e-15 (32), 3.1e-14 (64); tau_x 2.8e-15, 2.8e-15; tau_x 2.5248487, 2.5069703 | 7e-15, 3e-14 | holds |
| N3 | t_x 24.065902, 23.895492, 23.860390; order 2.2794; Richardson 23.85128 (ODE 23.85237: -4.6e-5) | 24.0659, 23.8955, 23.8604; 2.28; 23.8513 | holds |
| A1 | dev at t_end: 1.2979e-8 / 1.3034e-8 (x10), 1.2978e-10 / 1.3033e-10 (x1); ratio 100.01 | A^2 | holds |
| A2 | 1.27e-12 / 1.28e-12 (x1/10) | <= 1e-11 | holds (still A^2: rounding is below it) |
| A3 | dev/t^2 over the second half within a factor 1.025 (x10; the same at x1 and x1/10) | t^2 | holds |
| A4 | largest relative spread of amplitude and phase errors over the three amplitudes 4.3e-4 | <= 6e-4 | holds |

Reading [JUDGEMENT, tested by A1-A3]: the difference between my TT route and my nonlinear
Weyl route after evolution is a third-order term, the product of the wave with the
second-order field that grows secularly as t^2 (the non-TT part of `waves/README.md` item 3
is 1.44e-4 of the wave at t_end and proportional to A); it is absent in the exact initial
data (2e-13 at t = 0) and is not a defect of either diagnostic. It means that "the two
diagnostics agree to 1e-11" is a statement about one particular construction; the
construction-independent statement is "they agree at linear order; their difference is of
order A^2 (t/period)^2 and measured at 1.3e-10 for A = 1e-6 after four periods".

## 3. Harness verify (`nrpic-stage verify B-emd-gw G1`, export of 43834604, 21:15-21:30 UTC)

FAIL on one check. `runs`: 2 of 289 runs have problems: B-20261121-202335-3e6a898
(flrw_conv J3, gate G2, a card chain still `submitted`) and B-20261121-202946-ec4a156
(population initial data, gate G2, `running` when verify read it; `completed` by 21:31 UTC).
Neither is G1 evidence. One run waived by `coord/WAIVERS.md` (B-20261115-164157-40b9f6d,
outputs moved after the run). Every other check passes: clean, sync, export, size, note,
package, note-pdf, style, fig-script (11 figures each with its script), min-figs (3 schematics,
8 data figures), status (36 lines), rerun (11 of 11 scripts in the clean export), compare (22
regenerated files within tolerance), regenerate (22 of 22). No other run failed the manifest
or output-checksum check (78 hand-written manifests read with defaults: WARN `run-notes`). This equals the lead's account of batch 5 with one fewer run in flight.

## 4. Criteria, one by one

| # | Criterion | Evidence I opened | Verdict |
|---|---|---|---|
| C1 | Baseline results without the NRPIC coupling | test F is vacuum Z4c (deck `waves/inputs/flat_oblique.athinput`, no particles; raw dumps read by me); the Newtonian-mode ellipsoid histories (read by me); manifests `completed` of the semi-analytic baseline B-emd-gw-20261115-115752-840e994 and of the population Newtonian runs B-20261119-143828-0ef9b5b, -143832-85cbe25, -145324-525e4fd | PASS |
| C2 | Analysis pipeline validated on them | my check F reproduces the TT pipeline's numbers of test F to <= 0.8 per cent from the raw dumps with independent code; manifests `completed` of the final analysis B-20261119-164402-7438a99, verifier2 B-20261119-142135-e582e09, verifier_c18 summary B-20261121-132955-cb150b2; verifier3 sections 4, 6, 7 read | PASS WITH RESERVATION (validated on single-mode linear waves only; verifier3's weakest point 1 stands: at linear order the Weyl route is an algebraic re-expression of the TT route, so their agreement checks the chain, not the evolution) |
| C3 | Interface proposals submitted | 35 messages in `outbox/` (to core, kb, A, E, orch); core's triage and answers `tracks/core/interfaces/REQUESTS_B.md` on main; oblique generator, double-precision output and jitter in core-v0.4 | PASS |
| C4 | Baseline data and figures | `note/figures/fig_waves.png`, `fig_newton.png` looked at (panel (b) of fig_newton shows the first-order energy convergence honestly); my own figures | PASS |
| C5 | Interface documents | `gw_diag/README.md` present; reader and gauge modules named with run ids; core's interface documents on main | PASS |
| C6 | The two diagnostics agree on analytic linear waves | checks F0-F6 and A1-A4 (section 2); `waves/README.md` items 1-7; ledger rows of test F (`note/tables/ledger.tex`); verifier3 section 4; I did not recheck test X or F2 (verifier3 covered X) | PASS WITH RESERVATION (the stated agreement levels 1.2e-11 and <= 6.4e-11 are construction-dependent; the agreement after evolution is limited by a third-order term, 1.3e-10 here, proportional to A^2 t^2) |
| C7 | The Newtonian baseline reproduces the scaling of the literature | source lines read: arXiv:2403.15126 `pII_GW_Vir_C2_Arx.tex:1007` (peak amplitude proportional to delta_L^(7/2)), `:1031` (spectrum decreases roughly as sigma^(7/2), omega_peak proportional to sigma^(3/2)), `:1074` (Omega_GW(f0, t0) proportional to sigma^(7/2)); checks N1-N3 from the raw histories; `newton_tests/README.md` N1, N3; `ellipsoid.json` | PASS WITH RESERVATION (the law holds in the code by an exact symmetry of the single-patch Newtonian problem, so the check tests scale invariance of the code, not more; the energy constant converges at first order, 0.0621, 0.0772, 0.0855 at 32, 64, 128 cells against the ODE 0.0946; the ensemble average of 2403.15126 is not redone; the G0 reservation on Omega today, sigma^(7/2) at :1074 against sigma^(5/2) from its eq. result_OmZ, stays [TO VERIFY]) |
| C8 | Stand-in matter | struck by decision 0013 (text read) | NA |
| C9 | Ruling 0013 applied | the N-body baseline runs in the Newtonian mode (N1, N3 read by me); the multi-code row is G2 work (shear package registered, its first series failed, R18) | PASS |
| C10 | Schematic: updated architecture | `note/figures/schem_architecture.png` looked at | PASS WITH RESERVATION (out of date: "quadrupole history of one species" and "fourth-order Newtonian force" are marked "to be written" although core-v0.6 carries the group moments and the spectral Poisson symbol, `OPEN.md` items 5-6) |
| C11 | Schematic: data flow | `note/figures/schem_dataflow.png` looked at | PASS |
| C12 | Data figure: baseline results | fig_waves, fig_newton looked at; verify regenerated all 22 figure files within tolerance | PASS |
| C13 | Data figure: pipeline validation | fig_waves panels (c), (d) looked at; my fig_review_ascan | PASS |
| C14 | Package documents (0012) | STAGE_REPORT, EVIDENCE, OPEN, CHECKLIST, REVIEW, VERIFIER (and two more verifier reports) present; scoping text `scope/SCOPE.md`; verify `package` PASS | PASS |
| C15 | Data figures from registered runs, one script each | verify `fig-script`, `rerun`, `compare`, `regenerate` PASS | PASS |
| C16 | Schematics with paperfig | `note/scripts/schem_*.py`; style copies equal `harness/style/SHA256SUMS` (verify `style`) | PASS (reservation of C10) |
| C17 | Working note, checker with --compile | `note/main.log`: 21 pages, 0 undefined, 0 overfull; PDF committed with the last .tex change (56501bc1); every data row of `ledger.tex` names a run (the rows without one are headers); claims check of the stage documents 24 of 28 agree (the four that differ are G0 documents, recorded) | PASS WITH RESERVATION (the manuscript checker was not rerun on v3, as the lead states; I did not rerun it either) |
| C18 | Verifier; every number of the ledger recomputed | VERIFIER.md (verifier2), verifier3, VERIFIER-C18, VERIFIER-C18b (56 of 58 CONFIRMED, none WRONG; line 59 NOT CONFIRMED as worded); ledger line 59 now reads "at the five dumps after crossing (a = 22, 25, 30, 35, 41.9)" | PASS |
| C19 | Null results and failed runs on record | the failed and stopped runs listed in STAGE_REPORT (verify reads their manifests); `waves/JOURNAL.md` failed predictions (lines 161, 216, 333, 382); my own failed sub-predictions F1 (helicity equality) and F4 recorded here | PASS |
| C20 | STATUS, JOURNAL, HANDOFF current | STATUS.md 36 lines, dated batch 5; verify `status` PASS (another session of this owner is writing flrw_conv files in the worktree now) | PASS |

## 5. Reservations to carry to G2

1. Criterion 1 wording: state the TT-Weyl agreement as linear-order agreement with a
   measured third-order difference (proportional to A^2 t^2; 1.3e-10 for A = 1e-6 after four
   periods with the full nonlinear Weyl tensor, runs B-20261121-212222-3260317 and
   B-20261121-212429-7812339), not as a rounding-level agreement; the ledger row "Weyl
   diagnostic with spectral derivatives minus TT ... 1.22e-11" should name its construction.
2. The pipeline is validated on single-mode linear waves (one direction per test, amplitude
   1e-6); at linear order the two routes are an algebraic re-expression of each other
   (verifier3, weakest point 1). The regime of the science runs (scalar tidal fields, shift,
   power up to the Nyquist scale) is not covered by criterion 1; G2 needs a check there.
3. Criterion 2 rests on an exact symmetry of the Newtonian single-patch problem; the energy
   constant converges at first order only (9.7 per cent low at 128 cells, Richardson within
   0.7 per cent). The ensemble statements of arXiv:2403.15126 are not redone, and the
   Omega-today exponent (7/2 at :1074 against 5/2 from eq. result_OmZ) stays [TO VERIFY].
4. The architecture schematic predates core-v0.6 (species moments, spectral Poisson symbol).
5. The manuscript checker was not rerun on note v3.
6. Test X and F2 were not rechecked by this review (verifier3 covered X; F2 was remeasured by
   the lead with verifier3's code, run B-20261121-154933-a79da09).
7. The harness verdict FAIL on `runs` is due only to the G2 chain flrw_conv J3
   (B-20261121-202335-3e6a898) still in flight; a rerun of verify after it is finished should
   pass every check.
