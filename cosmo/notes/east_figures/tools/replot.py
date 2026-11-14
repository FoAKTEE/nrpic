"""Check figures: original EPS render (left) next to a replot of the extracted
numbers in calibrated data coordinates (right), same axis limits and scales."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.abspath(_os.path.join(_HERE, '..', '..', '..', '..'))

import os
import sys
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, _HERE + '/')
sys.path.insert(0, _REPO + '/python')
import extract_all          # noqa: F401,E402  (for unpickling Curve)
from extract_all import Curve  # noqa: F401,E402
from nrpic import figstyle as fs  # noqa: E402

OUT = _REPO + '/cosmo/notes/east_figures'
REND = _HERE + '/render'

fs.use_style()
store = pickle.load(open(_HERE + '/curves.pkl', 'rb'))

LS = {(): '-', (6.0, 6.0): '--', (1.0, 3.0): ':', (3.0, 5.0, 1.0, 5.0): '-.'}


def scale_of(axis):
    return axis.kind


for name, v in store.items():
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    a0 = fig.add_axes([0.0, 0.02, 0.48, 0.96])
    img = plt.imread(os.path.join(REND, name + '.png'))
    a0.imshow(img)
    a0.set_axis_off()
    a0.set_title('original (%s.eps)' % name, fontsize=8)
    ax = fig.add_axes([0.58, 0.14, 0.40, 0.76])
    X, Y = v['Xaxis'], v['Yaxis']
    for c in v['curves']:
        for s in c.segs:
            x = np.array(s['x'], float)
            y = np.array(s['y'], float)
            if Y.kind == 'log':
                y = np.where(y > 0, y, np.nan)
            ax.plot(x, y, color=c.rgb, ls=LS.get(c.dash_t, '-'), lw=1.0)
    if X.kind == 'log':
        ax.set_xscale('log')
    if Y.kind == 'log':
        ax.set_yscale('log')
    elif Y.kind == 'symlog':
        ax.set_yscale('symlog', linthresh=1e-2, linscale=1.0)
    ax.set_xlim(*v['box']['xlim'])
    ax.set_ylim(*v['box']['ylim'])
    ax.set_title('replot of extracted CSV', fontsize=8)
    ax.tick_params(labelsize=8)
    fig.savefig(os.path.join(OUT, name, 'check_%s.png' % name), dpi=150)
    plt.close(fig)
    print('wrote', name)
