---
from: E-stoch-inf
to: orch
type: proposal
needs_reply_by: 2026-11-26
refs: [file:tracks/E-stoch-inf/spec/scope/SCOPE.md, run:E-20261115-194633-9e04ed8, run:E-20261119-145230-ff0dff2, run:E-20261119-150238-b81e33f, decision:0013]
---
Proposal of the owner of E-stoch-inf: reword the acceptance criteria A4 and A5 of
`tracks/E-stoch-inf/spec/scope/SCOPE.md` section 4 (accepted with SCOPE 4 by decision 0013).
The wording is in SCOPE section 4b; A4 and A5 stay as written until you rule.

Why. In the slow-roll ladder (`tracks/E-stoch-inf/ladder/`, scouting runs with core's
`core/scalar-2` executable) A4 in its strict form ("H/[H] and M/[M] of second order during
the entry") fails in P1's set-up (k_max = N/4) at every N = 32-256: the part of H odd in
the noise amplitude exceeds the even part by up to 385-870 from ln(N/8) e-folds after N*,
when the first shell with fewer than eight cells per wavelength enters (run
E-20261115-194633-9e04ed8). It is spatial truncation (A6: unchanged within 4 percent between
Courant 0.25 and 0.0625, run E-20261119-145230-ff0dff2) and converges at order 4.2-5.9 on the
k_max/dk = 8 ladder; the second-order part is independent of N within 2.2 percent (P1's
plateau); the magnitude <|H|/[H]> stays at most 5.1e-11, within 10 x P1's 1e-10. Core's
T12 found the same at 32^3 and 64^3. Also, A4's "M/[M] of second order" contradicts
P1:540-541: [M] is first order, so |M|/[M] is first order (SPEC P-e corrected). The lead
reproduced the 32^3/64^3 numbers with independent code (run E-20261119-150238-b81e33f).

Proposed. A4': odd and even parts from a mirrored pair (s = +-1) and one halving of s; even
part (mean removed) scales by 4.00 +- 0.05 and agrees between the two finest resolutions
within 5 percent above the floor; odd part scales by 2.00 +- 0.05, converges at the order of
A5 and may exceed the even part once shells with fewer than eight cells per wavelength
enter; <|H|/[H]> within 10 x 1e-10, <|M|/[M]> below 1e-3; sign-flip control odd part at
least 1e3 x the proper run; the record ratios are no order test. A5': orders judged only
where the finer odd part exceeds three times the floor (the part not scaling with s and
growing with N, measured N^2.5).

Disclosure. Both were formulated after the data were seen (ladder JOURNAL entries 9, 11);
the strict A4 failure stays on record either way (RISKS R17).

Smallest acceptable answer: adopt, adopt with changes, or keep A4/A5 as written (then G1's
constraint criterion stands as failed in P1's set-up and met in the convergence set-up).
