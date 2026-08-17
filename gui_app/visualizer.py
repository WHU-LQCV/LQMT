"""
数据可视化模块
生成各类图表用于结果展示
"""

import tkinter as tk
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class VisualizationWindow:
    """可视化窗口类"""
    
    def __init__(self, parent, results_df, spd_array, sample_names):
        """
        初始化可视化窗口
        
        参数:
            parent: tk.Toplevel - 父窗口
            results_df: DataFrame - 计算结果数据
            spd_array: ndarray - SPD数组
            sample_names: list - 样本名称列表
        """
        self.parent = parent
        self.parent.title("数据可视化")
        self.parent.geometry("1000x700")
        
        self.results_df = results_df
        self.spd_array = spd_array
        self.sample_names = sample_names
        
        self._create_ui()
    
    def _create_ui(self):
        """创建UI"""
        # 创建标签页
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 光谱曲线标签页
        spd_frame = ttk.Frame(notebook)
        notebook.add(spd_frame, text="光谱曲线")
        self._create_spd_plot(spd_frame)
        
        # 色温分布标签页
        cct_frame = ttk.Frame(notebook)
        notebook.add(cct_frame, text="色温分布")
        self._create_cct_plot(cct_frame)
    
    def _create_spd_plot(self, parent):
        """创建光谱曲线图（所有 SPD 归一化到峰值 = 1，自适应图例/colorbar）"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        wavelengths = self.spd_array[0, :]
        n = len(self.sample_names)
        colors = plt.cm.rainbow(np.linspace(0, 1, n))

        # 样本数越多，线条越细、越透明，避免视觉混乱
        if n <= 20:
            lw, alpha = 1.5, 0.85
        elif n <= 100:
            lw, alpha = 1.0, 0.55
        else:
            lw, alpha = 0.6, 0.35

        for i in range(n):
            spd_values = self.spd_array[i + 1, :].copy()
            peak = np.max(spd_values)
            if peak > 0:
                spd_values = spd_values / peak
            lbl = self.sample_names[i] if n <= 15 else '_nolegend_'
            ax.plot(wavelengths, spd_values, color=colors[i],
                    linewidth=lw, alpha=alpha, label=lbl)

        ax.set_xlabel('波长 (nm)', fontsize=12)
        ax.set_ylabel('归一化相对光谱功率', fontsize=12)
        ax.set_title(f'光谱功率分布曲线（归一化，共 {n} 条）',
                     fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

        if n <= 15:
            ax.legend(loc='best', fontsize=9)
        else:
            import matplotlib.cm as cm
            import matplotlib.colors as mcolors
            sm = cm.ScalarMappable(
                cmap='rainbow',
                norm=mcolors.Normalize(vmin=1, vmax=n)
            )
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, pad=0.02)
            cbar.set_label('样本序号', fontsize=10)
            cbar.set_ticks([1, n])
            cbar.set_ticklabels([self.sample_names[0], self.sample_names[-1]], fontsize=8)
        
        # 嵌入到Tkinter窗口
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加工具栏
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_cct_plot(self, parent):
        """创建色温分布图 (CCT vs Duv)"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        required_cols = {'CCT', 'Duv', '还原分级', '喜好分级', '分辨分级'}
        if not required_cols.issubset(self.results_df.columns):
            ax.text(
                0.5, 0.5,
                '当前结果未计算 CCT/Duv 或分级指标，无法绘制色温分布图。',
                ha='center', va='center', transform=ax.transAxes, fontsize=12
            )
            ax.set_axis_off()
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            toolbar = NavigationToolbar2Tk(canvas, parent)
            toolbar.update()
            return
        
        # 提取CCT和Duv数据
        cct_values = self.results_df['CCT'].values
        duv_values = self.results_df['Duv'].values
        
        # 根据分级着色
        colors = []
        for _, row in self.results_df.iterrows():
            if row['还原分级'] == 'A' and row['喜好分级'] == 'A' and row['分辨分级'] == 'A':
                colors.append('green')  # AAA级
            elif row['还原分级'] in ['A', 'B'] and row['喜好分级'] in ['A', 'B']:
                colors.append('blue')  # 高质量
            else:
                colors.append('orange')  # 一般
        
        scatter = ax.scatter(cct_values, duv_values, c=colors, s=100, alpha=0.6, edgecolors='black')
        
        # 添加黑体轨迹参考线
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, label='黑体轨迹 (Duv=0)')
        ax.axhline(y=0.005, color='red', linestyle=':', linewidth=1, alpha=0.5)
        ax.axhline(y=-0.005, color='red', linestyle=':', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('相关色温 CCT (K)', fontsize=12)
        ax.set_ylabel('Duv', fontsize=12)
        ax.set_title('色温与Duv分布图', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(['黑体轨迹', 'Duv=±0.005'])
        
        # 添加图例说明
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', label='AAA级'),
            Patch(facecolor='blue', label='高质量'),
            Patch(facecolor='orange', label='一般')
        ]
        ax.legend(handles=legend_elements, loc='best')
        
        # 嵌入到Tkinter窗口
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
    
    def _create_metrics_plot(self, parent):
        """创建指标对比图（雷达图）"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111, projection='polar')
        
        # 选择关键指标进行对比
        metrics = ['Ra (CIE 13.3-1995 Ra)', 'Rf (CIE 224-2017 Rf / IES TM 30-18 Rf)', 
                  'MCPIr', 'CDMr', 'GAI', 'CQS Qa']
        metric_labels = ['Ra', 'Rf', 'MCPIr', 'CDMr', 'GAI', 'Qa']
        
        # 计算平均值
        avg_values = []
        for metric in metrics:
            if metric in self.results_df.columns:
                avg_values.append(self.results_df[metric].mean())
            else:
                avg_values.append(0)
        
        # 归一化到0-100范围
        normalized_values = []
        for val in avg_values:
            if val > 100:
                normalized_values.append(100)
            else:
                normalized_values.append(val)
        
        # 设置角度
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        normalized_values += normalized_values[:1]  # 闭合曲线
        angles += angles[:1]
        
        # 绘制雷达图
        ax.plot(angles, normalized_values, 'o-', linewidth=2, label='平均值')
        ax.fill(angles, normalized_values, alpha=0.25)
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_labels, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_title('关键指标雷达图', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True)
        ax.legend(loc='upper right')
        
        # 嵌入到Tkinter窗口
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
    
    def _create_grade_plot(self, parent):
        """创建分级统计图"""
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # 创建三个子图
        ax1 = fig.add_subplot(131)
        ax2 = fig.add_subplot(132)
        ax3 = fig.add_subplot(133)
        
        # 统计各分级的数量
        grade_categories = ['A', 'B', 'C', 'D']
        colors = ['#00C851', '#33B5E5', '#FFB64D', '#FF4444']
        
        # 还原分级
        fidelity_counts = [
            len(self.results_df[self.results_df['还原分级'] == grade])
            for grade in grade_categories
        ]
        ax1.bar(grade_categories, fidelity_counts, color=colors)
        ax1.set_title('还原度分级', fontsize=12, fontweight='bold')
        ax1.set_ylabel('样本数量', fontsize=10)
        ax1.grid(axis='y', alpha=0.3)
        
        # 喜好分级
        preference_counts = [
            len(self.results_df[self.results_df['喜好分级'] == grade])
            for grade in grade_categories
        ]
        ax2.bar(grade_categories, preference_counts, color=colors)
        ax2.set_title('喜好度分级', fontsize=12, fontweight='bold')
        ax2.set_ylabel('样本数量', fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        
        # 分辨分级
        discrimination_counts = [
            len(self.results_df[self.results_df['分辨分级'] == grade])
            for grade in grade_categories
        ]
        ax3.bar(grade_categories, discrimination_counts, color=colors)
        ax3.set_title('分辨力分级', fontsize=12, fontweight='bold')
        ax3.set_ylabel('样本数量', fontsize=10)
        ax3.grid(axis='y', alpha=0.3)
        
        fig.suptitle('ABCD分级统计', fontsize=14, fontweight='bold')
        fig.tight_layout()
        
        # 嵌入到Tkinter窗口
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()


class ChartGenerator:
    """图表生成器（用于导出）"""
    
    @staticmethod
    def generate_spd_chart(spd_array, sample_names, save_path=None):
        """
        生成光谱曲线图并保存
        
        参数:
            spd_array: ndarray - SPD数组
            sample_names: list - 样本名称列表
            save_path: str - 保存路径
        
        返回:
            Figure - matplotlib图表对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        wavelengths = spd_array[0, :]
        n = len(sample_names)
        colors = plt.cm.rainbow(np.linspace(0, 1, n))

        if n <= 20:
            lw, alpha = 1.5, 0.85
        elif n <= 100:
            lw, alpha = 1.0, 0.55
        else:
            lw, alpha = 0.6, 0.35

        for i in range(n):
            spd_values = spd_array[i + 1, :].copy()
            peak = np.max(spd_values)
            if peak > 0:
                spd_values = spd_values / peak
            lbl = sample_names[i] if n <= 15 else '_nolegend_'
            ax.plot(wavelengths, spd_values, color=colors[i],
                    linewidth=lw, alpha=alpha, label=lbl)

        ax.set_xlabel('波长 (nm)', fontsize=12)
        ax.set_ylabel('归一化相对光谱功率', fontsize=12)
        ax.set_title(f'光谱功率分布曲线（归一化，共 {n} 条）',
                     fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

        if n <= 15:
            ax.legend(loc='best', fontsize=9)
        else:
            import matplotlib.cm as cm
            import matplotlib.colors as mcolors
            sm = cm.ScalarMappable(
                cmap='rainbow',
                norm=mcolors.Normalize(vmin=1, vmax=n)
            )
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, pad=0.02)
            cbar.set_label('样本序号', fontsize=10)
            cbar.set_ticks([1, n])
            cbar.set_ticklabels([sample_names[0], sample_names[-1]], fontsize=8)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    @staticmethod
    def generate_grade_distribution_chart(results_df, save_path=None):
        """
        生成分级分布图并保存
        
        参数:
            results_df: DataFrame - 结果数据
            save_path: str - 保存路径
        
        返回:
            Figure - matplotlib图表对象
        """
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
        
        grade_categories = ['A', 'B', 'C', 'D']
        colors = ['#00C851', '#33B5E5', '#FFB64D', '#FF4444']
        
        # 还原分级
        fidelity_counts = [
            len(results_df[results_df['还原分级'] == grade])
            for grade in grade_categories
        ]
        ax1.bar(grade_categories, fidelity_counts, color=colors)
        ax1.set_title('还原度分级', fontsize=12, fontweight='bold')
        ax1.set_ylabel('样本数量', fontsize=10)
        ax1.grid(axis='y', alpha=0.3)
        
        # 喜好分级
        preference_counts = [
            len(results_df[results_df['喜好分级'] == grade])
            for grade in grade_categories
        ]
        ax2.bar(grade_categories, preference_counts, color=colors)
        ax2.set_title('喜好度分级', fontsize=12, fontweight='bold')
        ax2.set_ylabel('样本数量', fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        
        # 分辨分级
        discrimination_counts = [
            len(results_df[results_df['分辨分级'] == grade])
            for grade in grade_categories
        ]
        ax3.bar(grade_categories, discrimination_counts, color=colors)
        ax3.set_title('分辨力分级', fontsize=12, fontweight='bold')
        ax3.set_ylabel('样本数量', fontsize=10)
        ax3.grid(axis='y', alpha=0.3)
        
        fig.suptitle('ABCD分级统计', fontsize=14, fontweight='bold')
        fig.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


if __name__ == "__main__":
    # 测试代码
    print("可视化模块已加载")
