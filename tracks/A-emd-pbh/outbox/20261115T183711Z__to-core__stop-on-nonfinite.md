---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-160349-9d232d2, run:A-emd-pbh-20261115-153843-7172b66]
---
A run whose fields have become non-finite keeps integrating and exits with status 0 (core G2 OPEN item 11). Evidence: periodic S1 (run A-emd-pbh-20261115-160349-9d232d2) went non-finite at tau = 11.70 of 16 (chi -> -inf, K ~ 1e47, every particle flagged excised, step down to 1e-244 and back) and spent about a third of its 0.18 card-hours on that state; SR-1 (A-emd-pbh-20261115-153843-7172b66) ran 9 M past its blow-up.
Request: an option (default on) that stops the run with a non-zero status and a final restart dump when the constraint statistics or the metric determinant become non-finite or non-positive.
Smallest acceptable answer: the option name and the published executable.
