# Review of the wave-3 packages of F-hills (lead, batch 2a, 2026-11-21)

Lead of F-hills, worktree `wt/F-hills`, main merged at 9ce19873 (release core-v0.4). Checked from
the artefacts (run outputs, scripts, figures), not from the packages' conclusions. Predictions
of my checks (L1-L3) and their outcomes: `../JOURNAL.md`, entry of 2026-11-21T06:35Z, written
and committed (4dcca98f) before the checks ran. My script: `review_wave3/review3.py` (own
parsers and integrators; it imports none of the packages' readers). Labels as in the brief.

| Lead run | What | Outcome |
|---|---|---|
| F-20261121-063449-4dcca98 | L1: P1 trackers and horizons parsed from the raw files | merger at t = 48.8 M confirmed |
| F-20261121-063504-00f0743 | L2: arithmetic and S1 arrays behind the verifier's WRONG items | D3, D5, D6, D7 confirmed; SCOPING lines of D4 found |
| F-20261121-063520-abab33e | L3a: rerun of `eih/tests/test_eih.py` | 9 of 9, 346 of 346 values identical |
| F-20261121-063527-b4453db | L3b/c first attempt: own 1PN two-body and test-mass parabola | T5 reproduced; parabola check FAILED by my method (E_1PN = 0 imposed at pericentre) |
| F-20261121-063646-d826df4 | L3c second attempt (E_1PN = 0 at r0 = 1e4 M) | eih T4 reproduced to 1e-9 |
| F-20261121-063712-25981e0 | rerun of the verifier's ledger recomputation (`verify_g0/scripts/ledger_check.py`) from its registered outputs | 56 of 57 rows identical; row 57 has a stale locator (release core-v0.4 moved the paragraph) |

Figures read: `fig_review3_p1.png`, `fig_review3_g0.png`, `fig_review3_eih.png` (lead runs above);
`verify_g0/figures/fig_scan.png`, `fig_scales.png`; `fig_ledger_passages.png` of my rerun;
`eih/figures/fig_p1_q4.png`; `p1/figures/*` were read by p1 (I relied on my own figure).

## Packages finished since the last lead session

### verify_g0 (batch 1; `stage/G0/VERIFIER.md`, 20 claims, ledger C18, ten defects)

Confirmed by me:
- Its ledger recomputation reruns from its registered outputs to the same 57 rows (56 identical;
  row 57 differs only because `coord/INTERFACES/multi_puncture.md` was rewritten by core-v0.4
  after the verifier read it; the new text, lines 235-247, says "about 3100 slots with three
  finders", which is the verifier's own D5).
- D3 (G2 items sum to 131, 134.8 with the m/16 row), D5 (26.24 MiB per slot, 3122 slots), D6
  (4 q^(2/3)/2.085 = 14.14 at q = 20, 18.52 at q = 30), D7/N1 (a/R_curv 0.1993 at any time,
  0.0056 while bound, beta = 10 prograde; `fig_review3_g0.png` shows the bound-pair maximum
  flat near 5e-3 and the any-time value rising to 0.2 with beta), D4 (SCOPING l. 50, 114, 185
  named q = 10): all VERIFIED by run F-20261121-063504-00f0743.
- D5 further: g2mesh's card job (run F-20261120-222810-e408386, Slurm 4744, finished by me in
  nrpic-run; not yet analysed by its package) ran the q = 4 m/16 mesh with
  `max_nmb_per_rank = 3000` for 64 cycles at a peak of 78785 MiB of 81920
  (`m16_b16_s3000/athena.20261120-163047.log`), so 3000 slots fit one card and the largest
  q = 4 m/16 tree (2864) fits [VERIFIED by reading the log; the package's judgement pending].
- K12/D1 agrees with my wave-2b V9 (5.775 M, run F-20261119-145449-245e984).
- Its figures `fig_scan.png` (V7 lines against its own scans; the release-at-4 r_t points sit on
  V7, the 10 r_t points off it at r_p = 12-13 M) and `fig_scales.png` (plunge bound and the
  weaker separation bound; V^2 curves of the q = 10 start state in three readings) show what
  sections 1 and 4 say.
Not confirmed by me (not rerun): K1 (novelty; a search, judged by its limits), K2, K5 (its own
integrators; I reran only its ledger check), K13 scans themselves (I read their summaries and
figure), the kb searches.
Wrong in the package: nothing found. Its section-4 statement that V7 is right for its own
construction stands; the K13 verdict "PARTLY" is a statement about the plan, not about V7.

What the track does about each item the verifier marked WRONG, PARTLY or NOT DONE:

| Item | Verdict | Checked at the source by the lead | What the track does |
|---|---|---|---|
| K4 / D8 KHSR (1201.4794) not reproduced | NOT DONE | newton3/README.md:46-50 (energy combination only), :404-406 (non-parabolic orbits not done) | Accepted. SCOPING 5 (G1 (i)) now says so and plans one KHSR result (ejection against the eccentricity of the centre-of-mass orbit, ms.tex:1140-1152) at G1 with the newton3 driver (`e_orb`, processor minutes). G1 OPEN item. |
| K6 / D6 plunge bound read as a separation condition | numbers right, logic PARTLY WRONG | own arithmetic (L2d) | Accepted. SCOPING 4 amended; errata row 1.5 rewording asked of orch (outbox). |
| K12 / D1 r_p stated in Newtonian terms only | WRONG in effect | own V9 (wave 2b) and L2 | Accepted. SCOPING 3 and 6 give the GR turning points (9.25 M at q = 4; 5.77 M at q = 10, bound CM) and the rule for scan lines (GR parabola in the puncture reading). Note: correction listed for the note's resume (Sec. II text). |
| K13 / D2 V7 numbers not reproduced at r_p = 12-13 M with the plan's start rule | PARTLY | its figure and summaries; its H-k0 result (V7 reproduced with V7's own construction) | Accepted. SCOPING 4 quotes the percentages only with their construction and states that they are properties of it near the separation edge; SCOPING 3 requires one start state for the NR data and both references of a scan line. Errata row 1.5's "69 percent at 12 M" asked to be qualified (outbox to orch). |
| K14 / D5 "2864 is above the 2700 slots of one card" | WRONG as worded | L2b; core-v0.4 interface l. 235-247; g2mesh's card log (3000 slots at 78785 MiB) | Accepted. SCOPING 9 corrected: 2700 was the smoke input's limit; 3000 slots fit; q = 4 m/16 fits one card. |
| K15 / D3 G2 compute "about 120" | WRONG (131-135 before contingency) | L2a | Accepted. SCOPING 9: corrected sum, and a G2 plan of about 100 card-hours inside the 120 (the second large-r_p passage and the 3BH1 rerun move to G3), to be re-costed after P1's merger (below). |
| K16 / D4 SCOPING names q = 10 for the first passage | WRONG in SCOPING | L2e | Accepted. SCOPING 3, 6, 9 follow decision 0013 (q = 4); section 6 records P1 and its outcome; the q = 10 paragraph is kept as the wave-1 record. CHECKLIST C9 evidence amended. |
| N1 / D7 note main.tex:140 "small ... throughout" | WRONG | L2c | Accepted. Sentence corrected in `note/main.tex` (Sec. IV B); SCOPING 4 and 11, RISKS R5 carry the consequence; the ledger row (second number 0.199) listed for the note's resume (`note/JOURNAL.md`, lead entry 2026-11-21). |
| N2 / D10 inner retrograde point "still to be followed" | closed at D = 0.1 by the verifier | its run F-20261121-030155-1061bcb (summary) | Accepted; `note/main.tex` Sec. IV A corrected (the second inner point is not rerun). |
| N3 errata row 1.5 says "captured" for a plunge | wording | brief errata row read | Accepted; in the outbox to orch. |
| K3 / D10 BKRS "to about their stated accuracy" | generous | its numbers (0.015, 0.017 against 1 percent) | Accepted; note text now says "about one and a half times their stated accuracy". |
| K11 / D9 two precision remarks (0.9703 drifts; 97.1 is the first sample inside) | precision | its run F-20261121-030138-8d3ca16 (summary) | Accepted; ledger rows listed for the note's resume. |
| K20 / C18 table 3 not checked | for G1 | - | Table 3 goes to the G1 verifier. |

### eih (wave 3a; 1PN three-body reference)

Confirmed by me: the test suite (9 of 9, every recorded value identical, run
F-20261121-063520-abab33e); T5 with my own relative 1PN equation (radial eccentricity of a
Newtonian-circular binary 0.1217 at a = 30 m_b and 0.2080 at 20 m_b, equal to eih's); T4 with my
own 1PN test-mass integration and my own Schwarzschild quadrature (error of the relativistic
excess -0.393, -0.268, -0.196, -0.088, -0.035 at areal r_p = 8, 10, 12, 20, 40 M, equal to eih to
1e-9; Schwarzschild angles equal to 1e-12). Its P1 prediction figure (`fig_p1_q4.png`) shows no
model with a merger: every reference keeps |x1 - x2| above about 3.7 M to t = 300 M.
Not confirmed: the phase scans (scan, scan_far), the 1PN-consistent start states and their
`<problem>` blocks (not rerun), the claim that Bowen-York momenta are canonical 1PN momenta
(eih labels it TO VERIFY; it is a question for core).
Wrong: nothing found. One addition from my failed first attempt (run F-20261121-063527-b4453db):
imposing E_1PN = 0 at the pericentre instead of far away turns the 1PN parabola into a hyperbola
that deflects LESS than Newton at r_p = 8-40 M (excess error -1.1 to -1.6); this is eih's
"truncation ambiguity" in its starkest form and argues, with eih's request 1(a), that a
1PN-consistent start state must be built far out and integrated in, not matched locally.
Use: eih's trust ranges (1PN controlled beyond about 25 M areal, sign-and-size between 12 and
25 M, no reference inside 12 M) enter the plan; its P1 expectation ("m1 enters the GR capture
region") is moot because P1's binary merged first.

## Packages cut on 2026-11-20 (round 1; not reviewed in full, state for HANDOFF)

- **p1** (journal entries 0-4 and README; the intermediate analysis to t = 112 M was finished but
  uncommitted: committed by me, bb68684b). Its main result, the merger of the binary at
  t = 48.8 M, is CONFIRMED by my own parser (L1): separation below 0.1 M at 48.79 M; common
  horizon 0.2686 (finder 0, t = 48.81) and 0.2693 (finder 1, t = 49.06); beyond p1's range the
  remnant is closest to the heavy hole at t = 154.6 M (7.0 M coordinate distance) and recedes
  (16.9 M at t = 236). My prediction's clause "separation decreasing monotonically to 30 M" failed
  by a wiggle of 3e-4 M. Open in the package: analysis beyond 112 M when the chain ends; the
  resumed-chain predictions (entry 1); `REQUESTS.md` items (posted by me to orch and core).
  Cause of the merger [JUDGEMENT, TO VERIFY]: the members' resolution at m/8 (E3 measured coordinate
  speeds of 0.52-0.76 of the boost at the same resolution and gauge); no reference merges, and the
  gravitational-wave inspiral time is about 3400 M. Deciding test: the isolated binary at m/8 and
  m/16 for about 60 M (processor or card; next round).
- **junk_gauge** (committed to J4's prediction): E10 analyses ran (runs F-20261120-222403-b8dc28c,
  F-20261120-222415-137ada9) but E10's outcome is not yet in `nr_first/JOURNAL.md`; the junk of
  one member E/m = 7e-5 (range 4e-5 to 2e-4; runs F-20261120-222808-b65001c, -223018-a5c0838,
  -223121-c921d2d); J4 (junk of the three-hole data at P1's spheres) predicted, not measured. Not
  reviewed by me; to review when the package closes. Note for J4: P1's spheres also carry the
  merger signal after t = 48.8 M.
- **kerr** (everything uncommitted: JOURNAL entries 0-1 with predictions, `hrna_incl.py`, two
  tests, two scripts): no outcome yet. Left uncommitted as instructed; listed in HANDOFF.
- **g2mesh** (G2M-1 outcome committed; G2M-1b predicted; `scripts/card_analysis.py`
  uncommitted): its card job ran (above); the analysis of G2M-2 is not done (the m8_b32_s1150
  case aborted, rc 134).
- **note** (paused, committed): the G1 revision of `main.tex` is written; the registered rerun of
  `run_all.py`, the compile, the checker and the reading of the pages are not done. I added two
  text corrections and a list of ledger corrections (`note/JOURNAL.md`, lead entry). Requests of
  the note helper to the lead (WRITING_GUIDE allowed numbers eta m = 2 and 0.25, P = m/4, cells m/4;
  the outline split of the tests section): accepted, applied to `WRITING_GUIDE.md` by me.

## The G0 package

With VERIFIER.md (C18 for the plan: 20 claims, ledger tables 1-2 recomputed 57 of 57) and every
WRONG item corrected in SCOPING, the note's text and the risk list (or listed for the note's
ledger rerun, which does not change a G0 number: tables 1-2 change only by the precision remarks
D9 and the second alpha value), the G0 package is complete for an independent review under
decision 0016 item 4 [JUDGEMENT]. The harness verdict still fails on three wave-2 run
directories with moved-in outputs (waiver asked of orch since 2026-11-19, repeated) and on runs
in flight (P1's chain).

---

# Review of the packages finished in batches 2b and 3 (lead, batch 4a, 2026-11-21)

Lead of F-hills, main merged at 4b1194b1 (releases core-v0.4 to v0.6 on main). Checked from the
artefacts, not from the packages' conclusions. Predictions L4-L6 and their outcomes:
`../JOURNAL.md`, entry 2026-11-21T15:55Z (predictions committed in 2539625e before any check
ran). My script: `review_wave3/review4.py` (own parsers of trackers, horizons, history and
waveforms; own ADM 1PN Hamiltonian and harmonic EIH; own fixed-frequency integration; it
imports none of the packages' readers).

| Lead run | What | Outcome |
|---|---|---|
| F-20261121-155018-620fe7f | L4a-d: binary_conv separations, horizons, H-norm2 from the raw files; own 1PN and Newton | separations equal; my 1PN differs from the package's reference (below) |
| F-20261121-155353-e4d3354 | L4f: three 1PN variants of the isolated binary | package's EIH reproduced to 5e-5 M; the variants spread by 0.16 M at 20 M |
| F-20261121-155442-5f15a25 | L4e: rerun of binary_conv's registered analysis | identical in every key |
| F-20261121-155457-5f36517, F-20261121-155549-4359678 | L5, L5b: own FFI energy of P1's junk window | within 8 percent of junk_gauge; 75-83 percent of it is a steady emission |
| F-20261121-155605-7d21f63 | L6a: rerun of kerr T8 | identical (232 values) |
| F-20261121-155614-7997653 | L6b: rerun of kerr's 2402 analysis | identical (6772 values) |

Figures read: `fig_review4_bc.png`, `fig_review4_pn.png`, `fig_review4_junk.png` (lead runs);
`t8_bks_chart.png`, `fig_incld.png` (reruns); the packages' figures named below.

## binary_conv (batch 3; partial: R16n segments 2-3 and R12 queued)

Confirmed by me:
- The separations of P1, R8 (m/8 alone) and R16n (m/16 alone) in BC-3 to 1e-4 M at 2.5-20 M;
  the largest |s_R8 - s_P1| 0.0930 M at 20.94 M; Delta s ratios R8/P1 0.670, 0.812, 0.865 at
  7.5, 15, 20 M. So the m/8 binary decays like P1 without the heavy hole, and the m/16 binary
  does not decay over 0-7.7 M (Delta s 0.004 M against R8's 0.066 M at 7.5 M) [VERIFIED].
- Horizons: R16n member masses flat (0.12736-0.12768 in every search, fitted drift below 1e-5
  per M); R8 masses rise (absolute 1.3e-4 and 1.9e-4 per M). R8's H-norm2 sample 18292 at
  t = 0.5 (P1 5.99) and 10.9 at t = 1.0 [VERIFIED].
- The registered analysis repeats exactly (L4e); the Newtonian reference repeats to 1e-4 M.
Not confirmed:
- "R16n follows EIH within 0.006 M" as evidence of accuracy. The package's EIH-canonical
  reference is reproduced exactly by my EIH with the exact inversion v(p), but two other
  1PN-equivalent references from the same data (ADM Hamiltonian; EIH with the truncated v(p))
  differ from it by 0.019 M at 7.5 M and 0.158 M at 20 M (L4f). The members move at
  0.11-0.33 c, so the 1PN truncation is not sharp at this level. R16n lies +0.019 M from my
  ADM reference at 7.5 M, R8 -0.043 M.
- Hence the two-point order ">= 3.3 (deviation from EIH)" is not established: with the
  continuum Delta s(7.5) anywhere in the 1PN spread (0.004-0.023 M) the m/8 and m/16 errors
  give an order anywhere above about 1.2. The 3.96 from the Delta s ratio assumes a continuum
  Delta s of zero. Only the three-point (R12) or later R16n data decide the order.
- The verdict "m/16 survives 100 M" (BC-4 item 2) is an extrapolation from 7.7 M with an order
  not established; with p = 1.2 the m/16 merger would come near 110 M.
Wrong (small, corrected in this review, not in the package's files): the README and BC-3 give
fractional mass drifts (d ln m / dt: 1.0e-3, 1.4e-3 for R8; -7e-5, -5e-7 for R16n) labelled "per
M" as if absolute. My threshold (hrms < 1e-3) rejects 58 and 41 R16n searches whose masses are
within 1e-4 of the rest, so "found in every search" holds in substance.
What the track does: decision on P1b below (not submitted); the BC-5 check "refuted if R16n
departs from EIH by more than 0.05 M by 20 M" is replaced by the lead's decision rule P1b-D
(JOURNAL, this session), which needs no 1PN reference.

## junk_gauge (batch 2b; closed)

Confirmed by me:
- J4b's energy in the window u in [-35, 6] M: my own FFI gives 2.64, 2.48, 2.26, 2.35 e-6 M at
  40, 48, 70, 90 M, 0.92-0.95 of the package's; l >= 4 share 0.69-0.71 [VERIFIED].
- It arrives at the same retarded time at every sphere (outgoing radiation) [VERIFIED, figure].
- J4 "as written" refuted by P1's merger burst (my L1 of batch 2a shows the merger at 48.8 M;
  not recomputed here).
Not confirmed / qualified:
- The reading of the window's energy as the junk of the three-hole data. The cumulative
  energy rises quickly only over u of about -33 to -28 M (0.40-0.63e-6 M at the four radii)
  and then steadily at 5.0-5.4e-8 M per M at every radius to the end of the window (L5b):
  75-83 percent of the 2.2-2.8e-6 M is a steady outgoing emission, not a burst of the initial
  data. Its source is not identified; P1's numerically decaying m/8 binary (separation 4.95 to
  3.36 M by t = 30 M) is the likeliest feed [JUDGEMENT]. So for G1 T3 the three-hole junk is
  0.4-0.6e-6 M in its first 7 M of retarded time (l <= 8, FFI 0.2/M), with the window total
  2.2-2.8e-6 M as an upper bound in time and the l <= 8 cut as a lower bound in l.
- The single-member junk (E/m = 7e-5) and E10: not rerun by me (the package's figures read).
- The gauge recommendation (mass-scaled profile): a judgement; binary_conv tested the constant
  shift_eta = 2 at m/16 instead. The track keeps the constant gauge for P1b (comparability
  with P1 and with R16n) and moves the profile arm to the G2 gauge leg [JUDGEMENT].
Wrong: nothing found in the numbers.

## kerr (batch 3; closed)

Confirmed by me: T8 and the 2402 analysis repeat exactly from their registered inputs; the
figures show what the README says (InclD: L_z > 0 at beta = 0.52-0.68 one to three steps more
stable than the paper, the other families within one step; T8: the 'cks' runaway of the
retrograde a = 0.9 binary and the 'bks' chart following 'sch'). My own estimate of the slicing
pump has the package's coefficient 2M/r [JUDGEMENT].
Not confirmed (not rerun): T5-T7, R3, the scan itself, the spin trend and its reading, the
digitization of the paper's figures. Consequence for earlier results: geodesic_binary S4 (Kerr,
equatorial, chart 'cks') may carry the pump; it is not a G1 claim and is listed for rerun in
'bks'. The Schwarzschild results of T2 used 'sch' and are not affected.
Note on rule 9: `kerr/results/paper_2402_digitized.json` holds marker coordinates read from the
paper's figures, with locators (numbers, not the figures or the source) [JUDGEMENT: allowed];
named to orch for awareness.

## Packages still cut (not reviewed; state in HANDOFF)

p1 (analysis to 280 M; P1's chain ended DONE at t = 280 M on 2026-11-21 01:19 PST and is
finished in nrpic-run by me in this session), note (paused), g2mesh (`scripts/card_analysis.py`
uncommitted, left alone).

## Batch 5 (lead, 2026-11-21 afternoon): binary_conv's queued chains read; rule P1b-D

Rerun from the registered outputs: analysis F-20261121-202021-3c4321e over R8
(F-20261121-130358-6cf186a, to 20.94 M), R12 (F-20261121-153707-1eaa5d4, to 21.06 M) and R16n
(F-20261121-130351-04074e1, to 23.34 M); both chains closed in nrpic-run (completed; 60 and 52
files checksummed). Figures read: `fig_orbit_conv.png` (the m/12 curve lies under the m/16 curve
throughout; m/8 apart), `fig_horizons_H.png` (masses flat at m/12-m/16, rms H 6e-4, 1.4e-4,
4.5e-5 for m/8, m/12, m/16).

| binary_conv claim or prediction | verdict | what the track does |
|---|---|---|
| BC-1 item 2: R16n's Delta s(15) at most half of R8's 0.305 M | CONFIRMED (0.0865) | - |
| BC-4 item 2: R16n departs from EIH by at most 0.05 M by 20 M | WRONG (0.174 M) | replaced before the data by rule P1b-D (batch 4a); recorded as failed |
| BC-4 item 2: m/16 survives the 100 M of a passage ("merges after 500 M; even p = 2: 210 M") | NOT CONFIRMED; the extrapolation is refuted as reasoning: the decay left at m/12-m/16 does not shrink with resolution (stretch fit: merger at 93-97 M) | R16n extended to 120 M beside P1b (run B); RISKS R19 |
| R12 decides whether m/12 suffices (BC-5) | CONFIRMED that m/12 = m/16 for the binary alone within 0.002 M to 21 M | P1b at m/12 queued as the second resolution of the passage (run C, held) |
| member masses flat at m/16 (BC-1) | CONFIRMED (-3.9e-5, -5.5e-5 per M) | - |
| README "Results" table, separation at 20 M "(queued)" for m/16 | outdated | numbers above; README to be updated by the next binary_conv session |

Rule P1b-D: clause D1 holds (monotone 0.305 > 0.088 > 0.0865 M; p = 12.0; continuum loss
0.0864 M at 15 M); D2 applies only without R12 and would fail (0.196 > 0.10 M). P1b submitted
(F-20261121-203144-b2cf16b). Details and predictions: JOURNAL.md, batch 5.

# Batch 11 (lead, 2026-11-24): khsr_note reviewed; the card chains A, B, C read

## khsr_note (batch 6; closed; reviewed from its artefacts)

Rerun from the registered scan F-20261121-212757-77cdc15: `khsr_note/scripts/fig_khsr.py` (run
F-20261124-133112-db7d6b8) reproduces `khsr_note/results/khsr_checks.json` in all 1268 values;
`fig_khsr_ecc.png` read. K1 and K2 rederived by hand from KHSR's definitions (JOURNAL.md, batch
11, L-K) without the package's code. Source read: kb-data raw 1201.4794 v1 `ms.tex` 618-630,
737-778.

| khsr_note claim | verdict | what the track does |
|---|---|---|
| K1: E_bar = -2.667 at r_a/r_t = 100 (printed -2.7, ms.tex:746) | CONFIRMED (own derivation; r_a is the semi-major axis of the centre-of-mass orbit) | - |
| K2: start radii 12.22 and 17.42 r_t (printed 12.2, 17.4, ms.tex:624-626) | CONFIRMED (own Kepler and hyperbolic times at r_p = r_t: 12.22, 17.40) | - |
| K3a/K3b: no preference with the parabola; prograde ejection to 0.45-0.57 of P_dis and secondary preferred (0.08-0.15) at r_a/r_t = 100 | CONFIRMED from the registered outputs and the figure; matches ms.tex:756-769 qualitatively (KHSR gives no numbers there) | a second agent's check of K3 from the script and the scan is part of the G1 verifier (C18) |
| K3c/K3d: parabolic approximation within 0.012 except at D = 2 | CONFIRMED as stated (failed predictions on record) | - |
| P1 to 280 M (remnant at 6.99 M at 154.6 M, no common horizon, H flat, 2-3e-3 M radiated) | NOT RECHECKED by me in this session (numbers in `khsr_note/results/p1_280.json`, runs F-20261121-212240-c43f35f, -212441-1911b7d) | to the G1 verifier (C18) |
| Note v2 compiled (24 pages), figure run F-20261121-214141-256f945 | the copy into `note/` done by me (README section "Version 2"); compile and checker not repeated | `nrpic-stage verify` reruns the note's figure scripts |
| Cosmetic: right panel of fig_elliptic repeats the legend; floats after Sec. VI | open, small | note v3 |

## The card chains (decision 0026 item 4; JOURNAL.md batch 11: Q1-Q4, N1, N1m)

Registered analysis F-20261124-130009-33bef4d (`stage/review_wave3/b11_cards.py`, my own reader
over nrread's tracker join; figures `fig_b11_binary.png`, `fig_b11_health.png` read) and the
Newtonian references F-20261124-132934-375a163 (`b11_n1_tide.py`, `fig_b11_n1_tide.png` read).

| run, prediction (written before the run) | verdict |
|---|---|
| B (R16n extension), batch 5: reading E (minimum 2.5-4.6 M at 40-100 M, then a rise) | CONFIRMED: minimum 3.120 M at 73.9 M, 4.585 M at 107.85 M |
| B: no common horizon before 120 M; masses below 1e-4 per M | CONFIRMED to 107.85 M (the chain was cut there); masses -1.0e-5 to -5.5e-5 per M |
| A1: no common horizon of the members before 60 M | CONFIRMED (s = 2.74 M at 61.86 M) |
| A2: A within 0.05 M of R16n to 20 M | CONFIRMED at the edge (0.042 M) |
| A3: separated binary by 200 M | NOT JUDGED (A cut at 61.8 M; A2 continues) |
| A4: member masses drift below 1e-4 per M, no member near M | CONFIRMED for A; FAILS for C (1.2e-4 to 1.7e-4 per M) |
| A5: below 2864 MeshBlocks, fits the card | CONFIRMED (max 2584; 78787 MiB) |
| C: A and C agree within 0.02 M | CONFIRMED to 22.3 M (0.0023 M) |
| lead Q1 (merger at even odds) | WRONG: no merger |
| lead Q2 clause (A within 0.1 M of B to 61.8 M) | WRONG: -0.53 M at 60 M; cause not named (N1, N1m: tide plus heavier members match the size at 40-60 M, not the early part) |

Chains: A, B and C were cut by preemption (another user's `priority` partition, one job every
5-30 min for nights) and their segment caps; they are closed as stopped (A, C) and continued as
A2, B2, C2 from their newest restart files with restart files every 1-1.5 M (JOURNAL.md, batch
11, "Q4 decision").

## Packages still in progress

g2mesh (cut on 2026-11-20; G2M-1b prediction written, G2M-2/3 analysis not run): its untracked
`scripts/card_analysis.py` is committed in this session as work in progress, untested, following
decision 0030 item 1 (D's untracked tools of an open package), so that the worktree is clean for
`nrpic-stage verify`; the package's README and JOURNAL are not changed.

# Batch 21 (2026-11-25, lead; processors only, cards held by another partition)

No helper package has finished since batch 12: nothing of a helper to recheck. This section
records the lead's own reading of the card chain A2 and the horizon recheck of decision 0040 item
3, each against predictions written before the run (JOURNAL.md, batch 21, S1-S6 and H1-H4). A
second agent has not checked them: they go to the fresh G1 verifier (stage/G1/OPEN.md item 2).

| run | what | verdict against the prediction |
|---|---|---|
| F-20261125-170453-1175d44 (b21_a2_state.py; fig_b21_a2_state read) | A2 PARTIAL to 96.23 M: tracker copies, overlaps, appended outputs, separation, distances | S1, S2, S3 MET (join complete, overlaps <= 1.1e-12 M, outputs appended, 137/137 waveform samples); S4 = A2-1 REFUTED on timing (closest approach 2.110 M at 76.37 M, window 63-75 M); S5 MET (centre of mass 13.06 M from M, closing; A2-2 open); S6 MET to 96.23 M |
| F-20261125-170540-aa39bea, F-20261125-170632-5aa9786 (b21_horizon_recheck.py; fig_b21_horizon_recheck read) | every horizon statement of G1 rechecked by the failure signature; no run has the status file | H1 MET (no failed search at m/12, m/16); H2 REFUTED IN PART at the bands' second digit (R8 0.92e-3, C 1.71e-4), slopes identical with and without failed rows; H3 MET (P1 common horizon 48.81 M and 49.06 M accepted, trackers 48.79 M); H4 REFUTED as written for P1 (first three searches at t <= 0.125 M only; after 1 M within 0.70 percent) |
| F-20261125-170646-6dd4ae4 (b11_passage.py; fig_b11_passage read) | A + A2 and C against Newton | not a test; NR runs late against Newton (both members bound to M and to each other at 96 M; Newton's pair unbound by about 95 M) |

What the track does about the failed predictions: A2-1's timing failure is recorded and no cause
is named (B's own turn at 73.9 M and the tide of the passage are the comparison, not a test). H2
and H4 change wording, not conclusions: RISKS R4 now reads 0.9-1.7e-3 per M at m/8; P1's heavy
hole "within 0.7 percent after 1 M"; every horizon number carries "made without the diagnostics"
(R22; OPEN.md items 5 and 7). The decision on the passage (continue the chain as it is) and its
prediction are in JOURNAL.md, batch 21.

Runs closed: B (F-20261121-203156-03efdd3) finished as stopped (9.28 card-hours, 153 files
checksummed, 109.9 GB).

## Batch 25 (lead, 2026-11-25 late evening): A2 at its cap; the G1 verifier's requests

Artefacts read, not conclusions: A2's run directory (chain/events.log, the 21 segment logs, the
kept tracker copies, the horizon summaries, history and waveforms) through the registered
readers F-20261126-054946-a21f229 (b21_a2_state.py) and F-20261126-054957-6cdb7cf
(b11_passage.py); both figures read. VERIFIER.md (batch 22) read in full.

**A2 (q0001, F-20261124-210400-902c650), ended at MAX_SEGMENTS = 19 at 133.0 M, 11.15
card-hours (sacct, 21 jobs 5207-5349).** Confirmed: the join A + A2 is complete to 133.0 M (one
step largest gap; overlaps to 1.25e-9 M); waveforms complete. The batch-21 cap forecast holds
(125-140 M, 10-14 card-hours). Wrong in the track's predictions: A2-2 (the centre of mass did not
turn at 8-11 M by 115 M; at 133 M it is at 5.42 M and still closing, because the pair is
disrupted and m1 falls almost radially into M), A2-5's heavy-hole clause (1.55e-3 > 1e-3 by 133
M). Defect fixed: b21_a2_state.py drew its panels to a fixed 120 M; it now draws to the last
record (commit before F-20261126-054946-a21f229). Not confirmable now: the fates (m1 bound and
plunging, m2 marginal) are coordinate energies (R6) until the horizons show a merger of m1 with M.

**The verifier's requests (VERIFIER.md section 8) and what the track does:**
- (a) Fractional drifts. Applied: binary_conv/README.md row "member horizon drift, fraction of
  the mass per M"; CHECKLIST, STATUS, JOURNAL batch 25 say "fractions of the mass per M" for
  S6/H2 numbers (3.09e-5, -8.05e-6 over 65-95 M; m/8 0.9-1.7e-3; C 1.2-1.7e-4). RISKS R4 already
  said "fractional".
- (b) No order of convergence between the mesh members. Applied: binary_conv/README.md withdraws
  ">= 3.3" and states "m/12 and m/16 agree within 2.1e-3 M to 21 M; m/8 differs by 0.06-0.38
  M" (verifier F-20261125-175931-32701e4). The note's ledger row 194 (three-member "orders" 12,
  14.5) is to be reworded in note v3 the same way (OPEN.md item 3).
- (c) Newtonian pass of the centre of mass. Applied in wording: the three-body integration passes
  the centre of mass at 9.762 M at 104.34 M; 9.81 M is the two-body conic pericentre of the
  initial centre-of-mass state (9.8087 M), as SCOPING and G1/STATUS already call it ("conic").
  JOURNAL batch 11's A2-2 text ("Newton 9.81 M at 104.35 M") stays as written (append-only); its
  judgement does not depend on the 0.047 M.
- (d) p1_280.json's d_at_112. Checked in the source: khsr_note/scripts/p1_280.py line 63 stores
  np.interp(112.38, t, d) under the key d_at_112, so the stored 11.816 M is the remnant's distance
  at 112.38 M (khsr_note/JOURNAL.md line 94 says "at t = 112.38 ... 11.82 M"), not at 112.0 M
  (11.895 M, verifier). A label defect, not a wrong number; the key keeps its name in the
  registered output; any text that quotes it says "at 112.38 M".
- (e) F1, the heavy hole's two finder branches from 86.6 M: OPEN. Plan: A2's continuation carries
  `<fastflow> diagnostics = true` through `-i` (decision 0043 item 5) if the processor test R25
  holds; then each search of finder 2 has a status row (found, reason, iterations, expansion), and
  the branches are told apart by their mean expansion and flow iterations from 133 M on. The rows
  86.6-133 M stay "made without the diagnostics"; for them only the failure signature applies.
  A2-5's heavy-hole clause is already refuted as written (1.55e-3 by 133 M) whatever F1 decides.
- (f) Method behind "own residual 4.9e-7" and the baseline of "+0.32 percent": the baseline is the
  accepted search at 4 M (verifier reproduced 1.004190 there); the 4.9e-7 is not reproduced from
  the history (the ledger's raw m/16 value is 5.51e-7); the text is to say "5.5e-7 raw, about 30
  times below the uncorrected 1.6e-5" in note v3 (OPEN.md item 3).
- Junk-energy criterion (iii): the four radii agree within 19.8 percent: MET AT ITS EDGE
  (CHECKLIST C7).

## Batch 34 (lead, 2026-11-27 afternoon): A2 to 186.0 M; horizons from the status files; G1 package

No helper package finished since batch 25; this section reviews the card runs themselves from their
outputs (JOURNAL.md batch 34: predictions D34 written before any reader ran; outcomes there).
- A2 (F-20261124-210400-902c650): continuation q0069 from 133.0 M to 186.0 M, 25 attempts (17
  cut by preemption), 8 counted segments of the 9 allowed; ended because Slurm refused the next
  submission ("I/O error writing script/environment to file", chain/slurm-5492.out), the same
  failure at the same minute for C2. Closed `--status stopped` (checksums over about 724 GB in the
  background). The readers b21_a2_state.py and b11_passage.py ran unchanged to 186.0 M
  (F-20261127-232849-14345be, -232940-3f652bf); a new reader b34_horizons.py reads the finders'
  status files (F-20261127-232657-163727d; its first run F-20261127-232531-8d16e2c failed: the status
  rows end with `# <reason in words>` and nrread.read_table skipped every row). All four figures
  looked at.
- Confirmed from the outputs: the join has no gap to 186.0 M; the common horizon of m1 and M at
  137.5 M (finder 2 found at every search, mass 1.0053 -> 1.1137, its centre on M's tracker within
  3e-6 M); m2's horizon found at every search with its mass within 6.4e-4 of 0.12954; Newton's
  reverse fates. What is a coordinate reading (distances, energies with gauge velocities) and what
  the horizons show is separated in JOURNAL.md batch 34 and stage/G1/STATUS.md T4.
- Not confirmed: m2's fate (two-body energy within +-0.2 units of zero, depends on which mass of M
  is used and on the gauge velocities); the remnant's spin and the radiated energy (not computed);
  which heavy-hole branch of 86.6-133 M is converged (F1: the status file does not separate the
  branches, both "found" with equal mean expansion; the finder stops after a median of 6 flow
  iterations).
- Wrong and corrected: b11_cards.RUNS mapped B2 and C2 to the batch-11 runs that were stopped
  before they ran (F-20261124-135408-1e6db58, -141842-d5263e9); now the queued runs
  (F-20261126-052133-10f9a5f, -131751-89eaff8), so b11_passage draws C + C2 to 106.69 M (not judged).
- Wrong, listed: finder 0 reports "found" for 117 surfaces after 141 M with |mean expansion| up to
  23.7 (status file reason 0): a found flag that accepts such surfaces is a question to core
  (outbox, batch 34). b11_passage's member energies of m1 after the merger are meaningless (its
  distance to M is 1e-9 M) and it keeps M's pre-merger mass.
- The verifier's findings: F1 decided in part (above; stage/G1/OPEN.md item 5); F2-F4 and requests
  (a)-(f) as in batch 25. The verifier's rerun on the completed passage is the next session's.
- F-B2 (F-20261126-052133-10f9a5f) DONE at tlim 140, F-C2 (F-20261126-131751-89eaff8) stopped at
  106.69 M: health check only (trackers and history to their last time, no non-finite value);
  closed. Both are G2 material.
