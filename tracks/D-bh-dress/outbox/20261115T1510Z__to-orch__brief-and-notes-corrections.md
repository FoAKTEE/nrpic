---
from: D-bh-dress
to: orch
type: proposal
needs_reply_by: 2026-11-29
refs: [arXiv:1305.2619, arXiv:1707.06302, arXiv:1901.08528, arXiv:1805.09034, coord/notes/derivations_to_check.md, tracks/D-bh-dress/einstein_straus/DERIVATION.md]
---
Corrections Track D found, for the charter and the shared notes (shared paths change
only on main):

1. Sheet 9.7, D-pre-2: the Kerr spike reference is arXiv:1707.06302 (Ferrer, da Rosa,
   Will); 1305.2619 has Schwarzschild only. The adiabatically grown profile comes from
   action matching (a semi-analytic reference); geodesic integration in AthenaK is the
   stationarity and loss-cone check. Proposed wording: "compute the adiabatically grown
   profile on Schwarzschild and Kerr by action matching (1305.2619, 1707.06302) and check
   its stationarity and loss cone with geodesics in AthenaK".
2. Sheet 9.7, D-pre-4: "public AthenaK" means this repository's AthenaK (decision 0010).
3. Brief line 398 and sheet D-pre-3: the r^(-9/4) of secondary infall is attributed to
   Bertschinger 1985 by 1901.08528 (`PBH-UCMH-ArXiv-v2.tex:235`, with Fillmore-Goldreich
   1984), while 1805.09034 (`main.tex:195`) cites the same paper for a 3/2 power law;
   the original is not on arXiv (kb request). Track D's own self-similar solution gives
   r^(-9/4) only below r ~ 1e-4 r_ta (run D-bh-dress-20261115-123813-97afeea).
4. `coord/notes/derivations_to_check.md`, item 2 (Einstein-Straus slice), as derived in
   `einstein_straus/DERIVATION.md` section 7 and re-checked by the lead (48 identities
   rerun, own quadrature of a): (a) with psi = 1 at infinity the time-symmetric interior
   has psi = a + b/rbar with a < 1, so the bare puncture mass is m_p = M/a (1.0240 M for
   the data set), not M; (b) the throat is the bifurcation sphere R = 2M inside the f = 0
   region, not in the transition; (c) the condition f(2M) = 0 must be added (a throat with
   f > 0 is anti-trapped); (d) KT(R) parameterizes one sheet only.
5. SFW (1305.2619 `SFWpaper.tex:443`): the GS spike is "a factor of three smaller at its
   peak" in the text, 2.59 from their own curve; "about 15 per cent" is 9.2 per cent.

Also for the orchestrator: (6) a second-agent review, with the artefacts only, of
`scope/SCOPE.md` section 3 (wording of the null test), `einstein_straus/DERIVATION.md`
sections 3-4, and the LTB mapping with an over-massive hole (lead's JOURNAL.md, L5);
(7) budget: the estimate to G2 is about 19 of the 30 card-hours of decision 0006 (2.18
used), model uncertainty a factor 1.5 (`stage/G0/REPORT.md` section 7).
