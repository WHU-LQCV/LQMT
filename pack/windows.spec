# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for LQCV-LQMT. Paths are relative to this file / repo root."""

import importlib.util
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

SPECDIR = Path(SPECPATH).resolve()
ROOT = SPECDIR.parent

APP_NAME = "LQCV-LQMT"


def _pkg_dir(name: str):
    spec = importlib.util.find_spec(name)
    if spec and spec.origin:
        return Path(spec.origin).parent
    return None


datas = [
    (str(ROOT / "metrics" / "Rd.csv"), "metrics"),
    (str(ROOT / "metrics" / "Ob.csv"), "metrics"),
    (str(ROOT / "metrics" / "GVI_samples.txt"), "metrics"),
]

for pkg in ("resampy", "luxpy"):
    p = _pkg_dir(pkg)
    if not p:
        continue
    data_dir = p / "data"
    if data_dir.exists():
        datas.append((str(data_dir), f"{pkg}/data"))
    if pkg == "luxpy":
        tb = p / "toolboxes"
        if tb.exists():
            datas.append((str(tb), "luxpy/toolboxes"))

hiddenimports = [
    "luxpy",
    "luxpy.toolboxes",
    "luxpy.toolboxes.photbiochem",
    "luxpy.color",
    "luxpy.color.cam",
    "luxpy.spectrum",
    "luxpy.color.cri",
    "numpy",
    "numpy.fft",
    "pandas",
    "scipy",
    "scipy.interpolate",
    "scipy.optimize",
    "scipy.special",
    "scipy.linalg",
    # SciPy 1.18 loads these with __import__, which PyInstaller does not trace.
    "scipy._external.array_api_compat.numpy.fft",
    "scipy._external.array_api_compat.numpy.linalg",
    "shapely",
    "shapely.geometry",
    "resampy",
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "openpyxl",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.scrolledtext",
    "metrics.CDI",
    "metrics.GVI",
    "metrics.GAI",
    "metrics.CPKhanh",
    "metrics.Rd",
    "metrics.Sneutral",
    "metrics.smet_white_loci",
    "reference_illuminant_utils",
    "spd_utils",
    "gui_app",
    "gui_app.main_window",
    "gui_app.core_engine",
    "gui_app.data_parser",
    "gui_app.config",
    "gui_app.utils",
    "gui_app.visualizer",
    "gui_app.result_exporter",
    "numba",
    "llvmlite",
]
hiddenimports += collect_submodules("scipy._external.array_api_compat")
hiddenimports += collect_submodules("scipy._lib")

excludes = [
    "matplotlib.tests",
    "numpy.tests",
    "pandas.tests",
    "scipy.tests",
    "PIL.tests",
    "pytest",
    "IPython",
    "jupyter",
    "cv2",
    "xlwings",
]

a = Analysis(
    [str(ROOT / "run_gui.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)
