# Changelog

## 1.0.0 (2026-08-18)

First public pre-release of **LQCV 光品质指标工具箱** (LQMT). Canonical hosting is Gitee; GitHub is a mirror.

This public version is based on the laboratory internal test package
`dist_260727` (local development number 1.3.2). External alignment must
use GitHub tag `v1.0.0`, not the internal number.

Notable calculation choices carried into this release:

- Ra (CIE 13.3 / GB/T 26180): eight special indices Ri are rounded, then
  arithmetically averaged (`rf_from_avg_rounded_rfi=True`).
- Rd reflectance table aligned to Esposito Rd.xlsm RefData2 full precision,
  interpolated to 380–780 nm / 5 nm.
- CQS via LuxPy `v9.0` (approximate CQS 9.0.3).
- Sneutral uses CIE 1964 10°.
- LuxPy locked at 1.12.5.

See `docs/known-limitations.md` for CCT algorithm mismatch and unimplemented
CDM_e.
