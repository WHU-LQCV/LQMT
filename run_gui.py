"""
LQCV 光品质指标工具箱 (LQMT) — GUI 启动器
"""

import sys
import os

# Windows 高 DPI 支持 - 解决打包后界面模糊问题
if sys.platform == 'win32':
    try:
        import ctypes
        # 设置 DPI 感知级别 (Per Monitor DPI Aware)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # 回退方案：使用旧版 API
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_app.main_window import main
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"导入错误: {e}")
    print("\n请确保已安装所有依赖项：")
    print("pip install -r requirements.txt")
    sys.exit(1)
