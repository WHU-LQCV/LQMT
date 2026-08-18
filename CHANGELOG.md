# 更新记录

## 1.0.0 (2026-08-18)

LQCV 光品质指标工具箱（LQMT）首次公开预发布。主仓为 Gitee，GitHub 为镜像。

本版本计算口径：

- Ra（CIE 13.3 / GB/T 26180）：8 个特殊显色指数 Ri 先取整，再算术平均
- Rd 色样表对齐 Esposito Rd.xlsm RefData2 全精度，插值至 380–780 nm / 5 nm
- CQS 使用 LuxPy `v9.0`（近似 CQS 9.0.3）
- Sneutral 使用 CIE 1964 10°
- LuxPy 锁定 1.12.5

CCT 算法差异与未实现的 CDM_e 见 `docs/known-limitations.md`。
