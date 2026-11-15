"""`kb watch upstream` (brief 12.7, 12.10; inspection of brief section 2.2 repeated).

1. `git ls-remote --heads` of IAS-Astrophysics/athenak; difference against the previous
   watch snapshot (kb-data/meta/github/watch/<key>/*.json), or on the first run against the
   branch list of the clone record (kb-data/meta/github/<key>.json): new, removed and moved
   branches; names containing pic, vlasov, nrpic or deposit are flagged (brief 12.7).
2. Unless --no-fetch: one bare shallow clone of the tips of all branches (`git clone --bare
   --depth 1 --no-single-branch`) into a new empty directory
   kb-data/raw/watch/<key>/<stamp>.git, and for every branch, read with git plumbing only
   (for-each-ref, ls-tree, cat-file, grep on tree objects; no checkout, so no filter or
   attribute of the repository is applied):
     - tip commit, date, subject;
     - modules under src/; files of src/particles with blob ids; blob ids of src/z4c;
     - the pusher and particle-type enumerations of src/particles/particles.hpp;
     - lines of src/particles that mention z4c, tmunu, adm or deposit (the test of brief
       line 125), lines of src/z4c that mention particles, and lines of src/ with nrpic or
       vlasov;
     - files of src/particles and src/z4c whose blob changed since the previous snapshot.
3. Writes the snapshot JSON and a markdown report with a message for core when something
   the brief asks to watch changed.

Safety [JUDGEMENT]: the bare repository is created by our own git with the user's
configuration off (kbtool.code_fetch.git_env); a clone brings no configuration or hooks;
plumbing commands on objects run nothing from the repository. Nothing is built or run.
"""
import json
import os
import re
import time

from . import __version__
from . import code_fetch as F
from .lock import writer_lock

WATCHED = "IAS-Astrophysics/athenak"
FLAG_RE = re.compile(r"pic|vlasov|nrpic|deposit", re.I)                     # brief 12.7
RELATED_RE = re.compile(r"partic|prtcl|tracer|lagrang|montecarlo|_mc\b|pic|vlasov|deposit|geodesic|collapse|"
                        r"tidal|id_solve|tetrad|adm|z4c-matter", re.I)
BRIEF_BRANCHES = ["particles_gr", "feature/particles-infrastructure", "particles_montecarlo", "feature/lagrangian_mc",
                  "fix/update-prtcl", "tracer_particle", "collapse", "project/tidal-interactions", "id_solve",
                  "id_solve_porting", "project/collapse_relaxation"]                 # brief line 130
COUPLING_RE = r"z4c|tmunu|\badm\b|padm|adm::|deposit"                             # brief line 125, case-insensitive
BACK_RE = re.compile(r"tmunu|deposit", re.I)                                       # sources handed to the spacetime


def _stamp():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def watch_dirs(lay):
    key = F.repo_key(WATCHED)
    return (os.path.join(lay.meta_github, "watch", key), os.path.join(lay.data, "raw", "watch", key))


def previous(lay):
    """(source, {branch: sha}, inspections or None) of the last snapshot, else the clone record."""
    mdir, _ = watch_dirs(lay)
    def order(n):                                      # 20261115T132616Z.json < 20261115T132616Z-1.json
        stem = n[:-5]
        base, _, k = stem.partition("-")
        return base, int(k) if k.isdigit() else 0
    snaps = sorted((n for n in os.listdir(mdir) if n.endswith(".json")), key=order) if os.path.isdir(mdir) else []
    if snaps:
        d = json.load(open(os.path.join(mdir, snaps[-1])))
        insp = d.get("inspection")
        for n in reversed(snaps[:-1]):                 # the last snapshot may come from --no-fetch
            if insp is not None:
                break
            insp = json.load(open(os.path.join(mdir, n))).get("inspection")
        return snaps[-1], d["branches"], insp
    rec = json.load(open(os.path.join(lay.meta_github, F.repo_key(WATCHED) + ".json")))
    br = {b["name"]: b["sha"] for b in rec.get("branches", [])}
    insp = None
    return f"clone record {F.repo_key(WATCHED)}.json ({rec.get('branches_listed_utc')})", br, insp


def _git_lines(args, work, timeout=600):
    r = F.git(args, work, timeout=timeout)
    if r.returncode not in (0, 1):                     # git grep exits 1 when nothing matches
        raise RuntimeError(f"git {' '.join(args[:3])}: {r.stderr.strip()[-300:]}")
    return r.stdout.splitlines()


def parse_enum(text, name):
    m = re.search(r"enum\s+class\s+" + re.escape(name) + r"\s*\{([^}]*)\}", text)
    if not m:
        return None
    body = re.sub(r"//[^\n]*|/\*.*?\*/", "", m.group(1), flags=re.S)
    return [x.strip().split("=")[0].strip() for x in body.split(",") if x.strip()]


def inspect_branch(gd, work, name, sha):
    g = ["--git-dir", gd]
    out = {"name": name, "sha": sha}
    fmt = "%H%x00%cI%x00%s"
    ln = _git_lines(g + ["log", "-1", f"--format={fmt}", sha], work)
    if ln:
        h, date, subj = ln[0].split("\x00")
        out.update({"commit_date": date, "subject": subj[:160]})
    out["src_modules"] = sorted(x.split("/")[-1] for x in _git_lines(g + ["ls-tree", "-d", "--name-only", sha, "src/"], work))
    files = {}
    for line in _git_lines(g + ["ls-tree", "-r", sha, "--", "src/particles", "src/z4c"], work):
        meta, path = line.split("\t", 1)
        files[path] = meta.split()[2]
    out["particles_files"] = sorted(p[len("src/particles/"):] for p in files if p.startswith("src/particles/"))
    out["blobs"] = files
    hdr = F.git(g + ["cat-file", "-p", f"{sha}:src/particles/particles.hpp"], work)
    if hdr.returncode == 0:
        out["pushers"] = parse_enum(hdr.stdout, "ParticlesPusher")
        out["particle_types"] = parse_enum(hdr.stdout, "ParticleType")
    out["coupling_hits"] = _git_lines(g + ["grep", "-I", "-n", "-i", "-E", COUPLING_RE, sha, "--", "src/particles"], work)
    out["z4c_mentions_particles"] = _git_lines(g + ["grep", "-I", "-n", "-i", "-E", "partic|prtcl", sha, "--",
                                                    "src/z4c"], work)
    out["nrpic_vlasov_in_src"] = _git_lines(g + ["grep", "-I", "-n", "-i", "-E", "nrpic|vlasov", sha, "--", "src"], work)
    out["tmunu_users"] = sorted({x.split(":")[1].split("/")[1] for x in
                                 _git_lines(g + ["grep", "-I", "-l", "-i", "tmunu", sha, "--", "src"], work)
                                 if x.count("/") >= 2})
    for k in ("coupling_hits", "z4c_mentions_particles", "nrpic_vlasov_in_src"):
        out[k] = [x.split(":", 1)[1][:240] if x.startswith(sha) else x[:240] for x in out[k]]
    # the brief's test lumps two things together: reading the spacetime (z4c, adm) and acting
    # back on it (tmunu, deposit); the second is the coupling of the paper
    out["backreaction_hits"] = [x for x in out["coupling_hits"] if BACK_RE.search(x.split(":", 2)[-1])]
    out["metric_hits"] = [x for x in out["coupling_hits"] if x not in out["backreaction_hits"]]
    return out


def watch(lay, work, fetch=True, out_md=None, log=print):
    os.makedirs(work, exist_ok=True)
    stamp = base = _stamp()
    mdir0, rdir0 = watch_dirs(lay)
    k = 0
    while os.path.exists(os.path.join(mdir0, f"{stamp}.json")) or os.path.exists(os.path.join(rdir0, f"{stamp}.git")):
        k += 1
        stamp = f"{base}-{k}"                          # two watches within one second
    src_prev, prev_br, prev_insp = previous(lay)
    ok, _, head, branches, err = F.ls_remote(WATCHED, work, heads=True)
    if not ok:
        raise SystemExit(f"git ls-remote {WATCHED} failed: {err}")
    okh, default, head_sha, _, _ = F.ls_remote(WATCHED, work)
    added = sorted(set(branches) - set(prev_br))
    removed = sorted(set(prev_br) - set(branches))
    moved = sorted(b for b in set(branches) & set(prev_br) if branches[b] != prev_br[b])
    flagged = sorted(b for b in branches if FLAG_RE.search(b))
    snap = {"repo": WATCHED, "at": stamp, "tool_version": f"kbtool {__version__}", "default_branch": default,
            "head_sha": head_sha, "branches": branches, "compared_with": src_prev,
            "added": added, "removed": removed, "moved": {b: [prev_br[b], branches[b]] for b in moved},
            "flagged_names": flagged, "brief_branches": {b: branches.get(b) for b in BRIEF_BRANCHES}}
    log(f"{len(branches)} branches; vs {src_prev}: {len(added)} new, {len(removed)} removed, {len(moved)} moved; "
        f"flagged names {flagged}")
    if fetch:
        mdir, rdir = watch_dirs(lay)
        tmp = os.path.join(work, f"watch-{stamp}.git")
        cmd = ["clone", "--bare", "--depth", "1", "--no-single-branch", "--no-tags", F.url_for(WATCHED), tmp]
        t0 = time.time()
        r = F.git(cmd, work, timeout=3600)
        if r.returncode != 0:
            raise SystemExit(f"bare clone failed: {r.stderr.strip()[-300:]}")
        snap["clone_command"] = "git " + " ".join(F.git_safe_config() + cmd)
        snap["clone_seconds"] = round(time.time() - t0, 1)
        refs = {}
        for line in _git_lines(["--git-dir", tmp, "for-each-ref", "--format=%(objectname) %(refname)", "refs/heads"], work):
            sha, ref = line.split(" ", 1)
            refs[ref[len("refs/heads/"):]] = sha
        snap["clone_refs_differ_from_ls_remote"] = sorted(b for b in refs if branches.get(b) != refs[b])
        insp = {}
        for b in sorted(refs):
            insp[b] = inspect_branch(tmp, work, b, refs[b])
        # changes of src/particles and src/z4c against the previous inspection of the same branch
        for b, d in insp.items():
            old = (prev_insp or {}).get(b)
            if old:
                ob, nb = old.get("blobs", {}), d["blobs"]
                d["changed_paths"] = sorted(p for p in set(ob) | set(nb) if ob.get(p) != nb.get(p))
        snap["inspection"] = insp
        final = os.path.join(rdir, f"{stamp}.git")
        with writer_lock(lay, what="watch upstream (bare clone)"):
            os.makedirs(rdir, exist_ok=True)
            os.rename(tmp, final)
        snap["bare_clone"] = os.path.relpath(final, lay.data)
    mdir, _ = watch_dirs(lay)
    with writer_lock(lay, what="watch upstream (snapshot)"):
        os.makedirs(mdir, exist_ok=True)
        p = os.path.join(mdir, f"{stamp}.json")
        with open(p + ".tmp", "w") as f:
            json.dump(snap, f, indent=1, sort_keys=True)
            f.write("\n")
        os.replace(p + ".tmp", p)
    snap["snapshot_path"] = p
    md = report_md(snap)
    if out_md:
        os.makedirs(os.path.dirname(os.path.abspath(out_md)), exist_ok=True)
        with open(out_md, "w") as f:
            f.write(md)
    snap["summary"] = summary_line(snap)
    return snap


def verdict(snap):
    """(branches whose src/particles mentions tmunu or deposit, branches with nrpic/vlasov under src/)."""
    insp = snap.get("inspection") or {}
    with_hits = sorted(b for b, d in insp.items() if d.get("backreaction_hits"))
    with_nrpic = sorted(b for b, d in insp.items() if d["nrpic_vlasov_in_src"])
    return with_hits, with_nrpic


def summary_line(snap):
    insp = snap.get("inspection")
    if insp is None:
        return (f"watch {snap['at']}: {len(snap['branches'])} branches, {len(snap['added'])} new, "
                f"{len(snap['removed'])} removed, {len(snap['moved'])} moved (no clone)")
    hits, nrp = verdict(snap)
    return (f"watch {snap['at']}: {len(snap['branches'])} branches inspected; main {snap['head_sha'][:12]}; "
            f"branches whose src/particles mentions tmunu/deposit: {len(hits)}; z4c/adm only: "
            f"{sum(1 for d in insp.values() if d['metric_hits'] and not d['backreaction_hits'])}; with nrpic/vlasov in src: "
            f"{len(nrp)}; new {len(snap['added'])}, removed {len(snap['removed'])}, moved {len(snap['moved'])}")


def report_md(snap):
    insp = snap.get("inspection") or {}
    L = [f"# kb watch upstream: {snap['repo']}, {snap['at']}", "",
         f"Tool {snap['tool_version']}. Compared with: {snap['compared_with']}. Snapshot:",
         f"`kb-data/meta/github/watch/{F.repo_key(snap['repo'])}/{snap['at']}.json`"
         + (f"; bare clone `kb-data/{snap['bare_clone']}`." if snap.get("bare_clone") else "."), "",
         "## Branch tips", "",
         f"- default branch `{snap['default_branch']}` at {snap['head_sha']}",
         f"- {len(snap['branches'])} branches; new {len(snap['added'])}, removed {len(snap['removed'])}, "
         f"moved {len(snap['moved'])}"]
    for b in snap["added"]:
        L.append(f"  - new: `{b}` {snap['branches'][b][:12]}")
    for b in snap["removed"]:
        L.append(f"  - removed: `{b}`")
    for b, (o, n) in snap["moved"].items():
        L.append(f"  - moved: `{b}` {o[:12]} -> {n[:12]}")
    L.append(f"- names containing pic, vlasov, nrpic or deposit (brief 12.7): "
             + (", ".join(f"`{b}`" for b in snap["flagged_names"]) or "none"))
    L += ["", "## Branches named in brief line 130", "", "| branch | tip | commit date | particles files | pushers | "
          "src/particles lines with tmunu/deposit | with z4c/adm |", "|---|---|---|---|---|---|---|"]
    for b in BRIEF_BRANCHES:
        d = insp.get(b)
        if not snap["brief_branches"].get(b):
            L.append(f"| `{b}` | absent | | | | | |")
        elif d:
            L.append(f"| `{b}` | {d['sha'][:12]} | {d.get('commit_date', '')[:10]} | {len(d['particles_files'])} | "
                     f"{', '.join(d.get('pushers') or []) or '-'} | {len(d['backreaction_hits'])} | "
                     f"{len(d['metric_hits'])} |")
        else:
            L.append(f"| `{b}` | {snap['brief_branches'][b][:12]} | (not inspected) | | | | |")
    if insp:
        hits, nrp = verdict(snap)
        L += ["", "## Particle-spacetime coupling (test of brief line 125, every branch)", ""]
        anyhit = sorted(b for b, d in insp.items() if d["coupling_hits"])
        L.append(f"Branches inspected: {len(insp)} of {len(snap['branches'])}. Branches whose `src/particles` has a "
                 f"line matching `{COUPLING_RE}` (case-insensitive, the test of brief line 125): {len(anyhit)}. "
                 f"Of these, lines with `tmunu` or `deposit` (matter handed to the spacetime): {len(hits)} branches; "
                 f"the others only read the metric (`z4c`, `adm`).")
        for b in anyhit:
            d = insp[b]
            L.append(f"- `{b}` {d['sha'][:12]} ({d.get('commit_date', '')[:10]}): {len(d['backreaction_hits'])} "
                     f"tmunu/deposit lines, {len(d['metric_hits'])} z4c/adm lines, e.g.")
            for x in (d["backreaction_hits"][:4] + d["metric_hits"][:3]):
                L.append(f"    - `{x[:160]}`")
        L.append("")
        L.append(f"Branches with `nrpic` or `vlasov` anywhere under `src/`: {len(nrp)}"
                 + (": " + ", ".join(f"`{b}`" for b in nrp) if nrp else "."))
        zp = sorted(b for b, d in insp.items() if d["z4c_mentions_particles"])
        L.append(f"Branches whose `src/z4c` mentions particles: {len(zp)}"
                 + (": " + ", ".join(f"`{b}`" for b in zp) if zp else "."))
        m = insp.get(snap["default_branch"])
        if m:
            L += ["", f"## `{snap['default_branch']}` at {m['sha'][:12]} ({m.get('commit_date', '')})", "",
                  f"- modules under src/: {', '.join(m['src_modules'])}",
                  f"- src/particles: {', '.join(m['particles_files'])}",
                  f"- pushers: {', '.join(m.get('pushers') or [])}; particle types: "
                  f"{', '.join(m.get('particle_types') or [])}",
                  f"- modules that mention tmunu: {', '.join(m['tmunu_users'])}"]
        rel = sorted(b for b in insp if RELATED_RE.search(b))
        L += ["", "## Particle-related branches by name", "", "| branch | commit date | subject | particles files | "
              "pushers | tmunu/deposit lines | z4c/adm lines |", "|---|---|---|---|---|---|---|"]
        for b in rel:
            d = insp[b]
            L.append(f"| `{b}` | {d.get('commit_date', '')[:10]} | {d.get('subject', '')[:50]} | "
                     f"{len(d['particles_files'])} | {', '.join(d.get('pushers') or []) or '-'} | "
                     f"{len(d['backreaction_hits'])} | {len(d['metric_hits'])} |")
        ch = {b: d["changed_paths"] for b, d in insp.items() if d.get("changed_paths")}
        L += ["", "## Changes of src/particles and src/z4c since the previous snapshot", ""]
        if prev_has_inspection(snap):
            L += [f"- `{b}`: {', '.join(p[:80] for p in ps[:12])}" for b, ps in sorted(ch.items())] or ["- none"]
        else:
            L.append("- first inspected snapshot: this one is the baseline")
    L += ["", "## Message for core", ""]
    msg = []
    if snap["flagged_names"]:
        msg.append("branch names containing pic/vlasov/nrpic/deposit: " + ", ".join(snap["flagged_names"]))
    if insp:
        hits, nrp = verdict(snap)
        if hits:
            msg.append("src/particles mentions tmunu/deposit on: " + ", ".join(hits))
        if nrp:
            msg.append("nrpic or vlasov under src/ on: " + ", ".join(nrp))
        ch = sorted(b for b, d in insp.items() if d.get("changed_paths"))
        if ch:
            msg.append("src/particles or src/z4c changed on: " + ", ".join(ch))
    L.append(("Something to look at: " + "; ".join(msg)) if msg else "Nothing that brief 12.7 asks to report.")
    return "\n".join(L) + "\n"


def prev_has_inspection(snap):
    return not str(snap.get("compared_with", "")).startswith("clone record")
