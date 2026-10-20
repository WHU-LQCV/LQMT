"""
工具函数模块
提供通用辅助功能
"""

import threading
from datetime import datetime


class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, callback=None):
        """
        初始化进度跟踪器
        
        参数:
            callback: callable - 进度回调函数 callback(current, total, message)
        """
        self.callback = callback
        self.current = 0
        self.total = 0
        self.message = ""
    
    def update(self, current, total, message=""):
        """更新进度"""
        self.current = current
        self.total = total
        self.message = message
        
        if self.callback:
            self.callback(current, total, message)
    
    def increment(self, message=""):
        """递增进度"""
        self.current += 1
        self.message = message
        
        if self.callback:
            self.callback(self.current, self.total, message)


class ThreadSafeTask:
    """线程安全的任务执行器"""
    
    def __init__(self, target, args=(), kwargs=None, callback=None, error_callback=None):
        """
        初始化任务执行器
        
        参数:
            target: callable - 目标函数
            args: tuple - 位置参数
            kwargs: dict - 关键字参数
            callback: callable - 成功回调
            error_callback: callable - 错误回调
        """
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.callback = callback
        self.error_callback = error_callback
        self.thread = None
        self.result = None
        self.error = None
    
    def run(self):
        """在新线程中运行任务"""
        def _run():
            try:
                self.result = self.target(*self.args, **self.kwargs)
                if self.callback:
                    self.callback(self.result)
            except Exception as e:
                self.error = e
                if self.error_callback:
                    self.error_callback(e)
        
        self.thread = threading.Thread(target=_run, daemon=True)
        self.thread.start()
    
    def wait(self, timeout=None):
        """等待任务完成"""
        if self.thread:
            self.thread.join(timeout)


# 界面字体是微软雅黑，没有 Unicode 下标字形。带下标的指标用下划线表示。
METRIC_DISPLAY_NAMES = {
    'Ra': 'R_a',
    'Rf': 'R_f',
    'Rg': 'R_g',
    'Rd': 'R_d',
    '(Ra+Rf)/2': '(R_a+R_f)/2',
    'Duv': 'D_uv',
    'pe': 'p_e',
    'hab': 'h_ab',
    'CQS Qa': 'CQS Q_a',
    'CQS Qf': 'CQS Q_f',
    'CQS Qg': 'CQS Q_g',
    'CQS Qp': 'CQS Q_p',
    'MCPIr': 'MCPI_r',
    'CDMr': 'CDM_r',
    'CLa': 'CL_a',
    'Ra (CIE 13.3-1995 Ra)': 'R_a (CIE 13.3-1995 R_a)',
    'Rf (CIE 224-2017 Rf / IES TM 30-18 Rf)': 'R_f (CIE 224-2017 R_f / IES TM-30 R_f)',
    'Rg (IES TM30-18 Rg)': 'R_g (IES TM-30-18 R_g)',
}


def display_metric_name(name):
    """把内部列名换成界面和导出用的名称。"""
    return METRIC_DISPLAY_NAMES.get(name, name)


def rename_metric_columns(frame):
    """导出前把列名换成下划线写法，不改计算用的内部列名。"""
    mapping = {name: display_metric_name(name) for name in frame.columns}
    return frame.rename(columns=mapping)


def format_number(value, decimals=2):
    """
    格式化数字
    
    参数:
        value: float - 数值
        decimals: int - 小数位数
    
    返回:
        str - 格式化后的字符串
    """
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def get_grade_color(grade):
    """
    获取分级对应的颜色
    
    参数:
        grade: str - 分级 (A/B/C/D)
    
    返回:
        str - 十六进制颜色代码
    """
    colors = {
        'A': '#00C851',  # 绿色
        'B': '#33B5E5',  # 蓝色
        'C': '#FFB64D',  # 橙色
        'D': '#FF4444',  # 红色
    }
    return colors.get(grade, '#000000')


def get_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_example_spd_text():
    """创建示例SPD数据文本（从sample.csv读取）"""
    # sample.csv 的数据（380-780nm, 5nm间隔，3组样本）
    sample_data = [
        [0.0197, 0.00722, 0.0026],
        [0.0232, 0.00597, 0.0024],
        [0.0311, 0.00592, 0.0006],
        [0.0463, 0.00764, 0.0012],
        [0.0731, 0.0116, 0.0018],
        [0.114, 0.0207, 0.0031],
        [0.180, 0.0440, 0.009],
        [0.278, 0.0920, 0.0201],
        [0.411, 0.169, 0.0441],
        [0.570, 0.274, 0.0875],
        [0.718, 0.428, 0.147],
        [0.829, 0.596, 0.264],
        [0.898, 0.615, 0.336],
        [0.932, 0.573, 0.228],
        [0.959, 0.563, 0.220],
        [0.950, 0.496, 0.299],
        [0.932, 0.523, 0.284],
        [0.928, 0.646, 0.205],
        [0.899, 0.665, 0.200],
        [0.856, 0.594, 0.213],
        [0.837, 0.587, 0.224],
        [0.836, 0.606, 0.276],
        [0.838, 0.614, 0.344],
        [0.848, 0.645, 0.400],
        [0.857, 0.685, 0.434],
        [0.863, 0.716, 0.462],
        [0.864, 0.731, 0.471],
        [0.865, 0.745, 0.482],
        [0.870, 0.756, 0.485],
        [0.874, 0.768, 0.493],
        [0.881, 0.784, 0.507],
        [0.888, 0.800, 0.525],
        [0.896, 0.816, 0.541],
        [0.903, 0.832, 0.561],
        [0.906, 0.844, 0.579],
        [0.910, 0.849, 0.591],
        [0.910, 0.850, 0.603],
        [0.909, 0.846, 0.612],
        [0.907, 0.838, 0.623],
        [0.905, 0.830, 0.636],
        [0.905, 0.825, 0.653],
        [0.907, 0.823, 0.671],
        [0.915, 0.830, 0.700],
        [0.926, 0.842, 0.735],
        [0.940, 0.865, 0.775],
        [0.954, 0.889, 0.813],
        [0.970, 0.916, 0.861],
        [0.984, 0.945, 0.906],
        [0.995, 0.969, 0.941],
        [0.999, 0.987, 0.970],
        [0.998, 0.998, 0.988],
        [0.989, 0.999, 0.999],
        [0.975, 0.992, 0.989],
        [0.951, 0.975, 0.963],
        [0.920, 0.952, 0.934],
        [0.881, 0.924, 0.891],
        [0.838, 0.896, 0.843],
        [0.788, 0.874, 0.786],
        [0.736, 0.849, 0.728],
        [0.681, 0.859, 0.670],
        [0.626, 0.842, 0.608],
        [0.570, 0.840, 0.547],
        [0.517, 0.960, 0.489],
        [0.465, 0.839, 0.434],
        [0.415, 0.869, 0.385],
        [0.369, 0.906, 0.340],
        [0.326, 0.932, 0.298],
        [0.288, 0.836, 0.259],
        [0.253, 0.760, 0.224],
        [0.222, 0.740, 0.197],
        [0.194, 0.677, 0.169],
        [0.169, 0.612, 0.145],
        [0.147, 0.575, 0.126],
        [0.127, 0.528, 0.108],
        [0.110, 0.498, 0.0923],
        [0.0949, 0.442, 0.0787],
        [0.0822, 0.414, 0.0677],
        [0.0709, 0.367, 0.0580],
        [0.0611, 0.339, 0.0481],
        [0.0533, 0.307, 0.0424],
        [0.0489, 0.280, 0.0361]
    ]
    
    # 生成波长列（380-780nm, 5nm间隔）
    wavelengths = list(range(380, 785, 5))
    
    # 构建示例文本
    lines = ["Wavelength,sample1,sample2,sample3"]
    for i, wl in enumerate(wavelengths):
        line = f"{wl},{sample_data[i][0]},{sample_data[i][1]},{sample_data[i][2]}"
        lines.append(line)
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试工具函数
    print("工具函数模块已加载")
    print("示例SPD数据:", create_example_spd_text()[:200])
