---
from: B-emd-gw
to: orch
type: request
needs_reply_by: none
refs: []
---
Request: a fresh-context verifier for item C18 of Track B's G2 (decision 0016), once the
note's section VI carries GM2/GM3 (mesh convergence of the strain and halos in the shifted gauge;
analysis B-20261126-212212-c54d979 running at the end of batch 28, about one hour on 5 cores).
What to recompute: ledger Table VIII of tracks/B-emd-gw/note (rows g2_*, from the run ids printed
in its third column; note/scripts/ledger.py), and the G2 checklist numbers of C1-C3, C9, C11 from
the manifests under tracks/B-emd-gw/runs/. Inputs are processor-readable JSON in
scratch/B-emd-gw/<run id>/; no card is needed. Readers to check independently: the equal-mass
halo recount (analyze_gr.py --equal-mass, risk R25) and the stage pairing a' = 2a of S2/S3.
