#!/usr/bin/python3 -I
"""Stage-check rehearsal on a dummy track in a scratch repository (acceptance test 6 of brief 11.7).

    python3 -I harness/tests/test_nrpic_stage.py

Track A of the scratch repository gets a working note (compiled REVTeX PDF), two schematics and
two data figures made by their scripts with the vendored libraries, an analysis table regenerated
by a command listed in stage/G1/VERIFY, and a registered run. Then: collect (criteria of A's sheet
for G1), verify (PASS on a clean export), deliberate faults one at a time (a modified czstyle copy,
a figure without a script, a script changed without regenerating its figure, a table off by more
than the tolerance, an unfinished run) each caught; a hand-written manifest of wave 2 with a problem
fails until EVIDENCE.md names it and is then waived, one of wave 2b is not (decision 0016 item 3);
report (FAIL while items are OPEN, PASS when judged and the verifier's VERIFIER.md exists,
VERIFIER_REPORT.md accepted too: decision 0016 item 1), the tag made as the orchestrator would,
verification of A from the main checkout writing nothing into A's worktree, report refused from
B's worktree; the knowledge base's gates, KB-G2 with the charter's thresholds (0016 item 6).
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
    # the run nrpic-run registered (short id A-2026...), not the hand-written A-emd-pbh-... one: os.listdir
    # order is arbitrary, and picking the hand-written one made this fault a no-op (36/37 once in wave 2)
    rid = next(d for d in sorted(os.listdir(os.path.join(A, "tracks", OWNER, "runs"))) if re.match(r"A-\d{8}-", d))
    mp = os.path.join(A, "tracks", OWNER, "runs", rid, "manifest.json")
    orig_m = open(mp).read()
    git(A, "add", "-f", "--", os.path.relpath(mp, A))
    fault("run left unfinished", lambda: open(mp, "w").write(orig_m.replace('"status": "completed"', '"status": "running"')),
          "runs", lambda: open(mp, "w").write(orig_m))

    # decision 0016 item 3: a hand-written manifest of waves 1 and 2 that EVIDENCE.md names counts as
    # registered and its failures of the manifest check are waived; one of wave 2b is not
    rdir = os.path.join(A, "tracks", OWNER, "runs")
    sdir = os.path.join(A, "tracks", OWNER, "stage", "G1")
    old = "A-20261115-120000-abcdef1"
    os.makedirs(os.path.join(rdir, old))
    json.dump({"run_id": old, "status": "running", "gate": "G1", "output_dir": f"scratch/{OWNER}/{old}",
               "notes": "registered by hand in wave 2; never closed"}, open(os.path.join(rdir, old, "manifest.json"), "w"))
    hs = "A-20261115-120001-abcdef3"           # a helper's registration script copied the schema (D, wave 2)
    os.makedirs(os.path.join(rdir, hs))
    json.dump({"schema": "nrpic-run-manifest/1", "run_id": hs, "track": OWNER, "gate": "G1", "status": "submitted",
               "registered_by": "hand: helper script, because nrpic-run submit refused", "launcher": "local (hand registration)",
               "outputs": {"dir": f"scratch/{OWNER}/{hs}"}}, open(os.path.join(rdir, hs, "manifest.json"), "w"))
    commit_all(A, "A(run): hand-written manifests of wave 2 (one left as running, one copying the schema)")
    r = stage(A, ["verify", OWNER, "G1", "--no-rerun"])
    d = results(A)
    msg = next((x["message"] for x in d["checks"] if x["check"] == "runs"), "")
    c.ok(r.returncode == 1 and status_of(d, "runs") == "FAIL" and "2 of them hand-written in waves 1 and 2" in msg
         and "list them in stage/G1/EVIDENCE.md" in msg and "0016" in msg,
         "hand-written wave-2 manifests with problems (one copying the schema), not in EVIDENCE.md: FAIL, with the hint", msg)
    open(os.path.join(sdir, "EVIDENCE.md"), "w").write(
        "# Evidence\n\n| Artefact | Run |\n|---|---|\n| first look (by hand) | analysis -120000-abcdef1 |\n"
        f"| helper's run | {hs} |\n")
    r = stage(A, ["verify", OWNER, "G1", "--no-rerun"])
    d = results(A)
    wv = next((x for x in d["checks"] if x["check"] == "runs-waived"), None)
    c.ok(r.returncode == 0 and status_of(d, "runs") == "PASS" and wv is not None and wv["status"] == "WARN"
         and old in (wv["detail"] or {}) and "not finished" in json.dumps(wv["detail"])
         and hs in (wv["detail"] or {}) and "not finished" in json.dumps(wv["detail"][hs])
         and "fields missing" not in json.dumps(d),
         "named in EVIDENCE.md (by the -HHMMSS-<commit> suffix, or in full): failures waived and reported (decision 0016),"
         " also for a hand registration that copied the schema", r.stdout)
    new = "A-20261119-090000-abcdef2"
    os.makedirs(os.path.join(rdir, new))
    json.dump({"run_id": new, "status": "running", "gate": "G1", "output_dir": f"scratch/{OWNER}/{new}"},
              open(os.path.join(rdir, new, "manifest.json"), "w"))
    with open(os.path.join(sdir, "EVIDENCE.md"), "a") as f:
        f.write(f"| wave 2b by hand | {new} |\n")
    commit_all(A, "A(run): a hand-written manifest of wave 2b")
    r = stage(A, ["verify", OWNER, "G1", "--no-rerun"])
    d = results(A)
    c.ok(r.returncode == 1 and status_of(d, "runs") == "FAIL" and new in json.dumps(
         next(x for x in d["checks"] if x["check"] == "runs")["detail"]) and old not in json.dumps(
         next(x for x in d["checks"] if x["check"] == "runs")["detail"]),
         "a hand-written manifest of wave 2b is not waived, even when EVIDENCE.md names it", r.stdout)
    drop = [f"tracks/{OWNER}/runs/{x}" for x in (new, old, hs)]
    git(A, "rm", "-q", "-r", "--", *drop)
    git(A, "commit", "-q", "-m", "A(run): drop the three test manifests", "--", *drop)
    os.remove(os.path.join(sdir, "EVIDENCE.md"))
    H = F.H
    c.ok(H.parse_run_id("orch-20261119-101500-abcdef0") == ("orch", "20261119-101500", "abcdef0")
         and H.run_date("A-emd-pbh-20261115-112946-b7b431d") == "20261115" and H.is_wave12("20261118")
         and not H.is_wave12("20261119") and H.run_date("x", {"started": "2026-11-20T01:00:00Z"}) == "20261120",
         "run ids of decision 0016 item 2 (orch included, both forms); wave dates before 2026-11-19")

    # decision 0019 item 6: a run that main's committed coord/WAIVERS.md names has its failures of the
    # manifest check waived (B's run whose outputs were moved after finish); nothing else counts
    # (--package: the EVIDENCE.md removed above is another helper's change, recorded, not refused)
    r = F.sh([os.path.join(A, "harness", "bin", "nrpic-run"), "submit", "--kind", "scouting", "--gate", "G1",
              "--package", f"tracks/{OWNER}/analysis",
              "--purpose", "run whose outputs change after finish", "--", "python3", "-c",
              "import os; open(os.path.join(os.environ['NRPIC_RUN_DIR'], 'out.txt'), 'w').write('data\\n')"],
             cwd=A, check=False)
    mm = re.search(r"registered (\S+):", r.stdout)
    if not c.ok(r.returncode == 0 and mm, "a registered run for the waiver test", r.stdout + r.stderr):
        return c.done()
    wrid = mm.group(1)
    with open(os.path.join(repo, "scratch", OWNER, wrid, "out.txt"), "a") as f:
        f.write("moved here after finish\n")
    r = stage(A, ["verify", OWNER, "G1", "--no-rerun"])
    d = results(A)
    runs_detail = json.dumps(next(x for x in d["checks"] if x["check"] == "runs").get("detail") or {})
    c.ok(r.returncode == 1 and status_of(d, "runs") == "FAIL" and wrid in runs_detail and "out.txt" in runs_detail,
         "a registered run whose output changed after finish fails the manifest check (checksums)", r.stdout)
    wtext = ("# Waivers of the manifest check (decision 0019 item 6)\n\n"
             f"{wrid}  outputs moved into the run directory after the run finished; data unchanged\n")
    open(os.path.join(repo, "coord", "WAIVERS.md"), "w").write(wtext)
    r = stage(A, ["verify", OWNER, "G1", "--no-rerun"])
    c.ok(r.returncode == 1 and status_of(results(A), "runs") == "FAIL",
         "a waiver written on main but not committed does not count", r.stdout)
    git(repo, "add", "--", "coord/WAIVERS.md")
    git(repo, "commit", "-q", "-m", "Waiver of the manifest check", "--", "coord/WAIVERS.md")
    git(A, "merge", "-q", "--no-edit", "main")
    r = stage(A, ["verify", OWNER, "G1", "--no-rerun"])
    d = results(A)
    wv = next((x for x in d["checks"] if x["check"] == "runs-waived"), None)
    c.ok(r.returncode == 0 and status_of(d, "runs") == "PASS" and wv is not None and wv["status"] == "WARN"
         and (wv["detail"] or {}).get(wrid, {}).get("waived_by") == "coord/WAIVERS.md"
         and "outputs moved" in wv["message"] and "0019" in wv["message"]
         and "out.txt" in json.dumps(wv["detail"][wrid]["problems"]),
         "committed on main and merged: the run's failures are waived and reported under runs-waived with the "
         "reason (decision 0019 item 6)", r.stdout)
    pw = H.parse_waivers(
        "# Waivers\n\nProse that names A-20261120-101010-abcdef0 in the middle is no waiver.\n"
        "| Run id | Reason |\n|---|---|\n| `B-20261115-164157-40b9f6d` | outputs moved |\n"
        "- core-20261119-143232-4d1e995: checksum of a link\n"
        "A-emd-pbh-20261115-112946-b7b431d — long form of wave 1\nnot-a-run-id  reason\n"
        "C-20261120-010101-1234567\n")
    c.ok(pw == {"B-20261115-164157-40b9f6d": "outputs moved", "core-20261119-143232-4d1e995": "checksum of a link",
                "A-emd-pbh-20261115-112946-b7b431d": "long form of wave 1", "C-20261120-010101-1234567": "(no reason given)"},
         "WAIVERS.md lines: a run id at the start (plain, list item, table cell, backticks; either form), then the "
         "reason; prose and headers ignored", json.dumps(pw))
    drop = [f"tracks/{OWNER}/runs/{wrid}"]
    git(A, "rm", "-q", "-r", "--", *drop)
    git(A, "commit", "-q", "-m", "A(run): drop the waived test run", "--", *drop)

    # report: FAIL while items are open, PASS when judged
    r = stage(A, ["verify", OWNER, "G1"])
    r = stage(A, ["report", OWNER, "G1"])
    rep = open(os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md")).read()
    c.ok("verdict FAIL" in r.stdout and "checklist items not PASS or NA" in rep and "no VERIFIER.md" in rep,
         "report: FAIL while items are OPEN and the verifier has not reported (VERIFIER.md, decision 0016)", r.stdout)
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
    vpath = os.path.join(A, "tracks", OWNER, "stage", "G1", "VERIFIER.md")
    open(vpath, "w").write("Verdict: PASS\n\n# Verifier report (rehearsal)\n\nAll numbers recomputed; figures opened.\n")
    r = stage(A, ["report", OWNER, "G1", "--decision", "Accept G1 of A-emd-pbh (rehearsal)."])
    rep = open(os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md")).read()
    c.ok("verdict PASS" in r.stdout and "**PASS**" in rep and "Accept G1 of A-emd-pbh" in rep
         and "schem_timeline" in rep and "{{" not in rep, "report: PASS from the template, placeholders filled", r.stdout)
    c.ok("`stage/G1/VERIFIER.md` (verifier's report) | present" in rep and "VERIFIER.md` present; its first lines" in rep
         and "> Verdict: PASS" in rep, "report: VERIFIER.md is the verifier's report (decision 0016 item 1)", rep[:3000])
    os.rename(vpath, os.path.join(os.path.dirname(vpath), "VERIFIER_REPORT.md"))
    r = stage(A, ["report", OWNER, "G1"])
    rep = open(os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md")).read()
    c.ok("verdict PASS" in r.stdout and "`stage/G1/VERIFIER_REPORT.md` (verifier's report) | present" in rep,
         "report: VERIFIER_REPORT.md is accepted too", r.stdout)
    os.rename(os.path.join(os.path.dirname(vpath), "VERIFIER_REPORT.md"), vpath)
    r = stage(A, ["report", OWNER, "G1"])
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
    c.ok("## Thresholds of KB-G2 (coord/CHARTER.md" in ck and "Parse success rate: at least 95 per cent" in ck
         and "Retrieval hit rate: at least 80 per cent" in ck and "top ten" in ck and "not yet in coord/CHARTER.md" not in ck,
         "collect kb KB-G2: the thresholds of the charter's section \"Gates of the knowledge base\" (decision 0016)", ck)
    r = stage(KB, ["collect", "kb", "KB-G1", "--stdout"])
    c.ok(r.returncode == 0 and "Thresholds of" not in r.stdout, "KB-G1 has no thresholds in the charter", r.stdout)
    r = stage(KB, ["collect", "kb", "G4"])
    c.ok(r.returncode == 1 and "KB-G0, KB-G1, KB-G2, KB-G3" in r.stderr, "a gate the knowledge base lacks is refused", r.stderr)
    print("package to look at: " + os.path.join(A, "tracks", OWNER, "stage", "G1", "STAGE_REPORT.md"))
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
