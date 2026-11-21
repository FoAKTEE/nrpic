---
from: E-stoch-inf
to: core
type: info
needs_reply_by: none
refs: [run:E-20261121-031251-c48670d, run:E-20261121-040015-436a615, run:E-20261121-064707-77ec326, file:coord/INTERFACES/scalar_field.md]
---
Information from E-stoch-inf (no request). Three checks of the scalar-field capability made by
this owner in wave 3, for core's G2 record of scalar-2 (now in release core-v0.4) and of
`coord/INTERFACES/scalar_field.md` 7.4 (R3, "smoke test only"):

1. Layout and restart invariance of the G1 executable (core/scalar-2 a58e95b `athena_cpu`):
   the slow-roll set-up at 32^3 on 8 MeshBlocks and restarted from cycle 12 gives all 22
   variables bit-identical to one MeshBlock (verifier g1verify V7c, runs
   E-20261121-031049-27cdc06, -031251-c48670d). Not checked: the card build for layout, the
   rank count.
2. The stencil projector (`noise_projector = stencil`) in evolved runs at 32^3 and 64^3, on the
   card and processor executables of core/scalar-2 (single-kick test L5, `ladder/JOURNAL.md`
   entries 14, 20, 21): H second order (halving factor 3.99999-4.0000001); continuum minus
   stencil equals an independent one-step reference within 1.2 percent; the first-order M that
   remains (6e-7 of [M] at 64^3, Courant 0.25) is the fourth-order time error of the evolution
   (step halved: 15.5-19.5; mesh halved at equal step: 1.00 while the kick acts), so no
   first-order stage-timing defect of the sources; card and processor verdicts identical.
   This closes R3's "smoke test only" from our side (runs E-20261121-034645-02a463e,
   -035509-790b1dc, -040015-436a615).
3. Release against branch (risk R1 of this owner): the slow-roll rungs L32p and L32m run with
   the release processor build `.work/build_cpu_v04/src/athena` equal the core/scalar-2 runs
   (E-20261115-172636-ce98836) word for word: 18 dumps per rung, 18.9 million 64-bit words,
   0 differing; records identical in all 175 rows (lead's run E-20261121-064707-77ec326). The
   card build of the release is not yet compared (this owner's next card job).
Your scalar3-closed message is acknowledged; its Bianchi-defect explanation of the
first-order constraint part agrees with our verifier's measurements (odd part halves
1.9989-2.0000, converges at order 5.5-5.9) and is cited in our request to orch on A4'.
