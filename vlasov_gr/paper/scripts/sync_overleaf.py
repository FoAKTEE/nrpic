#!/usr/bin/env python3
"""
Two-way sync between vlasov_gr/paper/ and the Overleaf Git repository.

Only clean LaTeX manuscript sources are synced:
  - main.tex, supplement.tex, references.bib
  - sections/*.tex
  - sections/tables/*.tex
  - figures/*.pdf

Excludes simulation archives (data/), generator scripts (scripts/), PNG duplicates,
compiled PDFs (main.pdf, supplement.pdf), .gitignore, and TeX build artifacts.
"""

import argparse
import filecmp
import glob
import os
import shutil
import subprocess
import sys

DEFAULT_OVERLEAF_URL = "https://git@git.overleaf.com/6af776a94f165c70a8c2508f"
TOP_FILES = ("main.tex", "supplement.tex", "references.bib")
WHITELIST_GLOBS = (
    ("sections", "*.tex"),
    (os.path.join("sections", "tables"), "*.tex"),
    ("figures", "*.pdf"),
)


def run_git(args, cwd=None, check=True, capture=True):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    res = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if check and res.returncode != 0:
        err = (res.stderr or "").strip()
        out = (res.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed (rc={res.returncode}): {err or out}")
    return res


def get_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    paper_dir = os.path.dirname(script_dir)
    repo_root = run_git(["-C", paper_dir, "rev-parse", "--show-toplevel"]).stdout.strip()
    git_dir = run_git(["-C", repo_root, "rev-parse", "--git-common-dir"]).stdout.strip()
    if not os.path.isabs(git_dir):
        git_dir = os.path.abspath(os.path.join(repo_root, git_dir))
    staging_dir = os.path.join(git_dir, "overleaf_prx")
    return repo_root, paper_dir, staging_dir


def get_overleaf_url(repo_root):
    res = run_git(["-C", repo_root, "remote", "get-url", "overleaf"], check=False)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    return DEFAULT_OVERLEAF_URL


def collect_whitelist(root_dir):
    """Return sorted relative POSIX paths of all whitelisted files present under root_dir."""
    rel_paths = []
    for name in TOP_FILES:
        p = os.path.join(root_dir, name)
        if os.path.isfile(p):
            rel_paths.append(name)
    for subdir, pattern in WHITELIST_GLOBS:
        full_dir = os.path.join(root_dir, subdir)
        if not os.path.isdir(full_dir):
            continue
        for match in sorted(glob.glob(os.path.join(full_dir, pattern))):
            if os.path.isfile(match):
                rel_paths.append(os.path.relpath(match, root_dir).replace(os.sep, "/"))
    return sorted(set(rel_paths))


def ensure_staging_clone(repo_root, staging_dir, url):
    """Ensure staging_dir is cloned, points to url, and is fast-forwarded to origin/main."""
    if not os.path.isdir(os.path.join(staging_dir, ".git")):
        if os.path.exists(staging_dir):
            shutil.rmtree(staging_dir)
        print(f"Cloning Overleaf repo into {staging_dir} ...")
        run_git(["clone", url, staging_dir], capture=True)
    else:
        cur_url = run_git(["-C", staging_dir, "remote", "get-url", "origin"]).stdout.strip()
        if cur_url != url:
            run_git(["-C", staging_dir, "remote", "set-url", "origin", url])

    # Discard any stale uncommitted changes in internal staging mirror before syncing
    run_git(["-C", staging_dir, "reset", "--hard", "HEAD"])
    run_git(["-C", staging_dir, "clean", "-fd"])
    run_git(["-C", staging_dir, "fetch", "origin"])

    # Determine remote default branch (Overleaf uses 'main', fallback 'master')
    branch = "main"
    if run_git(["-C", staging_dir, "rev-parse", "--verify", "origin/main"], check=False).returncode != 0:
        if run_git(["-C", staging_dir, "rev-parse", "--verify", "origin/master"], check=False).returncode == 0:
            branch = "master"

    has_head = run_git(["-C", staging_dir, "rev-parse", "--verify", "HEAD"], check=False).returncode == 0
    if has_head:
        run_git(["-C", staging_dir, "checkout", branch])
        run_git(["-C", staging_dir, "merge", "--ff-only", f"origin/{branch}"])
    else:
        run_git(["-C", staging_dir, "checkout", "-B", branch, f"origin/{branch}"])

    # Ensure commit author identity exists in staging clone
    for key in ("user.name", "user.email"):
        val_res = run_git(["-C", staging_dir, "config", "--get", key], check=False)
        if val_res.returncode != 0 or not val_res.stdout.strip():
            parent_val = run_git(["-C", repo_root, "config", "--get", key], check=False).stdout.strip()
            if parent_val:
                run_git(["-C", staging_dir, "config", key, parent_val])
    return branch


def compute_diff(paper_dir, staging_dir):
    """Compare whitelisted files between local paper_dir and staging_dir."""
    local_files = set(collect_whitelist(paper_dir))
    remote_files = set(collect_whitelist(staging_dir))

    # Also detect any non-whitelisted tracked files in staging_dir
    tracked_all = {
        p.strip()
        for p in run_git(["-C", staging_dir, "ls-files"]).stdout.splitlines()
        if p.strip()
    }
    extra_remote = sorted(tracked_all - remote_files)

    added_local = sorted(local_files - remote_files)
    removed_local = sorted(remote_files - local_files)
    modified = []
    for rel in sorted(local_files & remote_files):
        lp = os.path.join(paper_dir, rel)
        rp = os.path.join(staging_dir, rel)
        if not filecmp.cmp(lp, rp, shallow=False):
            modified.append(rel)

    return {
        "local_files": sorted(local_files),
        "remote_files": sorted(remote_files),
        "added_local": added_local,
        "removed_local": removed_local,
        "modified": modified,
        "extra_remote": extra_remote,
    }


def cmd_status(repo_root, paper_dir, staging_dir, url):
    branch = ensure_staging_clone(repo_root, staging_dir, url)
    head_sha = run_git(["-C", staging_dir, "rev-parse", "--short", "HEAD"]).stdout.strip()
    diff = compute_diff(paper_dir, staging_dir)

    print(f"Overleaf URL:    {url}")
    print(f"Overleaf HEAD:   {branch} @ {head_sha}")
    print(f"Local whitelist: {len(diff['local_files'])} file(s)")
    print(f"Remote whitelist:{len(diff['remote_files'])} file(s)")

    if not diff["added_local"] and not diff["removed_local"] and not diff["modified"] and not diff["extra_remote"]:
        print("Status:          IN SYNC")
        return 0

    for rel in diff["added_local"]:
        print(f"  + local only:  {rel}")
    for rel in diff["modified"]:
        print(f"  M modified:    {rel}")
    for rel in diff["removed_local"]:
        print(f"  - remote only: {rel}")
    for rel in diff["extra_remote"]:
        print(f"  ! non-wl remote: {rel}")
    return 0


def cmd_push(repo_root, paper_dir, staging_dir, url, message):
    branch = ensure_staging_clone(repo_root, staging_dir, url)
    diff = compute_diff(paper_dir, staging_dir)

    if not diff["added_local"] and not diff["removed_local"] and not diff["modified"]:
        head_sha = run_git(["-C", staging_dir, "rev-parse", "--short", "HEAD"]).stdout.strip()
        print(f"Already up to date with Overleaf ({branch} @ {head_sha}).")
        return 0

    # Mirror local whitelist -> staging_dir (copy added/modified, remove deleted whitelisted files)
    local_set = set(diff["local_files"])
    remote_set = set(diff["remote_files"])
    for rel in sorted(remote_set - local_set):
        rp = os.path.join(staging_dir, rel)
        if os.path.isfile(rp):
            os.remove(rp)

    for rel in diff["local_files"]:
        src = os.path.join(paper_dir, rel)
        dst = os.path.join(staging_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    run_git(["-C", staging_dir, "add", "-A"])
    status_out = run_git(["-C", staging_dir, "status", "--short"]).stdout.strip()
    if not status_out:
        print("Nothing changed to commit in Overleaf staging clone.")
        return 0

    run_git(["-C", staging_dir, "commit", "-m", message])
    run_git(["-C", staging_dir, "push", "origin", branch])
    new_sha = run_git(["-C", staging_dir, "rev-parse", "--short", "HEAD"]).stdout.strip()
    print(f"Pushed {len(diff['local_files'])} file(s) to Overleaf ({branch} @ {new_sha}).")
    return 0


def cmd_pull(repo_root, paper_dir, staging_dir, url):
    branch = ensure_staging_clone(repo_root, staging_dir, url)
    remote_files = collect_whitelist(staging_dir)
    copied = 0
    for rel in remote_files:
        src = os.path.join(staging_dir, rel)
        dst = os.path.join(paper_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.isfile(dst) or not filecmp.cmp(src, dst, shallow=False):
            shutil.copy2(src, dst)
            copied += 1

    local_set = set(collect_whitelist(paper_dir))
    remote_only_missing = sorted(local_set - set(remote_files))
    head_sha = run_git(["-C", staging_dir, "rev-parse", "--short", "HEAD"]).stdout.strip()
    print(f"Pulled {len(remote_files)} whitelisted file(s) from Overleaf ({branch} @ {head_sha}); updated {copied} file(s).")
    if remote_only_missing:
        print("Local whitelisted files absent on Overleaf (not deleted automatically):")
        for rel in remote_only_missing:
            print(f"  {rel}")

    st = run_git(["-C", repo_root, "status", "-s", "vlasov_gr/paper/"]).stdout.strip()
    print("--- git status -s vlasov_gr/paper/ ---")
    print(st if st else "(clean)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Sync vlasov_gr/paper/ with Overleaf Git.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_push = sub.add_parser("push", help="Mirror whitelisted TeX/Bib/PDF figure files to Overleaf.")
    p_push.add_argument("-m", "--message", default="Sync manuscript from nrpic/vlasov_gr/paper")

    sub.add_parser("pull", help="Pull Overleaf updates back into vlasov_gr/paper/.")
    sub.add_parser("status", help="Compare local vlasov_gr/paper/ against Overleaf.")

    args = ap.parse_args()
    repo_root, paper_dir, staging_dir = get_paths()
    url = get_overleaf_url(repo_root)

    if args.cmd == "status":
        return cmd_status(repo_root, paper_dir, staging_dir, url)
    if args.cmd == "push":
        return cmd_push(repo_root, paper_dir, staging_dir, url, args.message)
    if args.cmd == "pull":
        return cmd_pull(repo_root, paper_dir, staging_dir, url)
    return 1


if __name__ == "__main__":
    sys.exit(main())
