# Sensitivity of the USR spectrum to s and sigma (128^3, nmax2 = 1024, last dump cN = 9.585)

| window | s | sigma | U-A2 k<=k_max/2 | U-A2 all | shell shift k<=k_max/2 (error) | shell shift all | linear shift | modes crossed before USR: max shift | passage residual (linear shift) | E/O rms | one-point rms NR/ref-1 | late M record / baseline | means vs baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b | 5 | 1 | 1.08e-04 | 4.27e-03 | - (-) | - | - | - | - (-) | 1.44e-04 | 3.73e-04 | 1-1 | 0.00e+00 |
| s25 | 2.5 | 1 | 1.15e-04 | 4.98e-03 | 2.45e-05 (1.87e-04) | 5.09e-04 | 1.32e-13 | 1.40e-06 | 2.59e-08 (2.97e-04) | 1.42e-04 | 3.85e-04 | 1.04-2.8 | 1.96e-08 |
| s10 | 10 | 1 | 1.05e-04 | 4.05e-03 | 7.30e-06 (2.19e-04) | 2.71e-04 | 0.00e+00 | 6.23e-07 | 8.74e-09 (2.95e-04) | 1.45e-04 | 3.63e-04 | 0.96-1.15 | 9.83e-09 |
| g05 | 5 | 0.5 | 4.69e-05 | 1.54e-03 | 6.47e-05 (1.47e-04) | 5.62e-03 | 0.00e+00 | 4.43e-07 | 8.10e-08 (3.40e-03) | 1.26e-04 | 8.47e-05 | 0.137-0.932 | 1.42e-07 |
| g2 | 5 | 2 | 2.60e-04 | 1.47e-02 | 1.87e-04 (1.87e-04) | 9.13e-03 | 0.00e+00 | 1.68e-05 | 2.62e-07 (1.13e-03) | 1.56e-04 | 6.74e-04 | 0.839-21.2 | 1.20e-07 |

k_max = 32 dk. Shifts are shell powers at the last dump against the baseline (odd parts where mirrored); error = |e_w| + |e_b|, the NR-vs-reference power error of the two runs. Passage residual: max over modes k <= k_max/2 and dumps 0 < cN < 4.5 of |(O_w - O_b) - (ref_w - ref_b)|/max_t|ref_w|.

Sensitivity d ln P/d ln(par) at the last dump, max per band (error from the NR-vs-reference power errors):

- s: k<6: 6.32e-07 (2.39e-05), 6<=k<12: 1.80e-06 (2.45e-05), 12<=k<=16: 2.30e-05 (1.01e-04), 16<k<=32: 5.63e-04 (7.53e-03), 8<k<=16: 2.30e-05 (1.01e-04); linear 9.5e-14
- sigma: k<6: 1.12e-06 (2.36e-05), 6<=k<12: 1.30e-05 (2.64e-05), 12<=k<=16: 8.82e-05 (6.56e-05), 16<k<=32: 1.06e-02 (1.19e-02), 8<k<=16: 8.82e-05 (6.56e-05); linear 0.0e+00
