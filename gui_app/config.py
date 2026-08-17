"""
配置管理模块
管理用户偏好设置和应用配置
"""

import json
from pathlib import Path


class AppConfig:
    """应用配置管理器"""
    
    DEFAULT_CONFIG = {
        # SSS筛选参数
        'sss_filter_enabled': False,
        'sss_cct_interval': 500,
        'sss_samples_per_interval': 2,
        
        # 波长范围设置
        'wavelength_start': 380,
        'wavelength_end': 780,
        'wavelength_step': 1,
        
        # 导出设置
        'export_format': 'excel',  # 'excel', 'csv', 'both'
        'excel_include_charts': True,
        'excel_apply_formatting': True,
        
        # 界面设置
        'window_width': 1200,
        'window_height': 800,
        'show_tooltips': True,
        'language': 'zh_CN',
        
        # 最近使用
        'recent_files': [],
        'last_export_path': '',
        
        # 显示选项
        'show_all_metrics': True,
        'show_grading': True,
        
        # 色度坐标显示观察者（仅作用于结果表中 x, y, u', v' 四列）
        # Ra/Rf/Qa/CDI/Rd/Sneutral/MCPI/CDM 等所有指标按各自标准固定观察者计算，不受此项影响。
        'cmf': '1931_2',  # '1931_2'（CIE 1931 2°）或 '1964_10'（CIE 1964 10°）
    }
    
    def __init__(self, config_file='lqcv_lqmt_config.json'):
        """
        初始化配置管理器
        
        参数:
            config_file: str - 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """从文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置，保留默认值中存在但加载配置中不存在的项
                    self.config.update(loaded_config)
                    self._migrate_config()
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
    
    def _migrate_config(self):
        """迁移旧版配置键，保持升级后用户设置有效。"""
        selected = self.config.get('selected_metrics')
        if not isinstance(selected, dict):
            return
        if 'CDI_76' in selected:
            if 'CDI76' not in selected:
                selected['CDI76'] = selected['CDI_76']
            del selected['CDI_76']
            self.config['selected_metrics'] = selected

    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def add_recent_file(self, file_path):
        """添加到最近文件列表"""
        recent_files = self.config.get('recent_files', [])
        
        # 移除已存在的相同路径
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 添加到列表开头
        recent_files.insert(0, file_path)
        
        # 限制列表长度
        self.config['recent_files'] = recent_files[:10]
        self.save()
    
    def get_recent_files(self):
        """获取最近文件列表"""
        return self.config.get('recent_files', [])


if __name__ == "__main__":
    # 测试配置管理
    config = AppConfig()
    print("默认配置:", config.config)
    
    config.set('sss_filter_enabled', True)
    config.save()
    print("已保存配置")
