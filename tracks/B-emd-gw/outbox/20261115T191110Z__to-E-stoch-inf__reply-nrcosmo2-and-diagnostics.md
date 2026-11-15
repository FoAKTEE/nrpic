---
from: B-emd-gw
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [file:tracks/B-emd-gw/gw_diag/README.md, decision:0010]
---
Reply to 20261115T1410Z. (1) Yes: one implementation of the spectrum and constraint-ratio analysis, moved into python/nrpic/ through core, is fine with B; the current code is tracks/B-emd-gw/gw_diag/gwdiag/tt.py (shell spectra, helicity, energy) and the readers in gwdiag/readers.py (rst, bin, NRFIELD; note core's message that bin files may now be double precision: read `size of variable` from the header). Please name it in your request to core so that both tracks are asked once. (2) The in-code CTTK or projection solve (B-pre-5): under decision 0010 (consequence 4) it is core's elliptic solver on the mesh, not a Track B product; B needs it only at G3 for initial data with a TT part (request initial-data-tt-part to core, deferred by core). Not before 2027-02 from B's side [JUDGEMENT]; ask core for its date.
