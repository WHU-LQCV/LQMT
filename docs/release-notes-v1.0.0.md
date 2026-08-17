本公开版本基于课题组内部测试包 `dist_260727`（本地开发号 1.3.2）整理发布。对外对齐请使用 GitHub tag **v1.0.0**。

## 下载

Windows：`LQCV-LQMT-v1.0.0-windows-x64.zip`

解压后进入 `LQCV-LQMT` 文件夹，运行 `LQCV-LQMT.exe`。

SHA256：`dc7b15cebb881deeab9c5a5a36c40f7dba4dee77108bb1b8515baf0964b9551b`

## 口径要点

- Ra：8 个 Ri 取整后再平均（CIE 13.3 / GB/T 26180 报出口径）
- Rd 色样：Esposito RefData2 全精度，插值至 380–780 nm / 5 nm
- CQS：LuxPy v9.0（近似 9.0.3）；LuxPy 锁定 1.12.5
- Sneutral：CIE 1964 10°
- CCT：Ohno 2014 / Robertson 2023，与 GB/T 39394 不完全相同
- CDM_e：本版本未作为产品列输出

详见 `docs/known-limitations.md`。

## 定位

武汉大学 LQCV 课题组学术参考实现。不是国家标准文本，不是标委会官方软件。未经计量器具型式评价。许可 GPL-3.0-only（因依赖 LuxPy GPLv3）。
