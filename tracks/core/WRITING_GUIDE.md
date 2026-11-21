# Writing guide: working note of core (the shared Einstein-Vlasov particle-in-cell implementation)

The per-paper layer of the paper-writing principles (Sec. 0) for core's REVTeX working
note `note/main.tex`. This file and `NOTATION.md` sit one level above the manuscript
directory `note/` (7.1). Started 2026-11-21 (batch 8, session core-lead-8) for gate G2.

## Journal and tone (2.8)

- Format: Physical Review D style, REVTeX 4.2 (`aps,prd,twocolumn`). The note is core's
  verification report for gate G2 and the seed of a methods paper.
- Where the methods go: the implementation and the tests are the subject, so they are in
  the main text; every number goes to the ledger appendix (Supplemental Material).
- Tone: letter-like concision, American English, no hype.

## Two exceptions for the working note (program rules over 4.1 and 5.5)

1. Program rule 4 (CLAUDE.md): a number enters a note only with a run id. The ledger
   appendix lists every number with the registered run that produced it or the source
   locator it was read from, and the claim of the fresh verifier that recomputed it.
   Run ids, locators and file names appear in the ledger appendix and in the scripts
   only; the main text and the captions follow 4.1 and 5.5. The checker's 5.5 and 5.8
   hits in the ledger appendix and in `note/scripts/` are accepted under this exception.
2. Release names (core-v0.3 to core-v0.6) are the program's unit of delivery and are what
   the tracks cite; they appear in the release section and in the architecture
   schematic. The checker's 5.7 hits on "version", "defect" and "fix" in the section on
   known limits are accepted: that section is about this code's own open items, which is
   what a verification report must state.
3. Evidence labels of the program stay out of the typeset text; the text says in words
   what is established, what is a judgement, and what is open.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Track leads of the program | which capability exists in which release, how it was tested, what it does not do |
| Numerical relativists | particle-in-cell coupling to a 3+1 evolution: push, deposit, sources of Z4c |
| Kinetic-theory and N-body readers | Einstein-Vlasov steady states, horizon mass as a check, cloud deposition |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; The shared implementation; The verification ladder; Known limits; Summary; appendix: ledger |
| Subsection of the implementation | release | base; core-v0.3; core-v0.4; core-v0.5 and core-v0.6 |
| Subsection of the ladder | the rows of the brief's section 10 marked CORE | geodesics; Oppenheimer-Snyder; oblate and prolate; steady states and threshold; supporting checks |

## Story (Sec. 10, steps 1-3)

Question: can every track build on the shared implementation, and what is still missing
for the gate? Turning points: the base reproduces the source paper's geodesic and dust
collapse tests on the released executables; four releases added what the tracks asked
for, each with its own tests; a fresh verifier recomputed a sample from raw outputs and
found the numbers right but five texts and one general statement wrong; two rows of the
ladder are still partial. The picture to leave with: the ladder schematic, two rows
green, two half-green, with the specific missing pieces named.

The 300-word version is in the session journal
(`tracks/core/JOURNAL.md`, batch 8); the longer version was written as the main text along the outline. Step 4 (reviewers as parallel subagents) was not
run: this session has no tool to start subagents; the fresh verifier's report on the
same claims stands in for an outside reading of the evidence, not of the prose.

## Allowed numbers (4.1)

- Structural integers: four ladder rows, five cluster models, two pushers, two
  resolutions, four releases, six tracks.
- Labels: release names core-v0.1 to core-v0.6 (exception 2); y_c values that label the
  cluster models (0.900, 0.819, 0.605, 0.500, 0.283) and the bisection members.
- Figure parameters in captions: a = 0.9 M, e = 0.99, the cell sizes M/4, M/8, M/16.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| apparent horizon | AH (in prose) | numerical relativity |
| central lapse | central alpha | numerical relativity |
| turning point of the binding energy | stability point | relativistic star clusters |
| cloud deposition | particle painting | particle-in-cell |
| card | GPU (in prose about this machine: nowhere in the note) | program |

## Project names (5.8)

Passed to the checker as `--forbid`: `NRPIC|nrpic|wt/core|scratch|Track [A-F]|batch [0-9]`.
The release names are exception 2.

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| schem_architecture | what exists per release and what is open; the gates | state 2026-11-21 |
| fig_geodesic | both pushers conserve E, L_z, Q to the paper's level; second order | a = 0.9 M, e = 0.99 |
| fig_collapse | horizon mass of the dust ball within the paper's band at formation, slightly outside late; prolate horizon at the paper's time with a mass deficit falling with resolution | lattice of 9328 particles; M/8, M/16 |
| fig_clusters | the fates of the five models; the M/4 bisection does not collapse | 10^4 particles; M/4 |
