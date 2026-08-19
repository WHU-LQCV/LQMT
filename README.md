# LQCV 光品质指标工具箱

**LQCV Lighting Quality Metrics Toolbox (LQMT)**

从光源光谱功率分布（SPD）计算颜色质量指标：Ra、Rf、MCPI、CDM、MCPIr、CDMr 及分级等。

当前版本：**v1.0.0**  
许可：[GPL-3.0-only](LICENSE)

| | 地址 |
|---|---|
| **Windows 安装包** | [GitCode Releases](https://gitcode.com/WHU-LQCV/LQMT/releases) |
| 源码 | [GitCode](https://gitcode.com/WHU-LQCV/LQMT) · [GitHub](https://github.com/WHU-LQCV/LQMT)（镜像） |
| 问题反馈 | [GitCode Issues](https://gitcode.com/WHU-LQCV/LQMT/issues) |

## 企业用户：下载可执行文件

1. 打开 GitCode [Releases](https://gitcode.com/WHU-LQCV/LQMT/releases) 中的 **v1.0.0**。
2. 下载 `LQCV-LQMT-v1.0.0-windows-x64.zip`（一个文件即可；不要下 Source code）。
3. 解压后进入 `LQCV-LQMT` 文件夹，双击 `LQCV-LQMT.exe`。

可将 `lqcv_lqmt_config.json` 放在 exe 同级目录以保留配置。

macOS / Linux 请从源码运行。

对齐数值时请写明：**LQMT v1.0.0**。

## 从源码运行

需要 Python 3.9+（建议 3.10–3.12）。

```bash
git clone https://gitcode.com/WHU-LQCV/LQMT.git
cd LQMT
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

## 本版本计算口径

| 项目 | 做法 |
|------|------|
| Ra | CIE 13.3 / GB/T 26180；8 个 Ri 取整后再平均 |
| Rf | CIE 224:2017 / IES TM-30（LuxPy `cierf`） |
| Qa / CQS | LuxPy CQS `v9.0`（LuxPy 1.12.5） |
| Sneutral | CIE 1964 10° |
| CCT | Ohno 2014 / Robertson 2023 |
| LuxPy | 锁定 `1.12.5` |

操作说明见 [docs/user-manual.md](docs/user-manual.md)。

## 许可证与二次分发

源码与 Windows 可执行文件均按 **GPL-3.0-only** 发行。

- **允许**：下载官方 exe 计算并对齐；阅读源码核对算法；通过 GitCode Issue 反馈。
- **若修改后再对外发布**（改过的 exe，或把改动版嵌进仪器软件并分发）：通常须按 GPL 提供对应源码。详见 [NOTICE](NOTICE)。

请引用 LuxPy：Smet, K. A. G. (2020). Tutorial: The LuxPy Python Toolbox for Lighting and Color Science. *LEUKOS*.

## 引用本工具

见 [CITATION.cff](CITATION.cff)。软件版本请使用 `1.0.0`。

## English

LQMT computes spectral colour-quality metrics from SPD data. **Windows package and issues:** [GitCode](https://gitcode.com/WHU-LQCV/LQMT). GitHub is a source mirror.

License: GPL-3.0-only (required by LuxPy GPLv3). See `NOTICE` for third-party credits.

## 目录

```
LQMT/
├── run_gui.py
├── gui_app/          GUI
├── metrics/          自定义指标与色样表
├── examples/         合成示例 SPD
├── docs/             使用说明
└── pack/             Windows 打包脚本
```

## 贡献与问题

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。
