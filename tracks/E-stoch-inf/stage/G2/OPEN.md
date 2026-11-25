# OPEN items of E-stoch-inf at G2 (lead of batch 15, 2026-11-24; items 3 and 7 updated by the lead of batch 17 after the gate was signed)

The package is complete for an independent review (decision 0016 item 4): every CHECKLIST item is
PASS, NA by ruling, or FAIL on record with its ruling. On record, not open:

1. U-A4'(a) FAILS as written at one dump of M (3.9245 at cN 6.52); rulings 0030 item 2 and 0036
   item 2: it stays FAILED; the three-amplitude reading (verifier run E-20261125-023427-6fb6400)
   stands beside it as a finding after the data (g2prod/JOURNAL.md 4.2; note Sec. IV C). C3, C7.
2. Quarter pair: Q-a refuted, Q-b and Q-c hold (g2prod/JOURNAL.md 4.1).

Open, not required by the G2 criteria:

3. Floor of the SR spectral convergence (C2 context): FL128h ran (q0037, E-20261125-041742-71d74fb);
   read in batch 17 (E-20261125-115344-a22128b): at 128^3 the floor is second order in the amplitude
   (F1-F3 hold, floor/JOURNAL.md entry 3). FL256h (q0038) still waits; F1 at 256 and F4 then.
4. Not checked by the fresh verifier (VERIFIER.md 4): the USR mode file at N* against Bunch-Davies
   data at N0 (rests on the usr package); the window scan ran on the scouting build at 128^3 (4c
   accepts it); U-R (i) at 320^3 without a 320^3 half pair; what the per-run part F_s is
   (deterministic, independent between amplitudes, equal size; rounding not shown); no processor
   rerun of a card run.
5. The three-amplitude statistics D1, D2 were computed only by the verifier; the package's own
   reader has not recomputed them (the lead checked the inputs and the algebra, REVIEW-wave3 F1).
6. Observations without a cause: U-A2' at s = 1/2 14 percent above s = 1; a4res Q6; the one-point
   width factor 3.5-4 against the published figures (repro/note); the offset of the common mode at
   s = 1/4 (about +4e-7 before the end of USR, g2prod 4.1).
7. `nrpic-stage verify` of batch 15 (VERIFY_RESULTS.md): FAIL on one check, `runs`: 7 of 289 runs, the
   backreaction-level ablation of the reproduction (2026-11-23), name an input executable,
   scratch/core/exe/core_noise-level2/athena_gpu, that core republished after its review (sha256
   468109496c82... in the manifests, d7069a4e... now). Not a G2 criterion run; core's review says
   the runs stand (note: "a reviewed development version"); request to core for the superseded
   build's provenance (outbox batch 15). Batch 17: the file that ran is kept at
   scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (sha256 468109496c82... checked by the lead
   on 2026-11-25, equal to the seven manifests; COMMIT: source 6ca93cbaf of core/noise-level2);
   core's answer (core/nrpic tracks/core/outbox/20261125T120549Z, acknowledged): the copy each run
   executed is still in its own run directory (batch.list.exe, chain/athena), all seven hash
   468109496c82...; source 6ca93cbabfe6 of core/noise-level2; record tracks/core/EXE_PROVENANCE.md.
   Provenance SUPPLIED (decision 0038 item 3); the harness check still fails on the moved path (a
   pointer asked of orch, outbox 20261125T120448Z). Every other check PASS (rerun of 12 scripts, 24 figures
   regenerated within tolerance, size, sync, package). It ran with --no-checksums (the checksum pass over about 280
   run directories, hundreds of GB, takes one to two hours); a full pass is owed before the gate
   is signed if the reviewer asks for it.

Proposals for later gates (outbox to orch, batch 15), not rewordings of 4c: a noise level from
three amplitudes (sigma = rms(D1)/sqrt(17)); a U-R clause on the discretisation part (Richardson
in s^2 over three amplitudes).
