import numpy as np
import luxpy as lx
# import spectral_databases as dat
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from pandas import read_csv, DataFrame
import math
import os
import sys
#Rd

def _get_rd_csv_path():
    """
    智能查找 Rd.csv 文件路径
    兼容开发环境和 PyInstaller 打包环境
    """
    # 候选路径列表（按优先级排序）
    candidates = []
    
    # 1. PyInstaller 打包环境：使用 _MEIPASS
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        candidates.append(os.path.join(base_path, 'metrics', 'Rd.csv'))
        candidates.append(os.path.join(base_path, 'Rd.csv'))
    
    # 2. 相对于当前文件的路径（适用于模块导入）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(current_dir, 'Rd.csv'))
    
    # 3. 当前工作目录（适用于开发环境直接运行）
    candidates.append(os.path.join(os.getcwd(), 'Rd.csv'))
    candidates.append(os.path.join(os.getcwd(), 'metrics', 'Rd.csv'))
    
    # 4. 简单相对路径（开发环境备选）
    candidates.append('Rd.csv')
    
    # 查找第一个存在的文件
    for path in candidates:
        if os.path.exists(path):
            return path
    
    # 如果都找不到，返回默认路径（让 pandas 报错）
    return 'Rd.csv'

def calc_Rd(SPD):
    rd_csv_path = _get_rd_csv_path()
    Read = read_csv(rd_csv_path) # (1+85) * 81[380:5:780]
    FM_rfl = Read.values
    _mask = np.logical_and(SPD[0, :] >= 380, SPD[0, :] <= 780)
    _wl_clip = SPD[0, _mask]
    _pwr_clip = SPD[1, _mask]
    _wl_target = np.arange(380, 781, 5, dtype=float)
    SPD = np.vstack([_wl_target, np.interp(_wl_target, _wl_clip, _pwr_clip)])
    A = []  # [1,22]
    B = []  # [23,43]
    C = []  # [44,64]
    D = []  # [65,85]
    xyz = lx.spd_to_xyz(SPD, cieobs='1964_10', relative=True, rfl=FM_rfl)
    xyzw = lx.spd_to_xyz(SPD, relative=True, cieobs='1964_10')
    pars = {
        'D': 1,
        'Dtype': None,
        'La': 100.0,
        'Yb': 20.0,
        'surround': 'avg'}
    # JabM = lx.xyz_to_jab_cam02ucs(xyz, xyzw=xyzw, conditions=pars)
    JabM = lx.color.cam.cam02ucs(xyz, xyzw=xyzw, conditions=pars, Yw=100, ucstype='ucs',
                                 mcat='cat02')

    for i in range(JabM.shape[0]):
        hi = {'id': int, 'hue': float}
        hi['id'] = i
        hi['hue'] = lx.color.cam.hue_angle(JabM[i, 0, 1], JabM[i, 0, 2], htype='deg')
        # if hi['hue'] < 0:
        #     hi['hue'] = 360 + hi['hue']
        if i < 22:
            A.append(hi)
        elif i < 43:
            B.append(hi)
        elif i < 64:
            C.append(hi)
        else:
            if hi['hue'] < 180:
                hi['hue'] = 360 + hi['hue']
            D.append(hi)
    Aorder = sorted(A, key=lambda i: i['hue'])
    Border = sorted(B, key=lambda i: i['hue'])
    Corder = sorted(C, key=lambda i: i['hue'])
    Dorder = sorted(D, key=lambda i: i['hue'])
    a = [2 * (21 + Aorder[0]['id'] - Aorder[-1]['id'])]
    for i in range(len(Aorder)-1):
        a.append(2 * (abs(Aorder[i+1]['id'] - Aorder[i]['id']) -1))
    b = [2 * (20 + Border[0]['id'] - Border[-1]['id'])]
    c = [2 * (20 + Corder[0]['id'] - Corder[-1]['id'])]
    d = [2 * (20 + Dorder[0]['id'] - Dorder[-1]['id'])]
    for i in range(len(Border)-1):
        b.append(2 * (abs(Border[i+1]['id'] - Border[i]['id']) -1))
        c.append(2 * (abs(Corder[i+1]['id'] - Corder[i]['id']) -1))
        d.append(2 * (abs(Dorder[i+1]['id'] - Dorder[i]['id']) -1))
    Rd = sum(a) + sum(b) + sum(c) + sum(d)
    return Rd