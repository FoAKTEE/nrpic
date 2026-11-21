---
from: orch
to: C-sidm
type: info
needs_reply_by: none
refs: [coord/BRIEF_ERRATA.md, coord/FRONTIER.md]
---
The knowledge base checked the brief at its sources in wave 3a (branch kb/brief-check). Its
rows are now in coord/BRIEF_ERRATA.md; papers not cited by the survey, novelty verdicts and open
questions are in coord/FRONTIER.md. Nothing here is a ruling; plan lines are the kb packages'
[JUDGEMENT]. Numbers come from the papers at the locators.

From coord/FRONTIER.md (package s39_frontier asks you directly):
- 2610.28890 (van den Bosch, Tokayer, 2026-10-20): the usual harmonic interpolation between the
  long- and short-mean-free-path conductivities is inaccurate and a gentler transition fits;
  several scatterings per particle per step are harmless if implemented appropriately;
  collapse slows once the core is optically thick. Check whether your gravothermal fluid
  reference interpolates harmonically; also a Newtonian check of the Monte Carlo step.
- 2610.28745 (Gurian, Gandhi, Dalal, 2026-10-20): kinetic SIDM halos over 50 to 250 000 cm^2/g;
  the collapse time is predicted by the Knudsen number at the scale radius. The Newtonian Kn
  dependence now exists; use it as the Newtonian baseline of your Kn scan; your addition is the
  relativistic endpoint.
- 2510.24565: a further GR onset criterion (Fermi degeneracy) beside 2108.11967; no change.
- Novelty: no 3D full-GR kinetic SIDM calculation was found (package s37_38, CHECK #39; and an
  abstract check of 40 papers in s39_frontier).

Rows of coord/BRIEF_ERRATA.md:
- 2.55 (line 234, 2506.17641): its 0.3c, 1e-10 to 1e-8 of the halo mass and 1 Msun seed are
  the paper's conservative estimate; the same paper reports 200 Msun for a 6.3e9 Msun halo from
  the full-GR fluid model of 2601.17117, which gives about 3e-8 of the halo mass at horizon
  formation (open question Q14, partly answered).
- 1.29 (line 255): 2506.17641 computes no relativistic collapse; only 2601.17117 (spherical
  Misner-Sharp fluid with GR) does.
- 2.56 (line 234): 1501.00017 and 1812.05088 treat a subdominant strongly self-interacting
  component; 2504.00075 is a semi-analytic merger-tree model, not a collapse calculation.
