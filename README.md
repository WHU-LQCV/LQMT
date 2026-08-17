# LQCV 光品质指标工具箱

**LQCV Lighting Quality Metrics Toolbox (LQMT)**

武汉大学 LQCV 课题组发布的**学术参考实现**，从光源光谱功率分布（SPD）计算颜色质量指标（Ra、Rf、MCPI、CDM、MCPIr、CDMr 及分级等）。

本工具计算的是**光源光谱的颜色质量指标**，不覆盖眩光、频闪等其他光品质维度。

> **不是**国家标准文本，**不是**标准化行政主管部门或标委会官方软件。与正式出版的 GB/Z / GB/T 文本冲突时，以正式出版物为准。  
> 本工具**未经计量器具型式评价**。仪器厂对齐时应锁定本仓库 tag，并自行复测。

当前公开版本：**v1.0.0**（GitHub Pre-release）  
仓库：https://github.com/WHU-LQCV/LQMT  
许可：[GPL-3.0-only](LICENSE)（因依赖 [LuxPy](https://github.com/ksmet1977/luxpy)，亦为 GPLv3）

## 企业用户：下载可执行文件

1. 打开 [Releases](https://github.com/WHU-LQCV/LQMT/releases)。
2. 下载 `LQCV-LQMT-v1.0.0-windows-x64.zip`。
3. 解压后进入 `LQCV-LQMT` 文件夹，双击 `LQCV-LQMT.exe`。
4. 可将 `lqcv_lqmt_config.json` 放在 exe 同级目录以保留配置。

macOS / Linux 本轮不提供官方安装包，请从源码运行。

对齐数值时请在报告中写明：**LQMT v1.0.0**（https://github.com/WHU-LQCV/LQMT）。

## 从源码运行

需要 Python 3.9+（建议 3.10–3.12）。

```bash
git clone https://github.com/WHU-LQCV/LQMT.git
cd LQMT
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

## 计算口径（摘要）

| 项目 | 本版本做法 |
|------|------------|
| Ra | CIE 13.3 / GB/T 26180；8 个 Ri 取整后再平均 |
| Rf | CIE 224:2017 / IES TM-30（LuxPy `cierf`） |
| Qa / CQS | LuxPy CQS `v9.0`（近似 9.0.3） |
| Sneutral | CIE 1964 10° |
| CCT | Ohno 2014 / Robertson 2023（**与 GB/T 39394 不完全相同**，见已知限制） |
| LuxPy | 锁定 `1.12.5` |

完整说明见 [docs/known-limitations.md](docs/known-limitations.md)。验证方法概述：课题组用官方工具锚点、独立复算与回归测试维护口径；内部审计报告含未公开材料，不随本仓库发布。

## 许可证与二次分发

源码与 Windows 可执行文件均按 **GPL-3.0-only** 发行。

- **允许**：下载官方 exe 计算并对齐；阅读源码核对算法；通过 Issue 反馈偏差。
- **若修改后再对外发布**（改过的 exe，或把改动版嵌进仪器软件并分发）：通常须按 GPL 提供对应源码。详见 [NOTICE](NOTICE)。以上说明**不是律师意见**。

请引用 LuxPy：Smet, K. A. G. (2020). Tutorial: The LuxPy Python Toolbox for Lighting and Color Science. *LEUKOS*.

## 引用本工具

见 [CITATION.cff](CITATION.cff)。软件版本请使用 `1.0.0`。

## English

LQMT is an **academic reference implementation** from the LQCV laboratory at Wuhan University. It computes spectral colour-quality metrics from SPD data. It is **not** the national standard text and **not** official software of any standards body. Conflict with a formally published GB/Z or GB/T document is resolved in favour of that publication.

The Windows zip is the primary distribution for lighting manufacturers and instrument vendors. Source is provided so that algorithms can be inspected and issues filed.

License: GPL-3.0-only (required by LuxPy GPLv3). See `NOTICE` for third-party credits and data-file provenance.

## 目录

```
LQMT/
├── run_gui.py
├── gui_app/          GUI
├── metrics/          自定义指标与色样表
├── examples/         合成示例 SPD
├── docs/             用户说明与已知限制
└── pack/             Windows 打包脚本
```

## 贡献与问题

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，并使用 Issue 模板提交：数值偏差/对齐、exe 使用问题、功能建议。

首次把本仓库推到 GitHub 的操作说明见 [docs/github-publish-steps.md](docs/github-publish-steps.md)。
