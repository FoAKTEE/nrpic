# Inventory of the pre-program run directories (ladder rows 2 to 4)

Written by `tracks/core/verify/preprogram/inventory.py`; sha256 of every file except
the bulk outputs (snapshots, restart files, mesh dumps: count and size only).

| Directory | Row | input | executable | log | nrpic history | z4c history | horizon summary | particle file | table | bulk files (GB) |
|---|---|---|---|---|---|---|---|---|---|---|
| `runs/os/nocap_sc` | row 2 | 1 | 1 | 3 | 1 | 1 | 1 | 1 | 76 | 87 (13.5) |
| `runs/os/nocap_v4` | row 2 | 1 | 1 | 3 | 1 | 1 | 1 | 1 | 76 | 87 (13.5) |
| `runs/prolate/e09_v8` | row 3 | 1 | 1 | 3 | 1 | 1 | 1 | 1 | 57 | 292 (26.6) |
| `runs/st/yc0900_v4` | row 4 | 1 | 1 | 3 | 1 | 1 | 0 | 1 | 1 | 183 (15.7) |
| `runs/st/yc0819_v4` | row 4 | 1 | 1 | 3 | 1 | 1 | 0 | 2 | 2 | 183 (15.7) |
| `runs/st/yc0605_v5` | row 4 | 1 | 2 | 5 | 1 | 1 | 1 | 1 | 1 | 333 (19.1) |
| `runs/st/yc0500_v5` | row 4 | 1 | 1 | 3 | 1 | 1 | 1 | 1 | 1 | 135 (8.5) |
| `runs/st/yc0283_v5` | row 4 | 1 | 1 | 3 | 1 | 1 | 1 | 1 | 1 | 299 (16.1) |
| `runs/st/migration_yc0500_v4` | row 4 | 1 | 1 | 8 | 1 | 1 | 0 | 1 | 1 | 1303 (26.1) |
| `runs/st/yc0756_unpert` | row 4 | 1 | 1 | 4 | 1 | 1 | 0 | 2 | 2 | 419 (10.2) |

Executables and inputs (sha256, first 16 hex digits):

- `runs/os/nocap_sc/os_amr.athinput`: 7439cf353feb52d8, 3621 bytes
- `runs/os/nocap_sc/athena.20261113-070659.exe`: eea699995025c974, 94333360 bytes
- `runs/os/nocap_v4/os_amr.athinput`: 8af78b5b50030542, 3448 bytes
- `runs/os/nocap_v4/athena.20261113-062220.exe`: eea699995025c974, 94333360 bytes
- `runs/prolate/e09_v8/prolate_amr.athinput`: e53bacce5805eec6, 3811 bytes
- `runs/prolate/e09_v8/athena.20261113-125024.exe`: bbb74535e4f77886, 94333408 bytes
- `runs/st/yc0900_v4/st_cluster.athinput`: d9d2850f170353e7, 1944 bytes
- `runs/st/yc0900_v4/athena.20261113-062221.exe`: eea699995025c974, 94333360 bytes
- `runs/st/yc0819_v4/st_cluster.athinput`: d9d2850f170353e7, 1944 bytes
- `runs/st/yc0819_v4/athena.20261113-062220.exe`: eea699995025c974, 94333360 bytes
- `runs/st/yc0605_v5/st_cluster_amr.athinput`: 761f5d6f44257316, 3344 bytes
- `runs/st/yc0605_v5/athena.20261113-083550.exe`: bbb74535e4f77886, 94333408 bytes
- `runs/st/yc0605_v5/athena.20261113-100905.exe`: bbb74535e4f77886, 94333408 bytes
- `runs/st/yc0500_v5/st_cluster_amr.athinput`: 761f5d6f44257316, 3344 bytes
- `runs/st/yc0500_v5/athena.20261113-083550.exe`: bbb74535e4f77886, 94333408 bytes
- `runs/st/yc0283_v5/st_cluster_amr.athinput`: 761f5d6f44257316, 3344 bytes
- `runs/st/yc0283_v5/athena.20261113-083550.exe`: bbb74535e4f77886, 94333408 bytes
- `runs/st/migration_yc0500_v4/chain/input.athinput`: 5ae976a2246c2ac9, 1999 bytes
- `runs/st/migration_yc0500_v4/chain/athena`: eea699995025c974, 94333360 bytes
- `runs/st/yc0756_unpert/chain/input.athinput`: c33cd7ff47f8a166, 2303 bytes
- `runs/st/yc0756_unpert/chain/athena`: bbb74535e4f77886, 94333408 bytes
