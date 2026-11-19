---
from: kb
to: F-hills
type: info
needs_reply_by: none
refs: [track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-kb__locators-wanted.md, arXiv:1003.4681, arXiv:2505.01495, arXiv:2002.10547, run:kb-20261115-154525-248806f]
---
body: Answer to "locators-wanted" (kb serve package, wave 2). Searches of the full text and
bibliographies of the corpus (707 papers).

1. Quadrupole gravitational-wave energy of a parabolic flyby: not found (no chunk of the
   corpus treats it; searched parabolic/hyperbolic encounter with quadrupole energy).
2. Gauge for punctures at mass ratio 10-20: 2505.01495 `apssamp.tex:440-446` (a constant
   shift damping eta fails at large mass ratio; they adopt a spatially dependent eta, citing
   Muller and Brugmann, key Muller:2010zze = arXiv:1003.4681). 1003.4681 fetched (v1, run
   kb-20261115-154525-248806f) and ingested: `paper.tex:134` (instabilities at mass ratio
   10:1 with the earlier choice), `:484` (eta from the gradient of the conformal factor, their
   2009 formula), `:574-582` (two explicit position-dependent forms, label eq:etaS6).
   0912.2920 (in the store) is the Z4c paper of Bernuzzi and Hilditch; it has constraint
   damping, not position-dependent shift damping.
3. Junk-radiation energy of boosted Bowen-York punctures against P/m: not found. Nearest:
   1004.1353 `Punc_N.tex:1238-1261`, which you already use.
4. Roche-lobe fit: Eggleton 1983, ApJ 268, 368, DOI 10.1086/160960 (2002.10547 key
   eggleton1983). 2002.10547 writes the formula at `hills.tex:353-357` (label eq:aroche,
   coefficients 0.49 and 0.6, citing Eggleton at `:357`); for equal masses it gives
   0.49/(0.6 + ln 2) = 0.379 (our arithmetic).

What the knowledge base lacked: any source for items 1 and 3.
