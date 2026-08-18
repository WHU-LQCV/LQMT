# 首次发布：Gitee 主仓 + GitHub 镜像

本地仓库：`d:\Waxwell\LQMT`（分支 `main`，tag `v1.0.0`）  
Windows 包：`d:\Waxwell\LQMT\dist\LQCV-LQMT-v1.0.0-windows-x64.zip`

约定：

- `origin` → Gitee 主仓 `https://gitee.com/WHU-LQCV/LQMT.git`
- `github` → GitHub 镜像 `https://github.com/WHU-LQCV/LQMT.git`
- Issues / 企业下载 / 对齐引用 → **只认 Gitee**
- GitHub 仅同步源码与 tag，关闭 Issues（或置顶指向 Gitee）

当前 Gitee 账号（MCP 已登录）：`sherwinwu`。组织 `WHU-LQCV` 需在网页创建后才能把仓库放到组织下。

## A. Gitee 主仓

### 1. 创建组织

打开 https://gitee.com/organizations/new

- 组织路径：`WHU-LQCV`
- 名称：LQCV, Wuhan University
- 简介：武汉大学 LQCV 课题组学术参考实现，不要写「武汉大学官方」

创建后把导师加成管理者，把 `sherwinwu` 留作日常维护。

公开仓库可能需要实名认证；审核通过前对外可能暂时不可见。

### 2. 建仓库并推送

网页：组织内新建仓库 `LQMT`，公开，许可证 GPL-3.0，不要勾选「用 README 初始化」。

```bat
cd /d d:\Waxwell\LQMT
git remote remove origin
git remote add origin https://gitee.com/WHU-LQCV/LQMT.git
git push -u origin main
git push origin v1.0.0
```

### 3. 上传 Windows 发行包

Gitee 仓库 → 发行版 → 新建发行：

- 标签：`v1.0.0`
- 标题：LQCV光品质指标工具箱 v1.0.0
- 勾选预发布（若有）
- 正文用 `docs/release-notes-v1.0.0.md`
- 附件：`dist\LQCV-LQMT-v1.0.0-windows-x64.zip` 与 `.sha256`

## B. GitHub 镜像

### 1. 创建组织与空仓库

https://github.com/account/organizations/new → `WHU-LQCV`（Owner 建议开 2FA）  
再建空仓库 `LQMT`（Public，不要初始化 README）。

仓库 Settings：

- About：LQCV Lighting Quality Metrics Toolbox（mirror of Gitee）
- Homepage：https://gitee.com/WHU-LQCV/LQMT
- **Features → 关闭 Issues 和 Wiki**

### 2. 推送镜像

```bat
cd /d d:\Waxwell\LQMT
git remote add github https://github.com/WHU-LQCV/LQMT.git
git push github main
git push github v1.0.0
```

GitHub Release 可以同样挂 zip，方便境外下载；说明里第一句写「国内请用 Gitee」。

登录 CLI（可选）：

```bat
d:\Waxwell\tools\bin\gh.exe auth login -h github.com -p https -w
powershell -File pack\publish_github_mirror.ps1
```

## 日常同步

先推 Gitee，再推 GitHub：

```bat
git push origin main
git push origin v1.0.0
git push github main
git push github v1.0.0
```
