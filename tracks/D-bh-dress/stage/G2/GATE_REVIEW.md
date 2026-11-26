# GATE_REVIEW.md: independent gate review of G2 of D-bh-dress

Gate reviewer of batch 27 (decision 0019 item 3), fresh context, 2026-11-26 from 03:44 PST.
I produced none of the work under review. No tag `stage/D-bh-dress/G2-pass-*` existed when I
started (`git tag -l`: `G0-pass-20261120`, `G1-pass-20261121` only).

(Sections 1-6 are written after the check run below; this commit holds only the predictions.)

## 0. Predictions for the reviewer's own check run (written and committed before it runs)

Script `scratch/D-bh-dress/tmp/gate_review_G2/review_checks.py` (imports nothing of the track
or of the verifier, only numpy and a copy of `harness/style/figstyle.py`), one core, registered
with `nrpic-run`. It reads the raw finder summaries (`*.horizon_summary_0.txt`, column 3; a time
that repeats after a restart keeps its last line) and the removal records (`*.removed.bin`,
docs/FORMATS.md line 127) of the registered card runs, and nothing else.

| # | Quantity (definition) | Claim in the package | Predicted (refuted if outside) |
|---|---|---|---|
| R1 | N at M/8: max over 100 <= t <= 500 M of /D_ES1L - D_V1L/, D_X(t) = M_X(t) - M_X(100) (g2long entry 1) | 2.28e-4 | [2.26e-4, 2.30e-4] |
| R2 | F_V(500) = max /D_V1L/ on 100-500 M; bound 2 F_V | 1.253e-4 (bound 2.51e-4) | F_V in [1.24e-4, 1.27e-4]; R1 < 2 F_V |
| R3 | N at M/16 on 100-300 M (ES-1L16 against V-1L16) | 1.99e-4 | [1.97e-4, 2.01e-4]; below 2 F_V16(300) |
| R4 | N at M/4 on 100-300 M (ES-1L4 against V-1L4) | 4.57e-3, fails | [4.5e-3, 4.65e-3]; above 2 F_V4 |
| R5 | Mesh of the growth: /dM_FL16 - dM_ESFL/ with dM(t) = M(t) - M(20 M), at 100, 200, 299 M | 4.4e-4, 1.2e-4, 8.6e-5 | each within 5 per cent of the claim; all below 3e-3 |
| R6 | Particle number: /M_4N - M_N/ <= /M_N - M_N/4/ at 100, 200, 300, 399.5 M (FN4, FK, FNQ) | 4 of 4 | 4 of 4 |
| R7 | ES-FL removals: time of the last reason-3 and of the first reason-2 record | 218.9 M, 224.0 M | last reason 3 in [218, 220] M; first reason 2 in [219, 226] M; no reason 1 or 4 dust removal |
| R8 | FK removals: reasons present to 400 M | reason 3 only | reason 3 only |
| R9 | ES-FL horizon mass at 499.5 M | 1.6090 | [1.6085, 1.6095] |

A miss is recorded below as a failed prediction, with what it means for the claim.
