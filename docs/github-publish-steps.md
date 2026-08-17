# GitHub 首次发布（需你本人登录）

本地仓库已就绪：`d:\Waxwell\LQMT`（分支 `main`，tag `v1.0.0`）。
Windows 包已生成：`d:\Waxwell\LQMT\dist\LQCV-LQMT-v1.0.0-windows-x64.zip`

创建 Organization 必须在网页完成，CLI 无法代替个人账号点确认。

## 1. 登录与 2FA

1. 打开 https://github.com/login
2. 账号设置 → Password and authentication → 开启 Two-factor authentication（创建 Org 通常要求 2FA）

本机已放置便携 `gh`：`d:\Waxwell\tools\bin\gh.exe`

```bat
d:\Waxwell\tools\bin\gh.exe auth login -h github.com -p https -w
```

按提示在浏览器完成授权。

## 2. 创建 Organization

打开 https://github.com/account/organizations/new

- Organization name: `WHU-LQCV`
- Contact email: 课题组邮箱
- 选 Free
- Display name / bio：LQCV, Wuhan University；写明是课题组参考实现，不要写 Official Wuhan University

创建后：Invite 导师为 Owner。

## 3. 建仓库并推送

```bat
cd /d d:\Waxwell\LQMT
d:\Waxwell\tools\bin\gh.exe repo create WHU-LQCV/LQMT --public --source=. --remote=origin --push --description "LQCV Lighting Quality Metrics Toolbox (academic reference implementation)"
git push origin v1.0.0
```

若 `repo create` 因 Org 权限失败，先在网页 New repository 建 `LQMT`（Public，加 GPL-3.0），再：

```bat
cd /d d:\Waxwell\LQMT
git remote add origin https://github.com/WHU-LQCV/LQMT.git
git push -u origin main
git push origin v1.0.0
```

## 4. 发布 Pre-release

```bat
cd /d d:\Waxwell\LQMT
d:\Waxwell\tools\bin\gh.exe release create v1.0.0 --prerelease --title "LQCV光品质指标工具箱 v1.0.0" --notes-file docs\release-notes-v1.0.0.md "dist\LQCV-LQMT-v1.0.0-windows-x64.zip" "dist\LQCV-LQMT-v1.0.0-windows-x64.zip.sha256"
```

仓库 Settings → About：填中文全称 + 英文全称；Topics 建议 `lighting-quality`、`color-rendering`、`cie`、`spd`。
