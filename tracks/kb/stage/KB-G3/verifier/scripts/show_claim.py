"""Read-only reader: a claim of the snapshot, its locator rows with the source lines, its events.

python3 -I show_claim.py [--window N] [--max-lines M] ID [ID ...]   (terminal only; paper text
stays on the machine and is never written into the repository)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcommon as vc  # noqa: E402

BRIEF = os.path.join(vc.REPO, "einstein_vlasov_pic_cosmology_agent_brief.en.md")


def show(c, cid, window, maxl):
    r = c.execute("select claim_id, label, kind, paper_id, locator, text, supersedes, origin, track_tags"
                  " from claims where claim_id=?", (cid,)).fetchone()
    if not r:
        print("no claim", cid)
        return
    m = c.execute("select track, status, status_detail, evidence, origin_path, origin_line from claim_meta"
                  " where claim_id=?", (cid,)).fetchone()
    print("=" * 100)
    print("claim %d  label %s  status %s  track %s  kind %s  paper %s  supersedes %s" % (r[0], r[1], m[1], m[0], r[2], r[3], r[6]))
    print("origin %s   tags %s" % (r[7], r[8]))
    print("locator string: %s" % r[4])
    print("TEXT: %s" % r[5])
    print("meta evidence: %s" % (m[3] or "")[:600])
    if m[4] and m[4].endswith("brief.en.md") and m[5]:
        bl = open(BRIEF, encoding="utf-8").read().split("\n")
        print("brief L%d: %s" % (m[5], bl[m[5] - 1][:1200]))
    for lr in c.execute("select ord, paper_id, version, file, line_start, line_end, written, resolved, problem"
                        " from claim_locators where claim_id=? order by ord", (cid,)):
        print("-- locator %s: %s %s %s L%s-%s (written %s, resolved %s %s)" % lr)
        if lr[3] and lr[4]:
            src = vc.source_lines(lr[1], lr[2], lr[3])
            if src is None:
                print("   <source file missing>")
                continue
            a0, b0 = max(1, lr[4] - window), min(len(src), (lr[5] or lr[4]) + window)
            for i in range(a0, min(b0, a0 + maxl) + 1):
                mark = ">" if lr[4] <= i <= (lr[5] or lr[4]) else " "
                print("%s%5d| %s" % (mark, i, src[i - 1][:400]))
    for e in c.execute("select at, by, action, from_label, to_label, from_status, to_status, evidence"
                       " from claim_events where claim_id=? order by event_id", (cid,)):
        print("   EV %s %s %s %s->%s %s->%s :: %s" % (e[0], e[1], e[2], e[3], e[4], e[5], e[6], (e[7] or "")[:700]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+", type=int)
    ap.add_argument("--window", type=int, default=1)
    ap.add_argument("--max-lines", type=int, default=30)
    a = ap.parse_args()
    c = vc.connect()
    for cid in a.ids:
        show(c, cid, a.window, a.max_lines)


if __name__ == "__main__":
    main()
