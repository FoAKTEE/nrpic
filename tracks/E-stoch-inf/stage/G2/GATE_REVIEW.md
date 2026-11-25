# GATE_REVIEW.md: independent gate review of G2 of E-stoch-inf

Reviewer of batch 16 (decision 0019 item 3; decisions 0036 item 2, 0037 item 2), fresh context,
2026-11-25 from 04:28 UTC. I produced none of the work under review. No tag
`stage/E-stoch-inf/G2-pass-*` existed when I started (`git tag -l 'stage/E-stoch-inf/*'`: G0 and
G1 pass tags only). Worktree after `git merge --no-edit main`: 51a5c279.

This first version holds only the predictions of my own check, committed before it runs. The
review follows in the next version of this file.

## 1. My own check: predictions (before the run)

Script `scratch/E-stoch-inf/gate_review_G2/review_g2.py` (my own NRSFDMP2 reader written from
`coord/INTERFACES/scalar_field_2.md` 4 and the record columns of `scalar_field_3.md` 6; no
script of the track or of its verifier imported or read; self-test on a synthetic dump: bit-exact
read-back, planted floor recovered). Registered with `nrpic-run submit`, processors, 2 cores.
Inputs: the raw dumps and records of the seed-A runs at 256^3 with s = +-1 (U256ap/am
E-20261121-211214-0377aab, E-20261121-214629-da64fb7), +-1/2 (U256hp/hm E-20261122-113320-9bbb52b,
E-20261122-152116-0542096), +-1/4 (U256qp/qm E-20261123-230004-861aea7, E-20261123-230507-a6246b1),
the control U256nc E-20261122-190341-0419be6, and the records of seed B and of the 320^3 pair.
Definitions as SCOPE 4c is written: odd and even parts of one seed, box means removed, M_i taken
together (rms of the vector), floor f^2 = max(0, (4 o_{s/2}^2 - o_s^2)/3), factor
sqrt(e_s^2 - f^2)/sqrt(e_{s/2}^2 - f^2) judged where e_{s/2} > 3 f.

The numbers I predict are those the package and its verifier print (g2prod/JOURNAL.md 2.3 and
4.1, stage/G2/VERIFIER.md 2 and 3). A reproduction by a third reader is the test.

| # | Quantity | Prediction | Refuted if |
|---|---|---|---|
| P1 | U-A4'(a), M, s = 1 over 1/2 | judged at dumps 0 and 4-13; dump 13 (cN 6.525) factor 3.9245 +- 0.002, the only one outside 4 +- 0.05 | dump 13 within 3.95-4.05, any other judged dump outside, or a different judged set |
| P1h | U-A4'(a), H | judged at dumps 0 and 5-12, factors 3.991-4.043; dump 13 not judged (e_{1/2} about 1.3e-14 < 3 f) | any judged H dump outside 3.95-4.05 |
| P2 | raw parts of M at dump 13 | o = 1.0881e-11, 5.4407e-12, 2.7211e-12; e = 1.0418e-12, 2.6991e-13, 9.751e-14 (s = 1, 1/2, 1/4); f = 5.05e-14 | any o or e off by more than 1e-3 relative, f by more than 2 percent (a common factor sqrt 3 from another vector convention would not refute) |
| P3 | three amplitudes, D1 = E(1) - 4 E(1/2), D2 = E(1/2) - 4 E(1/4) | rms(D2)/rms(D1) in 0.99-1.01 and corr(D1, D2) in -0.25 to -0.22 at every dump 1-13, H and M; sigma = rms(D1)/sqrt 17 = 7.30e-14 at dump 13 (M); factor with sigma there 3.9988 +- 0.001; every dump with e_{1/2} > 3 sigma within 4 +- 0.005 | ratio off 1 by more than 0.05 at any dump 1-13, corr outside -0.30 to -0.17, or a sigma-judged factor outside 4 +- 0.01 |
| P4 | quarter pair, M at dump 13 from (1/2, 1/4) with its own floor | 4.1275 +- 0.003, not judged by 4c's rule (e_{1/4} < 3 f) | outside 4.12-4.135 |
| P5 | U-A4'(d), control against the proper odd part of H, maxima over cN <= ln 32 | single reading 2.38e5, cross reading 1.19e5 (each +- 2 percent) | either below 1e3 |
| P6 | U-A4'(c), record maxima (columns 25 and 7) | proper runs: <abs H'/[H]> 1.1e-12 to 3.1e-12, <abs M/[M]> 8.0e-3 (320^3) to 2.53e-2; the M maximum at 256^3 equal within 1 percent at s = 1, 1/2, 1/4; control 1.28e-7 and 0.50 | any proper run above 1e-9 or 1e-1 |
| P7 | pairing | 21 dumps per run, recorded times equal across the six runs (abs dt <= 1e-9), the last at tlim within 1e-9, the same MeshBlock header | any of these |
| P8 | integrity | dump 13 of the six runs, the last control dump of the entry and the two record files of all eleven runs equal their entries in each run's sha256sums.txt | any mismatch or missing entry |
