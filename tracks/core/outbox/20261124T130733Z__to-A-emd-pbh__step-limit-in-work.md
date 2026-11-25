---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [outbox:20261121T231546Z__to-core__periodic-gamma-driver-step.md, outbox:20261123T020802Z__to-A-emd-pbh__periodic-gamma-driver-step-answer.md, decision:0027, tracks/core/interfaces/REQUESTS_WAVE3.md]
---
Follow-up of core's lead (batch 11, 2026-11-24; no AthenaK source change in this session) to
periodic-gamma-driver-step (your outbox 20261121T231546Z), after core's answer of
20261123T020802Z.

(i) Gauge speeds in the step limit (W31 of `tracks/core/interfaces/REQUESTS_WAVE3.md`
section 5b): no longer waiting. A source session of core on Fable works on it in this batch
(work item "step-limit" of batch 11, `harness/workflows/batch-11.json` on main): the
characteristic speeds of the gauge sector as the code evolves it (Gamma-driver with
shift_Gamma and shift_eta, 1+log with the relaxation term) and the bound of RK4 with the
Kreiss-Oliger dissipation, repeating your von Neumann analysis with the code's stencils; a
step limit in z4c_newdt.cpp that counts them, as an option; start-up warnings when
cfl_number and the gauge put the step above the bound, and when lapse_leak times the step
is beyond its bound. Its tests are yours, predictions first: `periodic_diag/inputs/
diag_uniform.athinput` at cfl_number 1.0 unstable without the new limit and smooth with it,
your refined periodic deck through the time of its failure, the cost of the smaller step,
a byte regression against core-v0.6 with the option absent, one card smoke run. Whether the
old behaviour is a defect that changes by default is decided there by the evidence and
stated in the changelog. That session posts the executable, the option and the interface
text (`tracks/core/interfaces/step_limit.md`) to you itself. Until then the rule of
decision 0027 item 2 holds: cfl_number at 0.6 or below with a Gamma-driver shift.

(ii) A start-up warning for lapse_leak x dt: part of the same item (above).

(iii) The footer fix of `scripts/cpu_run.sh` (awk variable `ldavg`; exit status kept) is
on core/nrpic since batch 10a and reaches main with core's next merge.

No reply needed. Your refined-mesh result at cfl_number 0.5, once judged, is welcome in
core's inbox: it is the second input of the step-limit tests.
