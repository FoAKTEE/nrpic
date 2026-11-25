# Writing guide: Kozai-Lidov Oscillations of Compact Binaries in Full Numerical Relativity

The per-paper layer of the paper-writing principles. Keep this file outside `paper/`.

## Journal and tone (2.8)

- Target journal: Physical Review Letters
- Where the methods go: Technical grid architecture, simulation catalog table, and coordinate derivations go in Appendix / End Matter
- Tone: Concise Physical Review Letters prose, active present tense, human voice, zero filler or hype

## Readers (1.2)

| Community | Minimum background the paper supplies |
|---|---|
| Numerical relativity | Physical scalings of hierarchical triple dynamics, Hill stability, and quadrupole/octupole secular excitation |
| Relativistic astrophysics / LISA EMRIs | Conformal-puncture initial data, conservative particle-mesh coupling, and finite-radius Weyl-scalar waveform extraction |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | Core physical argument for PRL | Introduction; Relativistic Triple Formulation; Secular Excitation, Quenching, and Spin Coupling; Gravitational-Wave Signatures; Conclusions |
| Appendix | Reference table and grid setup | Numerical Architecture and Simulation Catalog |

Special cases entered as limits (2.2): Equal-mass, nonspinning Schwarzschild triples enter as the quadrupole baseline before nonzero spin (`\chizero`) and unequal mass ratios (`m_1 \neq m_2`).

## Allowed numbers (4.1)

- Exact analytic factors and powers: `2`, `3`, `4`, `3/2`, `5/2`, `2/3`, `3+1`
- Structural integers: three-body triple (`1` central black hole, `2` stellar-mass black holes), fourth-order implicit Gauss-Legendre integration, quintic particle-to-mesh interpolation
- Labels of cases: canonical run identifiers in the catalog table only
- Numerical parameters and measurements belong in the Appendix table, figure captions, and figure labels rather than main-text prose

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| three-body triple | toy model | Astrophysics |
| post-Newtonian baseline | sanity check | Relativity |
| benchmark | proof of concept | Numerical relativity |
| binary-EMRI system | cloud disruption | Astrophysics |

## Project names (7.7)

- nrpic_grlbv
- kerr09_cloud_1m
- pn_zkl_scout
- repro_wave4c
- gb204
- login05
- Athena++

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters (cited from the setup table) |
|---|---|---|
| 1 | Relativistic triple eccentricity evolution across inclination threshold, 1PN pericenter quenching, and central Kerr spin plus unequal-mass octupole modulation | Table I Suites I--IV |
