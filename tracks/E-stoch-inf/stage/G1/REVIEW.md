# Lead's re-check of the helpers (G1 of E-stoch-inf)

The lead's review of the wave-2 and wave-2b helpers is `../REVIEW-wave2.md`, one file for
both gates. For G1 its parts are: the ladder's analyses rerun at the current commit from the
registered outputs, bit-identical in every number and pixel-identical in every figure (run
E-20261119-150842-ca70d37; the full rerun from the cold 256^3 dumps was stopped as I/O bound,
E-20261119-145853-ef835c2); the lead's own code on the 32^3 and 64^3 rungs (`scripts/lead_check.py`,
run E-20261119-150238-b81e33f, `fig/fig_lead_check.png`, `results/lead_check.json`): A1, A2,
A3, the record H0, the odd and even parts of H and their halving and the order 32 -> 64
agree with the ladder to the printed digits; the analysis package's synthetic tests rerun
identically (E-20261119-150346-a513bc8); A12 from the registered checksums.

Not confirmed by the lead's own code: A4 and A5 at 128^3 and 256^3 (only the ladder's
code read those dumps), and the attribution of the floor to rounding (no run tests it). The
lead's re-check is not a fresh-context verifier (checklist C16 stays OPEN).
