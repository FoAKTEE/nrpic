# Independent verification of Track E's G1 material (slow-roll ladder 32^3-256^3)

Verifier: helper g1verify of E-stoch-inf (decision 0016 item 4; item C16 of the G1
checklist), a fresh reader given the artefacts and not the conclusions. Two sessions:
2026-11-20 14:21-14:35 PST (cut by the five-hour limit) and 2026-11-20 18:55 PST onwards
(2026-11-21 UTC). Worktree commit at start: bc5e277 (session 1), 36824dc (session 2, after
`git merge main`).

Read before the verdicts: `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and section 9.8 (the
G1 criterion); decisions 0010, 0013 (Track E), 0016-0020; `spec/scope/SCOPE.md` section 4
item 4 (definitions and thresholds A1-A8; the amendment note under A2 quotes two ladder
numbers, 6.2e-3 and 1.2e-4 at 256^3, which I could not avoid seeing) and section 4b (A4',
A5' as proposals); `spec/SPEC.md` sections 1-7; core's interface
`core/scalar-2:tracks/core/interfaces/scalar_field_2.md` and the READY of
`scratch/core/exe/core_scalar-2/` (they quote core's own 32^3-128^3 test numbers, which are
core's verification, not the track's G1 results); `coord/INTERFACES/rng.md` sections 2-3,
`athenak/src/utils/rng.hpp`, the header of `core/scalar-2:.../scalar_field_noise.cpp`, the
NRSFDMP1 comment of `athenak/src/scalar_field/scalar_field_io.cpp`; every run manifest used;
the ladder inputs (`ladder/inputs/*.athinput`, `*.list`, `modes_n*.txt`) and the noise
unit-test inputs (`analysis/inputs/u64/`); the sources P1 = arXiv:2512.14649 v2
`PRD_v2.tex` 400-545 and 690-790, BZ = arXiv:2606.14853 v2 `Manuscript.tex` 140-290, TH =
arXiv:2610.32592 v1 `appendix.tex` 380-525, P2 = arXiv:2502.06783 v3 `main_V2PRD.tex`
395-460 (kb-data/raw/arxiv, read only).

Not read before the verdicts: the owner's STATUS, HANDOFF, JOURNAL, RISKS, PLAN-wave3;
`stage/REVIEW-wave2.md`; everything under `stage/G1/`; `ladder/README.md`, `JOURNAL.md`,
`results/`, `fig/`; `note/`; the packages a4res, usr, window; `spec/ref/` (the track's MS
reference); the wave reports of `scratch/orch`. The comparison with the track is the last
section, written after the verdicts.

Labels: [VERIFIED] recomputed here with the run id given; [JUDGEMENT] my inference;
[TO VERIFY] open. Predictions and outcomes, failed ones included: `JOURNAL.md`.
All my code is in `scripts/` (own reader, own Philox and Box-Muller, own background and
Mukhanov-Sasaki, own R^NR extraction, own odd/even split); nothing of `spec/ref/` or
`python/nrpic/sf_inflation.py` is used. Core's `read_dump` was used once, as the check of my
reader (C0).

## Runs

| Run id | What | Status |
|---|---|---|
| E-20261120-222844-dbca87f | C0: my reader vs core's read_dump (bit for bit), my Philox vs numpy.random.Philox, my alpha vs core's twin, my background fixing vs the deck, my Bunch-Davies modes vs the mode files, lists and checksums, my R^NR at t = 0 | completed |
| E-20261120-223154-d42de1a | pass 1: R^NR per mode and box means from all dumps of P256 (18) and L256p (10), sha256 of each dump checked | completed (closed with `finish` in session 2) |
| E-20261121-025750-d1b6139 | pass 2: the same for L32p, L64p, L128p, Q64p, Q128p (card) and L64p_proc (processors) | completed |
| E-20261121-030207-fb6f090 | V1, V2, V3 analysis (records of all 34 runs, my MS full and deformed) | completed |
| E-20261121-030657-c1afe38 | V4/V5 data: odd/even parts of H and M_i, bands, shell spectra, halving, controls, records | see V4 |
| (V4/V5 analysis run, below) | | |
| E-20261121-030412-42dd156 | V6, first version (the even part of H still held its box mean) | completed, superseded |
| E-20261121-030522-c6907b6 | V6: Richardson orders from the Courant runs | completed |
| E-20261121-030415-22d518b | V7, first attempt | failed (exit 1: my script read a processor manifest without batch entries) |
| E-20261121-030520-5a23d64 | V7: bit-identity of the noise unit test (layouts, restart), card vs processor, cost | completed |
| E-20261121-031049-27cdc06 | V7c: the G1 executable (core/scalar-2 processors) on the L32p set-up with 8 MeshBlocks, and restarted from cycle 12 (1 core, 98 s) | completed |
| E-20261121-031251-c48670d | V7c comparison with the registered L32p | completed |

All on processors (0 card-hours). Every run used is registered and finished; the sha256 of
every dump I read was compared with the producing run's `sha256sums.txt` (P256 and L256p in
pass 1, the others in pass 2, V6, V7, the constraint pass).

Set-ups confirmed from the lists [VERIFIED by reading `ladder/inputs/*.list`; C0 checked
that the lists are unchanged since submission]: L = `noise_nmax2 = 64` (k_max/dk = 8) with
`modes_n64.txt`; Q64 = nmax2 256, Q128 = 1024, P256 = 4096 (k_max = N/4, P1's set-up);
suffix p/m = `noise_mode_scale` +1/-1, ph/mh = +-1/2; NC = `noise_pi_sign = -1`; the m, h
and NC runs have `dump_metric = false` (no gt_ij, At_ij), so R^NR is measured on the p runs
only. Ends: P256, L32p/m, L64p/m, L128p/m, Q64p, Q128p at t = 8.5 (N - N* = 8.10); P256m,
L256p/m, Q-m/h, NC, L32ph/mh, L64p/m_proc at t = 4.5 (4.39). Card runs are core/scalar-2
a58e95b `athena_gpu`, processor runs its `athena_cpu`.

## Verdicts

### V1 (A1) Background: box means against my Friedmann and Klein-Gordon integration — CONFIRMED

[VERIFIED, run E-20261121-030207-fb6f090] My integration in code time (`scripts/ref.py`,
DOP853 at rtol 1e-13) from the deck's phi0, pi0, mass, which my own potential-position
fixing of P1/P2 reproduces to 1.2e-15 (C0). Over every row of the history record
(`sr.sf.hst`, every cycle) of all 34 catalogue runs (ladder, halved, controls, Courant):
max |<phi>/F - 1| = 3.2e-12, |<Pi>/F - 1| = 8.6e-12, |<K>/F - 1| = 3.6e-12; my own means of
the p-run dumps agree (at most 7.8e-12). Threshold 1e-4: passed by eight orders of magnitude
on every rung, controls included. The code's lockstep background (record columns phi_b,
Pi_b, ln_a) equals mine to 2.3e-11. Two observations, neither in A1: (i) the e-folds
-ln<chi>/2 differ from my ln a by 5.5e-6 (N = 32), 3.3e-7 (64), 2.0e-8 (128), 1.3e-9 (256):
the RK4 error of chi ~ exp(-2t), which converges at order 4.06 in the Courant factor (V6);
my prediction of 1e-8 failed at N <= 64. (ii) The lapse stays uniform but drifts from 1 by
-2.5e-13 (L32p) and -4.9e-13 (L64p) at t = 8.5, linear in the number of steps (rounding).
Figure `fig/fig_v1.png`.

### V2 (A2) R^NR per mode against W R alpha; the shell spectrum — CONFIRMED

[VERIFIED, runs E-20261120-223154-d42de1a, E-20261121-025750-d1b6139, E-20261121-030207-fb6f090]
My extraction (`scripts/rnr.py`): Phi_k = (X_k/<X> )/2 + (1/4) k_i k_j/k^2 (gt_ij)_k and
R^NR = Phi - <K>/(3<alpha><Pi>)(phi - <phi>) (TH appendix.tex:517-520, P1 PRD_v2.tex:522-526),
mode coefficients by my own FFT with the cell-centre phase exp(-i pi (n_x+n_y+n_z)/N);
reference L^-3/2 W(k,t) R_k(t) alpha_n with my full MS integrated from each run's mode file,
W of P1:503-506 with the Friedmann a, H, and my alpha_n (Philox-4x64-10 of rng.md, checked
against numpy's independent Philox on 7160 keys and against core's twin to 5e-16). At t = 0
my R^NR equals the reference to 1e-10 for |n| = 1 (C0), so convention and alpha are right.

| Rung | max over k <= k_max/2, last dump (N - N* = 8.10; L256p 4.39) | at t ~ 4.5 | all k <= k_max, last dump |
|---|---|---|---|
| L32p | 8.8e-5 at n = (4,0,0), k dx = pi/4 | 8.7e-5 | 4.1e-3 at (8,0,0) |
| L64p | 2.7e-6 | 2.0e-6 | 9.7e-5 |
| L128p | 2.5e-6 | 1.75e-6 | 7.1e-6 |
| L256p | 1.7e-6 (t = 4.5) | 1.74e-6 | 3.1e-6 |
| Q64p | 9.7e-5 | 9.5e-5 | 4.0e-3 |
| Q128p | 9.9e-5 | 9.2e-5 | 4.1e-3 |
| P256 (68532 modes with k <= 32) | 1.21e-4 at (0,32,0), k dx = pi/4 | 1.03e-4 | 4.5e-3 at (0,0,64) |

Threshold 0.02: passed by a factor 165 or more at k <= k_max/2, and still by 4.4 at k_max
itself. The error grows with k as the sixth-order dispersion (`fig/fig_v2.png`, top right);
in the L set-up it falls by 44 from 32 to 64 (order 5.4) and then sits at a floor of
~2e-6 on the lowest modes from 64 to 256 (the second-order part of R^NR [JUDGEMENT]: it
cannot be separated, the m runs carry no gt_ij).
Shell spectrum of P256 at the last dump (my alpha removed): Delta_R / (H^2/(8 pi^2 eps1 Mpl^2)
at crossing) = 1.0104-1.0116 over every shell k <= 32 (my full MS: 1.0104-1.0114; NR and MS
differ by 1.6e-4 at most); Q64p, Q128p, L-rungs: 1.0104-1.0134. The raw shell spectrum
(alpha not removed) scatters around the MS with pull rms 1.007 (max 4.1 over 854 shells),
i.e. cosmic variance only. The departure from the analytic slow-roll power, +1.0 to +1.3
percent, is the known slow-roll correction (my MS gives it too), not an error of the code.

### V3 (A3) Freezing of super-horizon modes (criterion of arXiv:2606.14853) — CONFIRMED

[VERIFIED, run E-20261121-030207-fb6f090] For each of the 1051 modes with N_f - N_k >= 6
(k <= 7.87 dk; crossing k = a H from my background) on every t = 8.5 rung (L32p, L64p,
L128p, Q64p, Q128p, P256): the per-mode power ratio |R_n(N_f)|^2/|R_n(N_k+4)|^2 (first dump
at or past N_k + 4; no alpha needed) equals my full-MS ratio within 2.4e-6 (L64p, L128p) to
3.2e-6 (P256, Q128p); threshold 1 percent. The drift of ln|R_n|^2 from N_k + 4 to N_f is
-1.4e-4 to -3.3e-5 per e-fold (threshold 2.5e-3) and equals the full MS within 1.7e-6. My
deformed (FLRW-lattice) equation of BZ (Manuscript.tex:192-194, 220-222, rewritten for R in
e-folds, `scripts/ref.py`) drifts by -0.0516 to -0.0530 per e-fold (-4 eps1) and ends 9 to
17 percent below the full MS: the NR data sit 3e4 times closer to the full MS than the
tolerance is wide, and 1e4-1e5 times closer than to the FLRW-lattice behaviour.
Figure `fig/fig_v3.png`.
