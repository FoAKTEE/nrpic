# Stage report: {{ID}} {{GATE}}

Date: {{DATE}} · branch `{{BRANCH}}` at `<commit>` · checklist
`tracks/{{ID}}/stage/{{GATE}}/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

PASS | FAIL. Tag: `stage/{{ID}}/{{GATE}}-pass-YYYYMMDD` (or `-fail-`).

## Package documents (decision 0012)

STAGE_REPORT.md (this file), EVIDENCE.md, OPEN.md, CHECKLIST.md; REVIEW.md where the lead
rechecked helpers; the scoping text (SCOPE.md or SCOPING.md, or the scope directory). No
REPORT.md is needed. Sections that `nrpic-stage report` does not generate are kept when it
runs again; so is the text of "Decision requested".

## Criteria (coord/CHARTER.md, gate {{GATE}} of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| 1 | | | PASS / FAIL / OPEN |

## Re-verification on a clean checkout (`nrpic-stage verify`)

What was re-run, where, and whether the regenerated tables and figures agree with the
committed ones (tolerance stated).

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|

## Verifier report

`tracks/{{ID}}/stage/{{GATE}}/VERIFIER.md` (decision 0016; VERIFIER_REPORT.md accepted too):
numbers recomputed, figures opened, sentences without support.

## Null results and failed runs

## Open risks

## Decision requested from the group

One paragraph: accept {{GATE}} of {{ID}}, or what is missing.
