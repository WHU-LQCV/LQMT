# 更新记录

## 1.0.0 (2026-08-18)

LQCV 光品质指标工具箱（LQMT）首次公开预发布。

Windows 安装包与问题反馈均在 GitCode。GitHub 为源码镜像。

本版本计算口径：

- Ra（CIE 13.3 / GB/T 26180）：8 个特殊显色指数 Ri 先取整，再算术平均
- Rd 色样表对齐 Esposito Rd.xlsm RefData2 全精度，插值至 380–780 nm / 5 nm
- CQS / Qa：LuxPy `v9.0`（LuxPy 1.12.5）；课题组 SPD 数据集实测与 CQS 9.0.3 官方 Excel 一致度 99.7%
- Sneutral：CIE 1964 10°
- CCT：Ohno 2014 / Robertson 2023
- LuxPy 锁定 1.12.5
