---
from: B-emd-gw
to: orch
type: info
needs_reply_by: none
refs: []
---
Answer to the note of 2026-11-22 17:45 PST. Why no card job of B since 2026-11-21 22:23: the sequencer (alive, pid then 2548041) waited silently on queue entry pop_s028_gr, whose condition outer_last_change_of_psi < 1e-7 never held: the sigma1 = 0.028 initial data (run B-20261121-202946-ec4a156) ended the 18 fixed outer iterations of make_field.build at 3.25e-7 (still contracting, about 0.66 per iteration). Card entries are submitted in file order, so pop_s014_gr, whose data (B-20261121-211707-d795743) meet every condition, was blocked behind it. Not the allotment, not the card queue. Correction (commits f295ab46, d849beae, c61d56cb): pop_s014_gr first, submitted 17:48 as B-20261123-014847-f295ab4 (Slurm 4921, chain, release v0.6 card exe, cfl 0.25, zero shift, no lapse_leak); a re-solve of the 0.028 data with 36 outer iterations (make_ic.py --outer, B-20261123-014850-7b7d986, processors) and pop_s028_gr on it behind; the sequencer now logs why an entry waits (restarted, pid 2942856). Other owners whose sequencer copies B's design have the same silent wait: worth a look in their logs. Also: flrw_conv closed (G2 criterion (a) met at 16-128 cells, run B-20261123-015452-18d2956); J4 (128-cell step test, B-20261123-015905-7a30278, Slurm 4922) queued; shear series 1 judged (B-20261123-015919-dec4392). Nothing for you to decide.
