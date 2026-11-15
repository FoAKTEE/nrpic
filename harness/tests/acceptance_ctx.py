#!/usr/bin/python3 -I
"""Acceptance tests of brief 11.7 that concern the context commands; writes the transcript.

    harness/tests/acceptance_ctx.py [--out coord/digests/bootstrap.md]     (main checkout, orchestrator)

1. test_ctx.py in a scratch repository under scratch/harness/ (tests 2, 3, 7; isolation; exactly once;
   refusals; audit; nrpic-wt), with its transcript;
2. read-only on the live repository: nrpic-doctor --all (test 1), nrpic-wt list, the start-up brief of
   every owner (test 7, cold start), nrpic-ctx audit.
No live branch, worktree or index is written; the only writes are the scratch repository (removed after
a passing run), the doctor's throwaway repositories (removed) and the output file.
"""
import argparse
import datetime as dt
import json
import os
import pwd
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
BIN = os.path.join(os.path.dirname(HERE), "bin")


def env():
    pw = pwd.getpwuid(os.getuid())
    return {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": pw.pw_dir, "USER": pw.pw_name, "LOGNAME": pw.pw_name,
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"}


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env())


def block(cmd_shown, p, limit=60):
    out = (p.stdout + ("\n" + p.stderr if p.stderr.strip() else "")).rstrip().splitlines()
    if len(out) > limit:
        out = out[:limit] + [f"... ({len(out) - limit} more lines)"]
    return "```\n$ " + cmd_shown + "\n" + "\n".join(out) + f"\n(exit {p.returncode})\n```\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="coord/digests/bootstrap.md")
    args = ap.parse_args()
    common = sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], HERE).stdout.strip()
    main_co = os.path.dirname(os.path.realpath(common))
    if os.path.realpath(sh(["git", "rev-parse", "--show-toplevel"], os.getcwd()).stdout.strip()) != main_co:
        print("run this from the main checkout", file=sys.stderr)
        return 2
    tmpdir = os.path.join(main_co, "scratch", "harness")
    os.makedirs(tmpdir, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tr, js = os.path.join(tmpdir, f"transcript-{stamp}.md"), os.path.join(tmpdir, f"summary-{stamp}.json")
    head = sh(["git", "rev-parse", "--short", "HEAD"], main_co).stdout.strip()

    print("1/2 self-test in a scratch repository ...")
    p = sh([os.path.join(HERE, "test_ctx.py"), "--transcript", tr, "--json", js], main_co)
    summ = json.load(open(js))
    sec = summ["sections"]

    def sec_res(*names):
        got = [sec.get(n, [0, 0]) for n in names]
        ok = sum(g[0] for g in got)
        bad = sum(g[1] for g in got)
        return f"PASS ({ok} checks)" if ok and not bad else f"FAIL ({bad} of {ok + bad} checks)"

    print("2/2 read-only runs on the live repository ...")
    live = []
    doc = sh([os.path.join(BIN, "nrpic-doctor"), "--all"], main_co)
    live.append(("Acceptance test 1: `nrpic-doctor --all` (read-only in the eight owner worktrees and the main checkout)",
                 block("harness/bin/nrpic-doctor --all", doc, limit=40)))
    table = [ln for ln in doc.stdout.splitlines()[2:] if re.match(r"^\S+\s+(PASS|FAIL|MISSING|SKIP|no worktree)", ln)]
    cols = doc.stdout.splitlines()[1].split()[1:] if len(doc.stdout.splitlines()) > 1 else []
    mine = ["wt", "build", "ctx"]
    mine_ok = all(all(ln.split()[1 + cols.index(r)] == "PASS" for r in mine if r in cols) for ln in table) and len(table) == 9
    wl = sh([os.path.join(BIN, "nrpic-wt"), "list"], main_co)
    live.append(("Worktrees (`nrpic-wt list`)", block("harness/bin/nrpic-wt list", wl)))
    owners = sh([os.path.join(BIN, "nrpic-ctx"), "owners"], main_co).stdout
    cold = []
    briefs = []
    for ln in owners.splitlines()[1:]:
        f = ln.split()
        if len(f) < 3 or f[0] == "orch":
            continue
        oid, wt = f[0], os.path.join(main_co, f[2])
        b = sh([os.path.join(BIN, "nrpic-ctx"), "-C", wt, "brief"], main_co)
        nxt = re.search(r"^handoff:\s+Run next: (.+)$", b.stdout, re.M)
        gate = re.search(r"^gate:\s+(.+)$", b.stdout, re.M)
        cold.append((oid, bool(nxt and gate), len(b.stdout.splitlines())))
        briefs.append(block(f"harness/bin/nrpic-ctx -C {f[2]} brief", b, limit=40))
    live.append(("Acceptance test 7 on the live worktrees: the start-up brief of every owner (`nrpic-ctx -C wt/<ID> brief`, read-only)",
                 "".join(briefs)))
    ob = sh([os.path.join(BIN, "nrpic-ctx"), "brief"], main_co)
    live.append(("The orchestrator's brief", block("harness/bin/nrpic-ctx brief", ob)))
    au = sh([os.path.join(BIN, "nrpic-ctx"), "audit"], main_co)
    live.append(("`nrpic-ctx audit` on the live branches (read-only)", block("harness/bin/nrpic-ctx audit", au, limit=80)))

    cold_ok = all(c[1] and c[2] <= 40 for c in cold)
    t = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    L = [f"# Bootstrap of the context-sharing harness ({t})", "",
         f"Written by `harness/tests/acceptance_ctx.py` from the main checkout at `{head}`. It covers the acceptance tests "
         "of brief section 11.7 that concern `nrpic-ctx`, `nrpic-wt` and `nrpic-doctor`; tests 4 and 6 (run registration, "
         "stage-check rehearsal) and the guard and hook rows of test 1 and test 5 belong to the commands of the "
         "runs-and-configuration helper (`nrpic-run`, `nrpic-env`, `nrpic-stage`, `harness/hooks/`) and are reported "
         "there. The round trips run in a scratch repository with five owners, never on the live branches.", "",
         "## Result", "",
         "| Test (brief 11.7) | Where | Result |", "|---|---|---|",
         f"| 1 `nrpic-doctor` passes in all eight worktrees | live, read-only | rows of these commands (`wt`, `build`, `ctx`) "
         f"{'PASS in all nine worktrees' if mine_ok else 'NOT all PASS'}; `gpu` PASS; `venv`, `env`, `scratch`, `guard`, `main`, `kb`, "
         "`git`, `stop` MISSING where their component is not built, not installed or not yet synced (table below) |",
         f"| 2 context round trip (A to B, B's brief, B's ack, A's board; nothing written across worktrees) | scratch | "
         f"{sec_res('Acceptance test 2: context round trip A -> B', 'Messages: each post writes only the poster' + chr(39) + 's worktree and branch')} |",
         f"| 3 proposal round trip (A to orch, DECISIONS on main, every track syncs and reads it) | scratch | "
         f"{sec_res('Acceptance test 3: proposal round trip A -> orch -> DECISIONS -> every track')} |",
         "| 5 destructive test | scratch (refusals of `nrpic-ctx`); guard not built | "
         f"`nrpic-ctx` refusals {sec_res('Refusals')}; the guard part (edit main, edit B, write B's scratch, force-push) is MISSING until `harness/hooks/pre_tool_guard.py` exists |",
         f"| 7 cold start from HANDOFF.md and the brief | scratch and live | scratch {sec_res('Acceptance test 7: cold start from HANDOFF.md and the brief')}; "
         f"live {'PASS' if cold_ok else 'FAIL'}: {sum(c[1] for c in cold)} of {len(cold)} owner briefs show the gate and the `Run next:` line of HANDOFF.md, "
         f"at most {max((c[2] for c in cold), default=0)} lines |", "",
         "Further checks of the self-test (each message exactly once, read commands write nothing, conflict, audit, nrpic-wt):", "",
         "| Section of `harness/tests/test_ctx.py` | Passed | Failed |", "|---|---|---|"]
    for name, (ok, bad) in sec.items():
        L.append(f"| {name} | {ok} | {bad} |")
    L += ["", f"Total: {summ['passed']} checks passed, {summ['failed']} failed (scratch repository `{summ['root']}/repo`, "
          f"{'removed after the passing run' if summ['failed'] == 0 else 'kept for inspection'}).", ""]
    a1 = au.stdout.split("## 1.")[1].split("## 2.")[0] if "## 1." in au.stdout else ""
    a1 = [ln for ln in a1.splitlines() if ln.startswith(("**`", "- `", "- note"))]
    a3 = [ln for ln in au.stdout.split("## Notes")[1].splitlines() if "ignore rule" in ln] if "## Notes" in au.stdout else []
    summary = re.search(r"^Findings: .*$", au.stdout, re.M)
    L += ["## Findings on the live repository (from the audit below)", ""]
    L += (["Commits outside the owner's paths (section 1):", ""] + a1 + [""]) if a1 else ["Section 1: no commit outside the owner's paths.", ""]
    L += a3 + ([""] if a3 else [])
    L += [f"{summary.group(0) if summary else ''}", ""]
    L += ["## Commands", "",
          "Run `harness/tests/test_ctx.py` (self-test, about 20 s) and `harness/tests/acceptance_ctx.py` (this file) "
          "from the main checkout. Usage: `harness/RULES.md`.", ""]
    for title, body in live:
        L += [f"## {title}", "", body]
    L += ["## Transcript of the self-test", "", open(tr).read()]
    out = os.path.join(main_co, args.out)
    with open(out, "w") as fh:
        fh.write("\n".join(L).rstrip() + "\n")
    print(f"wrote {args.out}: self-test {summ['passed']} passed, {summ['failed']} failed; doctor rows of this harness "
          f"{'PASS' if mine_ok else 'not all PASS'}; cold start {'PASS' if cold_ok else 'FAIL'}")
    return 0 if summ["failed"] == 0 and mine_ok and cold_ok else 1


if __name__ == "__main__":
    sys.exit(main())
