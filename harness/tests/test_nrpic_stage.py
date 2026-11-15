#!/usr/bin/python3 -I
"""Stage-check rehearsal on a dummy track in a scratch repository (acceptance test 6 of brief 11.7).

    python3 -I harness/tests/test_nrpic_stage.py

Track A of the scratch repository gets a working note (compiled REVTeX PDF), two schematics and
two data figures made by their scripts with the vendored libraries, an analysis table regenerated
by a command listed in stage/G1/VERIFY, and a registered run. Then: collect (criteria of A's sheet
for G1), verify (PASS on a clean export), deliberate faults one at a time (a modified czstyle copy,
a figure without a script, a script changed without regenerating its figure, a table off by more
than the tolerance, an unfinished run) each caught, report (FAIL while items are OPEN, PASS when
judged and the verifier report exists), the tag made as the orchestrator would, verification of A
from the main checkout writing nothing into A's worktree, and report refused from B's worktree.
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402

OWNER = "A-emd-pbh"
TABLE_SCRIPT = r'''"""Writes the analysis table of the dummy track (registered in stage/G1/VERIFY)."""
import math, os
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "table.csv"), "w") as f:
    f.write("n,err\n")
    for n in (16, 32, 64):
        f.write(f"{n},{1.0 / n ** 2:.10e}\n")
'''


def stage(wt, args, cwd=None):
    return F.sh([os.path.join(wt, "harness", "bin", "nrpic-stage")] + args, cwd=cwd or wt, check=False, timeout=1800)


def git(wt, *a, check=True):
    return F.sh(["git", "-C", wt] + list(a), check=check)


def commit_all(wt, msg):
    git(wt, "add", "-A", "--", f"tracks/{OWNER}")
    git(wt, "commit", "-q", "-m", msg, "--", f"tracks/{OWNER}")


def results(wt):
    return json.load(open(os.path.join(wt, "tracks", OWNER, "stage", "G1", "VERIFY_RESULTS.json")))


def status_of(doc, check):
    return next((c["status"] for c in doc["checks"] if c["check"] == check), None)


def main():
    fx = F.make_repo("test-stage")
    A, B, repo = fx["wt"][OWNER], fx["wt"]["B-emd-gw"], fx["repo"]
    c = F.Checks(f"nrpic-stage rehearsal (scratch repo {repo})")
    r = F.sh([os.path.join(A, "harness", "bin", "nrpic-env"), "create", "--no-kokkos"], check=False, timeout=900)
    c.ok(r.returncode == 0, "venv of the dummy track", r.stderr[-800:])

    # the package content
    note = F.seed_note(A, OWNER)
    res = F.run_note_scripts(A, OWNER)
    c.ok(all(x.returncode == 0 for x in res.values()), "figure scripts ran (2 data figures, 2 schematics)",
         "\n".join(k + ": " + v.stderr[-400:] for k, v in res.items() if v.returncode))
    r = F.sh(["latexmk", "-pdf", "-interaction=nonstopmode", "-quiet", "main.tex"], cwd=note, check=False, timeout=300)
    c.ok(os.path.isfile(os.path.join(note, "main.pdf")), "working note compiled to main.pdf (REVTeX)", r.stdout[-800:])
    for ext in ("aux", "log", "fls", "fdb_latexmk", "out"):
        p = os.path.join(note, f"main.{ext}")
        if os.path.exists(p):
            os.remove(p)
    an = os.path.join(A, "tracks", OWNER, "analysis")
    open(os.path.join(an, "make_table.py"), "w").write(TABLE_SCRIPT)
    F.sh([os.path.join(A, "harness", "bin", "nrpic-env"), "exec", "--", "python",
          os.path.join(an, "make_table.py")], cwd=A)
    os.makedirs(os.path.join(A, "tracks", OWNER, "stage", "G1"), exist_ok=True)
    # a hand-written manifest of wave 1 (decision 0012): no outputs.dir, status "done", no checksums
    hand = os.path.join(A, "tracks", OWNER, "runs", "A-emd-pbh-20261115-112946-b7b431d")
    os.makedirs(hand, exist_ok=True)
    json.dump({"run_id": "A-emd-pbh-20261115-112946-b7b431d", "status": "done", "gate": "G0",
               "output_dir": "scratch/A-emd-pbh/A-emd-pbh-20261115-112946-b7b431d", "command": ["x"]},
              open(os.path.join(hand, "manifest.json"), "w"))
    open(os.path.join(A, "tracks", OWNER, "stage", "G1", "VERIFY"), "w").write(
        "# commands re-run on the clean export (cwd: its root)\n"
        f"python tracks/{OWNER}/analysis/make_table.py\n")
    commit_all(A, "A(note): dummy package content")
    r = F.sh([os.path.join(A, "harness", "bin", "nrpic-run"), "submit", "--kind", "scouting", "--gate", "G1",
              "--purpose", "dummy analysis run", "--", "python3", "-c", "print('ok')"], cwd=A, check=False)
    c.ok(r.returncode == 0, "a registered run in the package", r.stderr)

    # collect
    r = stage(A, ["collect", OWNER, "G1"])
    ck = open(os.path.join(A, "tracks", OWNER, "stage", "G1", "CHECKLIST.md")).read()
    c.ok(r.returncode == 0 and "constraint residuals of A-pre-1 converge" in ck and "Pre-core baseline" in ck
         and "Updated architecture" in ck, "collect: G1 rows of charter 9.2, A's sheet and brief 13.4", r.stdout + r.stderr)
    nitems = len(re.findall(r"\*\*C\d+\*\*", ck))
    c.ok(nitems >= 10 and ck.count("status: OPEN") == nitems, f"collect: {nitems} items, all OPEN")

    # verify, clean
    r = stage(A, ["verify", OWNER, "G1"])
    doc = results(A)
    c.ok(r.returncode == 0 and doc["result"] == "PASS", "verify passes on the clean export", r.stdout + r.stderr)
    for chk in ("clean", "sync", "style", "fig-script", "runs", "rerun", "compare", "regenerate", "note-pdf"):
        c.ok(status_of(doc, chk) == "PASS", f"verify check {chk}: PASS", r.stdout)
    c.ok(status_of(doc, "run-notes") == "WARN" and "hand-written" in next(
         x["message"] for x in doc["checks"] if x["check"] == "runs"),
         "a hand-written manifest of wave 1 (status 'done', no checksums) is read, not failed (decision 0012)", r.stdout)
    c.ok(status_of(doc, "package") == "WARN" and "EVIDENCE.md" in r.stdout,
         "verify notes the package documents of decision 0012 that are missing", r.stdout)
    c.ok(F.sh(["git", "-C", A, "status", "--porcelain", "--", f"tracks/{OWNER}/note"]).stdout == "",
         "verify wrote nothing into the note of the worktree")

    def fault(label, mutate, check, undo):
        mutate()
        commit_all(A, f"A(test): fault {label}")
        rr = stage(A, ["verify", OWNER, "G1"])
        d = results(A)
        c.ok(rr.returncode == 1 and status_of(d, check) == "FAIL", f"fault caught: {label} -> {check} FAIL", rr.stdout)
        undo()
        commit_all(A, f"A(test): undo {label}")

    scripts = os.path.join(note, "scripts")
    czs = os.path.join(scripts, "czstyle.py")
    orig = open(czs).read()
    fault("czstyle.py copy modified", lambda: open(czs, "a").write("# local tweak\n"), "style",
          lambda: open(czs, "w").write(orig))
    orphan = os.path.join(note, "figures", "fig_orphan.png")
    fault("figure without a script", lambda: shutil.copyfile(os.path.join(note, "figures", "fig_style_lines.png"), orphan),
          "fig-script", lambda: os.remove(orphan))
    fl = os.path.join(scripts, "fig_style_lines.py")
    orig_fl = open(fl).read()
    fault("script changed, figure not regenerated",
          lambda: open(fl, "w").write(orig_fl.replace('PAL["red"], label="NRPIC"', 'PAL["green"], label="NRPIC"')),
          "compare", lambda: open(fl, "w").write(orig_fl))
    tab = os.path.join(an, "table.csv")
    orig_tab = open(tab).read()
    fault("table off by 1e-3 relative", lambda: open(tab, "w").write(orig_tab.replace("3.9062500000e-03", "3.9101562500e-03")),
          "compare", lambda: open(tab, "w").write(orig_tab))
    open(tab, "w").write(orig_tab.replace("3.9062500000e-03", "3.9062500001e-03"))
    commit_all(A, "A(test): table within tolerance")
    r = stage(A, ["verify", OWNER, "G1"])
    c.ok(r.returncode == 0 and status_of(results(A), "compare") == "PASS",
         "a table differing by 3e-11 relative passes (rtol 1e-6)", r.stdout)
    rid = next(d for d in os.listdir(os.path.join(A, "tracks", OWNER, "runs")) if d.startswith("A-"))
    mp = os.path.join(A, "tracks", OWNER, "runs", rid, "manifest.json")
    orig_m = open(mp).read()
    git(A, "add", "-f", "--", os.path.relpath(mp, A))
    fault("run left unfinished", lambda: open(mp, "w").write(orig_m.replace('"status": "completed"', '"status": "running"')),
          "runs", lambda: open(mp, "w").write(orig_m))

    # report: FAIL while items are open, PASS when judged
    r = stage(A, ["verify", OWNER, "G1"])
    r = stage(A, ["report", OWNER, "G1"])
    rep = open(os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md")).read()
    c.ok("verdict FAIL" in r.stdout and "checklist items not PASS or NA" in rep and "VERIFIER_REPORT" in rep,
         "report: FAIL while items are OPEN and the verifier has not reported", r.stdout)
    c.ok("no stage/G1/EVIDENCE.md (decision 0012)" in rep and "## Package documents" in rep
         and "REPORT.md" not in os.listdir(os.path.join(A, "tracks", OWNER, "stage", "G1")),
         "report: the package documents of decision 0012 listed, EVIDENCE.md and OPEN.md required, no REPORT.md", rep[:1500])
    sdir = os.path.join(A, "tracks", OWNER, "stage", "G1")
    open(os.path.join(sdir, "EVIDENCE.md"), "w").write("# Evidence\n\nrun ids and figures\n")
    open(os.path.join(sdir, "OPEN.md"), "w").write("# Open\n\nnothing\n")
    open(os.path.join(sdir, "SCOPE.md"), "w").write("# Scope\n")
    with open(os.path.join(sdir, "STAGE_REPORT.md"), "a") as f:
        f.write("\n## Notes of the lead\n\nWritten by hand; must survive a rerun.\n")
    ckp = os.path.join(A, "tracks", OWNER, "stage", "G1", "CHECKLIST.md")
    text = open(ckp).read().replace("status: OPEN", "status: PASS").replace("evidence: \n", f"evidence: run {rid}\n")
    open(ckp, "w").write(text)
    open(os.path.join(A, "tracks", OWNER, "stage", "G1", "VERIFIER_REPORT.md"), "w").write(
        "# Verifier report (rehearsal)\n\nAll numbers recomputed; figures opened.\n")
    r = stage(A, ["report", OWNER, "G1", "--decision", "Accept G1 of A-emd-pbh (rehearsal)."])
    rep = open(os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md")).read()
    c.ok("verdict PASS" in r.stdout and "**PASS**" in rep and "Accept G1 of A-emd-pbh" in rep
         and "schem_timeline" in rep and "{{" not in rep, "report: PASS from the template, placeholders filled", r.stdout)
    c.ok("## Notes of the lead" in rep and "must survive a rerun" in rep and "`stage/G1/SCOPE.md`" in rep,
         "report keeps a section written by hand and names the scoping text", rep[-1500:])
    r = stage(A, ["report", OWNER, "G1"])
    rep = open(os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md")).read()
    c.ok("Accept G1 of A-emd-pbh" in rep and rep.count("## Notes of the lead") == 1,
         "report run again keeps the decision text and the hand-written section once", r.stdout)
    r2 = stage(A, ["collect", OWNER, "G1"])
    c.ok("status: PASS" in open(ckp).read() and "kept from the previous version" in r2.stdout,
         "collect again keeps the judged statuses", r2.stdout)
    commit_all(A, "A(note): stage G1 package")
    tag = re.search(r"proposed tag (\S+)", r.stdout).group(1)
    git(A, "tag", "-a", tag, "-F", os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md"))
    c.ok(git(A, "tag", "--list", "stage/A-emd-pbh/G1-pass-*").stdout.strip() == tag,
         f"tag {tag} created as the orchestrator would")

    # the orchestrator verifies A from main; B may not write A's report
    before = F.sh(["git", "-C", A, "status", "--porcelain"]).stdout
    r = stage(repo, ["verify", OWNER, "G1", "--no-rerun"], cwd=repo)
    c.ok("VERIFY_RESULTS.md" in r.stdout and "scratch/orch/tmp/stage-verify" in r.stdout
         and F.sh(["git", "-C", A, "status", "--porcelain"]).stdout == before,
         "verify of A from the main checkout writes only under scratch/orch/", r.stdout + r.stderr)
    r = stage(B, ["report", OWNER, "G1"])
    c.ok(r.returncode == 1 and "own track" in r.stderr, "report for A refused in B's worktree", r.stderr)

    # the knowledge base: its own gates (brief 12.10), collect read-only with --stdout
    KB = fx["wt"]["kb"]
    r = stage(KB, ["collect", "kb", "G1", "--stdout"])
    c.ok(r.returncode == 0 and "Checklist: kb KB-G1" in r.stdout and "The inventory report" in r.stdout
         and "All priority-3 papers ingested" in r.stdout and "Code index and parameter index of AthenaK" in r.stdout
         and "The answers to the first questions" in r.stdout and "kb snapshot" in r.stdout
         and "Pre-core baseline" not in r.stdout and not os.path.exists(os.path.join(KB, "tracks", "kb", "stage", "KB-G1")),
         "collect kb G1 --stdout: the four KB-G1 criteria of brief 12.10 and the snapshot rule; nothing written",
         r.stdout + r.stderr)
    r = stage(KB, ["collect", "kb", "KB-G2"])
    ck = open(os.path.join(KB, "tracks", "kb", "stage", "KB-G2", "CHECKLIST.md")).read()
    c.ok(r.returncode == 0 and "All papers and repositories ingested" in ck and "QA report" in ck,
         "collect kb KB-G2 writes tracks/kb/stage/KB-G2/CHECKLIST.md", r.stdout + r.stderr)
    r = stage(KB, ["collect", "kb", "G4"])
    c.ok(r.returncode == 1 and "KB-G0, KB-G1, KB-G2, KB-G3" in r.stderr, "a gate the knowledge base lacks is refused", r.stderr)
    print("package to look at: " + os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md"))
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
