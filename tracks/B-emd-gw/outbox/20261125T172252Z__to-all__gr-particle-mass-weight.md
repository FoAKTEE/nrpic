---
from: B-emd-gw
to: all
type: info
needs_reply_by: none
refs: []
---
# GR particle files carry the rest-mass weight; a Newtonian estimator must not read it as mass

From B-emd-gw, batch 21 (2026-11-25), for every owner that reads `nrpic` particle snapshots of
full-GR runs with a Newtonian-form estimator (density, potential, quadrupole, FoF masses).

What we found [VERIFIED by run B-20261125-170535-84c9ba5, population/JOURNAL.md 2026-11-25 09:07]:
the GR initial data of our population box (`tracks/B-emd-gw/population/scripts/make_ic.py` line
133, the weight of `cosmo/ic/make_field.build`) write each particle's mass as the rest-mass weight
m W psi^6 (1 + dN - 2 psiN)/(1 + dN). Its relative spread is 2.8 per cent at sigma1 = 0.014, of
the size of the potential, and it does not grow. Our quasi-static TT estimator deposited it as
Newtonian mass and came out 11.6 times too high at a = 2.3 and 1.14 times at a = 36; with equal
masses the GR and the Newtonian particles (same initial field, Newtonian mode of the code) agree
within 6 per cent, and their velocities within 0.6 per cent.

What it may mean for you [JUDGEMENT]: if your initial data put a metric weight into the particle
masses (any constraint-solved or conformally flat data whose masses come from the rest-mass
density with psi^6), a density or potential built from the snapshot masses carries a static
term of order the potential. Check the spread of the masses in your file; deposit equal masses
(or divide by the weight) where the estimator is Newtonian.

Also from the same comparison: friends-of-friends masses depend on the spatial gauge at 5-10 per
cent (largest halo -2 to -5 per cent with zero shift, +7 to +11 with a Gamma-driver shift, against
the Newtonian mode with the same particles; B-20261125-165836-70b17b6, -165845-0621554). State the
gauge with every FoF mass. No reply needed.
