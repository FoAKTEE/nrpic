# What G2 of B-emd-gw still lacks (batch 37, 2026-11-27 19:30 PST)

The fresh G2 verifier has reported (VERIFIER.md here; its package stage/G2/verifier/). Batch 37
answered its corrections a-e (REVIEW-wave3.md, section "Batch 37"; note v5 from run_all
B-20261128-030805-78634c0) and decided the member 256^3 at eight particles per cell (decision 0048
item 3): it fits one card.

| Item | State (CHECKLIST.md) | What remains |
|---|---|---|
| C1 | PASS under 0046 2(a); L2 as run FAILED on record | the series-7 constraint floor (cause not named); L2's crossing before t_A is an inference, not a measurement |
| C2 | PASS for the band strain in mesh (GM2) and particle number (Q1); gauge leg recorded as an IDENTIFIED DEPENDENCE ON THE GAUGE, not a convergence; halo catalogue at one particle per cell FAILED on record | the member 256^3 at eight per cell (below), which the gate review may weigh or not |
| C3 | PASS under 0046 2(b) and 0039 2(c); M4, GM4, C3a early part FAILED on record | caveat: the 64/128 pair sits at coarser spacing than 128/256; extremes of the one-per-cell ratio depend on the pairing by a few hundredths (row g2_pair) |
| C5, C11, C17 | PASS | none |
| C18 | PASS, coverage limited as the verifier states (not every ledger number) | none |

Pending, not required by any criterion as worded: the member 256^3 at eight particles per cell
(Gamma driver, q0060's deck; fits one card: 42-46 GiB of 80, bound 76 GiB; about 12 card-h, 8-16;
B-20261128-030350-19295a4). Its initial data run detached on one core since 2026-11-27 19:04 PST
(B-20261128-030420-33ccdca, expected 30-55 h; predictions I1-I4, K1-K3 in population/JOURNAL
2026-11-27 19:02 and 19:05). The queue entry (priority 2, release build) is added by the session that
checks the data. A same-gauge mesh partner at eight per cell (128^3, Gamma driver, about 0.85 card-h,
data exist) is asked of the orchestrator (outbox).

Failures on record (no further run needed): X3 (setup error), the time part of GD1 and of N1p, the
particle leg's chain cut at a = 94.8; N4 as written (cause found), GN2 after a = 36, NB1, VC1 second
part, VC2 side statements, the defective first band run; M1 (B-20261125-093500-242d3a3 closed
failed), M4, GN1 of batch 21 withdrawn, the slip a' = 4a in S2/S3; GM4 first part, M2 largest masses
at a = 64-72, M3 first part at a = 100, Q1 high-k part; batch 29: the series-7 design claim "no
crossing before tlim" and N7b constraint part, the C3 step-1 wall-time expectation; batch 34: GM2
Omega part, GM3 counts at a = 121 and largest masses at a = 64, 121, C3a before a = 31, the step-1
wall time; batch 37: the halo catalogue at one particle per cell (C2, failed in the mesh), the
card-time expectation E2 of the 256^3 member (4-7 card-h expected, 12.2 estimated), P1 in part
(Table VII's 1.11-1.36 is not the epoch pairing of judge_c3.py, which gives 1.13-1.37), P2 for the
nearest-record pairing (1.50), the first mem_fit run's card time (B-20261128-030214-20f2961,
superseded).

G2 package complete for an independent review in the lead's judgement: what remains open is the
failures above with rulings 0046 item 2, 0039 item 2(c), 0048 item 3 and 0049 item 1, and the
pending 256^3 member at eight per cell. The full checksum pass of the stage check (13883 files,
1166.91 GB, PASS) is committed; the quick pass after batch 37's changes follows it.
