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
| V4 residual after the gauge piece above the third-order estimate | [JUDGEMENT], untested | open item of G2 (gauge leg); RISKS R4 |
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

# Batch 4a (lead of B-emd-gw, 2026-11-21 07:45-, PST)

Scope: the three packages finished since the lead session of batch 2a: `first_source`
round 3 (batch 2b), `waves` round 1 (batch 3), `stage/G1/verifier_c18` (batch 3). Still in
progress and not reviewed: `flrw_conv`, `shear`, `population` (HANDOFF.md). Method: the
helpers' reports were read first, so this is a recheck of the artefacts, not a blind one.
Predictions L4-L7 were committed (9015cd1f) before the runs; outcomes in
`review_wave3/JOURNAL.md` (2026-11-21T15:55Z); runs B-20261121-154933-a79da09 (L4, L5, with
verifier3's reader, TT projector and exact solutions, not the waves code),
B-20261121-155017-9aec47a (L6), B-20261121-155045-343bee1 (L7). All four predictions held.
Housekeeping: no stranded file; the worktree was clean at the start; no run was open.

## waves round 1 (F2, XS, x10, gw_diag gauge and reader modules)

Confirmed by the lead (L4, L5; figure `lw4_waves.png` of run -154933-a79da09, looked at):
- F2 (k = 2 pi (1,2,0)): with verifier3's code the last-dump TT amplitude and phase errors are
  the waves values to <= 2.9e-4 relative (amplitude at N = 64) and <= 1.7e-9 (phase); orders
  6.73/6.80/6.73 and 5.51/5.15/4.83 reproduced to the third digit. The comparison with the
  whole-Z4c symbol model (<= 0.12 per cent) was not redone (the model is waves' own).
- XS: the cross errors at dt_expansion = 0.001 (N = 16-64) are the waves values to <= 4e-5
  relative; with verifier3's own e(0.01) the time part at N = 64 is 1.42992e-7 (amplitude) and
  2.57038e-7 (phase), the waves numbers. XS-1 and XS-2 hold.
- The x10 outcome (plus excess at N >= 48 is rounding) was confirmed in batch 2a.
- gw_diag gauge module: equal to first_source's functions bit for bit (run
  B-20261121-125606-e2ebf60, ratio 1.1e-13 ... 7.2e-8 of G_tot to raw rms are the module's own
  numbers); tests 26 pass, 2 skip (as reported; not rerun).
Failed predictions on record (waves/JOURNAL.md): F2-4 per dump (Gamma at +k hits a floor of
1e-15 to 1e-14 at the nodes), XS-3 bound at N = 64 (2.76e-10 against 2e-10), XS-4 (the plus
rounding does not grow with the number of steps). Open, not blocking: the small-step
spectral-Weyl vs TT residual (6e-11, spikes 2.8e-10) is unexplained.
Verdict: G1 criterion 1 met for F, F2 and X with no open sub-item [lead's judgement, checked].

## first_source round 3 (P11-P14 at 32^3, P12, P13, the (1 + eps^2) test, P16')

Confirmed: the registered analyses rerun from their registered inputs give byte-identical
summaries (L6: conv_compare 142 values, p16_compare 137, none differs); this checks
reproducibility, not the method. The method-independent check is verifier_c18's (own code):
P12 7.76e-5, 7.44e-5, 3.35e-5, 2.51e-4; the (1 + eps^2) numbers; P16' D = 0.994, 0.856, 0.275.
Figures r2_conv_eps1.png and r2_p16_nowave_64.png looked at: as the README says.
Not confirmed independently: P16' per-shell fractions, (iv), (v); the 32^3 run without the
wave; P11 and P14 at 32^3 beyond the (1 + eps^2) numbers (verifier_c18's list).
Corrected (small): the P13 rms 1.3e-2 now names its window (80 <= a <= 140) and
interpolation in the README; verifier_c18 got 1.38e-2 with its own interpolation.
Decision of the helper not to run 128^3 at 8 per cell: accepted, not overruled [JUDGEMENT]:
after crossing the particle effect (1.4e-4) is a hundredth of the mesh difference (1.3e-2),
so the run would not change the conclusion; particle convergence at 128^3 is a G2 item.
Failed predictions on record (first_source/JOURNAL.md): P11(c') K2 A-ratio at 32^3, the
(1 + eps^2) test at a = 20, P14(c) at a = 10, P16'(i) and (ii) at a = 12, P16'(iv).
Open (G2): whether the extra grid-scale TT the wave adds by a = 12 is leakage of a
wave-modulated noise field or a response.

## stage/G1/verifier_c18 (item C18)

Confirmed: its summary reruns byte for byte from its committed results (L7); 116 numbers,
103 within 1 per cent, 113 within 5 per cent (figure a3_summary.png looked at; not in
figstyle, a style defect only); its line-125 statement is in p3_slicing.json as written.
It meets the brief of the package for the rows it took: the second-round table, gauge rows
116-117 (eps = 0.1, 0.3) and 120-123, line 125, line 101, wave-1 lines 26-27, round 3.
What the track does with each of its items:

| Item | Verifier's finding | Track's action |
|---|---|---|
| Line 125 | CONFIRMED in digits; 5.48e-5 is the initial slice (evolved 3.8e-3 to 0.0408) | note v3 rewords (owed; OPEN item 2) |
| Line 101 | 0.00857, 0.00821 hold over the 22 double-precision dumps; 0.00882 over all dumps | note v3 (already owed from verifier3) |
| Line 197 | CONFIRMED at about 1e-12 (second digit is rounding) | note v3 quotes "about 1e-12" |
| Lines 201-203, 206 | confirmed in substance with a growing-mode-only prediction (5 per cent ratios, 7 per cent phases) | accepted for G1 [JUDGEMENT]; a re-implementation with the decaying parts is not required |
| P13 rms | 1.38e-2 against 1.30e-2 (window and interpolation not stated) | README fixed (this session) |
| Line 124 (magnetic Weyl across gauges) | NOT RECOMPUTED | owed: verifier_c18b |
| Line 199 (residuals of the jittered data) | read from id.json, not recomputed | owed: verifier_c18b |
| Line 217 (second-reading bookkeeping) | NOT RECOMPUTED | owed: verifier_c18b |
| Wave-1 lines 34-36, 49-63, 70-71 (junk TT, omega_vir, cost; pancake; homogeneous; quadrature, second-order lapse) | NOT RECOMPUTED (line 34's slope -0.997 was confirmed by the G0 verifier) | owed: verifier_c18b |
| Round-3 P16' per-shell, (iv), (v); 32^3 without wave; P11, P14 at 32^3 | NOT CHECKED | lead's L6 shows reproducibility only; verifier_c18b takes P16'(v) and the per-shell fractions |
| Limit of independence: the track's definitions were read | recorded | accepted; reader, projection, reference and gauge piece are its own |
| Wrote VERIFIER-C18.md outside its directory | the package brief named that path | accepted |

Verdict on C18: met in part. Every row that carries a G1 criterion, the gauge rows and the
second-round table are now recomputed by an agent that did not produce them (G0 verifier,
verifier2, verifier3, verifier_c18); not yet recomputed: ledger lines 34-36 (in part), 49-63,
70-71, 124, 199 (residuals), 217. Owed: one more fresh verifier package (verifier_c18b,
processors only, artefacts only) or a ruling that these wave-1 scouting rows may be carried
to G2 (request to orch, this session).

## Batch 5 (2026-11-21, lead): verifier_c18b

Package `stage/G1/verifier_c18b/` (report `stage/G1/VERIFIER-C18b.md`), the second verifier of
item C18: ledger lines 34-36, 49-63, 70-71, 124, 199, 217 recomputed from the registered
outputs, processors only.

Checked by the lead from the artefacts (run B-20261121-203426-ea1e945,
`review_wave3/scripts/lb5_line59.py`, own reader of the cstat histories; figure
`lb5_line59.png` and the verifier's `pancake_c18b.png` looked at):
- CONFIRMED: line 59 as the verifier says. Largest Hr_mean over all records with
  22 <= a <= 42: 0.00751 (a = 22.56) and 0.00254 (a = 23.31); at the records nearest the five
  dumps: 0.00706 and 0.00203, the printed values. The printed numbers are right, the wording
  ("a = 22-42") was not.
- CONFIRMED: line 56 at the record nearest a = 10 (a = 9.962): 1.576e-4 and 3.216e-5; at
  a = 10.00 interpolated 1.641e-4 and 3.607e-5 (4 and 12 per cent higher), finding 3b.
- CONFIRMED: the verifier's pancake.py and small_rows.py, rerun from the registered outputs,
  reproduce its JSON files byte for byte.
- Not rechecked by the lead: lines 124, 199, 217 (finding 3e, 3f, 3g) beyond reading them;
  they do not change a printed value.

Verdicts and what the track does:
| Item | Verifier | Lead | Action |
|---|---|---|---|
| Line 59 | NOT CONFIRMED as worded | confirmed | reworded "at the five dumps after crossing (a = 22, 25, 30, 35, 41.9)" (ledger runs B-20261121-202548-3c3de2f, -203254-928275f) |
| Line 34 | CONFIRMED (1 per cent; grid ends) | accepted | reworded: ends of the 60-point grid (delta = 0.00255, 0.0495) |
| Line 56 | CONFIRMED (records nearest a) | confirmed | reworded: records nearest a = 10, 15 (a = 9.96, 15.02) |
| Line 63 | CONFIRMED; history file not in the run's inputs | accepted | the row names `runs/cosmo/dtexp_test/lim/flrw.cstat.hst` with its sha256 (ed6353a8ec0d794a...) |
| 3f Nyquist-plane momentum residual | finding | accepted, open | what AthenaK's differences do with it is not checked; recorded in OPEN.md (not a G1 item) |
| 3h exact-sheet crossing 21.029 | failed sub-prediction of the verifier | accepted | printed "21" unaffected |

With this and the v3 corrections of verifier3 and verifier_c18 (rows 101, 118, 125, 168, 197,
the (1 + eps^2) sentence with a new ledger row; run B-20261121-202758-544416e), item C18 is
PASS and nothing owed by the gate remains (stage/G1/OPEN.md).


## Batch 10a (2026-11-22, lead): card runs after 2026-11-21

No helper ran in this batch; the lead read the runs itself, from the registered outputs, with
figures looked at.

- flrw_conv J3 (B-20261121-202335-3e6a898, 128 cells to a = 1000, 2.00 card-h): confirmed from
  the output with the package's own analysis rerun (B-20261123-015452-18d2956); the 16-64 rows
  repeat the batch-6 analysis digit for digit. Outcome: G2 criterion (a) met at 16-128 cells;
  the entry-4 prediction "|e_D| at 128 at most a quarter of 64" fails (1.83e-6 against
  1.37e-6), floor attributed to the start step from 32-cell runs, J4 queued to test it at 128.
  Not confirmed: the cause of Hr growing about as N^2 with the mesh.
- shear series 1 (B-20261121-202830-417af0c): summary written and run by the lead
  (B-20261123-015919-dec4392). Confirmed: P5, P6, P11, P7 for S1, S2, S4, M1 and L1 inside the
  paper's bounds. Wrong against prediction: P4 Hamiltonian order (8.5, 14.3), S3 order, M2 sign,
  P12 convergence at small HL. Not judged: L2 (analysis NaN), P10 (guard stop).
- population: no GR run had been submitted. Cause found in the queue (silent wait on the 0.028
  data's outer tolerance, card entries in file order); corrected, pop_s014_gr on the cards.
  Defect of the sequencer (no log line while an entry waits) corrected in cards/sequencer.py.

## Batch 11 (2026-11-24, lead): runs read after batch 10a

No helper ran in this batch; the lead read every run from its registered outputs, with figures
looked at, against predictions written before the runs (journals named below).

- Sequencer: ended by itself on 2026-11-23 06:55 ("queue empty and every run closed"), after
  closing pop_s014_gr, the 0.028 re-solve, J4 and pop_s028_gr. It did not stall; it had nothing
  left. Restarted in this session with the new queue (below).
- flrw_conv J4 (B-20261123-015905-7a30278; analysis B-20261124-125457-79ce723, `analyze_step.py
  --set n128`, figure `flrw_conv/figs/fig_step128.png`): J4a, J4b, J4c hold. Confirmed: the
  amplitude floor at 128 cells is the start error of the step (0.001 - 0.002 = 1.19e-6, second
  order, 0.29 of the 0.002 error at 0.001), now tested at 128 cells and not only by analogy with
  32. Not confirmed: nothing. Figure defect: one tick label on the log axis of panel 3.
- population, re-solve of the 0.028 data (B-20261123-014850-7b7d986): R1, R2, R3 hold (first 18
  outer iterations identical; 9.1e-10 at outer 33; 67 min).
- shear, P10 (B-20261124-131336-bc61eee on a copy of series 1's S1_n64_lap1): holds, -8.7e-5
  against the 1e-4 bar; the f = 1 run carries the larger error (six times the f = 1/3 error at
  that mesh). Not confirmed: the k_x, k_z drift of 3.6e-3 over the stored track (it includes the
  blow-up after t = 0.54; not restricted).
- shear, L2: the cause of "no number" found from series 1's outputs (A rays had not reached x = L
  by tlim = 6; the four-ray window was built from two crossings). Fixed in `analyze_rays.py`;
  series 2 reruns L2 with tlim = 10.
- population, full GR (B-20261123-014847-f295ab4, -035002-bcc82bd; analysis -131918-e71996f,
  -133150-e9ef701; mosaic -133709-85c4be7): confirmed against fidL8 and the design (H1, H2, A1 to
  a = 30, Z); wrong against prediction: A1 from a = 36, A2 above 0.9 only to a = 72, the strain-rms
  half of A3, G1's cost (0.19 below 0.2), G1 for 0.028 (stop at a = 30.7). Not confirmed: what the
  high-k TT energy after halo formation is. Two analysis attempts failed on my own script (a
  dump written at the guard stop; a keyword clash in the figure step), both on record.
- shear series 2 and 3 (B-20261124-133702-4a06a52, -134209-4584052, summary -134720-c753aff):
  L2 = -0.828, -0.830, -0.835, near CosmoGRaPH and not converging (P9''b, P9 fail); S3 floor
  2-3e-5. The series-2 fan was too coarse (my design error, recorded).
- Follow-ups queued (predictions first): Newtonian reference at 128^3 (Slurm 5167), restarts
  X0-X3 of the 0.028 run (Slurm 5169), and through the sequencer the Newtonian analysis and the
  particle and mesh legs of the 0.014 GR box.
- shear L2 observer (B-20261124-135244-17ebf5c): the L2 field has relative constraint means of
  0.1-0.4 from a = 2.25 on at every N_y; the L2 values are not a converged statement. Schematic
  of the verification ladder (C10) drawn (B-20261124-135151-8e1ac95) and looked at; TT spectra of
  the GR box (B-20261124-134953-18618df): the excess starts at |k| = 4-5 k_f.
- shear series 4 and 5 (B-20261124-135516-34befaf, -135951-237e27b; summary -140808-e6ba5c3):
  the step does not move L2 (8e-5); particles along y do (1-8 per cell at N_y = 64: -0.830 to
  -0.821, converging near -0.820, beside CosmoGRaPH); N_y = 128 at 4 per cell -0.831. Wrong against
  prediction: series 4's 'Delta moves less than 2.1e-3' with 4 per cell, series 5's 'N_y = 128 within
  5e-3'.

## Batch 11b (2026-11-24 09:23-, resumed lead session): what ran after the cut of 07:20

No helper ran. The session before was stopped by the pause flag (sequencer log: flag present
from 07:20 to 09:20) with shear series 6 ended but not closed and the two stage verify results
uncommitted.

- stage verify G1 (`stage/G1/VERIFY_RESULTS.md`, 14:57Z, export of 2116dce): PASS, 0 failed
  checks, 11 of 11 scripts rerun, 22 regenerated files equal. Committed. G1 is signed already
  (coord/GATES.md); this is the formal rerun after the chains ended.
- stage verify G2 (same time): FAIL on one check only, 'runs': four runs open (card jobs 5167 and
  5169 held by the priority partition; the two initial-data solves still running). Everything
  else PASS. Not a defect of the package; rerun when those runs are closed.
- shear series 6 (B-20261124-140856-911ded9; closed by me with `nrpic-run finish`, exit 0, 27
  min on one core): reran the summary from the registered rays.json files of series 3-6
  (B-20261124-172623-03699f5, then -172643-d1e88c7 after a colour fix; `fig_ppc.png` looked at,
  both panels). Confirmed: Delta(256, 4 per cell) = -0.83915; mesh differences 9.4e-3 and 7.9e-3.
  The prediction (committed in 911ded99, before the run) holds as written but only just; the
  ratio 0.84 means no useful mesh convergence, away from CosmoGRaPH. SPEC section 7 item 5 ("within
  max(3 x own numerical error, 0.01) of -0.8183") is formally met if the own error is the last
  difference (0.0209 < 0.0237), but that error estimate is not reliable at order 0.25: judged not
  informative, L2 reported as not converged in this code.
- Defect found and fixed: `fig_ppc` drew the CosmoGRaPH line in the colour of a data series
  (fixed: grey). Defect noted, not fixed: the shear journal headings of 07:00-07:35 carry clock
  times about 1.5 h later than the registrations of the runs they predict (06:08 PST for series 6);
  the order (prediction committed before registration) is established by git, not by the headings.
- Initial-data solves for the particle and mesh legs (B-20261124-135029-3fe13f6,
  -135030-b54972f): running since 05:50, at outer iterations 16 and 13 after 3.6 h (13-16 min per
  outer iteration; the change of psi falls exactly as in the 128^3 one-per-cell solve). Not judged
  yet; the time part of I3 (256^3 in 3-8 h) will likely fail (about 9 h expected from the rate).
- Changed in the queue: the 256^3 GR leg writes restart files every 1.0 in t (decision 0032 item 2);
  the Newtonian reference moved from the held card job 5167 to two processor runs
  (B-20261124-172958-fc4a2cf, -73b0662, prediction N1p in population/JOURNAL 09:29).
- Newtonian reference on processors: 33 s per step on one core (about 13 h per run); the time part
  of N1p fails; card job 5167 cancelled before it ran (manifest 'failed, exit 1': it never started).

## Batch 17 (2026-11-25 03:46-, lead): the three population runs that ended in the shared queue

Checked from the artefacts (run directories, guard files, histories, analysis JSON, figures looked
at), each against the prediction committed before its registration (git: X0-X3 in cb0bb7d9f,
GD1-GD3 in 614abe3be, Q1-Q2 in 6d2c3b7b1, 05:35-05:50 PST on 2026-11-24; registrations 13:04 PST
and later). `nrpic-run finish` of the three runs hashes 45-62 GB each; the analyses were started
while it ran (read only) and the order is on record in the analysis manifests' purposes.

- q0005, X0-X3 (B-20261124-210432-6c4d005; analysis B-20261125-115619-ad8b3f4,
  `population/figs/pop_stop028.png`). Confirmed from `pop.guard.txt` of each case and the base:
  X0 stops at the base's time and cycle (9.086462674958188, 599), its history rows equal the base's
  to every printed digit; X1 stops at 9.07865; X2 reaches t = 10 with exit 0 and K < 0 everywhere
  from t = 8.48. X3 never started: `dt_lightspeed` is not in the restart's stored input and the
  command line may not add it. Wrong in the batch-11 design: X3 could not run as specified (setup
  error of that lead, on record; not retried, X2 answers the question). Not confirmed: whether the
  shifted 0.028 box lasts to a = 143 (q0044).
- q0004, gauge leg (B-20261124-210431-6bf48af; analysis -115558-2ab4161, comparison
  -120818-1dfae55, `population/figs/pop_legs.png`). Confirmed: t = 21.916 at cycle 1421, exit 0, no
  guard file, 11.1 min of card time. GD1 holds (time part fails: 0.185 against 0.2-0.5 card-h),
  GD2 holds for counts and fails for the largest masses (+10 to +16 per cent), GD3 holds in both
  parts (high-k Omega 950 times smaller at a = 121). The band ratio of GD3 rests on the per-shell
  Omega spectrum divided by the shell's squared wavenumber, an approximation inside each shell
  that is common to both runs (`compare_legs.py` header); the exact mode sums are in the JSON as
  rms_raw, rms_cor over all k only.
- q0006, particle leg (B-20261124-223926-33194d9). Confirmed from chain/events.log: two segments
  cut by SIGTERM at 15:42 and 17:08 PST, the chain ended FAILED at its cap of two segments
  (the v0.6 chain script counts a signalled attempt), last row t = 17.477 (a = 94.8), newest
  restart rst/pop.00008.rst (t = 16.0). Closed as failed; the continuation is a new run (q0042).
  Analysis to a = 94.8: B-20261125-115657-91b61ec (see the next paragraph when it ends).
- Initial-data solves of the legs (B-20261124-135029-3fe13f6, -135030-b54972f), prediction I3 not
  judged before: HOLDS (outer change 8.3e-10 and 8.4e-10, Hamiltonian residual 2.1e-11 and
  3.2e-11, both below 1e-7 and 1e-9; the 256^3 solve took 6.1 h, inside 3-8 h). Wrong in the
  previous HANDOFF: "the time part of I3 likely fails" (it holds).
- Defects of this session: a log of a background `nrpic-run finish` was written to
  `scratch/B-emd-gw/tmp_finish_p8.log` instead of `scratch/B-emd-gw/tmp/`; one `finish` was cut
  by a 110 s timeout before it wrote anything (manifest unchanged, rerun in the background).
- Particle leg analysis (B-20261125-115657-91b61ec, comparison -121830-9ecb59c): judged in
  population/JOURNAL 04:20 (Q1 part 2 fails, Q2 counts hold, mass at a = 64 fails); the particle
  leg's finish ended with status failed (exit 1, the chain's cap), 127 files checksummed.
- Stage verify G2 without checksums (export of 37439b2, 12:10Z): every check PASS but 'runs': seven
  runs not yet closed at the export (five finishes still hashing, the mesh leg in Slurm, one
  analysis running). Not a defect of the package; the full verify with checksums waits for q0007,
  q0042, q0044 and the five finishes. G2 is not complete (stage/G2/OPEN.md); not listed for review.

## Batch 21 (2026-11-25 08:56-09:30 PST, lead, processors only)

Package reviewed: population, the Newtonian reference at the GR runs' own particles (processor
runs B-20261124-172958-fc4a2cf, -73b0662; analysis B-20261125-122434-060d53d, started by the lead
of batch 17 and left running). Checked from the artefacts: the analysis ended with exit 0 at
12:49Z (`.nrpic/result.json`), closed with `nrpic-run finish` (8 files hashed); its copies in the
package (`results/analysis_n128.json`, three figures) were uncommitted and are now committed. The
lead reran the comparison against both GR gauges (B-20261125-165836-70b17b6, -165845-0621554),
recomputed every N2-N4 number from their JSON, looked at both figures, and tested the N4 failure
in three further registered runs (band test, same particles through one estimator, radiated part).
Predictions were written before each run (population/JOURNAL 2026-11-25 08:58, 09:00, 09:03,
09:05, 09:24).

- Confirmed: N2 in both gauges (counts in band at every catalogue; at a = 121 ten of ten matched,
  median |dM| 2.5 and 2.8 per cent); N3 (Newtonian amplitude scaling, counts in band, largest mass
  within 4 per cent at a = 25-60); the GR and Newtonian particles move alike (velocities within
  0.3-0.6 per cent, positions within 0.002-0.08 cells to a = 36, B-20261125-170535-84c9ba5).
- Wrong in the package, found here: `analyze_gr.py` `hqs_particles` deposits the GR particle file's
  rest-mass weight (m W psi^6 ..., `make_ic.py` line 133; spread 2.8 per cent) as mass. Its
  quasi-static estimate is high by 11.6 times at a = 2.3 and 1.14 at a = 36; with equal masses the
  GR and Newtonian particles agree within 6 per cent. Every earlier use of `Omega_qs_part`,
  `spec_qs`, `cmp_*_qs` (A1-A3 of 2026-11-24, GD3's "particles' estimate" and the ratio "5.4e-7
  against 8.3e-7 at a = 121") is not a reference until rerun. Large defect: listed (OPEN.md C9),
  not fixed here (an hour of processors with a prediction first).
- Wrong in the batch-17 review and CHECKLIST C9: "the two gauges bracket the Newtonian mass"
  (against fidL8, other particles). With the same particles the zero-shift masses are the closer
  ones (largest halo -2 to -5 per cent, Gamma driver +7 to +11). Withdrawn in C9 and in the note.
- Failed predictions of this session: N4 as written in both parts (quasi-static: cause found;
  radiated: 0.29 against a factor 2, cause not tested), GN1 (gauge order of the masses), GN2 after
  a = 36, NB1 (the excess is not the grid), VC1 second part, VC2 side statements. One defective
  analysis on record (B-20261125-170051-49ada01, unlike units; rerun -170116-0b635a0).
- Not confirmed: why the radiated measure does not follow the sigma^(7/2) map between the two
  Newtonian boxes; the gauge dependence of FoF masses by a proper-distance mass.

G2 products without a card, this session: one data figure and two schematics for the note
(B-20261125-171148-563a6f0, looked at; C16 PASS), the G2 section of the note with ledger Table VIII
(checker with --compile clean on the new text, pages read), the reproducibility list
`stage/G2/REPRODUCE.md` (C6 PASS), the ladder schematic's SVG committed from its run. C15 stays
open (package scripts that draw several figures). Stage verify without checksums: every check
PASS except 'runs' (q0007's chain B-20261125-093500-242d3a3 is in flight).

Queue entries waiting for a card, nothing partial read: q0007 (job 5283 pending), q0042, q0044.
