"""File type from content (not from the extension) and safe extraction (brief 12.3, K1).

kinds returned by `sniff`:
  gzip-tar      gzip-compressed tar archive (the usual arXiv e-print)
  gzip-tex      gzip-compressed single file that looks like TeX
  gzip-other    gzip-compressed single file of another kind
  tar           uncompressed tar archive
  pdf           PDF (arXiv serves it when no TeX source exists)
  tex           plain single TeX file
  html          an HTML page (an error or rate-limit page, never a valid e-print)
  empty, unknown
`source_kind` maps them onto the schema's papers.source_kind ('tex', 'pdf', 'none').

Everything here treats the bytes as data: archives are listed with tarfile and never
extracted with extractall over unchecked members; nothing found is executed.
"""
import io
import os
import stat as _s
import tarfile
import zlib

MAX_DECOMPRESSED = 2 * 1024**3       # bytes: refuse gzip members that inflate beyond this
MAX_FILE = 256 * 1024**2             # bytes: largest single extracted file
MAX_TOTAL = 1024**3                  # bytes: largest extracted total
MAX_MEMBERS = 20000

TEX_HINTS = (b"\\documentclass", b"\\documentstyle", b"\\begin{document}", b"\\input", b"\\section",
             b"\\title", b"\\author", b"\\begin{abstract}", b"\\def")


class TooLarge(ValueError):
    pass


def gunzip_bounded(blob, limit=MAX_DECOMPRESSED):
    """Decompress a gzip stream (concatenated members allowed) without exceeding `limit`."""
    out = []
    total = 0
    data = blob
    while data:
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        while True:
            chunk = d.decompress(data, 1 << 20)
            total += len(chunk)
            if total > limit:
                raise TooLarge(f"gzip stream inflates beyond {limit} bytes")
            out.append(chunk)
            data = d.unconsumed_tail
            if d.eof or not data:
                break
        if not d.eof:
            raise ValueError("truncated gzip stream")
        data = d.unused_data
        if data and data[:2] != b"\x1f\x8b":
            break                                    # trailing garbage after the last member
    return b"".join(out)


def _is_tar(data):
    if len(data) >= 262 and data[257:262] == b"ustar":
        return True
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as t:
            return t.next() is not None
    except Exception:                       # any failure to parse means "not a tar archive"
        return False


def _looks_tex(data):
    head = data[:200000]
    return any(h in head for h in TEX_HINTS)


def _looks_html(data):
    head = data[:2048].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html")


def sniff(blob):
    """Kind of a downloaded e-print, and the decompressed payload when gzip."""
    if not blob:
        return "empty", blob
    if blob[:4] == b"%PDF":
        return "pdf", blob
    if blob[:2] == b"\x1f\x8b":
        data = gunzip_bounded(blob)
        if data[:4] == b"%PDF":
            return "gzip-pdf", data
        if _is_tar(data):
            return "gzip-tar", data
        if _looks_tex(data):
            return "gzip-tex", data
        return "gzip-other", data
    if _is_tar(blob):
        return "tar", blob
    if _looks_html(blob):
        return "html", blob
    if _looks_tex(blob):
        return "tex", blob
    return "unknown", blob


def tar_members(data):
    """List (name, type, size, problem) of the members of a tar archive, without extracting."""
    rows = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as t:
        for m in t:
            rows.append((m.name, member_type(m), m.size, member_problem(m)))
            if len(rows) > MAX_MEMBERS:
                rows.append(("<truncated>", "other", 0, f"more than {MAX_MEMBERS} members"))
                break
    return rows


def member_type(m):
    if m.isfile():
        return "file"
    if m.isdir():
        return "dir"
    if m.issym():
        return "symlink"
    if m.islnk():
        return "hardlink"
    if m.isdev() or m.isfifo():
        return "device"
    return "other"


def member_problem(m):
    name = m.name
    if name.startswith("/") or (len(name) > 1 and name[1] == ":"):
        return "absolute path"
    if ".." in name.replace("\\", "/").split("/"):
        return "parent reference"
    if not (m.isfile() or m.isdir()):
        return f"not a regular file ({member_type(m)})"
    if len(name) > 400:
        return "name too long"
    if m.isfile() and m.size > MAX_FILE:
        return f"file larger than {MAX_FILE} bytes"
    return None


def source_kind(kind, members=None):
    """Map a sniffed kind onto papers.source_kind."""
    if kind in ("gzip-tex", "tex"):
        return "tex"
    if kind in ("pdf", "gzip-pdf"):
        return "pdf"
    if kind in ("gzip-tar", "tar"):
        names = [n.lower() for n, typ, _, prob in (members or []) if typ == "file" and not prob]
        if any(n.endswith(".tex") or n.endswith(".ltx") for n in names):
            return "tex"
        if any(n.endswith(".pdf") for n in names):
            return "pdf"
        return "none"
    return "none"


def safe_extract(blob, dest):
    """Extract an e-print into `dest`, which must not exist yet. Refuses absolute paths,
    parent references, links and devices, and enforces the size limits. Returns
    (kind, list of skipped member names with reasons)."""
    if os.path.lexists(dest):
        raise FileExistsError(dest)
    kind, data = sniff(blob)
    os.makedirs(dest)
    skipped = []
    if kind in ("pdf", "gzip-pdf"):
        _write(os.path.join(dest, "paper.pdf"), data)
        return kind, skipped
    if kind in ("gzip-tex", "tex", "gzip-other"):
        _write(os.path.join(dest, "main.tex"), data)
        return kind, skipped
    if kind not in ("gzip-tar", "tar"):
        return kind, [("<all>", f"not an e-print ({kind})")]
    total = 0
    count = 0
    real_dest = os.path.realpath(dest)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as t:
        for m in t:
            count += 1
            if count > MAX_MEMBERS:
                skipped.append(("<rest>", f"more than {MAX_MEMBERS} members"))
                break
            prob = member_problem(m)
            if prob:
                skipped.append((m.name, prob))
                continue
            target = os.path.realpath(os.path.join(dest, m.name))
            if not (target == real_dest or target.startswith(real_dest + os.sep)):
                skipped.append((m.name, "leaves the directory"))
                continue
            if m.isdir():
                os.makedirs(target, exist_ok=True)
                continue
            total += m.size
            if total > MAX_TOTAL:
                skipped.append((m.name, f"total beyond {MAX_TOTAL} bytes"))
                break
            parent = os.path.dirname(target)
            os.makedirs(parent, exist_ok=True)
            if os.path.lexists(target):
                skipped.append((m.name, "duplicate member"))
                continue
            f = t.extractfile(m)
            _write(target, f.read() if f else b"")
    return kind, skipped


def _write(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def scan_tree(root):
    """Safety scan of an extracted tree: symlinks, devices, oversized files, totals.
    Returns dict(files, bytes, problems=[(relpath, reason)], names=set of file relpaths)."""
    problems, names = [], {}
    total = 0
    real_root = os.path.realpath(root)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for d in list(dirnames):
            p = os.path.join(dirpath, d)
            if os.path.islink(p):
                problems.append((os.path.relpath(p, root), "symlink (directory)"))
                dirnames.remove(d)
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            st = os.lstat(p)
            if _s.S_ISLNK(st.st_mode):
                problems.append((rel, "symlink"))
                continue
            if not _s.S_ISREG(st.st_mode):
                problems.append((rel, "not a regular file"))
                continue
            if not os.path.realpath(p).startswith(real_root + os.sep):
                problems.append((rel, "outside the tree"))
            if st.st_size > MAX_FILE:
                problems.append((rel, f"larger than {MAX_FILE} bytes"))
            if st.st_mode & 0o111:
                problems.append((rel, "executable bit set"))
            total += st.st_size
            names[rel] = st.st_size
    if total > MAX_TOTAL:
        problems.append((".", f"total {total} bytes beyond {MAX_TOTAL}"))
    return {"files": len(names), "bytes": total, "problems": problems, "names": names}
