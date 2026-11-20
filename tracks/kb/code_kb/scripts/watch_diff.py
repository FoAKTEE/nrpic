"""Line-level size of the src/particles and src/z4c changes found by `kb watch upstream`.

Usage: python3 -I watch_diff.py <old snapshot.json> <new snapshot.json> <out_dir>

Reads the two watch snapshots (kb-data/meta/github/watch/<key>/<stamp>.json) and the two
bare shallow clones they name (kb-data/raw/watch/<key>/<stamp>.git). For every branch whose
src/particles or src/z4c blobs changed between the snapshots, and for every new branch
against `main` of the new snapshot, it reads the old and new blobs with `git cat-file -p`
(plumbing only: nothing in the clone is checked out, built or run; git runs with the user's
configuration off, as kbtool.code_fetch does) and counts added and removed lines with
difflib. Writes <out_dir>/watch_diff.json and <out_dir>/watch_diff.md (counts and file names
only, no code).
"""
import difflib
import json
import os
import subprocess
import sys

DATA = "/data/haiyangw/nrpic/kb-data"


def git_env(work):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
                "HOME": work, "LC_ALL": "C"})
    return env


def blob_text(gitdir, blob, work):
    if blob is None:
        return []
    r = subprocess.run(["git", "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false",
                        "--git-dir", gitdir, "cat-file", "-p", blob], cwd=work, env=git_env(work),
                       capture_output=True, timeout=120, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(f"cat-file {blob} in {gitdir}: {r.stderr.decode(errors='replace')[-200:]}")
    return r.stdout.decode("utf-8", errors="replace").splitlines()


def counts(a, b):
    add = rem = 0
    for ln in difflib.unified_diff(a, b, lineterm="", n=0):
        if ln.startswith("+++") or ln.startswith("---"):
            continue
        if ln.startswith("+"):
            add += 1
        elif ln.startswith("-"):
            rem += 1
    return add, rem


def main(old_p, new_p, out):
    os.makedirs(out, exist_ok=True)
    work = out
    old, new = json.load(open(old_p)), json.load(open(new_p))
    og, ng = os.path.join(DATA, old["bare_clone"]), os.path.join(DATA, new["bare_clone"])
    rows = []
    for b in sorted(new["moved"]):
        ob = old["inspection"][b]["blobs"]
        nb = new["inspection"][b]["blobs"]
        for p in sorted(set(ob) | set(nb)):
            if ob.get(p) == nb.get(p):
                continue
            a, r = counts(blob_text(og, ob.get(p), work), blob_text(ng, nb.get(p), work))
            rows.append({"branch": b, "kind": "moved", "path": p, "old_tip": old["branches"][b],
                         "new_tip": new["branches"][b], "old_blob": ob.get(p), "new_blob": nb.get(p),
                         "added": a, "removed": r, "status": "added" if p not in ob else
                         ("deleted" if p not in nb else "modified")})
    main_b = new["inspection"][new["default_branch"]]["blobs"]
    for b in sorted(new["added"]):
        nb = new["inspection"][b]["blobs"]
        for p in sorted(set(main_b) | set(nb)):
            if main_b.get(p) == nb.get(p):
                continue
            a, r = counts(blob_text(ng, main_b.get(p), work), blob_text(ng, nb.get(p), work))
            rows.append({"branch": b, "kind": "new (against main)", "path": p,
                         "old_tip": new["branches"][new["default_branch"]], "new_tip": new["branches"][b],
                         "old_blob": main_b.get(p), "new_blob": nb.get(p), "added": a, "removed": r,
                         "status": "added" if p not in main_b else ("deleted" if p not in nb else "modified")})
    moved_info = {b: {"old": o, "new": n, "commit_date": new["inspection"][b].get("commit_date"),
                      "subject": new["inspection"][b].get("subject")} for b, (o, n) in new["moved"].items()}
    added_info = {b: {"tip": new["branches"][b], "commit_date": new["inspection"][b].get("commit_date"),
                      "subject": new["inspection"][b].get("subject")} for b in new["added"]}
    removed_info = {b: {"tip": old["branches"][b], "commit_date": old["inspection"][b].get("commit_date"),
                        "subject": old["inspection"][b].get("subject")} for b in new["removed"]}
    res = {"old": old["at"], "new": new["at"], "main_old": old["head_sha"], "main_new": new["head_sha"],
           "n_branches": len(new["branches"]), "moved": moved_info, "added": added_info, "removed": removed_info,
           "flagged_names": new["flagged_names"], "rows": rows}
    with open(os.path.join(out, "watch_diff.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    L = [f"# Watch diff {old['at']} -> {new['at']}", "",
         f"main {old['head_sha'][:12]} -> {new['head_sha'][:12]}; {len(new['branches'])} branches; "
         f"flagged names: {new['flagged_names'] or 'none'}", "",
         "| branch | kind | tip | commit date | subject |", "|---|---|---|---|---|"]
    for b, d in sorted(moved_info.items()):
        L.append(f"| `{b}` | moved {d['old'][:12]} -> | {d['new'][:12]} | {d['commit_date']} | {d['subject']} |")
    for b, d in sorted(added_info.items()):
        L.append(f"| `{b}` | new | {d['tip'][:12]} | {d['commit_date']} | {d['subject']} |")
    for b, d in sorted(removed_info.items()):
        L.append(f"| `{b}` | removed (last tip) | {d['tip'][:12]} | {d['commit_date']} | {d['subject']} |")
    L += ["", "src/particles and src/z4c files that differ (moved: old tip -> new tip; new: main -> branch):", "",
          "| branch | kind | path | status | lines added | lines removed |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| `{r['branch']}` | {r['kind']} | {r['path']} | {r['status']} | {r['added']} | {r['removed']} |")
    if not rows:
        L.append("| (none) | | | | | |")
    with open(os.path.join(out, "watch_diff.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:4])
