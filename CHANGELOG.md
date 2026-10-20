# 更新记录

## 1.0.1 (2026-10-20)

基础色度列增加两项，观察者都跟随界面里的 CMF：

- p_e：激发纯度。无彩色点为同一观察者下的 CIE D65，紫色刺激取紫边界。单位为 1。测试初期曾用等能白 E，已改为 D65。结果页、配置页、表头和导出列名标明为 `p_e (D65)`
- h_ab：光源 Y=100 的 XYZ 相对同一观察者 D65 的 CIE 1976 a*b* 色调角，单位为度。落在 D65 上时无定义

界面字体没有 Unicode 下标，只有 p_e 和 h_ab 用下划线表示下标，其余指标名称保持原样。

Windows 安装包：`LQCV-LQMT-v1.0.1-windows-x64.zip`，发布在 GitCode Releases，GitHub 同步一份。

打包只生成一个 zip，不再为 Gitee 分卷。修复 SciPy 1.18 在冻结程序里缺少 `array_api_compat.numpy.fft` 导致 exe 无法启动的问题。

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
