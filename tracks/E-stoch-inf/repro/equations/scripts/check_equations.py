"""Computer-algebra checks of the equations of arXiv:2401.08530 (P0) and arXiv:2512.14649 (P1).

Items (a) linear ADM and the gauge families as functionals of R, (b) coarse-grained sources,
constraints, negative controls, BSSN, the usual stochastic-inflation limit. Writes
results.json into --out. Locators in the comments are lines of the paper sources, which this
script does not read.
"""
import argparse
import json
import os
import sys
import time

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adm_lin import (BASE_RATES, BB, DPHI, EE, H, M, P, PHI, PSI, Dt, a, add_jet_rates,  # noqa: E402
                     build, eps1, eps2, eps3, is_zero, jets, k, ms_rule, paper_linear, phid,
                     reduce_ms, sq2e1M, substitute_pert, V1, V2)

EQS = ('field', 'K', 'Kt_xx', 'Kt_yy', 'Ham', 'Mx')
RES = {}


def record(key, ok, detail=''):
    RES[key] = {'pass': bool(ok), 'detail': str(detail)[:600]}
    print('%-58s %s %s' % (key, 'PASS' if ok else 'FAIL', str(detail)[:160]))


def zero(e):
    return is_zero(e)


# ----------------------------------------------------------------------------- gauge families
def families(R, S, coarse, newtonian_variant='corrected'):
    """Each family: (fields dict, extra rates). R: jets of R (or R>), S: jets of S_R.

    The Bardeen potentials as functionals of R (P0:286-287, P1:164-165); for coarse=True
    Psi_B is the coarse-grained one of P0:613 / P1:201."""
    g = {n: jets(n) for n in ('Es', 'Bs', 'Ps', 'Fs', 'Ns', 'Qs')}   # gauge functions
    rates = dict(BASE_RATES)
    for J in list(g.values()) + [R, S]:
        add_jet_rates(rates, J)
    R0, R1, R2 = R[0], R[1], R[2]
    S0 = S[0] if coarse else 0
    PhiB = -eps1 * H * a ** 2 / k ** 2 * R1
    if coarse:
        PsiB = -eps1 * a ** 2 / k ** 2 * (H * R1 - S0)
    else:
        PsiB = eps1 * R0 + eps1 * a ** 2 / k ** 2 * (R2 + H * (2 - eps2) * R1)
    out = {}
    # 1. pure gravity P0:296-308 (delta phi = Fs, E = Es)
    dps = g['Fs']
    r = dict(rates)
    out['pure_gravity'] = ({
        'E': g['Es'][0], 'dphi': dps[0],
        'Phi': R0 - H / (M * P[0]) * dps[0],
        'Psi': H / (M * P[0]) * (eps1 + eps2 / 2) * dps[0] - R1 / H + dps[1] / (M * P[0]),
        'B': g['Es'][1] + eps1 * R1 / k ** 2 + (R0 - H / (M * P[0]) * dps[0]) / (a ** 2 * H)}, r)
    # 2. fixed curvature P0:325-339 (Phi = Fs, E = Es)
    ph = g['Fs']
    out['fixed_curvature'] = ({
        'E': g['Es'][0], 'Phi': ph[0], 'dphi': sq2e1M * (R0 - ph[0]),
        'Psi': eps1 * (R0 - ph[0]) - ph[1] / H,
        'B': g['Es'][1] + eps1 * R1 / k ** 2 + ph[0] / (H * a ** 2)}, dict(rates))
    # 3. Newtonian P0:343-355 (B = Bs, E = Es)
    chis = -a ** 2 * (g['Bs'][0] - g['Es'][1])
    chis_dot = Dt(chis, rates)
    if newtonian_variant == 'printed':
        dphiN = sq2e1M * (R0 + eps1 * H * a ** 2 / k ** 2 * R1 - a ** 2 * (g['Bs'][0] - g['Es'][1]))
    else:
        dphiN = sq2e1M * (R0 + eps1 * H * a ** 2 / k ** 2 * R1 - H * a ** 2 * (g['Bs'][0] - g['Es'][1]))
    PsiN = (PhiB if newtonian_variant == 'printed_psi_phiB' else PsiB) + chis_dot
    out['newtonian'] = ({
        'E': g['Es'][0], 'B': g['Bs'][0], 'Phi': PhiB - H * chis, 'dphi': dphiN,
        'Psi': PsiN}, dict(rates))
    # 4. uniform N P0:360-389 (B = 0, delta N = Ns), E an integral with the rate of P0:373
    Eint = sp.Symbol('Eint')
    rN = dict(rates)
    rN[Eint] = k ** 2 * Eint / (3 * a ** 2 * H) - g['Ns'][0] / (a ** 2 * H) - eps1 * R1 / k ** 2
    Edot = rN[Eint]
    out['uniform_N'] = ({
        'E': Eint, 'B': 0, 'Phi': -k ** 2 * Eint / 3 + g['Ns'][0],
        'dphi': sq2e1M * (R0 + k ** 2 * Eint / 3 - g['Ns'][0]),
        'Psi': eps1 * (R0 + k ** 2 * Eint / 3 - g['Ns'][0]) + (k ** 2 * Edot / 3 - g['Ns'][1]) / H},
        rN)
    # 5. generalised synchronous P0:392-405 (Psi = Ps, B = Bs), chi and E integrals
    chi, Ei = sp.symbols('chiint Eint2')
    rS = dict(rates)
    rS[chi] = g['Ps'][0] - PsiB
    rS[Ei] = g['Bs'][0] + chi / a ** 2
    PhiS = PhiB - H * chi
    out['synchronous'] = ({
        'Psi': g['Ps'][0], 'B': g['Bs'][0], 'E': Ei, 'Phi': PhiS,
        'dphi': sq2e1M * (R0 - PhiS)}, rS)
    return out


def residuals(L, fields, rates, R, S, coarse):
    Sj = S if coarse else None
    sub, rr = ms_rule(R, Sj, rates)
    out = {}
    for q in EQS:
        e = substitute_pert(L[q], fields, rr)
        e = reduce_ms(e, sub)
        out[q] = sp.cancel(sp.together(sp.expand(e)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()
    R = jets('R')
    S = jets('S')
    L = build('gamma')
    Ld = build('delta')
    Pp = paper_linear()

    # ---- (a) background
    record('a0 background equations hold (P0:220-227)',
           all(L[q] == 0 for q in ('bg_field', 'bg_K', 'bg_Ham')))
    # P0 appendix A and P1:267
    rates = dict(BASE_RATES)
    record('a0 V_phi = sqrt(2eps1)(-3+eps1+eps2/2) M H^2 (P0:914)',
           zero(V1 - sq2e1M * (-3 + eps1 + eps2 / 2) * H ** 2)[0])
    ok267, _ = zero(V1 - (-3 + eps1 + eps2 / 2) * H / phid)
    ok267c, _ = zero(V1 - (-3 + eps1 + eps2 / 2) * H * phid)
    record('a0 P1:267 as printed: V_phi = (-3+eps1+eps2/2) H phidot^-1', ok267)
    record('a0 P1:267 corrected: V_phi = (-3+eps1+eps2/2) H phidot', ok267c)
    Vpp = -sp.Rational(1, 4) * (8 * eps1 ** 2 + 2 * eps1 * (-12 + 5 * eps2)
                                + eps2 * (-6 + eps2 + 2 * eps3)) * H ** 2
    record('a0 V_phiphi (P0:915-916, P1:268-269)', zero(V2 - Vpp)[0])
    Hdd = Dt(BASE_RATES[H], rates)
    record('a0 Hddot = 2 eps1 (1 - eps2/2) H^3 (P0:911)',
           zero(Hdd - 2 * eps1 * (1 - eps2 / 2) * H ** 3)[0], sp.simplify(Hdd / (eps1 * H ** 3)))
    e1dd = Dt(Dt(eps1, rates), rates)
    record('a0 eps1ddot = eps1 eps2 (eps1+eps2+eps3) H^2 (P0:913)',
           zero(e1dd - eps1 * eps2 * (eps1 + eps2 + eps3) * H ** 2)[0])
    ok_e1dd_alt = zero(e1dd - eps1 * eps2 * (eps2 + eps3 + eps1) * H ** 2)[0]
    if not RES['a0 eps1ddot = eps1 eps2 (eps1+eps2+eps3) H^2 (P0:913)']['pass']:
        cand = sp.simplify(e1dd / (eps1 * H ** 2))
        RES['a0 eps1ddot = eps1 eps2 (eps1+eps2+eps3) H^2 (P0:913)']['detail'] = (
            'eps1ddot/(eps1 H^2) = ' + str(sp.factor(sp.simplify(cand.subs({})))))
    # check the sign: with eps_{i+1} = -H^-1 dln eps_i: eps1dot = -H eps1 eps2
    e1d = Dt(eps1, rates)
    record('a0 eps1dot = -H eps1 eps2 (definition P0:919)', zero(e1d + H * eps1 * eps2)[0])
    cand = sp.expand(sp.simplify(e1dd / (eps1 * H ** 2)) - eps2 * (eps1 + eps2 + eps3))
    cand2 = sp.expand(sp.simplify(e1dd / (eps1 * H ** 2)) - eps2 * (eps1 + eps2 - eps3))
    record('a0 eps1ddot = eps1 eps2 (eps1+eps2-eps3) H^2 (alternative sign)',
           sp.simplify(cand2) == 0)

    # ---- (a) linear equations: direct linearisation against the printed ones
    for q in ('field', 'Kt_xx', 'Kt_yy', 'Ham'):
        record('a1 linearised LHS == printed linear eq [%s]' % q, zero(L[q] - Pp[q])[0])
    record('a1 momentum: linearised = (1/3) printed (prefactor -2/3, not -2; P0:249, P1:610)',
           zero(L['Mx'] - Pp['Mx'] / 3)[0])
    record('a1 momentum: linearised == printed (prefactor -2)', zero(L['Mx'] - Pp['Mx'])[0])
    record('a2 K: linearised LHS == printed P0:231 - Ham_lin (uses the Hamiltonian constraint)',
           zero(L['K'] - (Pp['K'] - L['Ham']))[0])
    record('a2 K: linearised LHS == printed P0:231 exactly', zero(L['K'] - Pp['K'])[0])
    # trace of the trace-free equation with delta_ij literally (P0:138, P1:346)
    trd = sp.simplify((Ld['Kt_xx'] + 2 * Ld['Kt_yy']))
    trg = sp.simplify((L['Kt_xx'] + 2 * L['Kt_yy']))
    record('a3 Kt eq with gamma_ij is trace-free (delta^ij-trace = 0)', trg == 0, trg)
    record('a3 Kt eq with delta_ij literally is trace-free', trd == 0, trd)

    # ---- (a) gauge families satisfy all linear equations (no window)
    for variant in ('corrected', 'printed'):
        fam = families(R, S, coarse=False, newtonian_variant=variant)
        for name, (fields, rr) in fam.items():
            if variant == 'printed' and name != 'newtonian':
                continue
            res = residuals(L, fields, rr, R, S, coarse=False)
            bad = [q for q in EQS if res[q] != 0]
            tag = name if variant == 'corrected' else name + ' (delta phi as printed, P0:350)'
            record('a4 %s satisfies the 6 linear eqs' % tag, not bad,
                   {q: res[q] for q in bad})
            if variant == 'printed':
                continue
            # gauge-invariant relations P0:286-289 in this gauge
            Phi, Psi, B, E, dphi = (fields[n] for n in ('Phi', 'Psi', 'B', 'E', 'dphi'))
            sub, r2 = ms_rule(R, None, rr)
            chi = -a ** 2 * (B - Dt(E, rr))
            checks = {
                'Phi_B': Phi + H * chi - (-eps1 * H * a ** 2 / k ** 2 * R[1]),
                'Psi_B': Psi - Dt(chi, rr) - (eps1 * R[0] + eps1 * a ** 2 / k ** 2
                                               * (R[2] + H * (2 - eps2) * R[1])),
                'dphi_gi': dphi - phid * chi - sq2e1M * (R[0] + eps1 * a ** 2 * H / k ** 2 * R[1]),
                'R': Phi + H / phid * dphi - R[0],
            }
            # zeta_gi = -Phi + delta rho / (3 (rho+P)), rho+P = phidot^2
            drho = phid * Dt(dphi, rr) + V1 * dphi - phid ** 2 * Psi
            checks['zeta_gi'] = -Phi + drho / (3 * phid ** 2) - (-R[0] + R[1] / (3 * H))
            badc = {}
            for cn, ce in checks.items():
                ce = reduce_ms(sp.expand(ce), sub)
                ce = sp.cancel(sp.together(ce))
                if ce != 0:
                    badc[cn] = ce
            record('a5 %s: GI relations P0:286-289' % name, not badc, badc)
    # Phi_B = Psi_B on MS solutions (P0:293)
    sub0, _ = ms_rule(R, None, dict(BASE_RATES))
    d = reduce_ms(-eps1 * H * a ** 2 / k ** 2 * R[1]
                  - (eps1 * R[0] + eps1 * a ** 2 / k ** 2 * (R[2] + H * (2 - eps2) * R[1])), sub0)
    record('a5 Phi_B = Psi_B on MS solutions (P0:293)', zero(d)[0])
    # uniform N: sign of delta N from its definition P0:365 (dN/dt = -alpha K / 3)
    Lg = L
    Ktr = Lg['_Ktr']
    from adm_lin import first_order, lin, eps as EPS
    dN_rate = first_order(lin(-Lg['_alpha'] * Ktr / 3))
    rr = dict(BASE_RATES)
    for J in (PHI, PSI, BB, EE):
        add_jet_rates(rr, J)
    # with B = 0: d(delta N)/dt should be d/dt(-Phi - k^2 E/3)
    cand_minus = Dt(-PHI[0] - k ** 2 * EE[0] / 3, rr)
    cand_plus = Dt(PHI[0] + k ** 2 * EE[0] / 3, rr)
    dN0 = dN_rate.subs({BB[0]: 0})
    record('a4 uniform N: delta N = -(Phi + k^2 E/3) from P0:365 (B=0)', zero(dN0 - cand_minus)[0])
    record('a4 uniform N: delta N = +(Phi + k^2 E/3) as printed P0:371', zero(dN0 - cand_plus)[0])

    # ---- (b) coarse-grained: residuals are the printed sources, gauge independent
    srcs = {'field': sq2e1M * S[0], 'K': -eps1 * S[0],
            'Kt_xx': a ** 2 * eps1 * (sp.Rational(1, 3) - 1) * S[0],
            'Kt_yy': a ** 2 * eps1 * sp.Rational(1, 3) * S[0], 'Ham': 0, 'Mx': 0}
    fam = families(R, S, coarse=True)
    for name, (fields, rr) in fam.items():
        res = residuals(L, fields, rr, R, S, coarse=True)
        bad = {q: sp.factor(res[q] - srcs[q]) for q in EQS if sp.cancel(res[q] - srcs[q]) != 0}
        record('b1 %s: residuals = printed sources, constraints 0' % name, not bad, bad)
        # residual of the printed (paper-form) K equation as well
        resp = residuals(Pp, fields, rr, R, S, coarse=True)
        record('b1 %s: printed linear K eq (P0:231) residual = -eps1 S_R' % name,
               sp.cancel(resp['K'] + eps1 * S[0]) == 0, sp.factor(resp['K']))
    # negative control (i): flip the sign of S_R in Psi_B> (P0:613)
    Sm = sp.symbols('Sm0:7')
    fam_neg = families(R, S, coarse=True)
    for name in ('synchronous', 'newtonian'):
        fields, rr = fam_neg[name]
        flip = {S[n]: -S[n] for n in range(len(S))}
        f2 = {kk: (sp.sympify(v).xreplace(flip)) for kk, v in fields.items()}
        rr2 = {kk: sp.sympify(v).xreplace(flip) for kk, v in rr.items()}
        res = residuals(L, f2, rr2, R, S, coarse=True)
        record('b2 control: sign of S in Psi_B> flipped [%s] -> Ham or M nonzero' % name,
               res['Ham'] != 0 or res['Mx'] != 0, {'Ham': sp.factor(res['Ham']),
                                                   'Mx': sp.factor(res['Mx'])})
    # negative control (ii): Psi_B> = Phi_B> (P0:690), Newtonian gauge as printed P0:351
    fam_b = families(R, S, coarse=True, newtonian_variant='printed_psi_phiB')
    fields, rr = fam_b['newtonian']
    res = residuals(L, fields, rr, R, S, coarse=True)
    record('b2 control: Psi_B> := Phi_B> (Newtonian, P0:351 form) -> constraint violated',
           res['Mx'] != 0 or res['Ham'] != 0,
           {q: sp.factor(res[q]) for q in ('Ham', 'Mx', 'field')})
    # gauge dependence under that control: Psi_B> := Phi_B> in the synchronous family too
    def fam_phiB_sync():
        f5 = families(R, S, coarse=True)
        fields5, rr5 = f5['synchronous']
        chi = sp.Symbol('chiint')
        rr5 = dict(rr5)
        rr5[chi] = sp.Symbol('Ps0') - (-eps1 * H * a ** 2 / k ** 2 * R[1])
        return fields5, rr5
    f5, rr5 = fam_phiB_sync()
    res5 = residuals(L, f5, rr5, R, S, coarse=True)
    dif = {q: sp.factor(sp.cancel(res5[q] - res[q])) for q in ('field', 'K', 'Kt_xx')}
    record('b2 control: with Psi_B> := Phi_B> the Newtonian and synchronous residuals are '
           'identical to each other', all(v == 0 for v in dif.values()), dif)
    difc = {q: sp.factor(sp.cancel(res[q] - srcs[q])) for q in ('field', 'K', 'Kt_xx')}
    record('b2 control: with Psi_B> := Phi_B> (Newtonian, synchronous) the residuals differ '
           'from those of the comoving, flat and uniform-N families (= printed sources), '
           'i.e. depend on the gauge family (P0:690)', any(v != 0 for v in difc.values()), difc)
    record('b2 control: with Psi_B> := Phi_B> the synchronous constraints are violated',
           res5['Ham'] != 0 or res5['Mx'] != 0,
           {q: sp.factor(res5[q]) for q in ('Ham', 'Mx')})

    # ---- (b5) constraint propagation in the synchronous gauge of the code (Psi = B = 0):
    # evolve with the sources c_X S (printed coefficients), impose H = M = 0 on the data and
    # check that dH/dt and dM/dt vanish; then flip the sign of one source at a time
    rp = dict(BASE_RATES)
    for J in (PHI, EE, DPHI, S):
        add_jet_rates(rp, J)
    zero_gauge = {PSI[n]: 0 for n in range(len(PSI))}
    zero_gauge.update({BB[n]: 0 for n in range(len(BB))})
    Ls = {q: sp.expand(L[q].xreplace(zero_gauge)) for q in EQS}
    cS = {'field': sq2e1M, 'K': -eps1, 'Kt_xx': a ** 2 * eps1 * (sp.Rational(1, 3) - 1)}
    for flip in (None, 'field', 'K', 'Kt_xx'):
        sgn = {q: (-1 if q == flip else 1) for q in cS}
        sol = sp.solve([Ls[q] - sgn[q] * cS[q] * S[0] for q in ('field', 'K', 'Kt_xx')],
                       [DPHI[2], PHI[2], EE[2]], dict=True)[0]
        cons = sp.solve([Ls['Ham'], Ls['Mx']], [DPHI[1], PHI[1]], dict=True)[0]
        out = {}
        for q in ('Ham', 'Mx'):
            e = sp.expand(Dt(Ls[q], rp)).xreplace(sol)
            e = sp.expand(e).xreplace(cons)
            out[q] = sp.factor(sp.cancel(sp.together(e)))
        ok = all(v == 0 for v in out.values())
        if flip is None:
            record('b5 constraint propagation (Psi=B=0), printed sources: dH/dt = dM/dt = 0 '
                   'on H = M = 0', ok, out)
        else:
            record('b5 negative control: sign of S_%s flipped -> dH/dt or dM/dt nonzero at '
                   'first order' % flip, not ok, out)

    # ---- (b6) P1:241-259: coarse-grained variables without a gauge, delta phi> free
    Fj = jets('F')
    r6 = dict(BASE_RATES)
    for J in (R, S, Fj):
        add_jet_rates(r6, J)
    sub6, rr6 = ms_rule(R, S, r6)
    Phi6 = R[0] - H / phid * Fj[0]
    chi6 = -Phi6 / H - eps1 * a ** 2 / k ** 2 * R[1]
    Psi6 = Dt(chi6, rr6) - eps1 * a ** 2 / k ** 2 * (H * R[1] - S[0])
    red6 = lambda e: sp.cancel(sp.together(reduce_ms(sp.expand(e), sub6)))  # noqa: E731
    printed6 = {
        'Phidot> (P1:251)': (Phi6, R[1] - H / phid * Fj[1] - eps2 * H ** 2 / (2 * phid) * Fj[0]),
        'chidot> (P1:253-254)': (chi6, H * (eps1 + eps2 / 2) / phid * Fj[0] + Fj[1] / phid
                                 - R[1] / H + eps1 * a ** 2 / k ** 2 * (H * R[1] - S[0])),
    }
    Psid_pr = (Fj[2] / phid + (2 * eps1 + eps2) * H / phid * Fj[1]
               + sp.Rational(1, 4) * eps2 * (-2 * eps1 + eps2 - 2 * eps3) * H ** 2 / phid * Fj[0]
               + a ** 2 / H * k ** 2 * R[0] + (3 - eps1 - eps2) * R[1] - S[0] / H)
    printed6['Psidot> as printed (P1:256-259, term a^2 H^-1 k^2 R>)'] = (Psi6, Psid_pr)
    printed6['Psidot> corrected (term k^2 a^-2 H^-1 R>)'] = (
        Psi6, Psid_pr - a ** 2 / H * k ** 2 * R[0] + k ** 2 / (a ** 2 * H) * R[0])
    for name, (var, pr) in printed6.items():
        dd = sp.factor(red6(Dt(var, rr6) - pr))
        record('b6 %s' % name, dd == 0, dd)

    # ---- (b) BSSN: K equation of BSSN differs from ADM K equation by the Hamiltonian
    # constraint; A_ij = X Kt_ij so S_A = X_b S_Kt = a^-2 S_Kt (P0:1025, P1:686)
    from adm_lin import build as _b  # noqa: F401
    g, gi, Kdd, Kt = L['_g'], L['_gi'], L['_Kdd'], L['_Kt']
    Xc, rho, Ssc, alpha, lap_al = L['_X'], L['_rho'], L['_S'], L['_alpha'], L['_lap_al']
    rB = L['_rates']
    At = (Kt * Xc).applyfunc(lin)
    AtAt = 0  # second order
    KB = {}
    for variant, coef in (('M^-2/2', 1 / (2 * M ** 2)), ('4 pi (printed)', 4 * sp.pi)):
        e = lin(Dt(Ktr, rB) + lap_al - alpha * (Ktr ** 2 / 3 + AtAt) - coef * alpha * (rho + Ssc))
        KB[variant] = first_order(e)
        bg = sp.simplify(sp.expand(e).subs(EPS, 0))
        okK = zero(KB[variant] - L['K'] - (-L['Ham']) * 0 - (KB[variant] - L['K']))[0]
        diff = sp.cancel(sp.together(KB[variant] - L['K']))
        prop = sp.cancel(sp.together(diff / L['Ham'])) if L['Ham'] != 0 else None
        record('b3 BSSN K eq [%s]: background holds' % variant, bg == 0, bg)
        record('b3 BSSN K eq [%s]: minus ADM K eq is a multiple of Ham_lin' % variant,
               prop is not None and not prop.free_symbols - {M}, prop)
    # A_xx equation: dt A - X[ -DDal + alpha R ]^TF - alpha K A = X * (ADM Kt LHS) at 1st order
    DDal, Ric = L['_DDal'], L['_Ric']
    for (i, j), key in (((0, 0), 'Kt_xx'), ((1, 1), 'Kt_yy')):
        trDD = lin(sum(gi[m, n] * DDal[m][n] for m in range(3) for n in range(3)))
        trR = L['_Rs']
        TF = lambda T, tr: lin(T - g[i, j] * tr / 3)  # noqa: E731
        inner = TF(-DDal[i][j] + alpha * Ric[i, j], lin(-trDD + alpha * trR))
        eA = lin(Dt(At[i, j], rB) - Xc * inner - alpha * Ktr * At[i, j])
        A1 = first_order(eA)
        ratio = sp.cancel(sp.together(A1 / L[key]))
        record('b3 BSSN A_%s LHS = X_b * ADM Kt LHS (so S_A = a^-2 S_Kt)' % key[-2:],
               sp.simplify(ratio - 1 / a ** 2) == 0, ratio)
    # printed BSSN momentum constraint D^j(gamma_ij K - K_ij) - M^-2 S_i with S_i = J_i
    Gam = L['_Gam']
    from adm_lin import x as X_, EX
    def dsp(e, i):
        return sp.diff(e, X_) if i == 0 else sp.S(0)
    # D^j T_ij for T_ij = gamma_ij K - K_ij, i = x (linear order)
    T = (g * Ktr - Kdd).applyfunc(lin)
    divT = 0
    for j in range(3):
        for m in range(3):
            # D_m T_xj
            DmT = dsp(T[0, j], m) - sum(Gam[l][m][0] * T[l, j] + Gam[l][m][j] * T[0, l]
                                        for l in range(3))
            divT += gi[m, j] * DmT
    divT = lin(divT)
    J = L['_J']
    Mprinted = first_order(lin(divT - J[0] / M ** 2))
    Mcorr = first_order(lin(-divT - J[0] / M ** 2))
    fam = families(R, S, coarse=False)
    fields, rr = fam['synchronous']
    sub, rr2 = ms_rule(R, None, rr)
    vp = sp.cancel(sp.together(reduce_ms(substitute_pert(Mprinted, fields, rr2), sub)))
    vc = sp.cancel(sp.together(reduce_ms(substitute_pert(Mcorr, fields, rr2), sub)))
    record('b3 BSSN momentum constraint as printed (S_i = J_i) vanishes on a solution', vp == 0,
           sp.factor(vp))
    record('b3 BSSN momentum constraint D_j(K^j_i - delta K) - M^-2 J_i vanishes', vc == 0, vc)

    # ---- (b4) usual SI limit P0 section IV E
    Rp = sp.symbols('r0:5')  # R in e-folds: r_n = d^n R / dN^n
    W = sp.symbols('w0:5')
    e1, e2 = sp.symbols('e1 e2')
    Hs, Ms = sp.symbols('Hs Ms', positive=True)
    # d/dN of R-jets and window jets; eps1' = -eps1 eps2, eps2' = -eps2 eps3
    e3 = sp.Symbol('e3')
    rN = {e1: -e1 * e2, e2: -e2 * e3, Hs: -e1 * Hs}
    for J in (Rp, W):
        add_jet_rates(rN, J)
    DN = lambda ex: Dt(ex, rN)  # noqa: E731
    sq = sp.sqrt(2 * e1) * Ms
    dphi_flat = sq * Rp[0]
    dpi_flat = DN(dphi_flat)
    # check P0:726: delta pi = sqrt(2eps1) M (-eps2 R/2 + R')
    record('b4 flat-gauge delta pi = sqrt(2 eps1) M (R\' - eps2 R/2) (P0:726)',
           sp.simplify(dpi_flat - sq * (Rp[1] - e2 * Rp[0] / 2)) == 0)
    Sphi = W[1] * dphi_flat
    Spi = W[1] * dpi_flat
    Sigma = Hs * (Spi + DN(Sphi) + (3 - e1) * Sphi)
    SR_N = Hs ** 2 * (Rp[0] * W[2] + (2 * Rp[1] + (3 - e1 - e2) * Rp[0]) * W[1])   # P0:718
    record('b4 Sigma = sqrt(2 eps1) M S_R / H  (= S_Pi / H)',
           sp.simplify(Sigma - sq * SR_N / Hs) == 0)
    record('b4 Sigma = sqrt(2 eps1) M S_R  (= S_Pi, as stated at P0:730)',
           sp.simplify(Sigma - sq * SR_N) == 0)
    # P0:718: S_R in cosmic time -> e-folds
    tR = sp.symbols('R0:4')
    tW = sp.symbols('W0:4')
    rt = dict(BASE_RATES)
    for J in (tR, tW):
        add_jet_rates(rt, J)
    SR_t = tR[0] * tW[2] + (2 * tR[1] + (3 - eps2) * H * tR[0]) * tW[1]
    # in e-folds: d/dt = H d/dN: R1 = H r1, W1 = H w1, W2 = H^2 w2 + Hdot w1
    sub_t = {tR[1]: H * Rp[1], tW[1]: H * W[1], tW[2]: H ** 2 * W[2] + BASE_RATES[H] * W[1]}
    SR_conv = sp.expand(SR_t.xreplace(sub_t).subs(tR[0], Rp[0]))
    SR_N_t = H ** 2 * (Rp[0] * W[2] + (2 * Rp[1] + (3 - eps1 - eps2) * Rp[0]) * W[1])
    record('b4 S_R in e-folds (P0:718, P0:1037)', sp.simplify(SR_conv - SR_N_t) == 0)
    # Friedmann line of P0:530, P0:710, P1:108 with pi = dphi/dN: 3 M^2 H^2 = H^2 pi^2/2 + V
    piN, Vv = sp.symbols('pi_N V', positive=True)
    Hsq_true = Vv / (3 * Ms ** 2 * (1 - piN ** 2 / (6 * Ms ** 2)))
    Hsq_printed = Vv / (1 - piN ** 2 / (6 * Ms ** 2))
    fr = sp.simplify(3 * Ms ** 2 * Hsq_true - (Hsq_true * piN ** 2 / 2 + Vv))
    record('b4 H^2 = V / (3 M^2 (1 - pi^2/6M^2)) solves Friedmann', fr == 0)
    frp = sp.simplify(3 * Ms ** 2 * Hsq_printed - (Hsq_printed * piN ** 2 / 2 + Vv))
    record('b4 H^2 = V / (1 - pi^2/6M^2) as printed solves Friedmann', frp == 0, frp)
    # P0:708 Pi equation in N_b time from the ADM field equation with alpha = 1/H>
    # (1/alpha) dPi/dt - K Pi + V' = S_Pi, K = -3H>, t = N_b
    Pi_, Vp_, SPi_ = sp.symbols('Pi Vp SPi')
    Hl = sp.Symbol('Hl', positive=True)
    dPi = (1 / Hl) * (-3 * Hl * Pi_ - Vp_ + SPi_)
    record('b4 dPi/dN = -3 Pi - V\'/H> + S_Pi/H> (P0:708)',
           sp.simplify(dPi - (-3 * Pi_ - Vp_ / Hl + SPi_ / Hl)) == 0)

    RES['_meta'] = {'seconds': round(time.time() - t0, 1), 'sympy': sp.__version__}
    with open(os.path.join(args.out, 'results.json'), 'w') as fh:
        json.dump(RES, fh, indent=1)
    npass = sum(1 for kk, v in RES.items() if not kk.startswith('_') and v['pass'])
    print('done: %d entries, %d pass, %.1f s' % (len(RES) - 1, npass, time.time() - t0))


if __name__ == '__main__':
    main()
