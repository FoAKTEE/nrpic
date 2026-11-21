"""K8 seeds from the brief itself (brief 12.8): the labelled statements of its main text.

Brief 12.8: "Import the labelled statements of the main text of this document one by one into
the `claims` table as seeds: [VERIFIED] as abstract or title_only according to the level noted
in the text; [BACKGROUND] as background; [JUDGEMENT] as judgement; [TO VERIFY] as to_verify."

The brief is read by script, never by eye (as `kbtool.brief` and `kbtool.meta_brief16` do):

    main text    the sections "## N." with N in MAIN_SECTIONS (1 to 10 and 15). Section 0 is the
                 legend of the labels, 11 to 14 are instructions for the sessions (harness, the
                 knowledge base, git, prompts), 16 and 17 the reference list and the manifests.
                 Fenced code blocks are skipped. Section 15 ("Items for the agents to verify or
                 complete") labels its items by its heading: an item without a label of its own
                 is a to_verify seed (bracket IMPLICIT_BRACKET).
    label        a bracket that holds VERIFIED, BACKGROUND, JUDGEMENT or TO VERIFY ("[VERIFIED:
                 abstracts]", "[titles VERIFIED]", "[BACKGROUND; defer to the original]",
                 "[JUDGEMENT + TO VERIFY]", ...). The first keyword decides the family:
                 VERIFIED (or "title(s) ... verified") -> title_only when the bracket names
                 titles, else abstract; BACKGROUND -> background; JUDGEMENT -> judgement (also
                 "JUDGEMENT + TO VERIFY": a judgement is never upgraded, brief 12.8);
                 TO VERIFY -> to_verify.
    mention      a bracket right after "marked" or "labelled" names a label and labels nothing
                 (line 1751, item 7 of section 15: "Quantitative statements marked [BACKGROUND]").
    statement    every labelled line of the main text is a block of its own (checked: no
                 labelled line continues onto a neighbour), so the unit is the line.
                 Table row: the row. Heading: the heading. Bullet or paragraph, for the k-th
                 label of the line:
                 - inside a bold lead-in ("**Name [VERIFIED].** ..."): the lead-in and the text
                   after it up to the next label;
                 - followed by a colon ("... [all VERIFIED]: a, b, c"): from the start of its
                   sentence to the next label;
                 - written after the full stop of its sentence ("... . [JUDGEMENT]"): the text
                   since the previous label (the whole block when it is the only label);
                 - otherwise (inside its sentence): that sentence, from its start (not before
                   the previous label) to its end (not after the next label).
    paper id     the first arXiv id of the statement (all of them in claim_meta.evidence).
    track tags   from the section: section 2 core; S1 A-emd-pbh, S2 B-emd-gw, S3 C-sidm,
                 S4 D-bh-dress, S11 E-stoch-inf, S12 F-hills (section 5); the track sheets 9.3
                 to 9.9; 3.10 and 3.11, whose headings name Tracks E and F. Otherwise the tracks
                 that use the cited ids: the tracks whose claims (wave-1 notes, requests) cite
                 the paper, and the track sheets 9.4 to 9.9 that cite it.
    origin       claims.origin 'brief v2 L<n>'; claim_meta.seed_key 'brief:v2:L<n>:<k>' (k-th
                 label of the line), origin_path the brief file, origin_commit its sha256.

Seeding is idempotent: a seed whose key exists is never touched again (its label may have been
changed by `kb claim verify`/`refute`). Seeds get label_set_by 'kb-claims_brief (12.8 map)',
which also makes `kb claim seed --rebuild` refuse (claims_cli.rebuild_refused), so the rebuild
of the wave-1 seed cannot remove them.

Also here (wave 3, package tracks/kb/claims_brief):
    parse_check()   the CHECK.md tables of the brief-check packages (branch kb/brief-check)
    join_rows()     each CHECK.md row to a seed, by brief line, label and quotation
    DEFECTS         defects of cited papers (coord/BRIEF_ERRATA.md section 5 and the requests
                    of the brief-check reports), entered as a refuted claim of the printed
                    statement plus, where the evidence gives the right value, a claim that
                    supersedes it
    annotate(), add_defect(), recheck_defects()   database writes, only on claims created here

Standard library only; files under kb-data/raw are read as text and never executed.
"""
import difflib
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field

from . import claims_db as _cdb
from .claims_parse import RE_ID

BRIEF_NAME = "einstein_vlasov_pic_cosmology_agent_brief.en.md"
ORIGIN_REF = "brief v2"
BY_DEFAULT = "kb-claims_brief"
LABEL_SET_BY = "kb-claims_brief (12.8 map)"
SEED_PREFIX = "brief:v2:"
DEFECT_PREFIX = "brief-defect:"
MAIN_SECTIONS = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15})

RE_BRACKET = re.compile(r"\[([^\[\]]*?(?:VERIFIED|BACKGROUND|JUDGEMENT|JUDGMENT|TO VERIFY|[Vv]erified)[^\[\]]*?)\]")
RE_SECTION = re.compile(r"^## (\d+)\.\s*(.*)$")
RE_SUB = re.compile(r"^#{3,4}\s+(.*)$")
RE_BULLET = re.compile(r"^(\s*(?:[-*+]|\d+[.)])\s+)")
# a sentence ends at . ! ? followed by space and a capital, a quote, a bracket or bold; not
# after an initial, a usual abbreviation, or inside "et al."
RE_SENT_END = re.compile(r"(?<=[.!?])(?:\*\*)?[)\"'’”]?(?:\*\*)?\s+(?=[A-Z\"“‘(\[*`])")
ABBREV = ("al.", "e.g.", "i.e.", "cf.", "Fig.", "Figs.", "Eq.", "Eqs.", "Ref.", "Refs.", "vs.", "Sec.", "Secs.",
          "No.", "approx.", "resp.", "Phys.", "Rev.", "Lett.", "Astrophys.", "J.", "Mon.", "Not.", "Dr.", "St.")

IMPLICIT_SECTION = 15         # "Items for the agents to verify or complete"
IMPLICIT_BRACKET = "TO VERIFY (implicit: heading of section 15)"
RE_ITEM = re.compile(r"^\d+[.)]\s+")
RE_MENTION = re.compile(r"\b(?:marked|labell?ed)\s*(?:as\s*)?$", re.I)
RE_THIS_TABLE = re.compile(r"\b(?:this|the above|the preceding) table\b", re.I)

SECTION_TRACKS = {          # section or subsection key -> tracks (module docstring)
    "2": ("core",), "S1": ("A-emd-pbh",), "S2": ("B-emd-gw",), "S3": ("C-sidm",), "S4": ("D-bh-dress",),
    "S11": ("E-stoch-inf",), "S12": ("F-hills",), "9.3": ("core",), "9.4": ("A-emd-pbh",),
    "9.5": ("B-emd-gw",), "9.6": ("C-sidm",), "9.7": ("D-bh-dress",), "9.8": ("E-stoch-inf",),
    "9.9": ("F-hills",), "3.10": ("E-stoch-inf",), "3.11": ("F-hills",),
}
SHEETS = {"9.4": "A-emd-pbh", "9.5": "B-emd-gw", "9.6": "C-sidm", "9.7": "D-bh-dress", "9.8": "E-stoch-inf",
          "9.9": "F-hills"}


# ------------------------------------------------------------------ labels
def label_of(bracket):
    """(family, db label, level) of the text inside a label bracket, or None."""
    t = bracket.strip()
    up = t.upper()
    keys = [(up.find(k), k) for k in ("VERIFIED", "BACKGROUND", "JUDGEMENT", "JUDGMENT", "TO VERIFY")
            if up.find(k) >= 0]
    if not keys:
        return None
    # "TO VERIFY" contains no "VERIFIED"; "titles VERIFIED" starts with titles: VERIFIED family
    first = min(keys)[1]
    if first in ("BACKGROUND",):
        return "BACKGROUND", "background", "background"
    if first in ("JUDGEMENT", "JUDGMENT"):
        return "JUDGEMENT", "judgement", "judgement"
    if first == "TO VERIFY":
        return "TO VERIFY", "to_verify", "to_verify"
    if re.search(r"\btitles?\b", t, re.I):
        return "VERIFIED", "title_only", "title"
    return "VERIFIED", "abstract", "abstract"


def _strip_md(s):
    s = s.replace("**", "")
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)\*(?![\w*])", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def _clean(s):
    s = _strip_md(s)
    s = re.sub(r"^[;,.:\s|]+", "", s)
    return s.strip()


def sentence_starts(text):
    """Offsets where a sentence starts (0 included)."""
    out = [0]
    for m in RE_SENT_END.finditer(text):
        before = text[:m.start() + 1]
        tok = before.split()[-1] if before.split() else ""
        tok = tok.rstrip(")\"'’”*")
        if tok in ABBREV or re.fullmatch(r"[A-Z]\.", tok) or re.fullmatch(r"(?:[A-Z]\.){2,}", tok):
            continue
        out.append(m.end())
    return out


# ------------------------------------------------------------------ statements
@dataclass
class BriefStatement:
    line: int
    ordinal: int              # k-th label of the line (1-based)
    bracket: str              # the label as written, without brackets
    family: str               # VERIFIED, BACKGROUND, JUDGEMENT, TO VERIFY
    label: str                # db label
    level: str                # abstract, title, background, judgement, to_verify
    section: int
    section_title: str
    subsection: str           # '3.3 Late universe ...', 'S1 ...', 'M3 ...' or ''
    unit: str                 # row, heading, bullet, para
    rule: str                 # lead-in, colon, after-stop, sentence, row, heading
    span: tuple               # (start, end) offsets of the statement in the line
    text: str                 # the statement (the brief's wording, markdown removed)
    ids: list = field(default_factory=list)
    tracks: list = field(default_factory=list)
    line_end: int = 0         # last line the statement covers (a label before a list: its items)
    line_start: int = 0       # first line it covers (a statement about "this table": the table)

    @property
    def subkey(self):
        m = re.match(r"^(\d+\.\d+|S\d+|M\d+)\b", self.subsection or "")
        return m.group(1) if m else ""

    def seed_key(self):
        return f"{SEED_PREFIX}L{self.line}:{self.ordinal}"

    def kind(self):
        t = self.text.lower()
        if self.label == "to_verify":
            return "open_question"
        if re.search(r"\b(?:does not|not found|cannot|limitation|caveat|fails?)\b", t):
            return "limitation"
        if re.search(r"\d\.\d|10\^|10⁻|\d+e[-+]?\d|×\s*10", t):
            return "number"
        return "result"


def _unit_kind(line):
    if line.lstrip().startswith("|"):
        return "row"
    if line.startswith("#"):
        return "heading"
    if RE_BULLET.match(line):
        return "bullet"
    return "para"


def _statements_of_line(line, lineno):
    """[(ordinal, bracket, rule, (start, end))] for the labels of one line."""
    ms = list(RE_BRACKET.finditer(line))
    # a label named, not applied ("statements marked [BACKGROUND]", "labelled [TO VERIFY]")
    ms = [m for m in ms if label_of(m.group(1)) and not RE_MENTION.search(line[:m.start()])]
    if not ms:
        return []
    kind = _unit_kind(line)
    out = []
    if kind in ("row", "heading"):
        start = len(line) - len(line.lstrip("|# ").lstrip()) if kind == "heading" else 0
        for k, m in enumerate(ms, 1):
            out.append((k, m.group(1), kind, (start, len(line))))
        return out
    mb = RE_BULLET.match(line)
    body0 = mb.end() if mb else 0
    starts = [body0 + s for s in sentence_starts(line[body0:])]

    def sent_start(pos, lo):
        return max([s for s in starts if s <= pos] + [lo])

    prev_end = body0
    for k, m in enumerate(ms, 1):
        lo = max(ms[k - 2].end() if k > 1 else body0, prev_end)
        # a later label's statement starts at the start of its own sentence
        nxt_start = max(sent_start(ms[k].start(), m.end()), m.end()) if k < len(ms) else len(line)
        before = line[body0:m.start()]
        after = line[m.end():]
        # bold lead-in that opens the block and holds the label ("**Name [VERIFIED].** ...")
        lead = before.startswith("**") and before.count("**") == 1
        if lead:
            span, rule = (lo, nxt_start), "lead-in"
        elif re.match(r"\s*\**\s*:", after):
            span, rule = (max(sent_start(m.start(), lo), lo), nxt_start), "colon"
        elif re.search(r"[.!?][)\"'’”]?\**\s*$", line[lo:m.start()].rstrip()) or not line[lo:m.start()].strip():
            span, rule = (lo, m.end()), "after-stop"
        else:
            nxt = [x for x in starts if x > m.end()]
            end = nxt[0] if nxt else len(line)
            if k < len(ms) and ms[k].start() < end:       # the next label is in the same sentence
                end = m.end()
                while end < len(line) and line[end] in ".,;:":
                    end += 1
            span, rule = (max(sent_start(m.start(), lo), lo), end), "sentence"
        out.append((k, m.group(1), rule, span))
        prev_end = span[1]
    return out


def _table_before(lines, i):
    """1-based line numbers of the table that ends just above line i (blank lines allowed)."""
    j = i - 2                                # lines[j] is line j+1, the line above line i
    while j >= 0 and not lines[j].strip():
        j -= 1
    out = []
    while j >= 0 and lines[j].lstrip().startswith("|"):
        out.append(j + 1)
        j -= 1
    return sorted(out)


def _list_after(lines, i):
    """1-based line numbers of the list that follows line i (a label before a colon at the
    end of a line labels the items below it): consecutive bullet lines, blank lines between
    items allowed, up to the first other block."""
    out = []
    j = i                                   # lines[j] is line j+1
    while j < len(lines):
        t = lines[j]
        if RE_BULLET.match(t):
            out.append(j + 1)
        elif t.strip() == "":
            if out:
                nxt = next((x for x in lines[j + 1:j + 3] if x.strip()), "")
                if not RE_BULLET.match(nxt):
                    break
        else:
            break
        j += 1
    return out


def extract(path):
    """(statements, info): every labelled statement of the main text, and counts of all
    labels by section (main text or not) for the record."""
    blob = open(path, "rb").read()
    lines = blob.decode("utf-8").split("\n")
    sha = hashlib.sha256(blob).hexdigest()
    sec, sec_title, sub = None, "", ""
    fence = False
    out = []
    per_section = {}
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = RE_SECTION.match(line)
        if m:
            sec, sec_title, sub = int(m.group(1)), m.group(2).strip(), ""
        else:
            ms = RE_SUB.match(line)
            if ms and sec is not None:
                sub = RE_BRACKET.sub("", ms.group(1)).strip()
        found = _statements_of_line(line, i)
        if not found and sec == IMPLICIT_SECTION and RE_ITEM.match(line):
            # section 15 ("Items for the agents to verify or complete"): an unlabelled item is
            # labelled by the heading
            found = [(1, IMPLICIT_BRACKET, "item", (RE_BULLET.match(line).end(), len(line)))]
        if not found:
            continue
        per_section[sec] = per_section.get(sec, 0) + len(found)
        if sec not in MAIN_SECTIONS:
            continue
        for k, bracket, rule, (a, b) in found:
            fam, lab, level = label_of(bracket)
            seg = line[a:b]
            text = _clean(seg)
            line_end = i
            if rule == "row":
                cells = [_strip_md(c) for c in line.strip().strip("|").split("|")]
                text = " | ".join(c for c in cells if c)
            line_start = i
            if rule in ("sentence", "after-stop") and RE_THIS_TABLE.search(seg):
                tab = _table_before(lines, i)
                if tab:
                    line_start = tab[0]
                    rule += "+table"
            if rule == "colon" and not line[b:].strip() and re.search(r":\**\s*$", line):
                items = _list_after(lines, i)
                if items:
                    seg = seg + " " + " ".join(lines[x - 1] for x in items)
                    text = _clean(line[a:b]) + " " + " ".join(_clean(RE_BULLET.sub("", lines[x - 1])) for x in items)
                    line_end = items[-1]
                    rule = "colon+list"
            ids = list(dict.fromkeys(mm.group(1) for mm in RE_ID.finditer(seg)))
            out.append(BriefStatement(line=i, ordinal=k, bracket=bracket, family=fam, label=lab, level=level,
                                      section=sec, section_title=sec_title, subsection=sub, unit=_unit_kind(line),
                                      rule=rule, span=(a, b), text=text, ids=ids, line_end=line_end,
                                      line_start=line_start))
    info = {"brief_sha256": sha, "lines": len(lines), "labels_by_section": per_section,
            "main_sections": sorted(MAIN_SECTIONS)}
    return out, info


def sheet_ids(path):
    """{arXiv id: {tracks}} cited in the track sheets 9.4 to 9.9 of the brief."""
    lines = open(path, encoding="utf-8").read().split("\n")
    cur, out = None, {}
    for line in lines:
        ms = re.match(r"^###\s+(\d+\.\d+)\b", line)
        if ms:
            cur = SHEETS.get(ms.group(1))
            continue
        if line.startswith("## "):
            cur = None
        if cur:
            for mm in RE_ID.finditer(line):
                out.setdefault(mm.group(1), set()).add(cur)
    return out


def track_usage(con):
    """{paper id: {tracks}} from the claims of the tracks (seeds of their notes, requests),
    without the claims seeded from the brief."""
    out = {}
    if con is None:
        return out
    try:
        rows = con.execute("SELECT c.paper_id, m.track FROM claims c JOIN claim_meta m USING(claim_id) "
                           "WHERE c.paper_id IS NOT NULL AND m.seed_key NOT LIKE ? AND m.seed_key NOT LIKE ?",
                           (SEED_PREFIX + "%", DEFECT_PREFIX + "%")).fetchall()
    except Exception:                                    # no claim tables yet
        return out
    known = {"A-emd-pbh", "B-emd-gw", "C-sidm", "D-bh-dress", "E-stoch-inf", "F-hills", "core"}
    for pid, t in rows:
        if t in known:
            out.setdefault(pid, set()).add(t)
    return out


def assign_tracks(statements, usage, sheets):
    for s in statements:
        key = s.subkey if s.subkey in SECTION_TRACKS else str(s.section)
        if key in SECTION_TRACKS:
            s.tracks = list(SECTION_TRACKS[key])
            continue
        tr = set()
        for pid in s.ids:
            tr |= usage.get(pid, set()) | sheets.get(pid, set())
        s.tracks = sorted(tr)
    return statements


def seed_rows(statements):
    """Rows of the dry-run table."""
    return [{"seed_key": s.seed_key(), "line": s.line, "lines": f"{s.line_start or s.line}-{max(s.line_end, s.line)}",
             "ordinal": s.ordinal, "section": s.section,
             "subsection": s.subsection, "unit": s.unit, "rule": s.rule, "bracket": s.bracket, "label": s.label,
             "kind": s.kind(), "paper_id": s.ids[0] if s.ids else "", "ids": ",".join(s.ids),
             "tracks": ",".join(s.tracks), "span": f"{s.span[0]}-{s.span[1]}", "chars": len(s.text), "text": s.text}
            for s in statements]


# ------------------------------------------------------------------ database
def upsert(con, s, sha, by):
    """Insert one seed unless its key exists. Returns (claim_id, 'new' | 'same' | 'differs')."""
    key = s.seed_key()
    row = con.execute("SELECT m.claim_id, c.text FROM claim_meta m JOIN claims c USING(claim_id) WHERE m.seed_key=?",
                      (key,)).fetchone()
    if row:
        return row[0], ("same" if row[1] == s.text else "differs")
    now = _cdb.utcnow()
    origin = f"{ORIGIN_REF} L{s.line}"
    cur = con.execute(
        "INSERT INTO claims(text, kind, paper_id, locator, label, origin, track_tags) VALUES (?,?,?,?,?,?,?)",
        (s.text, s.kind(), s.ids[0] if s.ids else None, None, s.label, origin, ",".join(s.tracks) or None))
    cid = cur.lastrowid
    detail = {"ids": s.ids, "span": list(s.span), "lines": [s.line_start or s.line, max(s.line_end, s.line)],
              "unit": s.unit, "rule": s.rule, "level": s.level,
              "label_as_written": s.bracket}
    section = f"{s.section}. {s.section_title}" + (f" > {s.subsection}" if s.subsection else "")
    con.execute("INSERT INTO claim_meta(claim_id, seed_key, source_label, track, origin_ref, origin_commit, "
                "origin_path, origin_line, section, evidence, status, status_detail, label_set_by, checked_by, "
                "checked_at, seeded_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid, key, s.bracket, "brief", ORIGIN_REF, sha, BRIEF_NAME, s.line, section,
                 ("ids: " + ", ".join(s.ids)) if s.ids else "", "unlocated", json.dumps(detail), LABEL_SET_BY, by,
                 now, now))
    _cdb.event(con, cid, by, "seed", None, s.label, None, "unlocated", origin)
    return cid, "new"


def own_claim(con, cid):
    """True for a claim created by this module (seed of the brief or defect claim)."""
    r = con.execute("SELECT seed_key FROM claim_meta WHERE claim_id=?", (cid,)).fetchone()
    return bool(r and r[0] and (r[0].startswith(SEED_PREFIX) or r[0].startswith(DEFECT_PREFIX)))


def annotate(con, cid, by, evidence, status=None):
    """An outcome that changes no label: an event, and the evidence appended to claim_meta.
    Only on claims created here; optionally the status (e.g. 'located', 'partial')."""
    if not own_claim(con, cid):
        raise ValueError(f"claim {cid} was not created by claims_brief")
    old = con.execute("SELECT status, evidence FROM claim_meta WHERE claim_id=?", (cid,)).fetchone()
    if old[1] and evidence in old[1]:
        return False                                      # idempotent
    new_ev = (old[1] + " || " if old[1] else "") + evidence
    con.execute("UPDATE claim_meta SET evidence=?, checked_by=?, checked_at=?" + (", status=?" if status else "") +
                " WHERE claim_id=?", (new_ev, by, _cdb.utcnow()) + ((status,) if status else ()) + (cid,))
    _cdb.event(con, cid, by, "annotate", None, None, old[0], status or old[0], evidence)
    return True


# ------------------------------------------------------------------ CHECK.md of the brief check
CHECK_HEAD = "| # | Brief line | Quotation | Label | Verdict | Locator | Note |"
RE_TEXLOC = re.compile(r"(?P<key>(?:[a-z][a-z\-]*(?:\.[A-Z]{2})?_\d{7})|\d{4}\.\d{4,5})/(?P<ver>v\d+)/src/"
                       r"(?P<file>[^\s:`;,()]+?\.(?:tex|bbl|ltx|txt|sty|cls))"
                       r"(?::(?P<nums>\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*))?")


@dataclass
class CheckRow:
    package: str
    n: int
    brief_line: int
    quotation: str
    label_col: str
    verdict_raw: str
    locator_raw: str
    note: str
    md_line: int

    @property
    def verdict(self):
        v = self.verdict_raw.upper()
        if v.startswith("CORRECTED"):
            return "CORRECTED"
        if v.startswith("CONFIRMED (PRECISION"):
            return "PRECISION"
        if v.startswith("CONFIRMED"):
            return "CONFIRMED"
        if v.startswith("ANSWERED"):
            return "ANSWERED"
        if v.startswith("NOT FOUND"):
            return "NOT FOUND"
        return "OTHER"

    @property
    def label(self):
        """db label of the Label column, '' for unlabelled ('(unl.)', 'unl.')."""
        t = self.label_col.strip()
        if re.match(r"^\(?unl", t):
            return ""
        m = re.search(r"\[([^\]]+)\]", t)
        if m:
            lab = label_of(m.group(1) + " " + t[m.end():])
            return lab[1] if lab else ""
        lab = label_of(t.upper())
        return lab[1] if lab else ""

    def tex_locators(self):
        """[(paper id, version, file, a, b)] of the TeX locators of the row."""
        out = []
        for m in RE_TEXLOC.finditer(self.locator_raw):
            key = m.group("key")
            pid = key if re.match(r"\d", key) else key.replace("_", "/", 1)
            nums = m.group("nums")
            if not nums:
                continue
            for part in re.split(r"\s*,\s*", nums):
                mm = re.match(r"(\d+)(?:\s*[-–]\s*(\d+))?$", part.strip())
                if mm:
                    a = int(mm.group(1))
                    b = int(mm.group(2) or a)
                    out.append((pid, m.group("ver"), m.group("file"), min(a, b), max(a, b)))
        return out


def _cells(line):
    """Cells of a Markdown table row; '|' inside backticks does not split."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells, cur, tick = [], [], False
    for ch in s:
        if ch == "`":
            tick = not tick
        if ch == "|" and not tick:
            cells.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    cells.append("".join(cur).strip())
    return cells


def parse_check(md, package):
    """CheckRow of every row of the 7-column verdict tables of a CHECK.md; other tables
    (open-question status, candidates) are skipped. Returns (rows, problems)."""
    rows, problems = [], []
    lines = md.split("\n")
    in_t = False
    for i, line in enumerate(lines, 1):
        if line.strip() == CHECK_HEAD:
            in_t = True
            continue
        if not line.startswith("|"):
            in_t = False
            continue
        if not in_t or re.match(r"^\|[-| :]+\|$", line.strip()):
            continue
        c = _cells(line)
        if len(c) != 7:
            problems.append(f"{package} line {i}: {len(c)} cells")
            continue
        try:
            n, bl = int(c[0]), int(re.match(r"\d+", c[1]).group(0))
        except (ValueError, AttributeError):
            problems.append(f"{package} line {i}: row number or brief line not a number")
            continue
        rows.append(CheckRow(package, n, bl, c[2], c[3], c[4], c[5], c[6], i))
    return rows, problems


def _norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = s.replace("–", "-").replace("—", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"arxiv:", "", s)
    return re.sub(r"[^a-z0-9.\-+/= ]+", " ", re.sub(r"\s+", " ", s)).strip()


def quote_overlap(quotation, text):
    """Share of the quotation's characters (fragments between '...') found in text."""
    q = quotation.strip().strip('"“”')
    frags = [f for f in re.split(r"\.\.\.|…", q) if _norm(f)]
    t = _norm(text)
    if not frags:
        return 0.0
    tot = sum(len(_norm(f)) for f in frags)
    got = 0
    for f in frags:
        nf = _norm(f)
        if nf in t:
            got += len(nf)
        else:
            sm = difflib.SequenceMatcher(None, nf, t, autojunk=False)
            got += sum(b.size for b in sm.get_matching_blocks() if b.size >= 12)
    return min(1.0, got / max(tot, 1))


def join_rows(rows, statements, min_overlap=0.6):
    """[(row, statement or None, how, score)]. A row joins the seed of its brief line whose
    statement holds its quotation; a labelled row may join the only seed of its label on the
    line whatever the overlap."""
    by_line = {}
    for s in statements:
        for ln in range(s.line_start or s.line, max(s.line_end, s.line) + 1):
            by_line.setdefault(ln, []).append(s)
    out = []
    for r in rows:
        cands = by_line.get(r.brief_line, [])
        if not cands:
            out.append((r, None, "no seed on the line", 0.0))
            continue
        scored = sorted(((quote_overlap(r.quotation, s.text), s) for s in cands), key=lambda x: -x[0])
        lab = r.label
        same = [(sc, s) for sc, s in scored if lab and s.label == lab]
        if same and (same[0][0] >= min_overlap or len(same) == 1):
            out.append((r, same[0][1], "label and quotation" if same[0][0] >= min_overlap else "only seed of its label",
                        same[0][0]))
        elif scored[0][0] >= min_overlap:
            out.append((r, scored[0][1], "quotation", scored[0][0]))
        else:
            out.append((r, None, "quotation outside the labelled statements", scored[0][0]))
    return out


# ------------------------------------------------------------------ defects of cited papers
@dataclass
class Defect:
    key: str                      # stable id: brief-defect:<key>:printed / :right
    row: str                      # the row it comes from ('BRIEF_ERRATA 5.11', 'report s37_38', ...)
    paper_id: str
    printed: str                  # the paper's printed statement, our wording
    printed_loc: str              # locator string of the printed statement
    evidence: str                 # run id and/or locator of the counter-evidence
    right: str = ""               # the right value, our wording ('' = none)
    right_loc: str = ""
    right_label: str = "judgement"   # fulltext (read at the locator) or judgement (computed)
    kind: str = "number"
    tracks: str = ""
    existing: str = ""            # claims of other writers that hold the same finding
    refute: bool = True           # False: a fact recorded without a printed statement to refute


def defect_rows():
    """The DEFECTS table at the end of this module."""
    return list(DEFECTS)


RE_RAWLOC = re.compile(r"^kb-data/raw/arxiv/(?P<key>[^/]+)/(?P<ver>v\d+)/src/(?P<file>.+?):L(?P<a>\d+)(?:-(?P<b>\d+))?$")


def parse_any_locator(text):
    """Locator parts of a defect: '<id><vN>:<file>:L<a>-<b>' or the raw-store form
    'kb-data/raw/arxiv/<key>/<vN>/src/<file>:L<a>-<b>'; other parts (meta:..., runs) are kept as
    written and not resolved. Returns [(paper id, version, file, a, b, raw)] and [other]."""
    tex, other = [], []
    for part in (p.strip() for p in (text or "").split(";") if p.strip()):
        m = _cdb.RE_LOC.match(part)
        if m:
            a = int(m.group("a"))
            tex.append((m.group("pid"), m.group("ver") or "", m.group("file").strip(), a, int(m.group("b") or a), part))
            continue
        m = RE_RAWLOC.match(part)
        if m:
            key = m.group("key")
            pid = key if re.match(r"\d", key) else key.replace("_", "/", 1)
            a = int(m.group("a"))
            tex.append((pid, m.group("ver"), m.group("file"), a, int(m.group("b") or a), part))
            continue
        other.append(part)
    return tex, other


def in_database(con, pid):
    r = con.execute("SELECT version FROM papers WHERE paper_id=?", (pid,)).fetchone() if con else None
    return r[0] if r else None


def resolve_parts(con, store, tex):
    """[(raw, resolved_in_db, problem, LocResult or None)] for TeX locator parts."""
    from .claims_parse import Locator
    out = []
    for pid, ver, f, a, b, raw in tex:
        r = store.resolve(Locator(pid, ver, f, a, b, raw, 0))
        dbv = in_database(con, pid)
        ok = bool(r.resolved and dbv)
        prob = r.problem if not r.resolved else ("" if dbv else "paper not in the database")
        out.append((raw, ok, prob, r))
    return out


def write_locator_rows(con, cid, parts):
    con.execute("DELETE FROM claim_locators WHERE claim_id=?", (cid,))
    for k, (raw, ok, prob, r) in enumerate(parts):
        con.execute("INSERT INTO claim_locators(claim_id, ord, paper_id, version, file, line_start, line_end, "
                    "written, resolved, problem, flat_start, flat_end, chunk_ids_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, k, r.paper_id, r.version, r.file, r.line_start, r.line_end, raw, int(ok), prob,
                     r.flat_start if ok else None, r.flat_end if ok else None,
                     json.dumps(r.chunk_ids if ok else [])))


def add_defect(con, d, store, by):
    """The printed statement (refuted) and, where given, the right value (supersedes it).
    Idempotent by key. Returns {'printed': (cid, what), 'right': (cid, what) or None}."""
    res = {}
    now = _cdb.utcnow()

    def one(part, text, loc, label, kind, supersedes=None, evidence=""):
        key = f"{DEFECT_PREFIX}{d.key}:{part}"
        row = con.execute("SELECT claim_id FROM claim_meta WHERE seed_key=?", (key,)).fetchone()
        if row:
            return row[0], "same"
        tex, _other = parse_any_locator(loc)
        parts = resolve_parts(con, store, tex)
        # 'checked' only for a passage read for this claim (fulltext); a judgement or a record-level
        # claim whose locators resolve is 'located'
        status = ("refuted" if label == "refuted" else
                  ("checked" if label == "fulltext" else "located") if parts and all(p[1] for p in parts) else
                  "unresolved" if parts else "unlocated")
        cur = con.execute("INSERT INTO claims(text, kind, paper_id, locator, label, origin, track_tags, verified_by, "
                          "verified_at, supersedes) VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (text, kind, d.paper_id, loc or None, label, f"defects of cited papers: {d.row}",
                           d.tracks or None, by if label in ("fulltext", "refuted") else None,
                           now if label in ("fulltext", "refuted") else None, supersedes))
        cid = cur.lastrowid
        detail = {"row": d.row, "evidence": d.evidence, "existing": d.existing,
                  "locators_in_db": [p[1] for p in parts], "problems": [p[2] for p in parts if p[2]]}
        con.execute("INSERT INTO claim_meta(claim_id, seed_key, source_label, track, origin_ref, origin_path, section, "
                    "evidence, status, status_detail, label_set_by, checked_by, checked_at, seeded_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, key, label.upper(), "kb", "wave 3", "coord/BRIEF_ERRATA.md", d.row, evidence, status,
                     json.dumps(detail), by, by, now, now))
        write_locator_rows(con, cid, parts)
        _cdb.event(con, cid, by, "add", None, label, None, status, evidence)
        if label == "refuted":
            _cdb.event(con, cid, by, "refute", None, "refuted", None, "refuted", d.evidence)
        return cid, "new"

    ev_p = f"refuted by {d.evidence}" + (f"; same finding in claims {d.existing}" if d.existing else "")
    if d.refute:
        res["printed"] = one("printed", d.printed, d.printed_loc, "refuted", d.kind, None, ev_p)
    else:
        res["printed"] = one("fact", d.printed, d.printed_loc, d.right_label, d.kind, None, d.evidence)
    res["right"] = None
    if d.right:
        res["right"] = one("right", d.right, d.right_loc, d.right_label, d.kind, res["printed"][0],
                           f"{d.evidence}; supersedes claim {res['printed'][0]}")
    return res


def recheck_defects(con, store, by):
    """Resolve again the locators of the defect claims that were left unresolved (papers not
    yet in the database); a claim whose locators now all resolve becomes 'checked'."""
    out = []
    for cid, key, status, loc in con.execute("SELECT m.claim_id, m.seed_key, m.status, c.locator FROM claim_meta m "
                                             "JOIN claims c USING(claim_id) WHERE m.seed_key LIKE ? ORDER BY claim_id",
                                             (DEFECT_PREFIX + "%",)).fetchall():
        tex, _ = parse_any_locator(loc)
        if not tex:
            continue
        parts = resolve_parts(con, store, tex)
        ok = all(p[1] for p in parts)
        write_locator_rows(con, cid, parts)
        new = status
        if status == "unresolved" and ok:
            lab = con.execute("SELECT label FROM claims WHERE claim_id=?", (cid,)).fetchone()[0]
            new = "checked" if lab == "fulltext" else "located"
            con.execute("UPDATE claim_meta SET status=?, checked_by=?, checked_at=? WHERE claim_id=?",
                        (new, by, _cdb.utcnow(), cid))
            _cdb.event(con, cid, by, "check", None, None, status, new, "locators now in the database")
        out.append((cid, key, new, ok, [p[2] for p in parts if p[2]]))
    return out


# ------------------------------------------------------------------ the defects (step 3)
# coord/BRIEF_ERRATA.md section 5 has 17 rows (r1 to r17 in the order of the table; r11 to r17
# are the section-5 rows of the brief-check ERRATA_ROWS.md files on kb/brief-check 476a1763),
# and the reports of the brief check (scratch/orch/wave3a_reports/kb.md) ask for three more
# claims (q1 to q3). Texts are our wording. Labels of the right values: fulltext only where the
# value is printed at the locator and was read by kb-claims_brief; judgement where it was
# computed (a run, arithmetic) or read from a figure; abstract where it comes from a metadata
# record (the brief's [VERIFIED] level). `existing` names claims of other writers with the
# same finding (not changed here).
_E = "coord/BRIEF_ERRATA.md section 5"
DEFECTS = [
    Defect("r1-2108.11967-table1", f"{_E} r1", "2108.11967",
           "Table 1 of arXiv:2108.11967 prints the compactness C = 1.41053e-2 in the row w(0) = 0.3 and "
           "p(0) = 1.09378e-3 in the row w(0) = 1.1 of the b = 0.1 block, and C = 4.00960e-4 in the row "
           "w(0) = 0.05 of the next block.",
           "2108.11967v2:main.tex:L491; 2108.11967v2:main.tex:L493; 2108.11967v2:main.tex:L516",
           "run C-sidm-20261115-120722-38ab057; arithmetic on the printed columns by kb-claims_brief",
           "In the same rows M/R = 3.29993e-2/2.892 = 1.141e-2 (w(0) = 0.3) and 3.87808e-2/9.672 = 4.010e-3 "
           "(w(0) = 0.05): C is misprinted (a digit transposition and a factor 10); p(0) at w(0) = 1.1 is "
           "about 1.09e-2 judging by the neighbouring rows.",
           "2108.11967v2:main.tex:L491; 2108.11967v2:main.tex:L493; 2108.11967v2:main.tex:L516",
           "judgement", "number", "C-sidm", "309, 610, 611, 612"),
    Defect("r1-2108.11967-e2phi", f"{_E} r1", "2108.11967",
           "The metric function of arXiv:2108.11967, e^{2 Phi(r)} as printed at main.tex:197, is the one "
           "behind its tabulated equilibria.",
           "2108.11967v2:main.tex:L197",
           "run C-sidm-20261115-120722-38ab057: the printed e^{2 Phi} is not consistent with the tabulated "
           "numbers", kind="method", tracks="C-sidm", existing=""),
    Defect("r2-gr-qc0601112-Zc", f"{_E} r2", "gr-qc/0601112",
           "arXiv:gr-qc/0601112 defines the central redshift as Z_c = 1/sqrt(alpha(0)) - 1 (ssevnum7.tex:694), "
           "the definition behind its tables.",
           "gr-qc/0601112v1:ssevnum7.tex:L694",
           "run C-sidm-20261115-121626-e99907d",
           "The tables of arXiv:gr-qc/0601112 are reproduced only with Z_c = 1/alpha(0) - 1.",
           "gr-qc/0601112v1:ssevnum7.tex:L694", "judgement", "definition", "C-sidm", "257, 328, 614"),
    Defect("r2-gr-qc0601112-table3", f"{_E} r2", "gr-qc/0601112",
           "Table 3 of arXiv:gr-qc/0601112 lists Z_c = 0.045 and 0.052 between the rows 0.42 and 0.77.",
           "gr-qc/0601112v1:ssevnum7.tex:L809-813",
           "run C-sidm-20261115-121626-e99907d; the first column increases down the table (L809-813)",
           "The two entries of Table 3 of arXiv:gr-qc/0601112 read Z_c = 0.45 and 0.52.",
           "gr-qc/0601112v1:ssevnum7.tex:L811-812", "judgement", "number", "C-sidm", "615"),
    Defect("r3-1101.3097-b-footnote", f"{_E} r3", "1101.3097",
           "The footnote of arXiv:1101.3097 on the conduction constant says that astro-ph/0110561 used "
           "b = 25 sqrt(pi)/(32 sqrt 6) = 1.002 and that the value should be 25 pi/32.",
           "1101.3097v2:sidm1.tex:L411-412",
           "read at the sources by kb-claims_brief: astro-ph/0110561 prints 25 pi/(32 sqrt 6) = 1.002 "
           "(SIDMGT_Xiv2.tex:394); 25 sqrt(pi)/(32 sqrt 6) = 0.565, and 25 pi/32 = 2.45 differs from the "
           "paper's own b = 25 sqrt(pi)/32 = 1.38 (sidm1.tex:410)",
           "Two values of the conduction constant are in use: b = 25 sqrt(pi)/32 = 1.38 (arXiv:1101.3097, "
           "arXiv:2601.17117) and b = 25 pi/(32 sqrt 6) = 1.002 (astro-ph/0110561).",
           "1101.3097v2:sidm1.tex:L410; 2601.17117v2:SIDM_MS.tex:L233; astro-ph/0110561v2:SIDMGT_Xiv2.tex:L393-394",
           "fulltext", "number", "C-sidm", "317, 320, 616, 618"),
    Defect("r4-2502.06783-eq17", f"{_E} r4", "2502.06783",
           "Eq. (17) of arXiv:2502.06783 builds the initial momentum perturbation of the field with the term "
           "-sqrt(2 eps1) H Mpl Psi_G (main_V2PRD.tex:320), for data in the geodesic gauge the paper uses.",
           "2502.06783v3:main_V2PRD.tex:L318-321",
           "run E-stoch-inf-20261115-123146-82d2fd4; tracks/E-stoch-inf/spec/SPEC.md 5.3",
           "In the geodesic gauge (main_V2PRD.tex:490) the term -sqrt(2 eps1) H Mpl Psi_G vanishes; the "
           "initial data need -sqrt(2 eps1) Mpl H Psi_B, and with the printed term the linear Hamiltonian "
           "residual is 4 eps1^2 H^3 a^2 k^-2 dR/dt.",
           "2502.06783v3:main_V2PRD.tex:L318-321; 2502.06783v3:main_V2PRD.tex:L490",
           "judgement", "method", "E-stoch-inf", "603"),
    Defect("r5-2502.06783-draw", f"{_E} r5", "2502.06783",
           "arXiv:2502.06783 normalises the Gaussian draws of its initial noise by the prefactors printed at "
           "main_V2PRD.tex:876-884 in front of the inverse real FFT (the first line reduces to dk^(3/2)).",
           "2502.06783v3:main_V2PRD.tex:L876-884",
           "run E-stoch-inf-20261115-122934-9ac98d8: the printed prefactor gives (2 pi)^3 too much power",
           "With the normalisation of the inverse FFT the draw prefactor must be L^(-3/2) (box side L).",
           "2502.06783v3:main_V2PRD.tex:L876-884", "judgement", "method", "E-stoch-inf", "604"),
    Defect("r5-2610.32592-draw", f"{_E} r5", "2610.32592",
           "The appendix of arXiv:2610.32592 normalises the Gaussian draws by (dk/sqrt(2 pi))^(3/2) in front of "
           "the inverse real FFT (appendix.tex:487-491).",
           "2610.32592v1:appendix.tex:L487-491",
           "run E-stoch-inf-20261115-122934-9ac98d8: the printed prefactor gives (2 pi)^(3/2) too much power",
           "With the normalisation of the inverse FFT the draw prefactor must be L^(-3/2) (box side L).",
           "2610.32592v1:appendix.tex:L487-491", "judgement", "method", "E-stoch-inf", "605"),
    Defect("r6-2206.11234-weight", f"{_E} r6", "2206.11234",
           "The importance-sampling weight of arXiv:2206.11234 carries the sign printed at method.tex:78 and, "
           "for a constant drift, :151.",
           "2206.11234v2:method.tex:L78; 2206.11234v2:method.tex:L151",
           "runs E-stoch-inf-20261115-125312-dafadc4, E-stoch-inf-20261115-125658-e3eaef3: the sign of the "
           "weight is wrong", kind="method", tracks="E-stoch-inf", existing="606"),
    Defect("r6-2206.11234-pole", f"{_E} r6", "2206.11234",
           "The appendix of arXiv:2206.11234 states that the leading pole Lambda_0 = v0/4 holds in general, "
           "beyond the large phi_UV limit (appendix.tex:168-173).",
           "2206.11234v2:appendix.tex:L168-173",
           "runs E-stoch-inf-20261115-125312-dafadc4, E-stoch-inf-20261115-125658-e3eaef3: v0/4 is not the "
           "leading pole in general", kind="result", tracks="E-stoch-inf", existing="607"),
    Defect("r7-2512.14649-friedmann", f"{_E} r7", "2512.14649",
           "arXiv:2512.14649 writes the Friedmann constraint as H^2 = V/(1 - pi^2/(6 Mpl^2)) (PRD_v2.tex:108).",
           "2512.14649v2:PRD_v2.tex:L108",
           "read at the source (E-stoch-inf; reread by kb-claims_brief)",
           "The Friedmann constraint of that model is H^2 = V/[3 Mpl^2 (1 - pi^2/(6 Mpl^2))]: the printed "
           "denominator lacks the factor 3 Mpl^2.",
           "2512.14649v2:PRD_v2.tex:L108", "judgement", "definition", "E-stoch-inf", "608"),
    Defect("r7-2512.14649-usr", f"{_E} r7", "2512.14649",
           "arXiv:2512.14649 puts the USR phase between N of about 3.5 and 8 and says the field passes a "
           "shallow maximum of the potential before the slow roll (PRD_v2.tex:534).",
           "2512.14649v2:PRD_v2.tex:L534",
           "read at the source by E-stoch-inf (coord/BRIEF_ERRATA.md section 5 r7); not rederived here",
           "The feature is an exact stationary inflection point at -sqrt(2) v, and the USR interval of the "
           "text is one e-fold later than the paper's own Fig. 1.",
           "2512.14649v2:PRD_v2.tex:L534", "judgement", "result", "E-stoch-inf", "609"),
    Defect("r8-1305.2619-prose", f"{_E} r8", "1305.2619",
           "arXiv:1305.2619 says the Gondolo-Silk spike is a factor of three below the relativistic one at its "
           "peak and that the 4Gm variant peaks about 15 per cent above it (SFWpaper.tex:443).",
           "1305.2619v1:SFWpaper.tex:L443",
           "run D-bh-dress-20261115-123029-4df1e76 (read off the paper's own Fig. 1)",
           "From the paper's own Fig. 1 the peak ratio is 2.59 and the excess of the 4Gm variant 9.2 per cent.",
           "1305.2619v1:SFWpaper.tex:L443", "judgement", "number", "D-bh-dress", "682"),
    Defect("r8-1305.2619-action", f"{_E} r8", "1305.2619",
           "The relativistic radial action of arXiv:1305.2619 (its Eq. (3.19), label Ir_rel; also Eq. (4.13)) "
           "is the canonical one of the Schwarzschild geodesic.",
           "1305.2619v1:SFWpaper.tex:L413-418",
           "run D-bh-dress-20261115-123029-4df1e76: the factor 1/(1 - 2Gm/r) of the canonical radial action is "
           "missing (+5.2 per cent at the spike peak)",
           "The canonical radial action carries the factor 1/(1 - 2Gm/r) in the integrand; without it the "
           "spike peak is off by 5.2 per cent.",
           "1305.2619v1:SFWpaper.tex:L413-418", "judgement", "method", "D-bh-dress", "679, 680"),
    Defect("r8-1305.2619-fig3", f"{_E} r8", "1305.2619",
           "Fig. 3 of arXiv:1305.2619 shows the spike for the black-hole mass m = 4e6 M_sun.",
           "1305.2619v1:SFWpaper.tex:L695-700",
           "run D-bh-dress-20261115-123029-4df1e76 (a 0.04 dex fit, [JUDGEMENT] of D-bh-dress)",
           "Fig. 3 of arXiv:1305.2619 corresponds to m = 1e6 M_sun.",
           "1305.2619v1:SFWpaper.tex:L695-700", "judgement", "number", "D-bh-dress", "681"),
    Defect("r9-1707.06302-boost", f"{_E} r9", "1707.06302",
           "arXiv:1707.06302 says the spike peak at spin 0.8 is about 35 per cent above that at 0.5 for the "
           "Hernquist profile, and about 20 per cent for the constant distribution (kerrdm.tex:929-931).",
           "1707.06302v2:kerrdm.tex:L929-931",
           "read from the paper's figures by D-bh-dress (coord/BRIEF_ERRATA.md section 5 r9)",
           "From the paper's figures the increases are about +45 and +14 per cent.",
           "1707.06302v2:kerrdm.tex:L929-931", "judgement", "number", "D-bh-dress", "683"),
    Defect("r10-2611.12831-L729", f"{_E} r10", "2611.12831",
           "arXiv:2611.12831 says particle communication and removal at block boundaries and at the outer "
           "boundaries of the domain are described in its section on the numerical implementation "
           "(main.tex:729, pointing to L673-698).",
           "2611.12831v1:main.tex:L729",
           "tracks/core/interfaces/SECTION2_CORRECTIONS.md section 4.2 (core); kb-claims_brief searched "
           "L673-698 for removal and outer boundaries: only the step order and particle excision are there",
           kind="method", tracks="core", existing=""),
    Defect("r11-2604.03628-jref", f"{_E} r11 (s310)", "2604.03628",
           "The arXiv record of arXiv:2604.03628 gives the journal reference Phys. Rev. D 111, 063518 (2025).",
           "meta:arxiv-api/2604.03628",
           "kb-data/meta/arxiv-api/2410.23942.json carries the same reference (it is that of the companion "
           "paper 2410.23942); kb-data/meta/inspire/2604.03628.json publication_info; s310 CHECK #42",
           "INSPIRE gives Phys. Rev. D 114 (2026) 6, 063530 for arXiv:2604.03628.",
           "meta:inspire/2604.03628", "abstract", "result", "E-stoch-inf", ""),
    Defect("r12-1203.6185-titles", f"{_E} r12 (s311)", "1203.6185",
           "arXiv:1203.6185 carries two titles and two author orders: on arXiv 'Perturbational treatment of the "
           "gravitational potential effect on binary black hole evolution' with Cao first (bbbhPRD.tex:8-14); "
           "the journal record J. Phys. Conf. Ser. 330, 012016 and INSPIRE also carry 'From binary black hole "
           "simulation to triple black hole simulation' with Bai first. A metadata divergence for the "
           "citation resolver, not an error of the paper.",
           "1203.6185v1:bbbhPRD.tex:L8-14; meta:inspire/1203.6185; meta:arxiv-api/1203.6185",
           "kb-data/meta/inspire/1203.6185.json (titles, authors); kb-data/meta/arxiv-api/1203.6185.json; "
           "package s311", right_label="abstract", kind="result", tracks="F-hills", existing="", refute=False),
    Defect("r13-1807.01711-abstract", f"{_E} r13 (s33)", "1807.01711",
           "The abstract of arXiv:1807.01711 gives the global backreaction energy density as of order 1e-8 of "
           "the matter energy density (INCAPRD2019.tex:106).",
           "1807.01711v2:INCAPRD2019.tex:L106",
           "read at the source by s33 (CHECK #3) and kb-claims_brief: INCAPRD2019.tex:524, :644",
           "The body of arXiv:1807.01711 gives, globally at z = 0, Omega_Q + Omega_L of about 1e-9 for the "
           "backreaction and Omega_R of about 1e-8 for the curvature; the abstract's 1e-8 is the curvature "
           "parameter.",
           "1807.01711v2:INCAPRD2019.tex:L524; 1807.01711v2:INCAPRD2019.tex:L644", "fulltext", "number",
           "B-emd-gw", ""),
    Defect("r14-2512.13673-abstract", f"{_E} r14 (s34_36)", "2512.13673",
           "The abstract of arXiv:2512.13673 pairs mu_crit of about 0.02 Mpl with r_crit of about 1e-6 "
           "(main.tex:80).",
           "2512.13673v1:main.tex:L80",
           "run kb-20261119-150703-95bba8b; Eq. (r) at main.tex:135 with N* = 60 gives 5.6e-6 (kb-claims_brief "
           "arithmetic: 16 pi (0.02)^2/60^2 = 5.59e-6)",
           "The body of arXiv:2512.13673 gives r_crit of about 5.6e-6 for mu_crit of about 0.020 Mpl "
           "(main.tex:114, :309), as Eq. (r) gives with N* = 60.",
           "2512.13673v1:main.tex:L114; 2512.13673v1:main.tex:L135; 2512.13673v1:main.tex:L309", "fulltext",
           "number", "E-stoch-inf", ""),
    Defect("r14-2512.13673-L276", f"{_E} r14 (s34_36)", "2512.13673",
           "arXiv:2512.13673 pairs mu_crit of about 0.025 and 0.020 Mpl (in-phase and out-of-phase data, in "
           "that order) with r_crit of about 5.6e-6 and 8.7e-6 respectively (main.tex:276).",
           "2512.13673v1:main.tex:L276",
           "run kb-20261119-150703-95bba8b; kb-claims_brief arithmetic with Eq. (r): 16 pi (0.025)^2/60^2 = "
           "8.73e-6",
           "By Eq. (r) of arXiv:2512.13673, mu_crit of about 0.025 Mpl (in-phase) gives r_crit of about 8.7e-6 "
           "and 0.020 Mpl (out-of-phase) gives 5.6e-6; the caption at main.tex:238 has the right order of the "
           "two branches.",
           "2512.13673v1:main.tex:L135; 2512.13673v1:main.tex:L238", "judgement", "number", "E-stoch-inf", ""),
    Defect("r15-2508.10070-variance", f"{_E} r15 (s35)", "2508.10070",
           "arXiv:2508.10070 calls sigma_0 and sigma_h the variance of the density contrast, and sigma_h^* the "
           "quantity that characterises that variance (main.tex:81, :322, :775).",
           "2508.10070v1:main.tex:L81; 2508.10070v1:main.tex:L322; 2508.10070v1:main.tex:L775",
           "read at the source by s35 and kb-claims_brief: the definition at main.tex:767; the group's "
           "2409.00435 main.tex:62",
           "With the definition sigma_j^2 = integral of d ln k k^(2j) P(k) (main.tex:767), sigma_0 and sigma_h "
           "are standard deviations, as 2409.00435 (main.tex:62) says of sigma_H; the abstract's beta of about "
           "A sigma_h^*5 is a fifth power of a standard deviation.",
           "2508.10070v1:main.tex:L767; 2409.00435v3:main.tex:L62", "fulltext", "definition", "A-emd-pbh", ""),
    Defect("r16-astro-ph0608642-MH", f"{_E} r16 (s5_s6)", "astro-ph/0608642",
           "arXiv:astro-ph/0608642 gives the horizon mass as M_H(T) of about 1 M_sun (T/100 MeV)^-2 "
           "(g_eff/10.75)^(-1/2) (ms.tex:197-198).",
           "astro-ph/0608642v1:ms.tex:L197-198",
           "run kb-20261119-154408-2b35ecd (panel b of fig_numbers.png): a factor 15 below M_H = c^3 t/G with "
           "the radiation-era t(T), 1e4 against 1.5e5 M_sun at 1 MeV",
           "With t of about 0.738 s (g*/10.75)^(-1/2) (T/1 MeV)^(-2) and M_H = c^3 t/G = 2.03e5 (t/1 s) M_sun "
           "(arXiv:2002.12778), the horizon mass at 1 MeV is about 1.5e5 M_sun.",
           "2002.12778v2:CKSY2021.tex:L276-291", "judgement", "number", "", ""),
    Defect("r17-2607.09326-abstract", f"{_E} r17 (s7_s8)", "2607.09326",
           "The abstract of arXiv:2607.09326 says that every near-flat initial data set on T^3 with positive "
           "energy density converges to a flat metric under the Einstein-Euler flow with a polytropic "
           "equation of state, with no condition on the index (main.tex:96).",
           "2607.09326v1:main.tex:L96",
           "read at the source by s7_s8 and kb-claims_brief: main.tex:141, :299-300",
           "The theorem of arXiv:2607.09326 holds for polytropic index n > 3 (main.tex:141, :300); the authors "
           "do not expect homogenisation for 0 < n < 3 (main.tex:300).",
           "2607.09326v1:main.tex:L141; 2607.09326v1:main.tex:L299-300", "fulltext", "result", "", ""),
    Defect("q1-2403.03470-burnett", "brief-check report (novelty): record Burnett's conjecture proven", "2403.03470",
           "Huneau and Luk (arXiv:2403.03470, Burnett's conjecture in generalized wave coordinates) prove the "
           "Burnett conjecture without symmetry assumptions or angular regularity; earlier proofs needed a U(1) "
           "symmetry (elliptic gauge) or angular regularity (double null gauge).",
           "2403.03470v1:wavecoordinate.arxiv.240305.tex:L116-125; 2403.03470v1:wavecoordinate.arxiv.240305.tex:L143",
           "read at the source by the novelty package and kb-claims_brief",
           right_label="fulltext", kind="result", tracks="", existing="", refute=False),
    Defect("q2-1903.01490-masses", "brief-check report (novelty): record the lattice horizon masses", "1903.01490",
           "In the numerical-relativity lattices of spinning black holes of arXiv:1903.01490 the irreducible "
           "and horizon masses stay constant during the evolution to a relative fluctuation of about 0.1 per "
           "cent, dominated by numerical uncertainty.",
           "1903.01490v2:spinning_BH_v2_CT.tex:L653-657",
           "read at the source by the novelty package and kb-claims_brief",
           right_label="fulltext", kind="number", tracks="D-bh-dress", existing="", refute=False),
    Defect("q3-2506.17641-seed", "brief-check report (s37_38): record both seed estimates", "2506.17641",
           "arXiv:2506.17641 v3 quotes M_GR/M_200 of about 1e-10 to 1e-8 for halos of 1e8 to 1e11 M_sun from "
           "Gad-Nasr et al. (sidmacc.tex:133) and reports that the full-GR non-equilibrium model gives "
           "M_GR/M_smfp of about 4e-6, a factor 10 above its own estimate, which it therefore calls "
           "conservative (sidmacc.tex:145).",
           "2506.17641v3:sidmacc.tex:L133; 2506.17641v3:sidmacc.tex:L145",
           "read at the source by s37_38 (CHECK #34) and kb-claims_brief",
           right_label="fulltext", kind="number", tracks="C-sidm", existing="", refute=False),
]
