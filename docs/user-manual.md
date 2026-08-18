# 用户手册（简要）

## 启动

- Windows 发行包：从 Gitee Releases 下载并解压 `LQCV-LQMT-v1.0.0-windows-x64.zip`，进入 `LQCV-LQMT`，运行 `LQCV-LQMT.exe`。
- 源码：安装 `requirements.txt` 后执行 `python run_gui.py`。

窗口标题为「LQCV 光品质指标工具箱 v1.0.0」。配置文件默认名为 `lqcv_lqmt_config.json`，与 exe 或工作目录同级。

## 输入 SPD

- 第一列为波长（nm），后续列为各样品相对光谱功率。
- 建议覆盖 380–780 nm；范围不足时程序在两端补零。
- 可用粘贴、CSV，或「示例数据」。仓库 `examples/` 另提供合成双峰 LED 示例。

## 输出

结果表包含 CCT、Duv、色度坐标、Ra、Rf、MCPI、CDM、MCPIr、CDMr、A/B/C/D 分级，以及其他可选指标（Rg、CQS、GAI、Rd 等）。可导出 Excel / CSV，并打开可视化窗口。

界面中的 CMF 选项**只改变** x, y, u′, v′ 辅助列；Ra、Rf、MCPI 等核心指标按各自标准固定观察者。

## 对齐建议

1. 记录 LQMT 版本 tag（例如 `v1.0.0`）和 LuxPy 1.12.5。
2. 记录 SPD 波长范围与间隔。
3. 阅读 [known-limitations.md](known-limitations.md)，尤其是 CCT 与 CDM_e。
4. 不要把本工具表述为「国标委官方软件」或「与国标逐字一致」。
