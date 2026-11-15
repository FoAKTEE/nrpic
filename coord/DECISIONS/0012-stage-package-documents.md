# 0012 Documents of a stage package

Status: ACCEPTED · 2026-11-15 · orchestrator

The agent sessions of this program cannot create a file named `REPORT.md` (their tool
guard keeps report files for the session's reply). A stage package under
`tracks/<ID>/stage/G<k>/` therefore consists of: `STAGE_REPORT.md` (the template of the
harness; the scoping text may live in `SCOPE.md` or `SCOPING.md` beside it or in the
package's scope directory and is then named in the report), `EVIDENCE.md`, `OPEN.md`,
`CHECKLIST.md`, and `REVIEW.md` where the lead rechecked helpers. No `REPORT.md` is
required; one written through the shell in wave 1 is accepted as it is. Run ids follow
`nrpic-run` (`<owner id>-<YYYYMMDD-HHMMSS>-<commit7>`, UTC); the harness reads the
hand-written manifests of wave 1 as well.
