# 计算方法说明（LQMT v1.0.0）

本文面向需要核对算法、撰写对齐报告或二次开发的读者。日常下载与使用见仓库首页与 [user-manual.md](user-manual.md)。

对齐报告请写明：**LQMT v1.0.0**，并以本仓库对应 tag 的源码为准。

## CCT

本版本 CCT 使用 LuxPy 的 Ohno 2014 / Robertson 2023 路径。报告中请同时写明算法名称与 LQMT tag。

## CQS / Qa

MCPI 使用 CQS Qa。本版本调用 LuxPy `version='v9.0'`（LuxPy 1.12.5）。

课题组 SPD 数据集实测与 CQS 9.0.3 官方 Excel 一致度 99.7%（1009 条光谱对照，平均绝对差 0.003）。

## Sneutral 观察者

本版本 Sneutral 使用 CIE 1964 10°（Smet 模型原始定义）。对齐报告请按本 tag 口径注明观察者。

## Ra 取整

Ra 按 CIE 13.3 / GB/T 26180 报出口径：对 8 个特殊显色指数 Ri **取整后再算术平均**。

## Rd 色样表

`metrics/Rd.csv` 对齐 Esposito 工具 RefData2 全精度后插值到 380–780 nm / 5 nm。来源链见 [NOTICE](../NOTICE)。

## 范围

- 本工具计算光源光谱的颜色质量指标，不覆盖眩光、频闪、照度均匀性等其他维度。
- v1.0.0 提供图形界面；请以 GUI 计算结果为准。
