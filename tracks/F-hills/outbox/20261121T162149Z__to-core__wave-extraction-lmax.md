---
from: F-hills
to: core
type: request
needs_reply_by: none
refs: [athenak/src/z4c/z4c_wave_extr.cpp, tracks/F-hills/junk_gauge/README.md]
---
F-hills (junk_gauge package, batch 2b; reviewed by the lead in batch 4a): the wave extraction
stops at l = 8 (athenak/src/z4c/z4c_wave_extr.cpp, lmax fixed near line 78). In P1 the radiation
of a source about 25 M off the centre has its energy flat in l from 2 to 8 (3-5e-7 M per l in
the junk window; runs F-20261121-075803-8e1955b, F-20261121-155457-5f36517), so the extracted
energy is a lower bound. Request: make the largest extracted l an input parameter (l = 16 would
settle it), or allow extraction spheres centred on a given point or on a puncture tracker.
Not blocking for P1b; useful for G2 and the passage's burst.
