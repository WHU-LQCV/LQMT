"""
核心计算引擎。

CMF（色匹配函数）策略:
  Ra        → CIE 1931 2°  (GB/T 26180 惯例，spd_to_cria 内部固定)
  CIE-Rf    → CIE 1964 10° (spd_to_cierf 内部固定)
  Qa        → CQS v9.0/9.0.3 口径（MCPI 原论文计算口径）
  CDI       → CIE 1931 2° + CIE 1976 u'v'（CDI76）
  Rd        → CIE 1964 10° (Rd.py 内部固定)
  Sneutral  → CIE 1964 10° (Smet 模型 xyz10 口径，固定不随全局 cieobs 变化)
  x,y,u',v',pe,hab → 由 cieobs 参数决定（辅助色度列，默认 1931_2）

全局 cieobs 参数仅作用于辅助色度列（x, y, u', v', pe, hab），
核心指标均已按上述规则固定，不受 UI CMF 切换影响。

pe：激发纯度。指定无彩色刺激为同一观察者下的全波段 CIE D65。
hab：把光源相对三刺激值（Y = 100）相对同一观察者的 D65 硬算 CIELAB，再取 a*b* 色调角。
"""

import luxpy as lx
import numpy as np
import pandas as pd
from pandas import DataFrame
from luxpy.color.cri.utils.helpers import spd_to_cri
from metrics import CDI, GVI, GAI, CPKhanh, Rd, Sneutral
from reference_illuminant_utils import get_reference_illuminant_spd
from spd_utils import pad_spd_to_range

# Sneutral 使用 Smet 模型原生的 CIE 1964 10° xyz10 口径。
_CMF_SNEUTRAL = '1964_10'
# MCPI 原论文实际计算使用 CQS 9.0.3；本版本 LuxPy version='v9.0'（1.12.5）。
_CQS_VERSION = 'v9.0'
def d65_white_xyz(cieobs='1931_2'):
    """同一观察者下全波段 CIE D65 的相对三刺激值。

    激发纯度的无彩色点用这个色品。它不随样品波长范围改变。
    """
    return lx.spd_to_xyz(lx._CIE_D65, relative=True, cieobs=cieobs)


def excitation_purity(xyz, cieobs='1931_2', xyzw=None):
    """激发纯度 pe，CIE S 017 17-23-066 的 NC/ND。

    N 为同一观察者下的 CIE D65。D 为 N 与样品色品的连线同光谱轨迹的交点；
    紫色刺激时 D 落在紫边界上。返回值无量纲，范围通常在 0 到 1。
    样品色品与该 D65 重合时纯度为 0。
    """
    if xyzw is None:
        xyzw = d65_white_xyz(cieobs)
    ydlep = np.asarray(
        lx.xyz_to_Ydlep(xyz, cieobs=cieobs, xyzw=xyzw),
        dtype=float,
    )
    return ydlep[..., 2]


def d65_white_on_spd_grid(spd, cieobs='1931_2'):
    """把 CIE D65 插到与样品相同的波长网格上，再求相对三刺激值。

    工具箱会把样品补齐到 380–780 nm。参考白使用同一网格，
    避免全波段 D65（360–830 nm）与截断光谱之间留下无意义的色调角。
    """
    d65 = lx._CIE_D65
    values = np.interp(spd[0], d65[0], d65[1], left=0.0, right=0.0)
    d65_spd = np.vstack([spd[0], values])
    return lx.spd_to_xyz(d65_spd, relative=True, cieobs=cieobs)


def source_cielab_hue_d65(xyz, cieobs='1931_2', xyzw=None):
    """光源相对 D65 的 CIE 1976 hab，单位为度，范围 [0, 360)。

    xyz 须是 relative=True 的光源三刺激值。xyzw 缺省时使用同一观察者下的
    全波段 CIE D65；批量计算会传入与样品同一波长网格的 D65。
    a* 与 b* 同时接近 0 时色调角无定义，返回 NaN。
    """
    if xyzw is None:
        xyzw = d65_white_xyz(cieobs)
    lab = np.asarray(lx.xyz_to_lab(xyz, xyzw=xyzw, cieobs=cieobs), dtype=float)
    a_star = lab[..., 1]
    b_star = lab[..., 2]
    hue = np.asarray(
        lx.math.positive_arctan(a_star, b_star, htype='deg'),
        dtype=float,
    )
    hue[np.hypot(a_star, b_star) < 1e-8] = np.nan
    return hue


class MetricsCalculator:
    """光谱指标计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.metrics_columns = [
            'ID', 'CCT', 'Duv', 'x', 'y', "u'", "v'", 'pe', 'hab',
            'Ra (CIE 13.3-1995 Ra)',
            'Rf (CIE 224-2017 Rf / IES TM 30-18 Rf)',
            'Rg (IES TM30-18 Rg)',
            'CRI2012', 'CQS Qa', 'CQS Qf', 'CQS Qg', 'CQS Qp',
            'MCRI', 'FCI', 'Sneutral', 'GAI', 'CDI76', 'GAI-CRI',
            'Rd', 'CS', 'CLa', '(Ra+Rf)/2', 'MCPI', 'CDM',
            'MCPIr', 'CDMr', '还原分级', '喜好分级', '分辨分级'
        ]
        
    def calculate_batch(self, spd, sample_names, progress_callback=None, selected_metrics=None, cieobs='1931_2'):
        """
        批量计算光谱指标
        
        参数:
            spd: ndarray - SPD数组，第一行为波长，后续行为各样本的光谱数据
            sample_names: list - 样本名称列表
            progress_callback: callable - 进度回调函数，接收参数 (current, total, message)
            selected_metrics: dict - 选中的指标字典，键为指标名称，值为是否选中
            cieobs: str - 颜色匹配函数，'1931_2' (CIE 1931 2°) 或 '1964_10' (CIE 1964 10°)
        
        返回:
            DataFrame - 包含所有指标的数据框
        """
        short_to_full = {
            'Ra': 'Ra (CIE 13.3-1995 Ra)',
            'Rf': 'Rf (CIE 224-2017 Rf / IES TM 30-18 Rf)',
            'Rg': 'Rg (IES TM30-18 Rg)',
        }

        def is_selected(metric_name):
            if selected_metrics is None:
                return True
            return selected_metrics.get(metric_name, True)

        # 输入范围不足时补零到 380–780 nm
        spd = pad_spd_to_range(spd)

        output_columns = ['ID']
        for col in self.metrics_columns:
            short_name = next((short for short, full in short_to_full.items() if full == col), col)
            if col != 'ID' and is_selected(short_name):
                output_columns.append(col)

        metrics = {col: [] for col in output_columns}
        sample_count = len(sample_names)

        need_fidelity_grade = is_selected('还原分级')
        need_preference_grade = is_selected('喜好分级')
        need_discrimination_grade = is_selected('分辨分级')

        need_ra = is_selected('Ra') or is_selected('(Ra+Rf)/2') or is_selected('GAI-CRI') or need_fidelity_grade
        need_rf = is_selected('Rf') or is_selected('(Ra+Rf)/2') or need_fidelity_grade
        need_cri2012 = is_selected('CRI2012')
        need_cct_duv = (
            is_selected('CCT') or is_selected('Duv') or need_cri2012 or
            is_selected('MCPIr') or is_selected('CDMr') or need_discrimination_grade or
            need_preference_grade
        )
        need_pe = is_selected('pe')
        need_hab = is_selected('hab')
        need_xyz = (
            is_selected('x') or is_selected('y') or is_selected("u'") or is_selected("v'") or
            need_pe or need_hab or
            is_selected('Sneutral') or is_selected('CDM') or is_selected('CDMr') or
            need_discrimination_grade
        )
        need_uv = is_selected("u'") or is_selected("v'")
        need_rg = is_selected('Rg')
        need_qa = is_selected('CQS Qa') or is_selected('MCPI') or is_selected('MCPIr') or need_preference_grade
        need_qf = is_selected('CQS Qf')
        need_qg = is_selected('CQS Qg')
        need_qp = is_selected('CQS Qp')
        need_mcri = is_selected('MCRI')
        need_fci = is_selected('FCI')
        need_sn = is_selected('Sneutral') or is_selected('CDM') or is_selected('CDMr') or need_discrimination_grade
        need_cs_cla = is_selected('CS') or is_selected('CLa')
        need_gai = is_selected('GAI') or is_selected('GAI-CRI')
        need_cdi = is_selected('CDI76') or is_selected('MCPI') or is_selected('MCPIr') or need_preference_grade
        need_rd = is_selected('Rd') or is_selected('CDM') or is_selected('CDMr') or need_discrimination_grade
        need_mcpi = is_selected('MCPI') or is_selected('MCPIr') or need_preference_grade
        need_cdm = is_selected('CDM') or is_selected('CDMr') or need_discrimination_grade
        need_reference = is_selected('MCPIr') or is_selected('CDMr') or need_preference_grade or need_discrimination_grade

        def add_metric(name, value):
            if name in metrics:
                metrics[name].append(value)

        def update_progress(current, message):
            if progress_callback:
                progress_callback(current, sample_count, message)
        
        # 计算基础指标
        xyz = None
        uvDash = None
        ciera = None
        CRI2012 = None
        CCT = None
        Duv = None
        cierf = None
        iesrg_18 = None
        Qa = None
        Qf = None
        Qg = None
        Qp = None
        MCRI = None
        FCI = None
        Sn = None
        CS = None
        CLa = None

        if need_xyz:
            update_progress(0, "计算基础色度指标...")
            xyz = lx.spd_to_xyz(spd, relative=True, cieobs=cieobs)
            if need_uv:
                uvDash = lx.xyz_to_Yuv(xyz)

        pe_values = None
        hab_values = None
        if xyz is not None and (need_pe or need_hab):
            update_progress(0, "计算激发纯度与色调角...")
            if need_pe:
                pe_values = np.asarray(excitation_purity(xyz, cieobs), dtype=float).reshape(-1)
            if need_hab:
                xyzw_d65 = d65_white_on_spd_grid(spd, cieobs)
                hab_values = np.asarray(
                    source_cielab_hue_d65(xyz, cieobs, xyzw=xyzw_d65),
                    dtype=float,
                ).reshape(-1)

        if need_ra:
            update_progress(0, "计算Ra指标...")
            # CIE 13.3 / GB/T 26180：Ri 取整后再平均得 Ra
            ciera = spd_to_cri(spd, cri_type='ciera', out='Rf', rf_from_avg_rounded_rfi=True)

        if need_cct_duv:
            update_progress(0, "计算CCT/Duv指标...")
            CRI2012, CCT, Duv = lx.cri.spd_to_cri2012(spd, out='Rf,cct,duv', wl=None)

        if need_rf:
            update_progress(0, "计算Rf指标...")
            cierf = lx.cri.spd_to_cierf(spd)

        if need_rg:
            update_progress(0, "计算Rg指标...")
            iesrg_18 = lx.cri.spd_to_iesrg(spd)

        if need_qa or need_qf or need_qg or need_qp:
            update_progress(0, "计算CQS指标...")
            if need_qa:
                Qa = lx.cri.spd_to_cqs(spd, version=_CQS_VERSION, out='Qa', wl=None)
            if need_qf:
                Qf = lx.cri.spd_to_cqs(spd, version=_CQS_VERSION, out='Qf', wl=None)
            if need_qg:
                Qg = lx.cri.spd_to_cqs(spd, version=_CQS_VERSION, out='Qg', wl=None)
            if need_qp:
                Qp = lx.cri.spd_to_cqs(spd, version=_CQS_VERSION, out='Qp', wl=None)

        if need_mcri:
            update_progress(0, "计算MCRI指标...")
            MCRI = lx.cri.spd_to_mcri(spd, D=0.9, E=None, Yb=20.0, out='Rm', wl=None, mcri_defaults=None)

        if need_fci:
            update_progress(0, "计算FCI指标...")
            FCI = lx.cri.spd_to_fci(spd, use_cielab=True)

        if need_sn:
            # Sneutral 固定用 CIE 1964 10°，与辅助色度 cieobs 解耦。
            xyz_sn = lx.spd_to_xyz(spd, relative=True, cieobs=_CMF_SNEUTRAL)
            Sn = Sneutral.xyz_to_neutrality_smet2018(xyz_sn, 'uw', 'Linvar')

        if need_cs_cla:
            update_progress(0, "计算光生物效应...")
            from luxpy.toolboxes.photbiochem import spd_to_CS_CLa_lrc
            CS, CLa = spd_to_CS_CLa_lrc(El=spd, E=300)  # Normalized to 300 lux
        
        # 逐个样本计算
        reference_cache = {}
        for i in range(sample_count):
            update_progress(i + 1, f"计算样本 {i+1}/{sample_count}: {sample_names[i]}")

            metrics['ID'].append(sample_names[i])

            cct_value = int(CCT[i][0]) if CCT is not None else None
            ra_value = ciera[0][i] if ciera is not None else None
            rf_value = cierf[0][i] if cierf is not None else None
            gai_value = None
            cdi_value = None
            rd_value = None
            mcpi_value = None
            cdm_value = None
            mcpir_value = None
            cdmr_value = None

            if CCT is not None:
                add_metric('CCT', cct_value)
            if Duv is not None:
                add_metric('Duv', Duv[i][0])
            if xyz is not None:
                xyz_sum = sum(xyz[i])
                add_metric('x', xyz[i][0] / xyz_sum)
                add_metric('y', xyz[i][1] / xyz_sum)
            if uvDash is not None:
                add_metric("u'", uvDash[i][1])
                add_metric("v'", uvDash[i][2])
            if pe_values is not None:
                add_metric('pe', float(pe_values[i]))
            if hab_values is not None:
                add_metric('hab', float(hab_values[i]))
            if ciera is not None:
                add_metric('Ra (CIE 13.3-1995 Ra)', ra_value)
            if cierf is not None:
                add_metric('Rf (CIE 224-2017 Rf / IES TM 30-18 Rf)', rf_value)
            if iesrg_18 is not None:
                add_metric('Rg (IES TM30-18 Rg)', iesrg_18[0][i])
            if CRI2012 is not None:
                add_metric('CRI2012', CRI2012[0][i])
            if Qa is not None:
                add_metric('CQS Qa', Qa[0][i])
            if Qf is not None:
                add_metric('CQS Qf', Qf[0][i])
            if Qg is not None:
                add_metric('CQS Qg', Qg[0][i])
            if Qp is not None:
                add_metric('CQS Qp', Qp[0][i])
            if MCRI is not None:
                add_metric('MCRI', MCRI[0][i])
            if FCI is not None:
                add_metric('FCI', FCI[i])
            if Sn is not None:
                add_metric('Sneutral', Sn[i][0])
            if CS is not None:
                add_metric('CS', CS[i])
            if CLa is not None:
                add_metric('CLa', CLa[i])
            if ra_value is not None and rf_value is not None:
                add_metric('(Ra+Rf)/2', (ra_value + rf_value) / 2)

            # 准备单个SPD用于特定指标计算
            spdi = np.vstack([spd[0, :], spd[i + 1, :]])

            if need_gai:
                gai_value = GAI.calc_GAI(spdi)
                add_metric('GAI', gai_value)
                if ra_value is not None:
                    add_metric('GAI-CRI', (gai_value + ra_value) / 2)

            if need_cdi:
                cdi_value = CDI.calc_CDI(spdi)
                add_metric('CDI76', cdi_value)

            if need_rd:
                rd_value = Rd.calc_Rd(spdi)
                add_metric('Rd', rd_value)

            if need_mcpi and Qa is not None and cdi_value is not None:
                mcpi_value = Qa[0][i] * 0.62 + cdi_value * 0.38
                add_metric('MCPI', mcpi_value)

            if need_cdm and rd_value is not None and Sn is not None:
                cdm_value = rd_value * (-0.07) + Sn[i][0] * 0.93
                add_metric('CDM', cdm_value)

            if need_reference:
                cache_key = (
                    cct_value,
                    int(spd[0, 0]),
                    int(spd[0, -1]),
                    int(spd[0, 1] - spd[0, 0]),
                    cieobs,
                )

                if cache_key not in reference_cache:
                    spd_ref = get_reference_illuminant_spd(
                        cct_value,
                        wl_start=cache_key[1],
                        wl_end=cache_key[2],
                        wl_step=cache_key[3]
                    )

                    ref_values = {}
                    if need_mcpi:
                        # Qa_ref 使用与被测体相同的 CQS 9.0/9.0.3 口径。
                        Qa_ref = lx.cri.spd_to_cqs(spd_ref, version=_CQS_VERSION, out='Qa', wl=None)
                        CDI_ref = CDI.calc_CDI(spd_ref)
                        ref_values['MCPI_ref'] = Qa_ref[0][0] * 0.62 + CDI_ref * 0.38
                    if need_cdm:
                        # Sn_ref 固定 CIE 1964 10°，与被测体 Sneutral 口径一致。
                        xyz_ref_sn = lx.spd_to_xyz(spd_ref, relative=True, cieobs=_CMF_SNEUTRAL)
                        Sn_ref = Sneutral.xyz_to_neutrality_smet2018(xyz_ref_sn, 'uw', 'Linvar')
                        Rd_ref = Rd.calc_Rd(spd_ref)
                        ref_values['CDM_ref'] = Rd_ref * (-0.07) + Sn_ref[0][0] * 0.93
                    reference_cache[cache_key] = ref_values

                ref_values = reference_cache[cache_key]
                if need_mcpi and mcpi_value is not None:
                    mcpi_ref = ref_values.get('MCPI_ref')
                    mcpir_value = (mcpi_value / mcpi_ref) * 100 if mcpi_ref else 0
                    add_metric('MCPIr', mcpir_value)
                if need_cdm and cdm_value is not None:
                    cdm_ref = ref_values.get('CDM_ref')
                    cdmr_value = (1 - (cdm_ref - cdm_value) / abs(cdm_ref)) * 100 if cdm_ref else 0
                    add_metric('CDMr', cdmr_value)

            if need_fidelity_grade and ra_value is not None and rf_value is not None:
                add_metric('还原分级', self.grade_fidelity(ra_value, rf_value, cct_value))
            if need_preference_grade and mcpir_value is not None:
                add_metric('喜好分级', self.grade_preference(mcpir_value, cct_value))
            if need_discrimination_grade and cdmr_value is not None:
                add_metric('分辨分级', self.grade_discrimination(cdmr_value, cct_value))
        
        # 转换为DataFrame
        result_df = DataFrame(metrics)
        
        if progress_callback:
            progress_callback(sample_count, sample_count, "计算完成！")
        
        return result_df
    
    @staticmethod
    def grade_fidelity(ra, cierf, cct):
        """
        颜色保真度（还原度）分级
        基于：(Ra + CIE-Rf) / 2
        """
        fidelity_index = (ra + cierf) / 2
        
        if fidelity_index >= 95:
            return 'A'  # 优秀
        elif fidelity_index >= 90:
            return 'B'  # 良好
        elif fidelity_index >= 77:
            return 'C'  # 合格
        else:
            return 'D'  # 不合格
    
    @staticmethod
    def grade_preference(mcpir, cct):
        """
        颜色偏好度（喜好度）分级
        基于：MCPIr
        """
        if mcpir >= 100:
            return 'A'  # 优秀
        elif mcpir >= 97:
            return 'B'  # 良好
        elif mcpir >= 85:
            return 'C'  # 合格
        else:
            return 'D'  # 不合格
    
    @staticmethod
    def grade_discrimination(cdmr, cct):
        """
        颜色分辨力分级
        基于：CDMr
        不同CCT范围有不同的分级标准
        """
        if cdmr >= 105:
            return 'A'  # 优秀
        
        if cct < 5000:
            if cdmr >= 85:
                return 'B'  # 良好
            elif cdmr >= 50:
                return 'C'  # 合格
            else:
                return 'D'  # 不合格
        else:
            if cdmr >= 95:
                return 'B'  # 良好
            elif cdmr >= 75:
                return 'C'  # 合格
            else:
                return 'D'  # 不合格
    
    def apply_sss_filter(self, metrics_df, cct_interval=500, samples_per_interval=2):
        """
        筛选SSS级光源
        
        参数:
            metrics_df: DataFrame - 计算结果数据框
            cct_interval: int - 色温间隔（K）
            samples_per_interval: int - 每个基准点选择的样本数量
        
        返回:
            tuple: (all_sss_df, representative_sss_df)
        """
        # 筛选所有SSS级光源
        sss_filter = (
            (metrics_df['还原分级'] == 'A') &
            (metrics_df['喜好分级'] == 'A') &
            (metrics_df['分辨分级'] == 'A')
        )
        all_sss_df = metrics_df[sss_filter].copy()
        
        if len(all_sss_df) == 0:
            return all_sss_df, pd.DataFrame()
        
        # 按CCT排序
        all_sss_df = all_sss_df.sort_values('CCT')
        
        # 选择代表性样本
        min_cct = all_sss_df['CCT'].min()
        max_cct = all_sss_df['CCT'].max()
        
        cct_min_rounded = (min_cct // 100) * 100
        cct_max_rounded = ((max_cct + 99) // 100) * 100
        
        cct_start_500 = ((cct_min_rounded + cct_interval - 1) // cct_interval) * cct_interval
        cct_end_500 = (cct_max_rounded // cct_interval) * cct_interval
        
        target_ccts = [cct_min_rounded]
        current_cct = cct_start_500
        while current_cct <= cct_end_500:
            if current_cct != cct_min_rounded and current_cct != cct_max_rounded:
                target_ccts.append(current_cct)
            current_cct += cct_interval
        
        if cct_max_rounded not in target_ccts:
            target_ccts.append(cct_max_rounded)
        
        target_ccts.sort()
        
        representative_indices = []
        CCT_TOLERANCE = 100
        
        for target_cct in target_ccts:
            candidates = all_sss_df[
                abs(all_sss_df['CCT'] - target_cct) <= CCT_TOLERANCE
            ].copy()
            
            if len(candidates) > 0:
                candidates['距基准点距离'] = abs(candidates['CCT'] - target_cct)
                candidates_sorted = candidates.sort_values('距基准点距离')
                selected = candidates_sorted.head(samples_per_interval)
                
                for idx in selected.index:
                    if idx not in representative_indices:
                        representative_indices.append(idx)
        
        representative_sss_df = metrics_df.loc[representative_indices]
        
        return all_sss_df, representative_sss_df


if __name__ == "__main__":
    # 测试代码
    print("核心计算引擎模块已加载")
