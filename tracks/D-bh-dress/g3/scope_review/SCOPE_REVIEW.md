# SCOPE_REVIEW.md: independent review of Track D's G3 scope before its runs

Reviewer: helper of D-bh-dress, batch 34, 2026-11-27 16:32-17:05 PST, fresh context. I wrote neither
`scope/SCOPE_G3.md` (lead of batch 34, commits e92904aed, acb5f7202) nor any run read here. The scope text
is changed by the lead; this file proposes wordings only.

**Verdict: do not queue the production set as written. Change B1, B2 and B3 first (they decide whether
the mesh leg and Claim D can mean anything), then S1-S8.** What may proceed now: EG8 (q0085, running);
G-8 once EG8's E1 is read (G-8's deck is the base of every design below; its criteria are read only after
the amendment); and the processor work of section 4, which needs no card.

Read: CLAUDE.md; coord/CHARTER.md to "Owners"; brief lines 394-405, 766-783, 834-860; decision 0045;
`scope/SCOPE_G3.md` whole; `scope/SCOPE.md` sections 1-5; `stage/G2/GATE_REVIEW.md` whole;
`stage/G2/VERIFIER.md` whole; `g2long/JOURNAL.md` entries 1, 4-6, 19, 24-27; `excguard/JOURNAL.md`;
`coord/INTERFACES/finder_stop.md`; docs/FORMATS.md line 123.

Ran (processors, one core each, all registered, predictions committed before each run; JOURNAL.md
entries 1-7, including the predictions that failed: A3, B1, B3, C1, B2b, half of B2c):

| Run | What | Figure (looked at) |
|---|---|---|
| D-20261128-004344-1119b6f (and -004218-80cf6ab, labels fixed) | `athena -m` block counts of G-8, G-12, G-16 as section 3 describes them, and of G-16b (blocks of 12) | none (integers from the code's mesh file) |
| D-20261128-004801-cd648e5 | the Claim G criteria applied to G2's registered outputs, one factor coarser | g2_analogs.png |
| D-20261128-005059-e65d075 | Claim D's statistic on the exact LTB solution with FK's per-particle clocks | dress_model.png |
| D-20261128-005416-65b4dde, D-20261128-005447-0705a41 | power of a whole-run form of G3-G3 (single-sample and window anchor) | g3g3_power.png (both) |

## 1. Findings, ranked

### Blocking

**B1. The mesh members cannot be built as described, and G-12 is not a refinement of G-8.**
Evidence (run D-20261128-004344-1119b6f, `block_counts.json`; JOURNAL entry 2):
- G-8: 456 blocks, level 7 (M/8) over +-6 M [VERIFIED, as g2long entry 4].
- G-16 ("level 8 added over +-6 M"): **3648 blocks, 8.0 times G-8**, not "about 2.5 times". Level 8 over
  the whole level-7 box puts level-8 blocks next to level-6 blocks; the 2:1 rule of the tree refines a
  448-block shell on every level out to the root (448 leaves on each of levels 1-7, 512 on level 8, none
  on the root). With twice the steps that is about 16 times G-8's mesh work: about 28 card-hours to
  400 M by the scope's own cost model (blocks x steps; G-8's mesh part 1.71 card-hours: ES-FL's 2.60 to
  500 M scaled to 400 M, less the particle part 0.37 per N from FN4's 3.19, EVIDENCE.md line 61) [JUDGEMENT], against the scope's 10 (cap 13). Card memory
  for 3648 blocks is [TO VERIFY] (eight times G-8's mesh).
- G-12 ("root 96 -> 144, the whole hierarchy refined by 1.5"): **2176 blocks (4.8 times), and its finest
  level (M/12) covers only +-4 M.** With the root at 144 cells the refined regions of the ES-FL deck fall
  on different block boundaries: level extents +-512, 256, 128, 64, 16, 8, 4 M against G-8's +-384, ...,
  12, 6 M. Radius by radius G-12 is coarser than G-8 in 4-6 M (dx 0.167 against 0.125 M), 8-12 M and
  16-24 M, and finer elsewhere. The late horizon (smallest radius 4.53 M at 399.5 M, g2long entry 19) sits
  in the shell where G-12 is the coarser member. It breaks the scope's own rule "the finest level must
  cover a cube of +-6 M" and decision 0045's "third mesh member inside the convergent regime".
- G-16b (G-16 with blocks of 12 cells) exists at a lower price: 8296 small blocks, 2.27 times G-8's
  cells, 4.44 times its cells with ghost zones; level 8 over +-6 M, level 7 over +-9 M (A4 held).
- The smoke-test rule "finder found at t = 0 within 3e-4 of ES-F's 0.9915" refuses every M/16 deck by
  construction: FL16's t = 0 mass is 0.99981 (its horizon summary), 8.3e-3 away; the offset is the mesh's
  (g2long entry 4: -7.6e-3 at M/8, -1.8e-4 at M/16).

Proposed wording for section 3 (replacing the member table's G-12/G-16 rows and the cost lines):
"The three mesh members are one family: the same physical refinement boxes, the cell size at every
radius 1, 2/3 and 1/2 times that of G-8, the finest level over +-6 M in each. Each deck's MeshBlock count per
level and level extents are measured with `athena -m` (tools/make_decks.py and block_counts.py of
g3/scope_review) and listed here before its smoke test; the cost estimate is blocks x steps x G-8's
measured cost per block-step, and a card timing of 2 M (memory and seconds per M) precedes the queue
entry. Smoke test at t = 0: the finder is found, and its mass equals that of the same deck on the
processors within 1e-8." If no family fits the budget, the mesh leg is restricted in time to the window
in which the horizon stays inside a cheaper finest box (FL16's +-3 M holds it to about 200 M, scope
section 2 [TO VERIFY]), and the text says so.

**B2. Claim D's statistic, as written, measures the shells' lead and a borrowed tracer clock, not a profile.**
Evidence (run D-20261128-005059-e65d075, JOURNAL entry 4; the exact cycloid tested against
esf_growth.csv to 6.0e-9):
- The exact side takes "the proper time of the bin from the tracers of the nearest label". By 200 M the
  inner tracer labels (6, 10, 20 M) are swallowed and the nearest left is 28 M; inside one 1 M label bin
  the particles' own proper times spread by 5.4-7.1 M and differ from the tracer label's by up to 15.4 M.
  On the exact solution with FK's real clocks, that reference alone gives |q| up to 44, 73, 69 per cent at
  100, 200, 300 M and an inner slope of -0.05 to -1.2 where the exact one is -1.9 to -2.8. D1 (2 per cent)
  and D3 (0.05) fail by construction. Every snapshot carries each particle's proper time
  (docs/FORMATS.md line 123), so no tracer clock is needed.
- With each particle's own clock, the measured lead (verifier 4.1: 0.79 M at R0 = 28 M, M/8, N) gives
  |q| up to 24 per cent in the inner bins (18 per cent with the M/16 lead). q near the hole is the lead
  re-expressed: matter falls at nearly the speed of light there, so 0.4-0.8 M of proper time is half a
  logarithmic bin. With section 6's lead correction applied to the exact side, D1 then tests how well a
  lead measured at three tracer labels (14 tracers each) and interpolated in R0 reproduces itself, not
  the profile. D2's ordering of |q| is not implied by the ordering of the lead (at 300 M the innermost bin
  has |q| 14 per cent with the smaller M/16 lead, 9 per cent with the M/8 lead; the labels are lumpy).
- D3's tolerance 0.05 on the inner slope is about one standard deviation of its counting noise (Poisson
  bootstrap 0.042, 0.062, 0.073 at 100, 200, 300 M [JUDGEMENT: the lattice is quieter than Poisson, the
  dynamics adds scatter]); "at every snapshot from 100 M" then fails by noise.
- Passing D would not mean "the dress": in cold spherical infall no bound dress forms (scope section 1
  and 8 say so). What D can show is that the infalling matter follows LTB in the strong field.

Proposed wording for section 5 (replacing statistic, estimator and D1-D3):
"Claim D (the infalling matter in the strong field; no bound dress forms in cold spherical infall).
Statistic: for every dust particle in a snapshot, its areal radius R_p (coordinate radius mapped with the
tangential metric of the slice dump at the same time) and its own proper time tau_p; the timing residual
dtau_p = tau_p - tau_LTB(R_p; R0_p), the proper time at which the exact shell of its label has that areal
radius on the way in. Estimator: the median of dtau_p in cells of (R0: 2 M bins) x (R: 1.2 R_AH-3 M,
3-6, 6-10, 10-20, 20-40 M), with a bootstrap standard error. D1: |median dtau| at the finest member and
16N below [a number fixed from the G2 snapshots, section 4 item 2] in every cell with 200 particles.
D2: the medians fall with h and with N in each cell by more than twice their combined standard error
(this is also G3-L1, with thousands of particles per label instead of 14 tracers). D3: the density
profile and its inner slope are shown beside the exact one with bootstrap errors, as a figure, not a
pass/fail number." The reader is built and its noise fixed on G2's snapshots before any G3 card hour
(section 4).

**B3. The mesh criteria of Claim G cannot pass when the code converges (G3-G3) or do not measure
convergence (G3-G2).**
Evidence (run D-20261128-004801-cd648e5, JOURNAL entry 3; runs D-20261128-005416-65b4dde,
D-20261128-005447-0705a41, entries 6-7):
- G3-G3 as written (max |D| per 50 M window, D_8,12 above D_12,16 in every window after 100 M, ratio in
  [1.5, 8]): with G2's noise (one member at N: sd 3.9e-4 in M_AH; mesh members correlated at 0.83) and a
  deterministic difference of order 2 the size of G2's M/16 - M/8 offset (+5.8e-4), it passes with
  probability 0.11-0.15 (0.08-0.10 at order 1). The envelope of a noisy series is its noise maximum.
- The anchor Delta M_h(t) = M_AH(t) - M_AH(20 M) injects one finder sample's noise as a constant offset
  of the whole series: whole-run means anchored this way still pass with only 0.30 and pass a
  non-converging set with 0.22-0.24. Anchored at the 20-40 M mean, the whole-run form passes with 0.66
  (full noise) to 0.95 (high-pass noise) and falsely with 0.25 to 0.08.
- G3-G2 orders |e_h| "toward the exact solution". e_h is not an error that falls to zero: e_8 - e_16 =
  +1.48e-3 in each of 23 bins (tau_rem 50-280 M, sd 3.0e-4), of which the lead explains about 3e-4; the
  rest matches the mesh's converged horizon-area offset in vacuum, +9.9e-4 at M/8 and -2.0e-4 at M/16
  (tight finder at 200 M, A16; -9.1e-3 at M/4; fp_analyse D-20261124-172508-c847ee4, whose order test
  FP4 was refuted as non-monotone) [JUDGEMENT: the decomposition is arithmetic on registered numbers].
  After the vacuum offset (A16, tight), the lead and the unpolished rule's -6e-5 are taken out, about
  +0.02 to +0.09 per cent remains at both meshes: a limit e_inf of the removal-time estimator that is
  not zero [JUDGEMENT]. An order p_G from three members of a quantity whose leading part changes sign
  between M/4, M/8 and M/16 is not defined, and |e_16| < |e_12| < |e_8| can hold or fail without saying
  anything about convergence.

Proposed wording:
"G3-G2 (mesh, against the exact solution). Window means over 50 M of tau_rem, e-bar_h, with standard
errors from the bin scatter. Converging if |e-bar_12 - e-bar_16| < |e-bar_8 - e-bar_12| and
|e-bar_8 - e-bar_12| exceeds three standard errors in at least four of the six windows after 100 M;
no order p is quoted unless the members are one family (B1) and both differences have one sign. The
converged vacuum offset of each mesh (polished finder, section 4 item 3) is quoted beside e-bar_h; the
mesh error of the growth law is max |e-bar_8 - e-bar_16|. Refuted if |e-bar_12 - e-bar_16| exceeds
|e-bar_8 - e-bar_12| by three standard errors in any window."
"G3-G3 (mesh, free of the exact solution). Delta M_h(t) = M_AH(t) minus its mean over 20-40 M. The means
over 100-400 M of D_8,12 and D_12,16 with intervals from phase-randomised noise surrogates of the
particle leg (tools/g3g3_power.py); quoted as a measured ratio with its interval. Claimed converging
if the ratio's 90 per cent interval lies in [1.2, 8]; the power of this statement at the measured noise
is computed and stated before the runs are read." If the power stays below 0.8, run the mesh members at
4N (the noise halves, B1 of JOURNAL entry 3; the particle part costs +1.1 card-hours at M/8 to 400 M and
about twice that at M/16, whose step is half [JUDGEMENT]).

### Should change

**S1. Cost and memory of G-8-16N.** G2's measured particle cost (FN4 3.19 card-hours to 400 M,
`stage/G2/EVIDENCE.md` line 61, against ES-FL's 2.60 to 500 M, i.e. 2.08 for 400 M: 0.37 card-hours
per N) gives 2.08 + 15 x 0.37 = 7.6 card-hours plus polishing for 16N, not 5.5 (cap 7) [JUDGEMENT]. State it; the smoke test already checks memory.

**S2. G3-N1 is decided before it runs, and k_95 has no estimator.** Polishing equals the tight rule to
6e-9 (finder_stop.md section 6), and the tight re-search of the same restart files exists (FP, FP-ext):
at most 7.31e-5 at M/8 (100-500 M) and 3.66e-5 at M/16 (200-300 M) (run D-20261124-172508-c847ee4,
read in my B7). G3-N1's "< 1.0e-4" holds already; its "within a factor 2" holds by 0.3 per cent on
unequal windows (1.99) and by 1.78 on the common 200-300 M. No statistic for "k_95" is defined anywhere
(SCOPE section 3.2 names sigma_k without a model). Proposed: "N at G3 reproduces G2's FP with the release
finder. The bound is k_max(h) = max over common re-searched times 100-300 M of |D_ES(t) - D_V(t)| /
ln[a(t)/a(100 M)], a deterministic bound and not a 95 per cent limit, at M/8 and M/16; the quoted bound
is the larger." Say that the criterion cannot fail unless the release finder differs from the tight one.

**S3. G3-G5 adds little to G3-G1, and its ordering clause cannot fail.** On G2's outputs the slope test
flags the known excision end of ES-FL (0.0335 with fixed windows of 0.1 in ln a, 0.052 sliding) and
passes FK (0.0048), FN4, FNQ; G3-G1 flags the same defect with the clearer margin (0.62 against 0.5 per
cent) (run D-20261128-004801-cd648e5). "The three mesh members' slopes are ordered toward it" has no
refutation. Proposed: fixed windows named in the text; the ordering clause removed or given a refutation.

**S4. The lead (section 6) needs a defined scatter and the full statistics.** "Combined tracer scatter"
is not defined; 14 tracers per label; the verifier's first R0 = 28 M tracer lies 0.11-0.13 M from the
median (v6_tracers.json), the size of the predicted M/12-M/16 step (0.13 M). The lead also grows from R_max/2
to the horizon (0.742 to 0.788 M at M/8, N) and shrinks at 4N (0.56 M throughout). Proposed: the lead
from every dust particle's clock in the snapshots (B2's estimator), at R_max/2 and at 1.2 R_AH, with
bootstrap standard errors as "scatter". If the mesh members are not one family (B1), say which part of
the lead the far-field mesh controls: G-16 changes the dust region only through the global step, and the
lead halved at M/16 in G2 although the far mesh was unchanged [JUDGEMENT: a step-size error]; a G-8 with
cfl 0.125 (2.2 card-hours) separates the step from the cell size if the lead is to be called convergent
in the mesh.

**S5. V-8 feeds no criterion.** Only P-V1 uses it (1.8 card-hours, cap 2.5). B3 needs the converged
vacuum offset of each mesh instead: re-search the restart files of V-1L and V-1L16 with polishing
(processors) and, for a new hierarchy, a short polished vacuum control of that hierarchy (to about 150 M).

**S6. G3-E1's bar is set by the mesh offset.** "G-8-e1 differs from G-8 by less than G-8 differs from
G-16" admits a gauge effect up to 1.5e-3 in e_h (B3). Proposed bar: the particle-noise level of e_h
(window means of N/4, N, 4N differ by 1.3e-4 to 3.2e-4 on G2, B1 of entry 3), i.e. "within 3e-4 of G-8 in
every 50 M window", and name the leg what it is (shift damping, the slicing unchanged).

**S7. Wording of the claims.** Claim G compares the code with an exact solution: passing it verifies the
code; the growth law itself is LTB's, and the text should say so before the Newtonian and
Zel'dovich-Novikov comparisons. Claim D, by decision 0045 "the dress it leaves", is in this set-up the
infalling matter (scope sections 1 and 8 already admit it); the claim's heading and every summary line
should say "infalling matter", and the brief's spike question stays open at G3.

**S8. The guard factor 10 is not the factor EG8 tests (8).** The mechanism is one line of source
[JUDGEMENT, finder_stop.md section 3]; state that the factor-10 runs rely on EG8 at 8, and flag the first
reason-2 dust removal after 2 M of a segment as the scope already does.

### Notes

- N1. G3-G1 (+-0.5 per cent) can fail: it flags ES-FL's excision end (0.620 per cent) and passes FK, FN4,
  FNQ (0.249, 0.237, 0.290) (run D-20261128-004801-cd648e5). It cannot see the lead (bias 6e-4 at M/8,
  N), the stopping rule (6e-5) or the angular grid (1.8e-4). It is an accuracy bound, and the text may say
  that.
- N2. G3-G4 is passable and can fail: one factor coarser, the 50 M-window rms ratio of (N/4 - N) to
  (N - 4N) is 2.11-2.91 in all seven windows, inside [1.4, 3]. Keep the raw rms: about the window mean two
  windows would read 3.12 and 3.10. Its second clause (window means of e_h within 0.1 per cent) catches
  only gross defects (G2: 1.3e-4 to 3.2e-4).
- N3. P-G1's lower edge (+0.05 per cent) may be crossed at M/16: FL16's bins lay at +0.04 to +0.09 per
  cent before its excision ended.
- N4. Claim D's areal-radius map needs the metric at the snapshot time: in ES-FL's deck the z4c slices
  come every 10 M and the snapshots every 25 M (g2long/inputs/esfl.athinput: `<output3>` dt 10,
  `<particles> snap_dt` 25), so they coincide only every 50 M. Set the z4c slice cadence to 5 M (or 25 M) in the G3 decks.
- N5. Section 2 keeps the conditions of decision 0045 that are about settings (polished finder with
  diagnostics, excision kept on, EG8 first, envelopes quoted): met in the text. The third mesh member
  (B1) and the lead "carried as a bias in every profile" (B2: in Claim D it is the profile) are not.

## 2. Criteria, one by one

| Criterion | Number fixed in advance | Model test (run) | Can it fail? |
|---|---|---|---|
| G3-G1 | +-0.5 per cent, every bin | flags ES-FL (0.62), passes FK (D-20261128-004801-cd648e5) | yes, for excision-end-size defects; not for the lead |
| G3-G2 | ordering of abs(e_h), p in [0.5, 4] | e_8 - e_16 = +1.48e-3, mesh offset changes sign (same run; FP4) | yes, but its outcome does not measure convergence (B3) |
| G3-G3 | every window, ratio [1.5, 8] | passes with 0.11-0.15 when the code converges (same run) | fails without a defect (B3) |
| G3-G4 | ratio [1.4, 3], refuted outside [1.2, 4]; e_h within 0.1 per cent | 2.11-2.91 at N/4, N, 4N (same run) | yes; sound |
| G3-G5 | 0.03 per window of 0.1 in ln a | flags ES-FL at 0.0335 (fixed windows) (same run) | yes, marginally; ordering clause cannot (S3) |
| G3-D1 | 2 per cent, bins of 400 particles | the scope's reference alone gives 73 per cent (D-20261128-005059-e65d075) | fails by construction (B2) |
| G3-D2 | orderings in 4 of 5 bins | abs(q) does not follow the lead's order (same run) | yes, but measures the lead (B2) |
| G3-D3 | 0.05 | counting noise sd 0.04-0.07 (same run) | fails by noise (B2) |
| map test | 1e-3 at t = 0 | verifier read R0 to 2e-6 M (VERIFIER 4.1) | yes; sound |
| G3-L1 | M/12 in [0.40, 0.78] M, orderings beyond "scatter" | scatter undefined; members not one family | yes, but ill-defined (S4, B1) |
| G3-N1 | 1.0e-4; factor 2; refuted above 2.0e-4 | FP gives 7.3e-5 and 1.99 already (D-20261124-172508-c847ee4) | no, decided by G2 data (S2) |
| G3-E1 | below G-8 - G-16 | that bar is 1.5e-3 (D-20261128-004801-cd648e5) | barely (S6) |
| P-C | costs within 30 per cent | G-16 8.0 x blocks; G-12 4.8 x (D-20261128-004344-1119b6f) | already refuted (B1) |

## 3. Convergence, as decision 0045 asks

- Third mesh member inside the regime: not met as written (B1). The family proposed in B1 or a
  time-restricted leg; either way measured block counts before the text is final.
- Envelopes instead of single samples: the text quotes envelopes, but uses max |.| of noisy series as the
  comparison statistic (B3). Window means with surrogate intervals are the honest form; maxima are shown.
- Particle number: N, 4N, 16N at M/8 is sound (N2); 16N costs about 7.6 card-hours (S1).
- Gauge: the shift-damping leg with the slicing unchanged and the honest statement of section 8 are
  acceptable; its bar must not be the mesh offset (S6).

## 4. Order of work and budget

What can end the plan, first, all without a card:
1. Block counts of every candidate deck with `athena -m` (seconds; tools/make_decks.py and
   block_counts.py here). This review already ends the plan as written: G-16 about 28 card-hours, G-12
   not a refinement. The total of section 10 with the measured counts and the decks as written (EG8 1.4,
   G-8 2.2, V-8 1.8, G-16 28, G-12 12.8, G-8-4N 3.3, G-8-16N 7.7, G-8-e1 2.2) is about 60 card-hours with
   no reserve and with G-12 still invalid [JUDGEMENT: blocks x steps].
2. The per-particle-clock reader of B2 on G2's snapshots (FK, FN4, FNQ, FL16, ES-FL; 25 M apart, with
   slice dumps): it fixes D1's number, the lead at every label (G3-L1) and the noise of Claim D before any
   G3 card hour.
3. The converged vacuum offset of M/8 and M/16 with polishing on V-1L and V-1L16 restart files (processors;
   B3, S5).
4. The power of the amended G3-G2 and G3-G3 at the measured noise (tools/g3g3_power.py), with the decision
   N or 4N for the mesh leg.
Then on cards: EG8 (running) -> G-8 -> a 2 M timing run of the chosen fine deck (memory, seconds per M;
this can end the mesh leg) -> the fine member -> the middle member -> particle leg -> shift leg.

## Requests

- To the lead of D-bh-dress: amend `scope/SCOPE_G3.md` for B1-B3 and S1-S8 by dated amendments before any
  production run is queued; G-8 may be queued once EG8's E1 is read.
- To core (through the lead's outbox): the cheapest hierarchy that holds M/16 (and M/12) over +-6 M without
  the 2:1 cascade to the root (block size, region alignment), and the card memory per MeshBlock of a Z4c
  run with particles, so that G-16 (3648 blocks) or G-16b (8296 blocks of 12) can be judged before a card
  hour is spent.
- To orch: the measured counts put the mesh leg as written at about half the 60 card-hours of decision
  0045 item 2 (G-16 alone about 28); a ruling is needed if the lead's amended family still exceeds it
  (time-restricted mesh leg, or a larger allotment).
