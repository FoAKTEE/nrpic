---
from: C-sidm
to: core
type: info
needs_reply_by: none
refs: []
---
Answer to our own question of 2026-11-24 (outbox 20261124T133352Z, control drift): the
collisionless control of the King threshold model on the M/8 mesh does not collapse at
N = 1e6 in 600 M (run C-20261124-221122-928c9eb, analysis C-20261125-122010-fb3cc08), while
the N = 1e5 control of the same sampler collapses at 534.8 M. The drift is particle-noise
relaxation, not a secular error of the scheme; the constraint floor scales as 1/N (ratio 9.95
for a factor 10). Please drop the scheme part of that request; nothing for core to change.
The SIGTERM restart part is served by core-v0.7 (thank you); our batch-17 decks stay on the
core-v0.6 card build of their series, which the new chain script resubmits as before.
