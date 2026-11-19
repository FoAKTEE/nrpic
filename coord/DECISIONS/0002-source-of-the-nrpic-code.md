# 0002 Source of the NRPIC code (D2)

Status: ACCEPTED for the rebuild; ACCEPTED by the user on 2026-11-19 (decision 0017); before that provisional for the request to the authors · 2026-11-15

Fact. The critical-path risk of the brief (sections 1.9 and 2.2: the particle-spacetime
coupling is not in public AthenaK) is retired in this repository. An independent rebuild
from the published text exists here and is verified: pushers, metric reconstruction,
deposition with filter and compensation, coupling to Z4c, deposition across refinement
boundaries, initial data, excision, restart, diagnostics (`athenak/src/particles/`,
`athenak/src/pgen/nrpic/`; tests in `docs/TESTLOG.md`; manuscript `paper/main.pdf`). The
extension to periodic domains with a cosmological gauge and density-form sources also
exists (`cosmo/`, `cosmo/TESTLOG.md`, `cosmo/paper/main.pdf`).

Decision. core starts from this implementation: steps C0 to C4 of the brief become
"document, re-verify, tag" (core-v0.1: asymptotically flat capability; core-v0.2: periodic
particles and cosmological gauge), and new work in core is what the tracks need next.
Whether to ask the authors of arXiv:2611.12831 for their code is for the group; nobody has
been contacted. Upstream is re-checked weekly by the knowledge base.
