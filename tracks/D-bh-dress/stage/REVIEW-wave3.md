# Lead review of the wave-3 packages of D-bh-dress

Lead session of batch 2a, 2026-11-21 06:29-07:20 UTC (Opus). Packages that finished since the
lead of wave 2b (2026-11-19): `es_runs` (ES-1G closed) and `verifier_g1` (VERIFIER.md). Packages
cut by the usage limit of 2026-11-20 and still open: `flux_tools`, `drift_controls`,
`secondary_infall`, `note`; their finished parts are reviewed below, what remains is listed in
`../HANDOFF.md`. Plan of the round: `../PLAN-wave3.md`.

Method: rechecked from the registered outputs and figures, not from the helpers' reports. My
predictions Z1-Z6 were committed to `../JOURNAL.md` (entry "lead-wave3-batch2a ... predictions",
commit 68db5e73) before the check ran. Check script `review_wave3/wave3_check.py` (mine; readers
taken from the previous lead's `review_wave2/es_finish_check.py`, no helper code), run
D-20261121-063617-3f2036f (`wave3_check.json`, `wave3_check.png`, looked at). Paths relative to
`tracks/D-bh-dress/`; outputs under `/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/`.

| Check | Outcome |
|---|---|
| Z1 ES-1G horizon from the raw finder summary | held, all digits |
| Z2 ES-1G wall, crossings, proper time from traj/trajmet | held |
| Z3 V-1B against V-1 (drift_controls' Pb1, Pb2) | held: the late drift of V-1 is the outer boundary |
| Z4 Newtonian-mode dress at a/a_i = 2 (verifier V2) | held: the verifier is right, the G1 wording was wrong |
| Z5 ES-F particle file (flux_tools) | held, exact |
| Z6 figures (8 looked at) | consistent with the numbers; two cosmetic defects |
| `nrpic-run verify` of 17 wave-3 analysis runs (list in section 7) | PASS, all |

## 1. es_runs: ES-1G closed (FINISHED)

ES-1G = ES-1 with core's `lapse_leak = 0.5`, run D-20261119-142633-6f72922 (0.794 card-hours),
analyses D-20261120-221754-ae3dafe, -222424-230f936, slice mass -222956-6abf860.

Confirmed by my own reading (Z1, Z2, run D-20261121-063617-3f2036f):
- [VERIFIED] M_AH(100 M) - 1 = +1.1410e-3; drift from 100 M: maximum +6.963e-3 at 199.5 M,
  minimum -4.167e-4 at 126 M, range on 100-165 M [-4.17e-4, +9.46e-4]; mean coordinate radius
  1.398 M at 25 M and 0.776 M at 199.5 M. Every number of README rows G6 and of the
  "late horizon drift" paragraph reproduced to the printed digits.
- [VERIFIED] Wall tracers (tags 56-69), my areal radius r sqrt(B): max |R/R_w - 1| = 1.676e-4
  over the whole run (tau to 206.4 M), two classes (axis, diagonal) visible in my panel (c) but
  both below 1.7e-4. G4 held.
- [VERIFIED] Group R0 = 6 M: 14 of 14 cross R = 2M, mean tau 14.82607 M, error -8.51e-4 M
  (range -8.62e-4 to -8.43e-4; claim -8.6e-4); R0 = 10 M: 14 of 14, errors -4.98e-3 to
  +0.91e-3 M (claim -5.0e-3 to +0.9e-3). Group R0 = 48 M at t = 200 M: tau 205.320-205.326 M
  (claim 205.3; ES-1 279.7). G3 and G5 held.
- Figures looked at: `figs/es1g/judge_horizon.png` (the three panels show the numbers above;
  defect: the top-panel legend sits on the early transient and the black core-ES line runs
  through the label "core-ES", cosmetic, not fixed), `figs/es1g/slicemass_ES-1G.png` (m(R)
  flat at 1 inside the bubble up to t = 150 M; the exterior plateau 2.74 erodes from the outer
  edge inward, 2.3 left at t = 200 M; the finder's R = 2M_finder marks sit on 2m/R = 1 at every
  dump, which is K2's "not the finder").
- Not rechecked by me: G1, G2, J1-J6 (lapse and K-hat against the lapse_leak model), K1-K2
  (Misner-Sharp mass from the 2.3 GB restart dumps). Their figures are consistent with the
  claims; the K2 conclusion is supported independently by the shape of the drift (smooth
  growth of 7e-3 that the finder's convergence settings could not produce at that size).

Judgement of the lead on the package's conclusions:
- "G6 refuted, the dust-coupling reading not established": agreed. With V-1B (section 3) the
  natural reading is that ES-1G's late growth comes through the outer boundary (the exterior
  mass is lost from the faces inward, K1), now with a mechanism that is tested in vacuum. It is
  still a [JUDGEMENT] for ES-1G itself: no ES-1G run with the faces at +-384 M exists.
- "G2 runs should use lapse_leak, with the boundary beyond the light-travel distance, an M/16
  nest, a matched V-1G control and an excision criterion not resting on alpha_exc": agreed and
  adopted as the plan of the G2 null test (`../HANDOFF.md`). The boundary condition is now
  measured, not only argued (section 3).
- No defect found in the package. Closing: complete.

## 2. verifier_g1: fresh-context verifier of the G1 material (FINISHED)

`verifier_g1/VERIFIER.md` (commit 102d696b with the verdicts before any review was read; the
V4 correction c8a53093 and the comparison section after). Copied to `stage/G1/VERIFIER.md`
(item C17). Its runs verify PASS (section 7). Independence: the verifier read the note at the
pinned commit 78d470ca and no stage file before its verdicts; its V4 correction was found with
the track's grid in view, which it states.

Checked by me: Z4 reproduces the V2 finding from the track's own table
(`secondary_infall/nm_growth_cellcentre.txt`): dress against the kernel shells at a/a_i = 2
+0.55 (N128c), +1.40 (N64c), +3.31 (N128Lc) per cent; at a/a_i = 4: -0.01, +0.15, +0.47; at 8:
+0.10; largest |deviation| for a/a_i >= 3: 0.28, 0.68, 1.03 per cent. M_ta: within 0.12 per cent
at 2 and 4, 0.29 at 8. Figures `v2_growth_ratio.png` (run D-20261121-031711-0d79cb3) and my panel
(d) show the same picture: the dress is high by 1-7 per cent below a/a_i = 2, where it is small.
Figure `v3_hern_a0.8.png` (run D-20261121-033209-9c0bd44): the verifier's curve lies below FdRW
by 4-5 per cent only at the peak (r ~ 5 Gm), where the digitised FdRW curve has a narrow bump;
1-2 per cent below beyond 8 Gm. Consistent with its [JUDGEMENT].

What the track does about each WRONG and NOT CONFIRMED item:

| Verifier item | Verdict | Action of the track |
|---|---|---|
| V2 dress at a/a_i = 2 within 0.1-0.5 per cent | WRONG | Corrected in `stage/G1/STATUS.md` (this session): M_ta within 0.3 per cent of the kernel shells at a/a_i = 2, 4, 8; dress within 1.1 per cent from a/a_i = 3 on, 0.5-3.3 per cent at a/a_i = 2, sensitive to the central force law. The note's text and ledger (package `note`, open) must take the same wording; listed in HANDOFF. |
| V2 profile "within 25 per cent" at a/a_i = 8 | CONFIRMED marginally (25.9 per cent, 33-35 with r_ta +-3 per cent) | Restated as "about 25 per cent, sensitive to r_ta" in `stage/G1/STATUS.md`. The profile criterion stays open (C7) pending orch's ruling `d-pre-3-criterion` or the run to a/a_i = 30 (secondary_infall). |
| V2 comparison with `secondary_infall/selfsimilar.py`; seeded vs seedless lambda_1 (0.3553 vs 0.3630) | NOT CONFIRMED (not done; not comparable) | The ledger must describe the seeded model (note package); no new run this session. |
| V3 Hernquist on the axis within 1.5 per cent | NOT CONFIRMED (not computed) | Stays [TO VERIFY] in `stage/G1/STATUS.md`; a second-agent axis curve is a G2-time item, not needed for the D-pre-2 baseline (equatorial curves confirmed). |
| V3 a = 0.8 Hernquist peak 4.5 per cent below FdRW | CONFIRMED; [JUDGEMENT] the gap is in FdRW's curve | Recorded as such with the verifier's reasons; OPEN item 1 of G1 (second agent for action matching at L_z != 0) closed for the equatorial Kerr reference. |
| V3 hole mass 4e6 Msun | [TO VERIFY] (not in the text) | Checked: `kerrdm.tex:127` (kb-data/raw/arxiv/1707.06302) says only "M_BH >~ 4e6 Msun"; the track's 4e6 is the lower bound, a choice [JUDGEMENT], supported by the a = 0 curve agreeing to 0.55 per cent (V3). Stated in STATUS. |
| V4 inner-range deficits 3.1, 1.8, 0.9 per cent | CONFIRMED, not independently (verifier's own error found with the track's grid in view) | Each within 1-2 sigma; a second sampler seed decides a bias; listed as a G2 item. Superseded verifier runs D-20261121-034048-17427b0 (reference numbers), -035106-0c619ee, -040417-8a3c402 stay on record. |
| V5 eight ledger rows not done | NOT CONFIRMED | Listed in `stage/G1/OPEN.md`; the track's own reruns of those rows (D-20261120-223535-24f7f90, note package) exist but are not a second agent. |
| V5 table-density residuals are upper bounds; "wall radius against the closed form" ambiguous | remarks | Note package (ledger wording); listed. |
| V1 "no dust in the bubble" depends on the wall model; checked at snapshots only | qualification | Accepted; my predecessor's Y5 used 10-degree cones and found the same margins (0.126-0.154 M). |

## 3. drift_controls (OPEN; step 1A finished, card run (b) ran, not judged by the package)

Finished part, step 1A (run D-20261120-222107-cc4937b): its figures and `results/step1.json`
were left uncommitted by the cut session; they are byte-identical to the run's outputs and are
now committed (3f2036fe). The five figures were looked at by the helper; I looked at none of
them in detail this session (the numbers I rely on below come from my own check).

Card run (b), V-1B = V-1 with the faces at +-384 M (D-20261120-222625-63abd72, Slurm 4743,
DONE (tlim) on 2026-11-20 16:43 PST, closed by me: 0.7775 card-hours). The package's
predictions Pb1-Pb5 (its JOURNAL entry 2) were written before submission. My first reading
(Z3; run D-20261121-063617-3f2036f, panels (a) and (b) of `wave3_check.png`):
- Pb1 HELD: drift of V-1B from 100 M stays within [-4.84e-5, +1.97e-5] over 100-199.5 M, D(199.5 M)
  = -9.2e-6 (V-1: -1.363e-4 with my reference sample). V-1's late fall after 165 M is absent.
- Pb2 HELD: V-1B and V-1 agree to rounding (1e-15) until t ~ 90 M, separate by more than 1e-9 at
  116 M and by more than 1e-6 at 133 M (predicted between 110 and 165 M).
- Pb5 HELD: 0.7775 card-hours against 0.78 +- 10 per cent.
- Pb3, Pb4 (Theta at the hole, coordinate-radius rate) not computed by me; left to the package.
- Consequence [VERIFIED for V-1 at M/8]: the common late drift of V-1 (risk R13) comes from the
  outer boundary at +-192 M; with the faces at +-384 M the vacuum-bubble floor at M/8 over
  100-200 M is 4.8e-5. For ES-1 and ES-1G (with dust and its exterior) the same cause is
  likely but not tested [JUDGEMENT].
- Pre-flight of card run (a) (D-20261120-222820-94f20b3, closed by me, exit 0): the processor
  re-search at t = 150 M gives 1.00091844 against the card's 1.00091841 (3.1e-8 relative), so
  its prediction C1 (1e-8) is refuted as written; the A32 grid is offset by +1.84e-4 (D-pre-4:
  1.8e-4). Both are the package's to judge; for a drift question at 1e-5 the 3e-8 is irrelevant.

Left uncommitted (in progress, untouched): `tools/compare_runs.py`, `tools/count_blocks.py`,
`tools/slice_profiles.py`.

## 4. flux_tools (OPEN; construction check finished, ES-F not submitted)

Finished part (entries 6, 6b, 7): second-agent check of the ES-F construction (runs
D-20261120-222314-ed5d325, -222651-3180e07, -222815-f8d1b42; all verify PASS) and the
pre-registration of the ES-F card run (entry 7, commit 54a52aea).
- Z5 held exactly (my reader of `esf.nrp` of data run D-20261119-145022-2208a19): 850724 records,
  140 with m = 1e-30, every u_i = 0; dust rest mass 2.815600140293471 and sum of m (1 - 2M/R0)^(1/2)
  2.738654513324783, both equal to `esf.json` bit for bit, -4.27e-7 and -4.06e-7 below the
  continuum values.
- Figure `figs/check_esf_construction.png` looked at: table against closed forms at 1e-15 of
  max|K_T| except at the inner dust edge (R ~ 3 M), Hamiltonian residual below 1e-16 of 16 pi
  rho0, momentum residual 1e-5 at the edge falling to 1e-12, energy per tag exact, growth table
  on the closed-form curve.
- The construction is CONFIRMED by an agent who did not build it [VERIFIED as far as the
  identities and data go]; the evolution's physics is not checked (shell crossing, sphericity).
- Remaining (package): submit ES-F as pre-registered (the release core-v0.4 card executable
  now has the accretion diagnostics; the pre-registered command names
  `core_requests-adf/athena_gpu`, keep it so that the pre-registration holds), finish script,
  analysis, V-0 control, README update.

## 5. secondary_infall (OPEN; design and references finished, production run not started)

Finished: design table D-20261120-222358-e98ffbd, timing D-20261120-222405-ce8922c (0.66 s per
step at 192^3 on 6 threads), matched shell references to a/a_i = 30 (kernel -222511-34be8a8,
Plummer -222513-9849530, point -222515-c2ef5b8, hybrid -222758-acc6929, hybrid of N128Lc
-222804-e5183e9), R8 = N128Lc rerun on the threaded build (-222550-e472402). The last three
"running" manifests were left open by the cut; their processes had ended with exit 0 and I
closed them with `nrpic-run finish`. Not analysed: R8 against N128Lc (prediction in its
JOURNAL), the production run to a/a_i = 30 (not started). Core's correction of 2026-11-21
(inbox): isolated Newtonian boxes are faster on processors (0.41 s per step on six threads
against 0.65 on a card), so this run stays a processor run: about 2000-4000 steps, 0.4-0.8 h.

## 6. note (OPEN; v1 text, figures and schematics finished, PDF not rebuilt)

Finished: five figure and schematic runs (D-20261120-222413-4a67fa2, -222422-983f3f6,
-222424-d7cd958, -222429-026731f, -222430-452c907; P7-P10 held) and the run of every figure and
the ledger (D-20261120-223535-24f7f90, "11 of 11 scripts ran cleanly"; P11's outcome not
written). `figures/schem_architecture.png` looked at: three columns (initial data, evolution,
analysis) with exists / provided by core / new for Track D; core's wave-2 capabilities
(tracers on timelike orbits, removal record, flux spheres, analytic excision, Newtonian point
mass, relaxed lapse, threaded build) and the run chain bubble data -> bubble run and control
-> relaxed lapse -> late-drift controls -> dust to the hole -> growth law and null test; no
label outside its block. G1 item C9 is met by this schematic. Remaining: P11 outcome, compile,
`check_manuscript.py --compile` (P12), read every page, commit the PDF; the verifier's wording
corrections (section 2) into the text and ledger.

## 7. Housekeeping

- Runs closed with `nrpic-run finish` (all ended with exit 0 while their sessions were cut):
  D-20261120-222515-c2ef5b8, D-20261120-222550-e472402, D-20261120-222820-94f20b3,
  D-20261120-222625-63abd72 (card, 0.7775 card-hours).
- `nrpic-run verify` PASS: D-20261120-221754-ae3dafe, -222424-230f936, -222956-6abf860,
  -222107-cc4937b, -222209-871e07f, -222314-ed5d325, -222651-3180e07, -222815-f8d1b42,
  -222429-026731f, -223535-24f7f90, D-20261121-031031-e23da04, -031711-0d79cb3, -033209-9c0bd44,
  -034048-17427b0, -035114-8a3cb38, -040826-9d5051a, -063617-3f2036f.
- Budget after this session (`nrpic-run budget`): G1 4.41 used; G2 0.78 used; nothing
  reserved; 29.22 left toward G2 (allotment 30 per gate, decision 0014).
- `stage/G0/REPORT.md` (wave 1) is a file name decision 0012 no longer uses; G0 is signed
  with it in place (coord/GATES.md), so I leave the signed package unchanged.
- `nrpic-stage verify D-bh-dress G1` (07:07 UTC, on 9182d4d; `stage/G1/VERIFY_RESULTS.md`): FAIL on
  four checks, none a defect of the G1 evidence: clean (the three untracked drift_controls tools),
  sync (main moved during the 25-minute verify; merged at 0cb321d6), runs (three wave-2 runs with
  outputs outside their sha256 lists: D-20261115-170002-8cefc3e, -170326-dfb2a02, -193755-3a53b08;
  waiver requested from orch), compare (`note/figures/fig_newton_numbers.json` lacks the key
  `kernel_shells_at` that `fig_newton.py` writes since c2e0571d: the note package did not copy its
  last outputs; open with the note). Rerun of 10 figure scripts in the clean export: PASS.
- `docs/FORMATS.md` still gives `.trajmet.bin` as 12 doubles (17 in the source); request
  `trajmet-format-doc` to core is open (2026-11-15).

## 8. Lead's decisions of this session

1. G1 stays NOT MET: C7 (D-pre-3 profile criterion) waits on orch's ruling or on the run to
   a/a_i = 30, and C16 on the rebuilt note. C9 and C17 are now met.
2. The G2 null test is run with the outer faces at +-384 M (V-1B mesh, 400 MeshBlocks, 0.78
   card-hours per 200 M at M/8). Next card runs, in order and one change each: ES-1GB (ES-1G
   with the faces at +-384 M; decides whether ES-1G's +7e-3 is the boundary) and the matched
   V-1GB (V-1B with lapse_leak); then ES-F as pre-registered; then the M/16 nest.
3. No card job was submitted in this session (no card-hours were named for the lead).

## 9. Lead session of batch 4a (2026-11-21 15:45-17:00 UTC, Opus)

Packages finished since the lead of batch 2a: `secondary_infall` (batch 2b, closed), `g2runs`
(batch 3, session closed; its two card runs are queued) and `note` (batch 3, closed). Still open
and left alone: `drift_controls` (cut 2026-11-20; three untracked tools) and `flux_tools` (its
ES-F run was submitted by g2runs and is queued; the judging is g2runs' `finish_g2.sh esf`).

Method as before: my predictions Y1-Y5 were committed to `../JOURNAL.md` (commits d794a485 and
the Y5 commit) before the checks ran; no helper code. Scripts `review_wave3/batch4a_check.py`
(readers of `wave3_check.py` and `review_wave2/infall_check.py`) and `review_wave3/batch4a_profile.py`.
Runs D-20261121-155215-0611c24 is Y5; D-20261121-154912-27e91c6 is Y1-Y2 (D-20261121-154902-f2724c5
failed on a syntax error of mine, kept on record). Figures looked at: `batch4a_check.png`,
`batch4a_profile.png` (mine), `compare_horizons.png` (D-20261121-144657-cf510fc),
`axis_profiles.png` (-145907-f76095b), `secondary_infall/figs/w3_Q16_late_profiles.png`.

| Check | Outcome |
|---|---|
| Y1 g2runs horizons from the raw finder summaries | held, with one marginal clause (below) |
| Y2 Q16 growth, particle counts of Q16 and P192 | held (after matching the snapshot times) |
| Y3 note compiles; 3.43 against 3.31 per cent | compile held; my guess of the cause was wrong |
| Y4 figures | consistent with the numbers |
| Y5 Q16 profile against the verifier's self-similar solution | held: 16.3 per cent |

### 9.1 g2runs (FINISHED as a session; ES-F running; ES-1GB ends at 188 M, its second segment capped)

Confirmed from the finder summaries (Y1, run D-20261121-154912-27e91c6):
- [VERIFIED] ES-1GB (faces at +-384 M) equals ES-1G (+-192 M) to 2.9e-15 for t <= 90 M and to
  4.2e-9 up to 188 M (panel a: rounding until ~133 M, then growing). Its drift from 100 M is
  +4.157e-3 at 188 M, the same as ES-1G's +4.157e-3 at that time. **The late horizon growth of
  ES-1G is not the outer boundary.** This refutes my predecessor's reading (sections 1 and 3 of
  this file, HANDOFF and STATUS of batch 2a: "likely the boundary [JUDGEMENT]"); that reading
  was a judgement, it was tested, and it failed. What section 3 established for V-1 (1+log,
  vacuum) stands.
- [VERIFIED] V-1GB (V-1B with lapse_leak) drifts over [-5.60e-4, +1.265e-3] on 100-199.5 M
  (claim +1.27e-3: within one unit of the last digit), V-1B over [-4.84e-5, +1.98e-5]. Mean
  coordinate radius at the end: V-1GB 0.875 M, V-1B 2.196 M, ES-1GB 0.795 M at 188 M.
- [VERIFIED] Null test ES-1GB minus V-1GB: largest |difference| up to 90 M is 1.005e-4 (at
  t ~ 62 M), so the package's "below 1e-4 up to 90 M" holds only to rounding (my clause Y1(d)
  failed by 0.5 per cent; immaterial); above 2e-4 from 137.5 M on, without return; 3.53e-3 at
  188 M. Floor of the null test with lapse_leak at M/8: about 3.5e-3 over 100-188 M.
- Figures: `compare_horizons.png` shows the same (its panel (c) legend sits on the data,
  cosmetic); `axis_profiles.png` shows the lapse at x = 1 M near 0.43 (lapse_leak) against 0.19
  (1+log) at 180 M, the shift peak 0.16 against 0.40 and chi at 5 M falling from 0.68 to about
  0.50 in V-1GB: the numbers of the package's L1/L2 reading. The mechanism stays [JUDGEMENT].
- Not rechecked: the slice masses (S1, B4'), X1 (executable change neutral), T1/T2 tool tests.
- Consequence (decision 0022 item 3): the G2 null test runs without lapse_leak, or with core's
  corrected option (first item of core-v0.7). ES-F (queued, D-20261121-144631-aa7ce9b) has no
  lapse_leak in its input (1+log, faces at +-192 M), so it is not affected by this defect; its
  faces are close, but V-1 at +-192 M drifted by 1.4e-4 over 100-200 M, small against the
  predicted growth of 0.1-0.25 M.

### 9.2 secondary_infall (FINISHED, batch 2b)

Confirmed (Y2, Y5):
- [VERIFIED] Q16 (D-20261121-085652-7e189a2): every one of 520048 particles is in the box at
  a/a_i = 15.96. M_ta and dress at 8.00 and 15.96 equal the README's 4.815/2.148 and
  9.302/4.911 to 4e-5. At "4" and "12" the README quotes values at a/a_i = 4.00 and 12.00; the
  nearest snapshots are 3.976 and 12.020, so my absolute values differ (-0.5, +0.2 per cent),
  but the ratios to the hybrid_cc shells at the same a agree with the README within 0.05 points:
  M_ta +0.21, +0.16, +0.17, +0.78 per cent and dress +0.42, -0.05, +0.17, +0.10 per cent at
  3.98, 8.00, 12.02, 15.96 (kernel_cc: +0.43 to +1.26 per cent). dress/M_ta 0.528 and
  M_ta/(M a/a_i) 0.583 at 15.96, as claimed.
- [VERIFIED] P192 (D-20261121-075559-31835c4) misses 16462 dust particles (0.704 M) at its last
  snapshot (a/a_i = 29.97); the first goes missing at 23.56 (panel f).
- [VERIFIED, Y5, D-20261121-155215-0611c24] Q16's dust profile at 15.96 in six 0.1-dex bins on
  lambda = 0.075-0.3, my r_ta = 246.4 M (zero of the mean radial velocity), against the
  fresh verifier's seedless self-similar solution: largest deviation 16.3 per cent (last bin,
  lambda ~ 0.27, next to the outermost caustic), rms 10.6 per cent; 24.9 and 21.6 per cent with
  r_ta moved by -3 and +3 per cent. The package gives 16 per cent (rms 7.6) against its own
  seeded solution: two references and two r_ta estimators give the same bound.
- Figure `w3_Q16_late_profiles.png`: run and three shell laws on the self-similar line from
  lambda ~ 0.04 to 0.3 at 15.96; below it inside lambda ~ 0.05 (seed and softening of 4 dx).
- Not rechecked: the cause of P192's late failure (shell energies), the kernel's dependence on
  the clump position, R8 (threaded build), the regression of 617 leaves. The package's
  [JUDGEMENT] that a clean a/a_i = 30 run needs nx ~ 450-500 is accepted; it is not needed for
  G1 under decision 0021 item 2.
- Erratum asked by the package (wave-2 shells used the vertex kernel while the runs had the
  clump at a cell centre; about half of the dress excess at a/a_i = 2): taken into
  `G1/STATUS.md` (this session). Masses from a/a_i = 3 on are unaffected.
- Closing: complete. D-pre-3 under the wording of decision 0021 item 2 is met (section 10).

### 9.3 note (FINISHED, batch 3)

- [VERIFIED] The committed source (`git archive` of this branch into scratch) compiles with
  latexmk to 18 pages with no undefined reference or citation; the log has two "Overfull \vbox
  (6.1pt too high) while \output is active" (page builder, not a line overrun), which the
  checker's 0 overfull boxes (it counts hboxes) does not see. Cosmetic; recorded.
- [VERIFIED] 3.43 against 3.31 per cent (N128Lc, dress over the kernel shells at a/a_i = 2): the
  two growth tables are identical (`secondary_infall/nm_growth_cellcentre.txt` and `nm_growth.txt`
  of D-20261115-190541-e27453d); the note's ledger takes nm_analyze's interpolation of the ratio
  at a/a_i = 2 (3.43), my predecessor's Z4 interpolated the two masses (3.31), between snapshots at
  1.954 and about 2.05. My guess (two tables) was wrong. Both are correct; STATUS now says
  "0.5-3.4 per cent at a/a_i = 2, by interpolation between snapshots".
- Not rechecked: the 51 + 3 ledger rows (P11, P13 of the package), the claims check.
- G1 item C16 is met: v1 compiled, checked with `--compile`, every page read by the package
  (note/JOURNAL.md 2026-11-21T13:06Z), the verifier's corrections in.
- Open, recorded (not G1): P14 three data keys of registered outputs ("ES-1",
  pass_e0.1_s0.5_a100) caught by the forbid list; the package asks for an exception in
  WRITING_GUIDE.md (I add it, section 10); a second agent for the eight ledger rows the verifier
  left NOT CONFIRMED.

### 9.4 What the track does about the verifier's items (update of section 2)

| Verifier item | State now |
|---|---|
| V2 dress at a/a_i = 2 WRONG as worded | corrected in STATUS and the note (0.5-3.4 per cent at 2; within 1.1 from 3); half of the N128Lc excess is the reference's vertex kernel (secondary_infall, D-20261121-092852-a0c75f0) |
| V2 profile "about 25 per cent, sensitive to r_ta" | carried; Q16 at a/a_i = 16 gives 16 per cent against both self-similar solutions (Y5), so the profile approaches the solution as a/a_i grows |
| V2 seeded vs seedless not compared | done in effect: Y5 used the verifier's seedless solution, the package its seeded one, same bound |
| V3 axis curve NOT CONFIRMED | open, G2-time item (STATUS) |
| V4 inner-range deficits | open, second sampler seed (G2) |
| V5 eight ledger rows NOT CONFIRMED | open; the note package did not get a second agent (no subagent tool) |

## 10. Lead's decisions of batch 4a

1. G1 criteria: C7 PASS under decision 0021 item 2 (growth against matched shells within 1.1
   per cent from a/a_i = 3 in three wave-2 runs and within 0.8 per cent to a/a_i = 16 in Q16; profile
   within 16 per cent of the self-similar solution at a/a_i = 16, about 25 at 8; r^-9/4 not
   claimed). C16 PASS (note v1). With C19 refreshed, every G1 item is PASS: the package is complete
   for the orchestrator's independent review (decision 0016 item 4). I do not pass the gate.
2. G2 plan after decision 0022 item 3: the vacuum null test with plain 1+log and the faces at
   +-384 M has its floor (V-1B, 4.8e-5 over 100-200 M at M/8). Next card runs, one change each:
   ES-1B (ES-1, 1+log, faces at +-384 M) against V-1B, the matched null test without lapse_leak;
   then the M/16 nest of the pair. lapse_leak runs wait for core-v0.7. No card job was submitted
   this session. ES-F (Slurm 4806) is running; ES-1GB's second segment (Slurm 4805) stopped without
   running because its chain was capped at one segment (MAX_SEGMENTS=1 from the 0.98 card-hour
   reservation): the run ends at t = 188 M and was closed at 16:40Z (status failed, 0.83 card-hours).
3. WRITING_GUIDE.md exception 1 extended to data keys of registered outputs (note package request).

## 11. Lead session of batch 5 (2026-11-21 12:19 PST on, Opus; decision 0025 items 3-5)

No helper package finished since batch 4a; the G1 gate was signed with reservations
(coord/GATES.md, 2026-11-21). This session reviewed only what the card plan needed.

11.1 ES-F (flux_tools pre-registration, g2runs finish script) - CONFIRMED by the lead from the
raw outputs: the run reached 200 M in one segment (0.81 card-hours); the lead re-read the
finder file (M_AH 1.04155, 1.10735, 1.17514, 1.24278 at 50, 100, 150, 199.5 M; finite at 400
samples), the accretion history (first excision 7.8 M, 57722 removals, none escaped, max
m_inside1 0.0101 after 20 M) and looked at `esf_growth.png` and `esf_criteria.png`: the finder
curve lies on the exact m(R0) at tau_H(R0) over tau = 0-265 M, the (iii) bin medians sit at
+0.2 per cent inside the +-1 per cent band, D3 margins are all above -3e-4, every removal is
0.075-0.43 M of proper time after tau_H. Outcomes against flux_tools entry 7 in
g2runs/JOURNAL.md entry 10: all predictions held except P3 (i), which fails at the single
finder sample t = 0.5 M (initial finder dip, sigma 2.8e-5 there), and P3 (ii-tau), predicted
to fail and holding. Not confirmed: a second resolution, faces beyond +-192 M (both in the
long runs below).

11.2 Smoke tests of the long-run inputs found a set-up defect before any card time: the ES-F
table ends at 345 M with `exterior = zero`, so on a +-768 M mesh the slice's curvature would
jump to zero at 345 M. Fixed by re-running the data maker with `--rbar_max 1340`
(D-20261121-203042-82deeec; rows to 345 M and particles byte-identical); g2long JOURNAL entry 2.

## 12. Lead's decisions of batch 5

1. Long card runs toward G2, all plain 1+log (decision 0025 item 3), release core-v0.6, the
   faces at +-768 M so that no face reaches the hole before ~540 M: V-1L (control) and ES-1L
   (null test) to 500 M; ES-FL (growth and dress, the ES-F data) to 500 M; the M/16 pair
   V-1L16, ES-1L16 to 300 M (mesh convergence of the floor and of the null test). Criteria N
   (null test) and G (growth against flux) and every prediction: g2long/JOURNAL.md entry 1,
   committed before any run. Caps 3.5 + 4.0 + 4.0 + 5.0 + 6.0 = 22.5 card-hours (estimate
   ~14); G2 had 26.8 left.
2. The ES-1B/V-1B pair at +-384 M planned in section 10 is replaced by ES-1L/V-1L at
   +-768 M: it contains the same 0-200 M comparison (V-1L against V-1B is prediction V2) and
   reaches 500 M without the faces.
3. Queue: R1, R2 eligible; R3-R5 held and released by a sequencer process
   (scratch/D-bh-dress/g2long_seq/) when fewer than two D jobs are active (0025 item 5).
4. D-pre-3 reservation: Q16-256 (Q16 with nx 256), processors, six threads, prediction in
   secondary_infall/JOURNAL.md (20:36Z).
5. drift_controls stays open (its three untracked tools are left as found); note v2 waits for
   the long runs.

## 13. Lead session of batch 10a (2026-11-22 17:45 PST on, Opus; decisions 0026, 0027)

No helper packages ran since batch 5; this session read the card runs of batch 5 itself, from
their registered outputs, against the predictions committed before them (g2long entry 1,
secondary_infall 20:36Z). Every number below has a registered run; every figure was read.

| Item | Outcome | Evidence |
|---|---|---|
| Sequencer of batch 5 | ended normally: released R5 at 11:12, exited 11:14 with its queue empty; nothing stalled | `scratch/D-bh-dress/g2long_seq/log` |
| R1-R4 | DONE, closed with `nrpic-run finish`; R5 at 225.6 M of 300, job 4920 queued | chain STATUS files |
| Null test N (track criterion 1) | HOLDS at M/8 to 500 M: 2.28e-4 against 2.51e-4; margin 9 per cent | D-20261123-020550-f9a3482, judge_long.png |
| Growth G (track criterion 2) | HOLDS: (iii) to tau 650 M within 0.62 per cent, D2 everywhere | D-20261123-020614-7ba5874, esf_criteria.png |
| Failed predictions | V3 (floor 1.25e-4 > 1e-4), E2 sharp bounds, V3/E3 radii, F2 at 400/500 M, F3 median and D1, F4 reason 3, H1 (sign), H2 (floor not lower at M/16), QR3 per-bin, QR4 slope | g2long entry 5; secondary_infall 02:08Z |
| Cause named after a check that could fail | the end of horizon excision at 219 M: source guard nrpic.cpp:451-455 and the crossing of 3.2 M by the finder's smallest radius between 219.0 and 219.5 M; its effect on (iii) is a [JUDGEMENT] until ES-FLK | g2long entry 5 F4 |
| Constraint norms | bounded, but they measure inside the horizon (chi cut) | D-20261123-021027-e3af9b8, constraints_long.png |
| Q16-256 | QR1, QR2, QR5 hold; D-pre-3 rests on two resolutions | D-20261123-020626-183c254, -020756-e9922e7 |

What I could not confirm: the cause of the vacuum drift step at 240-300 M (both resolutions);
whether the M/8-M/16 sign change of the finder mass is convergent (needs a third member).

## 14. Lead's decisions of batch 10a

1. Follow-ups (g2long entry 6, predictions before any run): FV4 and FE4 (finest level M/4, the
   third mesh member of the floor and of the null test), FK = ES-FLK (initial_radius 1.6, horizon
   excision kept; the run in which the excision cause of the (iii) step can fail), FF4 = ES-FL at
   M/4. Smoke tests on processors first. Caps 2.0 + 2.0 + 3.0 + 2.0 = 9.0 card-hours, expected
   4.5; the budget tool shows 10.57 left toward G2 (R5 counted at its ceiling).
2. Not queued, and why: an M/32 nest that holds the 2.2 M horizon (~13 card-hours per run) waits
   for the M/4 outcome; ES-FL at 4N (particle-number member) waits for ES-FLK, so that it is
   built on inputs with the excision kept and with exterior constraint norms.
3. note_v2 replaces note/ (git mv); G1 stage report: Looked-at column filled from its list.
4. drift_controls stays open with its three untracked tools left as found (no change since batch 5).

## 15. Lead session of batch 11 (2026-11-24 04:51-06:19 PST, Opus; paused by the flag)

No helper packages ran since batch 10a; this session read the card runs queued then, from their
registered outputs, against the predictions committed before them (g2long entries 1, 6), and ran the
processor tests of entry 10. Every figure named here was read.

| Item | Outcome | Evidence |
|---|---|---|
| Sequencer g2long_seq2 | ended normally 2026-11-23 08:23 (all released); new g2long_seq3 for FK, FN4 | `$S/g2long_seq2/log`, `$S/g2long_seq3/` |
| R5 ES-1L16 | DONE at 300 M; H3 HOLDS (1.99e-4 against 2.28e-4) | D-20261124-131138-0b8ffc5, judge_long.png |
| FV4 V-1L4 | DONE; P1, P3 (description), P4 hold; P2 REFUTED (offset -8e-3, no mesh order) | D-20261124-131149-9f0166d, judge_conv.png |
| FK, FE4, FF4 | cut by preemptions, closed FAILED by their caps; resumed from the newest restart, pending | chain events.log |
| Exterior constraints (XC) | bounded in every long run; near-hole level set by the shared coarse levels; dust residual looks like particle noise | D-20261124-134211-c6fce88, xc_plane.png |
| Finder test (FP, FP-ext) | running at the pause; the run log points to the finder's stopping rule as the cause of the vacuum plateaus | D-20261124-130935-fdca920, -140606-286a302; entry 13 |
| Removal records of preempted segments | duplicated after a resumption (FF4: 12582); fluxio.drop_overlaps removes them | commit fdca9208 |

What I could not confirm: FP and FP-ext (not judged at the pause); FE4, FF4, FK, FN4 (on the cards).

## 16. Lead's decisions of batch 11

1. Resume cut chains from their newest restart (task text, 2026-11-24) rather than repeat them; raise
   MAX_SEGMENTS in chain/config.sh because preemptions consume segments.
2. Queue the particle-number member 4N (FN4) now; N/4 (FNQ) and the M/16 growth member (FL16) wait for card
   allotment (request to orch): G2 had 4.29 card-hours left.
3. Treat the production finder's plateaus as the finder's until FP is judged; quote N both ways.
4. drift_controls tools committed as work in progress (decision 0030 item 1).

## 17. Lead session of batch 11b (2026-11-24 09:23 PST on, Opus; resumed after the pause; decision 0032)

No helper packages. This session closed the two processor runs left running at the pause and judged
them from their registered outputs against the predictions of g2long entries 10 and 11 (written before
the runs; the raw log had been seen at the pause, so FP2, FP3 and FP-ext (ii) are confirmations, not
blind tests). The cards are held by another user's priority jobs (decision 0032 item 2): no card run
moved since 06:19.

| Item | Outcome | Evidence |
|---|---|---|
| FP, FP-ext closed | completed, exit 0 (84 and 24 probes) | D-20261124-130935-fdca920, -140606-286a302 |
| FP1 | HOLDS: h0 reproduces every run's mass within 3.6e-6 at 29 dumps | fp_analyse.json, D-20261124-172508-c847ee4 |
| FP2, FP3 (cause C1) | HOLD: converged-finder vacuum drift 1.8e-5 (M/8, 100-500 M), 3.9e-6 (M/16); the 1.2e-4 plateaus are the finder's | fp_analyse.png panels (a), (b) (read) |
| FP4 | REFUTED: converged-finder offset -8.9e-3, +1.18e-3, -1.8e-5 over M/4, M/8, M/16 (sign change) | panel (d) (read) |
| FP5 | HOLDS: tight null difference <= 6.5e-5 (M/8), <= 3.7e-5 (M/16) | panel (c) (read) |
| FP-ext | (i) HOLDS; (ii) missed its 5e-5 bound (7.3e-5 at 400 M), not refuted | panel (c) |
| Not predicted | read in entry 14 as a step by 150 M, halving at M/16; withdrawn after test FE: a dip of the bubble's mass at 100 M (4.2e-5 M/8, 5.8e-5 M/16) | entries 14, 17 |
| Test FE (early dumps, predictions entry 16) | FE1, FE2 missed their bounds, not refuted; FE3 holds | D-20261124-173137-f358715, fe_analyse D-20261124-175356-0f40f1a, fe_analyse.png (read) |
| Figure defect fixed | legend of panel (a) over the data, clipped title of (d): rerun with layout only, JSON byte-identical | commit c847ee4a |
| Ladder schematic | registered, read | D-20261124-172838-3a30e48 |
| Slice mosaic | read again (lapse and particle energy, four zooms) | D-20261124-134644-2389227 |

What I could not confirm: anything on the cards (FK, FE4, FF4, FN4 and the newly registered FNQ, FL16).
What is wrong and stays on record: FP4 (no mesh order of the offset), FP-ext (ii) bound.

## 18. Lead's decisions of batch 11b

1. Register FNQ and FL16 under decision 0032 item 3 (caps 3.0 and 5.0; G2 had 11.73 card-hours left),
   held behind FK and FN4 in the running sequencer.
2. Restart cadence of decision 0032 item 2 through the chains' EXTRA_ARGS (output2/dt = 25 M for FK, FN4,
   FNQ; 12.5 M for FL16), keeping the registered inputs as smoke-tested; FE4 and FF4 (M/4, ~6 min per 50 M)
   unchanged.
3. Measure the null test and its floor with the converged finder on dumps (processors), and keep the
   production finder in the card inputs for comparability with their parents.
4. Post the finder's stopping rule to core as an interface-text request, with an optional source item.

## 19. Lead session of batch 17 (2026-11-25 03:46 PST on, Opus; analysis round, decision 0038)

No helper packages. The card queue ran overnight: FK (q0008) and FN4 (q0009) reached tlim, FF4 and FE4 had
reached it on 2026-11-24, FNQ (q0010) is running, FL16 (q0011) waits. Every reading below is a registered
run of this session against predictions written before the card runs (g2long entries 6, 10, 12, 15); the
two new tools were run once on the data as smoke tests before their registered runs (entry 18 says so).

| Item | Outcome | Evidence |
|---|---|---|
| FK closed | completed, 2.70 card-hours (sacct, 11 jobs); by hand: nrpic-run refuses manifests with `continuations` | D-20261123-022725-a553496, tools/close_by_hand.py |
| P7 | HOLDS: FK = ES-FL to 1.8e-6 up to 219 M | fk_compare D-20261125-115637-7ee26c1, fk_compare.png (read) |
| P8 | HOLDS: all 119848 dust removals by reason 3 | same |
| P9 (mechanism) | HOLDS: FK's late (iii) medians 0.16-0.24 per cent (ES-FL 0.6), D3 after 220 M 2.88e-3 < 3e-3: the step is the end of horizon excision | same |
| P10 | HOLDS: M_FK(399.5) 3.6e-4 below 1.4920 | same |
| P11 | FAILED: 2.70 card-hours against 1.8-2.4 | manifest |
| G for FK | HOLDS (50 bins, max 0.249 per cent; D2 all 760) | esf_criteria D-20261125-115647-fd2f3f7 (read) |
| Not predicted | FK D4: 29.5 per cent removed before the exact crossing (ES-FL 0.23) [TO VERIFY] | panel (d) |
| FF4 closed | completed, 1.34 card-hours | D-20261123-022727-1c17e73 |
| P12 | HOLDS with the M/4 control V-1L4; FAILED with V-1L (D2 207/480); control chosen after the first reading | D-20261125-121123-143a007 (read), D-20261125-121034-8f82998 |
| P13 | FAILED as written (M/4 t = 0 finder mass 1.0330); switch at 225.0 M holds | same |
| P14 | HOLDS: 1.34 | manifest |
| FN4 / FNQ (partial) | N2, N3 hold for FN4 (read whole two minutes after its chain ended, before its close); Q2 holds at 100 M; FNQ cut at 125 M | np_partial D-20261125-115729-011d028, np_partial.png (read) |
| FE4 closed; P5 | REFUTED: at M/4 the null difference grows to 4.6e-3 by 300 M (M/8, M/16: 2e-4); P6 failed narrowly (0.83 card-hours, 0.5-0.8) | judge_conv D-20261125-122227-3eb563a, judge_conv.png (read) |
| FN4 closed (3.19 card-hours); N1, N4, XN | HOLD: G 50 bins max 0.239 per cent, D2 all 760; XN ratios 0.43-0.49 (N^-1/2) | esf_criteria D-20261125-122827-c5735f8, xc_plane D-20261125-122849-43db157 (read) |
| Relaxed lapse per G2 item | no G2 item uses it; none could be judged at its bound with the mitigation beyond ~100 M; controls named | stage/G2/OPEN.md section 2 |

What I could not confirm: FNQ, FL16 (on the cards); FN4's region-sphere norms (not read). What is wrong and stays on record: P5 (null test fails at
M/4), P6, P11, P13, P12's failure with the M/8 control, FF4's D3 at early times, FK's D4 timing.

## 20. Lead's decisions of batch 17

1. Close chain manifests that carry `continuations` with tools/close_by_hand.py (nrpic-run's own chain-close
   code; manifest committed path-limited by the lead) and ask orch whether nrpic-run finish should accept the
   field (outbox).
2. Judge each mesh member of the growth against the vacuum control of the same mesh (V-1L4 for M/4, V-1L for
   M/8, V-1L16 for M/16); record the M/8-control reading beside it. The growth's mesh order is read with a
   reference time after the t = 0 transient (L3: 20 M).
3. Keep q0010 (FNQ) and q0011 (FL16); add no queue entry: everything else missing for G2 is processor and
   writing work (OPEN.md section 1).
4. G2 stays on plain 1+log; `lapse_leak_hole` is a G3 matter, with the mitigated vacuum control beside it.

## 21. Lead session of batch 20 (2026-11-25 07:54 PST on, Opus; processors only)

No helper package finished since batch 17; nothing stranded in the worktree (git status clean after the
merge of main). The lead's own readings, predictions first (g2long entry 23, committed acf204b81 before any
of the runs), outcomes in entry 24, each figure looked at:
- H, decision 0040 item 3 (horizon status). No D input sets `<fastflow> diagnostics` and no status file
  exists: every D run was made without the diagnostics. Recheck by the failure signature that the source
  fixes (NaN until a surface is accepted in a process, else a bit-identical repeat; fastflow.cpp:228-231,
  455-474, 777, 915-935, read by the lead): CONFIRMED that no G2 number rests on a failed search (none after
  20 M in 13 summaries; the V-1L/V-1L16 plateaus are found surfaces; N unchanged at 2.28e-4, 1.99e-4,
  4.57e-3; no removal reads a failed line); the FP/FP-ext tight re-searches are found (36 probes; four
  match core's status-file run bit for bit). NOT CONFIRMED by a status file for the production runs
  themselves: the signature argument stands in for it [VERIFIED by reading, not by a run with the
  diagnostics].
- R, FN4/FNQ region norms: CONFIRMED particle noise on [1.2 r_AH, 30 M] (ratio 3.4-4.4 for 16x particles);
  R1 failed as written on one NaN (empty horizon sphere at t = 0), harmless.
- T, D4: CONFIRMED that FK and ES-FL are identical before 219 M and that FK's early removals all lie after
  235 M; NOT explained why excision then removes dust up to 0.36-0.66 M of proper time before the exact
  LTB crossing, nor why the onset is earlier at 4N ([TO VERIFY]; no criterion depends on it).
- C6: rerun_g2.py written and tested on one analysis (byte-identical json).
- FNQ (q0010) has not ended (353 M of 400; job 5293 pending): not closed (task item 5 waits).

## 22. Lead's decisions of batch 20

1. Ruling 0039 item 4: the mesh leg of the null test is stated with two members (M/8, M/16) and no order;
   no M/12 member is queued (no error above the converged-finder floor for a third member to order; up to
   4 card-hours in a tight week; cards held). C2's text says so.
2. Beside every horizon number of the package: "run without `<fastflow> diagnostics`; failed searches by
   signature: none after 20 M (hz_check D-20261125-160142-b1c51b5)". New D inputs set `<fastflow>
   diagnostics = true`; with core-v0.8 also `polish_iterations_0 = 100`, `mass_tol_0 = 1e-5` (core's
   finder_stop.md) once core has judged its card check (q0049).
3. No new queue entry; q0010 (FNQ) and q0011 (FL16) kept.

## 23. Lead session of batch 25 (2026-11-25 21:40 PST on, Opus; analysis round and G2 package)

No helper package ended; the two card runs of the queue did (q0010 FNQ, q0011 FL16). Everything below was
recomputed from the registered outputs by registered readers of this session, each figure looked at, each
result compared with the prediction written before the run (g2long entries 10, 15; entry 25 committed in
1fdfb6719 before any reading).

| Item | Prediction | Outcome | Run | Figure |
|---|---|---|---|---|
| FNQ close | - | completed, 1.90 card-hours, 51.1 GB checksummed | D-20261124-172725-2f426b6 | - |
| Q1 criterion G at N/4 | every bin within 2 per cent | CONFIRMED: max 0.290 per cent, D2 at 760 samples | D-20261126-054616-a13a888 | esf_criteria.png |
| Q2 removed m E_K vs N | within 3 per cent | CONFIRMED: -0.86 to +0.49 per cent | D-20261126-054636-93618ee | np_partial.png |
| Q3 cost | 1.6-2.3 | CONFIRMED 1.90 | - | - |
| XQ plane norms N/4 over N | 1.4-2.9 | CONFIRMED 1.65-1.89 | D-20261126-054718-afa783e | xc_plane.png |
| FL16 close | - | completed, 3.66 card-hours, 85.9 GB checksummed | D-20261124-172745-72472ed | - |
| L1 finite, horizon every sample | - | CONFIRMED to 299.75 M | D-20261126-055158-30ae09c, D-20261126-055208-4e0fd0e | hz_check.png |
| L2 criterion G at M/16 | every bin within 1 per cent | CONFIRMED max 0.485, D2 at 1120 | D-20261126-055158-30ae09c | esf_criteria.png |
| L3 mesh ordering | fine < coarse at 100-300 M | HOLDS as written; M/4 outside the regime, so no order | D-20261126-055249-505b079 | conv3.png |
| L4 cost | 3.0-4.0 | CONFIRMED 3.66 | - | - |
| L5 A1 norm M/16 vs M/8 | >= 0.8 at one of two times | CONFIRMED 2.11, 1.08 | D-20261126-055159-6c40115 | xc_plane.png |
| C2a, C2b, C2c (entry 25) | ordered; <= 3e-3; no failed search after 20 M | CONFIRMED (4 of 4; 4.4e-4 max; none) | D-20261126-055249-505b079, D-20261126-055208-4e0fd0e | conv3.png, hz_check.png |

Wrong or not confirmed, on record (g2long entries 26-27): D3 fails at N/4 after ~220 M (not predicted, no
bound in G); conv3's first registered reading D-20261126-055207-0137c53 dropped the 300 M mesh time (the
reader skipped a named time 1 M past the common end); fixed after that reading and labelled post hoc; the
particle reader np_partial.py still labels a whole reading "PARTIAL" (label only; chain_done is true for all
three runs and the numbers are those of the ended runs).

## 24. Lead's decisions of batch 25

1. G2 package assembled: every CHECKLIST item PASS except C17; OPEN.md lists only failures on record with
   their rulings (P5 and ruling 0039 item 4; mesh leg of the null test, ruling 0041 item 4) and the fresh
   verifier. G2 is offered for the fresh-context verifier and the gate review (decision 0016 item 4).
2. Item C2 is stated as: particle number three members ordered with N^-1/2 noise; mesh of the growth two
   members in the regime agreeing to <= 4.4e-4, M/4 labelled outside the regime, no order claimed; null-test
   mesh leg two members, no order; boundary three face distances; gauge plain 1+log only.
3. No new card run is queued for G2. Core's guard test (ah_exc_max_growth) stays a G3 item after core's
   card check q0049; new inputs set `<fastflow> diagnostics = true` (ruling 0041 item 5).
4. stage verify ran with --no-checksums (PASS); the full checksum pass (--full) is left for the session
   before the gate review, as harness/RULES.md asks.

## 25. Lead session of batch 34 (2026-11-27 15:21 PST on, Opus): G2 signed, corrections, G3 scope, guard test

Gate G2 is SIGNED, pass with reservations (coord/GATES.md row of 2026-11-26, tag
`stage/D-bh-dress/G2-pass-20261126`, decision 0045 item 1). No helper package finished since batch 25; this
section records the lead's own work.

The eight corrections of `stage/G2/GATE_REVIEW.md` section 6, each checked against the artefact it names:
- a. CHECKLIST C17 set to PASS with VERIFIER.md and GATE_REVIEW.md (commit 5720e3cc1); collect, verify and
  report rerun on the final package (below).
- b. LADDER.md rows that read PENDING in batch 11b now carry the outcomes from g2long entries 19-22, 26, 27
  (FE4's P5 failed, FF4's P12-P14, FK's P7-P11, FN4/FNQ/FL16); the ladder schematic redrawn from
  `g2long/tools/schem_ladder.py` (run D-20261127-234652-5b9af43, looked at: every rung green except the
  bounded constraints).
- c. Ledger row of FF4 (note/scripts/ledger.py): "480 (control held at its last value after 299M; 280
  samples within the control)". Checked first that run D-20261125-121123-143a007 reads the control
  v1l4.horizon_summary_0.txt of V-1L4 (ends 299 M) and reports n = 480 [VERIFIED]; the 280 is the
  verifier's number (section 4.2), not recomputed here.
- d. CHECKLIST C2 and note section V C quote the envelope of the M/16 - M/8 difference (at most 1.0e-3,
  mean +5.8e-4 over 250-299 M, not removed by the own controls) beside the three samples; "a few parts in a
  hundred thousand" is gone.
- e. Note section V A: "at most 7.3e-5 at M/8 (100-500 M) and 5.5e-5 at M/16 (100-300 M)" (CHECKLIST C7,
  FP5 of run D-20261124-172508-c847ee4).
- f. Note section VI rewritten to the state after G2 (the long runs are done; what G3 must answer) and the
  summary's last sentence (the boundary question was answered at G2); "Long runs are on the cards" and
  "ends where the boundary signal arrives" removed.
- g. The verifier's decided cause of the early removals (shells ahead of exact LTB, VERIFIED for tracers,
  JUDGEMENT for dust) entered in OPEN.md, CHECKLIST C8, RISKS R28 and note section V D.
- h. FK's D3 wording in CHECKLIST C8 and LADDER: "no violation; smallest value -1.4e-4 inside the allowance
  -3e-4". The original wording stays in g2long entry 19 (journals are not rewritten).
Note v3.1: build D-20261127-234333-5720e3c (15 of 15 scripts), compiled, 24 pages, checker with --compile:
0 undefined references, 0 undefined citations, 0 overfull boxes; pages 12-13 read after the change.

Not done by me and not claimed: the 280-sample figure of correction c and the shell-lead numbers of g are
the verifier's, carried with its locator. One reading of my own that bears on G3, labelled [JUDGEMENT, TO
VERIFY]: FL16's level 8 covers only +-3 M (64 blocks of 1.5 M, g2long entry 4 block counts), and ES-FL's
smallest horizon radius passes 3.2 M at 219.5 M, so FL16's horizon probably left its M/16 level near 200 M;
the late M/16 - M/8 offset may come from it. Not a G2 correction (no G2 claim rests on M/16 after 200 M
beyond the band of G), but SCOPE_G3 builds its members so that it cannot recur.

G3 scope: `scope/SCOPE_G3.md` written before any production run (commits e92904aed, acb5f7202), for the
independent review of decision 0045 item 2. No production run is queued.

Guard test EG8 (scouting): predictions committed first (excguard entry 1, 6111945a6); processor smoke test
S1 held (D-20261127-232517-6111945); queued at priority 2 (q0085, run D-20261127-233719-db5be88, job 5536,
pending at 15:48 PST). Card-hours used by this session so far: 0 (the job had not started).

## 26. Lead session of batch 35 (2026-11-27 17:56 PST on, Opus): the G3 scope review checked, the scope amended

Package reviewed: `g3/scope_review/` (helper of batch 34, fresh context; SCOPE_REVIEW.md, JOURNAL entries
1-7, five registered processor runs). Checked from its artefacts with code of my own (`g3/amend/tools/
check_review.py`, run D-20261128-020346-c4079e9, predictions committed first in c4079e991, figure
`check_review.png` looked at; the reviewer's `dress_model.png` and `g3g3_power.png` looked at as well).

| Finding | Confirmed | How (my numbers) | What the track does |
|---|---|---|---|
| B1 G-16 3648 blocks (8.0x), G-12 not a refinement (finest +-4 M), smoke rule rejects every M/16 deck | yes, all three | `athena -m` on decks written by my tool from EG8's deck: 3648, 2176 (+-4 M); my 2:1 derivation 7 x 448 + 512 = 3648 and 7 x 56 + 64 = 456; t = 0 masses 0.99152 (M/8) and 0.99981 (M/16) | A1: uniform family G-8/G-12u/G-16u (456 blocks of 24/36/48 cells, finest +-6 M at 1/8, 1/12, 1/16 [VERIFIED]); smoke rule rewritten; card timing runs before production; t_16 rule within 20 card-hours |
| B2 tracer-label clock fails by construction | yes | FK at 200 M: nearest-label clock off by up to 12.5 M (R0 24-25 M); own proper times of a 1 M label bin spread 6.2 M | A2: per-particle clock, dtau_p statistic, D1* fixed on G2 snapshots before any G3 card hour, D3 a figure |
| B3 G3-G3 passes a true signal with 0.11-0.15; G3-G2 ordering does not measure convergence | yes, and extended | independent Monte Carlo: 0.14 (p = 2), 0.10 (p = 1) at 5.8e-4; the reviewer's amended form 0.997 (white) but 0.0 with a 10 M noise correlation time; FL16 - FK -1.1e-3 to -2.0e-3 (size of the reviewer's e_8 - e_16 = +1.48e-3) | A3: G3-G2 with the finder's vacuum offset at matched horizon resolution; G3-G3 a criterion only if its power on measured noise is at least 0.8, otherwise a reported ratio; V-8 withdrawn |
| S1 16N cost | in part | matched pair FK/FN4 gives 5.2 card-hours (particle part 0.163 per N), the review 7.6 | A4: both quoted, cap 8 |
| S2-S7 | accepted on reading (not recomputed) | - | A4 wordings |
| S8 guard factor 10 untested | accepted | - | A1: factor 10 withdrawn; FK's remedy (guard 6.4 M, verified to 399.5 M) in every member |

What I could not confirm: the reviewer's split of e_8 - e_16 into lead (3e-4), vacuum offset (1.19e-3) and a
nonzero e_inf (B3) is arithmetic on registered numbers I did not recompute; the noise numbers (sd 3.9e-4,
correlation 0.83) are the reviewer's, and my high-pass check of them (difference sd 2.24e-4 against the
model's 2.27e-4) tests only their short-time part. Failed predictions of mine: g12s (blocks of 18) has 2472
blocks over +-3 M, not 3648 over +-6 M (I ignored the alignment of level 7 to level-6 blocks); C3's "spread
above 2 M in every bin inside 30 M" fails at 27-30 M (0.4-1.1 M).

Scope amended by dated amendments A1-A5 (`scope/SCOPE_G3.md` section 11, commit acee85249), predictions for
the amended criteria in `g3/amend/JOURNAL.md` entry 4, committed and pushed before any production entry.
