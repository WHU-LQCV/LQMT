# Push LQMT to the GitHub mirror. Gitee remains canonical.
# Prerequisite: gh auth login, org WHU-LQCV, empty repo LQMT, Issues disabled.
# Usage: powershell -File pack\publish_github_mirror.ps1

$ErrorActionPreference = "Stop"
$Gh = "d:\Waxwell\tools\bin\gh.exe"
if (-not (Test-Path $Gh)) {
    $found = Get-Command gh -ErrorAction SilentlyContinue
    if ($found) { $Gh = $found.Source } else { throw "gh not found. Run gh auth login first." }
}

Set-Location (Join-Path $PSScriptRoot "..")
& $Gh auth status

$remote = "https://github.com/WHU-LQCV/LQMT.git"
$existing = git remote
if ($existing -notcontains "github") {
    git remote add github $remote
} else {
    git remote set-url github $remote
}

git push github main
git push github v1.0.0

$notes = @"
国内用户请从 Gitee 主仓下载与反馈：https://gitee.com/WHU-LQCV/LQMT

This GitHub repository is a mirror. File issues on Gitee.

$(Get-Content -Raw docs\release-notes-v1.0.0.md)
"@
$notesFile = Join-Path $env:TEMP "lqmt-gh-release.md"
Set-Content -Path $notesFile -Value $notes -Encoding utf8

& $Gh release create v1.0.0 --repo WHU-LQCV/LQMT --prerelease --title "LQCV光品质指标工具箱 v1.0.0" --notes-file $notesFile "dist\LQCV-LQMT-v1.0.0-windows-x64.zip" "dist\LQCV-LQMT-v1.0.0-windows-x64.zip.sha256"
Write-Host "Mirror pushed: https://github.com/WHU-LQCV/LQMT"
