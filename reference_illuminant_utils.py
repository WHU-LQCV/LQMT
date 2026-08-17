"""
根据 CCT 生成参考照明体工具函数
符合 CIE 224:2017 (IES TM-30-18) 标准
供 GUI 计算引擎调用
"""

import luxpy as lx
import numpy as np


def get_reference_illuminant_spd(cct, wl_start=380, wl_end=780, wl_step=1):
    """
    根据 CCT 生成参考照明体 SPD (符合 CIE 224:2017 标准)
    
    参数:
        cct: float - 相关色温 (K)
        wl_start: int - 起始波长 (nm), 默认 380
        wl_end: int - 结束波长 (nm), 默认 780
        wl_step: int - 波长步长 (nm), 默认 1
    
    返回:
        spd: ndarray - 参考照明体的 SPD
             spd[0] = 波长数组
             spd[1:] = 相对光谱功率
    
    计算规则:
        - CCT < 4000K: 使用普朗克辐射体
        - CCT > 5000K: 使用 CIE 日光照明体
        - 4000K ≤ CCT ≤ 5000K: 使用普朗克和日光的线性组合
    """
    
    # 生成波长数组
    wl3 = np.arange(wl_start, wl_end + wl_step, wl_step)
    
    if cct < 4000:
        # 使用普朗克辐射体
        spd_ref = lx.spectrum.blackbody(cct, wl3=wl3)
        
    elif cct > 5000:
        # 使用 CIE 日光照明体
        spd_ref = lx.spectrum.daylightphase(cct, wl3=wl3)
        
    else:
        # 4000K-5000K: 使用线性组合
        # 生成普朗克辐射体和日光照明体
        spd_planck = lx.spectrum.blackbody(cct, wl3=wl3)
        spd_daylight = lx.spectrum.daylightphase(cct, wl3=wl3)
        
        # 重标准化（归一化到 Y=100）
        xyz_planck = lx.spd_to_xyz(spd_planck, relative=False, cieobs='1931_2')
        xyz_daylight = lx.spd_to_xyz(spd_daylight, relative=False, cieobs='1931_2')
        
        # 归一化
        spd_planck_norm = spd_planck.copy()
        spd_planck_norm[1:, :] = 100 * spd_planck[1:, :] / xyz_planck[0, 1]
        
        spd_daylight_norm = spd_daylight.copy()
        spd_daylight_norm[1:, :] = 100 * spd_daylight[1:, :] / xyz_daylight[0, 1]
        
        # 线性组合权重
        T_b, T_c = 4000, 5000
        w_daylight = (cct - T_b) / (T_c - T_b)
        w_planck = (T_c - cct) / (T_c - T_b)
        
        # 组合 SPD
        spd_ref = spd_planck_norm.copy()
        spd_ref[1:, :] = w_daylight * spd_daylight_norm[1:, :] + w_planck * spd_planck_norm[1:, :]
    
    return spd_ref


def get_reference_type(cct):
    """
    获取给定 CCT 应使用的参考照明体类型
    
    参数:
        cct: float - 相关色温 (K)
    
    返回:
        str - 参考照明体类型: "Planckian", "Daylight", 或 "Mixed"
    """
    if cct < 4000:
        return "Planckian"
    elif cct > 5000:
        return "Daylight"
    else:
        return "Mixed"


# ============= 使用示例 =============
if __name__ == "__main__":
    print("=" * 60)
    print("参考照明体生成工具 - 使用示例")
    print("=" * 60)
    
    # 示例1: 生成 2700K 参考照明体
    print("\n示例1: 生成 2700K 参考照明体")
    cct1 = 2700
    spd1 = get_reference_illuminant_spd(cct1)
    ref_type1 = get_reference_type(cct1)
    print(f"CCT: {cct1}K")
    print(f"参考照明体类型: {ref_type1}")
    print(f"SPD 形状: {spd1.shape}")
    print(f"波长范围: {spd1[0, 0]:.0f} - {spd1[0, -1]:.0f} nm")
    
    # 示例2: 生成 4500K 参考照明体（混合）
    print("\n示例2: 生成 4500K 参考照明体（混合）")
    cct2 = 4500
    spd2 = get_reference_illuminant_spd(cct2)
    ref_type2 = get_reference_type(cct2)
    print(f"CCT: {cct2}K")
    print(f"参考照明体类型: {ref_type2}")
    
    # 验证计算的 CCT
    xyz2 = lx.spd_to_xyz(spd2, relative=True, cieobs='1931_2')
    cct2_calc = lx.xyz_to_cct(xyz2, out='cct')
    print(f"验证 CCT: {float(cct2_calc.flat[0]):.0f}K")
    
    # 示例3: 生成 6500K 参考照明体（日光）
    print("\n示例3: 生成 6500K 参考照明体（CIE D65）")
    cct3 = 6500
    spd3 = get_reference_illuminant_spd(cct3)
    ref_type3 = get_reference_type(cct3)
    print(f"CCT: {cct3}K")
    print(f"参考照明体类型: {ref_type3}")
    
    # 示例4: 自定义波长范围（5nm步长）
    print("\n示例4: 自定义波长范围（5nm步长）")
    cct4 = 5000
    spd4 = get_reference_illuminant_spd(cct4, wl_start=400, wl_end=700, wl_step=5)
    print(f"CCT: {cct4}K")
    print(f"波长范围: {spd4[0, 0]:.0f} - {spd4[0, -1]:.0f} nm")
    print(f"数据点数: {spd4.shape[1]}")
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)

