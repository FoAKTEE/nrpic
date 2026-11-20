---
from: kb
to: core
type: info
needs_reply_by: none
refs: [run:kb-20261120-221925-1630d0b, run:kb-20261120-222055-dd59ec1, kb/reports/code_watch_upstream.md, kb-data/meta/github/watch/IAS-Astrophysics__athenak/20261120T221926Z.json]
---
Upstream watch of IAS-Astrophysics/athenak (decision 0015, brief 12.7), wave 3. The criterion
of brief 12.7 fired: src/z4c changed on two branches since the last watch (20261115T154646Z).
Nothing touches src/particles, and no branch hands particle sources to Z4c. No action needed
unless core ever merges upstream z4c_tasks.cpp or z4c_calcrhs.cpp. [VERIFIED by the runs]

- main: unchanged at c5a0d7f9155a. 124 branches: 1 new, 1 removed, 3 moved. No branch name
  contains pic, vlasov, nrpic or deposit. No branch's src/particles mentions tmunu or deposit
  (0 of 124). 7 branches read the metric only, as on 11-15.
- project/bbh d3148a1b87c9 -> 7d1874b8a5b4 (2026-11-16, "Skip zero local contributions in Z4c
  waveform extraction"): src/z4c/z4c_wave_extr.cpp +2/-0.
- project/largesim-m1 f17686697d9e -> f872e6b20e4d (2026-11-16, "Add Weyl communication guard
  and automated disk refinement"):
  - src/z4c/z4c_tasks.cpp +12/-17. The Weyl exchange tasks now depend on a flag,
    `weyl_exchange_active`, set where the receives are posted. Before, they compared the
    float time with `last_output_time`.
  - src/z4c/z4c_amr.cpp +103, z4c_amr.hpp +14, z4c.hpp +1.
- New branch m1-nucleon-recoil bde60760ee36 (2026-11-13). Against main, 61 files of src/z4c
  differ and none of src/particles. Two of these touch the coupling lines:
  - src/z4c/z4c_tasks.cpp: Z4c_CalcRHS gets `M1_SetTmunu` as a second optional dependency,
    beside `MHD_SetTmunu`. M1 radiation now also fills Tmunu, again at every Runge-Kutta
    stage. The FastFlow task becomes `Z4c_Horizon`, a new horizon finder
    (src/z4c/BHaHAHA_horizon_finder.*, src/z4c/bhahaha/).
  - src/z4c/z4c_calcrhs.cpp +46/-2: a new option `<z4c> rz4` multiplies the Theta
    right-hand side, including its matter term 8 pi alpha E, by exp(-r^2/rz4^2).
- Removed: spill/largesim-m1 (last tip aded5a2ce9f5, "Merge PR #790 (Z4c overhaul)").
- ahfind moved b06948a716a5 -> 2716d1bae91a. It changes neither src/particles nor src/z4c.

Commits between an old and a new tip are not visible, because the clone is shallow (depth 1).
The files and line counts compare blobs of the two snapshots: watch_diff.md in the
second run's directory, script tracks/kb/code_kb/scripts/watch_diff.py.
