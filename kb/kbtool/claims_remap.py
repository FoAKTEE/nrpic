"""Claim-safe re-ingest: claims follow a paper to its new chunk ids and flat.tex ranges.

A re-ingest (`kb ingest arxiv`) deletes a paper's chunks and writes new ones with new row
ids, and a changed parser can move every character offset of flat.tex. Claims point into a
paper through claims.chunk_id, claims.quote_start/quote_end and, per locator, through
claim_locators.flat_start, flat_end and chunk_ids_json; each locator row also holds what the
note wrote (file, line_start, line_end), which does not change with the parser.

So the remap recomputes, for every locator row of the paper, the flat range from (file,
line_start, line_end) through the NEW source map, and its chunk ids from that range, exactly
as kbtool.claims_check.Store resolves a locator. The old flat range is kept only when the new
lines cannot be mapped and flat.tex is byte-identical (then the old offsets are still right).
A claim's own chunk_id and quote range then follow the rule of kbtool.claims_db.upsert_seed
(first resolved locator row: its first chunk and its range). A claim with a chunk in the paper
but no locator row of the paper is carried through the OLD source map: old chunk range ->
(file, lines) -> new range -> new chunk. Labels and statuses are never touched; every claim
handled gets a claim_events row (action 'remap').

Use: capture() before the paper's rows and build files are replaced, apply() after, in the
same transaction and writer-lock hold (kbtool.papers_ingest.store with remap_claims=True).
"""
import bisect
import json
import os

from . import claims_check as CK
from . import inventory as _inv
from .claims_db import event

ROW_COLS = ("loc_id", "claim_id", "ord", "paper_id", "version", "file", "line_start", "line_end", "resolved",
            "flat_start", "flat_end", "chunk_ids_json")
BUILD_FILES = ("flat.tex", "doc.json", "sourcemap.json")


def _build_dir(lay, pid):
    return os.path.join(lay.build, "tex", _inv.id_key(pid))


def _claim_tables(con):
    names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    return {"claims", "claim_locators", "claim_events"} <= names


def capture(con, lay, pid):
    """State of the paper and of every claim that points into it, before the re-ingest."""
    r = con.execute("SELECT flat_sha256, version FROM papers WHERE paper_id=?", (pid,)).fetchone()
    smap = None
    try:
        with open(os.path.join(_build_dir(lay, pid), "sourcemap.json")) as f:
            smap = json.load(f)
    except (OSError, ValueError):
        pass
    out = {"paper_id": pid, "flat_sha": r[0] if r else None, "version": r[1] if r else None, "sourcemap": smap,
           "rows": [], "claims": {}}
    if not _claim_tables(con):
        return out
    out["rows"] = [dict(zip(ROW_COLS, x)) for x in con.execute(
        "SELECT " + ", ".join(ROW_COLS) + " FROM claim_locators WHERE paper_id=? ORDER BY claim_id, ord", (pid,))]
    cids = {x[0] for x in con.execute(
        "SELECT claim_id FROM claims WHERE paper_id=? OR chunk_id IN (SELECT chunk_id FROM chunks WHERE paper_id=?)",
        (pid, pid))} | {row["claim_id"] for row in out["rows"]}
    for cid in sorted(cids):
        c = con.execute("SELECT c.chunk_id, c.quote_start, c.quote_end, k.paper_id, k.char_start, k.char_end "
                        "FROM claims c LEFT JOIN chunks k ON k.chunk_id = c.chunk_id WHERE c.claim_id=?",
                        (cid,)).fetchone()
        out["claims"][cid] = {"chunk_id": c[0], "quote_start": c[1], "quote_end": c[2],
                              "chunk_in_paper": c[3] == pid, "chunk_range": (c[4], c[5]) if c[3] == pid else None}
    return out


def save_build(lay, pid):
    """The paper's current build files (bytes), so a rolled-back write can put them back."""
    saved = {}
    d = _build_dir(lay, pid)
    for name in BUILD_FILES:
        try:
            with open(os.path.join(d, name), "rb") as f:
                saved[name] = f.read()
        except OSError:
            saved[name] = None
    return saved


def restore_build(lay, pid, saved):
    d = _build_dir(lay, pid)
    for name, data in (saved or {}).items():
        p = os.path.join(d, name)
        if data is None:
            continue
        tmp = p + f".restore-{os.getpid()}"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, p)


def _old_lines(smap, lo, hi):
    """(file, first line, last line) of the old flat range [lo, hi) through the old source map."""
    if not smap or lo is None:
        return None
    starts = [e[0] for e in smap]
    i = bisect.bisect_right(starts, lo) - 1
    j = bisect.bisect_right(starts, max(lo, (hi if hi is not None else lo) - 1)) - 1
    if i < 0:
        return None
    f0, l0 = smap[i][1], smap[i][2]
    f1, l1 = smap[j][1], smap[j][2]
    return (f0, l0, l1 if f1 == f0 and l1 >= l0 else l0)


def _best_chunk(con, pid, a, b):
    """The non-comment chunk of the paper that covers most of [a, b) (first in order on a tie)."""
    if a is None or b is None:
        return None
    best, best_ov = None, 0
    for cid, s, e in con.execute("SELECT chunk_id, char_start, char_end FROM chunks WHERE paper_id=? AND "
                                 "kind!='comment' AND char_start < ? AND char_end > ? ORDER BY char_start",
                                 (pid, b, a)):
        ov = min(b, e) - max(a, s)
        if ov > best_ov:
            best, best_ov = cid, ov
    return best


def apply(con, lay, pid, before, by):
    """Remap after the paper's new rows and build files are written. Returns a summary."""
    summary = {"paper_id": pid, "rows": 0, "rows_changed": 0, "claims": 0, "claims_changed": 0, "methods": {},
               "identical_flat": False, "per_claim": []}
    if not before or not _claim_tables(con) or (not before["rows"] and not before["claims"]):
        return summary
    r = con.execute("SELECT flat_sha256, version FROM papers WHERE paper_id=?", (pid,)).fetchone()
    new_sha, new_ver = (r[0], r[1]) if r else (None, None)
    identical = before["flat_sha"] is not None and before["flat_sha"] == new_sha
    summary["identical_flat"] = identical
    store = CK.Store(lay.raw_arxiv, os.path.join(lay.build, "tex"), con)

    def count(m):
        summary["methods"][m] = summary["methods"].get(m, 0) + 1

    new_rows = {}
    for row in before["rows"]:
        summary["rows"] += 1
        old = (row["flat_start"], row["flat_end"], row["chunk_ids_json"])
        a, b = row["flat_start"], row["flat_end"]
        if not row["resolved"]:
            method = "unresolved row (untouched)"
        elif row["version"] and new_ver and row["version"] != new_ver:
            a, b, method = None, None, "version differs from the ingested one (no range)"
        elif row["file"] and row["line_start"]:
            a, b = store.flat_range(pid, row["file"], row["line_start"], row["line_end"] or row["line_start"])
            method = "lines through the new source map"
            if a is None:
                if identical and row["flat_start"] is not None:
                    a, b, method = row["flat_start"], row["flat_end"], "old range kept (flat.tex byte-identical)"
                else:
                    method = "lines not in the new flat.tex (no range)"
        elif identical:
            method = "no lines; old range kept (flat.tex byte-identical)"
        else:
            a, b, method = None, None, "no lines and flat.tex changed (no range)"
        chunks = store.chunks_overlapping(pid, a, b) if (row["resolved"] and a is not None) else \
            (json.loads(row["chunk_ids_json"] or "[]") if not row["resolved"] else [])
        new = (a, b, json.dumps(chunks))
        count(method)
        new_rows[row["loc_id"]] = {"flat_start": a, "flat_end": b, "chunk_ids": chunks, "method": method}
        if new != old:
            summary["rows_changed"] += 1
            con.execute("UPDATE claim_locators SET flat_start=?, flat_end=?, chunk_ids_json=? WHERE loc_id=?",
                        (a, b, new[2], row["loc_id"]))

    for cid, c in sorted(before["claims"].items()):
        summary["claims"] += 1
        rows = [dict(zip(ROW_COLS, x)) for x in con.execute(
            "SELECT " + ", ".join(ROW_COLS) + " FROM claim_locators WHERE claim_id=? ORDER BY ord, loc_id", (cid,))]
        first = next((x for x in rows if x["resolved"]), None)
        chunk, qs, qe = c["chunk_id"], c["quote_start"], c["quote_end"]
        if first is not None and first["paper_id"] == pid:
            ch = json.loads(first["chunk_ids_json"] or "[]")
            chunk, qs, qe = (ch[0] if ch else None), first["flat_start"], first["flat_end"]
            how = "first resolved locator row"
        elif c["chunk_in_paper"]:
            lo, hi = c["chunk_range"]
            if identical:
                a, b = lo, hi
                how = "old chunk range (flat.tex byte-identical)"
            else:
                ln = _old_lines(before["sourcemap"], lo, hi)
                a, b = store.flat_range(pid, ln[0], ln[1], ln[2]) if ln else (None, None)
                how = "old chunk range through the old and new source maps"
                if c["quote_start"] is not None:
                    lq = _old_lines(before["sourcemap"], c["quote_start"], c["quote_end"])
                    qs, qe = store.flat_range(pid, lq[0], lq[1], lq[2]) if lq else (None, None)
            chunk = _best_chunk(con, pid, a, b)
        else:
            how = "no locator row and no chunk in this paper (untouched)"
        changed = (chunk, qs, qe) != (c["chunk_id"], c["quote_start"], c["quote_end"])
        if changed:
            summary["claims_changed"] += 1
            con.execute("UPDATE claims SET chunk_id=?, quote_start=?, quote_end=? WHERE claim_id=?",
                        (chunk, qs, qe, cid))
        ev = {"paper": pid, "how": how, "chunk": [c["chunk_id"], chunk], "quote": [[c["quote_start"], c["quote_end"]],
                                                                                [qs, qe]],
              "rows": {str(x["loc_id"]): new_rows[x["loc_id"]] for x in rows if x["loc_id"] in new_rows},
              "flat_identical": identical}
        event(con, cid, by, "remap", None, None, None, None, json.dumps(ev)[:4000])
        summary["per_claim"].append({"claim_id": cid, "how": how, "old_chunk": c["chunk_id"], "new_chunk": chunk,
                                     "changed": changed})
    return summary
