"""Windows onedir build for LQCV-LQMT. Run from repository root or via pack/build_windows.bat.

Gitee community releases cap a single attachment at about 100 MB. This script
always writes the full zip, then splits it into 90 MiB parts for Gitee upload.
"""

from __future__ import annotations

import os
import sys
import zipfile
import hashlib
import subprocess
from pathlib import Path


APP_NAME = "LQCV-LQMT"
VERSION = "1.1.0"
# Stay under Gitee's ~100 MB attachment cap (decimal or binary).
PART_SIZE = 90 * 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_join_helpers(dist_dir: Path, zip_name: str) -> None:
    """Write merge helpers. Do not upload .bat to Gitee; its CDN rejects that type."""
    bat = "\r\n".join(
        [
            "@echo off",
            "setlocal EnableDelayedExpansion",
            'cd /d "%~dp0"',
            f"set PREFIX={zip_name}",
            'if exist "%PREFIX%" del "%PREFIX%"',
            "set LIST=",
            "for %%F in (%PREFIX%.00*) do (",
            "  if defined LIST (",
            '    set LIST=!LIST!+"%%F"',
            "  ) else (",
            "    set LIST=%%F",
            "  )",
            ")",
            "if not defined LIST (",
            "  echo Missing %PREFIX%.001",
            "  pause",
            "  exit /b 1",
            ")",
            "echo Merging !LIST!",
            'copy /b !LIST! "%PREFIX%"',
            "if errorlevel 1 (",
            "  echo Merge failed.",
            "  pause",
            "  exit /b 1",
            ")",
            "echo Extracting...",
            'tar -xf "%PREFIX%"',
            "if errorlevel 1 (",
            "  powershell -NoProfile -Command \"Expand-Archive -LiteralPath '%PREFIX%' -DestinationPath '.' -Force\"",
            ")",
            "echo Done. Open the LQCV-LQMT folder and run LQCV-LQMT.exe",
            "pause",
            "",
        ]
    )
    bat_bytes = bat.encode("ascii")
    (dist_dir / "join-and-extract.bat").write_bytes(bat_bytes)
    (dist_dir / "合并解压.bat").write_bytes(bat_bytes)

    note = (
        f"LQMT v{VERSION} Windows 分卷合并说明\r\n"
        "\r\n"
        "Gitee 无法在浏览器中直接下载 .bat。请只下载三个分卷：\r\n"
        f"  {zip_name}.001\r\n"
        f"  {zip_name}.002\r\n"
        f"  {zip_name}.003\r\n"
        "放到同一文件夹后，在该文件夹的地址栏输入 cmd 并回车，粘贴下面两行：\r\n"
        "\r\n"
        f"copy /b {zip_name}.001+{zip_name}.002+{zip_name}.003 {zip_name}\r\n"
        f"tar -xf {zip_name}\r\n"
        "\r\n"
        "然后进入 LQCV-LQMT 文件夹，运行 LQCV-LQMT.exe。\r\n"
        "不要下载 Source code 压缩包，那是源码不是安装包。\r\n"
    )
    (dist_dir / "合并说明.txt").write_bytes(b"\xef\xbb\xbf" + note.encode("utf-8"))

    helper_zip = dist_dir / "join-and-extract.zip"
    with zipfile.ZipFile(helper_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("join-and-extract.bat", bat_bytes)


def split_for_gitee(zip_path: Path) -> list[Path]:
    """Split zip into numbered parts that `copy /b` can rejoin."""
    dist_dir = zip_path.parent
    zip_name = zip_path.name
    for old in dist_dir.glob(zip_name + ".00*"):
        old.unlink()

    parts: list[Path] = []
    with zip_path.open("rb") as src:
        index = 1
        while True:
            chunk = src.read(PART_SIZE)
            if not chunk:
                break
            part_path = dist_dir / f"{zip_name}.{index:03d}"
            part_path.write_bytes(chunk)
            parts.append(part_path)
            index += 1
    write_join_helpers(dist_dir, zip_name)
    return parts


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)
    dist_dir = repo_root / "dist"
    spec_file = Path(__file__).resolve().parent / "windows.spec"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        str(spec_file),
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    out_dir = dist_dir / APP_NAME
    if not out_dir.exists():
        raise SystemExit(f"Missing output directory: {out_dir}")

    zip_name = f"{APP_NAME}-v{VERSION}-windows-x64.zip"
    zip_path = dist_dir / zip_name
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in out_dir.rglob("*"):
            if file.is_file():
                zf.write(file, Path(APP_NAME) / file.relative_to(out_dir))

    digest = sha256_file(zip_path)
    (dist_dir / f"{zip_name}.sha256").write_text(
        f"{digest}  {zip_name}\n", encoding="ascii"
    )
    print(f"Wrote {zip_path}")
    print(f"SHA256 {digest}")

    parts = split_for_gitee(zip_path)
    print("Gitee attachments (each < 100 MB):")
    for part in parts:
        print(f"  {part.name}  {part.stat().st_size} bytes")
    print("  合并说明.txt")
    print("  join-and-extract.zip")
    print("Do not upload .bat files to Gitee; the download CDN rejects them.")
    print("Keep the full zip locally; do not upload it to Gitee.")


if __name__ == "__main__":
    main()
