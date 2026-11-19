"""Commit and licence of a repository checkout, read as files (brief 12.3, K1).

`git` is never run inside a downloaded checkout: a repository's configuration can name
programs that git would execute (core.fsmonitor, filters, hooks). Instead HEAD, loose refs
and packed-refs are read as text. Commit dates and remote branch tips are not in these
files; they come from the download record in kb-data/meta/github/<owner>__<repo>.json,
which the cloning step writes (a later stage).
"""
import os
import re

SHA = re.compile(r"^[0-9a-f]{40}$")
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING", "COPYING.md", "LICENSE.rst")

# conservative text signatures; anything else stays "unknown" and is checked by hand
SPDX_SIGNATURES = [
    ("Apache-2.0", (r"Apache License", r"Version 2\.0")),
    ("GPL-3.0", (r"GNU GENERAL PUBLIC LICENSE", r"Version 3")),
    ("GPL-2.0", (r"GNU GENERAL PUBLIC LICENSE", r"Version 2")),
    ("LGPL-3.0", (r"GNU LESSER GENERAL PUBLIC LICENSE", r"Version 3")),
    ("LGPL-2.1", (r"GNU LESSER GENERAL PUBLIC LICENSE", r"Version 2\.1")),
    ("AGPL-3.0", (r"GNU AFFERO GENERAL PUBLIC LICENSE",)),
    ("MPL-2.0", (r"Mozilla Public License", r"2\.0")),
    ("BSD-3-Clause", (r"Redistribution and use in source and binary forms",
                      r"(?:Neither the name|names of its\s+contributors)")),
    ("BSD-2-Clause", (r"Redistribution and use in source and binary forms",)),
    ("MIT", (r"Permission is hereby granted, free of charge",)),
]


def _read(path, limit=1 << 16):
    try:
        with open(path, "rb") as f:
            return f.read(limit).decode("utf-8", errors="replace")
    except OSError:
        return None


def guess_spdx(text):
    for spdx, pats in SPDX_SIGNATURES:
        if all(re.search(p, text, re.IGNORECASE) for p in pats):
            return spdx
    return "unknown"


def resolve_ref(gitdir, ref):
    """sha of a ref name ('refs/heads/main') from loose refs or packed-refs, or None."""
    p = os.path.normpath(os.path.join(gitdir, ref))
    if not p.startswith(os.path.normpath(gitdir) + os.sep):
        return None
    if os.path.isfile(p) and not os.path.islink(p):
        s = (_read(p) or "").strip()
        if SHA.match(s):
            return s
    packed = _read(os.path.join(gitdir, "packed-refs"), limit=1 << 24) or ""
    for line in packed.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].strip() == ref and SHA.match(parts[0]):
            return parts[0]
    return None


def read_checkout(path):
    """dict(commit_sha, head_ref, license_files, license_spdx_guess, problems)."""
    out = {"problems": []}
    gitdir = os.path.join(path, ".git")
    if os.path.isfile(gitdir):                       # a gitdir file: not followed (could point anywhere)
        out["problems"].append(".git is a file (linked checkout); not followed")
        gitdir = None
    elif not os.path.isdir(gitdir):
        out["problems"].append("no .git directory")
        gitdir = None
    if gitdir:
        head = (_read(os.path.join(gitdir, "HEAD")) or "").strip()
        if head.startswith("ref: "):
            ref = head[5:].strip()
            out["head_ref"] = ref
            out["commit_sha"] = resolve_ref(gitdir, ref)
            if out["commit_sha"] is None:
                out["problems"].append(f"HEAD ref {ref} does not resolve")
        elif SHA.match(head):
            out["head_ref"] = None                   # detached at the pinned commit
            out["commit_sha"] = head
        else:
            out["problems"].append("HEAD unreadable")
    lic = [n for n in LICENSE_NAMES if os.path.isfile(os.path.join(path, n))
           and not os.path.islink(os.path.join(path, n))]
    out["license_files"] = lic
    out["license_spdx_guess"] = guess_spdx(_read(os.path.join(path, lic[0])) or "") if lic else "none"
    return out
