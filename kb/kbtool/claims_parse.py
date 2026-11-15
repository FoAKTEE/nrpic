"""K8 seeds: statements with locators in the tracks' notes, parsed into claim records.

The tracks wrote their verified statements in wave 1 as Markdown (scope/REFERENCES.md and
equivalents), each with locators into the stored arXiv source, in several styles:

    (L264-268)  (abstract L173-174)       Track A, core's SECTION2_CORRECTIONS (2611.12831)
    (879-882)   (abstract 52-72; method 235-357)    Tracks B and C (bare line numbers)
    (main.tex:103-118)  `SIDM_MS.tex:233`  (`:60-74`, `:412-419`)    C, D, tables of C's report
    (`TBH3.tex` lines 582-626)   `template.tex` lines 45, 80          Track F
    2502.06783 main_V2PRD.tex:320          errata requests (paper id before the file)

This module only parses text; it reads nothing from kb-data and resolves nothing (that is
`claims_check`). A note is cut into units (bullets with their continuation lines, table
rows, paragraphs), each unit into claims at its locators: the text from the end of the
previous locator to the end of this one is one claim. An evidence label in brackets
([VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]) before the first locator is the
unit's label; a bracket after a locator that holds JUDGEMENT or TO VERIFY becomes a claim
of its own (the inference of the track, not the paper's statement); a trailing [VERIFIED
...] confirms the claim before it. Units without any label take the note's default label
(Tracks B and C state in their headers that every statement was read at the locator).

Pure functions, standard library only; tested in tests/test_claims_parse.py.
"""
import hashlib
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- patterns
NEW_ID = r"\d{4}\.\d{4,5}"
OLD_ID = (r"(?:astro-ph|gr-qc|hep-th|hep-ph|hep-lat|math-ph|nucl-th|quant-ph|physics|cond-mat|math)"
          r"(?:\.[A-Z]{2})?/\d{7}")
ARXIV_ID = rf"(?:{OLD_ID}|{NEW_ID})"
RE_ID = re.compile(rf"(?<![\w./])(?:arXiv:)?({ARXIV_ID})(?:\s*\(?\s*(v\d+)\)?)?(?![\w])")
RE_LABEL = re.compile(r"\[(VERIFIED|BACKGROUND|JUDGEMENT|JUDGMENT|TO VERIFY)\b([^\]]*)\]")
NUM = r"\d{1,5}"
RANGE = rf"{NUM}(?:\s*[-–]\s*L?{NUM})?"
NUMLIST = rf"{RANGE}(?:\s*,\s*{RANGE})*"
SRC_EXT = r"(?:tex|bbl|ltx|txt|sty|cls)"
FILE = rf"[A-Za-z0-9_][A-Za-z0-9_./+-]*\.{SRC_EXT}"
FILE_ANY = r"[A-Za-z_][A-Za-z0-9_./+-]*\.[A-Za-z][A-Za-z0-9]{0,7}"
RE_SRC_EXT = re.compile(rf"\.{SRC_EXT}$")

# file-qualified: `file.tex:12-14`, file.tex:12, `file.tex` lines 1-3, `file.tex` abstract, line 129
RE_FILE_LOC = re.compile(
    rf"`?(?P<file>{FILE_ANY})`?\s*(?:"
    rf":(?P<colon>{NUMLIST}(?:\s*,\s*{NUMLIST})*)"
    rf"|(?:\s*[a-z]{{0,12}},?\s*)?(?:lines?|l\.)\s*(?P<words>{NUMLIST}))")
# same file as the context: (`:60-74`, `:412-419`) or `:67`
RE_COLON_LOC = re.compile(rf"(?:(?<=`)|(?<=\()|(?<=\s)|(?<=,)):(?P<colon>{RANGE}(?:\s*,\s*{RANGE})*)`?")
# Lnnn forms: L264-268, L1101- 1103, L45-L47
RE_L_LOC = re.compile(rf"(?<![A-Za-z0-9_])L(?P<l>{NUM}(?:\s*[-–]\s*L?{NUM})?)(?![\d.])")
# bare line numbers in parentheses (styles B and C): (879-882), (274), (abstract 52-72; method 235-357)
PREFIXW = r"(?:abstract|caption|captions|method|methods|appendix|app\.|table|tables|footnote|text|conclusions?|introduction|intro|lines?|eq\.?|fig\.?)"
RE_BARE_PAREN = re.compile(
    rf"\((?P<inner>(?:{PREFIXW}\s*,?\s*)?{NUMLIST}(?:\s*;\s*(?:{PREFIXW}\s*,?\s*)?{NUMLIST})*)\)")
# lines 173-175 outside parentheses (style B "Abstract: lines 173-175"), not "brief lines"
RE_COLON_BARE = re.compile(rf"(?<=[A-Za-z_)]):\s+(?P<nums>{NUMLIST})(?=\s*[.;]|\s*$)")
RE_LINES_WORD = re.compile(rf"(?<![`\w])lines?\s+(?P<words>{NUMLIST})")
RE_BRIEF_BEFORE = re.compile(r"(brief|CHARTER|section|charter|SCOPE|sheet)\W{0,3}(\w+\W{0,3}){0,2}$", re.I)

# paths of this repository (evidence of the tracks, not paper locators)
REPO_PATH = re.compile(r"^(?:paper|docs|athenak|cosmo|notes|tracks|problems|python|coord|harness|kb|refs|scripts)/")
RE_BULLET = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
RE_TABLE = re.compile(r"^\s*\|")
RE_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}")
RE_BACKTICK_TEX = re.compile(rf"`({FILE})`")
RE_NUMBERTOKEN = re.compile(r"[-+]?\d")

LABEL_NORM = {"VERIFIED": "VERIFIED", "BACKGROUND": "BACKGROUND", "JUDGEMENT": "JUDGEMENT",
              "JUDGMENT": "JUDGEMENT", "TO VERIFY": "TO VERIFY"}


@dataclass
class Locator:
    """One locator as written: a line range of a file of a paper's source."""
    paper_id: str            # arXiv id as written or from the context ('' when unknown)
    version: str             # 'v2' or '' when the note does not say
    file: str                # file name relative to src/ ('' = the context's main file)
    line_start: int
    line_end: int
    raw: str                 # the locator text as written
    pos: int                 # offset in the unit text (end of the match)
    alt_ids: tuple = ()      # other ids of the unit, tried when the file is not in paper_id

    def key(self):
        return f"{self.paper_id}{self.version and ':' + self.version}:{self.file}:{self.line_start}-{self.line_end}"


@dataclass
class ClaimSeed:
    text: str                # our tracks' wording (never paper text)
    label: str               # VERIFIED, VERIFIED-implicit, BACKGROUND, JUDGEMENT, TO VERIFY
    locators: list           # [Locator]
    paper_id: str            # main paper of the claim ('' if none)
    origin_path: str         # file the statement was read from (repository path)
    origin_ref: str          # branch or commit the file was read at
    origin_line: int         # first line of the unit in that file (1-based)
    track: str               # owner id that wrote it
    section: str = ""        # heading path within the note
    kind: str = "result"
    evidence: str = ""       # bracket text, run ids
    extra: dict = field(default_factory=dict)

    def seed_key(self):
        """Stable identity across re-seeding: origin file, normalized text, locators."""
        norm = re.sub(r"\s+", " ", self.text).strip().lower()
        h = hashlib.sha1()
        h.update(self.origin_path.encode())
        h.update(b"\0" + norm.encode())
        h.update(b"\0" + ";".join(l.key() for l in self.locators).encode())
        return h.hexdigest()[:20]


@dataclass
class SourceSpec:
    """One note to seed from, with the conventions of its writer."""
    track: str
    ref: str                 # git ref (branch) the note is read at
    path: str                # path inside the repository
    default_label: str = ""  # label of statements that carry none ('' = skip unlabelled units)
    bare_numbers: bool = False   # (879-882) means lines of the context file
    lines_word: bool = True      # "lines 173-175" means lines of the context file
    fixed_paper: tuple = ()      # (id, version, main file) when the whole note is about one paper
    only_sections: tuple = ()    # heading prefixes to keep ('' = all)
    l_form: bool = True
    kind_hint: str = ""          # 'erratum' for defect reports
    note: str = ""


# ---------------------------------------------------------------- helpers
def _ranges(numlist):
    """'879-882, 890' -> [(879, 882), (890, 890)]; 'L1101- 1103' handled by caller."""
    out = []
    for part in re.split(r"\s*,\s*", numlist.strip()):
        part = part.strip().lstrip("L")
        if not part:
            continue
        m = re.match(rf"({NUM})(?:\s*[-–]\s*L?({NUM}))?$", part)
        if not m:
            continue
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if b < a:                                   # '1101-03' style shorthand
            sa, sb = str(a), str(b)
            if len(sb) < len(sa):
                b = int(sa[:len(sa) - len(sb)] + sb)
        if b < a:
            a, b = b, a
        out.append((a, b))
    return out


def norm_label(raw):
    return LABEL_NORM.get(raw.upper().replace("JUDGMENT", "JUDGEMENT"), raw.upper())


def heading_context(text):
    """(paper id, version, main file) named in a heading or a bold paper line, else None."""
    m = RE_ID.search(text)
    if not m:
        return None
    pid, ver = m.group(1), (m.group(2) or "")
    if not ver:                                       # "2403.15126 (v1)" or "arXiv:x v2,"
        mv = re.search(rf"{re.escape(pid)}\s*\(?\s*(v\d+)", text)
        ver = mv.group(1) if mv else ""
    mf = RE_BACKTICK_TEX.search(text)
    return pid, ver, (mf.group(1) if mf else "")


# ---------------------------------------------------------------- units
@dataclass
class Unit:
    text: str
    line: int                # 1-based first line in the note
    kind: str                # 'bullet', 'row', 'para'
    section: str
    ctx: tuple               # (paper id, version, main file) in force


def units(md, spec):
    """Cut a note into units with the paper context in force at each."""
    lines = md.split("\n")
    out = []
    ctx = spec.fixed_paper or ("", "", "")
    heads = []
    cur = None
    in_code = False
    table_versions = {}                       # id -> version from table rows "| id (vN) |"

    def flush():
        nonlocal cur
        if cur is not None and cur["text"].strip():
            out.append(Unit(cur["text"].strip(), cur["line"], cur["kind"], " > ".join(heads), cur["ctx"]))
        cur = None

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        mh = RE_HEADING.match(line)
        if mh:
            flush()
            level = len(mh.group(1))
            heads[:] = heads[:level - 1] + [mh.group(2).strip()]
            while len(heads) < level:
                heads.insert(0, "")
            if not spec.fixed_paper:
                hc = heading_context(mh.group(2))
                if hc:
                    pid, ver, f = hc
                    ctx = (pid, ver or table_versions.get(pid, ""), f)
                elif level <= 2:
                    ctx = ("", "", "")
            continue
        if not line.strip():
            flush()
            continue
        if RE_TABLE.match(line):
            flush()
            if RE_TABLE_SEP.match(line.strip().strip("|").strip() or "---") and set(line.strip()) <= set("|-: "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            mt = re.match(rf"^({ARXIV_ID})\s*\((v\d+)\)", cells[0]) if cells else None
            if mt:
                table_versions[mt.group(1)] = mt.group(2)
            out.append(Unit(" | ".join(cells), i, "row", " > ".join(h for h in heads if h), ctx))
            continue
        mb = RE_BULLET.match(line)
        if mb:
            flush()
            body = line[mb.end():]
            uctx = ctx
            if not spec.fixed_paper:                   # Track F: "**arXiv:2406.11985** (...)"
                mbold = re.match(rf"\*\*(?:arXiv:)?({ARXIV_ID})\*\*", body.strip())
                if mbold:
                    hc = heading_context(body)
                    uctx = (hc[0], hc[1] or table_versions.get(hc[0], ""), hc[2]) if hc else uctx
            cur = {"text": body, "line": i, "kind": "bullet", "ctx": uctx}
            continue
        if cur is not None:
            cur["text"] += " " + line.strip()
        else:
            cur = {"text": line.strip(), "line": i, "kind": "para", "ctx": ctx}
    flush()
    return [u for u in out if not spec.only_sections or any(u.section.startswith(p) or p in u.section
                                                            for p in spec.only_sections)]


# ---------------------------------------------------------------- locators
def _join_hyphen_breaks(text):
    return re.sub(r"(\d)\s*[-–]\s+(L?\d)", r"\1-\2", text)


def find_locators(text, ctx, spec):
    """All locators of a unit, in order of their end position."""
    text = _join_hyphen_breaks(text)
    pid0, ver0, file0 = ctx
    found = []
    taken = []                                         # spans already used

    def free(a, b):
        return all(b <= s or a >= e for s, e in taken)

    ids = [(m.start(), m.group(1), m.group(2) or "") for m in RE_ID.finditer(text)]
    unit_ids = tuple(dict.fromkeys(i for _, i, _ in ids))

    def paper_before(pos, with_pos=False):
        """Nearest arXiv id written before pos in the unit (errata, C's table rows)."""
        best = None
        for s, i, v in ids:
            if s < pos:
                best = (i, v, s) if with_pos else (i, v)
        return best

    for m in RE_FILE_LOC.finditer(text):
        nums = m.group("colon") or m.group("words")
        if REPO_PATH.match(m.group("file")) or not RE_SRC_EXT.search(m.group("file")):
            taken.append((m.start(), m.end()))         # a file of this repository, not of a paper
            continue
        pb = paper_before(m.start())
        pid, ver = (pb if pb else (pid0, ver0))
        if pid == pid0 and not ver:
            ver = ver0
        rngs = []
        for chunk in re.split(r"\s*,\s*", nums):
            rngs += _ranges(chunk)
        for a, b in rngs:
            found.append(Locator(pid, ver, m.group("file"), a, b, m.group(0), m.end(),
                                 tuple(i for i in unit_ids if i != pid) + ((pid0,) if pid0 and pid0 != pid else ())))
        taken.append((m.start(), m.end()))
    # a later "`:412-419`" after a file-qualified locator in the same unit means that file
    for m in RE_COLON_LOC.finditer(text):
        if not free(m.start(), m.end()):
            continue
        prev_files = [l for l in found if l.pos <= m.start()]
        pb = paper_before(m.start(), with_pos=True)
        if prev_files and (not pb or pb[2] < prev_files[-1].pos):
            pid, ver, f = prev_files[-1].paper_id, prev_files[-1].version, prev_files[-1].file
        elif pb and pb[0] != pid0:
            pid, ver, f = pb[0], pb[1], ""                 # "astro-ph/0111176 `:289-291`": its main file
        else:
            pid, ver, f = pid0, ver0, file0
        for a, b in _ranges(m.group("colon")):
            found.append(Locator(pid, ver, f, a, b, m.group(0), m.end(), unit_ids))
        taken.append((m.start(), m.end()))
    if spec.l_form:
        for m in RE_L_LOC.finditer(text):
            if not free(m.start(), m.end()):
                continue
            for a, b in _ranges(m.group("l").replace("L", "")):
                found.append(Locator(pid0, ver0, file0, a, b, m.group(0), m.end(), unit_ids))
            taken.append((m.start(), m.end()))
    if spec.lines_word:
        for m in RE_LINES_WORD.finditer(text):
            if not free(m.start(), m.end()):
                continue
            if RE_BRIEF_BEFORE.search(text[max(0, m.start() - 30):m.start()]):
                continue
            if re.search(r"`[^`]+`\s*\S{0,6}\s*\(?$", text[max(0, m.start() - 40):m.start()]):
                taken.append((m.start(), m.end()))        # lines of a repository file named just before
                continue
            prev_files = [l for l in found if l.pos <= m.start() and l.file]
            pb = paper_before(m.start(), with_pos=True)
            if prev_files and (not pb or pb[2] < prev_files[-1].pos):
                pid, ver, f = prev_files[-1].paper_id, prev_files[-1].version, prev_files[-1].file
            else:
                pid, ver = (pb[:2] if pb else (pid0, ver0))
                f = file0 if pid == pid0 else ""
            for a, b in _ranges(m.group("words")):
                found.append(Locator(pid, ver, f, a, b, m.group(0), m.end(), unit_ids))
            taken.append((m.start(), m.end()))
    if spec.bare_numbers:
        for m in RE_COLON_BARE.finditer(text):
            if not free(m.start(), m.end()):
                continue
            for a, b in _ranges(m.group("nums")):
                if a >= 10:
                    found.append(Locator(pid0, ver0, file0, a, b, m.group(0), m.end(), unit_ids))
            taken.append((m.start(), m.end()))
        for m in RE_BARE_PAREN.finditer(text):
            if not free(m.start(), m.end()):
                continue
            inner = m.group("inner")
            if RE_BRIEF_BEFORE.search(text[max(0, m.start() - 30):m.start()]):
                continue
            for part in inner.split(";"):
                part = re.sub(rf"^\s*{PREFIXW}\s*,?\s*", "", part.strip())
                for a, b in _ranges(part):
                    if b < 10 and a == b:                # "(1)", "(2)": item numbers, not lines
                        continue
                    found.append(Locator(pid0, ver0, file0, a, b, m.group(0), m.end(), unit_ids))
            taken.append((m.start(), m.end()))
    found.sort(key=lambda l: l.pos)
    return text, found


# ---------------------------------------------------------------- segmentation
def _kind(text, spec, label):
    t = text.lower()
    if spec.kind_hint == "erratum" or re.search(r"\btypo|\berratum|\bmisprint|not consistent|should be", t):
        return "limitation"
    if label == "TO VERIFY":
        return "open_question"
    if re.search(r"not computed|caveat|not stated|limitation|does not|no (?:horizon|black-hole) mass|fails?\b", t):
        return "limitation"
    if re.search(r"^\s*(set-up|setup|method|gauge|matter|initial|numerical|model)\b", t):
        return "method"
    if re.search(r"\bdefin(ed|ition)\b", t):
        return "definition"
    if re.search(r"\d\.\d|\d+e[-+]?\d|10\^", t):
        return "number"
    return "result"


def _clean(s):
    s = s.strip()
    s = re.sub(r"^[;,.:\s]+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def split_unit(u, spec, origin_ref):
    """Claims of one unit."""
    text, locs = find_locators(u.text, u.ctx, spec)
    labels = [(m.start(), m.end(), norm_label(m.group(1)), m.group(0)) for m in RE_LABEL.finditer(text)]
    first_loc = locs[0].pos if locs else len(text)
    if not locs and (len({l[2] for l in labels}) >= 2 or re.search(r"\bLabels?\b", text)):
        return []                                         # the note's legend of the labels
    lead = [l for l in labels if l[0] < first_loc]
    unit_label = lead[0][2] if lead else ""
    if not unit_label and locs:
        late = [l for l in labels if l[2] in ("VERIFIED", "BACKGROUND")]
        if late:
            unit_label = late[0][2]                       # label written after the locator (table rows)
    if not unit_label and not locs:
        lab_any = labels[0][2] if labels else ""
        if not lab_any:
            return []                                     # unlabelled prose without locators
        unit_label = lab_any
    if not unit_label:
        unit_label = (spec.default_label + "-implicit") if spec.default_label == "VERIFIED" else spec.default_label
        if not unit_label:
            # no default: a unit with locators but no label keeps them as to-verify
            unit_label = "UNLABELLED"
    pid_main = u.ctx[0]
    out = []

    def emit(seg, label, seg_locs, evidence=""):
        seg_c = _clean(seg)
        if len(re.sub(r"[\W\d_]+", "", seg_c)) < 3 and not seg_locs:
            return
        pid = seg_locs[0].paper_id if seg_locs else pid_main
        out.append(ClaimSeed(text=seg_c, label=label, locators=list(seg_locs), paper_id=pid,
                             origin_path=spec.path, origin_ref=origin_ref, origin_line=u.line,
                             track=spec.track, section=u.section, kind=_kind(seg_c, spec, label),
                             evidence=evidence))

    if not locs:
        emit(text, unit_label, [])
        return out

    # group locators that end at the same place or are separated only by punctuation
    groups = []
    for l in locs:
        if groups and l.pos - len(l.raw) < groups[-1][-1].pos:
            groups[-1].append(l)                          # several ranges of one locator ("lines 185, 269-277")
            continue
        gap = text[groups[-1][-1].pos:l.pos - len(l.raw)] if groups else None
        # same group: only punctuation between, or a few words inside one parenthesis
        # ("(abstract L78-79; criterion L315-331)")
        if gap is not None and (re.fullmatch(r"[\s,;()`]*", gap) or
                                (re.fullmatch(r"[\s;,]+[A-Za-z][A-Za-z .]{0,24}", gap) and
                                 text.rfind("(", 0, l.pos) > text.rfind(")", 0, l.pos - len(l.raw)))):
            groups[-1].append(l)
        else:
            groups.append([l])
    prev = 0
    carry = ""                                          # row text before a first prefix locator
    for gi, g in enumerate(groups):
        gstart = g[0].pos - len(g[0].raw)
        end = g[-1].pos
        # include a closing parenthesis right after the locator
        while end < len(text) and text[end] in ")`":
            end += 1
        if re.match(r"\s*:", text[end:]) and gstart >= prev:
            # prefix style "L1340: t_m = 64.15625 M; L1360: ...": the statement follows
            left = text[prev:gstart]
            if len(re.sub(r"[\W\d_]+", "", left)) > 3:
                if out and len(_clean(left)) < 200:
                    out[-1].text = _clean(out[-1].text + " " + left)
                else:
                    carry = left
            nxt = (groups[gi + 1][0].pos - len(groups[gi + 1][0].raw)) if gi + 1 < len(groups) else len(text)
            mstop = re.search(r"[;|]", text[end:nxt])
            stop = end + mstop.start() if mstop else nxt
            lab_in = [l for l in labels if gstart <= l[0] < stop and l[2] in ("JUDGEMENT", "TO VERIFY")]
            emit(carry + " " + text[gstart:stop], lab_in[0][2] if lab_in else unit_label, g)
            carry = ""
            prev = stop
            continue
        seg = text[prev:end]
        seg_label = unit_label
        inner = [l for l in labels if prev <= l[0] < end]
        for s, e, lab, raw in inner:
            if s > prev + 2 and lab in ("JUDGEMENT", "TO VERIFY") and e <= end:
                # an inline judgement inside the segment: the segment is the track's inference
                seg_label = lab
            elif lab != unit_label and s <= prev + 2:
                seg_label = lab
        # trailing bracket right after the locator(s): attach or split
        rest = text[end:]
        mt = re.match(r"\s*[.;,]?\s*(\[(VERIFIED|BACKGROUND|JUDGEMENT|JUDGMENT|TO VERIFY)\b[^\]]*\])", rest)
        evidence = ""
        if mt:
            lab = norm_label(mt.group(2))
            if lab == "VERIFIED":
                evidence = mt.group(1)
                seg_label = "VERIFIED"
                end += mt.end()
                emit(seg, seg_label, g, evidence)
            else:
                if seg_label != lab:
                    emit(seg, seg_label, g)
                emit(seg + " " + mt.group(1), lab, g, mt.group(1))
                end += mt.end()
        else:
            emit(seg, seg_label, g)
        prev = end
    tail = text[prev:]
    if _clean(tail):
        tl = RE_LABEL.search(tail)
        if tl:
            emit(tail, norm_label(tl.group(1)), [], tl.group(0))
        elif out and len(_clean(tail)) < 200:
            out[-1].text = _clean(out[-1].text + " " + tail)
        elif len(re.sub(r"[\W\d_]+", "", tail)) > 20:
            emit(tail, unit_label if not unit_label.startswith("VERIFIED") else "UNLOCATED", [])
    return out


def strip_front_matter(md):
    """Drop the YAML front matter of an outbox message (kept as blank lines, so that line
    numbers stay those of the file); 'body:' is removed from the first body line."""
    lines = md.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines[:i + 1] = [""] * (i + 1)
                break
    for i, l in enumerate(lines):
        if l.startswith("body:"):
            lines[i] = l[len("body:"):].lstrip()
            break
    return "\n".join(lines)


def parse_note(md, spec, origin_ref):
    """All claims of a note."""
    md = strip_front_matter(md)
    out = []
    for u in units(md, spec):
        out += split_unit(u, spec, origin_ref)
    return out


# ---------------------------------------------------------------- the seed sources of wave 1
def wave1_sources():
    """The notes the tracks wrote in wave 1 with statements read at the source.
    E-stoch-inf and F-hills have no scope/REFERENCES.md: F's novelty note is parsed; E's
    statements with locators are its errata request, transcribed in claims_curated (with
    C's defect request)."""
    return [
        SourceSpec("A-emd-pbh", "track/A-emd-pbh", "tracks/A-emd-pbh/scope/REFERENCES.md",
                   default_label="", bare_numbers=False, lines_word=True),
        SourceSpec("B-emd-gw", "track/B-emd-gw", "tracks/B-emd-gw/scope/REFERENCES.md",
                   default_label="VERIFIED", bare_numbers=True, lines_word=True,
                   note="header: every statement was read at the locator"),
        SourceSpec("C-sidm", "track/C-sidm", "tracks/C-sidm/scope/REFERENCES.md",
                   default_label="VERIFIED", bare_numbers=True, lines_word=True,
                   note="header: all sources read at the source; labels as in SCOPE.md"),
        SourceSpec("C-sidm", "track/C-sidm", "tracks/C-sidm/stage/G0/REPORT.md",
                   default_label="VERIFIED", bare_numbers=False, lines_word=False,
                   only_sections=("6. Key references",),
                   note="section 6: read by the lead at the source (kb-request index-locators-typos)"),
        SourceSpec("D-bh-dress", "track/D-bh-dress", "tracks/D-bh-dress/scope/REFERENCES.md",
                   default_label="", bare_numbers=False, lines_word=True),
        SourceSpec("F-hills", "track/F-hills", "tracks/F-hills/novelty/NOVELTY.md",
                   default_label="VERIFIED", bare_numbers=False, lines_word=True,
                   note="F has no scope/REFERENCES.md; the novelty search is its read-at-source note; "
                        "header: [VERIFIED] read in the source at the locator given"),
        SourceSpec("core", "main", "tracks/core/interfaces/SECTION2_CORRECTIONS.md",
                   default_label="VERIFIED", bare_numbers=False, lines_word=False,
                   fixed_paper=("2611.12831", "v1", "main.tex"),
                   note="Lnnn = lines of 2611.12831 v1 main.tex ('every locator Lnnn below is a line of "
                        "that file'); 'lines' there are brief lines"),
    ]
