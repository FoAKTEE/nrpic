# JOURNAL of package g3/amend (Track E, gate G3): the lead's checks of the scope review and the amendments of SCOPE 4d

Batch 19 (2026-11-25), lead of E. Ruling: coord/DECISIONS/0040 item 1. Review: `../scope_review/SCOPE_REVIEW.md`.

## entry-1 (2026-11-25 07:25 PST): B1, the top bin of the lattice factor; predictions before `bins_lead.py`

What I have already seen: the review's numbers (factor 0.279 against 0.934 for |n| <= 32, 0.166 against
0.992 for 64; expected variant/lattice 0.9778 and 0.9906; top-bin share 3.4 and 1.1 per cent). My script
`bins_lead.py` uses none of the review's code and none of ref_spec's binning code (own vector count, own
bins written from the rule, own integrals); its weight (b) takes P_R(N_e) from the reference's linear module.
Predictions:
- LB1 (weight P_R(N_e)): variant/lattice as ref_spec bins it 0.978 +- 0.002 (32) and 0.991 +- 0.002 (64);
  with the top bin cut at NLAT 1.000 +- 0.001 at both; top-bin factor as is 0.28 +- 0.02 (32), 0.17 +- 0.02
  (64); top-bin share of the band 0.034 +- 0.005 (32), 0.011 +- 0.003 (64). Refuted if the as-is ratio at
  32 lies outside [0.970, 0.985] or a fixed ratio outside [0.998, 1.002]: then B1 is not confirmed as
  stated and the reference is not changed on its strength.
- LB2 (weight P = 1, pure lattice geometry, no reference code): the top bin spans only ln 32 - 3.45 =
  0.016 of 3.47 in ln n, so the as-is deficit is small, 0.996-0.998 at 32; fixed within 0.003 of 1 (the
  sparse low shells make the per-bin factor a coarse stand-in for the lattice sum). Refuted outside.

## entry-2 (2026-11-25, written before the rerun of the pilot reference): the corrected reference, its variance gate

Change to `../../langevin/scripts/ref_spec.py` (lattice_factor_fn): the upper edge of the last bin is cut at
NLAT (the review's second option), and for the lattice variant the tails are also standardised with
sigma = sqrt(var_lattice_Ne) (B1, last sentence). The output of the corrected pilot goes to
`results/ref_inflection_n32_binfix.json` (`NRPIC_REF_SUFFIX=_binfix`); the old file stays.
Pilot rerun: 2e5 realisations, NLAT = 32, as E-20261125-115707-b845282 otherwise.
Predictions:
- RF1 (the variance gate of the amended 4d.3 at the pilot's size): var(s0.01_lattice)/var_lattice_Ne =
  1.000 within three of its standard errors (about 0.0032 each at 2e5; the old run gave 0.9796 +- 0.0032).
  Refuted if outside 1 +- 3 se: then the variant has a second defect and no tail comparison uses it.
- RF2 (only the lattice variant changes): every other variant gives the same moments as the old file to
  all printed digits (same seeds from crc32 of the variant name). Refuted otherwise (then the run is not
  deterministic and the pilot comparisons need their own seeds on record).
- RF3: skewness of s0.01_lattice at N_e within two standard errors of the old value (0.0288 class; the top
  bin carries 3.4 per cent of the variance and is near Gaussian at crossing, so the shape moves little).
