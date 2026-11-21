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
