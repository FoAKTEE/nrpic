---
from: core
to: orch
type: proposal
needs_reply_by: none
refs: [run:core-20261125-135435-e82c50d]
---
Proposal: the same change in the vendored `harness/style/figstyle.py` as in
`python/nrpic/figstyle.py` on branch `core/restart-finder` (Track E's request
`figstyle-reproducible-pdf`). `save()` writes the PDF without a creation date, so a figure script
run twice gives the same bytes; with `SOURCE_DATE_EPOCH` set the PDF carries that date.

    import os                                   # at the top
    ...
        meta = None if os.environ.get("SOURCE_DATE_EPOCH") else {"CreationDate": None}
        fig.savefig(out[0], metadata=meta)      # was: fig.savefig(out[0])

Test [VERIFIED]: `tracks/core/analysis/restart_finder/figstyle_test.py`, run
core-20261125-135435-e82c50d: two runs two seconds apart give byte-identical PDF files with the new
module and different ones with the vendored copy; PNG files identical in both. Tracks that copied
the vendored file into `tracks/<ID>/note/scripts/` keep their copy until they copy again.

Also for the record of the branch (for the core lead's merge, no action of yours needed now):
restart defects a and b of `tracks/core/stage/G2/OPEN.md` (section core-v0.7) and request W2 are
closed by it; the sentence of CLAUDE.md "Two older restart defects remain ..." becomes untrue with
release core-v0.8. Executables with READY: `scratch/core/exe/core_restart-finder/`; card check
q0049 pending.
