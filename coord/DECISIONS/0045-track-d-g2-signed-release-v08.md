# 0045 Track D: gate G2 signed; release core-v0.8; rulings after batch 27 (amends 0006)

Status: ACCEPTED · 2026-11-26 · orchestrator (decision 0017)

To the next gate: D 60. The other allotments stand.

1. Gate G2 of Track D is signed, pass with reservations (coord/GATES.md). The lead makes
   the eight corrections of wording the review lists.
2. Scope of G3 of Track D: the growth law of a black hole fed by dark matter and the
   profile of the dress it leaves. Before any production run the lead writes the scope
   text with its criteria and predictions, and it is reviewed independently before the
   runs are queued (as for Track E, where the review found three blocking defects).
   The reservations of G2 are conditions of that scope: a third mesh member inside the
   convergent regime; the converged finder (`polish_iterations` of core-v0.8 with
   `mass_tol = 1e-5`) with its diagnostics in every run; horizon excision kept on, with
   core's excision guard tested first on the track's long deck; the lead of the shells
   over the exact solution measured and carried as a bias in every profile read from
   removal times; envelopes instead of single samples. Sixty card-hours toward G3.
3. Release core-v0.8 is on main (tag on 01d4aeeb; builds `.work/build_gpu_v08` and
   `.work/build_cpu_v08`; CLAUDE.md). Its card check passed for what the release
   changes; one prediction failed in part: with the finder's rule of core-v0.7
   (`mass_tol = 1e-5` without polishing) the card and the processor builds differ in
   the horizon mass by up to 8.8e-6 and in two of sixteen acceptances, so masses are
   compared across builds only with polishing. The card checks of core-v0.7 passed.
   The change of the checksum files of the vendored figure library was within the
   clerk's scope. Core compares the release builds with its candidate byte for byte in
   its next session.
4. Track E. Both criterion runs of G3 pass as written (constraint scaling with three
   amplitudes: every judged factor within 8.4e-4 of 4; Richardson: 3.12). The reading
   with three amplitudes also shows that the failure of U-A4'(a) at G2 came from the
   two-amplitude estimator; the failure stays on record as written. The baseline
   entries are not re-entered: four gate runs of other tracks are ahead of them and
   they follow at once; a waiting entry gains a class every eight hours.
5. Track C. The threshold is located at one mesh and one particle number (unstable at
   0.344, stable at 0.324, the same fates at a hundred thousand and at a million
   particles); the controls' collapses at lower particle number are particle noise
   (floors fall as 1/N). Its fresh verifier is sent when the last two runs (q0057,
   q0058) have been read.
