---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-01
refs: [run:D-20261124-130935-fdca920, run:D-20261124-140606-286a302, run:D-20261124-172508-c847ee4]
---
Finding of Track D (tracks/D-bh-dress/g2long/JOURNAL.md entry 14; runs D-20261124-130935-fdca920 and
D-20261124-140606-286a302, finder re-search of restart dumps; judgement D-20261124-172508-c847ee4,
fp_analyse.json and fp_analyse.png in its output directory): the apparent-horizon finder's stopping
rule, not the slice, sets the vacuum "noise floor" of D's null test.

What: `fastflow` stops the flow at the first iteration whose mass differs from the previous one by less
than `mass_tol` (athenak/src/z4c/fastflow.cpp:914), starting from the previous surface. With mass_tol =
1e-5 (every input of D) the reported mass of a vacuum puncture at M/8 and M/16 sits on one of two
plateaus about 1.3e-4 apart and switches between them (V-1L, V-1L16, 230-500 M); summary column 9 (area
mean of the squared expansion, fastflow.cpp:825, :1504) is ~7e-9 on the plateaus. Re-searching the dumps
on one cycle with the release core-v0.6 threaded processor build:
- mass_tol 1e-5 from the dump's stored radius reproduces the run to 3.6e-6 at all 29 dumps;
- mass_tol 1e-5 from 2 M (outside) lands on the low plateau at every dump (V-1L: 1.000915-1.000933);
- mass_tol 1e-9 with 4000 iterations gives V-1L 1.000980-1.000998 at every dump from 100 to 500 M
  (spread 1.8e-5), where the run's own mass jumps by 1.2e-4; V-1L16 within 3.9e-6 over 100-300 M.
- ntheta 16 / lmax 8 against ntheta 32 / lmax 16 (both tight): the mass differs by -1.80e-4, -1.85e-4,
  -1.85e-4 at M/4, M/8, M/16, the same on every mesh (an angular truncation of the surface at r ~ 2.2 M).

Requests (smallest acceptable answer first):
1. Interface text (coord/INTERFACES, finder section): mass_tol is an absolute change of the mass between
   two flow iterations; the reported mass can then lie about 6 times mass_tol from the converged one,
   on the side the flow comes from; a converged mass needs mass_tol <= 1e-8 with flow_iterations of a
   few thousand; the angular resolution A16 carries an offset of ~1.8e-4 M at r ~ 2.2 M that cancels in
   differences only.
2. Optional, for core-v0.7: a stopping rule on the residual (summary column 9), or a fixed number of
   polishing iterations after the mass rule is met, off by default; with its cost per call on a card.
No source change is needed for D's own runs: D re-searches dumps with the tight rule on processors and
new null-test inputs set mass_tol_0 = 1e-8. Other tracks that read horizon masses to 1e-4 (A's threshold
scan, F's punctures) may want to know.
