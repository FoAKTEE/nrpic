import numpy as np, math
# transcription of MultigridDriver::CalculateMultipoleCoefficients / ScaleMultipoleCoefficients /
# EvalMultipolePhi (multigrid_driver.cpp 2245-2369, multigrid.hpp 782-809), order 4
def coeffs(src, w, fix):
    mp=np.zeros(25)
    for (x,y,z),s in zip(src,w):
        x2,y2,z2=x*x,y*y,z*z; xy,yz,zx=x*y,y*z,z*x; r2=x2+y2+z2; h=0.5*(x2-y2)
        mp[0]+=s; mp[1]+=s*y; mp[2]+=s*z; mp[3]+=s*x
        mp[4]+=s*xy; mp[5]+=s*yz; mp[6]+=s*(3*z2-r2); mp[7]+=s*zx; mp[8]+=s*h
        t=3*x2-y2; u=x2-3*y2; f=5*z2-r2
        mp[9]+=s*y*t; mp[10]+=s*xy*z; mp[11]+=s*y*f
        mp[12]+=s*z*((5*z2-3*r2) if fix else (z2-3*r2)); mp[13]+=s*x*f; mp[14]+=s*z*h; mp[15]+=s*x*u
        a=7*z2-r2; b=7*z2-3*r2
        mp[16]+=s*xy*h; mp[17]+=s*yz*t; mp[18]+=s*xy*a; mp[19]+=s*yz*b
        mp[20]+=s*(35*z2*z2-30*z2*r2+3*r2*r2); mp[21]+=s*zx*b; mp[22]+=s*h*a; mp[23]+=s*zx*u
        mp[24]+=s*0.125*(x2*u-y2*t)
    P=math.pi
    sc=[.25/P]*4+[.75/P,.75/P,.0625/P,.75/P,.75/P]+[.0625*2.5/P,.25*15/P,.0625*1.5/P,.0625/P,.0625*1.5/P,.25*15/P,.0625*2.5/P]
    sc+=[.25*35/P,.0625*17.5/P,.0625*5/P,.0625*2.5/P,.0625*.0625/P,.0625*2.5/P,.0625*5/P,.0625*17.5/P,.25*35/P]
    return mp*np.array(sc)
def ev(m,x,y,z,fix):
    x2,y2,z2=x*x,y*y,z*z; xy,yz,zx=x*y,y*z,z*x; r2=x2+y2+z2; ir2=1/r2; ir1=math.sqrt(ir2); ir3=ir2*ir1; ir5=ir3*ir2
    h=0.5*(x2-y2)
    p=ir1*m[0]+ir3*(m[1]*y+m[2]*z+m[3]*x)+ir5*(m[4]*xy+m[5]*yz+(3*z2-r2)*m[6]+m[7]*zx+m[8]*h)
    ir7=ir5*ir2; ir9=ir7*ir2; u=x2-3*y2; t=3*x2-y2
    p+=ir7*(y*t*m[9]+x*u*m[15]+xy*z*m[10]+z*h*m[14]+(5*z2-r2)*(y*m[11]+x*m[13])+z*((5*z2-3*r2) if fix else (z2-3*r2))*m[12])
    p+=ir9*(xy*h*m[16]+0.125*(x2*u-y2*t)*m[24]+yz*t*m[17]+zx*u*m[23]+(7*z2-r2)*(xy*m[18]+h*m[22])+(7*z2-3*r2)*(yz*m[19]+zx*m[21])+(35*z2*z2-30*z2*r2+3*r2*r2)*m[20])
    return p
rng=np.random.default_rng(1); src=rng.uniform(-1,1,(20,3)); w=rng.uniform(.5,1.5,20)
for R in (8.,16.,32.):
    x=np.array([0.3,-0.5,0.81]); x=x/np.linalg.norm(x)*R
    exact=sum(w/np.linalg.norm(x-src,axis=1))/(4*math.pi)
    print(R, "upstream rel err %.2e"%abs(ev(coeffs(src,w,False),*x,False)/exact-1), " with (5z2-3r2): %.2e"%abs(ev(coeffs(src,w,True),*x,True)/exact-1))
