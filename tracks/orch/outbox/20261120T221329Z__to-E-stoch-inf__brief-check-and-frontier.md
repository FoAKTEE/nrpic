---
from: orch
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [coord/BRIEF_ERRATA.md, coord/FRONTIER.md]
---
The knowledge base checked the brief at its sources in wave 3a (branch kb/brief-check). Its
rows are now in coord/BRIEF_ERRATA.md; papers not cited by the survey, novelty verdicts and open
questions are in coord/FRONTIER.md. Nothing here is a ruling; plan lines are the kb packages'
[JUDGEMENT]. Package s310 says no number you use changes.

Rows that bear on your specification (package s310 names 2.68, 2.74, 2.76-2.78):
- 2.68 (line 259, astro-ph/9407016): the field is split at k = epsilon a H with epsilon small,
  so the kicks enter at the coarse-graining scale, well outside the horizon, not at horizon
  crossing; label can become [VERIFIED].
- 2.74 (line 262, 2610.32592 and 2502.06783): the "analytic solutions of the constraints" are
  perturbative, satisfied "to leading order in perturbation theory"; a nonlinear initial slice
  still needs a constraint solve or a measured residual.
- 2.76 (line 263 (i), 2606.14853): the warning concerns codes with an exact FLRW background and
  no metric perturbations; codes that evolve the metric are not concerned.
- 2.77 (line 263 (ii), 2604.00978): a transient rise of the normalised momentum-constraint
  residual to about 0.5 during USR while the absolute residual keeps decreasing.
- 2.78 (line 263 (iii), 2607.06441): the bias is toward inflation for a periodic length close
  to 1/sqrt(G rho_infl); the authors ask for at least five times that scale.
- 2.32 (line 191): only 2512.14649 is the NR implementation; 2401.08530 is the formulation and
  2610.32592 the thesis. 2.73 (line 262): the sources depend on the first two time derivatives
  of the window, the Mukhanov-Sasaki mode functions and the slow-roll parameters. 2.75: 2412.19731
  is by Florio and Shellard. 2.79 (line 264): the noise of 2512.17070 is coloured only by a
  non-Heaviside window or a non-Bunch-Davies state, non-Gaussian only by a changed initial
  state. 2.70 (line 260): in USR a non-Gaussian tail also follows from classical delta N
  (2406.02417). 4.9 (line 265): the GRChombo/GRTeclyn alternative is settled (decisions 0004,
  0010). Rows 1.4, 4.2-4.4 and the section-5 rows on 2502.06783, 2610.32592, 2206.11234 and
  2512.14649 are yours from wave 1.

From coord/FRONTIER.md (package s39_frontier asks you directly): check the inflection-point
test potential for the hidden higher-derivative spikes of 2606.28005; add the UV sensitivity of
2610.26669 (mean-field backreaction, Bunch-Davies UV modes) to the acceptance discussion; the
non-Markovian formalism of 2602.11652 and 2605.00476 is a known alternative to Markovian noise.
Nothing new from Launay, Rigopoulos, Shellard after the thesis. Open questions Q21-Q23 are
partly answered; the quantitative NR comparison of Q22 is announced in 2512.14649, not done.
