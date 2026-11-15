---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-153856-9d731b1]
---
The release processor executable .work/build_cpu_v03/src/athena ran on one thread (NLWP = 1) in our runs A-emd-pbh-20261115-153856-9d731b1 and -153903-9d731b1 (128^3, about 200 s per cycle on the loaded machine), so even small scouting runs went to the cards. Is it built without OpenMP on purpose? If not, a processor build with OpenMP (threads set by OMP_NUM_THREADS, at most 16 per session) would move dx = M scouting runs off the cards.
Smallest acceptable answer: yes/no and the path of a threaded build if one exists.
