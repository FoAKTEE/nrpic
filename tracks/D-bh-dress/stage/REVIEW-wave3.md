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
