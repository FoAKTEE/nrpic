---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-153719-91b03d1]
---
The time step ignores the coordinate speed of light (core G2 OPEN item 12). In geodesic slicing of a collapsing core the radial coordinate light speed grows as R_i/R (17 at the first trapped sphere of data set 2t), so SR-1 needs six restarts with smaller cfl_number in the last 2.5 M (step plan in run A-emd-pbh-20261115-153719-91b03d1, runs_ball/JOURNAL.md entry 2). Request: a step limit dt <= cfl dx / max(coordinate light speed) evaluated from alpha, beta and the metric each cycle (or every n cycles), off by default.
Smallest acceptable answer: yes/no for this wave.
