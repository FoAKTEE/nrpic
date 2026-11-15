# Lead's re-check of the helpers (G0 of A-emd-pbh)

The lead's review of the wave-2 helper packages (runs_ball, periodic_threshold, newton,
criteria2, note, verifier) is `../REVIEW-wave2.md` (one file for both gates): predictions
written before the checks (section 0), the lead's runs (section 1: six reruns of the
helpers' analyses from their registered outputs, all reproducing exactly, and an independent
reader, run A-20261115-182314-bebd0cf), the outcome of each prediction (section 2), per
package what is confirmed, not confirmed and wrong (section 3), and what the track does with
each finding of the verifier. The wave-1 re-check is `../../JOURNAL.md` entry
2026-11-15T12:57Z (L1-L8).

Wrong statements found and corrected: the ball window (verifier C1c; SCOPE.md 4, 8, 10.9),
the H1 timing (verifier C4b; SCOPE.md 2), the label of the finite-duration cutoff (SCOPE.md 3),
the table-interpolation deviation (1.37 H; SCOPE.md 10.3, RISKS row 11), two background-time
conversions of the periodic package (1.2 and 35.8 t_H; DESIGN.md).
