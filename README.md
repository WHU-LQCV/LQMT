# LQCV 光品质指标工具箱

**LQCV Lighting Quality Metrics Toolbox (LQMT)**

武汉大学 LQCV 课题组发布的**学术参考实现**，从光源光谱功率分布（SPD）计算颜色质量指标（Ra、Rf、MCPI、CDM、MCPIr、CDMr 及分级等）。

本工具计算的是**光源光谱的颜色质量指标**，不覆盖眩光、频闪等其他光品质维度。

> **不是**国家标准文本，**不是**标准化行政主管部门或标委会官方软件。与正式出版的 GB/Z / GB/T 文本冲突时，以正式出版物为准。  
> 本工具**未经计量器具型式评价**。仪器厂对齐时应锁定本仓库 tag，并自行复测。

当前公开版本：**v1.0.0**（预发布）  
**主仓（国内下载与 Issue）：** https://gitee.com/WHU-LQCV/LQMT  
**镜像（国际可见）：** https://github.com/WHU-LQCV/LQMT  
许可：[GPL-3.0-only](LICENSE)（因依赖 [LuxPy](https://github.com/ksmet1977/luxpy)，亦为 GPLv3）

问题与建议请只在 **Gitee Issues** 提交，避免两处反馈分裂。

## 企业用户：下载可执行文件

Gitee 开源仓库单个发行附件上限约 100 MB，完整 Windows 包超过该限制，因此拆成若干分卷。请**全部下载**后再合并。

1. 打开 Gitee [Releases](https://gitee.com/WHU-LQCV/LQMT/releases) 中的 **v1.0.0**。
2. 下载全部 `LQCV-LQMT-v1.0.0-windows-x64.zip.00*` 分卷（不要下 Source code，也不要下 `.bat`）。
3. 放到同一文件夹。在资源管理器地址栏输入 `cmd` 回车，执行：

```bat
copy /b LQCV-LQMT-v1.0.0-windows-x64.zip.001+LQCV-LQMT-v1.0.0-windows-x64.zip.002+LQCV-LQMT-v1.0.0-windows-x64.zip.003 LQCV-LQMT-v1.0.0-windows-x64.zip
tar -xf LQCV-LQMT-v1.0.0-windows-x64.zip
```

4. 进入解压出的 `LQCV-LQMT` 文件夹，双击 `LQCV-LQMT.exe`。
5. 可将 `lqcv_lqmt_config.json` 放在 exe 同级目录以保留配置。

请勿只下载其中一个分卷，也无法直接解压 `.001` 文件。完整 zip 的 SHA256 写在发行说明中。

macOS / Linux 本轮不提供官方安装包，请从源码运行。

对齐数值时请在报告中写明：**LQMT v1.0.0**（https://gitee.com/WHU-LQCV/LQMT）。

## 从源码运行

需要 Python 3.9+（建议 3.10–3.12）。

```bash
git clone https://gitee.com/WHU-LQCV/LQMT.git
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
| CCT | Ohno 2014 / Robertson 2023（**不能代表 GB/T 39394**，见已知限制） |
| LuxPy | 锁定 `1.12.5` |

完整说明见 [docs/known-limitations.md](docs/known-limitations.md)。

## 许可证与二次分发

源码与 Windows 可执行文件均按 **GPL-3.0-only** 发行。

- **允许**：下载官方 exe 计算并对齐；阅读源码核对算法；通过 Gitee Issue 反馈偏差。
- **若修改后再对外发布**（改过的 exe，或把改动版嵌进仪器软件并分发）：通常须按 GPL 提供对应源码。详见 [NOTICE](NOTICE)。以上说明**不是律师意见**。

请引用 LuxPy：Smet, K. A. G. (2020). Tutorial: The LuxPy Python Toolbox for Lighting and Color Science. *LEUKOS*.

## 引用本工具

见 [CITATION.cff](CITATION.cff)。软件版本请使用 `1.0.0`。代码主地址请引用 Gitee。

## English

LQMT is an **academic reference implementation** from the LQCV laboratory at Wuhan University. **Canonical repository and issue tracker: [Gitee](https://gitee.com/WHU-LQCV/LQMT).** This GitHub copy is a read-only mirror for international access. Please file issues on Gitee.

It computes spectral colour-quality metrics from SPD data. It is **not** the national standard text and **not** official software of any standards body.

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

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。
