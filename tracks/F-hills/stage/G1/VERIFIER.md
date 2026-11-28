# VERIFIER of G1, F-hills (checklist C18; decisions 0016 item 4, 0042 item 2)

Fresh verifier, batch 22, 2026-11-25 09:38-10:10 PST, processors only, 0 card-hours. Package:
`verifier/` (README, JOURNAL with predictions and outcomes, scripts, results, figures). Every
number below is from the registered run **F-20261125-175931-32701e4** (`verifier/scripts/run_all.sh`;
Sec. 3.5 from F-20261125-180244-25c98a5, `verifier/scripts/vkhsr.py`;
its passage numbers at the cut equal those of the earlier passes F-20261125-175038-4719d4a,
-175132-e7c6c68, -175235-e0fdde6, -175533-141e4f1, which it supersedes) unless another run id is given. Horizon numbers are all **made without the diagnostics** (no run of
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
  commit 8afb440c8; for KHSR commit of entry 4 before its run; entry 3's ledger predictions were
  written into the journal before the reader ran and committed with its code, where I had seen the t = 0 history rows before writing, so K1 is arithmetic, not
  a blind test). By accident I read the owner's journal lines 1060-1075 (the first outcome lines of
  batch 21, S1-S3) while reading its predictions; those numbers are also in b21_a2_state.json,
  which the task gives me as the claim.
- A2's chain resumed at 09:49 PST (Slurm 5294) during this session. The passage is read twice by
  the same code: cut at 96.2285 M, the owner's last record (`results/cut_96.23/`), and to the live
  record (97.33 M in the reference run).

## 2. G1 criteria of the scope text (`../G0/SCOPING.md` section 5) as far as I checked them

| Criterion | What I checked | State |
|---|---|---|
| (i) F-pre-1 reproduces 0911.1136 and 1804.02911; one KHSR result | the KHSR result (khsr_note K3) at four points with my own three-body integrator (Sec. 3.5); not 0911.1136 or 1804.02911 | KHSR part reproduced; the rest not checked |
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
| order of the separation error m/8 to m/16 >= 3.3 (3.96 from Delta s) | with m/12 (R12): s12 - s16 = +7.7e-6 at 7.5 M, -4.4e-4 at 10 M (sign change) while s8 - s16 = -0.061 to -0.38; three-member order undefined at 5 and 7.5 M, 13.4, 12.0, 14.5 at 10, 15, 20 M | not reproduced as an asymptotic order: the statement was made from two members before R12 existed; m/12 and m/16 agree within 2.1e-3 M, m/8 is outside the convergent regime |
| note ledger row 194: three-member order 12, 14.5 at 15, 20 M | 11.98, 14.46 | reproduced as numbers, 2-3 digits; an "order" of 12-14 for fourth-order differences is not asymptotic (F2) |
| R12 = R16n within 0.002 M | largest 2.12e-3 M at 0.71 M, -3.4e-4 M at 21.06 M | reproduced after the first M; marginally exceeded in the start transient |
| C (P1b m/12) vs A within 0.0023 M to 22 M | largest 2.33e-3 M at 0.59 M, 2.08e-3 at 22.3 M | reproduced, 2 digits |
| P1 merger: tracker separation < 0.1 M at 48.79 M | 48.793 M | reproduced |
| H3: finder 0 first above 0.2 at 48.81 M (0.2686), finder 1 at 49.06 M (0.2693) | 48.8125 M (0.26857), 49.0625 M (0.26930) | reproduced, 4 digits |
| remnant passes M at 6.99 M at 154.6 M | 6.991681 M at 154.598 M | reproduced, all digits |
| p1_280.json d_at_112 = 11.816 | 11.895 at 112.0 M (its rows at 120-280 M equal mine to 10 digits) | not reproduced; my value of 11.816 occurs near 112.4 M |
| ledger row 200: common horizon 24.9 M from the heavy hole | 24.879 M (tracker 0 to M at 48.8125 M) | reproduced, 3 digits |
| ledger row 201: remnant 24.25 M from M at 280 M, rate 0.158 | 24.2502 M; rate 0.159 (fit over 275-280 M) | reproduced, 4 and 2 digits |
| P1 rms H 4.7e-5 to 8.8e-5 over 60-280 M; ledger row 207: 3.2e-4 at 1 M, 6e-5 at 112 M, 8.8e-5 largest over 112-280 M, 4.7e-5 at 280 M | 4.66e-5 to 8.79e-5; 3.17e-4, 6.02e-5, 8.79e-5, 4.66e-5 | reproduced, 2 digits |
| remnant mass -0.42 percent over 60-280 M; ledger row 203: medians 0.2683, 0.2672 | -0.43 percent; medians 0.26743, 0.26628 (all accepted rows; p1_280 keeps only its "good" rows, about 9e-4 higher) | change reproduced, 1-2 digits; medians differ in the third digit by the row selection |
| heavy hole +0.32 percent (P1); ledger row 205: 1.00419 at t = 4 M, median 1.00736 over 240-280 M | 1.004190 at 4.0 M (accepted search), 1.007359; ratio +0.316 percent | reproduced, 2 digits (the baseline is the search at 4 M) |
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
| truncation order 7.6-8; ledger row 126: 7.98, 7.68 (corrected), 7.96, 7.62 (uncorrected) | raw-norm orders L9 -> L10: 7.98 (approx), 7.91 (none); L10 -> L11: 6.42, 1.62 | the ledger measures the truncation error against a closed form (note Sec. on the data), which the history does not hold: 7.98 reproduced, the others not checkable from the history |
| ledger row 122: rms H at t = 0, corrected: 0.0119, 4.71e-5, 5.51e-7 (m/4, m/8, m/16) | 0.011906, 4.7134e-5, 5.5141e-7 | reproduced, 3 digits |
| own residual of the corrected data 4.9e-7 = 1/33 of the uncorrected (junk_gauge README) | raw rms at m/16: approx 5.51e-7 (= ledger row 122), none 1.633e-5, ratio 29.6 | not reproduced as raw numbers (4.9e-7 is not the ledger's raw 5.51e-7; its method is not in what I read); the substance (the correction lowers the m/16 residual about thirtyfold) holds |
| plain sum vs approx at m/8 | plain/approx = 0.999 (truncation-dominated at m/8) | measured; no claim to compare |
| junk at r = 40, 48, 70, 90 M in u in [-35, 6] M: 2.8, 2.6, 2.5, 2.5e-6 M | 2.73, 2.50, 2.28, 2.36e-6 M (FFI omega_0 = 0.2, u = t - r*, M_adm = 1.25, record cut at u = 14) | reproduced within 3-9 percent; largest/smallest 1.198 |
| 1.5-3.9e-6 over integration choices | omega_0 = 0.1: 3.3-4.2e-6; 0.3: 1.7-2.1e-6; u = t - r: 1.7-2.4e-6 | reproduced in range (my omega_0 = 0.1 reaches 4.2e-6 at 40 M) |
| 67-70 percent in l >= 4, flat in l | 69-71 percent; E_l flat from l = 2 to 8 (fig_v_junk) | reproduced |

### 3.5 KHSR K3 (khsr_note, scan F-20261121-212757-77cdc15), run F-20261125-180244-25c98a5

My three-body integrator (vnewton.rhs, DOP853, rtol 1e-11), KHSR's set-up as khsr_note states it
(M/m = 1e6, m1/m2 = 3, circular prograde coplanar binary, start 10 r_t, stop at 30 r_t outbound),
256 phases per point against the scan's 512; sigma is the binomial error of my sample.

| point | claim P1, P2, Pdis, both bound | mine | verdict |
|---|---|---|---|
| D = 0.5, parabola | 0.485, 0.485, 0.971, 0 | 0.484, 0.484, 0.969, 0 | reproduced (0.2 sigma) |
| D = 0.5, r_a = 100 r_t | 0.068, 0.484, 0.973, 0.420 | 0.070, 0.488, 0.977, 0.418 | reproduced (0.4 sigma) |
| D = 1, parabola | 0.459, 0.459, 0.918, 0 | 0.457, 0.457, 0.914, 0 | reproduced (0.2 sigma) |
| D = 1, r_a = 100 r_t | 0.070, 0.457, 0.922, 0.395 | 0.070, 0.453, 0.922, 0.398 | reproduced (0.1 sigma) |
| ledger row 60: P1/P2 at r_a = 100 r_t, D = 0.5, 1 | 0.141, 0.154 | 0.144, 0.155 | reproduced, 2 digits |

So the KHSR statements "the ejection probability falls to a little more than half of the disruption
probability at r_a = 100 r_t" (0.55 of 0.97; 0.52 of 0.92) and "the primary escapes six to eight
times less often than the secondary" hold at these two penetration factors.

## 4. Predictions that failed as written (owner's and mine)

- A2-1 (batch 11): minimum 2.0-2.7 M at 63-75 M. The minimum, 2.110 M, came at 76.37 M: failed on
  timing; the band held.
- H2 (batch 21) in part: R8's member 0 drifts 0.92e-3 per M, below the written band 1.0-1.7e-3.
- H4 (batch 21): P1's heavy finder is 2.3 percent below its median in its first three searches.
- Mine: P0(c) one bound (Kepler energy 3.2e-11 against 1e-11); P1 the centre-of-mass distance 9.81
  (three-body 9.762); P7 A's waveform count (257 to 64 M, not 248 to 61.75 M); P8 the order of
  convergence (I predicted 2-5; there is none at 5 and 7.5 M and 12-14.5 at 10-20 M). Each is in
  `verifier/JOURNAL.md` entries 2 and 3.

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
  within 2.1e-3 M to 21 M; m/8 differs by 0.06-0.38 M". The ledger's row 194 (orders 12 and 14.5 at
  15 and 20 M) is reproduced as arithmetic (11.98, 14.46; 13.4 at 10 M; none at 5 and 7.5 M), and
  orders that large and that scattered are themselves the sign that the members are not asymptotic.
- F3 (wording). "Per M" drifts in the S6/H2 numbers are fractions of the mass per M; "Newton 9.81 M"
  is the two-body conic, the three-body pass is 9.762 M; p1_280.json's d_at_112 is not the value at
  112.0 M.
- F4 (junk). The four radii agree within 19.8 percent: criterion (iii)'s 20 percent is met at its
  edge, and most of the window's energy is the steady flat-in-l flux after the pulse at u = -33 M,
  not the pulse (OPEN item 4 says as much).

## 6. Not checked (plainly)

F-pre-1 (newton3, criterion (i): 0911.1136, 1804.02911) and KHSR beyond the four points of Sec. 3.5
(retrograde, r_a = 500, 200, 130, the parabolic approximation K3c/K3d); F-pre-2 (geodesic_binary,
kerr, criterion (ii)); the eih package (EIH separations, 1PN scans); the note v2 ledger tables except
rows 122, 126 (in part), 128, 168, 194, 200, 201, 203, 205, 207 (checked in sections 3.3 and 3.4; row
168, the conic 9.809 and e = 1.00023, is my 9.8087 and 1.000235); P1's remnant spin (row 204),
radiated energy (row 208) and "recoil"; the
batch-11 card analysis beyond the quantities above (N1/N1m tide, F-20261124-132934-375a163); the
single-member junk (S2g) and its scaling; the junk at
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
  (f) state the method behind "own residual 4.9e-7" (junk_gauge README; the ledger's raw value is
  5.51e-7) and that "+0.32 percent" is measured from the search at 4 M.
- To core: nothing new; the open request on the finder's diagnostics after a restart (decision 0042
  item 4) would let F1 be judged.

## 9. Comparison with the lead's verdicts (written after sections 1-8 were committed, 05e52ce51)

(Sections 3.3-3.5 gained the ledger rows and the KHSR check after this section was first written;
their rows here were updated with them.) Read for this section only: `CHECKLIST.md` (C6-C8, C18), `../REVIEW-wave3.md` (binary_conv,
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
| C8 FAIL (NOT MET, PARTIAL): P1 merged; P1b to 96.23 M needs A2 to at least 170 M | same: P1b not complete; the join and the state to 96.23 M (and to 97.33 M live) reproduced | agree |
| binary_conv (batch 4a): order ">= 3.3" not established; "only the three-point (R12) or later R16n data decide the order" | R12 now decides it: no order exists (s12 - s16 changes sign; m/8 outside the asymptotic regime) | agree, and the open question is closed in the negative (F2) |
| binary_conv (batch 4a): fractional drifts labelled "per M" | the S6/H2 "per M" numbers are fractional too | agree; the wording is still in the batch-21 numbers (F3) |
| khsr_note: P1 to 280 M "not rechecked, to the G1 verifier" | merger, remnant pass and recession, rms H, remnant mass change, heavy hole +0.32 percent (from 4 M) reproduced; d_at_112 not reproduced; spin and radiated energy not checked | mostly done; one defect found |
| khsr_note: K3 "a second agent's check ... is part of the G1 verifier" | four prograde points (D = 0.5, 1; parabola, r_a = 100 r_t) with my own integrator, all within 0.41 sigma; P1/P2 0.144, 0.155 | agree at these points (K3a/K3b); K3c/K3d and the other r_a not checked |
| C6 PASS (F-pre-1, F-pre-2) | not checked by me | no opinion |
| C18 OPEN: "every number of the Supplemental Material recomputed from the manifests" | ledger rows 122, 128, 168, 194, 200-207 (part) recomputed; the passage, Newton, mesh, horizon and junk numbers above too; the rest of the ledger not | C18 is met for the material of sections 3.1-3.5 only; the rest of the ledger, F-pre-1/2 (except the four KHSR points) and eih remain for a verifier |

Where the lead's text should change (my requests a-f of section 8): F1 (heavy-hole branches, before
judging A2-5), F2 (no order of convergence; quote the m/12-m/16 agreement instead), F3 (fractional
"per M"; the conic 9.81 M; p1_280's d_at_112), the baseline of "+0.32 percent" and the method of
"own residual 4.9e-7".

---

# Part 2, 2026-11-27 (batch 34): the completed passage to 186.0 M

Second fresh verifier (not the author of part 1), helper package `verifier-tail/` (README,
JOURNAL with predictions PT1-PT20 and outcomes, scripts, results, figures), processors only,
0 card-hours. Runs (all registered, local, 1 core):
**F-20261128-003721-95f3c15** (part 1's `verifier/scripts/run_all.sh`, unchanged),
**F-20261128-004301-ce51e1f** (`vtail.py`: status files, fates, overlaps, waves),
**F-20261128-004549-2a094fb** (`vbranch.py`: finder branches), **F-20261128-004718-796bd33**
(`vlogs.py`: chain logs), **F-20261128-004800-5f93427** (`vhrms.py`: residual classes). Every
number below is from one of them. A2's outputs were last written 2026-11-27 04:17 PST (chain STATUS
FAILED after an sbatch I/O error, no job queued); A2's manifest still said "submitted" while the
lead's `nrpic-run finish` pass ran, so I read a run that was not yet closed but no longer changing.

## 10. What was done, and how independent it is

- Before writing predictions I had seen: the subjects of the lead's commits da850964a and
  3c43374a0 (capture of m1 at 137.5 M, m2 to 186 M, "C8 met", "F1 decided in part"), decision
  0044 item 2, the last rows of A2's heavy-hole summary and status files, criterion (iv) and
  A2-1..A2-5 as written. I did not read the lead's batch-34 journal entries, `REVIEW-wave3.md`,
  the current CHECKLIST or STAGE_REPORT before section 16 was committed.
- Part 1's readers ran unchanged. New readers (in `verifier-tail/scripts/`) read what part 1's do
  not: the status files (`hills.horizon_status_<n>.txt`, with a self-test on synthetic files with
  restart repeats and two kinds of failure; the self-test first failed on a bug of its synthetic
  writer, not of the reader), the hrms column of the summaries, the chain's segment logs, and the
  (2,2) amplitude against retarded time.

## 11. Part 1's readers on the completed passage (run F-20261128-003721-95f3c15)

| Quantity | Value | Remark |
|---|---|---|
| tracker join | 77 files per tracker (A + A2), 0-186.0 M, 95233 times, every step 2^-9 M, no gap | |
| overlaps of recomputed stretches | A-A <= 1.13e-12 M, A-A2 <= 4.8e-14 M, A2-A2 <= 1.25e-9 M | the 1.25e-9 M is tracker 0 at 104.0-104.4 M (two cut segments); 1.1e-10 M tracker 1 at 165.0 M; all others <= 1.2e-12 M (fig_t_waves_overlaps b). Restart round-off of an asymptotically flat refined run, harmless at this size |
| pair closest approach | 2.109626 M at 76.3727 M; no later minimum; s = 17.53 M at 186 M | unchanged from part 1 |
| centre of mass of the pair to M | one minimum, 4.5251 M at 140.585 M | after m1 is inside M this point is not the c.o.m. of a bound pair |
| end state | tracker 0 1.3e-9 M from M's tracker; tracker 1 17.53 M from M | the reader's E_0M (-2e10 units) is 1/r of coinciding trackers, meaningless |
| Newtonian reference (same deck) | identical to part 1 in every digit (m1 = comp0 ejected, m2 bound; pair 3.67475 M at 87.6 M) | `vtest.json`, `vjunk.json` byte-identical too |
| horizon medians in A2 | 0.129487 (m1), 0.129508 (m2), 1.004220 (M) | M's median is still a pre-capture value |
| failures by the signature | finder 0: 1340 from 139.56 M; finders 1, 2: none | confirmed by the status files, section 12 |
| rms H = sqrt(H-norm2/Volume), A2 | at most 6.19e-5 at 135.5 M; 1.51e-5 at 186 M | below 1e-4 throughout (A: at most 2.6e-5) |
| waveforms | every 0.25-M sample 0-186 M at 40, 48, 70, 90 M, both parts (745 joined); A-A2 common samples agree to 1.4e-12 | |
| `heavy_A2_branches` | splits at 1.063, i.e. before/after the capture | no longer the F1 reading; F1 is redone in section 12 |

Figures read: `verifier-tail/figures/fig_v_passage.png`, `fig_v_horizons.png` (part 1's
figures, redrawn to 186 M).

## 12. Checked by eye and with the new readers

**Fates from positions** (fig_t_fates). m1 (tracker 0) comes within 1 M of M's tracker at
138.334 M and stays (0.604 M at 140 M, 0.1 M at 144.53 M; the two trackers then converge
exponentially to 1.3e-9 M). m2 (tracker 1) passes M once, 8.7333 M at 134.31 M, and recedes:
13.84 M at 170 M, 17.53 M at 186 M, 0.241 M per M at the end. Newton from the same deck assigns
the fates the other way (m1 to 45 M at 200 M, m2 bound near 6-10 M).

**Fates from the horizons.** Status files exist from 133.0 M (1697 search times each after one
row per time; 1771 raw rows with restart repeats). Finder 2 (M): found at all 1697; its mass jumps
from 1.01121 (137.469 M) to 1.12015 at 137.5 M (found), then median 1.12284 (1.12122-1.12358)
from 138.5 M, drift +1.0e-6 per M; at 186 M mass 1.122912, S = 0.31887, chi = 0.2529, irreducible
(area) mass 1.113750. Finder 1 (m2): found at all 1697. Finder 0 (m1): found at 357, not found at
1340 (1302 iteration limit, 31 mean expansion above tolerance, 6 negative mean radius, 1 area
mass below 1e-10); it keeps finding a 0.1298-0.1300 surface until about 139.5 M, i.e. for about
2 M after the common horizon appeared, then "found" surfaces of 0.12, 0.97-1.06 and 0.80 that are
no member horizon (last found 147.656 M) (fig_t_horizons a). [Corrected in section 17: the 0.12 surfaces of
140.3-141.1 M have a small mean expansion; my "no member horizon" holds for the later ones only.] So: m1 is captured (common horizon
of M and m1 from 137.5 M); m2's horizon persists to 186 M.

**The signature of part 1 against the status files.** On the 3 x 1697 searches where both exist
the status file's found flag and the signature (a row identical to the previous one, or a
non-positive or non-finite mass) agree at every search. Part 1's horizon statements made without
the diagnostics (before 133 M) rest on a method that this run confirms where it can be checked.

**m2's energy, with the remnant.** With the remnant mass (1.12284) at M's tracker m2's coordinate
two-body energy is -0.036 units at 186 M (-0.051 against the centre of mass of M and m1; the
reader's +0.121 uses M = 1.00422). v_rel = 0.3739 against v_esc = 0.3780 at 17.53 M. The quantity
rises almost linearly from -0.50 at 145 M to -0.04 at 186 M (fig_t_fates d): it is not conserved,
so whether m2 escapes is not decided by coordinates [JUDGEMENT].

**Masses, finding F1** (fig_t_branches a, fig_t_horizons c). From 86.6 M the heavy hole's
accepted searches fall in two classes that the summary's own column 9 (hrms, the area mean of the
squared expansion; zero on a marginally trapped surface) separates by four orders of magnitude:
the upper branch (825 searches, median 1.004222, 1.004189 to about 1.00425 up to about 131 M)
has hrms 9.4e-9 to 3e-8; the lower branches (803 searches, 1.00289-1.00394, last at 129.41 M)
have 1.4e-4 to 6.5e-4, and so has the smooth decline of 62-86.6 M (1.6e-4 to 3.7e-4) that part 1
fitted at -1.72e-5 per M. Which branch do the status files support? None directly: they begin at
133 M, after the last lower-branch search, and hold only upper-branch searches (144 up to the jump,
all found, 4-61 flow iterations). The hrms column decides it: **the converged heavy horizon is
the upper branch, 1.00422, constant to about 3e-5 from 86.6 to about 131 M; the decline and the
lower branches are unconverged surfaces** [JUDGEMENT on the meaning of hrms]. From about 131 M
the upper branch grows (1.0161 and hrms 1.1e-2 at 137.47 M) as m1 closes in, then the jump.

**New finding F5: "found" does not mean converged** (fig_t_branches b, c; fig_t_hrms). Finder 1
alternates from 160.56 to 179.22 M between an upper branch (300 searches, 0.12956-0.12963, hrms
1.2e-6 to 2.8e-6, 43-47 flow iterations) and a lower branch (298 searches, 0.12890-0.12918, hrms
0.154 to 0.231, exactly 6 flow iterations, mean expansion -0.043); the status file marks all 598
found. Before the capture every member finder accepts, in episodes, surfaces of hrms 0.011 to 0.50:
29.0 percent of A's finder-0 searches (A's file, 0-64 M), 16.7 percent of A's finder 1, 3.8 and
5.1 percent of A2's finders 0 and 1, with masses below their low-hrms neighbours by medians of
6e-5 to 3.2e-4 (at most 1.35e-3). The heavy finder accepts no search above 1e-2 before 136.9 M, but
its two classes (about 1e-8 and 1e-4) run side by side in A as well. The drift fits of part 1 and
of the owner (H2, S6) include these rows.

**Chain logs (A2-5's mesh clause).** 46 segments: 1968 to 2514 MeshBlocks (below 2864); card
memory peak 78789 MiB (96 percent of an 80 GB card); exits 0 and 143 only; no error line.

**Waves** (fig_t_waves_overlaps a, fig_t_branches d). |r Psi4 (2,2)| at 40, 48 and 70 M coincide
against u = t - r* and rise above three times their 60-130 M level from u = 97.2, 95.2, 95.6 M to
the end (8.4e-3 at r = 40 M at 186 M, 52 times that level); at 90 M the record ends before that
u. [JUDGEMENT: the chirp of m1's plunge into M.] The capture (137.5 M) reaches only the 40-M
sphere before the record ends (u = 139.7 at 186 M): no ring-down is recorded at any radius.

## 13. Judged as written

| Item | Text (where) | Verdict | Evidence |
|---|---|---|---|
| A2-1 | minimum 2.0-2.7 M at 63-75 M, s > 1 M throughout (JOURNAL l. 829-831) | REFUTED on timing (stays): 2.1096 M at 76.37 M; the band and s > 1 M hold | section 11 |
| A2-2 | c.o.m. closest approach at 95-115 M and 8-11 M (l. 831-833) | REFUTED (stays): one minimum, 4.525 M at 140.6 M | section 11 |
| A2-3 | by 170 M one member > 30 M from M with positive energy, the other bound with pericentre 4-8 M (l. 833-836) | REFUTED. At 170 M m2 is 13.84 M from M (17.53 M at 186 M); m1 is captured, not bound on a 4-8 M pericentre; m2's energy is marginal and not conserved in coordinates. The binary is separated (it holds that it broke up) | section 12 |
| A2-4 | no common horizon of a member with M (l. 836) | REFUTED: common horizon of M and m1 from 137.5 M (found, 1.12015 rising to 1.1228) | section 12 |
| A2-5, members | drift below 1e-4 per M outside the encounter | MET on the low-hrms searches (part 1: 3.1e-5, -8.1e-6 per M as fractions, 65-95 M); m2 after the capture +2.7e-5 per M [from the upper branch 147-186 M, read from fig_t_horizons b, not fitted]. The high-hrms rows (F5) are not drift | sections 11, 12 |
| A2-5, heavy hole | changes by less than 1e-3 to 200 M | REFUTED (stays): +0.12 at the capture; on the converged branch constant to about 3e-5 from 86.6 to about 131 M, which is what the clause meant to test [JUDGEMENT]; the record ends at 186 M | section 12 |
| A2-5, mesh and memory | below 2864 MeshBlocks, inside the card's memory | MET: at most 2514; peak 78789 MiB | section 12 |
| A2-5, constraints | rms H below 1e-4 | MET: at most 6.19e-5 (135.5 M) | section 11 |
| C8 / criterion (iv) | one complete vacuum passage: all horizons found in every search until a merger, trackers until t = 200 M, outcome stated with the constraint norm (`../G0/SCOPING.md` l. 139-141) | MET IN SUBSTANCE, NOT AS WRITTEN on one clause [JUDGEMENT]: (a) every search of all three finders accepted until m1's merger with M (signature, 0-139.5 M; status 133-137.5 M; the two agree wherever both exist), but "found" includes unconverged surfaces (F5); (b) trackers end at 186.0 M, not 200 M (14 M short; decision 0042 item 2 says "at least 170 M", which is not an amendment of the criterion's text that I can find); (c) the outcome can be stated: the binary is disrupted, m1 plunges into M (common horizon 137.5 M), m2 survives its 8.73-M passage on a marginal orbit whose binding is not decided by the record; rms H at most 6.2e-5 | sections 11, 12 |

On the gate question (a baseline without new core work: one complete vacuum passage with its
checks): the passage is complete in the sense that matters for G1 (pericentre, break-up, capture
and the survivor's recession are all in the record, with horizons, constraints and waves), and
the failed predictions (A2-1 on timing, A2-2, A2-3, A2-4, the heavy-hole clause of A2-5) are
failures of what was expected, not of the run. I see no reason in the data to withhold G1 on
them if they are stated as refuted [JUDGEMENT]. Two things should be stated with the verdict: the
end at 186 M against the criterion's 200 M (or an amendment by the orchestrator), and m2's fate
as undecided.

## 14. Predictions that failed (mine, part 2)

PT1 in one class (A2-A2 overlaps up to 1.25e-9 M, bound 1e-11); PT3 on my own window (140.6 M,
window 115-140 M); PT11 (the large overlap is at 104 M, not after 133 M); PT12 for finder 0 (I
expected the signature to undercount; it agrees at every search: my count came from raw rows);
PT13 (finder 0 still finds a 0.130 surface for 2 M after the common horizon); PT15's mechanism
(the rise starts at u = 95-97 M, long before the capture's signal); PT17 as written (the heavy
upper branch's hrms rises near the capture, so the ranges overlap); PT20 in its numbers
(fractions 3.8-29 percent, mass offsets 6e-5 to 3.2e-4). Details in `verifier-tail/JOURNAL.md`
entries 2-6. The header times of entries 2-6 there were estimated, not read from the clock (the
commits, 16:42-16:48 PST, are the record).

## 15. From part 1's "not checked" (section 6), and what remains

Done here: the tail of the passage (sections 11-13), the status files, A2-5's mesh clause, the
residual classes of all accepted searches of A and A2. Still not checked by a verifier: criterion
(i) F-pre-1 against 0911.1136 and 1804.02911, and KHSR beyond the four points of section 3.5;
criterion (ii) F-pre-2 against 2404.16270 and the Kerr part (2402.02178); the EIH package; P1's
remnant spin (ledger row 204), radiated energy (row 208) and recoil; the N1/N1m tide; the single-
member junk (S2g); the junk at P1b's spheres; the energy radiated in P1b (the record ends before
the capture's signal passes r >= 48 M).

## 16. Requests

- To the lead (F-hills): (a) state the passage's end as 186.0 M and ask the orchestrator whether
  criterion (iv)'s "trackers until t = 200 M" is met by it or amended; (b) state m2's outcome as
  undecided in coordinates (two-body energy -0.04 to +0.12 units by mass convention, v/v_esc =
  0.989 at 186 M, not conserved); (c) quote the heavy hole on the upper branch, 1.00422, and say
  that part 1's decline (-1.72e-5 per M) and the lower branches are unconverged surfaces by the
  summary's hrms; (d) do not read "found" as "converged": exclude or flag accepted searches with
  hrms above 1e-2 in the member drifts (H2, S6), and say that finder 1 alternates at 160-179 M
  with a found branch of hrms 0.2; (e) state that the capture's wave is recorded only at 40 M and
  without ring-down; (f) note the A2-A2 overlap of 1.25e-9 M at 104 M (restart round-off).
- To core: the status file marks as found a surface accepted after 6 flow iterations with an
  expansion residual of 0.15-0.23 (A2, finder 1, 160.6-179.2 M, `mass_tol` rule without
  polishing on the core-v0.5 card build). Please say whether `polish_iterations_<n>` of core-v0.8
  removes such a branch on this case, or record the case in `finder_stop.md`.

## 17. Comparison with the lead's verdicts (written after sections 10-16 were committed, 88fa5d04a)

Read: the lead's batch-34 entries (`../../JOURNAL.md` l. 1280-1421), CHECKLIST C8 and OPEN.md
items 1-5 (current). One further reading made after that, with a prediction first (PT21,
`verifier-tail/JOURNAL.md` entry 7): run **F-20261128-005105-f29eb5a** (`vf0.py`).

| Point | Lead | Mine | Agreement |
|---|---|---|---|
| C8 | MET, "beyond the 170 M asked" | met in substance; criterion (iv) says trackers until t = 200 M, the record ends at 186.0 M | same outcome; I ask that the 186-against-200 M departure be stated or the criterion amended by the orchestrator (decision 0042's "at least 170 M" is the run's target, not an amendment of (iv) that I can find) |
| capture of m1 | common horizon from 137.5 M; area mass 1.0053 -> 1.1137 | same time; summary (Christodoulou) mass 1.12015 -> 1.1228, area mass 1.11375 at 186 M, chi 0.253 | agree (the lead quotes the irreducible mass, I the summary mass; both are in the files) |
| m1's own horizon after 137.5 M | lasts to about 141 M (area mass 0.13, mean expansion below 2e-3) | part 2 said the 140-141 M surfaces were no member horizon | **I correct myself** (PT21): to 141.09 M the found surfaces have small mean expansion (mostly below 2e-3, at most 0.21) but hrms 2e-3 to 7.5e-2 and a mass that drops from 0.133 to 0.119 at 140.3 M: found, distorted surfaces; "m1's horizon to about 141 M" is a fair reading of the mean expansion, not of the residual. Spurious found surfaces 141.1-147.7 M: we agree |
| m2 | found at every search, mass within 6.4e-4 of 0.12954; recedes on a marginal orbit, fate undecided | same; but 160.6-179.2 M finder 1 alternates and the lower branch (298 searches) has hrms 0.15-0.23 after 6 flow iterations | agree on the fate; the lead's "constant mass within 6.4e-4" includes the unconverged lower branch (finding F5) |
| m2's energy | +0.12 units with M's pre-merger mass, about -0.04 with the remnant; UNDECIDED | -0.036 (remnant 1.12284 at M's tracker), -0.051 (c.o.m. of M and m1), +0.121; not conserved (-0.50 at 145 M to -0.04 at 186 M) | agree |
| F1 | "decided in part": the status file does not separate the two branches near m1's approach (from 135.2 M both found, mean expansions 4.64e-3 and 4.61e-3); which branch is converged not established; test proposed with polished searches on restart files 87-133 M | from 86.6 to about 131 M the summary's hrms separates the branches by four orders of magnitude (upper 9.4e-9 to 3e-8, lower 1.4e-4 to 6.5e-4; the 62-86.6 M decline also 1.6e-4 to 3.7e-4): the upper branch, 1.00422, is the converged surface | **differ**: the lead did not use the hrms column; on it F1 is decided for 86.6-131 M [JUDGEMENT: hrms vanishes on a marginally trapped surface]. Near the approach (from about 131-135 M) the hrms rises on both and no longer separates them: there I agree with the lead. The polished-search test the lead proposes would confirm independently |
| heavy hole's change, A2-5 | REFUTED; "1.55e-3 by 133 M before the merger" | REFUTED by the capture; on the converged branch constant to about 6e-5 from 86.6 to about 131 M; at 133.0 M the status file's first row is 1.00444 | same verdict; the lead's 1.55e-3 is reached only by about 135 M as m1 approaches (its own text: 1.00443 at 133.0 rising to 1.0055), so "by 133 M" should read "by 135 M, during m1's approach" |
| A2-1, A2-2, A2-3, A2-4 | refuted (A2-1 on timing) | the same | agree |
| A2-5 members, rms H, mesh | MET; MeshBlocks 1968-2584 | MET; MeshBlocks 1968-2514 (registered read of all 46 segment logs, start and end counts); 2584 not found anywhere in the chain directory (text search) | agree on the verdict; ask the lead for the source of 2584 |
| overlaps | <= 1.25e-9 M | the same, located at 104.0-104.4 M (tracker 0) | agree |
| waveforms | every sample to 186 M, none missing | the same; plus: the plunge chirp from u = 95-97 M at 40, 48, 70 M; the capture's signal reaches only r = 40 M; no ring-down recorded | agree; the lead says nothing of what the waves contain |
| found flag | "a found search means the mass rule held, not a vanishing expansion" (D34-1); request to core sent | the same, with numbers for the members (F5: 3.8-29 percent of member searches at hrms above 1e-2 before the capture, m2's branch at 160-179 M) | agree; F5 widens it to the members and to the drift fits (H2, S6) |
| failed predictions | A2-1 (timing), A2-2, A2-3, A2-4, A2-5 heavy clause, C25-1 tracker clause, C25-3 rate, D34-1, D34-2 in part | I did not judge C25 or D34 one by one; my readings agree with the numbers the lead gives for them (8.733 M at 134.3 M; 140.55 M below 0.5 M from my d0 series: 0.604 M at 140 M) | no disagreement found |

Where the lead's text should change: (1) C8's evidence should say 186.0 M against the 200 M of
criterion (iv) and leave the acceptance to the orchestrator; (2) F1 can be stated as decided for
86.6-131 M by the summary's hrms (upper branch 1.00422 converged; the decline of part 1 and the
lower branches unconverged), and open only during m1's approach; (3) "m2's mass constant within
6.4e-4" should say that the lower half of that range is an unconverged branch found at 160-179 M;
(4) "1.55e-3 by 133 M" -> "by about 135 M, during m1's approach"; (5) the source of MeshBlocks
2584.
