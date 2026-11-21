#!/bin/bash
# Close and analyse the card runs of the g2runs package once their chains are DONE.
# Usage (from anywhere): finish_g2.sh es1gb | esf
#   es1gb: nrpic-run finish of ES-1GB, then compare_horizons.py (ES-1G, ES-1GB, V-1B, V-1GB)
#          and slicemass.py on its restart dumps (B1, B3, B4', B5 of JOURNAL entries 1, 4)
#   esf:   nrpic-run finish of ES-F, then flux_tools/esf_analyse.py (criteria i, ii) and
#          tools/esf_criteria.py (iii, D1-D4, P1/P2/P5/P6) with V-1 as the control
#          (flux_tools/JOURNAL.md entry 7)
# Each analysis is a registered local run on one core; the figures are to be looked at
# and the outcomes written into g2runs/JOURNAL.md by the session that runs this.
set -eu
WT=/data/haiyangw/nrpic/wt/D-bh-dress
S=/data/haiyangw/nrpic/scratch/D-bh-dress
RUN=$WT/harness/bin/nrpic-run
PKG=tracks/D-bh-dress/g2runs
cd "$WT"
case "${1:-}" in
  es1gb)
    ID=D-20261121-125900-ea4c442
    st=$(cat "$S/$ID/chain/STATUS")
    [ "$st" = DONE ] || { echo "ES-1GB chain status: $st (not DONE)"; exit 2; }
    "$RUN" finish "$ID"
    "$RUN" submit --kind scouting --gate G2 --launcher local --cores 1 --package "$PKG" \
      --purpose "ES-1GB complete: compare_horizons.py on ES-1G, ES-1GB, V-1B, V-1GB (B1-B3, C2); g2runs JOURNAL entry 1" \
      -- python3 $PKG/tools/compare_horizons.py --out '$NRPIC_RUN_DIR' \
      ES-1G=$S/D-20261119-142633-6f72922:es ES-1GB=$S/$ID:es1gb \
      V-1B=$S/D-20261120-222625-63abd72:v1b V-1GB=$S/D-20261121-125909-06f856e:v1gb
    "$RUN" submit --kind scouting --gate G2 --launcher local --cores 2 --package "$PKG" \
      --purpose "B4' slice mass of ES-1GB on all restart dumps (to 200 M); g2runs JOURNAL entry 4" \
      -- python3 analysis/diag/slicemass.py ES-1GB=$S/$ID --base es1gb --out '$NRPIC_RUN_DIR/slicemass_ES-1GB'
    ;;
  esf)
    ID=D-20261121-144631-aa7ce9b
    st=$(cat "$S/$ID/chain/STATUS")
    [ "$st" = DONE ] || { echo "ES-F chain status: $st (not DONE)"; exit 2; }
    "$RUN" finish "$ID"
    DATA=$S/D-20261119-145022-2208a19
    CTRL=$S/D-20261115-172730-c6d151b/v1.horizon_summary_0.txt
    "$RUN" submit --kind scouting --gate G2 --launcher local --cores 1 --package "$PKG" \
      --purpose "ES-F: esf_analyse.py (criteria i, ii; flux_tools entry 7) with V-1 as the control" \
      -- python3 tracks/D-bh-dress/flux_tools/esf_analyse.py --run $S/$ID --data $DATA \
      --control $CTRL --out '$NRPIC_RUN_DIR'
    "$RUN" submit --kind scouting --gate G2 --launcher local --cores 1 --package "$PKG" \
      --purpose "ES-F: esf_criteria.py (iii, D1-D4, P1/P2/P5/P6 of flux_tools entry 7) with V-1 as the control" \
      -- python3 $PKG/tools/esf_criteria.py --run $S/$ID --data $DATA --control $CTRL \
      --out '$NRPIC_RUN_DIR'
    ;;
  *)
    echo "usage: $0 es1gb|esf"; exit 1 ;;
esac
