"""Minimal parser for matplotlib-1.5 EPS output (data only, nothing executed).

Walks the body after %%EndProlog and records
  strokes : polylines with colour, dash, linewidth, clip box
  markers : '/o {...} bind def' bodies and their 'X Y o' instances (ticks)
  texts   : glyph runs after 'X Y translate' (tick labels, legend text)
All coordinates are in PostScript points of the page after the initial
'18 180 translate' (i.e. the same frame as the clipbox numbers).
"""
import re
import sys
import json

NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'

GLYPH = {'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
         'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
         'period': '.', 'minus': '-', 'hyphen': '-', 'space': ' ',
         'comma': ',', 'parenleft': '(', 'parenright': ')', 'equal': '=',
         'plus': '+', 'slash': '/', 'greater': '>', 'less': '<',
         'bar': '|', 'multiply': 'x', 'approxequal': '~'}


def gname(g):
    if g in GLYPH:
        return GLYPH[g]
    if len(g) == 1:
        return g
    return '{%s}' % g


def parse(path):
    with open(path, 'r', errors='replace') as f:
        lines = f.read().split('\n')
    try:
        i0 = next(i for i, s in enumerate(lines) if s.startswith('%%EndProlog'))
    except StopIteration:
        i0 = 0
    st = dict(color=(0., 0., 0.), dash=(), lw=1.0, clip=None, tx=(0., 0.),
              font=None, size=None)
    stack = []
    strokes, fills, markers, texts = [], [], [], []
    cur = []          # current path: list of subpaths
    mdefs = {}        # name -> body lines
    in_def = None
    def_body = []
    text = None       # current text block
    i = i0
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        if in_def is not None:
            if s.startswith('} bind def'):
                mdefs[in_def] = list(def_body)
                in_def = None
            else:
                def_body.append(s)
            continue
        if not s:
            continue
        m = re.match(r'^/(\w+) \{$', s)
        if m:
            in_def = m.group(1)
            def_body = []
            continue
        toks = s.split()
        op = toks[-1]
        args = toks[:-1]
        try:
            nums = [float(a) for a in args]
        except ValueError:
            nums = None
        if op == 'gsave':
            stack.append(dict(st))
            if text is not None:
                pass
        elif op == 'grestore':
            if text is not None and text.get('depth') == len(stack):
                texts.append(text)
                text = None
            st = stack.pop() if stack else st
        elif op == 'setrgbcolor':
            st['color'] = tuple(nums)
        elif op == 'setgray':
            st['color'] = (nums[0],) * 3
        elif op == 'setlinewidth':
            st['lw'] = nums[0]
        elif op == 'setdash':
            m = re.match(r'^\[(.*)\]\s+(' + NUM + r')\s+setdash$', s)
            st['dash'] = tuple(float(x) for x in m.group(1).split()) if m else ()
        elif op == 'clipbox' and nums is not None:
            st['clip'] = tuple(nums)       # w h x y
        elif op == 'm' and nums is not None:
            cur.append([(nums[0], nums[1])])
        elif op == 'l' and nums is not None:
            if not cur:
                cur.append([])
            cur[-1].append((nums[0], nums[1]))
        elif op == 'c' and nums is not None:
            cur[-1].append((nums[4], nums[5]))
        elif op == 'cl':
            if cur and cur[-1]:
                cur[-1].append(cur[-1][0])
        elif op == 'stroke':
            for sp in cur:
                if len(sp) >= 2:
                    strokes.append(dict(pts=sp, color=st['color'], dash=st['dash'],
                                        lw=st['lw'], clip=st['clip'], line=i))
            cur = []
        elif op == 'fill':
            for sp in cur:
                fills.append(dict(pts=sp, color=st['color'], clip=st['clip'], line=i))
            cur = []
        elif op == 'newpath':
            cur = []
        elif op == 'translate' and nums is not None:
            # text block origin (marker defs are handled separately)
            text = dict(x=nums[0], y=nums[1], depth=len(stack), runs=[], rot=0.0, line=i)
        elif op == 'rotate' and nums is not None and text is not None:
            text['rot'] = nums[0]
        elif op == 'scalefont' and nums is not None:
            st['size'] = nums[0]
        elif op == 'moveto' and nums is not None and text is not None:
            text['pen'] = (nums[0], nums[1])
        elif op == 'glyphshow' and text is not None:
            g = args[-1].lstrip('/')
            if len(args) == 4 and args[2] == 'm':
                text['pen'] = (float(args[0]), float(args[1]))
            text['runs'].append((gname(g), st['size'], text.get('pen', (0, 0))))
        elif op == 'o' and nums is not None and len(nums) == 2:
            # marker instance; find the most recent def named o
            body = mdefs.get('o', [])
            markers.append(dict(x=nums[0], y=nums[1], body=body,
                                color=st['color'], line=i))
        elif op == 'box' and nums is not None:
            pass
    return dict(strokes=strokes, fills=fills, markers=markers, texts=texts)


def text_string(t):
    """Reconstruct a label: superscripts (smaller font, raised) in ^{}."""
    runs = t['runs']
    if not runs:
        return ''
    base = max(r[1] or 0 for r in runs)
    out = ''
    sup = False
    for ch, size, pen in runs:
        small = size is not None and base and size < 0.9 * base
        if small and not sup:
            out += '^{'
            sup = True
        elif not small and sup:
            out += '}'
            sup = False
        out += ch
    if sup:
        out += '}'
    return out


def tick_markers(markers):
    """Return list of (x, y, dx, dy) for markers whose body is a single segment."""
    res = []
    for mk in markers:
        b = ' '.join(mk['body'])
        mm = re.search(r'0 0 m\s+(' + NUM + r') (' + NUM + r') l', b)
        if mm:
            res.append((mk['x'], mk['y'], float(mm.group(1)), float(mm.group(2))))
    return res


if __name__ == '__main__':
    d = parse(sys.argv[1])
    print('strokes', len(d['strokes']), 'markers', len(d['markers']), 'texts', len(d['texts']))
    clips = {}
    for k, s in enumerate(d['strokes']):
        xs = [p[0] for p in s['pts']]
        ys = [p[1] for p in s['pts']]
        print('%3d L%5d c=(%.3f,%.3f,%.3f) dash=%s lw=%.2f clip=%s n=%4d x[%.2f,%.2f] y[%.2f,%.2f]' % (
            k, s['line'], *s['color'], s['dash'], s['lw'], s['clip'], len(xs),
            min(xs), max(xs), min(ys), max(ys)))
    print('--- ticks (x, y, dx, dy)')
    for t in tick_markers(d['markers']):
        print('  %.4f %.4f %g %g' % t)
    print('--- texts')
    for t in d['texts']:
        print('  (%.2f, %.2f) rot=%g  %r' % (t['x'], t['y'], t['rot'], text_string(t)))


# ---------------------------------------------------------------- calibration
def label_value(lbl):
    """'10^{-2}' -> 0.01, '-10^{0}' -> -1, '0.2' -> 0.2, '0' -> 0. None if not numeric."""
    s = lbl.replace(' ', '')
    m = re.match(r'^(-?)10\^\{(-?\d+)\}$', s)
    if m:
        return (-1 if m.group(1) else 1) * 10.0 ** int(m.group(2))
    try:
        return float(s)
    except ValueError:
        return None


def axis_ticks(d, clip):
    """Return dict with 'x' and 'y' lists of (pos, value, label) for major ticks
    on the bottom / left spines of the axes whose clipbox is `clip` (w h x y)."""
    w, h, x0, y0 = clip
    ticks = []
    for mk in d['markers']:
        b = ' '.join(mk['body'])
        mm = re.search(r'0 0 m\s+(' + NUM + r') (' + NUM + r') l', b)
        if mm:
            ticks.append((mk['line'], mk['x'], mk['y'], float(mm.group(1)), float(mm.group(2))))
    out = {'x': [], 'y': [], 'xminor': [], 'yminor': []}
    texts = sorted(d['texts'], key=lambda t: t['line'])
    for t in texts:
        lbl = text_string(t)
        v = label_value(lbl)
        if v is None:
            continue
        prev = [tk for tk in ticks if tk[0] < t['line']]
        if not prev:
            continue
        tk = prev[-1]
        line, x, y, dx, dy = tk
        if abs(dy) > 0 and abs(dx) == 0:      # x-axis tick (vertical mark)
            out['x'].append((x, v, lbl))
        elif abs(dx) > 0 and abs(dy) == 0:
            out['y'].append((y, v, lbl))
    for line, x, y, dx, dy in ticks:
        if abs(dy) > 0 and abs(dx) == 0 and abs(dy) < 3 and abs(y - y0) < 1:
            out['xminor'].append(x)
        if abs(dx) > 0 and abs(dy) == 0 and abs(dx) < 3 and abs(x - x0) < 1:
            out['yminor'].append(y)
    return out
