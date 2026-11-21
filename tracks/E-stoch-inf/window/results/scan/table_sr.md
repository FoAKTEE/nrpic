# Sensitivity of the SR spectrum to s and sigma (64^3, nmax2 = 256, last dump cN = 8.099)

| window | s | sigma | U-A2 k<=k_max/2 | U-A2 all | shell shift k<=k_max/2 (error) | shell shift all | linear shift | modes crossed before USR: max shift | passage residual (linear shift) | E/O rms | one-point rms NR/ref-1 | late M record / baseline | means vs baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b | 5 | 1 | 9.64e-05 | 4.00e-03 | - (-) | - | - | - | - (-) | 2.85e-07 | 6.07e-05 | 1-1 | 0.00e+00 |
| s25 | 2.5 | 1 | 1.16e-04 | 4.93e-03 | 3.02e-05 (4.03e-04) | 1.45e-03 | 8.92e-12 | 1.32e-04 | 2.15e-05 (2.23e-01) | - | 7.12e-05 | 0.957-0.983 | 1.63e-12 |
| s10 | 10 | 1 | 9.29e-05 | 3.76e-03 | 8.57e-06 (3.65e-04) | 4.22e-04 | 0.00e+00 | 4.03e-05 | 1.92e-05 (1.87e-01) | - | 5.67e-05 | 1.01-1.01 | 3.44e-12 |
| g05 | 5 | 0.5 | 3.62e-05 | 1.11e-03 | 1.22e-04 (2.51e-04) | 5.87e-03 | 0.00e+00 | 4.51e-06 | 6.03e-05 (1.12e+00) | - | 1.84e-05 | 0.752-0.944 | 3.04e-12 |
| g2 | 5 | 2 | 3.65e-04 | 1.70e-02 | 4.30e-04 (8.03e-04) | 2.09e-02 | 0.00e+00 | 1.70e-03 | 1.86e-04 (9.97e-01) | - | 2.10e-04 | 1.05-1.56 | 4.97e-12 |

k_max = 16 dk. Shifts are shell powers at the last dump against the baseline (odd parts where mirrored); error = |e_w| + |e_b|, the NR-vs-reference power error of the two runs. Passage residual: max over modes k <= k_max/2 and dumps 0 < cN < 4.5 of |(O_w - O_b) - (ref_w - ref_b)|/max_t|ref_w|.

Sensitivity d ln P/d ln(par) at the last dump, max per band (error from the NR-vs-reference power errors):

- s: k<6: 4.50e-06 (1.61e-05), 6<=k<12: 1.06e-04 (7.59e-04), 12<=k<=16: 1.35e-03 (8.41e-03), 8<k<=16: 1.35e-03 (8.41e-03); linear 6.4e-12
- sigma: k<6: 2.02e-05 (2.72e-05), 6<=k<12: 1.51e-03 (1.69e-03), 12<=k<=16: 1.92e-02 (2.08e-02), 8<k<=16: 1.92e-02 (2.08e-02); linear 0.0e+00
