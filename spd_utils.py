"""
SPD 预处理工具。

输入 SPD 不足目标波长范围时，缺失部分补零；
若输入已覆盖目标范围，则为恒等操作。
"""

import numpy as np


def pad_spd_to_range(spd, wl_start=380, wl_end=780):
    """
    将输入 SPD 对齐到 [wl_start, wl_end]，保留原始步长，范围外补零。

    参数
    ----
    spd : ndarray, shape (1+N, M)
        第 0 行为等间距波长序列（nm），后续行为各样本相对光谱功率。
        输入至少需要 2 个波长点（用于推断步长）。
    wl_start : float
        目标范围起始波长（nm），默认 380。
    wl_end : float
        目标范围终止波长（nm），默认 780。

    返回
    ----
    ndarray
        补零/对齐后的 SPD，步长与输入相同；
        若输入已覆盖 [wl_start, wl_end] 则结果与输入完全一致。

    说明
    ----
    - 使用 np.interp(left=0, right=0) 实现"超出范围补零"而非端点外推。
    - CDI 内部使用 400–700 nm，补零后的两端会被内部裁剪掉，不受影响。
    """
    if spd.shape[1] < 2:
        return spd.copy()

    step = round(float(spd[0, 1] - spd[0, 0]), 6)
    # 用半步长偏移确保 wl_end 被正确包含（避免浮点截断）
    target = np.arange(wl_start, wl_end + step * 0.5, step)

    rows = [target]
    for i in range(1, spd.shape[0]):
        rows.append(np.interp(target, spd[0], spd[i], left=0.0, right=0.0))

    return np.vstack(rows)
