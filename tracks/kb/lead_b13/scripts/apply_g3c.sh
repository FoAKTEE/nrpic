#!/bin/bash
# kb lead batch 13, step 3: the verifier's findings on 85 (fragment) and 737 (correction, not refutation).
cd /data/haiyangw/nrpic/wt/kb || exit 2
test -n "${NRPIC_RUN_DIR:-}" || { echo 'not inside nrpic-run'; exit 2; }
cat > "$NRPIC_RUN_DIR/annotate.tsv" <<'EOT'
85	fragment (verifier KB-G3 item 1b, and claims_tracks/AUDIT.md): the stored text "and L550-563" carries no statement; the locator is right but the claim must be re-seeded from A's note with the sentence it belongs to. Do not cite 85 as it stands.
737	correction, not refutation (verifier KB-G3 item 2): 2606.02712 L205, L559, L798 give z0 = -0.4 (+0.8/-0.9) per cent, compatible with zero as the brief says and also with the void value 0.84 per cent; the brief's sentence is incomplete and misleading, not false. Read the label "refuted" of 737 as "corrected: incomplete".
EOT
python3 -I tracks/kb/lead_b13/scripts/annotate.py annotate "$NRPIC_RUN_DIR/annotate.tsv"
