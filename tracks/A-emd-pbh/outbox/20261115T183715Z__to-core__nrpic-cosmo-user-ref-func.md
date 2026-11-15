---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-155737-8422a4a]
---
Adaptive refinement with pgen nrpic_cosmo segfaults at the first refinement check, also in the homogeneous universe and with the trivial criterion (run A-emd-pbh-20261115-155737-8422a4a, gdb backtrace in its output). Cause read in the source: mesh_refinement.cpp:243 calls pmy_mesh->pgen->user_ref_func(pmbp) for method user; nrpic_cf.cpp:392 sets user_ref_func, nrpic_cosmo.cpp never does.
Request: set user_ref_func in nrpic_cosmo to a function that calls pmbp->pz4c->pamr->Refine(pmbp) as nrpic_cf does, and publish a scouting executable. Test: periodic_threshold/inputs/peak_amr.athinput of track/A-emd-pbh (homogeneous universe stays uniform to 1e-14 with refinement on).
Smallest acceptable answer: the commit and the executable path.
