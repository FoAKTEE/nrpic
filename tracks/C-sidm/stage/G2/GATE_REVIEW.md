# Gate review: C-sidm G2 (independent reviewer, batch 34)

Reviewer session of batch 34, 2026-11-27 (23:20-23:50 UTC). Decision 0019 item 3. I produced none
of this work. Tag check: `git tag -l 'stage/C-sidm/*'` lists G0 and G1 passes only; G2 is not
signed. Branch `track/C-sidm` reviewed at 65e3695ce (main merged; the fresh verifier's last commit
204b5d491 included). My predictions were committed first (8859b8615, kept unchanged in section 2).

Read before judging: CLAUDE.md; coord/CHARTER.md to "Owners" and sheet 9.6; brief lines 674-686
(gate table); decisions 0010, 0013, 0016-0019, 0039-0047; the package `stage/G2/` (STAGE_REPORT,
CHECKLIST, EVIDENCE, OPEN, RERUN, VERIFY_RESULTS of the lead's full pass, `verifier/VERIFIER.md`,
`verifier/README.md`); `scope/SCOPE.md` sections 2, 5, 6 (lines 110-140, 317-340); HANDOFF.md;
the note's Sec. V and Table VI (note/main.tex:237-334); the lead's journal entries named in C19.

Opened as evidence: the manifests of the eleven threshold runs (all `completed`, all on the same
card executable, `.work/build_gpu_v06/src/athena`, sha256 ea473498500f...); the decks of every leg
(`longruns/inputs/A8N_*`, `A16N_*`, diffs in section 4); the raw `cc.nrpic.hst`, `cc.z4c.user.hst`
of all eleven runs (my run, section 2); the figures `note/figures/fig_g2_threshold.png`,
`fig_g2_mosaic.png`, `schem_ladder.png`, `schem_architecture.png`, the analysis figure
`scratch/C-sidm/C-20261124-130021-5c9c207/fig_cc2_N.png`, the verifier's `fig_v1_king_sequence.png`
and `fig_v2_fates.png`, and my own `fig_review_check.png`, each looked at; the source locator of
the literature value, `kb-data/raw/arxiv/2009.08163/v1/src/paper.tex:948-958, 969-972, 1052-1076`;
the conductivity series output `scratch/C-sidm/C-20261124-131012-f920f45/heat_series.json`.

## 1. The stage check

**My rerun** (`harness/bin/nrpic-stage verify C-sidm G2`, 2026-11-27T23:31Z, export of 65e3695ce;
results kept in `scratch/C-sidm/tmp/gate_review_g2/VERIFY_RESULTS_reviewer_20261127T233118Z.md`):
FAIL on one check, `runs` (2 of 270 runs); every other check passes (rerun 14 of 14 scripts,
compare 28 of 28 regenerated files within tolerance, regenerate 28 of 28, style, figures, note
PDF); checksums WARN only because they came from the cache (the full pass below read every byte).
I restored the lead's full-pass files to `stage/G2/VERIFY_RESULTS.{md,json}` afterwards, as the
lead left them (uncommitted; the lead commits them, HANDOFF.md).

**The lead's full pass** (`--full`, 2026-11-27T10:40Z, export of 6764898; copy in
`scratch/C-sidm/tmp/gate_review_g2/VERIFY_RESULTS_full_lead_20261127T104035Z.md`): every byte of
9199 output files (1184.70 GB) hashed again and equal to the recorded checksums, so every output
of the threshold runs, the collisional series and the analyses is intact. The one failed check
is `runs`: two card runs, **heat_C1 C-20261121-210524-36a658e and heat_C2
C-20261122-183030-2f3a471** (conductivity against cell size and step, G1 reservation 1). In each
case directory the intermediate particle snapshots `heat.part.00001-00015.bin` recorded in the
run's `sha256sums.txt` are gone (120 and 45 files), and `case.json`, `reduced.npz`,
`summary.json` were added after the run finished (8 and 3 directories). Cause, from the file
times and the code: the reduction runs C-20261124-130338-43b5ffa and -c4ac85e
(`heat/scripts/run_mode.py reduce <card run dir>`) wrote their products into the card runs'
directories at 2026-11-24 13:03-13:05 UTC and `heatlib.SnapReducer` (heatlib.py:133-134) removes
every snapshot but the first and last after reducing it. [VERIFIED from the directory listing
and the code.] The reduction runs record only `run.log` as their output, and the series analysis
C-20261124-131012-f920f45 records no checksum of the `reduced.npz` it reads.

Does it bear on the gate? Not on the threshold (C2, C7, C9), the constraints (C3) or the
collision budgets (C8): none of those runs is involved and their bytes are verified. It bears
on two statements: the conductivity "1.020 +- 0.004" in C1, which is (4 x 1.0187 - 1.0149)/3
from the two zero-cell fits in `heat_series.json` (JOURNAL.md:674; fits 1.0187 +- 0.0026 at
k lambda 0.1 and 1.0149 +- 0.0026 at 0.2, the latter with chi^2 6.28; one seed per point; no
second agent has checked it, VERIFIER.md section 8), and on C6 ("all runs registered with sha256
of inputs and outputs"), which is not true for these two runs. The raw data behind the answer to
G1 reservation 1 can no longer be re-verified. The two runs cost 0.19 and 0.21 card-hours; the
clean remedy is to rerun them with a reduction that writes into its own run directory and
deletes nothing; a waiver (coord/WAIVERS.md) with this provenance is the alternative. Either is
a correction owed before G3, not a reason to hold G2.

## 2. Reviewer's own check R (run C-20261127-232854-8859b86)

### Predictions, as committed in 8859b8615 before the run

Reader of my own (`scratch/C-sidm/tmp/gate_review_g2/review_check.py`, registered with
`nrpic-run`, inputs checked against each run's `sha256sums.txt`): comment lines skipped; restart
rule (a row whose time is not later than the last kept row replaces every kept row from its time
on); marker crossing = first record with alpha_min (column 16 of `cc.nrpic.hst`) below 0.3,
linear between it and the record before. I looked at the lead's `fig_g2_threshold.png` and the
verifier's `fig_v2_fates.png` before writing these, so R1 repeats numbers I have seen; R2 and R3
are quantities neither of them states.

- R1 (fates). Crossings 252.31, 217.97, 252.41, 229.79, 295.78, 534.81 M for N6b344, A16b344,
  N6b344e1, A344s1i, N4c, A334s1c, each within 0.05 M; no crossing for N6b324, A16b324,
  N6b324e1, N6c, A324s1i, whose last kept record is at 600 M or later (to 0.25 M). Refuted by
  any crossing off by more than 0.05 M, a crossing in a stable member, or a stable member that
  ends before 599.75 M.
- R2 (what "holds" means). For each of N6b324, A16b324, N6b324e1 the 20 M block means of
  alpha_c - alpha_c(0) (alpha_c = column 13, alpha_probe at the origin) have an interior minimum
  followed by an interior maximum, the maximum between 300 and 500 M: the inward kick is reversed
  and the core re-expands (a stable oscillation, not a slow drift), and every block mean lies
  within +-0.03. For N6b344, A16b344, N6b344e1 the block means fall from 40 M to the last block
  before the crossing with no rise above 0.002 from one block to the next. Refuted by a stable
  member without an interior maximum in (300, 500) M or with a block mean outside +-0.03, or an
  unstable member with a block-to-block rise above 0.002 before its crossing.
- R3 (constraints in the members of the legs; column 4 `H-norm2` of `cc.z4c.user.hst`, the
  volume integral of H^2). (a) N6b324e1 against N6b324, mean over 100-200 M: equal within 5 per
  cent (the shift damping does not change the deposit noise). (b) A16b324 against N6b324 (cells
  of M/16 inside |x| < 1.95 M, same particles): ratio between 1.2 and 10 (fewer particles per
  cell where the mesh is finer; the lead reports 9.3 for M/4 to M/8). (c) No growth in the
  stable members: mean over 500-600 M divided by mean over 100-200 M within 0.7 to 1.4 for
  N6b324, A16b324, N6b324e1 and N6c. Refuted by any ratio outside its range.

### Outcomes

All three held. The 22 history files read matched their recorded sha256; the reader's self-test
on a synthetic continued history gave the exact crossing (249.75 M, one restart seen).

| | Number | Verdict |
|---|---|---|
| R1 | 252.311, 217.972, 252.413, 229.791, 295.785, 534.814 M; the five stable runs reach 600.0 M with lowest alpha_min above 0.64; restarts handled in N4c (4), N6c (6), A16b324 (8) | HELD |
| R2 | block means: N6b324 [-0.0119, +0.0150], minimum at 110 M, maximum at 370 M; N6b324e1 identical to four digits; A16b324 [-0.0171, +0.0107], minima at 170-210 M, maximum at 470 M; the three unstable members fall block by block (largest rise -0.0031 to -0.0045, i.e. none) | HELD |
| R3 | (a) 1.0055; (b) 6.43; (c) 1.009, 0.930, 1.007, 1.000 | HELD |

Figure `scratch/C-sidm/C-20261127-232854-8859b86/fig_review_check.png` (looked at): left, the
crossings; middle, the central lapse of the stable members turns back after the kick on both
meshes and in both gauges while the unstable members fall monotonically; right, `H-norm2` flat
from 50 to 600 M, the M/16 member 6.4 times higher.

What R adds [JUDGEMENT]: "holds 600 M" is backed by a reversal of the kicked contraction, the
signature of a stable pulsation, not only by the absence of a crossing. The finer mesh changes
both members in the same direction: the unstable member collapses 13.6 per cent earlier and the
stable member pulsates more slowly (maximum at 470 against 370 M). Both are what a threshold
moving toward smaller y0 under refinement would produce. The fates bound it to the bracket on
both meshes; nothing locates it inside.

## 3. The literature value and its name

The value compared, y_max = 0.334 for the King model, is printed in arXiv:2009.08163 as the
first maximum of the binding energy (paper.tex:952-958, Table "First binding energy maximizer and
zero") [VERIFIED]. The verifier's own solver gives 0.3340322 (run C-20261127-090849-dcfc1ae) and
the bracket members lie 2.49e-5 and 2.42e-5 below the maximum of E_b on either side [VERIFIED by
the verifier, figure read]. The same paper states that the turning-point principle (stability
changes at the first maximum of the mass-radius curve) "is not true" (paper.tex:969-972) and
supports the binding-energy maximum hypothesis instead (paper.tex:1059-1065, 1076). The note
calls the value "the turning point" and attributes a "turning-point criterion" to that reference
(main.tex:239, 254), and ruling 0013 uses the same words. The number is right; the name is
wrong at the source. This is a wording correction, not a defect of the result.

## 4. Criteria

| # | Criterion | Verdict | Evidence I opened, and why |
|---|---|---|---|
| C1 | Code paths pass their tests of §10 | PASS WITH RESERVATION | Rows held by C (charter 10): "Einstein-Vlasov steady states and their stability threshold": the control holds 600 M at N = 1e6 and decays by finite N below (R1; verifier 3a); the bracket keeps its fates (section 2). Collision rows: G1 signed. Reservations: the conductivity number rests on runs that fail the checksum check (section 1) and has no second check; BA.3 is listed as a failure but held (verifier X.2; JOURNAL 2026-11-25T16:14Z). |
| C2 | Three-way convergence (N, mesh, gauge or boundary) | PASS WITH RESERVATION | Fates invariant under N (1e5, 1e6), mesh (M/8, M/16) and shift damping (2, 1): R1, R2, verifier V2. Deck diffs read: M/16 members add only `<refined_region3>` level 8 inside \|x\|_inf < 1.95 M and double the cycle cadences; eta1 members change only `shift_eta` 2.0 -> 1.0; 0.344 and 0.324 differ only in particle and table files. Reservations: (i) the gauge leg changes the shift damping only; the slicing (1+log) and the outer boundary (outflow at 512 M) were not varied, although the scope names "domain 512 M against 1024 M; one alternative slicing" (SCOPE.md:129-130) and the note itself says the shift vanishes at the centre (main.tex:256); the central lapse of the two gauges agrees to 1.4e-5, so this leg could hardly fail; (ii) the M/16 leg refines only the inner 1.95 M of a cluster of radius about 13.5 M (R/M 13.48 at y0 = 0.344, verifier V1); (iii) one seed per member; (iv) at N = 1e5 the stable fate is a property of the 600 M cut (its own control crosses at 599.99 M); (v) no continuous quantity converges: the unstable collapse time moves 13.6 per cent between two meshes, the collisional series has two meshes in range and no order. |
| C3 | Constraints behave | PASS WITH RESERVATION | Integrated H^2 flat after about 50 M and falling as 1/N (7.68e-2, 7.86e-3, 7.90e-4; verifier 3b; fig_cc2_N.png panel 3 read); no growth to 600 M in the stable members (R3c). No bound was written at G0 for this track. Reservation: the floor is deposit noise and rises 6.4 times when the core is refined at fixed N (R3b); convergence with the mesh at fixed particles per cell is not shown; "behave" is the lead's JUDGEMENT reading, which I accept for G2 because no G0 bound exists and nothing grows. |
| C4 | A first minimal full-GR kinetic run | PASS | Eleven threshold runs and the D2 series, full GR with particles to 300-600 M (manifests completed). |
| C5 | Verification report | PASS WITH RESERVATION | STAGE_REPORT.md exists but predates the verifier (it says VERIFIER.md missing and C18 OPEN, verdict FAIL); EVIDENCE.md is the state of 2026-11-24 (runs "queued", "running"). Both are to be regenerated. RERUN.md is current. |
| C6 | Reproducibility package | PASS WITH RESERVATION | RERUN.md names every threshold run, deck generator, queue command and analysis; my rerun regenerated all 28 figure files. Reservation: the two heat runs (section 1). |
| C7 | Collisionless threshold reproduces the literature value with three-way convergence | PASS WITH RESERVATION | The literature value 0.334 (section 3) lies inside (0.324, 0.344), whose members keep their fates in every leg (R1, R2). This is a bracket of +-0.010 in y0 (+-0.017 in Z(0)) for one family, one seed per member; the location inside it is not shown to converge, and the note's sentence "the location of the threshold is [converged]" (main.tex:256) overstates it. Ruling 0039 item 3 asked exactly for the mesh and gauge legs of this bracket at a million particles, and they are delivered. |
| C8 | Budgets of conserved quantities close in curved spacetime | PASS WITH RESERVATION | Verifier V4 and X.7 (own reader): collision energy 2.84-3.17e-16 of sum M H to the first excision, momentum below 4e-19, rest mass exact, on M/8, M/16 and with shift damping 1. Reservations: this is the operator's pairwise budget; the scope's second half, a whole-system budget including the collisionless drift (SCOPE.md:327-328), is not in the package (the note lists it as open, main.tex:280 item iii). The count test of the rate before t_c passes in four of six members; f = 4 and shift damping 1 fall short by about one per cent at z = -3.34 and -3.83 (verifier section 4). |
| C9 | Ruling 0013: located with three-way convergence and compared with the turning-point criterion | PASS WITH RESERVATION | As C7, and section 3 on the name of the criterion. |
| C10 | Schematic: verification ladder | PASS | schem_ladder.png read: rungs, evidence, state; "collisionless threshold bracketed", consistent with the evidence. |
| C11 | Convergence figures (N, mesh, gauge) | PASS | fig_g2_threshold.png read: one panel per leg, crossings marked, the eta1 curves under the eta2 curves as stated. |
| C12 | Constraint norms against time | PASS WITH RESERVATION | fig_cc2_N.png (C-20261124-130021-5c9c207) read: H-norm2 at N = 1e4 and 1e5 on the old M/4 mesh. The constraint histories of the bracket legs are in no package figure (they are in my figure, right panel). |
| C13 | Multi-scale slice mosaic with zoom boxes | PASS | fig_g2_mosaic.png read: three rows by three zoom levels with boxes and scale bars; the unstable member's core visibly concentrated at 220 M, the stable member like its start. |
| C14 | Package documents | PASS WITH RESERVATION | All present. The verifier's report is at `stage/G2/verifier/VERIFIER.md`, where the stage tool does not look (`package` check: "no verifier's report yet"); it needs to be at `stage/G2/VERIFIER.md` (decision 0016 item 1). |
| C15 | Data figures from registered outputs, one script each, looked at | PASS | fig-script and regenerate checks pass (14 figures, 28 files); the scripts check input sha256 (RERUN.md section 3). |
| C16 | Schematics: architecture and gate timeline | PASS | schem_architecture.png read: core-v0.6 for the runs; "thresholds of the other two families" honestly marked new. |
| C17 | Working note with /paper-writing, checker passed | PASS WITH RESERVATION | Note compiles and the checker passed (lead). Wording to correct: "location ... is [converged]" (main.tex:256), "particle noise therefore drives the control collapse" (main.tex:250; shown is a finite-N effect, verifier section 3), "turning point" for the binding-energy maximum (section 3). |
| C18 | Fresh verifier | PASS | `verifier/VERIFIER.md` read in full: own readers tested first, every number of Table VI and RERUN.md section 1 reproduced to its printed digits, predictions judged from its own numbers, comparison written after. I reproduce its crossings and bands independently (R1, R2). |
| C19 | Null results and failed runs on record | PASS WITH RESERVATION | JOURNAL entries checked: N.3, D2.2, A.1 (kout), A.3, A.4, NS.2, D2.3 seed part FAILED as written; D2eta1 failed run; withdrawn B17.1-B17.3. Not on record: the M/4 seed-2 collisional run leaves the lapse range after its first excision (alpha_min -2.7e8, 335 non-finite rows; verifier section 4). Listed wrongly as failed: BA.3. |
| C20 | STATUS, JOURNAL, HANDOFF current | PASS | Current at the end of batch 32; the verifier's findings and the full pass came after, as HANDOFF.md foresaw. |

No number in the note's G2 section lacks a run id: every value of Table VI names its registered
analysis (main.tex:318-331), and the prose carries no numbers.

## 5. The track's own G2 criteria (scope section 5), which the checklist does not carry

SCOPE.md:323-328, written at G0 and not amended since (last commit touching SCOPE.md: ac4aac180, the wave-2 review):
"collisionless threshold of the monoenergetic and the King b = 0.1 family with three-way
convergence; the converged y_c (or Z(0)) agrees with the binding-energy maximum within the
convergence error [target 0.01 in y_c, 0.02 in Z(0)]; ... in curved spacetime the rest-mass,
energy and momentum budgets close to the round-off of pairwise conservation plus the measured
collisionless drift." SCOPE.md:124-130 adds "a located threshold, not a bracket" from the growth
rate of the radial mode, and a gauge or boundary leg of domain size or slicing.

| Clause | State |
|---|---|
| Monoenergetic family | NOT MET (no run) |
| King b = 0.1 family | NOT MET (no run). This is the science family of G3 (HANDOFF.md, G3 scope), a core-halo family whose threshold may not sit at the binding-energy maximum (the track's own risk 2, arXiv:2105.05556). |
| Agreement within 0.01 in y, 0.02 in Z(0) | MET for King b = 1 in the bracket sense: the members are 0.010 and 0.010 from 0.334 in y0 and 0.017 from it in Z(0). |
| Located threshold from the growth rate, not a bracket | NOT MET as written; the G1 review redirected the method to collapse times against controls (coord/GATES.md, G1 of C), which the package follows. |
| Domain or slicing leg | NOT MET (shift damping instead) |
| Budgets including the collisionless drift | Pairwise half MET, whole-system half NOT MET |

The King b = 1 family the package uses was named at G0 "for verification" (JOURNAL.md:94-95),
so the choice is not after the data. But no dated amendment moves the two other families out of
G2, and the lead did not ask for one; the note defers them to the scan (main.tex:278) and the
architecture schematic marks them new.

## 6. Reservations of G1 and where they stand

| G1 reservation (coord/GATES.md) | State at G2 |
|---|---|
| Conductivity not settled at the per-cent level | Answered with 1.020 +- 0.004 by the lead, one seed per point, no second check, raw inputs no longer verifiable (section 1). OPEN in substance. |
| Threshold from collapse times or contraction against a control, at least three seeds | Collapse times against controls: done. Three seeds: NOT done (one per bracket member at N = 1e6). |
| Quantities named after the data | The 20 M windows and the +-0.03 band of B17.6, B20.1-B20.3 were written before the runs (verifier checked the commits). |
| Card tests without a second check | Closed for the threshold and collisional runs (verifier, this review); open for the heat card runs. |
| The M/4 mesh does not hold the equilibrium | Answered: M/8 holds it at N = 1e6. |

## 7. The verifier's corrections

None of the verifier's text requests is applied yet (README.md, Requests; the batch text counts
four, the README lists five): (a) "BA.3 failed" in OPEN.md:6 and the C1 evidence (it held);
(b) the collision count test stated per member and window, not as one ratio; (c) the stale risk
25 that A334s3c ends at 0.25 M (STAGE_REPORT.md:158; it reaches 600 M, crossing 563.29 M);
(d) the broken M/4 seed-2 run after its first excision; (e) that the gauge leg changes the shift
damping only. I confirm (a) from the journal, (c) and (e) from the decks and histories, and add
the corrections of section 4 (C14, C17) and section 3. None changes a verdict; all are owed
before the stage report is regenerated.

## 8. Recommendation

**PASS WITH RESERVATIONS.** The code paths of the track work as claimed, and two independent
readers (the verifier's and mine) reproduce every number the gate rests on from bytes the full
checksum pass verified. A King b = 1 cluster 3 per cent beyond the binding-energy maximum
collapses after an inward kick at a time that barely depends on N (229.79 M at 1e5, 252.31 M at
1e6), unlike the noise-driven decay of the controls (295.78 M at 1e4, 534.81 M at 1e5, none by
600 M at 1e6). A cluster 3 per cent before it turns the kick back and pulsates inside +-0.03.
The two fates are the same on two meshes, in two shift dampings and at two particle numbers. The
collision operator conserves energy, momentum and rest mass pair by pair to rounding in the
evolved curved spacetime. Rulings 0013 and 0039 item 3 define C7 and C9 as this bracket with its
mesh and gauge legs at a million particles, and that is delivered. Nothing failed that the gate
rests on; the failures on record (A.3, A.4, NS.2, D2.2, D2.3 seed part, D2eta1) are understood
and stated.

The recommendation depends on one ruling that is the orchestrator's: the track's own G2 clause
(section 5) names the monoenergetic and King b = 0.1 families, and neither is run. I recommend
recording a dated amendment of SCOPE.md section 5 that moves both families into G3 as its first
step, required before any G3 production run on b = 0.1 models (the G3 models are to sit on known
sides of that family's collisionless threshold, which is unknown in the code and may not sit at
the binding-energy maximum). Without that amendment the clause stands as an unmet G2 criterion
of the track's own and, as decision 0047 held for Track A, the gate would not pass as written.

### Reservations to carry to G3

1. The collisionless threshold of the King b = 0.1 family (and the monoenergetic one, or its
   removal by ruling) is bracketed at N = 1e6 on two meshes before G3 production on b = 0.1.
2. At least three seeds per bracket member near any threshold the science uses (G1 reservation,
   not met at G2); a bracket narrower than +-0.010 in y0 where the scan needs it.
3. A gauge or boundary leg that can fail: another slicing or a domain of 1024 M. The shift
   damping leg cannot distinguish (central lapse equal to 1.4e-5).
4. Refinement over the whole cluster, not only the inner 1.95 M; no order or extrapolation of
   any collapse time from two meshes; the threshold may move toward smaller y0 under refinement
   (section 2, JUDGEMENT).
5. Collapse is the alpha_min = 0.3 lapse marker in every run; G3 needs the horizon finder with
   `<fastflow> diagnostics = true` and polishing (decisions 0040 item 3, 0041 item 5).
6. Constraint floors are deposit noise: rising 6.4 times under refinement at fixed N; their
   convergence at fixed particles per cell is not shown.
7. The whole-system energy budget including the collisionless drift (scope) and the collision
   rate count test that falls short by one per cent in two of six members.
8. The conductivity answer to G1 reservation 1 rests on runs whose raw outputs were deleted;
   rerun them (0.4 card-hours) or waive with provenance, and make the reduction write into its
   own run directory and delete nothing.
9. The particle-noise mechanism of the control collapses is shown as a finite-N effect, not as a
   mechanism (verifier section 3); the "log law" test (N6c to about 900 M, a second N4c seed) is
   the cheap way to show it.

### Corrections owed by the lead (before the stage report is regenerated)

Move or copy `verifier/VERIFIER.md` to `stage/G2/VERIFIER.md`; judge C18; commit the full-pass
VERIFY_RESULTS and name the two heat runs in OPEN.md; regenerate EVIDENCE.md and STAGE_REPORT.md;
apply the verifier's (a)-(e); in the note replace "the location ... is converged" and "particle
noise therefore drives" by what is shown, and name the compared value the binding-energy maximum
of arXiv:2009.08163 (paper.tex:952-958), whose authors reject the turning-point principle
(paper.tex:969-972); put the bracket legs' constraint histories in a package figure.
