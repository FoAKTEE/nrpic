# Gate review: B-emd-gw G2 (independent reviewer, batch 38)

Reviewer session of batch 38, 2026-11-27 (PST evening). Decision 0019 item 3. I produced none
of this work. Tag check: `git tag -l 'stage/B-emd-gw/*'` lists G0-pass-20261119 and
G1-pass-20261121 only; G2 is not signed. This file is written in two commits: the predictions
of my own check (section 2) first, before the check ran (7c4aa6463); the rest afterwards.
Branch `track/B-emd-gw` reviewed at ae31c146f (main merged, decision 0049 item 7 included).

Read before judging: CLAUDE.md; `coord/CHARTER.md` to "Owners" and sheet 9.5; brief lines
674-686 (gate table); decisions 0010, 0013, 0016-0019, 0027, 0039, 0042, 0043, 0046-0049;
`coord/GATES.md` (B's G1 row and the G2 rows of C, D, E, A for precedent); the package
`stage/G2/` (STAGE_REPORT, CHECKLIST, EVIDENCE, OPEN, REPRODUCE, VERIFIER, VERIFY_RESULTS);
`scope/SCOPE.md` whole (sections 6, 7 and 9 bear on G2); `population/JOURNAL.md` entries
2026-11-27 15:24 to 19:12; note sections VI and VII and the ledger rows of `note/tables/ledger.tex`;
`first_source/README.md` round 3; `flrw_conv/README.md` "Verdict".

Opened as evidence: the manifests of the population legs (B-20261123-014847-f295ab4,
-20261124-210431-6bf48af, -20261124-223926-33194d9 with its continuation -20261125-221742-5100a22,
-20261126-105021-6343c13, -20261128-030420-33ccdca) and the deck `population/inputs/pop_gr_run.athinput`
(lines 52-54: `shift_Gamma = 0.0`); the raw line and history files of all seventeen `flrw_conv` runs
(my run, section 2); the analysis files of the base, gauge and particle legs; the figures
`pop_legs.png` (B-20261127-232236-7ab7aa2), `c3_mesh_pair.png` (B-20261127-232628-1361e3b),
`series7.png` (B-20261126-230056-294b265), `flrw_conv/figs/fig_b_conv.png`,
`population/figs/pop_gr_mosaic.png`, `note/figures/schem_ladder.png`,
`note/figures/schem_architecture_g2.png` and my own `review_check.png`, each looked at; the source
locator of the shearing-dust references, `kb-data/raw/arxiv/2003.08014/v2/src/draft.tex:360`; the
writer of the line records, `athenak/src/particles/nrpic_io.cpp` (NrpicWriteLine).

## 1. The stage check

**My rerun** (`harness/bin/nrpic-stage verify B-emd-gw G2`, 2026-11-28T03:20:06Z, export of
ae31c146f; copy kept in `scratch/B-emd-gw/tmp/gate_review_g2/VERIFY_RESULTS_reviewer_20261128T032006Z.md`;
the lead's files restored in the stage directory afterwards): FAIL on one check, `runs`, for one run
only: the initial data B-20261128-030420-33ccdca of the pending 256^3 member at eight per cell,
status `running` (I saw its process, `make_ic.py --n 256 --ppc 2`, alive on one core). Every other
check passes: rerun 15 of 15 scripts, compare 30 of 30 regenerated files within tolerance,
regenerate 30 of 30, style, figures (6 schematics, 9 data figures), note PDF newer than its source.
Checksums WARN only because they come from the cache. The lead's `--full` pass (13883 files,
1166.91 GB read again, 0 failed checks) is committed in 397511402. The one FAIL is by design and is
not a defect of the package; it clears when that run is closed with `nrpic-run finish`.

## 2. Reviewer's own check R (predictions, written before the run)

Script `stage/G2/gate_review/review_check.py` (my own readers; the line-record format read from
`athenak/src/particles/nrpic_io.cpp` NrpicWriteLine, the history columns from their headers; of
the lead's code only the definition of the band power, `compare_legs.py` band_rms2, is taken,
so that my number is the same quantity). It covers what the fresh verifier did not recompute
(VERIFIER.md section 4, "cannot claim" 6): the track's own G2 criterion C7 (sub-percent scale
factor and growth rate, converging in particle number and mesh) and the particle-number leg of
the band strain; and it tabulates the gauge leg against a.

Seen before writing these predictions: the lead's numbers in `flrw_conv/README.md` ("Verdict"),
CHECKLIST.md and VERIFIER.md; the decks of the population legs (the particle leg at eight per
cell, B-20261124-223926-33194d9 and its continuation, runs `pop_gr_run.athinput` with
`shift_Gamma = 0.0`: zero shift); the list of dump epochs with spectra in the three analysis
files. No number of my own was computed before this commit.

- RA1 (C7, growth rate, sub-percent). In every run of leg B (16, 32, 64, 128 cells at one
  particle per cell; 32 cells at 8 and 27 per cell) the largest |f - f_ref| for a >= 3 is below
  1e-3. The prediction fails between 1e-3 and 1e-2; the criterion itself fails at 1e-2 or above.
- RA2 (C7, mesh). The median |f - f_ref| for a >= 3 falls at every halving of the spacing,
  16 -> 32 -> 64 -> 128, by a factor of at least 4 from 16 to 32 and from 32 to 64. Refuted if
  any halving leaves it equal or larger.
- RA3 (C7, particle number). At 32 cells the medians at 8 and 27 per cell are at most 1.5 times
  the median at one per cell. Refuted above 1.5.
- RA4 (agreement with the lead). My medians (window 0.5 in ln a, a least-squares fit of the
  wave, normalised by the line mean) are within a factor 3 of the lead's 6.7e-5, 4.9e-6, 3.0e-7
  (16, 32, 64 cells) and within a factor 10 of 2.8e-8 (128 cells). Refuted outside.
- RB1 (C7, scale factor). Leg F: the largest relative error of alpha_min, alpha_max, the proper
  volume and the mean K against a(t) = (1 + t/2)^2 is below 1e-6 for the lattices at rest (a0) at
  16, 32, 64 cells, and below 1e-4 with position noise (a1, a2). The criterion fails at 1e-2.
- RB2 (C7, scale factor, mesh). At rest the error falls from 32 to 64 cells by at least 8.
- RC1 (C2, particle-number leg). Band rms |k| <= 8 k_f (corrected spectra), 128^3 zero shift,
  eight over one particle per cell, within 3e-3 of one at every common dump (a = 56 to 132).
  Refuted outside 1e-2.
- RD1 (C2, gauge leg). The same band rms, Gamma driver over zero shift at 128^3, within 5 per
  cent of one at every dump with a <= 36. Refuted if it leaves 0.95-1.05 at some a <= 36.

### Outcomes (run B-20261128-032405-7c4aa64, completed, exit 0; `review_check.png` looked at)

Every prediction holds. [VERIFIED by this run]

| Prediction | Result | Verdict |
|---|---|---|
| RA1 | largest |f - f_ref| for a >= 3: 7.85e-5 (16 cells), 5.89e-6 (32), 6.65e-7 (64), 4.26e-7 (128); 1.78e-6, 2.09e-6 (32 cells, 8 and 27 per cell) | HOLDS (two orders below the sub-percent bar) |
| RA2 | medians 6.75e-5, 4.81e-6, 2.75e-7, 2.87e-8: factors 14.0, 17.5, 9.6 per halving | HOLDS (about fourth order to 64 cells, 9.6 from 64 to 128) |
| RA3 | 32 cells: 1.36e-6 (8 per cell), 1.69e-6 (27) against 4.81e-6 (1 per cell): 0.28 and 0.35 times | HOLDS |
| RA4 | mine against the lead's: 6.75e-5 / 6.7e-5, 4.81e-6 / 4.9e-6, 2.75e-7 / 3.0e-7, 2.87e-8 / 2.8e-8 | HOLDS, within 10 per cent at every mesh with a different estimator |
| RB1 | at rest 3.81e-7 (16), 1.86e-7 (32, equal at 1, 8, 27 per cell), 1.23e-8 (64); with noise 5.30e-5 (16, a2), 3.18e-6 and 3.19e-5 (32, a1 and a2), 1.04e-5 and 6.17e-6 (32, a2 at 8 and 27 per cell), 1.70e-5 (64, a2) | HOLDS; the lead's 3.8e-7 and 5.3e-5 reproduced to their digits |
| RB2 | 1.86e-7 / 1.23e-8 = 15.1 | HOLDS (the lead's 15.1) |
| RC1 | 8 over 1 per cell, corrected: 1.0000 at a = 56-72, 0.9999 at 81-90, 0.9997 at 100, 0.9996 at 110, 0.9998 at 121, 0.9980 at 132 (raw within 7e-4) | HOLDS (largest departure 2.0e-3, at a = 132) |
| RD1 | Gamma driver over zero shift, corrected: 1.0000 to 0.9981 for a = 2.3 to 36 | HOLDS |

Beyond what was predicted (same run): the gauge ratio continues 0.9929, 0.9836, 0.9678, 0.9503,
0.9318, 0.9052, 0.8652, 0.8026, 0.7284, 0.6827, 0.6426 at a = 42, 49, 56, 64, 72, 81, 90, 100,
110, 121, 132. The two gauges agree on the band strain within 1.6 per cent to a = 49, differ by
5 per cent at a = 64, 20 per cent at a = 100 (the verifier's 0.803) and 36 per cent at a = 132.
The lead's file of the earlier particle-leg comparison (B-20261125-121830-9ecb59c, read, not
recomputed) gives 8 over 1 per cell = 1.0000 at every dump a = 4 to 49 as well.

Figure defect of mine (cosmetic): the log-axis tick labels of the top-right panel overlap at 30-40.

## 3. Criteria

Checklist items C1-C20 (generated from charter 9.2 and 9.5, brief 13.3-13.4 and decision 0013).

| # | Criterion | Verdict | Evidence I opened, and why |
|---|---|---|---|
| C1 | Code paths pass their tests of §10 | PASS WITH RESERVATION | Rows held by B (charter 10): FLRW dust and linear growth pass (my RA, RB); linear waves (Table V, reproduced to every digit by the verifier; G1 signed); plane-symmetric pancake (G1, note Sec. IV C: null at rounding through crossing, departure the same at 32, 64, 96 cells; the G2 C1 text does not name this row and should); multi-code row as ruled by 0013 (C9). Szekeres: optional for B in its scope (SCOPE.md:210), not run. Reservations: (i) L2 of the shearing dust fails as run (-0.822, -0.831, -0.839 at N_y = 64, 128, 256, moving away from CosmoGRaPH's -0.8183 +- 0.0004, draft.tex:360); (ii) its cause, stream crossing before the rays arrive, is inferred, not measured (no L2 snapshot after t = 0); (iii) the source says the three codes that report a number at H L = 4 all use particles (draft.tex:360), and CosmoGRaPH quotes +-0.0004, so the note's sentence "Stream crossing, which a particle code follows and a fluid cannot, is therefore the likely cause" (main.tex:328) does not explain why this particle code does not converge where another particle code reports a converged value; (iv) the series-7 constraint floor (Mr 1.66e-4 to 1.64e-4 from N_y = 128 to 256) falls neither with the mesh nor is it shown to fall with particles: by decision 0039 item 2(c) it is a defect to be explained. Series 7 itself converges (Delta 0.053749, 0.053800, 0.053821; figure looked at; verifier reproduced). Ruling 0046 item 2(a) asked for exactly that run before G2, and it is delivered. |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | PASS WITH RESERVATION, restricted as stated | For the observable the track reads, the band strain |k| <= 8 k_f of the population box: **all three legs agree within 1.6 per cent for a <= 49** (mesh, Gamma driver, 256^3 over 128^3: 0.999, 0.999, 1.004 at a = 9, 25, 49; particle number, zero shift, 8 over 1 per cell: 1.0000 at a = 4-49; gauge, Gamma driver over zero shift: 1.0000-0.9836 at a = 2.3-49, my RD). **For a > 50 the gauge leg fails as worded**: 0.950 at a = 64, 0.803 at 100, 0.643 at 132; this is the identified dependence on the gauge recorded under decision 0049 item 1, not a convergence. The mesh leg holds there in the Gamma-driver gauge (within 1.1 per cent to a = 64, 2.8 per cent to 132; verifier, pop_legs.png looked at), **but the particle-number leg exists only in the zero-shift gauge** (deck lines 52-54 of every eight-per-cell member; my RC: within 2.0e-3 to a = 132). The checklist's "Three-way for the quantity the track reads (band strain, Gamma-driver gauge): particle number to 2e-3 (Q1)" is therefore wrong as written: no run at eight per cell in the Gamma-driver gauge exists. Further legs: FLRW 16-128 cells and 1-27 per cell (my RA, RB); the first source after crossing, 32/64/128 cells and 1/8/27 per cell (G1, first_source round 3). Failed on record and confirmed: the halo catalogue at one particle per cell does not converge in the mesh (15 against 31 halos at a = 121, outside 2 sqrt(N) + 2; verifier reproduced; pop_legs.png looked at); L2 (C1). |
| C3 | Constraints behave | PASS WITH RESERVATION | At eight per cell the mean constraints fall with the spacing (64/128: Hamiltonian 1.64-2.34 after a = 36, momentum 1.71-2.16 after a = 49; verifier reproduced to 3 digits; c3_mesh_pair.png looked at) and they fall with particle number at 128^3 (momentum 2.9 times, Hamiltonian 1.6 times at a = 141). By decision 0039 item 2(c) this is not a violation that falls with neither. Reservations: (i) at one particle per cell, the production sampling of every 256^3 member so far, they do not fall with the mesh (1.05-1.4, M4, GM4 failed on record); (ii) one mesh pair at eight per cell, at coarser spacing than the one-per-cell pair, and zero shift only; (iii) the absolute late level is large: mean relative momentum constraint 0.18-0.20 at a = 141 at one per cell in both gauges (pop_legs.png, lower right), about 0.07 at eight per cell; every late-time quantity sits on that; (iv) the series-7 floor (C1 iv); (v) FLRW leg B: largest Hr rises with the mesh (3e-9, 1.3e-8, 6.2e-8), cause untested (R20), harmless in size. |
| C4 | A first minimal full-GR kinetic run | PASS | Manifests completed: B-20261123-014847-f295ab4 (128^3, 2.1e6 particles, to a = 143), the Gamma-driver legs at 128^3 and 256^3, the flrw_conv card runs. |
| C5 | Verification report | PASS WITH RESERVATION | STAGE_REPORT, EVIDENCE, OPEN present. EVIDENCE.md's title still says "state of batch 11" and its table ends at batch 34 (the verifier's runs, pair_ratio B-20261128-030556-5ef9294, mem_fit B-20261128-030350-19295a4 and the pending initial data are missing). |
| C6 | Reproducibility package | PASS WITH RESERVATION | REPRODUCE.md rows checked against manifests for series 7, GM2/GM3, q0070, C3; rows of batch 37 missing (as C5). Card runs with deposition do not repeat byte for byte (CLAUDE.md); the stage rerun regenerates every figure from committed scripts. |
| C7 | Scale-factor error and linear growth rate sub-percent, converging in particle number and mesh | PASS | My RA1-RA4, RB1-RB2 (section 2), from the raw line and history files with my own readers: growth-rate error at most 7.9e-5, falling about fourth order to 64 cells; scale-factor error at most 3.8e-7 at rest and 5.3e-5 with one-percent noise; particle number lowers both. fig_b_conv.png looked at and consistent. This is the track sheet's own G2 criterion and the one the fresh verifier did not recompute. Reservation only of scope: it is a background and linear test; it says nothing about the nonlinear regime. |
| C8 | Agreement with gevolution in the weak-field regime | NA | Replaced by decision 0013 (C9). |
| C9 | Ruling 0013: shearing dust of 2003.08014 and full GR against the Newtonian mode | PASS WITH RESERVATION | Shearing dust S1-S4, M1, L1 within their bounds (lead; not recomputed by me or the verifier), L2 failed (C1). Full GR against the Newtonian mode with the same particles and equal masses: counts 108 and 98 against 106 at a = 121, ten largest within a median 2.6 and 1.2 per cent (verifier reproduced exactly); amplitude scaling S2, S3 (lead, not recomputed). N4 failed as written, cause found in a run that could have failed. Reservation: the halo-mass part of "GR against Newton" is at one particle per cell, where the catalogue does not converge in the mesh (C2), and masses differ by 10-17 per cent between gauges (R23). |
| C10 | Schematic: verification ladder | PASS WITH RESERVATION | schem_ladder.png looked at: legible, rungs with references. Stale: the top rung says the mesh, particle and gauge legs are "queued" and the full-GR rung says "stop at 2x amplitude"; both have run (the shifted 0.028 box reaches a = 141). |
| C11 | Convergence figures (particle number, mesh, gauge) | PASS WITH RESERVATION | pop_legs.png (B-20261127-232236-7ab7aa2), c3_mesh_pair.png, series7.png, fig_b_conv.png looked at. No package figure shows the gauge ratio against a beyond the single gauge-leg comparison; my review_check.png (lower right) does. |
| C12 | Constraint norms against time | PASS | fig_b_constraints, the constraint panels of pop_legs.png and c3_mesh_pair.png. |
| C13 | Multi-scale slice mosaic with zoom boxes | PASS | pop_gr_mosaic.png looked at: box, L/4 and L/16 zooms with boxes drawn, lapse, K and strain on the plane; K saturates in the core as the lead states. |
| C14 | Package documents | PASS | All present; `package` check PASS. |
| C15 | Data figures from registered outputs, one script each, looked at | PASS | fig-script, regenerate and compare PASS in my rerun. |
| C16 | Schematics: architecture and gate timeline | PASS | schem_architecture_g2.png looked at: classes by evidence, core-v0.7 named; the shearing-dust L2 box honestly red. |
| C17 | Working note with /paper-writing, checker passed | PASS WITH RESERVATION | Section VI read: every number is in Tables VII-VIII with a run id (I checked every data row of the ledger carries one; sample of prose numbers found there). Wording to correct: main.tex:318 does not say the particle leg is zero shift, and the summary's three-way reading inherits that; main.tex:328 on stream crossing (C1 iii); Section VII "Plan and open questions" (main.tex:340-342) is the G1 text (it lists particle-number convergence of the background as open, which C7 closed). |
| C18 | Fresh verifier | PASS | VERIFIER.md read whole: own readers tested on analytic cases, numbers the gate rests on reproduced to their digits, coverage stated honestly ("every number" not met as worded). My check adds C7 and the particle leg it left out. |
| C19 | Null results and failed runs on record | PASS | The journals carry M1, M4, GM4, GM2 Omega part, GM3, C3a early part, N4, GN1, X3, E2 and the rest; STAGE_REPORT lists 32 failed or stopped runs. I found no failed prediction recorded as held. |
| C20 | STATUS, JOURNAL, HANDOFF current | PASS | Rewritten in batch 37 (a92d32519); the pending run and its queue step are in HANDOFF. |

## 4. The track's own scope text against the checklist

The checklist carries the brief's G2 rows (C1-C6), the track sheet (C7, C8) and decision 0013 (C9).
It carries nothing from `scope/SCOPE.md`, nor did the G1 checklist. What the scope says about G2:

| Scope text (written at G0, 2026-11-15) | State |
|---|---|
| Section 6, first source, "numbers I propose for G1 to G3" (no gate named except G3 for the last): null at rounding; noise floor ten times below the eps = 0.3 signal; before crossing, linearity in eps to 1 per cent and the strain "within a truncation error that falls at second order between 64, 128 and 256 cells" | Null and linearity done at G1. The mesh clause is **not met**: before a ~ 60 the first-source mesh differences sit at about 1e-4 of the strain and do not fall with the mesh (first_source/README.md round 3, item 2), and no 256-cell member of the first source exists. |
| Section 6, after crossing, explicitly G3: rho_K and the TT spectrum converge to 10 per cent in particle number, mesh and **lapse condition** | G3. Note that the gauge leg of the package varied the shift, not the lapse; for the population no lapse variation exists. |
| Section 7, growth row: "G2 asks for sub-percent and convergence" | Met (C7). |
| Section 9, "Plan to G2 for the first and second sources [JUDGEMENT]": nulls at 64 and 128 cells at 1 and 8 per cell, eps scan at two amplitudes, the three-wave set, convergence at 256 cells for two points | A plan, not a criterion. The 256-cell points of the first source were not run; the population box, which the scope placed at G3 (section 3, last row), was brought forward and carries the G2 convergence instead. |

Reading [JUDGEMENT]: the scope assigns none of its section-6 numbers to G2, so I do not count them
as G2 criteria; the criterion in force is the charter's and decision 0013's, as for Track C
(decision 0048 item 1). But the mesh clause of section 6 is unassigned and unmet, and the G3 criterion
of section 6 names a lapse leg the package has not run. Both have to be placed by a dated amendment of
the scope before G3 production, not after the G3 data (the lesson of decisions 0047 and 0048).

## 5. Reservations of G1 and where they stand

| G1 reservation (coord/GATES.md) | State at G2 |
|---|---|
| Pipeline validated on single-mode linear waves only | Answered in part: the verifier's own projector on random TT fields (1.5e-16) and its raw recomputation of the population spectra (equal to the files to 1e-15); the band strain converges in the mesh. No analytic multi-mode nonlinear reference exists. |
| Baseline rests on an exact symmetry; energy constant at first order | Not revisited; superseded for comparisons by the Newtonian mode with the same particles. |
| Schematic predates core-v0.6 | Answered (C16). |
| Harness FAIL on runs until a chain ends | Same form again: one running initial-data run (section 1). |

## 6. Corrections the verifier asked for, and mine

The lead answered the verifier's a-e (REVIEW-wave3.md, batch 37; note v5): I find a (main.tex:322),
c (main.tex:308) and d (main.tex:328) in the note as asked; b in ledger row g2_pair; e as a dated
amendment of shear/SPEC.md. Owed by the lead before the stage report is regenerated (none changes a
verdict above):

1. C2 evidence and note main.tex:318 and Summary: say that the particle-number leg is zero shift,
   and that no eight-per-cell run in the Gamma-driver gauge exists; drop "Three-way for the quantity
   the track reads (band strain, Gamma-driver gauge)" or restrict it to a <= 49.
2. State the gauge dependence of the band strain as a function of a (within 1.6 per cent to
   a = 49, 5 per cent at 64, 20 at 100, 36 at 132; my run B-20261128-032405-7c4aa64) wherever the
   20 per cent at a = 100 is quoted alone.
3. main.tex:328: the reference codes at H L = 4 are particle codes (draft.tex:360); reword the cause.
4. Section VII of the note (G1 text), the ladder schematic's stale states, EVIDENCE.md's title and
   its missing batch-37 runs, REPRODUCE.md's batch-37 rows, C1's omission of the pancake row.

## 7. The pending member (256^3, eight per cell, Gamma driver)

What it decides, by the lead's predictions written before it (population/JOURNAL 2026-11-27 19:02):
K1 that the driven gauge survives resolved cores at eight per cell; K2 the particle-number leg of the
band strain at fixed mesh **in the gauge the strain is read in** (against q0060, within 2 per cent);
K3 whether the halo deficit at 256^3 is sampling.

Could its outcome change my verdict? **Yes, for C2 beyond a ~ 50, not for the gate as a whole.**
If K2 fails, the late-time band strain has no particle-number leg in its own gauge, and the mesh
agreement at one per cell (GM2) could be two meshes sharing a sampling bias; C2 would then be met
only for a <= 49, and every G3 strain statement after a ~ 50 would lack a verified capability. If K1
fails, the driven gauge, the only one that passes resolved cores, is not shown at the sampling G3
needs. K3 cannot change a verdict: the halo catalogue at one per cell is already failed on record; it
tells G3 whether eight per cell is enough. Nothing in C1, C3-C20 depends on the member. The 128^3
partner at eight per cell in the Gamma-driver gauge (0.85 card-hours, allowed by decision 0049
item 7, data B-20261124-135029-3fe13f6 exist, not queued as of 19:25 PST) answers K2's question at
128^3 within a day instead of three; it should run first.

## 8. Recommendation

**PASS WITH RESERVATIONS**, with the failures on record stated as failures and the three-way
statement restricted as below. The answer to "is it a verified capability for gravitational waves
from structure in an early matter era" is yes for what the gate can verify now, with an explicit
limit in time: the background and linear growth meet the track sheet's own criterion by two orders
(checked twice, by the lead and by my readers); linear tensor waves are reproduced to their digits
(verifier); the strain of the crossed-wave source converges in mesh and particle number through shell
crossing (G1); and the box-mode strain of a halo population converges in mesh, particle number and
gauge within 1.6 per cent up to a = 49, after halos have begun to form. Beyond a ~ 50 the same strain
converges in the mesh (Gamma driver) and in particle number (zero shift only) but depends on the shift
by 5 to 36 per cent: the late-time strain is a quantity of the chosen gauge, and the criterion's third
leg is not met as a convergence there. I do not reword that: C2 is met as worded for a <= 49 and fails
as worded for the gauge leg beyond. Precedent: D and E were signed with no gauge leg at all and C with
one that could hardly fail; B ran a gauge leg that could fail, and it located where it does. The other
failures (L2 as run, constraints at one per cell, the halo catalogue at one per cell, the zero shift at
256^3) limit what G3 may claim; none removes a capability the G3 science needs if the conditions below
hold. If the orchestrator reads "three-way convergence" as required over the whole time range the
science uses, the answer is **no** until a gauge-invariant (or gauge-qualified) measure of the late
strain agrees between the two gauges, or the late strain is shown converged in particle number in the
gauge it is read in (K2, or the 128^3 partner), whichever the ruling names.

### Conditions for G3 (before any production run of the population scan)

1. The particle-number leg in the Gamma-driver gauge: the 128^3 eight-per-cell partner (0.85 card-h)
   read against the 128^3 one-per-cell Gamma-driver leg, prediction first; no late-time (a > 50)
   strain claim enters G3 before it, or K2 of the 256^3 member, has been read.
2. No claim on halo counts or masses against the mesh before K3 is read (decision 0049 item 7);
   halo masses quoted with their gauge (R23) or by proper distance.
3. A G3 scope written and reviewed independently before production (as for C, D, E), which places the
   scope's section-6 mesh clause of the first source (amend it with a date, or run 256 cells), names
   the gauge leg of the G3 criterion (the scope says lapse condition; the package varied the shift),
   and states how the late strain is made gauge-qualified: a gauge-invariant estimator (Weyl or
   rho_K) compared between the two gauges, or every late number quoted in the Gamma-driver gauge with
   the measured gauge dependence as part of its error.
4. G3 population runs at eight particles per cell or more, with the constraint levels quoted beside
   every late-time number (mean relative momentum constraint 0.07 at eight per cell, 0.2 at one per
   cell, at a = 141).

### Reservations to carry to G3

1. Gauge dependence of the late band strain: 5 per cent at a = 64, 20 at 100, 36 at 132 (my run);
   within 1.6 per cent to a = 49.
2. The particle-number leg of the strain exists only in the zero-shift gauge (until condition 1).
3. Halo catalogue not converged in the mesh at one particle per cell (failed on record).
4. Constraints converge with the mesh only at fixed eight per cell, on one coarse pair (64/128), zero
   shift; not at one per cell; the series-7 floor and the FLRW Hr rise unexplained.
5. Shearing dust L2 failed as run; its cause inferred, and the inference in tension with the source's
   statement that the reference codes are particle codes.
6. The zero shift fails in resolved cores (256^3, a = 102); every finer or larger-amplitude run uses
   the driven shift, which is untested at eight per cell (K1).
7. The first source has no 256-cell member and its pre-crossing mesh differences do not fall (scope
   section 6 clause unmet, unassigned to a gate).
8. The scope's G3 gauge leg is the lapse condition; no lapse variation of the population exists.
9. Corrections of text and figures owed (section 6).
