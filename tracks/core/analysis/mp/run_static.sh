#!/usr/bin/env bash
# Test 1a of tracks/core/JOURNAL-mp.md: Bowen-York data on the mesh at t = 0, on
# processors (one core per run, eight at a time).  Tables are written first into
# scratch/core/tmp by python/nrpic/bowen_york.py.
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/core-mp
TMP=/data/haiyangw/nrpic/scratch/core/tmp
N="python3 $WT/tracks/core/analysis/mp/nrun.py --exe cpu --input $WT/problems/puncture/by_static.athinput"
cd "$WT"
export PYTHONPATH=$WT/python
python3 -m nrpic.bowen_york --mass 1 --momentum 0.3 --lmax 8 --out $TMP/by_m1_p0.3.tab
python3 -m nrpic.bowen_york --mass 1 --momentum 0.3 --lmax 8 --linear --out $TMP/by_m1_p0.3_lin.tab

res() { echo "mesh/nx1=$1 mesh/nx2=$1 mesh/nx3=$1"; }
jobs_list=()
add() { jobs_list+=("$*"); }

for n in 32 64 128; do
  add "--label s_p0.0_none_n$n --purpose 'Test 1a: truncation error of the Hamiltonian residual of a Brill-Lindquist puncture, no curvature' -- $(res $n) problem/comp0_p1=0.0"
  add "--label s_p0.3_none_n$n --purpose 'Test 1a (i): Bowen-York puncture P = 0.3, no correction' -- $(res $n)"
  add "--label s_p0.3_approx_n$n --purpose 'Test 1a (iv): P = 0.3, closed-form correction' -- $(res $n) problem/comp0_corr=approx"
  add "--label s_p0.3_table_n$n --file $TMP/by_m1_p0.3.tab --purpose 'Test 1a (v): P = 0.3, tabulated full correction' -- $(res $n) problem/comp0_corr=table problem/comp0_corr_file=by_m1_p0.3.tab"
done
add "--label s_p0.3_tablelin_n128 --file $TMP/by_m1_p0.3_lin.tab --purpose 'Test 1a: P = 0.3, tabulated second-order correction (must agree with approx)' -- $(res 128) problem/comp0_corr=table problem/comp0_corr_file=by_m1_p0.3_lin.tab"
for p in 0.1 0.2 0.4; do
  add "--label s_p${p}_none_n128 --purpose 'Test 1a (ii),(iii): scaling with momentum, no correction' -- $(res 128) problem/comp0_p1=$p"
  add "--label s_p${p}_approx_n128 --purpose 'Test 1a (iv): scaling with momentum, closed-form correction' -- $(res 128) problem/comp0_p1=$p problem/comp0_corr=approx"
done
SP="problem/comp0_p1=0.0 problem/comp0_s3=0.4"
PS="problem/comp0_p1=0.3 problem/comp0_s2=0.2 problem/comp0_s3=0.4"
for n in 64 128; do
  add "--label s_spin_none_n$n --purpose 'Test 1a (vi): spin 0.4 along z, no correction' -- $(res $n) $SP"
  add "--label s_spin_approx_n$n --purpose 'Test 1a (vi): spin 0.4 along z, closed-form correction' -- $(res $n) $SP problem/comp0_corr=approx"
  add "--label s_ps_none_n$n --purpose 'Test 1a (vi): momentum and spin not parallel, no correction' -- $(res $n) $PS"
  add "--label s_ps_approx_n$n --purpose 'Test 1a (vi): momentum and spin not parallel, closed-form correction with cross term' -- $(res $n) $PS problem/comp0_corr=approx"
done
TWO="problem/ncomp=2 problem/comp0_x1=-1.5 problem/comp0_p1=0.0 problem/comp0_p2=0.3 problem/comp1_type=puncture problem/comp1_mass=0.5 problem/comp1_x1=1.5 problem/comp1_p2=-0.3 problem/comp1_s3=0.1"
for n in 64 128; do
  add "--label s_two_none_n$n --purpose 'Test 1a (vii): two punctures with momenta and a spin, no correction' -- $(res $n) $TWO"
  add "--label s_two_approx_n$n --purpose 'Test 1a (vii): two punctures, closed-form corrections' -- $(res $n) $TWO problem/comp0_corr=approx problem/comp1_corr=approx"
done

# -d: xargs must not strip the quotes of the purpose strings
printf '%s\n' "${jobs_list[@]}" | xargs -d '\n' -P 8 -I{} bash -c "$N {}"
