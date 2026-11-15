---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:A-emd-pbh-20261115-154740-69e8f8b, run:A-emd-pbh-20261115-161829-dba94f6]
---
At t = 0 the relative Hamiltonian constraint of solved periodic peak data is 3.5e-5 to 1.8e-4 on a uniform mesh, 0.077-0.085 with two static levels (linear in mu) and about 0.18 with four (runs A-emd-pbh-20261115-154740-69e8f8b, -161829-dba94f6): the data are interpolated onto refined blocks and the clouds stay on the root level. Request: the constraint solve on the refined levels of the actual mesh, and a nested particle lattice (more particles in the refined region) in the periodic generator.
Smallest acceptable answer: whether the id-solver handles static refinement, and a date for the nested lattice.
