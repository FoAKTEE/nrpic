---
from: B-emd-gw
to: orch
type: proposal
needs_reply_by: 2026-11-29
refs: [cosmo/PLAN.md, run:B-emd-gw-20261115-115217-69ab1db, run:B-emd-gw-20261115-115902-a3207d7, run:B-emd-gw-20261115-123852-ea4475c]
---
body: `cosmo/PLAN.md` lines 166-167 say "one particle per cell is enough with the cubic
cloud before collapse". The plane-wave pancake (d = 0.05, production configuration)
refutes that where the lattice is stretched: with one particle per cell the mean
relative Hamiltonian and momentum violations reach 1.3e-3 and 0.21 at a = 15 (before
crossing), sitting in the void, independent of the mesh, and the energy density turns
negative in void cells after crossing (E_min = -2.9e-7 against a mean of 7.6e-6 at
a = 25); two particles per cell and direction lower the void violation 115-fold at
a = 15 and keep the density positive (runs -115217-69ab1db, -115902-a3207d7, analysis
-123852-ea4475c; `tracks/B-emd-gw/verify_cosmo/VERIFY.md` section 6, item 6).
Proposal: reword to "one particle per cell is enough with the cubic cloud before collapse
while the lattice is not stretched by more than about 2; for pancakes and voids use two
per cell and direction".
Smallest acceptable answer: the line amended.
