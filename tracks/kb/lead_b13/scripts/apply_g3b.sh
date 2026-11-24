#!/bin/bash
# kb lead batch 13, step 2: open brief to_verify seeds with no processing event that the store
# answers (716, 798, 799 from the KB-G1 first answers; 808 in part from ingest4's INSPIRE records).
cd /data/haiyangw/nrpic/wt/kb || exit 2
test -n "${NRPIC_RUN_DIR:-}" || { echo 'not inside nrpic-run'; exit 2; }
cat > "$NRPIC_RUN_DIR/annotate.tsv" <<'EOT'
716	processed: answered item by item in tracks/kb/stage/KB-G1/FIRST_QUESTIONS.md (KB-G1, signed): deposition first order, B1 cloud in cell (2611.12831v1 main.tex L637-663); filtered, binomial (1/4,1/2,1/4) per direction on the ten ADM sources (L680-686), number of passes not stated; Z4c damping kappa_1, kappa_2 with a kappa_1 profile for collapse (L238-248, L388-397); particle data satisfy the Hamiltonian constraint by construction of the conformally flat time-symmetric slices, no solve with deposited sources (L888-905, L1119-1129); no performance numbers (searched); no code-availability statement (L1395-1399); common global time step (L75, claim 781); follow-up directions L1393. The label stays to_verify because the seed is a list of questions, two of which the paper leaves open (filter passes, c_H).
798	processed: the same questions as 716, answered in tracks/kb/stage/KB-G1/FIRST_QUESTIONS.md sections 1-5 with locators in 2611.12831v1 main.tex (see the annotation of 716); open in the paper itself: the number of filter passes and the value of c_H (only the authors can answer).
799	processed: 2611.12831v1 has no code- or data-availability statement (KB-G1 FIRST_QUESTIONS.md section 4, acknowledgements L1395-1399; no repository address in the paper, kb/reports/code_links_explicit.tsv). Decision D2 and the weekly upstream check are program items, not literature (kb watch upstream).
808	processed in part (kb package ingest4, run kb-20261124-132936-4784ebb): INSPIRE records without e-print found and recorded for Bertschinger 1985 (ApJS 58, 39), Einstein and Straus 1945 (RMP 17, 120) and 1946 (RMP 18, 148); the other classic references of the list (Shapiro-Teukolsky 1985-1992, Choptuik 1993, Burnett 1989, Zel'dovich 1970, Esirkepov 2001, Villasenor-Buneman 1992, Boris 1970, Kandrup-Morrison 1993, Hills 1988, Starobinsky 1986) are not yet looked up.
EOT
python3 -I tracks/kb/lead_b13/scripts/annotate.py annotate "$NRPIC_RUN_DIR/annotate.tsv"
