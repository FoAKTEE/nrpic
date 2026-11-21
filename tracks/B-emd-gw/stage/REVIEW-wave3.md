# Review of wave 3 (lead of B-emd-gw, batch 2a, 2026-11-20 night)

Scope: the packages that finished since the last lead session (2026-11-15, end of wave 2):
wave 2b `note` (v1), `stage/G1/verifier2`, `waves` (its wave-2b part and the x10 check of
round 1); wave 3a `population` (its session ended with status partial); round 1 of wave 3
`note` (v2, whose last outputs were stranded by the cut of 14:35 and are committed now) and
`stage/G1/verifier3` (finished in batch 1). Packages still in progress are not reviewed
here; what they hold and what remains is in `HANDOFF.md`: `first_source` (second-round
results committed; the round-3 analyses of the particle and mesh legs ran unattended),
`waves` round 1 (F2 and the step test ran, not analysed; the gauge module of gw_diag is
uncommitted), `flrw_conv`, `shear`.

Method: the lead's checks are in `review_wave3/JOURNAL.md` (predictions L1-L3 committed in
ecb32b71 before the runs), runs B-20261121-063617-6183015 (L1, L2) and
B-20261121-063835-826c461 (L2b), scripts in `review_wave3/scripts/`, results and figure in
`review_wave3/{results,figs}/` (looked at). I read the helpers' reports first, so this is a
recheck of the artefacts, not a blind one. Two of my three predictions failed (L2, L3) and
one held with a marginal exception (L1); all are on record.

## Housekeeping done in this session

- Seven runs of round 1 had ended unattended with exit 0 and were never closed; closed with
  `nrpic-run finish` (manifests and checksums): B-20261120-222841-acfe21d (card job 4745),
  -222849-3b921b7, -222849-e5673dc, -222955-c8e16e3 (card job 4746), -223006-24448ac,
  -223236-e213594, -223241-f1efd4f. Their outputs are not analysed (packages in progress).
- note v2 outputs committed (e1773add) after `cmp` of all 28 figure and table files against
  run B-20261120-223319-cc5320d (0 differences).
- Erratum appended to `REVIEW-wave2.md` (note helper's Request 5); `newton_tests/README.md`
  names the measure behind "1.3e-15 L" (verifier2's request 3).

## Per package

### stage/G1/verifier3 (G1 criterion 1 and the spatial-gauge piece)

Confirmed by the lead:
- Its committed results equal the registered outputs (v3_summary.json against run
  B-20261121-030121-58fe5dc, byte for byte).
- Every last-dump TT error it gives for F (N = 16-64) and X (N = 16-64, x10) agrees with the
  waves package to 1 per cent or better, except the X plus amplitude at N = 48, 64 (x1) and
  the F cross amplitude at N = 64 (1.07 per cent, 3.4e-10 absolute, round-off level)
  (L1; `review_wave3/figs/lw3_crit1.png`).
- Its criterion-1 verdict: both set-ups recover amplitude, phase and both polarizations of
  the exact waves with the errors the code's operators predict; the two diagnostics agree to
  6.4e-11 (F, forward combination) and 2.4e-8 (X).

Not confirmed / corrected:
- Its item X1 ("the README's plus amplitudes 4.362e-7, 1.538e-7 at N = 48, 64 are not
  confirmed; mine are 4.2346e-7, 1.3775e-7"): a third reading by the lead from the raw dumps
  (L2) gives 1.53836e-7 at N = 64, the waves value to 1e-6 of itself; verifier3's own
  projection route gives the same complex amplitude to 2e-16 (L2b). The difference is a
  definition: verifier3's summary keeps only the part of the mode in phase with the exact
  cos(K.x) (`v3_summary.py` lines 99-112) and reports the rest as "spatial quadrature"
  (plus: 7.2e-9, 1.27e-8, 1.61e-8 at N = 32, 48, 64; x10: 1.75e-9; cross 2.4e-13), which
  equals the waves-minus-verifier difference at every N. Both are right for their
  definition; neither is the truncation error, which is the cross value 1.399e-7 and the x10
  value of both polarizations (1.40e-7 to 1.42e-7). Its statement "plus and cross moduli agree
  to 2e-9" holds for the in-phase part only.
- What the track does with each of its items:

| Item | Verdict of verifier3 | Track's action |
|---|---|---|
| F5 / criterion paragraph: spectral Weyl vs TT "1.2e-11" | NOT CONFIRMED AS WORDED (6.0-6.4e-11 in its evaluation; forward combination only; h alone differs by theta^6/1120) | accepted; stage/G1 states "<= 6.4e-11 for the forward combination"; waves/README and ledger row 168 to say "forward combination" (owed by the next waves and note sessions, HANDOFF) |
| X1 plus amplitudes at N = 48, 64 | NOT CONFIRMED AS WORDED | resolved above: definition (complex modulus vs in-phase part); the README values stand as moduli, labelled rounding-limited; stage/G1 quotes the cross and x10 values as the truncation error |
| F2, F4, X2, X3: Weyl-6 levels depend on the stencil construction | CONFIRMED IN PART | accepted; the construction (gw_diag's sixth-order curvature) is to be stated next to the numbers (waves, next session) |
| X5, X6, X8, N1, N3: integrator attribution, background-error offset | CONFIRMED IN PART | the step test XS (run B-20261120-222841-acfe21d and -222849-e5673dc, done, not analysed) tests X6 and X8 directly; next waves session |
| N4, A1, the 2S predictor, F2, XS, AthenaK's own Psi_4 | NOT CHECKED | listed as open in stage/G1/OPEN.md; none is needed for criterion 1 as worded |
| Ledger row 101 (kinetic/gradient 0.00821) | NOT CONFIRMED AS WORDED (0.0088 over all dumps; driven shift 0.018) | accepted; note v3 changes the row (ledger.py, run_all, recompile) |
| Ledger rows 118-119 | CONFIRMED (reduction factors to 1 per cent); normalization s undefined | accepted; note v3 defines s and adds the direct-map row (residual 2.3e-5 to 2.7e-3) |
| Rows 120-125, eps = 0.1, 0.3 in rows 116-117 | NOT CHECKED | open for the G2 verifier |
| Its failed predictions P3.5, P4.5, P4.7 | on record in its JOURNAL | nothing to do |
| V4 residual after the gauge piece above the third-order estimate | [JUDGEMENT], untested | open item of G2 (gauge leg); RISKS R10 |
| Future scans in double-precision bin | request | adopted: the delta = 0.0025 and round-3 decks already write `dbin`; flrw_conv and population decks to do the same |

### waves (wave 2b, and the x10 check of round 1)

Confirmed: the committed final_results.json and x10_64_results.json equal their registered
outputs; their numbers agree with verifier3 (above) and, for X at N = 64, with the lead's
third reading to 1e-6 relative (plus and cross, x1 and x10; polarization-ratio errors
-1.0792e-7 in argument and -1.3947e-8 in modulus at x1, -1.094e-8 and -1.449e-9 at x10).
The x10 prediction (journal 2026-11-20 22:15) held: the plus excess falls 8.1-8.4 times, the
polarization-ratio errors 9.86 and 9.62 times; the plus excess of X at N >= 48 is rounding
in the data (1/A), not an artefact of either processing.
Not confirmed: nothing beyond the verifier's wording items. Defects: README still lists the
x10 check as pending and carries the two wordings above (small; owed by the waves session
that closes round 1, because the package is in progress).

### note (v1 of wave 2b and v2 of round 1)

Confirmed: figures and tables of v2 equal the outputs of registered run
B-20261120-223319-cc5320d (28 of 28); main.pdf has 21 pages; fig_waves.png and fig_r2.png
looked at; the note's numbers for criterion 1 agree with both readings (its ledger copies
the waves results). v1's recomputations (0.224, 0.222, 0.435 per cent; 32 vs 64 at most
0.086 per cent for 5 <= a <= 40) agree with verifier2's compare.json.
Not confirmed / to change in v3: ledger row 168 ("forward combination"), row 101 (0.0088),
rows 118-119 (define s; direct-map row); no reviewer subagent read v1 or v2 (the new-paper
procedure's step 4 does not apply to an edited draft). The note PDF is 1.15 MB, above the
1 MB guideline of the batch; it was tracked at 1.09 MiB before (request to orch).

### stage/G1/verifier2 (wave 2b; G1 runs of wave 2)

Confirmed: its numbers for NOT CONFIRMED item 2 (1.02 per cent at a = 75.8 for eps = 1;
1.9 per cent for the driven shift at a = 80) are in its compare.json; the note's linearity
row (0.000497, 0.00213) matches its item 1. Its twelve confirmed claims were not redone.
Track's action on its three NOT CONFIRMED items: (1) "linear in eps to 0.05 per cent" holds
for eps 0.1 against 0.3; eps = 1 departs by 0.2 per cent (fourth order): stage/G1 states it;
first_source/README to be reworded (owed, package in progress); (2) "32^3 and 64^3 agree to
0.5 per cent up to a = 80" is not a bound for eps = 1 (1.02 per cent at a = 75.8) or the
driven shift (1.9 per cent): stage/G1 states it; first_source/README owed; (3) plane symmetry
"1.3e-15 L": newton_tests/README now names the measure (done).

### population (wave 3a, partial; G3 design)

Confirmed: P3, P7, P9 numbers as reported (compare.json); figures looked at. The factor 3
of 2312.12499 (line 581: delta = (6/5)(a/a_hor) R; line 324 with the matter-era Poisson
relation gives (2/5)) is confirmed as a reading (L3; my prediction of a factor two failed).
Corrected: P5 mass ratios run to +14.3 per cent, not +12 (report). Figure defects: the legend
of pop_gw_fid.png covers the red curve; the square marked "halos of a = 20" sits at a = 30.
Open (not reviewed, not run): full-GR timing at 128^3 and 256^3 (0.3 card-hours), L = 8
initial data at three amplitudes (release core-v0.4 now has `<particles> id_solve` on uniform
meshes; whether it serves periodic cosmology data is to be read in its READY entry), the
G3 run list.

### first_source round 2 (results committed on 2026-11-19, used by note v2)

Not reviewed independently by the lead. The note's second reading (N13-N15, own s g, same
windows) reproduces the jittered-null, delta = 0.0025 and rerun numbers to 2e-12 relative,
which checks reference and bookkeeping, not the method; an independent verifier of the
second-round legs is G2 work.
