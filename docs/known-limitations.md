# 已知限制（LQMT v1.0.0）

LQMT 是学术参考实现，不代表国家标准文本。

## CCT 算法

本版本代码使用 LuxPy 的 Ohno 2014 / Robertson 2023 路径，不能代表 GB/T 39394。

## CQS / Qa

MCPI 使用 CQS Qa。本版本调用 LuxPy `version='v9.0'`，用以近似 CQS 9.0.3。与 NIST/Excel 9.0.3 在个别光源上可能存在微小差异。

## Sneutral 观察者

本版本 Sneutral 使用 CIE 1964 10°（Smet 模型原始定义）。若某份标准文本写 CIE 1931 2°，以本仓库 tag 说明的口径为准，并在对齐报告中注明。

## Ra 取整

Ra 按 CIE 13.3 / GB/T 26180 报出口径：对 8 个特殊显色指数 Ri **取整后再算术平均**。

## Rd 色样表

`metrics/Rd.csv` 对齐 Esposito 工具 RefData2 全精度后插值到 380–780 nm / 5 nm。来源链见 [NOTICE](../NOTICE)。若权利人提出异议，后续版本可能更换色样并产生 breaking change。

## 未实现或未作为产品列展示的内容

- 本工具不计算眩光、频闪、照度均匀性等非光谱颜色质量指标。
- v1.0.0 仅提供图形界面；请以 GUI 计算结果为准。
