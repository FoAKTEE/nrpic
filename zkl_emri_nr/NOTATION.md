# Notation: Kozai-Lidov Oscillations of Compact Binaries in Full Numerical Relativity

The notation dictionary for the PRL manuscript. Keep outside `paper/`.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| `M_0` | `\Mzero` | Central supermassive black hole mass | Sec. I |
| `\chi_0` | `\chizero` | Dimensionless Kerr spin parameter of central black hole along `+z` | Sec. I |
| `m_1, m_2` | — | Individual masses of the two stellar-mass black hole particles | Sec. II |
| `m_{\mathrm{bin}}` | `\mbin` | Total mass of the inner binary (`m_1 + m_2`) | Sec. II |
| `a_{\mathrm{in}}, e_{\mathrm{in}}` | `\ain, \ein` | Local Fermi-frame inner binary semimajor axis and eccentricity | Sec. II |
| `a_{\mathrm{out}}` | `\aout` | Outer binary semimajor axis around central black hole | Sec. II |
| `I_0` | `\Izero` | Initial mutual inclination between inner and outer orbital planes | Sec. III |
| `R_{\mathrm{H}}` | `\RH` | Hill radius `a_{\mathrm{out}}[m_{\mathrm{bin}}/(3M_0)]^{1/3}` | Sec. II |
| `f_{\mathrm{H}}` | `\fH` | Hill filling fraction `a_{\mathrm{in}}/R_{\mathrm{H}}` | Sec. II |
| `\epsilon_{\mathrm{GR}}` | `\epsGR` | Relativistic pericenter-precession quenching parameter | Sec. III |
| `t_{\mathrm{ZKL}}` | `\tZKL` | Characteristic quadrupole Zeipel-Kozai-Lidov timescale | Sec. III |
| `r\Psi_4` | `\rPsifour` | Outgoing Weyl gravitational-wave scalar | Sec. IV |
| `\alpha` | — | Lapse function | Sec. II |
| `\mathrm{d}` | `\dd` | Differential operator | Sec. II |

## Named results

| Name | What it is | Where |
|---|---|---|
| the relativistic quenching parameter | Dimensionless ratio `\epsGR` comparing general-relativistic inner pericenter precession to outer tidal torque | Sec. III |
| the local-frame harmonic transformation | 1PN conformal and Lorentz velocity mapping between proper binary rest elements and global harmonic coordinates | Sec. II |
| the static concentric shell hierarchy | Fixed nested spherical refinement boundaries avoiding time-dependent regridding noise in high-cadence waveforms | Appendix |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | upright differential `\mathrm{d}` |
| `\Mzero` | `M_0` |
| `\chizero` | `\chi_0` |
| `\mbin` | `m_{\mathrm{bin}}` |
| `\ain` | `a_{\mathrm{in}}` |
| `\ein` | `e_{\mathrm{in}}` |
| `\aout` | `a_{\mathrm{out}}` |
| `\Izero` | `I_0` |
| `\RH` | `R_{\mathrm{H}}` |
| `\fH` | `f_{\mathrm{H}}` |
| `\epsGR` | `\epsilon_{\mathrm{GR}}` |
| `\tZKL` | `t_{\mathrm{ZKL}}` |
| `\rPsifour` | `r\Psi_4` |
