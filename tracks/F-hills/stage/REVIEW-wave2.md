# Lead's review of the helpers of waves 2 and 2b (F-hills)

Lead session of wave 2b, 2026-11-19 (the wave-2 lead was cut off on 2026-11-15 before writing
anything). Checked from the artefacts (run outputs, figures, raw AthenaK files), not from the
helpers' conclusions. Predictions and outcomes of the checks: `JOURNAL.md`, session
"F-hills lead (wave 2b)", V8-V11. Lead's runs: F-20261119-145434-82c05f2 (V8, own parser of the
raw AthenaK files), F-20261119-145449-245e984 (V9, own GR invariants), F-20261119-145509-fb91531
(V10, newton3 tests), F-20261119-145619-8246322 (E3 analysis rerun with the fixed reader). Script:
`stage/review_wave2/review_check.py`. Figures read: `fig_review_nr.png`, `fig_review_gr.png` of
those runs; the helpers' `nr_first/figures/fig_e3_single_gauge.png` (old and new),
`fig_e7_p1smoke.png`, `fig_e10a_s3_s2_compare.png`, `fig_e11_tree_check.png`,
`fig_c0_constraints.png`, `fig_baselines_p1.png`; `newton3/figures/fig_energy_definition.png`;
`stage/G0/second_check/figures/fig_sc3_sc6_models.png`, `fig_sc4_capture_plane.png`.

## nr_finish (wave 2b) and nr_first (wave 2): `nr_first/`

Confirmed [VERIFIED, V8 from the raw files]:
- S3/S2 stopped on "1632 > max_nmb_per_rank 1600" at t = 21.97 m (tracker x = 2.2034) and
  14.22 m (x = 2.2168); E11's explanation (the tracker sphere reaches the next level-5 block at
  x > 2.202 m) is consistent with both stop positions. The rule model itself was not rerun by
  me; its agreement with the restart trees is the helper's (figure read).
- Horizon rows: 5 and 2 failed searches (repeated rows), first good search t = 3.5 (1.00789) and
  2.5 (1.00618), drift t = 4-6 to 12-14 +5.15e-4 and +8.55e-4; f(10-14) 0.468 and 0.758;
  tracker y, z below 2.5e-15. The source reading (failed search rewrites the previous row) was
  not re-read at `fastflow.cpp` by me; the planted-failure test passes (helper).
- P1 smoke: 1716 -> 1744 MeshBlocks, 2057.4 MeshBlock-cycles/s, 70847 MiB, trackers within
  4.1e-9 of the input, t = 0 masses 0.12778 / NaN / 0.99607, failures 1 / 2 / 17 of 25. Cost of P1
  16.9-20.1 card-hours (arithmetic reproduced).
- E2 (C0), E6, E9: figures read and consistent with the journal; not recomputed (E6's Newtonian
  energy equals the wave-1 lead's V5b and newton3's corrected value, three codes).

Wrong or stale, fixed by the lead: `results/e3_single_analysis.json` and
`figures/fig_e3_single_gauge.png` predated the reader fix (wrong found/missed counts; failed
searches drawn as masses at -2 percent). Rerun F-20261119-145619-8246322 replaced both; README
row updated. Remaining small defect (listed, not fixed): `single_analysis.py` reports `m_at` for
times after the end of a run by repeating the last value.

Not confirmed: E8's mechanism (finder oscillation at 4 cells per radius) beyond the figure;
E11's model along x = 0-20 m (not rerun).

Failed predictions of the helper, on record in `nr_first/JOURNAL.md`: E1(b) tree size; E3
first-search mass, S2 f >= 0.8, cost; E7 first-search masses; E4 rerun missed counts. None is
hidden or reworded.

Open, for the next session: S2g (run F-20261119-143443-f11ebb9, Slurm 4640, pending) and its
E10 outcome; junk energy of a single member (not measured); the m/16 partner S1.

## newton3_fix (wave 2): `newton3/`

Confirmed: 15 of 15 tests at 82c05f2e (V10); corrected passage energies +1.31191 (q = 4) and
+1.61272 (q = 10) units equal the wave-1 lead's independent barycentric values 1.31187 and
1.61267 (V5b, other integrator); captured orbits q = 4 a = 7.746, e = 0.2503, first pericentre
t = 122.1. Figure `fig_energy_definition.png` shows what the README says (old definition
oscillates by +-0.37 units at q = 4, corrected flat after t = 200).
Not confirmed: the Jacobi-split derivation was read, not re-derived; the finite-q rerun numbers
(P_dis unchanged, |dE| factor 0.982-1.009) were not recomputed.
Requests of the helper and what the track does: (1) corrected predictions copied into the G1
package (P1 section of `stage/G1/STATUS.md` and the journal's P1 prediction); (2) G0 OPEN item 7
closed; (3) the NR readers already give both energies (E4); (4) `three_punctures/scripts/
newton_start.py` still reads the old fields: listed in G1 OPEN, not rerun (its outputs are wave-1
records); (5) second agent on the derivation: still open (G1 OPEN); (6) "8.6 percent" at D = 0.1,
M/m = 10 was printed only in `newton3/README.md` line 281 (wave-1 text): corrected there to 10.4.

## note (wave 2): `note/`

Confirmed: the two differences the note's claims check found in the wave-1 lead's statements
(V11): the "nine points" claim of V4b is wrong for retrograde D = 0.1 and 0.2 (only V4 covers
them, |dP| 0.0023 and 0.0063, |dE|/E 0.4 and 1.2 percent); the q = 4 m/16 row of SCOPING section 9
was the radius-1.2 row (radius 1.8: 2514 / 2864 / 2568, 44.8 card-hours). Both corrected
(G1 T1 text, `stage/G0/SCOPING.md` section 9 with a dated note, EVIDENCE rows).
Not confirmed by me: every number of the ledger; the regeneration of the note's figures is left
to `nrpic-stage verify` (it reruns every `note/scripts/fig_*.py` and compares).
Open: the note does not contain the wave-2b NR results (E3, E7, E11); the paper-writing reviewer
step; a fresh verifier (C18).

## second_check (wave 2): `stage/G0/SECOND_CHECK.md`, `second_check/`

This is the only check by a second agent so far; its findings and the track's answer:
- (1) novelty verdict holds (31 INSPIRE queries, 10 forward-citation lists): CONFIRMED by the
  helper; not repeated by me. Track: the verdict stands, with the stated limits (no ADS, no
  journals outside arXiv).
- (2) neither baseline driver has a defect: CONFIRMED (helper's own integrators). Track: no change.
- (3) the q = 10 disagreement is physical capture: CONFIRMED by the helper (capture plane figure,
  read). Track: no change.
- (4) the size of HRNA's excess at q = 10 is inflated by the initial-binary convention and a
  spurious self-acceleration of a moving binary (1.065e-4 at V = 0.28): the wave-1 lead's HRNA
  percentages (94 percent capture at r_p = 8 M; separation at 13 M) are NOT usable as
  predictions. Track: qualified in the G1 package and STATUS (the HRNA numbers are quoted as
  model outputs at release 4 r_t only); the self-force test (R3) goes to the geodesic_binary
  package of the next wave; the wave-3a EIH reference (`eih/`) gives a third baseline. I did not
  rerun the flat-binary self-force test.
- (5) the q = 10 start state is not an r_p = 8 M encounter in GR (turning point 5.77 M): CONFIRMED
  by my own implementation (V9a: 5.775 M). Track: P1 is at q = 4 (decision 0013), where the same
  reading gives 9.25 M against 9.81 (V9b); the q = 10 input is rebuilt from a GR parabola before
  any q = 10 passage (G2 plan, RISKS R14).
- Requests R1 (rebuild q = 10 momenta) and R2 (qualify HRNA percentages): answered as above.
  R3 (flat-space moving-binary test in geodesic_binary/tests): open, next wave.
- Not checked by the second agent: retrograde encounters, q = 4, the EIH reference (now wave 3a).

## What is wrong in the track's earlier documents (found in this review)

| Statement | Where | Correct | Action |
|---|---|---|---|
| independent code agrees at nine points within 0.002 / 0.4 % (V4b) | G0 EVIDENCE V4b row, SCOPING s. 7/10, G1 T1, STATUS (wave 1) | seven points; retrograde D = 0.1, 0.2 differ by 0.0023, 0.0063 in P_dis and 0.4, 1.2 % in E | corrected in G1 package and STATUS; SCOPING and EVIDENCE get a dated note |
| q = 4 at m/16: 2416 / 2654 / 2348, 41 card-hours | SCOPING s. 9 | 2514 / 2864 / 2568, 44.8 (radius 1.8 of the inputs) | SCOPING s. 9 note |
| HRNA: member captured in 94 % of phases at r_p = 8 M | SCOPING s. 4, G1 STATUS, RISKS R4 | a model output at release 4 r_t, inflated by two artefacts (second check) | qualified |
| P1 = q = 10, r_p = 8 M | G1 STATUS (wave 1) | P1 is at q = 4 (0013); at q = 10 the GR turning point is 5.77 M | G1 package rewritten |
| both members captured in 8.6 % (D = 0.1, M/m = 10, isotropic) | newton3/README.md l. 281 | 10.4 % (newton3_fix) | corrected |
| multi-puncture not released; allotment 40 | STATUS, OPEN, RISKS (wave 1) | released in core-v0.3; 50 (0014) and 120 toward G2 (0016) | rewritten |
