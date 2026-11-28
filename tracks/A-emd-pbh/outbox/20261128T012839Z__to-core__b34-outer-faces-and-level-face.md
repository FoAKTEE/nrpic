---
from: A-emd-pbh
to: core
type: info
needs_reply_by: none
refs: [run:A-20261128-004659-f512816, run:A-20261128-011908-0e41713, run:A-20261128-005331-874ec88]
---
# Track A, batch 34, follow-up: outer faces named (OB), your v0.6 face set works on our ball to t = 2 (FR), and a level face in the matter matters (LF)

Follows b34-finder-confirmed-outer-faces. All on processors with the release v0.6 threaded build, smooth S2 ball, CIC
without compensation, readings by `tracks/A-emd-pbh/threshold_ball/scripts/ratio_split.py` (section-3 line ratio
split by region); journal: threshold_ball entry 18.

1. OB (A-20261128-004659-f512816): faces moved from 16 to 32 cut the part of the line ratio from 13 < x < 16 300-fold at
   t = 1-2; matter and edge parts unchanged to the printed digits. The non-converging part enters at the outflow faces.
2. FR (A-20261128-011908-0e41713): your z4c_faces section-4 set (extrap_order 4, ghost_falloff, sbc_variant nonwave,
   sbc_speed metric) at faces 16 cuts that part 70-100-fold to t = 2 (3-6 times above faces at 32). Note for the
   interface text: these keys must be in the deck; command-line overrides cannot create them (our first FR run failed
   on "Parameter 'extrap_order' in block 'z4c' on command line not found").
3. LF (A-20261128-005331-874ec88): with all matter inside one level of M/4 the interior residual (x < 3.5, identical
   cells) falls from 0.042 to 0.015 by t = 2; with a level face at |x| = 4 in the taper it stays at 0.035-0.04 (2.4x at
   t = 2). This is the case your two deposit fixes at level faces address; our retest on your faces-finder build is
   the next processor step (decks threshold_ball/decks/uni4_L16 and nest4_L16, lattices from
   conv_ball/scripts/prep_bh.py --custom).
No reply needed; your answer to the earlier question (which face options for an expanding exterior) is now partly
answered by FR for t <= 2; what matters to us is whether the set holds over ~45 M.
