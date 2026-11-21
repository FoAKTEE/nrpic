# GATE_REVIEW.md: independent gate review of G1 of E-stoch-inf

Reviewer of batch 4a (decision 0019 item 3), fresh context, 2026-11-21 from 15:45 UTC. I
produced none of the work under review. No tag `stage/E-stoch-inf/G1-pass-*` existed when I
started (`git tag -l`: only `stage/E-stoch-inf/G0-pass-20261120`).

This first version holds only my predictions; it is committed before my own check runs.

## Predictions for my own check (written before the run)

Script `scratch/E-stoch-inf/gate_review_G1/review_checks.py` (my code; it imports nothing of
the track but the figure style), registered with `nrpic-run`, processors only. It reads only
the scalar-field records `sr.sf.hst` and `sr.sf.con.hst` of the ladder runs (P256, P256s2,
L32p, L64p, L128p, L256p, Q64p, Q128p, NC32p, NC64p, NC128p) and integrates its own
Friedmann and Klein-Gordon background (quadratic potential, mass, phi0, pi0 and G = 1 from the
deck, lapse one, DOP853 at rtol 1e-13).

| # | Quantity | Claim in the package | Prediction | Refuted if |
|---|---|---|---|---|
| F | sha256 of every record file read against the producing run's `sha256sums.txt` | (verifier: all dumps match) | all match | any mismatch |
| B | A1: max over all rows of abs(<phi>/F - 1), abs(<Pi>/F - 1), abs(<K>/(-3 H_F) - 1) | phi 2.0e-12 (P256), Pi 8.6e-12, K 3.6e-12 (L32p); all rungs below 1e-4 | the three maxima within 30 percent of the claims at the named rungs; every rung below 1e-10 | any rung above 1e-10, or a named-rung maximum off by more than 30 percent |
| C | e-fold error at the last row: abs(-ln<chi>/2 - ln a_F) | 5.5e-6 (L32p); 3.3e-7, 2.0e-8, 1.3e-9 at N = 64, 128, 256 | L32p within 10 percent of 5.5e-6; falls by about 16 per doubling | L32p off by more than 10 percent, or no fall with N |
| D | A4'(c): record maxima <abs H/[H]>, <abs M/[M]> over the whole record, paper's set-up | Q64p 4.8e-11, Q128p 5.0e-11, P256 5.1e-11; M 3.8e-4 to 4.0e-4 | each within 5 percent of the claim; all below 1e-9 and 1e-3 | a claim off by more than 5 percent, or a limit exceeded |
| E | negative controls NC32p, NC64p, NC128p: record maxima | <abs H/[H]> 9.8e-8 to 9.9e-8; <abs M/[M]> 0.21-0.22 | within 5 percent of these | off by more than 5 percent |
| G | second seed P256s2: A1 and the record maxima | (seed 2 judged on A1-A3 by the ladder) | A1 below 1e-10; record maxima within 10 percent of P256's | otherwise |
