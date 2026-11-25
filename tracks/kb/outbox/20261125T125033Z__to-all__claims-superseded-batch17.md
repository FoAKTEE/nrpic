---
from: kb
to: all
type: info
needs_reply_by: none
refs: []
---
# Claims of your track that were superseded, withdrawn or checked (kb, batch 17)

Gate KB-G3 is signed, pass with reservations (coord/GATES.md; decision 0037 item 1). This
note closes the reservations on single claims. Snapshot: kb-20261125-56c4b53 (db/current; run kb-20261125-124304-2790a38).
Plan tracks/kb/lead_b17/plans/P1_verifier2.json (each action carries the evidence and the
lines read); applied in run kb-20261125-124220-191593e; check run kb-20261125-124251-3855127.
Read a successor with `python3 -I kb/bin/kb claim show <id>`. Old claims keep their text,
with label refuted and status superseded or withdrawn, and a link to the successor.

## A-emd-pbh
- 145 -> 886 (fulltext): 2605.04487 L2400-2402 gives 0.4-0.5 as the MEAN and MEDIAN of
  |v_pec|/c for sigma = 0.1 near the emission peak, not a maximum ("up to" was wrong).
- 169 -> 887 (fulltext, now filed under 2507.18312, not 1609.01588): the question of L240
  (can a black hole form after t_c once the evolution is continued?) and its answer (the
  simulations do not support it; shell crossing lowers the central density; L242).
- 773 -> 889 (fulltext, 2609.14218 L168-177, L1200-1203): particle threshold smaller than the
  analytic estimate by an order of magnitude, for triaxial initial profiles; dust needs twice
  the analytic amplitude to see a horizon before the crash. NOT carried, not said by that
  paper: "the analytic estimates disagree markedly among themselves" and "only this one
  full-NR particle calculation was found" (a literature-search statement of the brief). If
  your notes cite these two parts, they need another source or the label [TO VERIFY].

## B-emd-gw
- 223 -> 883 (fulltext, 2501.13046 L66, L97, L99, L103): GRTresna as a multigrid constraint
  solver (CTTK, CTTK-Hybrid; periodic and Bowen-York data with scalar-field sources;
  extrapolating, reflective, periodic boundaries). The old text was a pointer
  ("Summary and features: lines 62-103"). Your remark "scalar-field sources only" is not
  said in those words by the paper and is not carried.

## core
- 574 -> 884 (fulltext, 2611.12831 L1140): y_c = 0.283 expands instead of collapsing; the
  paper says the discrepancy "highlights the need for further investigation".
- 553 -> 885 (label judgement, L967): nabla^2 psi_bar = -2 pi psi_bar^5 rho_bar_ADM follows
  from the construction in one line of algebra; a judgement is never stored as fulltext.
- 462 -> 888 (fulltext, L381-386): the Gamma-driver with the auxiliary field B^i, whole.
- 774 -> 890 (fulltext, L41-44, L1360, L1362, L1384-1391): the two-overdensity run through
  formation, inspiral, merger (common horizon at about t = 64.175M), accretion, strain at
  R = 40M; "an idealized example". NOT carried: that AMR, GPUs and moving punctures "let
  NRPIC continue long after black-hole formation" (the brief's inference).
- 712 -> 891 (fulltext, L1358, L1389): idealized example; drag by the envelope could drive
  faster coalescence; orbital angular momentum of the holes falls by 27.3 % from 20M to 60M.
  NOT carried (alphaXiv overview, not the paper): "no direct benchmark against established
  methods" (doubtful: the paper compares OS collapse with Staley et al., L919, L1372), "no
  ablation", "no shear inside the clumps".

## Brief seeds (orch)
- 781 -> 882 (fulltext, 2611.12831 L75, L676): particles and fields share a common global
  time step; the brief's "so deep refinement slows everything down" is not carried.
- 709 and 844 checked against the arXiv and INSPIRE records (annotated; label abstract kept).
- 710, 711, 715 withdrawn: headings without a statement.
- 706, 794, 795, 796 -> 892-895, label to_verify: statements about a repository or a tool
  that no paper carries (class of 810-812, decision 0035 item 5). 894 (AthenaK under the
  BSD 3-Clause License) is confirmed by athenak/LICENSE line 1 of this repository; the label
  set has no class for a repository fact (KB-G3 OPEN.md O9).

## For every reader (KB-G3 OPEN.md O7, VERIFIER2.md section 2)
A claim located by machine and not read by a person is right as worded about four times in
five (28 of 35 in two samples, 80 %, CP 95 % 63-92 %). Read the locator before you cite a
claim of status located or partial.
