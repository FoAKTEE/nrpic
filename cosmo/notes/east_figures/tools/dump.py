import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.abspath(_os.path.join(_HERE, '..', '..', '..', '..'))
import sys
sys.path.insert(0, _HERE + '/')
import numpy as np
import calib as C
KIND = {'ud_comp': ('log', 'log'), 'od_comp': ('log', 'log'), 'delta10m2_comp_all': ('lin', 'log'),
        'rel_eff': None, '10m2_cnst_conv': ('lin', 'log')}
for name in sys.argv[1:]:
    if 'splash' in name:
        k = ('lin', 'lin')
    elif 'comp_frw' in name:
        k = ('log', 'symlog')
    elif 'newt_gr' in name:
        k = ('log', 'log')
    else:
        k = KIND[name]
    F = C.load_mpl(name, *k)
    print('=====', name, F['box']['xlim'], F['box']['ylim'])
    print('  X', F['X'].describe())
    print('  Y', F['Y'].describe())
    for i, s in enumerate(F['strokes']):
        x, y = s['x'], s['y']
        print('  %2d L%5d c=(%.3f,%.3f,%.3f) d=%-18s n=%4d  first=(%.4g, %.4g) last=(%.4g, %.4g) x[%.4g,%.4g] y[%.4g,%.4g]' % (
            i, s['line'], *s['color'], s['dash'], len(x), x[0], y[0], x[-1], y[-1], x.min(), x.max(), y.min(), y.max()))
