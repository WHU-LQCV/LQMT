#!/usr/bin/env python
"""
CDI – 基于绝对色域的颜色分辨指数（Color Discrimination Index）
计算方法来源：颜色分辨指数 CDI76（CIE 1931 2° + CIE 1976 u′v′）

CMF：CIE 1931 2°（公式 81，固定，由 lx.spectrum.spd_to_xyz 默认使用）
SPD 波长范围：400–700 nm
采样间隔：5 nm（≤10 nm 即符合规范，5 nm 更精确）
8 个 CDI 试验色样（附录 H）：使用 luxpy _CRI_RFL['cie-13.3-1995']['8']['5nm']
公式 85：CDI = 100 × GAt / k_corr，k_corr = 0.005
"""

import numpy as np
import luxpy as lx
from shapely.geometry import Polygon

# 计算波长范围：400–700 nm，步长 5 nm
_WL_START = 400
_WL_END   = 700
_WL_STEP  = 5
_N_POINTS = (_WL_END - _WL_START) // _WL_STEP + 1  # 61
_WL_GRID  = list(range(_WL_START, _WL_END + _WL_STEP, _WL_STEP))

# kcorr（公式 85）
_K_CORR = 0.005


def calc_CDI(SPD):
    """
    计算 CDI（基于绝对色域的颜色分辨指数）。

    参数
    ----
    SPD : ndarray, shape (2, n)
        第 0 行为波长（nm），第 1 行为相对光谱功率。
        输入波长范围无限制，内部自动裁剪并重采样到 400–700 nm / 5 nm。

    返回
    ----
    float
        CDI 值。
    """
    # 1. 提取 SPD 数值行，裁剪到 400–700 nm
    wl_in  = SPD[0, :]
    pwr_in = SPD[1, :]
    mask = (wl_in >= _WL_START) & (wl_in <= _WL_END)
    wl_clip  = wl_in[mask]
    pwr_clip = pwr_in[mask]

    # 2. 线性插值到标准 5 nm 网格（61 点）
    pwr_resamp = np.interp(np.array(_WL_GRID, dtype=float), wl_clip, pwr_clip)
    spd_std = np.vstack([_WL_GRID, pwr_resamp])

    # 3. 取 8 个 CDI 试验色样反射率（400–700 nm，5 nm）
    cri_rfl = lx._CRI_RFL['cie-13.3-1995']['8']['5nm']
    cri_rfl = cri_rfl[:, (cri_rfl[0, :] >= _WL_START) & (cri_rfl[0, :] <= _WL_END)]

    # 4. 计算 8 个色样在被测照明体下的三刺激值（CIE 1931 2°，公式 81）
    xyz_spd = lx.spectrum.spd_to_xyz(spd_std, rfl=cri_rfl)

    # 5. 转换为 CIE 1976 u'v' 坐标（公式 82–83）
    uv = lx.xyz_to_Yuv76(xyz=xyz_spd)
    gamut_uv = uv.reshape(8, 3)[:, 1:]

    # 6. 计算 8 边形面积 GAt（公式 84）并归一化（公式 85）
    poly = Polygon(gamut_uv).area
    return poly / _K_CORR * 100
