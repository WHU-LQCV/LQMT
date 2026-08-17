#!/usr/bin/env python

import numpy as np
import luxpy as lx
# import spectral_databases as dat
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
#Gamut Area Index
def calc_GAI(SPD):
    cri_rfl=lx._CRI_RFL['cie-13.3-1995']['8']['5nm'][:,4:-10]

    _mask = np.logical_and(SPD[0, :] >= 380, SPD[0, :] <= 780)
    _wl_clip = SPD[0, _mask]
    _pwr_clip = SPD[1, _mask]
    _wl_target = np.arange(380, 781, 5, dtype=float)
    SPD = np.vstack([_wl_target, np.interp(_wl_target, _wl_clip, _pwr_clip)])
    xyz_SPD = lx.spectrum.spd_to_xyz(SPD, rfl=cri_rfl)
    uv = lx.xyz_to_Yuv76(xyz=xyz_SPD)  # CIE 1976 u'v' diagram
    gamut_uv = uv.reshape(8, 3)
    return Polygon(gamut_uv[:, 1:]).area / 0.0000728468

    # gamut_uv=np.zeros((8,3))
    # for row in range(0,8):
    #     SPDc=np.vstack([range(380,781,5),SPD*cri_rfl[row+1]])
    #     xyz_SPD=lx.spectrum.spd_to_xyz(SPDc,relative=True)
    #     uv=lx.color.ctf.colortransforms.xyz_to_Yuv(xyz_SPD)
    #     gamut_uv[row]=uv
    # return Polygon(gamut_uv[:,1:]).area/0.0000736874664