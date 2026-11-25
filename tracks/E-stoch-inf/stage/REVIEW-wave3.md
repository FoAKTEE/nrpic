# Lead's review of the wave-3 packages of E-stoch-inf (batch 2a)

Lead of batch 2a (Opus), 2026-11-21 (UTC). Packages reviewed: the two that finished in
batch 1 of 2026-11-20, `g1verify` (fresh-context verifier of the G1 material) and `ladder`
(wave-3 items (a)-(d) of the slow-roll ladder). Method, as in `REVIEW-wave2.md`: from the
artefacts, not from the helpers' conclusions. (1) Every final analysis step of both packages
was rerun unchanged from its registered inputs and every JSON leaf compared with the
registered output and with the copy committed in the package; (2) the new ladder results were
recomputed with the lead's own code on the raw dumps (own reader, own R^NR extraction, LSODA
references, amplitudes from core's twin `mode_alpha`; nothing of `ladder/` or `g1verify/`
imported); (3) the release core-v0.4, merged since the packages ran, was tested against the
scouting executable on processors (risk R1); (4) every figure of both packages was looked at;
(5) every helper outcome was compared with the prediction its helper wrote before the run.
The lead's predictions LR, LW1-LW6, LR1 were committed before the runs (owner `JOURNAL.md`,
entry 2026-11-21T06:35Z; commits 7957a3d6, 3334d7c7).

Not reviewed (not finished; cut by the usage limit at 14:35 PST on 2026-11-20 and not resumed
in batch 1): `note`, `a4res`, `usr`, `window`. Their uncommitted files are left as they are
(`HANDOFF.md` lists them and what remains). Two card jobs of `usr` and `window` ran to the end
while their sessions were gone (Slurm 4742, run E-20261120-222621-ba66218, 9.4 min; Slurm 4740,
run E-20261120-222424-0eb754b, 23.0 min); their manifests still read "submitted", no analysis
exists; they belong to those packages.

## 1. Helper predictions against outcomes (read from the journals, checked against the outputs)

### g1verify (`g1verify/JOURNAL.md` entries 0-7)

Predictions were committed before each step (commits fb6f0904 for V4-V7, earlier entries for
C0 and V1-V3). Outcomes recorded by the helper, which I checked against its result files:
- Confirmed as predicted: C0 (reader bit for bit against core's on 22 variables; Philox on
  7160 keys; alpha to 5e-16), V2, V3, V6 (orders 3.93-4.10), V7 (zero differing words).
- Failed predictions on record (helper's own): the e-fold error 1e-8 at N <= 64 (measured
  5.5e-6 at 32, 3.3e-7 at 64: the RK4 error of chi, order 4.06); the k^4 shape of the floor
  spectrum (flat late in the run). Three runs failed on its own script bugs and stay on record
  (E-20261121-030415-22d518b, -031936-16d6ae5; -030412-42dd156 superseded).
- Checked: `VERIFIER.md` was committed (db88f631) before the comparison section (c43e050c),
  as the helper states; the comparison does not change a verdict.

### ladder (`ladder/JOURNAL.md` entries 12-22)

Predictions of entries 12-15, 18 and 20 were committed before the runs they concern (entry
times and the run registration times agree: entry 13 22:35Z before card job 4757 submitted
02:56Z; entry 15 22:36Z before job 4762; entry 20 03:49Z before E-20261121-034950-06f01f9 at
03:49:50Z). Outcomes:
- Confirmed: (a) every verdict unchanged under time-matched pairing, rows bit-identical
  otherwise, sequential reader = memory-map reader; (b) PB1 (A6 at 64^3, orders 3.82-4.03),
  PB4 (late odd part independent of the Courant factor to 1e-3; H0 1.67-1.74e-13, order
  4.05); (c) PL1's stated refutation criterion (even factor 3.999994-4.0000001), PL2's projector
  term (1.309e-7 against the reference 1.293e-7), PL3 (control 4.4e5 x); step test while the kick
  acts (A/B 15.5-19.5); (d) PD1, PD3, PD4, PD5, cost.
- Failed predictions on record (eight): "every reported maximum unchanged" in (a) (the P256
  maxima sat at the dropped dump: odd/even 384.8 -> 25.1); PB2 (largest R^NR time error 6.14e-4
  against 1e-4 to 6e-4, marginal); PB3(i) (low-shell D_n changes 19.5 percent, not below 10);
  PB3(ii) second half (odd part at the smallest Courant factor largest: a rounding floor growing
  with the number of steps); PL1 sub-claim (first-order part of H up to 2.2e-2 of the even part,
  not below 1e-2); PL2 stencil part (a common first-order M of 5.94e-7 of [M], predicted below
  1e-9, falling instead of growing); PL4 as written (cancellation quantities differ by up to
  2.3e-4 between card and processors); the step/mesh prediction for t >= 0.3 (a spatial part
  takes over at 32^3); PD2 as written (A2 maximum 2.12e-4 set by a mode with |alpha| = 6.5e-4
  of the rms, not by |n| = 32).
- One run failed on a script bug and was rerun (E-20261121-034609-f573ddc -> -034645-02a463e).
- The explanations given after the data are labelled [JUDGEMENT] in the journal (PB2 radians
  argument, PB3(ii) rounding, PD2 small-alpha modes); PD2's was then tested by the outlier
  check E-20261121-045236-755a956 (amplitude of the mode 6.5e-4 of the rms; the maximum over
  modes with |alpha| above half the rms is 1.208e-4 in both seeds).

## 2. The verifier's findings and what the track does about each

The verifier confirmed V1-V7 (A1, A2, A3, the convergence of the constraints in the sense of
the track sheet, A5, A6 for the first-order solution, A7) and found the strict A4 FAILED
(A4' passes with clause (d) read on the maxima). It marked nothing of the track's verdicts
WRONG; it listed nine numerical disagreements above 10 percent and eleven weak points.

| # | Finding | Track's response |
|---|---|---|
| D1 | P256 odd/even of H "385" (stage STATUS, `results/final/`) is a time-mismatched pairing; 25 when matched | corrected in `stage/G1/STATUS.md` (25 at N = 3.93, `results/final2/`); the lead recomputed both numbers with own code (section 3, LW2) |
| D2 | halving factors 16.0, 9.0 (and 3.86, 1.93-1.97) at the last listed dump: same mismatch | corrected: time-matched 3.986-4.000 and 1.9989-2.0000 (verifier) |
| D3 | A3 ratio 4.57e-6 (track) against 2.72e-6 (verifier) on L32p | immaterial against 1 percent; STATUS quotes the range 2.4e-6 to 4.6e-6 (choice of the dump taken as N_k + 4) |
| D4 | STATUS's A1 maxima 1.1e-12 (phi), 2.0e-12 (K) understated | corrected to 2.0e-12 (phi, P256), 8.6e-12 (Pi), 3.6e-12 (K, L32p) |
| D5 | record max <|M|/[M]> at 256^3: window choice | STATUS quotes the whole record (4.0e-4) and the window to t = 4.6 (3.25e-4) |
| D6 | record max <|H|/[H]> at 128^3 4.43e-11 (final) | `final2` (constraint record, every cycle): 5.04e-11; STATUS uses it |
| D7 | negative-control separation "4e4-1.5e5" is the best case | STATUS states the record-ratio maximum and the odd-part minimum 89-179 at the end of the entry (ratio of maxima 1709-1874) |
| D8 | "second-order part independent of N within 2.2 percent" holds for 64 <-> 128 only | STATUS: 2.2 percent (64/128 raw), 0.8 percent (128/256 after each run's floor is removed) |
| D9 | card against processor normalisation (2.2e-15 against 4e-16) | information; A14 is not an A7 criterion; no change |
| W1 | one realisation | a second seed now exists (ladder (d)); the lead checked it with own code (LW1) |
| W2 | scouting executable; card build of the G1 executable not checked for layout | release core-v0.4 contains scalar-2: R1 tested on processors at 32^3 this session (section 3, LR1); the card rerun of P256 on the release (0.5 card-hours) is the next card job |
| W3 | P256's constraint split stops at t = 4.0 (P256m ends at 4.5) | open, not needed for G1 (the track criterion rests on the L set-up); a P256m to t = 8.5 (0.5 card-hours) closes it at G2 (`OPEN.md`) |
| W4 | no halved pair at 256^3 or in the L set-up above 32^3 | open; package `a4res` (in progress) and a halved pair at 128^3 in the L set-up for G2 (`OPEN.md`) |
| W5 | the floor is a definition chosen after the data | part of the request to orch (floor = the part not scaling with s, named in the ruling) |
| W6 | A4'(d) passes only on maxima | part of the request to orch (time qualifier) |
| W7 | absolute constraint levels 40-100 x below P1's statements; ratio matches | [TO VERIFY], open for the track: compare the definition of [H] and of the box statistic in P1 (PRD_v2.tex 530-541) with core's record (`OPEN.md`, `RISKS.md` R18) |
| W8 | the order of the whole odd part beyond 64 is not measurable (floor) | accepted; the in-band order 5.8-5.96 is reported as such |
| W9 | the R^NR floor ~2e-6 at L64-L256 attributed to the second-order part by judgement | open: a mirrored pair with `dump_metric = true` on both runs at 64^3 separates it (cheap; `OPEN.md`) |
| W10 | V6 only at N = 32 | ladder (b) adds A6 at 64^3 (orders 3.82-4.03); the lead recomputed it (LW4) |
| W11 | shared mode files | excluded to 6e-13 (n64) and 1.6e-6 (n256-n4096); accepted |

The verifier's three requests: the corrections to `stage/G1/STATUS.md` are made; `VERIFIER.md`
is copied to `stage/G1/VERIFIER.md`; the ruling request goes to orch
(`outbox/..__to-orch__a4-ruling-with-verifier.md`); the information to core goes with the
lead's R1 result (`outbox/..__to-core__...`). The ladder's requests 6 (quote 25, not 385) and
7 (L5 wording) are done: `stage/G1/STATUS.md`, `codebase/DESIGN_REVIEW.md` section 8.1 row L5
and the L5 paragraph of section 4.

## 3. The lead's runs (predictions LR, LW1-LW6, LR1 committed before the runs)

| Run | What | Outcome |
|---|---|---|
| E-20261121-063551-7957a3d | LR: the final analysis steps of g1verify (`v123.py`, `v45.py`, `v45_addendum.py`, `v6.py`, `v7.py`, `v7_g1exe.py`) and of the ladder (`verdicts.py` + `make_figures.py` for final2, `a6_analysis.py`, `l5_analysis.py`, `l5_scaling.py`, `ladder_analysis.py extract/judge` + `seed2_compare.py` reading the 50 GB of P256s2 dumps) rerun unchanged from their registered inputs (`scripts/rerun_all.sh`); every JSON leaf compared with the registered output and with the committed copy (`scripts/compare_json.py`) | CONFIRMED: 38136 numeric leaves in twelve files, all bit-identical to the registered outputs; every committed copy equals its run's output; the only differing leaf is a path string (npz location in `P256s2_judge.json`). `review3/fig/fig_rerun.png`, `review3/results/rerun_compare.json` |
| E-20261121-063758-d643396 | first attempt of LW1-LW6 | FAILED (my bug: the replaced deck reader called itself), on record |
| E-20261121-063816-64ac0dc | LW1-LW6 with my own code (`scripts/lead3_check.py` on top of `G1/scripts/lead_check.py`: own reader, own R^NR, LSODA background and MS, alpha from core's `mode_alpha`, run parameters from the command line the code logged) | see below; `review3/fig/fig_lead3.png`, `review3/results/lead3_check.json` |
| E-20261121-064707-77ec326 | LR1: L32p and L32m (`ladder/inputs/proc32.list`) on the release core-v0.4 processor build `.work/build_cpu_v04` against the same rungs of E-20261115-172636-ce98836 (core/scalar-2), word by word (`scripts/r1_run.sh`, `r1_compare.py`) | CONFIRMED: 18 dumps per rung, 18.9 million 64-bit words, 0 differing; times and cycles bit-equal; both records identical in all 175 rows. `review3/fig/fig_r1.png`, `review3/results/r1_compare.json` |

LW1-LW6 against the helpers' numbers:
- LW1, second seed of P256 (ladder item d): A2 2.121e-4 over |n| <= 32 (ladder 2.12e-4), 4.494e-3
  over all modes (4.494e-3); A3 3.80e-6 (ladder 4.4e-6; the dump taken as N_k + 4 differs, as
  between ladder and verifier on seed 1), drift 1.380e-4 per e-fold (1.380e-4); A1 2.16e-12,
  6.31e-12, 2.15e-12 (2.0e-12, 6.3e-12, 2.0e-12); seed 20261120 confirmed from the logged
  command line. CONFIRMED.
- LW2, the "385": time-matched maximum 25.15 at t = 4.0 (ladder final2 25.1, verifier 25); the
  index-paired last dump stands at t = 4.50377 against 4.50000 and gives 384.8. CONFIRMED: the
  number of waves 2-2b came from the pairing, as the verifier and the ladder say.
- LW3, records: P256 5.105e-11 / 3.994e-4, P256s2 5.112e-11 / 3.999e-4. CONFIRMED.
- LW4, A6 at 64^3 (ladder item b): <chi> 4.03; late odd part of H independent of the Courant
  factor to 4.7e-4 and less from N = 2.42; orders of phi and chi 3.84-4.04 at t >= 0.98.
  My max-norm order of K is 3.52 at t = 0.98 and 3.47 at t = 0.49 (ladder, rms norm: 3.82-4.01):
  my prediction (3.8-4.2) fails there; A6 (3.5-4.5) holds from t = 0.98 on in both norms.
  CONFIRMED for A6 with this reservation.
- LW5, L5 (ladder item c): even factor 3.9999936-4.0000001; first-order M after one step
  5.943e-7 (stencil), 6.083e-7 (continuum); continuum minus stencil 1.3091e-7 against the
  reference 1.293e-7. CONFIRMED, digit for digit with the ladder.
- LW6, step test: A/B 15.5-19.5 for t <= 0.25. CONFIRMED.
- LR1, risk R1 on processors: the release reproduces the scouting executable bit for bit at
  32^3 (above). The card build of the release is not yet compared (P256 rerun, 0.5 card-hours,
  HANDOFF).

## 4. Per package: confirmed, not confirmed, wrong

**g1verify.** Confirmed: every number of `VERIFIER.md` that comes from its registered analyses
(rerun bit for bit, 8414 numeric leaves in six files); its central claims recomputed by the lead's
own code where they overlap (the 385/25 explanation, LW2; the record maxima of P256, LW3;
A1-A3 on L32p-L128p by the wave-2b lead check, which agrees with its V1-V3 to the printed
digits); its figures fig_v1-fig_v7 show what the text says; its process (verdicts committed
before it read the track's numbers, db88f631 before c43e050c). Not confirmed by me: its 256^3
R^NR passes (pass 1, 31 min, 45 GB) and the constraint pass (12 min, 60 GB) were not rerun; I
reran everything downstream of them, and `nrpic-run verify` passes on their outputs
(E-20261120-223154-d42de1a, E-20261121-025750-d1b6139, -030657-c1afe38) and on the V7c run
(-031049-27cdc06), i.e. the files I reran from are the files it wrote. Wrong: nothing found. Its own reservations stand (weak points W1-W11, section 2).

**ladder.** Confirmed: items (a)-(d) by bit-identical reruns of every analysis (29722 numeric leaves
in six files) and by my own code on the raw dumps (LW1-LW6); the eight failed predictions are on
record as the journal says; predictions were committed before the runs (checked by git
ancestry: entries 12-15 before runs 684821a, 02526ff, fe18c5f; entry 20 before 06f01f9). Not
confirmed: R1 on cards (no merged card executable was compared; now possible with the
release). Wrong: nothing in the wave-3 results; the wave-2b number "odd/even 385 at N = 256"
that the stage package quoted was wrong and is corrected (D1).

**Defects fixed by the lead:** `stage/G1/STATUS.md` (D1-D8), `codebase/DESIGN_REVIEW.md` 8.1
row L5 and the L5 remark of section 4 (ladder request 7). **Larger items listed, not fixed:**
`OPEN.md` items 2-4 (note products; P256 on the release card build; P256m to t = 8.5, halved
pair at 128^3/256^3, R^NR floor separation, absolute constraint levels).

## 5. Stage packages after this review

- G0: signed PASS on 2026-11-20 (`coord/GATES.md`, tag `stage/E-stoch-inf/G0-pass-20261120`);
  every item was present then; not touched in this session.
- G1: `nrpic-stage collect`, `verify --no-checksums`, `report` rerun on 5aa8bcd4/478299f9.
  The verifier's report is in (C16 PASS). Not met: C6 (A4' ruling) and the note products C8,
  C9, C13, C14, C15. Verify fails only on `clean` and `runs`, both from the cut packages (not
  G1 material). Not complete for the independent gate review of decision 0016 item 4.

---

# Part B. Batch 3 (lead of batch 3, 2026-11-21): packages `note` and `usr` of batch 2b

Lead of batch 3 (Opus), 2026-11-21 12:58Z onward. Packages reviewed: `note` (the G1 products
C8, C9, C13-C15 of the working note) and `usr` (the ultra-slow-roll case on the cards, G2
material), both finished in batch 2b. Not reviewed: `a4res`, which a helper session of this
batch is working on in this worktree at the same time (it committed its scripts and
submitted card job 4798, run E-20261121-131000-b23055b, pending at 13:30Z); and `window`
(card job 4740 finished on 2026-11-20; its manifest was closed by the lead with `nrpic-run
finish`, 721 files checksummed; nothing else touched, no analysis yet). Method as in Part A: (1) every analysis of both
packages rerun unchanged from its registered outputs and every JSON leaf, PNG and table
compared (run E-20261121-130021-0140e4e, `review3/scripts/rerun4.sh`, `note_compare.py`,
`compare_json.py`); (2) own code on the raw dumps for the central usr numbers (run
E-20261121-130236-e39e143, `review3/scripts/lead4_check.py`: the verifier's reader
`g1verify/scripts/nrsf.py`, numpy FFT, nothing of `usr/scripts/` imported); (3) every figure
looked at (13 of `usr/fig/`, the 7 new or redrawn of `note/figures/`, the lead's
`fig_lead4.png`); (4) every helper outcome compared with the prediction written before its
run, with git ancestry; (5) the note's G1 ledger compared row by row with the independent
values of the verifier and of the leads' own-code runs (B4). The lead's predictions LR4,
LU1-LU3 were committed before the runs (owner `JOURNAL.md`, entry 2026-11-21T12:58Z; commit
0140e4ef).

## B1. Helper predictions against outcomes (journals, checked against the outputs)

### note (`note/JOURNAL.md`, predictions N4-N12)

Ancestry: N4-N8 were committed with the wave-3 set-up (e2f926e3, 2026-11-20); N9-N10 are in
1849987a (before run E-20261121-075717-1849987), N11 in 7fbe919a (before -080526-7fbe919), N12
in 6112292a (before -080840-6112292). Outcomes: N4 held (drafted unregistered, then reproduced by
the registered runs); N5/N9 held (every input passes its checksum); N6/N9 held (every figure
repeats with pixel rms 0); N7 held (94-102 s against 10 min); **N8 FAILED in part** (the ladder
README's A1 maxima, claims g22, g23); N10, N11, N12 held. Cosmetic defect: the journal heading
"08:20 UTC" of the outcome of run -075717 is out of order (that outcome is already in commit
7fbe919a of 08:05Z); it does not affect the order of prediction and run.

### usr (`usr/JOURNAL.md`, entries 9-15)

Ancestry: entry 9.3 is in ba66218 (14:26 PST), before job 4742 started (14:36:46 PST, sacct).
**Entry 10 (the amended bar of U-A4 for H, 3e-13 instead of 1e-12 of <[H]>) was first committed
in 7f764776 at 23:50 PST, after job 4742 had run**; its pre-registration rests on its own time
stamp (22:35Z) and on the batch-2a HANDOFF's description of the then-uncommitted file. It
rescues no verdict: with the original bar the even part of H at s = 1/2 (at most 3.4e-13 of
<[H]>) is judged at no dump; with the amended bar it is judged at one dump and fails (3.82).
Entries 12.1, 13, 14.1, 14.3 are each in the commit of the run they predict or earlier (a0cc3eb2;
1f579fe3 before job 4783 at 01:40 PST; 19571c7f; 2f068acc). Entry 12.1 is labelled post hoc by
its author.

| Prediction | Outcome (checked) | Verdict |
|---|---|---|
| 9.3 G1a: U-A0/U-A1 on 64^3, 128^3 | abs dN 4.2e-7, 2.6e-8; <Pi> 2.50e-5, 1.33e-6 | held |
| 9.3 G1b: lockstep 2.6e-5, 1.6e-6 +- 30 % | 3.57e-5, 2.25e-6 | **FAILED** (1.4 x; cause tested in 14.2: RK4 phase error) |
| 9.3 G1c, G1d, G1e: odd-part per-mode error, even/odd 2.19e-5, U-A3 | as predicted (1.14e-4, 2.12e-6; 2.187e-5, half at s = 1/2; 4.8e-5, 2.5e-6) | held |
| 9.3 G1f: record of H 6.2e-9, 3.6e-10 | 6.24e-9, 3.75e-10 | held |
| 9.3 G1f: record <abs M/[M]> at most 1e-3 | 1.07e-2, 2.47e-2, 4.3e-2 (late) | **FAILED** |
| 9.3 G1f / U-A4 (a), (b): halving 4.00 and 2.00 +- 0.05 above the bars | H even 3.82 at its one judged dump; M even 3 of 20 within; M odd 0 of 20 | **FAILED** as pre-registered |
| 9.3 G1f: odd part of M during USR at 128^3 lower by 16-90 | per dump 37-60 to cN 4.05; max over the window 4.6e-4 | **FAILED** as written (window max), held per dump |
| 9.3 U-A4 (c), (d) | orders 5.15-5.90 where above the floor; strict A4 at 128^3 holds for M (0.079), H not judged | held where judged |
| 9.3 G1g: cost | 0.157 card-hours | held |
| 12.1 F1 (post hoc): floor-corrected even factor 4.00 +- 0.10 | 3.987-4.001 (H and M, ten dumps each) | held (not blind) |
| 12.1 F2 | 8/20 and 10/20 within 15 % | **FAILED** |
| 9.3 U1, U4, U5, U6, U7, U8 (U256) | all inside their ranges (abs dN 1.6e-9; <Pi> 4.17e-5; U-A3 0.9923-1.0016; U-A5 5.9e-4/6.7e-3; rms 0.89452, skew 0.0024, max 4.568; records; 1.298 s per step, 0.617 card-hours, 19.6 GB) | held |
| 9.3 U2: lockstep within 1e-6 | 2.55e-3 | **FAILED** (by 2500; the RK4 phase error k^5 dt^4/600) |
| 9.3 U3: U-A2 as written on the single U256 | max 5.9e-2 on 10 of 68532 modes | **FAILED** (small-alpha clause held: all ten have rank below 7e-4) |
| 9.3 U3 refutation clause (shell-normalised < 0.02 at every dump) | 6e4 ... 8.7e-2 at the first four dumps | **FAILED** as written (normalisation by a reference the window has not switched on) |
| 13: late M of U256m odd > even, even/odd in [0.05, 0.7] | 0.15-0.44 to cN 8.0, then 0.81-1.00 | **FAILED** from cN 8.5 |
| 14.1 L1-L3, 14.3 (four clauses), 9.3 U256m (three clauses) | as predicted | held |

## B2. The lead's runs (predictions LR4, LU1-LU3, committed in 0140e4ef before the runs)

- **LR4 CONFIRMED in (a), (b), (d) and for the committed copies; REFUTED in (c) by 13 leaves**
  (run E-20261121-130021-0140e4e, 3 cores, 30 min; comparison `review3/results/batch3/
  rerun4_compare.json`, `note_compare.json`; figure `review3/fig/fig_rerun4.png`, looked at;
  its title still names the batch-2a packages, a label of the shared comparer). (a) group 1:
  0 of 4220 numeric leaves differ (the current script writes 386 more leaves than the
  registered run, added by later commits of the package); floor split 0 of 241 (one string,
  the source path); quick records 0 of 294. (b) pair U256/U256m: 0 of 12289; and the single-run
  section U256 equals the summary of E-20261121-084815-63462b8 in all 4279 shared leaves. (d)
  note: all 12 PNGs byte-identical to the committed and to the registered ones (pixel rms 0),
  all six tables byte-identical. Every committed copy in `usr/results/runs/` equals its run's
  output. (c) lockstep: 13 of 56 leaves differ, all from the code-time reference of the 3414
  shells at 256^3: lowest-shell error 9.3072e-8 against 9.2992e-8 (8.6e-4 relative, 8e-11
  absolute), top shell 5e-9 relative, the ratios of L1 by at most 6.5e-7 and of L3 and the
  odd-part ratios by at most 8e-9; the 64^3 and 128^3 entries are bit-equal. Reading
  [JUDGEMENT, not tested by a run that could fail]: my rerun exported OPENBLAS_NUM_THREADS=3
  where the registered run left it unset, so the reference ODE integration ran with another
  BLAS thread count and differs at its tolerance. No verdict changes (L1 0.9734-1.0235 within
  the factor 2; L3 and 14.3 unchanged to 8 digits). The lowest-shell number 9.3e-8 is
  therefore known to about 1e-10 absolute.

- **LU1 CONFIRMED** (own code, phi part of R^NR only): at N_f, rms 0.8945204 (U256) and
  0.8945199 (U256m) against the helper's 0.8945204, 0.8945199; skewness 0.0023740 and 0.0006108
  (helper 0.0023740, 0.0006108); max abs R 4.5678 and 4.5567 (4.5678, 4.5567); even/odd of the
  mode coefficients 2.533496e-4 over the 68532 modes 0 < |n|^2 <= 1024 (helper 2.533497e-4) and
  2.8766e-4 over the 548958 modes |n|^2 <= 4096 (helper 2.88e-4). The agreement to six or seven
  digits without the chi and anisotropic parts confirms that R^NR is carried by delta phi in
  USR (the helper's parts 6.1e-6, 1.6e-6). The even part relative to the odd one is not flat
  in k (`fig_lead4.png` (a): 3.7e-4 at |n| <= 3, 2.4e-4 at |n| ~ 15, 3.1e-4 at the top shells).
- **LU2 CONFIRMED against the file, my written prediction FAILED for dump 4**: at dumps 4, 6, 8
  (cN 2.06, 3.06, 4.05) all 18 numbers (raw even, raw odd and floor-corrected even factors of H
  and M) equal `floor_split` E-20261121-080134-a0cc3eb to relative difference 0 (same
  definitions, independent code). The values I wrote for dump 4 were copied from the dump at
  cN 1.55 (index 3), a transcription error of mine, on record.
- **LU3 CONFIRMED in part, FAILED in part**: record maximum of <abs M/[M]> 2.5193e-2 (U256, at
  cN 6.64) and 2.5195e-2 (U256m); value at N_f 2.1269e-3 and 2.1283e-3: the final values differ
  in the fourth digit (7e-4 relative). Reading [JUDGEMENT]: the record of abs M is not even in
  s once the even part of M is as large as the odd part, which entry 15 measured from cN 8.5
  on; the helper's "records equal to 4 digits" holds for the maxima, not for the late values.
  Card time from sacct: jobs 4742, 4774, 4783 ran 9:24, 37:00, 36:42 = 0.157, 0.617, 0.612
  card-hours (one card each): confirmed.
- Figure `review3/fig/fig_lead4.png` (copied from the run): (a) even/odd per shell, (b) the
  halving factors of LU2, (c) the two records; looked at.

## B3. Per package: confirmed, not confirmed, wrong

**note.** Confirmed: C8, C9, C14 (architecture with four states, data flow, timeline: looked
at; they match the state of the program on 2026-11-21 except that "ultra-slow-roll runs at
256^3 on cards" is still drawn as under way, true when drawn); C13 (four G1 data figures, one
script each, from registered outputs; the rerun reproduces them, B2); C15 (main.tex v1, 16
pages; its A4 text states the strict failure on record and A4' as ruled by decision 0021
item 1, read in the extracted text); the ledger rows equal their files (the rerun's ledger is
byte-identical, B2) and 27 of its 40 track rows agree with an independent value (B4). Not
confirmed: core's three rows (labelled [TO VERIFY] in the ledger; the check belongs to
`a4res`); the 13 rows of B4 marked "track only". Wrong: N8's two README numbers (fixed now in
`ladder/README.md`); the journal heading time (cosmetic); Table V's spread row (cosmetic). The
note's requests 1-3 are done by the lead (`NOTATION.md`, `WRITING_GUIDE.md`,
`ladder/README.md`); request 4 is done in `stage/G1/CHECKLIST.md`; request 5 waits for
`a4res`, `window` and the usr text.

**usr.** Confirmed: the six card runs and both 256^3 runs ran to N_f with rc 0 on the
core_scalar-3 card build (sacct, manifests); U-A0, U-A1, U-A3 on every rung; U-A2 on the odd
part (pairs at 64^3, 128^3, 256^3); the even/odd split, the one-point statistics and the
second-order skewness of the 256^3 pair (LU1, own code); the halving and floor reading of
group 1 (LU2); the cost per USR realisation, 0.617 card-hours (sacct); the lockstep reading
(L1-L3, its figure); every figure shows what the journal says. Not confirmed: that the
s-independent floor is rounding (a reading, as the helper says; no run in another precision);
the cause of the late momentum level at 256^3 (1.6e-13 to 1.9e-13 absolute, seven times the
128^3 floor; not named); whether 10 modes failing U-A2 in a single run would fail in a second
realisation (one realisation only). Wrong: "records equal to 4 digits" for U256m (LU3: the
late values differ at 7e-4); the pre-registration of entry 10 cannot be dated by git (B1).
All its failed predictions are on record in its journal.

**What the track does about the usr findings.**
1. The card pre-registration (entries 9.1 and 10) stands as the record of what was predicted.
   U-A2 for the single U256 run and U-A4 as pre-registered stay FAILED on record.
2. Proposal to orch (outbox, this session): read U-A2 at 256^3 on the odd part of a mirrored
   pair (as at 64^3 and 128^3) and U-A4 on the parts with the s-independent floor removed,
   the floor from the odd parts of the halving pair (U-A4', the analogue of A4' of decision
   0021). Both are after the data; the strict forms stay failed.
3. "USR case reproduced" (G2) is not declared now [JUDGEMENT]: the linear USR dynamics are
   reproduced in P1's set-up to 1.1e-4 per mode, but G2 also asks for the window sensitivity
   (package `window`: its job has run, no analysis), resolution in P1's set-up (one 256^3
   resolution so far), and runs on the release executable (core-v0.5 contains scalar-3).
4. RISKS R9 is updated with the measured 0.617 card-hours per USR realisation.
5. Request to core (outbox): sub-step the lockstep record of the mode functions (or start each
   shell later), which removes the RK4 phase error of the top shells; not blocking.
6. Open, for a later usr session: a halving pair at 256^3 (s = +-1/2, about 1.2 card-hours)
   for the late momentum level; a second U256 realisation for the small-alpha modes.

## B4. The note's G1 ledger against independent values (C16, ledger part)

The verifier's report was written before the ledger existed (its last paragraph); its
comparison section and verdicts V1-V7 give independent values for most rows. "V" = the
verifier (`stage/G1/VERIFIER.md`, own reader, own MS, own Philox; line of the value), "L2a" =
the lead of batch 2a (own code, Part A section 3), "L3" = this lead (LU1), "rerun" = the same
script rerun bit for bit only.

| Ledger row | Ledger | Independent value | Status |
|---|---|---|---|
| A1 box means phi, Pi, K | 2.0e-12, 8.6e-12, 3.6e-12 | V 348-349: P256 phi 2.0e-12, Pi 8.55e-12; V 78: Pi 8.6e-12, K 3.6e-12 over all runs (phi 3.2e-12 incl. controls) | agrees |
| A1 e-folds 32-128 | 5.5e-6, 3.3e-7, 2.0e-8 | V 82: same | agrees |
| A2 ladder, paper set-up, all-mode maxima | 8.8e-5 ... 1.21e-4; 4.08e-3, 9.65e-5, 7.09e-6 | V 101-107, 350-351: same to three digits | agrees |
| A2 mode counts | 548958, 68532 | V 107 (68532); L3 (548958, 68532 on the hemisphere) | agrees |
| A2 stencil wave number reference 6.16e-3 | 6.16e-3 | none | track only |
| shell ratio, slow-roll ratio | 1.9e-4; 1.0104-1.0109 | V 353: 1.6e-4 to 1.9e-4; 1.0104-1.0109 | agrees |
| A3 modes, ratio, drift, code minus MS, FLRW drift | 1051; 4.6e-6; 1.379-1.405e-4; 1.75e-6; 0.0513-0.0527, 365 | V 123-132: 1051; 2.4-3.2e-6 (dump choice, V 370); 1.4e-4; 1.7e-6; 0.0516-0.0530, factor ~350 (V 355) | agrees (ratio within the definition difference) |
| A4 odd/even maxima 32-256 | 745, 655, 869, 25 | V 360: 743, 659, 867; L2a LW2: 25.15 | agrees |
| A4 e-folds of maxima; first odd > even | 2.47 ... 3.91; 1.51, 1.99, 2.96, 3.44 | V 357-358 (first crossing the same); maxima e-folds none | crossing agrees; maxima e-folds rerun only |
| A4 record maxima | 5.1e-11; 3.8e-4 | V 144-146: 5.1e-11; 3.8-4.0e-4 | agrees |
| A4 halving 32^3 | odd 1.9999-2.0000, even 3.991-4.000 | V 160-162: 1.9989-2.0000, 3.986-4.000 (L32, Q64, Q128) | agrees |
| A4 convergence set-up odd/even 15.4, 0.27, 0.53 | | V 157-159 qualitative (L64 above, L128/L256 below) | qualitative only |
| Negative control ranges | 4e4-1.5e5; 0.20-0.22 | V 165-169, 361: M 0.204-0.216; H ratio "different statistic" (V 374) | M agrees; H range track only |
| A5 orders H, M | 4.20-5.82; 5.55-5.91 | V 355-356: identical | agrees |
| Floor exponent H; M | 2.48; 2.63 | V 206: 2.45-2.51; M none | H agrees; M track only |
| Floor at 256^3 first/last | 6.0e-13, 6.9e-15 | V 208: 6.3e-13 ... 3.3e-15 (out-band definition) | same order, other definition |
| Even part 64 vs 128 | 0.022 | V 375: 0.978-1.015 | agrees |
| Record H at N_f per rung | 3.12e-12, 1.83e-13, 1.12e-14 | none | track only |
| A6 orders; uniform residual order | 3.93-4.08; 4.10 | V 230-233, 362: 3.93-4.10; 4.10 | agrees |
| A6 R^NR difference 2.9e-4; top-shell D_n; odd-part change 0.041 | | none | track only (three rows) |
| A7 noise and restart 0; card vs processor 2.2e-15 | | V 247-254: 0 words; V 376: 3.2-4.4e-16 (other normalisation) | 0 agrees; 2.2e-15 normalisation differs |
| A7 22 of 22; release vs branch 18.9e6 words, 0 differ | | the verifier's own (V 255-258); L2a LR1 | own runs |
| Analysis rows (15/15; 2.35e-4, 0.999, 0.657; reader 0, 7.5e-10; E6 factors) | | wave-2b lead's independent extraction (E-20261119-150238-b81e33f) for E6 and the reader; V 97 (R^NR at t = 0 to 1e-10) | partly; synthetic-test rows track only |
| Cost 0.503 card-hours, 1811 s; steps 1386; 1.13-1.30 s per step | | V 265-267: 0.5031, 1811 s; steps and s/step none | cost agrees; two rows track only |
| Verifier rows | | the verifier's own numbers | own |
| Core rows (mu/k^2, 692, 12.7, 20 dk) | | none; labelled [TO VERIFY] | open (package `a4res`) |

Summary: the ledger has 45 rows: 2 are the verifier's own numbers, 3 are core's (labelled
[TO VERIFY] in the note), and 40 are the track's. Of these 40, 27 agree with an independent
value (V, L2a, L3; rows 32, 37-39 only in part, as marked) and 13 are the track's alone (rows
7, 16, 20, 21, 23 for M, 24, 26, 28-30, 35, 36, 40 of `note/tables/ledger_g1.md`), each
reproduced by a rerun of its registered analysis or of the ledger (Part A LR; B2 LR4). No row disagrees beyond a
stated difference of definition. [JUDGEMENT] This meets the ledger part of C16 for an
independent gate review; a gate reviewer may still ask a fresh agent for the 13 track-only rows.

## B5. Stage packages after this review

See `G1/STATUS.md`, `G1/CHECKLIST.md`, `G1/STAGE_REPORT.md` (rerun in this session). G0 is
signed (2026-11-20) and not touched.

# Part C. Batch 5 (lead of batch 5, 2026-11-21 afternoon): packages `a4res` and `window`

Both packages finished in batches 3 and 4a and were not reviewed by a lead before. Method: the
predictions in the packages' journals were checked to be ancestors of the runs they predict
(git), each analysis was rerun from its registered outputs, the committed results were compared
leaf by leaf with the rerun (`review5/scripts/compare_leaves.py`), one central number of a4res
was recomputed with code that is not the package's (`review5/scripts/lead5_check.py`, reader of
g1verify), and the figures the verdicts rest on were looked at. The lead's predictions LC1-LC3
are in the track JOURNAL (batch 5 entry, commit a9b5d10c). LC1 was written after the a4res
rerun had finished and been compared (12:34 PST against the commit at 12:35): it is on record
as a post-hoc statement, not a prediction.

## C1. a4res (strict A4 against resolution; card run E-20261121-131000-b23055b, 0.188 card-hours)

- Predictions Q1-Q8 (`a4res/JOURNAL.md` entry 3) are in commit b23055b, the commit of the card
  run's id: written before the job. Q9-style post-hoc checks (entry 5) are labelled as such.
- Rerun E-20261121-203016-7209255 (2 cores, 253 s) of `a4_analysis.py` and `post_checks.py`:
  5442 numeric leaves of `a4res.json` and 60 of `post.json` identical to the committed files
  (relative difference 0; the one string that differs is the input path); `verdicts.md`
  identical apart from wall times. CONFIRMED.
- Own code (LC3, run E-20261121-203540-a9b5d10, verifier's reader, box means removed, rms over
  the box, pairs at equal times): largest odd/even of H over the dumps with t > 0: N64q16
  0.4548 (package 0.455), N64q25 0.9997 (0.9997), N64q64 15.45 (15.5); of |M| 0.314, 0.795,
  13.83 (package 13.8 for N64q64). LC3 HELD. Figure `fig_lead5_ratio.png` in the run directory,
  looked at: the same curves as `a4res/fig/fig_ratio.png` panel (a) (also looked at).
- Confirmed: strict A4 holds at 12.8 and 16 cells per shortest source wavelength and fails at
  10.7 and 8; core's crossing at 12.7 cells (Q2); halving where testable (Q4); order 5.80-5.84
  (Q7); records (Q8).
- Not confirmed by me: Q3 (twin agreement 1.000-1.059) and Q5 (I did not rerun the twin with
  other code); the stencil symbols of step 1 (C1 of core) beyond the rerun.
- On record as failed: Q6 (even parts of N64q64 and N128q64 differ by 10.9 percent at t = 0.147,
  within 3.1 percent at the 35 other dumps; the interpolation explanation refuted post hoc,
  cause not found). A4'(b) "fails" for N64q16, N128q100, N128q64 in `verdicts.md` means no
  qualifying dump at 10 floors, not a measured failure (the README says so; correct).
- What the track does: forwards "For the A4 ruling" to orch as information (no new ruling
  asked; A4' of decision 0021 stands); tells core that C1-C3 are confirmed and C4 does not hold
  (outbox 20261121T203614Z). The optional 3-card-minute run with common dump times for Q6 is
  not queued: Q6 concerns A4'(a) at G1 resolution in the L set-up and decides no G2 criterion;
  it stays in OPEN (G2) as a known unexplained deviation at one dump.

## C2. window (sensitivity L9; card job 4740, run E-20261120-222424-0eb754b, 0.384 card-hours)

- Predictions W1-W8 (`window/JOURNAL.md` entry 1) are in commit 0eb754b, the commit of the
  card run's id: written before the job. The post-hoc P-a, P-b (entry 4) came after the main
  analysis and before their own run (78859e9b before E-20261121-155344-78859e9).
- Rerun E-20261121-203008-f104a3e (2 cores, 565 s) of `analyse_window.py` and
  `posthoc_window.py` from the registered dumps: 427 numeric leaves of `summary_usr.json`, 371 of
  `summary_sr.json`, 281 of `posthoc_usr.json` identical to the committed files (relative
  difference 0; one string, the input path, differs); `table_usr.md`, `table_sr.md` identical.
  LC2 HELD (better than predicted: no BLAS-order difference at all).
- Figures looked at: `window/fig/fig_usr_shift_Nf.png` (shift of the odd-part shell power at the
  last dump: below 2e-4 to k = 16 dk, rising to 9e-3 at 32 dk; sigma = 2 raises and sigma = 0.5
  lowers the top shells systematically, each below its NR-vs-reference bound |e_w| + |e_b|).
- Confirmed: W1, W3a, W4, W5, W7, W8 hold as the package states; the U-W criterion of SCOPE 4c
  rests on these numbers (1.9e-4 to k_max/2, 9.1e-3 to k_max).
- On record as failed and correct as stated: W6 refuted (late records depend on sigma by x0.14
  to x21.7); W2's per-mode clause failed (2.4e-2 on single small modes); W3b's premise failed
  for USR; P-b refuted for sigma = 2 at 6 <= k < 12.
- Weak points, and what the track does: (i) the "error of the shift" is a bound that holds by
  construction because the linear shift is zero; no independent error per window (no resolution
  pair per window) exists. SCOPE 4c U-W states the criterion as a bound, labelled as fixed after
  the scan; a resolution pair per window is not queued (it would cost about 0.4 card-hours per
  window at 128^3; listed in OPEN of G2 as optional). (ii) The predictions were judged at the last
  dump cN = 9.585 (t = 10.0), not at N_f = 10: the g2prod deck dumps at t = tlim exactly
  (dump_dt = tlim/20), so G2 judges at N_f. (iii) The window runs are 128^3 on the scouting
  executable core_scalar-2; U-W is a statement about the window, not about the release; the
  release repeat of the baseline is U256ap/am.
- The README's request: RISKS R8 updated (scan done, U-W); the note's \pending{} marker for
  window (Sec. IX) is left to the next note session (no note text in this session, decision 0025
  item 4).

## C3. Stage packages after this review

G0 and G1 are signed and not touched. G2: `stage/G2/CHECKLIST.md` collected this session (20
items); C7, C8 hold evidence pointers and stay OPEN until g2prod has run; C9 PASS; C4 proposed
NA (no kinetic matter before the hand-over). No gate is complete for review.

# Part D. Batch 10a (lead of batch 10a, 2026-11-22 evening): the g2prod card runs

No helper package finished in this batch: the eleven card runs of `g2prod` (submitted by the
lead of batch 5 and its sequencer) were analysed by this lead, so this part is the analysis
record, not an independent review. The independent check of G2 is still owed (C18, a fresh
verifier with the artefacts).

What was checked from the artefacts (registered outputs; every figure looked at):
- Sequencer: ended by itself at 13:49 PST ("queue empty and every run closed"); all eleven runs
  completed and closed with checksums; card-hours 7.51 in total (T 0.11, P256v6 0.51, six
  256^3 chains 0.62 each, two 320^3 chains 1.47 and 1.48, control 0.22); no chain was killed
  from outside; the 320^3 chains ran in two segments (restart exact for periodic set-ups).
- T and P256v6: `g2prod/JOURNAL.md` 2.1 (analysis E-20261123-015014-b4ecd4e).
- U320 and seed B: 2.2 (E-20261123-020751-0baf597, E-20261123-021730-a421438).
- Seed A with the halving pair and the control: 2.3 (E-20261123-014858-8e72d4c and the judge
  run named there).

Defects found in this session's own analysis code (fixed, on record in g2prod 2.2): a one-dump
crash of the --last mode (run E-20261123-015650-493cff5, failed) and a seed-B pass referred to
seed A's realisation (E-20261123-014905-2bf3570: per-mode numbers invalid, superseded by
E-20261123-021730-a421438). Nothing found wrong in the card runs themselves.

# Part E. Batch 13 (lead of batch 13, 2026-11-24 afternoon): what the reproduction left to the lead

The reproduction of arXiv:2512.14649 and arXiv:2401.08530 (decision 0028; packages repro/scope,
langevin, equations, ablation, continue, figs, note, verify) is complete
(`coord/digests/reproduction-state.md`); its fresh verifier is repro/verify (two passes,
`repro/verify/VERIFIER.md`). This part records what the lead checked from the artefacts, not from
the packages' conclusions, before closing the items they left to the lead.

## E1. Checked by the lead

- RSF256 fourth continuation E-20261124-214913-5956891 (q0034, job 5215): manifest `completed`,
  0.2872 card-hours; the join check E-20261124-225720-444aecc (repro/figs, with repro/continue's
  `join_check.py`) read from its `join_check.json`: every boolean true except the literal J3 at the
  cycle-0 junctions and `cont_has_header` (continuations write no header, by design), J2 958 of 958
  lines identical (largest relative difference 0), joined record 0-1386, dumps 00000-00034.
  CONFIRMED; recorded in `repro/continue/scripts/conts.json` and its journal entry 13 (K2 held).
- SR span: the joined `RSF256.sf.hst` column 21 (ln a) is 0 at t = 0 and 8.0989 at t = 8.5. The
  audit's "N* + 8.04" was WRONG; corrected to 8.10 in `repro/scope/SETUP_AUDIT.md` item 4 (the deck
  header comment `sr_paper.athinput` line 11 still says 8.04: a comment, left as is, listed here).
- S14 wording: `fig_contrasts.py` stores column 7 of `figlib.QUANT` = 99.5 under the key
  `pct_H_p99_max`; the USR row of RESULTS.md S14 now says 99.5th. CONFIRMED and fixed.
- Card costs: summed from the manifests (`resources.gpu_hours`) into `repro/scope/CARD_PLAN.md`:
  scope 2.611 + continuations 1.452 = 4.063; ablation 4.811 + 0.120 (AL2S continuation) = 4.931;
  reproduction 8.99 card-hours. The continue journal's "1.28 for the first eight" plus 0.29 agrees.
- Floor of the spectral convergence: recomputed from the dump-pass files (C128S of
  E-20261124-133251-42e8aab, CL256Sc of E-20261124-213029-e937f69): median abs(1 - P_NR/P_lin) over
  the shells n^2 = 2-12 is 1.48e-7 and 1.55e-7, amplitude statistic 3.78e-7 at both, the signs of the
  ten shells identical (++----+--+); the stencil part at n^2 >= 49 is 6.0e-7 at 128 and 3.6e-8 at
  256. CONFIRMED (RESULTS.md Fig. 7); the test at half amplitude is queued (package `floor`, F1-F5).
- Ablation draft `repro/ablation/outbox_draft/core_t5.md`: not posted; superseded, core judged T5 of
  `core/noise-level2` PASS on the card itself (commit 68d4ee56 on core's branch) and its review on
  Fable found the six ablation runs unchanged (inbox, acknowledged).

## E2. Not checked by the lead in this session

The 133 ledger rows of the note (the fresh verifier's verdicts stand, with the rows it did not
recompute listed in the digest); the 26 pages were not reread.

## E3. Stage package G2 after this review

`stage/G2/CHECKLIST.md` updated (C2 PASS by ruling 0030 item 2; C12 PASS; C3, C7 FAIL on record;
C5, C6, C10, C11, C13-C18 OPEN). Lacks, and whether it can go to review: `stage/G2/OPEN.md`.

# Part F. Batch 15 (lead of batch 15, 2026-11-24 evening): the fresh G2 verifier and the quarter pair

Package reviewed: `stage/G2/verifier/` (fresh verifier of SCOPE 4c, batch 14, report
`stage/G2/VERIFIER.md`), and the quarter-amplitude analysis E-20261124-233223-51b52c0 left by the
lead of batch 13. Ruling 0036 item 2 applies (U-A4'(a) stays FAILED as written; the three-amplitude
reading stands beside it, labelled as after the data).

## F1. Checked by the lead from the artefacts

- Quarter pair: reran `g2prod/scripts/judge_q.py` (registered E-20261125-033357-a608cda; figure
  fix and rerun E-20261125-033450-4c4a31c) on the g2q summary of E-20261124-233223-51b52c0 with
  judge_g2's floor code unchanged, prediction written first (g2prod/JOURNAL.md 4.0). Every number
  the verifier quotes (VERIFIER.md 3.2, 3.4) is reproduced by the package's own reader to its
  digits: M factor 4.1275 (verifier 4.127), common mode -2.0725e-6 (-2.07e-6), U-A0 1.61e-9,
  U-A1 2.52e-6, U-A3 0.99809-1.00042, records 1.19e-12 / 0.0251, even/odd 6.3337e-5 (6.334e-5).
  Two readers that share no code agree. Figure fig_g2_quarter.png looked at (the first version's
  common-mode panel was useless: fixed). Outcome: Q-a REFUTED, Q-b and Q-c hold (entry 4.1).
- The verifier's table (VERIFIER.md 2) against the package: each package number it cites is the
  one in judge_g2.json of E-20261123-024359-5dc3213 (checked for U-A0, U-A1, U-A2' A/B, U-A3,
  U-A4'(a) H range and M miss, U-A4'(c), U-A4'(d), U-R (i)-(iii), U-S, common mode; the ledger of
  the note reads them from that json and stops if a verifier string is not on its line: R11-R16).
- The three-amplitude reading: its numbers come only from the verifier's run
  E-20261125-023427-6fb6400 (floor3.json, checksum verified by the note's figure script); the lead
  did not recompute D1, D2 from the fields. Plotted beside the fixed-level factors (note Fig. 15):
  every judged cross lies within 4 +- 0.005, the one square at cN 6.52 outside the band. The
  derivation of the correlation -4/17 for independent per-run parts of equal size is checked by
  hand (var D = 17 sigma^2, cov = -4 sigma^2) [VERIFIED].

## F2. The verifier's findings and what the track does

| Finding (VERIFIER.md) | Verdict | What the track does |
|---|---|---|
| All recomputed SCOPE 4c numbers CONFIRMED; U-A4'(a) failure confirmed | CONFIRMED | CHECKLIST C3, C7 stay FAIL, C18 PASS citing VERIFIER.md |
| Q-a refuted by the quarter pair (3.2) | CONFIRMED by the package's reader (entry 4.1) | no s^4 cause named; entry 4 |
| Floor estimator of 4c ill-conditioned (3.3, weak point 1) | reading after the data, numbers from the verifier's run only | stands beside the failure (entry 4.2, note Sec. IV C); proposal of a three-amplitude floor for later gates to orch (outbox) |
| U-R (i) measures the third-order flat part (weak point 2) | agrees with note Fig. 14 (ratio 0.992 below |n| ~ 25, 2.91 above 40) | stated in the note (Sec. IV B); proposal of a U-R clause on the discretisation part for later gates (outbox) |
| CHECKLIST cited a missing entry 4 (weak point 3) | right | entry 4 written; C3, C5, C7 point to it |
| Judge's readings of U-A4'(c) (control counted out) and (d) (two control readings) | right, both stated in the package | stated in the note (Sec. IV D) and here; no change of verdict |
| The 4c remark "M record doubles at s = 1/2" not borne out at 256^3 | right (already marked in entry 2.3) | no change |
| Not checked: mode file at N* against Bunch-Davies; window scan on the scouting build; U-R (i) at 320^3 without a half pair; nature of F_s; no processor rerun of a card run | open | listed in stage/G2/OPEN.md |

## F3. Stage package G2 after this review

Every CHECKLIST item is PASS, NA by ruling, or FAIL on record with its ruling (C3, C7: ruling 0030
item 2 and 0036 item 2). Products added this session: g2prod entry 4, g2prod/README.md (rerun
recipe, results), note Sec. IV and Appendix F with six figures and ledger Table XVI (R16
E-20261125-035757-340bd1e). The package goes to independent review (decision 0016 item 4).

# Part G. Batch 17 (lead of batch 17, 2026-11-25 early morning): after the signed G2

Gate G2 is SIGNED, pass with reservations (coord/GATES.md 2026-11-24, tag
`stage/E-stoch-inf/G2-pass-20261124`; decision 0038). No helper package finished since Part F; this
part records what the lead did on the review's findings and on the floor test, from the artefacts.

## G1. The gate review's findings (stage/G2/GATE_REVIEW.md section 5)

| Finding | What the track did |
|---|---|
| F1 floor equation without 1/3 and max | note eq. (floor) corrected to f^2 = max[0, (4 o(1/2)^2 - o(1)^2)/3]; the judged numbers always used this form (judge_g2.py, verifier); g2prod JOURNAL 4.2 line 275 keeps its loose wording on record, corrected by this line |
| F2 stale STAGE_REPORT texts | Verdict line (no G2-fail tag exists; gate signed), Figures table (the G2 figures of repro/note, gate items), Decision section replaced |
| F3 fig_ladder box 1 lists +-1/4 | box 1 now +-1, +-1/2; box 1 of rung 2 says +-1/4 was added after the halving; caption likewise |
| F4 ledger rows without estimator | the two rows name the pooled estimator sigma^2 = [rms(D1)^2 + rms(D2)^2]/34 (floor3.py lines 37-39, read by the lead) and quote the review's D1-only values 3.99924 and 7.6e-4 |
| F5 provenance of the ablation executable | the file that ran is kept at scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu; the lead hashed it: 468109496c82..., equal to the seven manifests; core asked to confirm (outbox 20261125T120431Z), orch asked for a harness pointer |
| F6 duplicated rows of U256qp | core's open restart defect; readers keep the last line per cycle (runs.py); nothing to change |
| F7 the reviewer's own failed run | on the reviewer's record |

Registered note rerun R17 E-20261125-115608-b9c1b59 (repro/note/JOURNAL.md entries 27-28).

## G2. Floor test FL128h (risk R28), checked by the lead from the dumps

The first reading with the recipe of floor entry 1 gave P_NR/P_lin = 4 on every shell; the control F3
refuted it, and the cause was found on the files (the .modes record of an s = 1/2 run carries the
factor; R32). The corrected reading E-20261125-115344-a22128b: R = 1.90 and 2.00, signs kept, F3 0.97;
figure fig_floor.png looked at: the s = 1/2 curve lies on the s = 1 curve divided by 2 on all ten
shells. CONFIRMED at 128 (second order); NOT YET at 256 (q0038, job 5284 submitted during this session).

## G3. G3 scope and pilot

SCOPE 4d committed (cbe20398) and pushed before the first G3 submission (q0045, added after the push).
Power estimate and the 128-band reference are registered runs with predictions written first; two
of the power predictions (W2, W3) failed and are on record (g3/JOURNAL.md entry 1).

# Part H. Batch 19 (lead of batch 19, 2026-11-25 morning): the review of the G3 scope, FL256h

Packages finished since Part G: `g3/scope_review` (batch 18 helper, independent review of SCOPE 4d;
verdict "change B1-B3 first"). Card run finished: FL256h (q0038). Ruling: decision 0040 item 1.
Checks are the lead's own, from the artefacts, in `g3/amend/` (README, JOURNAL entries 1-5).

## H.1 g3/scope_review: what the lead confirmed, could not confirm, and found wrong

| Finding | Lead's check | Verdict | What the track does |
|---|---|---|---|
| B1 top bin of the lattice factor | own code (`g3/amend/bins_lead.py`, own vector count and bins, nothing shared with `ref_bins.py`), run E-20261125-151230-a4f4059, `fig_bins_lead.png` looked at: variant/lattice 0.97786 (32) and 0.99058 (64) as binned, 1.00002 and 0.99991 fixed; top factor 0.2789 vs 0.9338, 0.1656 vs 0.9922; share 3.38 and 1.13 per cent | CONFIRMED to every digit the review quoted | ref_spec.py fixed (d5a5f2f3c); pilot rerun E-20261125-151340-743c38c passes the new variance gate (0.9993 +- 0.0032), other variants bit-identical; SCOPE A1 |
| B2 variance and tail mixed at fixed nu sigma_lin | own arithmetic (`b2_lead.py`), run E-20261125-151429-83a040c: 9.849, 16.90; 3.94 per cent at S = 256 and 4e6, i.e. 0.40 per cent in sigma, 0.0090 in skewness; skewness 0.0231 moves F(3) by 10.1 per cent | CONFIRMED (a few per cent below the review's thresholds through my reference F(3) of 1.5e-3) | SCOPE A2: (V) and (T) judged apart, r(nu) reported only |
| B3 reader tests cannot fail; sign | from `ladder_lib.py` line 180 and the definition in 4d.1: R^NR = -psi + (H/Pi) dphi, zeta = psi + Delta N_bg = -R^NR at first order | CONFIRMED (test (a) cannot fail, test (b) has the wrong sign) | SCOPE A3: Z0-Z2 on processors; entry-2 predictions G3-T "for both variables" superseded (g3/JOURNAL entry 4) |
| B3 bullet 3 and S1: the non-Gaussianity of zeta comes from the shared map | smoke run of the reference with the state at N_f, E-20261125-152619-d917a14: phi at N_f has skewness 0.023 (+- about 0.02 at 2e4), the first-passage value | first read as contradicted by the 2e4 smoke run; the 4e6 run E-20261125-152832-c301e92 settles it: phi at N_f has skewness 0.0007 +- 0.0012 against 0.020 for delta N. CONFIRMED; my smoke-run reading was noise (g3/amend entry 6) | SCOPE A4 implemented: it tests the NR evolution at +-0.0012 in skewness, separately from the shared map |
| S2 mirrored pairs | follows from the definitions | adopted | A5; baseline lists of pairs |
| S3 gauge leg has no lever arm | not rerun (review run E-20261125-131805-0806ef8; ruled by decision 0040) | accepted on the review's run | A8: withdrawn, limitation stated, request to core for a field-dependent lapse (outbox) |
| S4, S5 | wording | adopted | A6, A7 |
| S6, S7 | arithmetic confirmed with B2 (nu = 4: three combined errors 25 per cent at 4e6 direct; the NR error a third of the reference's at 87 and 50 seeds) | CONFIRMED | A9 (sampler target 2 per cent per side), A10 (seeds with reference size) |
| N1 R^NR skewness band | adopted as a prediction band [0, 0.002] | adopted | g3/JOURNAL entry 4 |
| N3 sigma = 0.1 at 4e6 | adopted | adopted | in the 4e6 run |
| N4 s0.01_lin variance 0.9844 of the continuum | the corrected pilot file gives 0.9844 +- 0.0067 (2.3 standard errors low) | NOT CHECKED further | open; the linear-limit variant is not used by any criterion |
| N6 level 2 cost 1.9 | arithmetic | adopted | A11 |
| Owen's T and block estimates of S7, N2 box modes | not rerun | NOT CONFIRMED by the lead | not needed for a criterion; the pilot measures the per-seed scatter on real output (G3P-3) |

Own failed prediction: LB2 (flat-spectrum control) refuted in part (0.99998 instead of 0.996-0.998: the sparse
low shells overcount a flat spectrum by 0.27 per cent and cancel the top-bin deficit at |n| <= 32 by chance).
Failed run on record: E-20261125-152419-40200ec (figure code of ref_spec.py with a variant subset; fixed).

## H.2 FL256h (q0038) and the floor

Finished E-20261125-115534-8414659 (0.44 card-hours). Read by E-20261125-151222-d5a5f2f with the corrected
recipe (record ratio 0.5 checked): ratios 1.997 (median) and 2.000 (amplitude), no sign flip, per-mode rms
2.001; s = 1/2 medians at 128 and 256 0.1 per cent apart. F1 at 256, F2, F4, F5 HOLD (floor/JOURNAL.md
entry 4); the figure shows the s = 1/2 curve on the s = 1 curve divided by 2 on every shell. R28 closed. The
note's three sentences that called the floor open now state the halving (no new number; compiled).

## H.3 Gates

G0, G1, G2 are signed (coord/GATES.md). G3: scope fixed and amended before any production run; no
production run yet; `stage/G3/CHECKLIST.md` collected, `stage/G3/OPEN.md` lists what is open. Not ready for
review.

## I. Batch 20 (2026-11-25 07:54-09:05 PST, lead of E, processors only): the zeta reader and the reference proper

No helper package finished since batch 19; the cards were held all session (q0050-q0054 waiting, none started), so
this part records the lead's own processor work. It is not an independent check: the fresh verifier of G3 must
recompute it (A13). Every number below has its run id; predictions were committed before each registered run
(zeta/JOURNAL.md entries 4-6, g3/amend/JOURNAL.md entries 7-8).

### I.1 zeta reader (zeta/zeta_reader.py; run E-20261125-161456-8d3f43c on the 32^3 pairs E-20261125-153148-cfad424)
- Confirmed: the TO VERIFY of 4d.3. HiggsInflection(1.86e-6, 0.198) at phi0 = -1.2, N* - N0 = 3 mapped to code
  units gives the deck's vev, lambda, phi0, pi0 to 1.1e-14 relative and the landmarks to 1.3e-9 in N (the flat
  eps2 = 0 crossing 4.0e-7); the deck's tlim is N_f to 2e-13. [VERIFIED]
- Confirmed: Z0 = 3.0e-5 (bar 1e-3); Z2(i) ratio 0.999996; Z2(iii') -0.25 per cent (bar 0.5, pre-registered before
  the reading, entry 4); a_zeta = 6.763e-3, a_zeta sigma_lin(128) = 3.3e-3 (predicted [0.002, 0.008]).
- Failed as written: Z2(iii) -2.89 per cent against 2 per cent, predicted (entry 4) from a_zeta = a_map - a_R; Z1
  along Pi alone, second coefficient 0.142 against 1 per cent (floor of the independent integrator by the
  diagnostics; not a named cause: the test that could fail was stopped, E-20261125-161757-fb0eb95).
- A4 preview against the 8-band reference E-20261125-160705-5f75bb4: variance 1.031 (one box scatters 3.1 per
  cent), intrinsic skewness of d phi 7.4e-5 vs 0.0002 +- 0.0020, of zeta 0.0027 vs 0.0026 +- 0.0020. Consistent.
- What the track does: the reader may judge G3 runs only after the orchestrator rules on Z1 along Pi and on Z2(iii)
  (outbox); its cost on 128^3 (R41) is handled before the baseline is read.

### I.2 Reference proper (langevin/)
- Lattice sigma = 0.1 (E-20261125-160722-a6d1f26): TS1 FAILED (variance gate 1.00245 +- 0.00050); TS2 holds as
  worded (skewness difference -0.0017 +- 0.0018) but the A10 bound is not reached; TS3 holds.
- Importance sampler (A9; E-20261125-160658-855db8c): see I.3 (written when the run ended).
- Defects found and fixed: NaN in the biased sampler where the noise vanishes (sdn/langevin.py, before any
  registered run); the constant shift of A9 replaced by a variance-share profile (A14 (a)); the variance gate of
  ref_spec.py loops over the lattice variants that ran (it required s0.01_lattice in every run).
