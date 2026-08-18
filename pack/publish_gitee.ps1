# Push LQMT to the Gitee canonical remote.
# Prerequisite: org WHU-LQCV and empty repo LQMT already exist.
# Usage: powershell -File pack\publish_gitee.ps1

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$remote = "https://gitee.com/WHU-LQCV/LQMT.git"
$existing = git remote 2>$null
if ($existing -notcontains "origin") {
    git remote add origin $remote
} else {
    git remote set-url origin $remote
}

git push -u origin main
git push origin v1.0.0
Write-Host "Pushed to $remote"
Write-Host "Upload dist\LQCV-LQMT-v1.0.0-windows-x64.zip on the Gitee Releases page."
