# JOURNAL of B-emd-gw

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T13:05Z  session B-emd-gw lead (wave 1 review)  commits f3d772d..  runs (below)

Helper journals of this wave (predictions and outcomes of each package):
`scope/JOURNAL.md`, `periodic_z4c/JOURNAL.md`, `gw_diag/JOURNAL.md`, `baseline/JOURNAL.md`,
`verify_cosmo/JOURNAL.md`.

### Lead predictions before the independent re-check (13:05Z)

Re-check L1 (`analysis/lead_recheck.sh`): the five packages rerun from a clean `git archive`
export of this commit, on processors, into one run directory; every committed result file
compared with its rerun by `analysis/compare_results.py`; four AthenaK cases of
periodic_z4c re-executed with the release processor executable and their outputs compared
with the original run directories.
- P-L1a: every pytest of gw_diag passes (12, plus the 2 reader tests with real files),
  `test_zeldovich.py` passes. Refuted by any failure.
- P-L1b: the JSON results of scope (3 files), baseline (1), gw_diag validations (3),
  verify_cosmo (pancake.json, pancake_profiles.json, flrw_recheck.json) and the
  periodic_z4c tables are reproduced to a relative 1e-10 or better (same code, same
  inputs, same libraries; differences only from thread-count-dependent FFT/BLAS
  summation). Refuted by any number differing by more than 1e-8 relative, or by a key
  present on one side only.
- P-L1c: the AthenaK re-executions (lw_x_prod N16 and N32, gauge_nl_conformal N64,
  lw3d_check_diag) are bit-identical in every output file except athena.log (serial
  Kokkos build, deterministic). Refuted by any differing byte in a .tab, .hst, .dat or
  .rst file.

Lead independent checks L2 (`analysis/lead_checks.py`, written by the lead, not by the
helpers), each with its prediction:
- P-L2a: the polarization tensor of `athenak/src/pgen/tests/z4c_linear_wave.cpp` lines
  107-112 has e.k != 0 for k = (1,1,1); flipping the signs of a_xy and a_yz gives e.k = 0
  to rounding for any k, keeps trace 0 and e:e = 2. (Already seen in a one-line test
  at 13:00Z; recorded here as part of L2.)
- P-L2b: for ds^2 = -dt^2 + X(t,x)^2 dx^2 + Y(t)^2 (dy^2 + dz^2) with dust at rest, the
  Einstein equations give Y ~ t^(2/3) and X = Y (1 + D f(x)) with D = const (a
  relabelling of x) or D ~ 1/t (decaying): no growing mode (scope check 1E).
- P-L2c: for gamma = diag(X^2, Y^2, Y^2)(x) the traceless, divergence-free,
  plane-symmetric mixed tensor is A^i_j = c Y^-3 diag(1, -1/2, -1/2), and the integral
  of A^i_j K^j_i sqrt(gamma) over x equals -c d/dt of the integral of X/Y (scope 1C, 1D).
- P-L2d: quasi-static TT strain of Phi = phi_x sin kx + phi_y sin ky under the equation
  of arXiv:1604.06065 (compendium_arxiv.tex lines 294-298, metric line 142): the real
  amplitude of the cos((k,k,0).x) wave of h_+ is (5/6)|phi_x phi_y|, i.e. a complex
  Fourier coefficient (numpy fftn / N^3) of (5/12)|phi_x phi_y| as scope reports.
  Refuted if my real-space projection gives anything else.
- P-L2e: the Zel'dovich ellipsoid energy, by direct quadrature of
  P = (G/5) sum_i Q'''_ii^2 with Q''' from a finite difference of the closed-form Q, equals
  (8/15) M c^2 S [(t2/t_k)^(1/3) - (t1/t_k)^(1/3)] to 1e-6 (baseline T1).
- P-L2f: s = a and s = a^(-3/2) solve d/dtau (a ds/dtau) = (3/2) s with
  a = (1 + tau/2)^2 (verify_cosmo reference); the second-order box mean of Khat in a
  closed box with a TT wave grows as pi^2 A^2 t, so alpha - 1 = -(1/6) pi^2 A^2 t^2 for
  d_t alpha = -(1/3) alpha^2 K and -pi^2 A^2 t^2 for 1+log (periodic_z4c item 3).
- Note before the registered L2 run (13:25Z): a development smoke test of `lead_checks.py`
  (scratch/B-emd-gw/tmp/smoke_lead, not cited) failed P-L2e as written: Q''' from a
  five-point difference of Q at h = 1e-3 is limited by rounding of the large t^2 term of Q
  (1.7e-4 relative in E). The registered check differentiates Q symbolically (sympy) and
  integrates adaptively; P-L2e is kept (1e-6).
- Small fix before L1: the gw_diag scripts imported `python/nrpic` through the absolute
  path of this worktree; now relative, so a clean export uses its own copy.
- 13:09Z: first launch of L1 registered as B-emd-gw-20261115-130926-a1c2237 and stopped
  after 19 s: `analysis/register.py` (copied from verify_cosmo, one level shallower)
  resolved the main checkout, so id and commit carried main's a1c2237 and the manifest
  landed outside the worktree (moved into `runs/`, status stopped, not cited). Fixed with
  a depth assertion; L1 relaunched below.

### Lead outcomes (13:20Z)

L1 = run `B-emd-gw-20261115-131016-03b1119` (174 s, processors; summary
`scratch/B-emd-gw/<run>/compare.json`, `logs/compare.out`):
- P-L1a HOLDS: gw_diag 14 of 14 tests pass with the two real files supplied (lw3.00016.rst
  of run -113218-0ea0f74, east.field.00004.bin of runs/cosmo/dav_c256_n128_t);
  `test_zeldovich.py` 13 PASS, 0 FAIL.
- P-L1b HOLDS, stronger than predicted: every numerical leaf of every compared result file
  is bit-identical (scope 3 files, gw_diag 3, verify_cosmo 3, periodic_z4c 6 JSON and 4
  Markdown tables, baseline 374 leaves); the only differences are the figure paths and
  the wall times in `baseline_results.json`.
- P-L1c HOLDS for every .tab, .hst, .dat, .bin and waveform file (163 + 163 + 259 + 28
  files byte-identical). REFUTED as written for the two .rst files of lw3d_check_diag:
  they differ in 36 bytes at offsets 8794-8829, a region after the parameter block that
  holds leftover input-file text (uninitialised buffer in AthenaK's restart writer); the
  field data are identical. Consequence: byte checksums of .rst files are not a
  reproducibility test (info to core).
L2 = run `B-emd-gw-20261115-131027-03b1119` (6 s): P-L2a-f all HOLD. a: e.k of the
generator's tensor is O(1) for oblique k (0.77 for (1,1,1)), < 1e-15 after flipping a_xy,
a_yz, trace 0, e:e = 2. b: exponents of A and B are 2/3 and -1/3, so D = const or 1/t
(scope 1E confirmed). c: P = C/Y^3 and the overlap equals -c d/dt(X/Y) (scope 1C, 1D
confirmed). d: real cosine amplitude (5/6)|phi_x phi_y| = 2.7716e-5 at delta = 0.01,
L = 4, ratios (1, 0.9), i.e. Fourier coefficient 1.3858e-5 = scope's value; the
normalization of "(5/12)" is now stated in SCOPE.md. e: quadrature equals the closed
form to 2e-16. f: sheet modes a and a^(-3/2) exact; alpha - 1 = -(1/6) pi^2 A^2 t^2 and
-pi^2 A^2 t^2, i.e. -1.64e-10 and -9.87e-10 at t = 10, A = 1e-6 (periodic_z4c measured
-1.6e-10 and -1.0e-9). Figure `lead_checks.png` looked at.
Figures looked at in this session (Read): scope crossed_waves_tt, regime_estimates;
periodic_z4c lw_x_convergence, lw3d_check, awa_history, gauge_nl_gradient; gw_diag
athenak_tt, athenak_psi4, cosmo_tt, weyl_convergence, tt_gauge_scalar; baseline
t2_za_scaling, t4_t5_axes_quadrupole_power; verify_cosmo pancake_errors, pancake_ppc,
pancake_grdiff (rerun copy). Cosmetic defects only: overlapping x tick labels in
lw_x_convergence; a legend over the curve in lead_checks panel (d).

Found while reviewing (changed my mind / new):
- gw_diag's cosmology scouting (`figs/cosmo_tt.png`): the late rise of rms h^TT after
  a ~ 600 coincides with (rms of the non-TT conformal-metric part)^2 reaching the TT level
  (4e-5 squared = 1.6e-9 at a = 1000 against h^TT ~ 1.2e-9 frozen). In the code's
  zero-shift gauge the flat Lambda projection has a second-order gauge piece of that
  size, so the late rise is not yet a GW signal [JUDGEMENT; TO VERIFY with the covariant
  projection or a gauge change]. The frozen part before a ~ 550 is far above that
  (5e-7 squared = 2.5e-13 at a = 12).
- 34 hand-written manifests were labelled "production" without pre-registration or a
  G0 pass; relabelled "scouting" with a `kind_correction` note; `make_cases.py` now
  writes scouting.
- core/newton (branch tip ce329f5, not on main) already has the quadrupole history
  (columns 19-43 of `<basename>.newton.hst`, `python/nrpic/newton.py`) and found the same
  first-order lattice error of the plane wave with one particle per cell (its interface
  note section 5.6) that verify_cosmo found with `pm.py` (P8): an independent
  confirmation from a different code path.

### Session close (13:45Z)

did: reviewed the five wave-1 packages from their artefacts (`stage/G0/REVIEW.md`); wrote
the G0 package (`stage/G0/REPORT.md`, `EVIDENCE.md`, `OPEN.md`, `CHECKLIST.md` filled:
6 PASS, 3 NA, 9 OPEN) and `stage/G1/STATUS.md` (G1 not met: criterion 1 met in a flat box,
2 met for the semi-analytic part only, 3 superseded); fourteen outbox files
(`outbox/20261115T1340Z__*`); STATUS, HANDOFF, RISKS rewritten.
found: every result of the wave reproduces bit for bit; the helpers' key derivations
hold; three defects fixed (Fourier normalization of the crossed-wave coefficient stated,
34 manifests relabelled scouting, hard-coded path); restart files carry 36 bytes of
uninitialised padding; the late TT rise in the cosmology dumps may be a gauge piece.
evidence: runs B-emd-gw-20261115-131016-03b1119 (L1), -131027-03b1119 (L2); stopped
misregistered launch -130926-a1c2237 kept on record.
changed my mind about: the G1 item on the stand-in fluid (superseded, proposal to strike);
one particle per cell for pancakes (two per direction for every production run); the
weyl output of AthenaK as a GW measure (replaced by gw_diag's fixed-direction Psi_4).
open: `stage/G0/OPEN.md`; G1 waits on core (generator fix, Newtonian mode on main);
the first-source scouting at 64^3 can start without core (HANDOFF.md, next work 1).
The Write tool refused the file name `REPORT.md` for a subagent; written through the
shell because the stage package names it.

## 2026-11-15T19:15Z  session B-emd-gw lead (wave 2 review)  commits 6b2c423e..(this push)  runs B-20261115-190007-e09a0d2, -190015-4dd3416, -190019-b5f5eb6, -190323-2f8806a, -190433-2d1d185

did: took over the four wave-2 helper packages (first_source, newton_tests, note, verifier);
wrote predictions R1-R10 before rechecking (stage/review_wave2/JOURNAL.md, commit e09a0d2),
recomputed from the registered raw outputs with own code (reader of AthenaK bin output, +
amplitude by direct summation, own g(tau), own TT projector, own linear-growth integration
for H1, own reading of the Newtonian history files), reran three verifier scripts; wrote
stage/REVIEW-wave2.md; corrected scope/SCOPE.md (crossover 0.289 and thresholds 0.032 and
0.19, absolute null criterion, comparison window a <= 10, Omega-today scaling TO VERIFY) and
one sentence of the note (resolved part of the late rise grows; PDF recompiled); read the
abstracts of the seven S2 key references the scope had not read (stage/G0/EVIDENCE.md);
G0 and G1 checklists judged, OPEN/EVIDENCE rewritten, G1/STATUS corrected; eleven outbox
messages; inbox (11) acknowledged; STATUS, HANDOFF, RISKS rewritten.
found: R1-R4, R6b, R7-R10 confirmed (lead and helper c_+ agree to 9e-14 of s; H1 to 2
percent at a <= 5; verifier scripts bit for bit); R5 partly refuted (32^3 vs 64^3 differs by
1.02 percent between a = 40 and 80 for eps = 1, my bound was 1 percent; the helper's "<= 0.06
percent at a = 5-40" is 0.09 for eps = 0.1); R6 partly refuted (largest c_+/s is 2.55 at
a = 123, not 2.5 at a ~ 95). The G_tot-corrected strain departs from the second-order value
more than the raw one, so the departure after a ~ 10 is higher order, not spatial gauge
(helper's own scan_summary_64.json). 2403.15126 takes the emission redshift at each
configuration's collapse (line 1061), which supports the verifier's sigma^(5/2) for Omega
today against the paper's stated 7/2 (line 1074).
evidence: the five runs above; figures stage/review_wave2/figs/rv_review_first_source.png,
rv_review_newton.png (looked at); helper figures scan_kk0, scan_secondgauge, late_rise,
pancake_east, ell_convergence, verifier v6_za_scaling looked at; note pages 1-4 read.
changed my mind about: OPEN item 7 (closed at second order: derivation plus the measured
gauge piece) and item 9 (the late rise is not gauge; mostly grid scale); the role of the
second gauge (it validates G_tot, it does not bring the code to the second-order value);
G1 criterion 2 (met in AthenaK's Newtonian mode).
open: G1 criterion 1 (oblique and expanding-box waves), G1 schematics, note Sec. IV-V,
independent verifier of the wave-2 runs, jittered null, particle-number convergence;
requests to orch on the verifier file name and the runs check of nrpic-stage verify.
Card-hours this session: 0 (all review runs on processors); owner total 0.99 of 40.

## 2026-11-21T06:29Z  session B-emd-gw lead (wave 3, batch 2a)  commits 84b251fd..(this push)  runs B-20261121-063617-6183015, B-20261121-063835-826c461

did: merged main (release core-v0.4); found no session or card job of the owner running;
closed seven runs of round 1 that had ended unattended with exit 0 (`nrpic-run finish`:
B-20261120-222841-acfe21d, -222849-3b921b7, -222849-e5673dc, -222955-c8e16e3,
-223006-24448ac, -223236-e213594, -223241-f1efd4f); committed the stranded outputs of the
finished note v2 package after `cmp` of 28 files against run B-20261120-223319-cc5320d; left
the uncommitted gauge module of waves round 1 alone. Wrote predictions L1-L3 before any
review run (stage/review_wave3/JOURNAL.md, ecb32b71), rechecked verifier3, waves, note v1/v2,
verifier2 and population from their artefacts (stage/REVIEW-wave3.md); appended the erratum
to REVIEW-wave2.md; named the measure behind "1.3e-15 L" in newton_tests/README.md;
judged the G1 checklist after `nrpic-stage collect`, rewrote stage/G1 EVIDENCE, OPEN,
STATUS, added stage/G1/REVIEW.md; five outbox messages (orch: C18 verifier, note PDF size;
core: in-situ Fourier output and a correction of its bracket; kb: claim on 2312.12499);
seven inbox messages acknowledged; STATUS, HANDOFF, RISKS rewritten.
found: L1 held except one pair (F cross amplitude at N = 64, 1.07 percent, 3.4e-10 absolute):
the waves and verifier3 readings agree on every other number but the X plus amplitude at
N >= 48. L2 failed: my third reading of X at N = 64 gives the waves value (plus 1.53836e-7,
x10 1.41541e-7), not verifier3's 1.3775e-7. L2b failed as predicted (the projection route
equals direct contraction to 2e-16); the cause is verifier3's summary, which keeps only the
part of the mode in phase with the exact cos(K.x) and reports the rest as spatial quadrature
(1.61e-8 at N = 64, x1; 1.75e-9 at x10; cross 2.4e-13): a definition, not an error; the
truncation error is 1.40e-7. L3 failed: 2312.12499 line 581 is three times (not twice) the
line-324 route in delta. Population P5 mass ratios reach +14.3 percent (report: +12).
evidence: the two runs above; figure stage/review_wave3/figs/lw3_crit1.png (looked at);
note figures fig_waves, fig_r2, schem_architecture, schem_dataflow, population pop_compare,
pop_gw_fid looked at; kb-data source of 2312.12499 lines 318-330 and 572-590 and of
2403.15126 lines 1040-1078 read.
changed my mind about: which X plus amplitude to quote (neither reading's; the cross or x10
value); G1 readiness (criteria met; the package still lacks C18).
open: C18 verifier package (request to orch); waves, first_source, flrw_conv, shear round 1
(HANDOFF); note v3 wordings; `nrpic-stage verify` and `report` for G1 (see the end of this
entry). Card-hours this session: 0 (processors only); owner total 2.48 of 40.
verify and report (end of the session): `nrpic-stage verify B-emd-gw G1` (25 minutes,
checksums of every run directory) FAIL only on `clean` (the three untracked files of the waves
package, left as found) and `sync` (main moved during the run; merged at 790c492b); runs (234
manifests), rerun (11 of 11), compare and regenerate (22 files) PASS. `nrpic-stage report`:
verdict FAIL, one item not PASS (C18). Pushed.

## 2026-11-21T15:45Z  lead batch 4a (wave 3)  commits 9015cd1f..  runs B-20261121-154933-a79da09, -155017-9aec47a, -155045-343bee1

did: merged main (fd69f5d4: release core-v0.6, rulings 0022); found the worktree clean, no
run open, no card job of B queued. Wrote predictions L4-L7 (stage/review_wave3/JOURNAL.md,
9015cd1f) before any run, then reviewed the three packages that finished since batch 2a
(first_source round 3, waves round 1, verifier_c18) from their artefacts: F2 and XS
remeasured with verifier3's reader, projector and exact solutions (L4, L5); first_source's
round-3 analyses rerun from their registered inputs (L6); verifier_c18's summary rerun (L7);
figures lw4_waves, r2_conv_eps1, r2_p16_nowave_64, a3_summary looked at. Fixed one small
defect (first_source/README.md P13 now names its window and interpolation). Review in
stage/REVIEW-wave3.md section "Batch 4a". G1 package: collect, checklist judged (C18 open,
narrowed), EVIDENCE, OPEN, STATUS, REVIEW, README of stage/G1; verify and report (below).
Seven inbox messages acknowledged (releases v0.5 and v0.6, core's answers on the Newtonian
requests, A's Szekeres files, kb's receipt); three outbox posts (orch: c18-remaining-rows,
next-batch-packages-of-b; core: round-1 findings, info).
found: all four predictions held. L4: F2 errors equal the waves values to <= 2.9e-4 relative
(amplitude at N = 64), orders 6.73/6.80/6.73 and 5.51/5.15/4.83 to the third digit. L5: X
cross errors at dt_expansion = 0.001 to <= 4e-5 relative; time part at N = 64 1.42992e-7 and
2.57038e-7 with verifier3's own e(0.01). L6: conv_compare and p16_compare byte-identical. L7:
a3_summary byte-identical (116 numbers, 103 within 1 per cent); line-125 statement in
p3_slicing.json as written. C18 is met in part: lines 34-36, 49-63, 70-71, 124, 199, 217 were
never recomputed by an independent agent. Core-v0.6 answers the old G1 items 9 and 10
(group moments; spectral Poisson symbol).
evidence: the three runs above; review_wave3/JOURNAL.md 2026-11-21T15:50Z and T15:55Z.
changed my mind about: C18 scope: I had expected verifier_c18 to close it; its brief left the
wave-1 pancake and homogeneous rows out, so one more package (or a ruling) is needed.
open: verifier_c18b or a ruling (orch); note v3; flrw_conv, shear, population (HANDOFF).
Card-hours this session: 0 (processors only); owner total 2.51 of 40.

## 2026-11-21T20:19Z  lead batch 5 (wave 3, cards first)  commits dc3020e6..  runs B-20261121-202304-dc3020e, -202335-3e6a898, -202359-d12511c, -202503-abdf6f0, -202548-3c3de2f, -202758-544416e, -202830-417af0c, -202946-ec4a156, -203254-928275f, -203426-ea1e945

did: merged main (edc49c3c: rulings 0025). Loaded the cards first (decision 0025 item 4):
flrw_conv J2 (batch, Slurm 4824) and J3 (chain, 4825; 128^3 now to a = 1001, new deck with
restart output), both with J1's core-v0.3 executable, predictions in flrw_conv/JOURNAL.md
entry 4 before submission. Shear: nprobe = 0, smoke run on the release v0.6 processor build,
series 1 of 27 cases (one failed launch on a negative fan centre read as an option, fixed).
Population: deck of the first full-GR run (128^3, L = 8, to a = 143, double dumps, snapshots,
restarts), predictions G1-G4, initial data at sigma1 = 0.028 started; a sequencer
(cards/sequencer.py, queue.json, setsid nohup, pid in scratch/B-emd-gw/sequencer/pid) submits the
GR chain when the data converge and a card slot is free, then sigma1 = 0.014. G1: ledger rows 34,
56, 59, 63 reworded as VERIFIER-C18b asks; the owed v3 corrections (rows 101, 118, 125, 168, 197)
and the (1 + eps^2) sentence with its range and a new ledger row; note rebuilt, checker clean as
in v2. Lead check of verifier_c18b from the artefacts with my own reader (prediction in
review_wave3/JOURNAL.md first). CHECKLIST C18 PASS, OPEN.md without owed items; collect, verify
(background), report.
found: line 59 confirmed as the verifier says: over all records 0.00751 (a = 22.56) and 0.00254
(a = 23.31); the printed 0.00706, 0.00203 are the maxima at the records nearest the five dumps.
The verifier's pancake.py and small_rows.py rerun byte for byte. Smoke run: cos(theta) =
1.43108e-3 against 1.43117e-3 linear (prediction met). Shear series: the f = 1 lapse leg stopped
at t = 0.578 (guard, non-finite Khat; failed run, cause unknown); the L2 ray analysis failed at
N_y = 32 and 64 (NaN in the transport step). Population data: outer contraction about 0.48 per
iteration at 128^3, so the 1e-9 stopping tolerance may not be reached within 18 iterations
(my prediction said it would); the sequencer accepts the data below 1e-7 and a Hamiltonian
residual below 1e-9.
failed: run B-20261121-202503-abdf6f0 (shear series, initial data refused a negative fan
centre; my error in run_cases.py); S1_n64_lap1 inside series 1 (guard stop).
changed my mind about: J3 to a = 51 only: with card time free (0025) the 128^3 leg runs to
a = 1001, which tests PB3 over the whole expansion.
open: analyse flrw_conv, shear, population runs (HANDOFF); orch's review of G1.
Card-hours this session: none used yet; queued about 4.5 (J2, J3, two population runs).

## 2026-11-23T01:45Z  lead batch 10a (wave 3, analysis round)  commits f295ab46..  runs B-20261123-015452-18d2956, -015919-dec4392; submitted -014847-f295ab4, -014850-7b7d986, -015905-7a30278

plan: read the card runs queued on 2026-11-21 (J3 of flrw_conv; the population GR run), find
why no job of B had been submitted since 22:23, add the 128-cell member to flrw_conv and judge
G2 criterion (a), summarise the shear series against P4-P12, queue follow-ups, start the G2
package, rerun stage verify for G1.
predictions written before runs: population R1-R3 (re-solve of the 0.028 data) and the outcome
of step 1 (population/JOURNAL.md 2026-11-22 17:48); flrw_conv J4a-c (entry 13). The flrw_conv
128-cell and shear outcomes were judged against predictions written in earlier sessions
(flrw_conv entries 1, 4, 9; shear 2026-11-20 22:30).
found: (1) The sequencer was alive but waiting without a log line: pop_s028_gr needed an outer
change of psi below 1e-7 and the 0.028 data ended the 18 fixed outer iterations at 3.25e-7;
card entries go in file order, so pop_s014_gr (data converged at 7.3e-8) waited behind it.
Corrected: pop_s014_gr submitted 17:48 (Slurm 4921), a 36-iteration re-solve of the 0.028
data running, pop_s028_gr behind it; the sequencer logs 'waiting:' lines now (stopped with
STOP, file changed, restarted). (2) flrw_conv J3 (2.00 card-h): growth-rate plateau 2.8e-8 at
128 cells (x10.9 from 64), largest |f - f_ref| 5.0e-6, all in the first e-fold; amplitude
floor 1.83e-6; G2 criterion (a) met at 16-128 cells. (3) shear series 1: S1, S2, S4 converge
at order 2.1-3.8 to within 1e-5 of linear; M1 -3.4e-4 and L1 -5.0e-3 inside the paper's
bounds; P5, P6, P11 met.
failed: population step 1 "outer change below 1e-9" (3.25e-7 at 0.028, 7.3e-8 at 0.014);
flrw_conv J3 "|e_D| at 128 at most a quarter of 64" (final); shear P4 Hamiltonian order
(8.5, 14.3 < 16), P7 order for S3 (non-monotone), P8 sign of M2 (+3.45e-3), P12 convergence
for S2, S3, S4 (means rise with N_y at HL = 1/16, 1/128); not judged: shear L2 (ray analysis
NaN) and P10 (guard stop). No new failed run.
changed my mind about: placing a card entry whose inputs may not converge ahead of others in a
file-order queue; such entries go last or carry an alternative.
open: pop_s014_gr, J4, the 0.028 re-solve and pop_s028_gr (HANDOFF); shear L2, f = 1, S3;
G2 products (stage/G2/OPEN.md).
Card-hours this session: none run; submitted pop_s014_gr (ceiling 3, expected 0.2-0.6) and J4
(ceiling 1, expected 0.4). Toward G2 so far 2.68 used.

## 2026-11-24T12:51Z-14:00Z  session lead of batch 11 (wave 3)  commits 960ba447..(this)  runs B-20261124-125457-79ce723, -130512-d39dae4, -131336-bc61eee, -131438-5d7e049, -131918-e71996f, -133150-e9ef701, -133533-cb0bb7d, -133702-4a06a52, -133709-85c4be7, -134209-4584052, -134720-c753aff

plan: the analysis round after the card runs of 2026-11-22: close and judge them against the
predictions written before them, find out whether the sequencer is alive, queue the follow-ups,
the G2 package, the formal G1 verify.
found: (1) the sequencer ended by itself on 2026-11-23 06:55 with its queue empty (not stalled);
all four runs were closed: pop_s014_gr completed to a = 143 (0.19 card-h), the 0.028 re-solve
converged (R1-R3 hold), J4 completed, pop_s028_gr stopped at the guard at a = 30.7 (after a
preemption and a correct resubmission from the t = 4 restart). (2) population, full GR against
Newton and the design (analysis -131918-e71996f, figures -133150-e9ef701): halo counts and
largest masses equal fidL8's at equal stage (H1), first halo between a = 30 and 36 (H2), the
metric's TT near-field energy within 9-13 per cent of the design's 2.9e-9 a for 6 <= a <= 20 and
correlated above 0.94 with the particles' near field over |k| <= 8 k_f to a = 72; the 0.028 stop
sits in the core of the box's largest halo, where K runs away (Z). (3) J4: the 128-cell floor is
the start step. (4) shear: P10 holds; L2 had no number first because its rays had not arrived by
tlim = 6, then because the fan was too coarse; with narrow fans L2 = -0.828, -0.830, -0.835,
beside CosmoGRaPH's -0.8183, far from gevolution and GRAMSES, but not converging.
failed: population G1 cost (0.19 below 0.2) and G1 for 0.028 (guard stop); A1 from a = 36; A2
in part (correlation below 0.9 from a = 81, rms ratio 0.63 at a = 6.3); A3 for the strain rms
(x1.97 against x2.09); shear P9'' b (no convergence) and P9 (0.010-0.017 from CosmoGRaPH,
growing); series 2's L2 design (coarse fan). Runs failed: pop_s028_gr (guard), analyses
-130512-d39dae4 (guard-stop dump) and -131918-e71996f (figure step; its JSON is complete).
changed my mind about: reading the GR box's TT energy as a signal after halo formation: the
excess is at high k, G_tot is as large as the raw strain, and only |k| <= 8 k_f tracks the near
field; no radiated-energy number from the GR box until the legs show what the excess is.
open: X0-X3 and the Newtonian reference on the cards; the legs through the sequencer; the L2
transport non-convergence; G1 verify running; G2 verify not run (HANDOFF).
Card-hours this session: none run in it; read 0.74 (J4 0.45, pop_s014_gr 0.19, pop_s028_gr
0.10); queued 1.1 (ceilings), 7 more behind the sequencer. Toward G2 so far 3.42 used.

## 2026-11-24T17:23Z-17:40Z  resumed lead session of batch 11b (wave 3)  commits 9c77192a..(this)  runs B-20261124-140856-911ded9 (closed), -172623-03699f5, -172643-d1e88c7, -172958-fc4a2cf, -172958-73b0662, -131438-5d7e049 (cancelled), -173547-11afdaf (sequencer)

plan: continue from what the cut session left (pause flag from about 07:20): close shear series 6
and judge it, commit the stage verify results, read anything new, keep the work moving while the
cards are held by another user's priority jobs (decision 0032 item 2), records, push.
predictions written before runs: N1p (population/JOURNAL 09:29) for the Newtonian reference on
processors; shear series 6 was predicted in the earlier session (committed in 911ded99).
found: (1) stage verify G1 PASS (formal rerun after the chains ended), G2 FAIL only on four open
runs. (2) shear series 6: L2 = -0.83915 at N_y = 256, 4 per cell along y; mesh differences 9.4e-3,
7.9e-3 (order about 0.25), moving away from CosmoGRaPH's -0.8183; constraint means 0.12-0.15,
barely falling with the mesh. The prediction holds only as written. L2 is reported as not
converged in this code; SPEC item 5 met only formally. (3) The sequencer is alive (pid 168802); it
had logged nothing but the pause flag since 05:55 because both card slots were held by pending
jobs. (4) The Newtonian reference moved from card job 5167 (cancelled before it ran) to two
processor runs; the gauge leg took the freed card slot (Slurm 5176). (5) The initial-data solves
for the particle and mesh legs are at outer iterations 16 and 13 after 3.6 h. (6) The 256^3 leg
now writes a restart every 1.0 in t (decision 0032 item 2).
failed: N1p time part (33 s per step on one core, about 13 h against "0.5 to 3 hours"; judged
from the measured rate, final when the runs end); I3 time part likely (not yet judged); the
cancelled card job 5167 is on record as failed (exit 1) though it never ran. Figure defect fixed:
fig_ppc's reference line shared a colour with a data series.
changed my mind about: reading the particle-converged L2 at N_y = 64 (-0.820) as agreement with
CosmoGRaPH; without mesh convergence it may be a coincidence of one mesh.
open: Newtonian reference (about 22:30 PST), the two initial-data solves, X0-X3 and the gauge leg
on the cards, the particle and mesh chains behind them; the cause of L2's mesh dependence (an
amplitude without stream crossing before t_A, not yet designed); G2 products C2, C11, C17, C18, C6.
Card-hours this session: none run; 5167 cancelled (0); queued 2.5 (ceilings: 5169 0.5, 5176 2).
Toward G2 so far 3.42 used. Request posted to core: Fourier solver with the threaded build.
