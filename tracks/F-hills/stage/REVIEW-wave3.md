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
