#!/usr/bin/env python
import os
import sys
import numpy as np
import luxpy as lx
import resampy
import scipy


def _get_gvi_samples_path():
    candidates = []
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        candidates.append(os.path.join(base_path, 'metrics', 'GVI_samples.txt'))
        candidates.append(os.path.join(base_path, 'GVI_samples.txt'))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(current_dir, 'GVI_samples.txt'))
    candidates.append(os.path.join(os.getcwd(), 'GVI_samples.txt'))
    candidates.append(os.path.join(os.getcwd(), 'metrics', 'GVI_samples.txt'))
    for path in candidates:
        if os.path.exists(path):
            return path
    return os.path.join(current_dir, 'GVI_samples.txt')


def calc_GVI(SPD):
    txt = np.loadtxt(_get_gvi_samples_path())
    SPD = SPD[1, np.logical_and(SPD[0, :] >= 400, SPD[0, :] <= 700)]
    SPD = resampy.resample(SPD, len(SPD), 31)
    SPD = np.vstack([range(400, 701, 10), SPD])
    rfl = np.vstack([range(400, 701, 10), txt / 100])
    xyz_SPD = lx.spectrum.spd_to_xyz(SPD, relative=True, rfl=rfl)
    xyzw_SPD = lx.spectrum.spd_to_xyz(SPD, relative=True)
    ab = lx.xyz_to_lab(xyz=xyz_SPD, xyzw=xyzw_SPD)
    gamut_ab = ab.reshape(14, 3)
    return 5 / 10000 * scipy.spatial.ConvexHull(gamut_ab).volume
