# 用户手册

## 启动

- Windows：从 GitCode [Releases](https://gitcode.com/WHU-LQCV/LQMT/releases) 下载 `LQCV-LQMT-v1.0.1-windows-x64.zip`，解压后进入 `LQCV-LQMT`，双击 `LQCV-LQMT.exe`。
- 源码：安装 `requirements.txt` 后执行 `python run_gui.py`。

窗口标题为「LQCV 光品质指标工具箱 v1.0.1」。配置文件默认名为 `lqcv_lqmt_config.json`，与 exe 或工作目录同级。

## 输入 SPD

- 第一列为波长（nm），后续列为各样品相对光谱功率。
- 建议覆盖 380–780 nm；范围不足时程序在两端补零。
- 可用粘贴、CSV，或「示例数据」。仓库 `examples/` 另提供合成双峰 LED 示例。

## 输出

结果表包含 CCT、Duv、色度坐标、激发纯度 p_e、CIELAB 色调角 h_ab、Ra、Rf、MCPI、CDM、MCPIr、CDMr、A/B/C/D 分级，以及其他可选指标（Rg、CQS、GAI、Rd 等）。可导出 Excel / CSV，并打开可视化窗口。

界面中的 CMF 选项改变 x、y、u′、v′、p_e、h_ab。Ra、Rf、MCPI 等核心指标按各自标准固定观察者。

p_e 是激发纯度，无量纲。无彩色点是当前 CMF 观察者下的 CIE D65，所以 2° 和 10° 的 D65 色品不同。结果页摘要、配置页观察者说明、指标勾选、结果表表头和导出列名都写成这个口径，表头为 `p_e (D65)`。紫色刺激的分母端点取紫边界，不取光谱轨迹。光源色品落在该 D65 上时 p_e 为 0。

h_ab 是把光源光谱按 Y=100 换成 XYZ 后，以同一观察者、同一波长网格上的 D65 为参考白算出的 CIE 1976 a*b* 色调角，单位为度。它不是物体色的 CIELAB 色调。光源色品落在该 D65 上时，a* 与 b* 都是 0，h_ab 无定义，结果显示为「—」。L* 对所有按 Y=100 归一的光源都是 100，不携带明度信息。

## 对齐时请记录

1. LQMT v1.0.1 和 LuxPy 1.12.5。
2. SPD 波长范围与间隔。
