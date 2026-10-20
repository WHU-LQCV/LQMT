"""Windows onedir build for LQCV-LQMT. Run from repository root or via pack/build_windows.bat.

Writes one zip. Distribution no longer uses Gitee, so the archive is not split.
"""

from __future__ import annotations

import os
import sys
import zipfile
import hashlib
import subprocess
from pathlib import Path


APP_NAME = "LQCV-LQMT"
VERSION = "1.0.1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
    for stale in dist_dir.glob(zip_name + ".00*"):
        stale.unlink()
    print(f"Wrote {zip_path}")
    print(f"SHA256 {digest}")


if __name__ == "__main__":
    main()
