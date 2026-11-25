# VERIFIER of G1, F-hills (checklist C18; decisions 0016 item 4, 0042 item 2)

Fresh verifier, batch 22, 2026-11-25 09:38-10:10 PST, processors only, 0 card-hours. Package:
`verifier/` (README, JOURNAL with predictions and outcomes, scripts, results, figures). Every
number below is from the registered run **F-20261125-175533-141e4f1** (`verifier/scripts/run_all.sh`)
unless another run id is given. Horizon numbers are all **made without the diagnostics** (no run of
this track has `<fastflow> diagnostics`); failed searches are found by the source's failure
signature (a non-finite or non-positive mass, or columns 3-12 identical to the previous row).

## 1. What was done, and how independent it is

- Readers written here (`verifier/scripts/vread.py`, `vnewton.py`, `vjunk.py`); the packages'
  readers (`nrread.py`, `b11_*.py`, `b21_*.py`, `binary_conv/scripts/*`) were not used. I read one
  of them only to learn which time windows the owner's H2 used (b21_horizon_recheck.py lines
  146-149) and how its "rms H" is defined (b21_a2_state.py line 192), so that I compute the same
  quantity; the definition of H-norm2 I took from the source (`athenak/src/outputs/history.cpp`
  lines 172-260).
- Each reader was tested on an analytic case first (P0, `results/vtest.json`, `figures/fig_v_tests.png`):
  a Kepler orbit split into five overlapping tracker segments with an injected 1e-6 offset (joined
  exactly, offset found in both overlaps), pericentres to 1e-8, a three-body integration keeping
  energy to 1.05e-10 and angular momentum to 3.4e-12 over 200 M, a synthetic horizon summary with
  restart repeats and three failures (found), waveform times with duplicates, an analytic (2,2) wave
  whose FFI energy is exact to 3.5e-6 (J0). One bound I wrote failed: the Kepler energy is kept to
  3.2e-11, not 1e-11 (harmless).
- Predictions were committed before any reader ran on data (commit 57c7a67dc; for criterion (iii)
  commit 8afb440c8, where I had seen the t = 0 history rows before writing, so K1 is arithmetic, not
  a blind test). By accident I read the owner's journal lines 1060-1075 (the first outcome lines of
  batch 21, S1-S3) while reading its predictions; those numbers are also in b21_a2_state.json,
  which the task gives me as the claim.
- A2's chain resumed at 09:49 PST (Slurm 5294) during this session. The passage is read twice by
  the same code: cut at 96.2285 M, the owner's last record (`results/cut_96.23/`), and to the live
  record (96.89 M in the reference run).

## 2. G1 criteria of the scope text (`../G0/SCOPING.md` section 5) as far as I checked them

| Criterion | What I checked | State |
|---|---|---|
| (i) F-pre-1 reproduces 0911.1136 and 1804.02911; one KHSR result | nothing (not in this package's time) | not checked |
| (ii) F-pre-2 reproduces 2404.16270 | nothing | not checked |
| (iii) t = 0 Hamiltonian residual for approx, none, plain sum; junk at R >= 40 m, two radii within 20 percent | rms H at t = 0 of all seven E2 cases and the card smoke; FFI junk energy at P1's four spheres | reproduced (Sec. 3.4); the radii agree within 19.8 percent, at the edge of the criterion |
| (iv) one complete vacuum passage: all horizons found until a merger, trackers to 200 M, outcome with the constraint norm | P1 (merged at 48.8 M, to 280 M) and P1b (A + A2, to 96.2 M of at least 170 M) | P1: complete, reproduced; P1b: not complete (verified to its last record) |

## 3. Claims, one by one

Digits: "n digits" means my value and the claim agree when both are rounded to n significant
digits.

### 3.1 The Newtonian reference of P1b (deck `binary_conv/inputs/p1b_R16n.athinput`, bare masses, v = p/m)

| Claim (b11_passage.json "newton"; JOURNAL l. 832) | Mine | Verdict |
|---|---|---|
| pair closest 3.67475 M at 87.6 M | 3.674750 M at 87.598 M | reproduced, 7 digits (time to the claim's 0.1-M sampling) |
| comp0-M closest 12.0683 at 95.75 M | 12.068292 at 95.761 M | reproduced, 6 digits |
| comp1-M closest 5.77712 at 122.1 M | 5.777119 at 122.090 M | reproduced, 6 digits |
| fates: m1 (comp0) ejected, m2 bound | same; v_inf of comp0 0.365 relative to M | reproduced |
| energies at 200 M: 1.49387, -1.62560, pair 0.87396 units | the same to 10 digits | reproduced |
| centre of mass passes M at 9.81 M at 104.35 M | three-body: 9.762 M at 104.337 M; two-body conic of the initial centre-of-mass state: r_p = 9.8087 M | time reproduced; the distance 9.81 is the conic pericentre, not the three-body pass (0.047 M apart) |

### 3.2 The passage P1b, A (F-20261121-203144-b2cf16b) + A2 (F-20261124-210400-902c650)

| Claim | Mine (cut at 96.2285 M) | Verdict |
|---|---|---|
| S1: trackers of A + A2 join to 0-96.23 M, no gap | 45 files per tracker (31 A, 14 A2 incl. the copy made at 09:49); 0-96.228515625 M, 49270 times, every step exactly 2^-9 M; the new segment from 96.23 M joins without a gap (live: to 96.89 M) | reproduced |
| S2: overlaps agree to 1.1e-12 (A), 6.2e-14 (A2) | A-A 1.13e-12, A-A2 4.8e-14, A2-A2 6.2e-14 M; A's cut attempts after 61.80 M agree with A2 | reproduced |
| S4: pair closest approach 2.110 M at 76.37 M; A2-1 refuted on timing | 2.109626 M at 76.373 M (refined 2.109626 at 76.3727); the only minimum after 61.8 M; s > 1 M throughout | reproduced, 6 digits; A2-1 fails as written on timing only (its 2.0-2.7 M band holds) |
| S5: centre of mass 13.06 M from M, closing | 13.0626 M (claim 13.0628), d/dt = -0.237 per M; live 12.904 M at 96.89 M, still closing | reproduced, 4 digits (the weights differ in the 5th digit) |
| members 12.05 and 14.16 M from M | 12.053032, 14.159961 | reproduced, all digits |
| members bound to M and to each other (coordinate energies) | pair -0.823, comp0-M -0.362, comp1-M -0.161 units (claim -0.823, -0.363, -0.162); pair bound throughout after 61.8 M (max -0.807) | reproduced, 2-3 digits; coordinate quantities (R6) |
| S6: no failed search in A2; medians 0.12944, 0.12940, 1.00385 | 0 failures in 1102 times per finder; medians equal to all digits | reproduced |
| S6: member drift 3.1e-5 and -8.1e-6 per M (65-95 M) | 3.091e-5 and -8.055e-6 per M **as a fraction of the mass**; in absolute mass 4.0e-6 and -1.0e-6 per M | reproduced; the unit "per M" means fraction per M (the label should say so) |
| S6: heavy-hole change 6.9e-4 | max - min 6.887e-4 | reproduced, but see finding F1 |
| S6: rms H below 1e-4, max 3.13e-5 | sqrt(H-norm2/Volume) max 3.126e-5 at 84.5 M; H-norm2 0.0795 (62 M) to 0.102 (96 M) | reproduced, 4 digits |
| S3: waveforms of A2: 137 samples 62-96 M from 160 raw rows | 137 samples, none missing on the 0.25-M grid, 160 raw rows (first pass F-20261125-175038-4719d4a) | reproduced |
| A's waveforms 0-61.8 M | A's files hold 257 samples 0-64 M: A's cut attempts wrote 62-64 M, equal to A2's nine samples there to 1.4e-12; joined A + A2: 385 samples 0-96 M, none missing | reproduced; my own prediction (248 to 61.75 M) failed as written |

### 3.3 Mesh members and P1 (`binary_conv`, khsr_note/results/p1_280.json, H1-H4)

| Claim | Mine | Verdict |
|---|---|---|
| binary alone, s(7.5 M): m/8 4.8863, m/16 4.9477; P1 4.8539 | 4.88625, 4.94769, 4.85393 | reproduced, 5 digits |
| s(20 M): P1 4.2855, alone m/8 4.3753 | 4.28549, 4.37531 | reproduced, 5 digits |
| Newton, binary alone: 4.9430 (7.5 M), 4.9693 (20 M) | 4.94300, 4.96926 | reproduced, 5 digits |
| EIH 4.9478 (7.5 M), 4.9302 (20 M) | no EIH integrator of my own | not checked |
| order of the separation error m/8 to m/16 >= 3.3 (3.96 from Delta s) | with m/12 (R12) the three members give no order: s12 - s16 = +7.7e-6 at 7.5 M, -4.4e-4 at 10 M (sign change) while s8 - s16 = -0.061 to -0.38; the three-member order is undefined at 5, 7.5, 10, 20 M | not reproduced: the statement was made from two members before R12 existed; m/12 and m/16 agree within 2.1e-3 M, m/8 is outside the convergent regime |
| R12 = R16n within 0.002 M | largest 2.12e-3 M at 0.71 M, -3.4e-4 M at 21.06 M | reproduced after the first M; marginally exceeded in the start transient |
| C (P1b m/12) vs A within 0.0023 M to 22 M | largest 2.33e-3 M at 0.59 M, 2.08e-3 at 22.3 M | reproduced, 2 digits |
| P1 merger: tracker separation < 0.1 M at 48.79 M | 48.793 M | reproduced |
| H3: finder 0 first above 0.2 at 48.81 M (0.2686), finder 1 at 49.06 M (0.2693) | 48.8125 M (0.26857), 49.0625 M (0.26930) | reproduced, 4 digits |
| remnant passes M at 6.99 M at 154.6 M | 6.991681 M at 154.598 M | reproduced, all digits |
| p1_280.json d_at_112 = 11.816 | 11.895 at 112.0 M (its rows at 120-280 M equal mine to 10 digits) | not reproduced; my value of 11.816 occurs near 112.4 M |
| P1 rms H 4.7e-5 to 8.8e-5 over 60-280 M | 4.66e-5 to 8.79e-5 | reproduced, 2 digits |
| remnant mass -0.42 percent over 60-280 M | -0.43 percent (medians of all accepted rows; p1_280's medians keep only its "good" rows and sit about 9e-4 higher) | reproduced, 1-2 digits |
| heavy hole +0.32 percent (P1) | +0.24 percent from the 1-20 M median, +0.018 percent from 20-60 M | not checkable: the baseline of +0.32 percent is not stated where I read it |
| H1: failures < 1 percent at m/16 and m/12 before 96 M | 0 in R12, R16n+B, A+A2, C; P1 4, 5, 18 and R8 2, 2 (m/8, no number claimed) | reproduced |
| H2 as written: m/8 members 1.0-1.7e-3 per M | P1 (10-40 M) 1.12e-3, 1.65e-3; R8 (10-21 M) 0.92e-3, 1.43e-3 | failed as written (R8 member 0 below 1.0e-3); the corrected band 0.9-1.7e-3 (OPEN item 5) holds |
| H2: m/16 members below 1e-4 per M | at most 3.1e-5 (R16n+B 23-60, 60-108 M; A 15-40, 40-62 M; A2 65-95 M) | reproduced |
| H2: C's members 1.22e-4, 1.71e-4 per M | -1.20e-4, -1.69e-4 (15-22.3 M; the masses fall) | reproduced, 2 digits (magnitudes) |
| H2: all rows vs accepted rows within 10 percent | equal to 3 digits in every window | reproduced |
| H4 as written: heavy hole within 1 percent of its median in P1, A, A2, C | P1's first three searches 0.9961, 0.9915, 0.9844 (t <= 0.125 M), 2.3 percent below its median 1.0071; within 0.70 percent after 1 M; A, A2, C within 0.05 percent; no member finder above 0.5 | failed as written for P1's first 0.125 M; holds after 1 M (OPEN item 5's wording) |

### 3.4 Criterion (iii): the three-puncture data at t = 0 and their junk

| Claim (`junk_gauge/README.md` T3 text) | Mine | Verdict |
|---|---|---|
| t = 0 rms H at m/8 4.7e-5; card 4.713e-5 (E2 F-20261115-173547-a02af7d; smoke F-20261115-174602-c6879fe) | 4.7134e-5 (approx L10); the card history row gives the same to its 6 digits | reproduced |
| truncation order 7.6-8 | L9 -> L10: 7.98 (approx), 7.91 (none); L10 -> L11: 6.42 (approx), 1.62 (none, at its own residual) | reproduced for L9 -> L10 |
| own residual of the corrected data 4.9e-7 = 1/33 of the uncorrected | raw rms at m/16: approx 5.51e-7, none 1.633e-5, ratio 29.6 | not reproduced as raw numbers (the claim seems to remove truncation; its method is not in what I read); the substance (the correction lowers the m/16 residual about thirtyfold) holds |
| plain sum vs approx at m/8 | plain/approx = 0.999 (truncation-dominated at m/8) | measured; no claim to compare |
| junk at r = 40, 48, 70, 90 M in u in [-35, 6] M: 2.8, 2.6, 2.5, 2.5e-6 M | 2.73, 2.50, 2.28, 2.36e-6 M (FFI omega_0 = 0.2, u = t - r*, M_adm = 1.25, record cut at u = 14) | reproduced within 3-9 percent; largest/smallest 1.198 |
| 1.5-3.9e-6 over integration choices | omega_0 = 0.1: 3.3-4.2e-6; 0.3: 1.7-2.1e-6; u = t - r: 1.7-2.4e-6 | reproduced in range (my omega_0 = 0.1 reaches 4.2e-6 at 40 M) |
| 67-70 percent in l >= 4, flat in l | 69-71 percent; E_l flat from l = 2 to 8 (fig_v_junk) | reproduced |

## 4. Predictions that failed as written (owner's and mine)

- A2-1 (batch 11): minimum 2.0-2.7 M at 63-75 M. The minimum, 2.110 M, came at 76.37 M: failed on
  timing; the band held.
- H2 (batch 21) in part: R8's member 0 drifts 0.92e-3 per M, below the written band 1.0-1.7e-3.
- H4 (batch 21): P1's heavy finder is 2.3 percent below its median in its first three searches.
- Mine: P0(c) one bound (Kepler energy 3.2e-11 against 1e-11); P1 the centre-of-mass distance 9.81
  (three-body 9.762); P7 A's waveform count (257 to 64 M, not 248 to 61.75 M); P8 the order of
  convergence (none exists with the three members). Each is in `verifier/JOURNAL.md` entry 2.

## 5. Findings the claims do not state

- F1 (A2's heavy hole, fig_v_horizons). The heavy hole's horizon mass falls smoothly from 1.00401
  (63 M) to 1.00358 (86 M), -1.72e-5 per M; from 86.6 M the finder alternates between an upper branch
  (median 1.00422, near A's early value) and a lower branch that keeps falling (1.00379 to 1.00354,
  -1.25e-5 per M). The fit -2.7e-6 per M over 65-95 M averages the two branches and hides the trend.
  A2-5's clause "the heavy hole changes by less than 1e-3 to 200 M" is at risk: on the lower branch's
  slope the change passes 1e-3 near 120-125 M [JUDGEMENT: an extrapolation; which branch is the
  better surface I cannot tell without the finder's diagnostics]. An apparent-horizon mass that falls
  by 4e-4 while two holes approach is more likely numerical than physical [JUDGEMENT].
- F2 (convergence). The two-member order ">= 3.3" should not be quoted: with R12 the separation of
  the binary alone shows m/12 and m/16 agreeing within 2e-3 M with a sign change of their difference,
  so the m/8 member is far outside any asymptotic regime. What the data support: "m/12 and m/16 agree
  within 2.1e-3 M to 21 M; m/8 differs by 0.06-0.38 M".
- F3 (wording). "Per M" drifts in the S6/H2 numbers are fractions of the mass per M; "Newton 9.81 M"
  is the two-body conic, the three-body pass is 9.762 M; p1_280.json's d_at_112 is not the value at
  112.0 M.
- F4 (junk). The four radii agree within 19.8 percent: criterion (iii)'s 20 percent is met at its
  edge, and most of the window's energy is the steady flat-in-l flux after the pulse at u = -33 M,
  not the pulse (OPEN item 4 says as much).

## 6. Not checked (plainly)

F-pre-1 (newton3, criterion (i)) and the KHSR result (khsr_note K3); F-pre-2 (geodesic_binary,
kerr, criterion (ii)); the eih package (EIH separations, 1PN scans); the note v2 ledger tables; the
batch-11 card analysis beyond the quantities above (N1/N1m tide, F-20261124-132934-375a163); P1's
remnant spin, "recoil" and radiated energy; the single-member junk (S2g) and its scaling; the junk at
P1b's spheres. None of these was read with a reader of mine.

## 7. Running the readers on the completed passage

`verifier/scripts/run_all.sh` (README "How to rerun") reads every kept tracker copy and the live
file, the horizon summaries, the history and the waveforms to their last record, and integrates
Newton to max(200 M, last NR time); it writes the passage twice (to the last record and, for this
report's comparison, cut at 96.2285 M). On the completed passage: A2-2 is read from
`vpassage.json` `state_at_end.d_cm_minima` (the centre of mass's closest approach and time) against
95-115 M and 8-11 M; A2-3 from `d0`, `d1`, `E_0M_units`, `E_1M_units` at the end and the Newtonian
fates; A2-4 from the member and heavy horizon blocks (no member mass above 0.5, no common horizon);
A2-5 from `horizon_A2_*` and `heavy_A2_branches` (F1). A continuation into a new run directory is
added after A2 in `vpassage.py` (`RUN_A2`) and `vmesh.py` (`RUNS["A"]`).

## 8. Requests

- To the lead (F-hills): (a) relabel the member drifts as fractions per M; (b) replace "order >=
  3.3" by the three-member statement of F2; (c) quote the Newtonian centre-of-mass pass as 9.76 M at
  104.3 M (three-body), or say "conic 9.81 M"; (d) check p1_280.json's d_at_112; (e) look at the
  heavy hole's two branches in A2 (F1) before judging A2-5, and state which branch a number uses;
  (f) state the baseline of P1's "heavy hole +0.32 percent" and the method behind "own residual 4.9e-7".
- To core: nothing new; the open request on the finder's diagnostics after a restart (decision 0042
  item 4) would let F1 be judged.

## 9. Comparison with the lead's verdicts (written after sections 1-8 were committed, 05e52ce51)

Read for this section only: `CHECKLIST.md` (C6-C8, C18), `../REVIEW-wave3.md` (binary_conv,
khsr_note, card chains, batch 21), the owner's JOURNAL.md batch 21 outcomes (lines 1060-1120).

| Lead's verdict | Mine | Agreement |
|---|---|---|
| S1, S2, S3 MET (join complete, overlaps <= 1.1e-12, 137/137 samples) | same numbers from my readers | agree |
| S4 = A2-1 REFUTED on timing (2.110 M at 76.37 M) | same | agree |
| S5 MET (13.06 M, closing at 0.237 M per M; A2-2 open) | same | agree |
| S6 MET to 96.23 M (drifts 3.1e-5, -8.1e-6 per M, heavy range 6.9e-4, rms H 3.1e-5) | same numbers; but the heavy hole's range hides a smooth decline (-1.7e-5 per M, 63-86 M) and a two-branch finder from 86.6 M (F1) | agree on the numbers; I add F1, which puts A2-5's "heavy hole < 1e-3 to 200 M" at risk |
| H1 MET; at m/8 P1 0.09-0.4 percent, R8 0.6 percent | P1 4, 5, 18 of 4480 (0.09-0.40 percent), R8 2 of 336 (0.6 percent) | agree |
| H2 REFUTED IN PART (R8 0.92e-3; C 1.71e-4 above 1.7e-4 by rounding) | R8 0.92e-3 agree; C 1.20e-4, 1.69e-4 over 15-22.3 M against the lead's 1.22e-4, 1.71e-4 over 15-22 M | agree on R8; C's "above the band" depends on the window's end (0.3 M) and is not robust either way |
| H3 MET | same to all digits | agree |
| H4 REFUTED as written for P1 only (0.984 in the first three searches; 0.70 percent after 1 M; A + A2 5.0e-4, C 1.2e-4) | same | agree |
| C7 PASS with reservations (junk window 2.3-2.8e-6 M, burst then steady 5.0-5.4e-8 M per M) | 2.28-2.73e-6 M at the four radii; the steady part visible in fig_v_junk | agree; I add that the four radii agree within 19.8 percent, at the edge of criterion (iii)'s 20 percent |
| C8 FAIL (NOT MET, PARTIAL): P1 merged; P1b to 96.23 M needs A2 to at least 170 M | same: P1b not complete; the join and the state to 96.23 M (and to 96.89 M live) reproduced | agree |
| binary_conv (batch 4a): order ">= 3.3" not established; "only the three-point (R12) or later R16n data decide the order" | R12 now decides it: no order exists (s12 - s16 changes sign; m/8 outside the asymptotic regime) | agree, and the open question is closed in the negative (F2) |
| binary_conv (batch 4a): fractional drifts labelled "per M" | the S6/H2 "per M" numbers are fractional too | agree; the wording is still in the batch-21 numbers (F3) |
| khsr_note: P1 to 280 M "not rechecked, to the G1 verifier" | merger, remnant pass, rms H range, remnant mass change reproduced; d_at_112 not reproduced; heavy "+0.32 percent" not checkable | partly done; one defect found |
| khsr_note: K3 "a second agent's check ... is part of the G1 verifier" | not done | open |
| C6 PASS (F-pre-1, F-pre-2) | not checked by me | no opinion |
| C18 OPEN: "every number of the Supplemental Material recomputed from the manifests" | the note v2 ledger was not recomputed; the passage, Newton, mesh, horizon and junk numbers above were | C18 is met for the material of sections 3.1-3.4 only; the note's ledger, K3, F-pre-1/2 and eih remain for a verifier |

Where the lead's text should change (my requests a-f of section 8): F1 (heavy-hole branches, before
judging A2-5), F2 (no order of convergence; quote the m/12-m/16 agreement instead), F3 (fractional
"per M"; the conic 9.81 M; p1_280's d_at_112), the baseline of "+0.32 percent" and the method of
"own residual 4.9e-7".
