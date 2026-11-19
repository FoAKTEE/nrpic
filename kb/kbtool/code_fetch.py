"""K6 download step: shallow clones of the repository manifest (brief 12.2, 12.3, 17).

    kb fetch-repos [--repo owner/name ...] [--refresh] [--dry-run]

Each repository of kb/manifests/github.tsv is cloned with `git clone --depth 1` into a new
empty directory (first under the run's work directory, then moved into
kb-data/raw/github/<owner>__<repo>/ under the writer lock), and a record
kb-data/meta/github/<owner>__<repo>.json is written with url, commit sha and date, default
branch, licence guess, size and the exact command. A name that does not resolve
(`git ls-remote` fails) is recorded as "unresolved" and listed; no other name is tried.

Safety [JUDGEMENT]: git runs with the user's configuration switched off
(GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1), so no credential helper sends the
user's token and no URL rewrite applies; no terminal prompt; only https; no submodules,
no tags, no LFS smudge, symlinks checked out as plain files, objects checked with fsck.
A clone does not bring hooks or configuration from the remote. After the clone, git is run
exactly once on the fresh clone (`git log -1` for the commit date and subject), with the
same isolated environment; afterwards the checkout is only read as files. Nothing in a
clone is built, run or imported.
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import time

from . import __version__
from .brief import load_github_manifest
from .gitmeta import read_checkout
from .lock import writer_lock
from .paths import kb_manifest_dir

WATCHED = "IAS-Astrophysics/athenak"


def repo_key(repo):
    return repo.replace("/", "__")


def base_url():
    return os.environ.get("KB_GITHUB_BASE", "https://github.com").rstrip("/")


def url_for(repo):
    return f"{base_url()}/{repo}.git" if base_url().startswith("https://") else f"{base_url()}/{repo}"


def git_env(work):
    """Environment for every git call on downloaded data: no user or system config."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
                "GIT_ASKPASS": "/bin/false", "SSH_ASKPASS": "/bin/false", "GIT_LFS_SKIP_SMUDGE": "1",
                "GIT_PROTOCOL_FROM_USER": "0", "HOME": work, "LC_ALL": "C"})
    env.pop("SSH_AUTH_SOCK", None)
    return env


def git_safe_config():
    allowed = "file" if base_url().startswith("file://") else "https"     # tests use a local file:// remote
    opts = {"core.symlinks": "false", "core.hooksPath": os.devnull, "core.fsmonitor": "false",
            "protocol.allow": "never", f"protocol.{allowed}.allow": "always",
            "transfer.fsckObjects": "true", "submodule.recurse": "false", "credential.helper": "",
            "filter.lfs.smudge": "", "filter.lfs.process": "", "filter.lfs.required": "false",
            "advice.detachedHead": "false", "init.defaultBranch": "main"}
    out = []
    for k, v in opts.items():
        out += ["-c", f"{k}={v}"]
    return out


def git(args, work, timeout=900):
    return subprocess.run(["git"] + git_safe_config() + args, cwd=work, env=git_env(work),
                          capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)


def git_version():
    try:
        return subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return None


def ls_remote(repo, work, heads=False):
    """(ok, default_branch, head_sha, branches {name: sha}, error text)."""
    args = ["ls-remote", "--symref", url_for(repo), "HEAD"] if not heads else ["ls-remote", "--heads", url_for(repo)]
    try:
        r = git(args, work, timeout=180)
    except subprocess.TimeoutExpired:
        return False, None, None, {}, "ls-remote timed out"
    if r.returncode != 0:
        return False, None, None, {}, (r.stderr.strip().splitlines() or ["?"])[-1][:300]
    default, head, branches = None, None, {}
    for line in r.stdout.splitlines():
        if line.startswith("ref: ") and line.endswith("\tHEAD"):
            default = line[5:-5].strip().removeprefix("refs/heads/")
        else:
            parts = line.split("\t")
            if len(parts) == 2 and len(parts[0]) == 40:
                if parts[1] == "HEAD":
                    head = parts[0]
                elif parts[1].startswith("refs/heads/"):
                    branches[parts[1][len("refs/heads/"):]] = parts[0]
    return True, default, head, branches, None


def tree_size(path):
    """(bytes, files) of a checkout without .git; symlinks counted, never followed."""
    nbytes = nfiles = 0
    for root, dirs, files in os.walk(path):
        if root == path and ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            st = os.lstat(os.path.join(root, f))
            nbytes += st.st_size
            nfiles += 1
    return nbytes, nfiles


def make_read_only(path):
    """Remove write bits from the files of the checkout (directories stay writable)."""
    for root, dirs, files in os.walk(path):
        if root == path and ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            p = os.path.join(root, f)
            st = os.lstat(p)
            if stat.S_ISREG(st.st_mode):
                os.chmod(p, stat.S_IMODE(st.st_mode) & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def clone_one(lay, row, work, log=print):
    """Clone one manifest row. Returns the record written to meta/github (or that would be)."""
    repo = row["repo"]
    key = repo_key(repo)
    final = os.path.join(lay.raw_github, key)
    rec = {"repo": repo, "url": url_for(repo), "role": row["role"], "owners": row["owners"],
           "description": row.get("description"), "tool_version": f"kbtool {__version__}",
           "git_version": git_version(), "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t0 = time.time()
    ok, default, head, _, err = ls_remote(repo, work)
    if not ok:
        rec.update({"status": "unresolved", "error": err})
        return rec
    rec.update({"default_branch": default, "remote_head_sha": head})
    if repo.lower() == WATCHED.lower():
        okb, _, _, branches, errb = ls_remote(repo, work, heads=True)
        rec["branches"] = [{"name": n, "sha": s} for n, s in sorted(branches.items())] if okb else []
        rec["branches_listed_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not okb:
            rec["branches_error"] = errb
    tmp = os.path.join(work, f"clone-{key}")                    # a new empty directory (git creates it)
    if os.path.lexists(tmp):
        raise RuntimeError(f"work directory {tmp} exists; refusing to reuse it")
    cmd = ["clone", "--depth", "1", "--single-branch", "--no-tags", "--no-recurse-submodules",
           url_for(repo), tmp]
    rec["command"] = "git " + " ".join(git_safe_config() + cmd)
    try:
        r = git(cmd, work, timeout=1800)
    except subprocess.TimeoutExpired:
        rec.update({"status": "failed", "error": "clone timed out after 1800 s"})
        return rec
    if r.returncode != 0:
        rec.update({"status": "failed", "error": (r.stderr.strip().splitlines() or ["?"])[-1][:300]})
        return rec
    info = read_checkout(tmp)                                   # HEAD read as a file
    lg = git(["--git-dir", os.path.join(tmp, ".git"), "log", "-1", "--format=%H%x00%cI%x00%aI%x00%s"], work)
    parts = lg.stdout.rstrip("\n").split("\x00") if lg.returncode == 0 else []
    if len(parts) == 4:
        rec.update({"commit_date": parts[1], "author_date": parts[2], "commit_subject": parts[3][:200]})
        if info.get("commit_sha") and parts[0] != info["commit_sha"]:
            rec.setdefault("problems", []).append("git log HEAD differs from HEAD read as a file")
    rec["commit_sha"] = info.get("commit_sha")
    rec["head_ref"] = info.get("head_ref")
    if head and rec["commit_sha"] and head != rec["commit_sha"]:
        rec.setdefault("notes", []).append("remote HEAD moved between ls-remote and clone")
    rec["license_files"] = info.get("license_files")
    rec["license_spdx"] = info.get("license_spdx_guess")
    rec["license_source"] = "text signature of the licence file (kbtool.gitmeta.guess_spdx)"
    nbytes, nfiles = tree_size(tmp)
    rec.update({"bytes": nbytes, "n_files": nfiles,
                "git_dir_bytes": sum(os.lstat(os.path.join(r_, f)).st_size
                                     for r_, _, fs in os.walk(os.path.join(tmp, ".git")) for f in fs)})
    make_read_only(tmp)
    rec["clone_seconds"] = round(time.time() - t0, 1)
    rec["status"] = "ok"
    rec["path"] = os.path.relpath(final, lay.data)
    with writer_lock(lay, what=f"fetch-repos {repo}"):
        if os.path.lexists(final):
            raise RuntimeError(f"{final} exists; refusing to overwrite (use --refresh to move it aside)")
        os.makedirs(lay.raw_github, exist_ok=True)
        os.rename(tmp, final)
    return rec


def write_record(lay, rec):
    os.makedirs(lay.meta_github, exist_ok=True)
    p = os.path.join(lay.meta_github, repo_key(rec["repo"]) + ".json")
    with writer_lock(lay, what=f"fetch-repos record {rec['repo']}"):
        tmp = f"{p}.tmp-{os.getpid()}"
        with open(tmp, "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
            f.write("\n")
        os.replace(tmp, p)
    return p


def fetch_repos(lay, work, repos=None, refresh=False, dry_run=False, log=print, manifest_dir=None):
    """Clone the manifest repositories (or the subset `repos`) one after the other.
    AthenaK goes first (the upstream watch needs it). Returns the list of records."""
    rows = load_github_manifest(os.path.join(manifest_dir or kb_manifest_dir(), "github.tsv"))
    if repos:
        want = {r.lower() for r in repos}
        unknown = want - {r["repo"].lower() for r in rows}
        if unknown:
            raise SystemExit(f"not in the manifest: {sorted(unknown)}")
        rows = [r for r in rows if r["repo"].lower() in want]
    rows.sort(key=lambda r: r["repo"].lower() != WATCHED.lower())
    os.makedirs(work, exist_ok=True)
    out = []
    for i, row in enumerate(rows, 1):
        key = repo_key(row["repo"])
        final = os.path.join(lay.raw_github, key)
        meta_p = os.path.join(lay.meta_github, key + ".json")
        if os.path.isdir(final) and os.path.exists(meta_p) and not refresh:
            log(f"[{i}/{len(rows)}] {row['repo']}: present, skipped")
            out.append(json.load(open(meta_p)))
            continue
        if dry_run:
            log(f"[{i}/{len(rows)}] {row['repo']}: would clone {url_for(row['repo'])}")
            continue
        if refresh and os.path.isdir(final):
            with writer_lock(lay, what=f"fetch-repos refresh {row['repo']}"):
                aside = os.path.join(lay.data, "raw", "github-old",
                                     f"{key}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
                os.makedirs(os.path.dirname(aside), exist_ok=True)
                os.rename(final, aside)
        try:
            rec = clone_one(lay, row, work, log=log)
        except Exception as e:                                   # record and go on with the next one
            rec = {"repo": row["repo"], "role": row["role"], "status": "failed", "error": repr(e)[:300],
                   "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        write_record(lay, rec)
        out.append(rec)
        log(f"[{i}/{len(rows)}] {row['repo']}: {rec['status']} "
            + (f"{rec.get('commit_sha', '')[:12]} {rec.get('commit_date', '')} {rec.get('bytes', 0) / 1e6:.1f} MB "
               f"{rec.get('n_files', 0)} files {rec.get('license_spdx', '')} {rec.get('clone_seconds', '')} s"
               if rec["status"] == "ok" else rec.get("error", "")))
        sys.stdout.flush()
    return out
