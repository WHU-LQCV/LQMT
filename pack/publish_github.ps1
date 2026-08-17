# After: gh auth login, and org WHU-LQCV exists.
# Usage: powershell -File pack\publish_github.ps1

$ErrorActionPreference = "Stop"
$Gh = "d:\Waxwell\tools\bin\gh.exe"
if (-not (Test-Path $Gh)) {
    $found = Get-Command gh -ErrorAction SilentlyContinue
    if ($found) { $Gh = $found.Source } else { throw "gh not found. Run gh auth login first." }
}

Set-Location (Join-Path $PSScriptRoot "..")

& $Gh auth status
& $Gh repo create WHU-LQCV/LQMT --public --source=. --remote=origin --push --description "LQCV Lighting Quality Metrics Toolbox (academic reference implementation)"
git push origin v1.0.0
& $Gh release create v1.0.0 --prerelease --title "LQCV光品质指标工具箱 v1.0.0" --notes-file docs\release-notes-v1.0.0.md "dist\LQCV-LQMT-v1.0.0-windows-x64.zip" "dist\LQCV-LQMT-v1.0.0-windows-x64.zip.sha256"
Write-Host "Done: https://github.com/WHU-LQCV/LQMT/releases/tag/v1.0.0"
