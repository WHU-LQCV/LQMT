"""
主窗口模块
Tkinter GUI 主界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
import threading
import sys
import os
import time

# 支持直接运行和作为模块导入
try:
    from .core_engine import MetricsCalculator
    from .data_parser import SPDParser
    from .config import AppConfig
    from .utils import ProgressTracker, ThreadSafeTask, format_number, display_metric_name, get_grade_color, create_example_spd_text
    from . import APP_NAME_ZH, __version__
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from gui_app.core_engine import MetricsCalculator
    from gui_app.data_parser import SPDParser
    from gui_app.config import AppConfig
    from gui_app.utils import ProgressTracker, ThreadSafeTask, format_number, display_metric_name, get_grade_color, create_example_spd_text
    from gui_app import APP_NAME_ZH, __version__


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        """
        初始化主窗口
        
        参数:
            root: tk.Tk - Tkinter根窗口
        """
        self.root = root
        self.root.title(f"{APP_NAME_ZH} v{__version__}")
        
        # 加载配置
        self.config = AppConfig()
        
        # 设置窗口大小为屏幕的一半，并居中显示
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = screen_width // 2
        window_height = screen_height // 2
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 配置主题和样式
        self._configure_styles()
        
        # 初始化组件
        self.calculator = MetricsCalculator()
        self.parser = SPDParser()
        
        # 数据存储
        self.current_spd = None
        self.current_sample_names = None
        self.current_results = None
        
        # 创建UI
        self._create_menu()
        self._create_ui()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _configure_styles(self):
        """配置ttk主题和样式，改善界面美观度和清晰度"""
        style = ttk.Style()
        
        # 选择更现代的主题
        # Windows上可用: winnative, clam, alt, default, classic, vista, xpnative
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # 使用更清晰的中文字体
        # 优先使用 Microsoft YaHei UI，回退到 SimHei
        default_font = ('Microsoft YaHei UI', 10)
        bold_font = ('Microsoft YaHei UI', 10, 'bold')
        title_font = ('Microsoft YaHei UI', 11, 'bold')
        
        # 配置各组件样式
        style.configure('.', font=default_font)
        style.configure('TLabel', font=default_font, padding=2)
        style.configure('TButton', font=default_font, padding=(10, 5))
        style.configure('TCheckbutton', font=default_font, padding=2)
        style.configure('TRadiobutton', font=default_font, padding=2)
        style.configure('TEntry', font=default_font, padding=5)
        style.configure('TCombobox', font=default_font, padding=5)
        
        # LabelFrame 标题样式
        style.configure('TLabelframe', padding=10)
        style.configure('TLabelframe.Label', font=bold_font)
        
        # Notebook (标签页) 样式
        style.configure('TNotebook', padding=5)
        style.configure('TNotebook.Tab', font=default_font, padding=(15, 8))
        
        # Treeview (表格) 样式 - 动态计算行高以适应字体
        import tkinter.font as tkFont
        tree_font = tkFont.Font(font=default_font)
        # 行高 = 字体行高 + 上下内边距（字体高度的1.8倍通常足够）
        row_height = int(tree_font.metrics('linespace') * 1.8)
        row_height = max(row_height, 36)  # 最小36像素确保显示完整
        style.configure('Treeview', font=default_font, rowheight=row_height)
        style.configure('Treeview.Heading', font=bold_font, padding=10)
        
        # 进度条样式
        style.configure('TProgressbar', thickness=20)
        
        # 配置根窗口字体（影响菜单等）
        self.root.option_add('*Font', default_font)
        self.root.option_add('*TkDefaultFont', default_font)
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开CSV文件", command=self._open_csv_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_closing)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空输入", command=self._clear_input)
        edit_menu.add_command(label="加载示例数据", command=self._load_example_data)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="配置设置", command=self._show_settings)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_ui(self):
        """创建主界面"""
        # 创建主容器
        main_container = ttk.Frame(self.root, padding="5")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 输入标签页
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="数据输入")
        self._create_input_panel()
        
        # 结果标签页
        self.result_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.result_frame, text="计算结果")
        self._create_result_panel()
        
        # 配置标签页
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="配置选项")
        self._create_config_panel()
    
    def _create_input_panel(self):
        """创建输入面板"""
        # 输入方式选择（顶部）
        input_type_frame = ttk.LabelFrame(self.input_frame, text="输入方式", padding="10")
        input_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_type = tk.StringVar(value="paste")
        ttk.Radiobutton(input_type_frame, text="粘贴数据", variable=self.input_type, 
                       value="paste", command=self._on_input_type_changed).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(input_type_frame, text="上传CSV文件", variable=self.input_type, 
                       value="file", command=self._on_input_type_changed).pack(side=tk.LEFT, padx=10)
        
        # 进度标签（底部，先pack以确保始终可见）
        self.progress_label = ttk.Label(self.input_frame, text="")
        self.progress_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        
        # 进度条（底部）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.input_frame, variable=self.progress_var, 
                                           mode='determinate', maximum=100)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # 操作按钮（底部）
        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)
        
        ttk.Button(button_frame, text="开始计算", command=self._start_calculation, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="示例数据", command=self._load_example_data).pack(side=tk.LEFT, padx=5)
        
        # 数据输入区域（中间，最后pack以填充剩余空间）
        self.data_input_frame = ttk.LabelFrame(self.input_frame, text="数据输入区域", padding="10")
        self.data_input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 粘贴数据区域
        self.paste_frame = ttk.Frame(self.data_input_frame)
        self.paste_frame.pack(fill=tk.BOTH, expand=True)
        
        hint_text = ("请粘贴SPD数据:\n"
                    "• 第一列必须为波长(nm)，后续列为各样本的光谱数据。（可点击\"示例数据\"按钮查看大致形式）\n"
                    "• 建议：波长范围 ≥ 380~780 nm，波长间隔 ≤ 5nm。否则可能影响结果精度。\n"
                    "• 第一行可为列标题(如:WL(nm) Spectrum_001 Spectrum_002)，也可直接从第一行开始粘贴数据(将自动生成列名)\n"
                    "• 支持从Excel直接复制粘贴。")
        ttk.Label(self.paste_frame, text=hint_text, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 5))
        
        self.text_input = scrolledtext.ScrolledText(self.paste_frame, height=15, wrap=tk.NONE)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 文件选择区域（初始隐藏）
        self.file_frame = ttk.Frame(self.data_input_frame)
        
        file_select_frame = ttk.Frame(self.file_frame)
        file_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_select_frame, text="文件路径：").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_select_frame, text="浏览...", command=self._browse_file).pack(side=tk.LEFT)
        
        # CSV格式要求说明
        csv_hint_text = ("CSV文件格式要求:\n"
                        "• 第一列必须为波长(nm)，后续列为各样本的光谱数据\n"
                        "• 第一行可为列标题，也可直接从第一行开始数据\n"
                        "• 建议：波长范围 ≥ 380~780 nm，波长间隔 ≤ 5nm")
        ttk.Label(self.file_frame, text=csv_hint_text, justify=tk.LEFT, foreground='gray').pack(anchor=tk.W, pady=(5, 0))
    
    def _create_result_panel(self):
        """创建结果面板"""
        # 结果摘要（顶部）
        summary_frame = ttk.LabelFrame(self.result_frame, text="计算结果摘要", padding="10")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.summary_label = ttk.Label(summary_frame, text="尚无计算结果", font=("Microsoft YaHei UI", 10))
        self.summary_label.pack(fill=tk.X)
        
        # 操作按钮（底部，先pack以确保始终可见）
        action_frame = ttk.Frame(self.result_frame)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)
        
        ttk.Button(action_frame, text="导出Excel", command=self._export_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="导出CSV", command=self._export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="可视化", command=self._show_visualization).pack(side=tk.LEFT, padx=5)
        
        # 结果表格（中间，最后pack以填充剩余空间）
        table_frame = ttk.LabelFrame(self.result_frame, text="详细结果表格", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Treeview表格 - 按新顺序显示所有指标
        self.result_columns = ['ID', '还原分级', '喜好分级', '分辨分级',
                  'Ra', 'Rf', '(Ra+Rf)/2', 'MCPI', 'CDM', 'MCPIr', 'CDMr',
                  'CCT', 'Duv', 'x', 'y', "u'", "v'", 'pe', 'hab', 
                  'Rg', 'CRI2012', 
                  'CQS Qa', 'CQS Qf', 'CQS Qg', 'CQS Qp',
                  'MCRI', 'FCI', 'Sneutral', 'GAI', 'CDI76', 'GAI-CRI',
                  'Rd', 'CS', 'CLa']
        
        self.result_tree = ttk.Treeview(table_frame, columns=self.result_columns, show='headings', height=15)
        
        # 设置列标题和宽度（最小宽度，支持自适应）
        column_widths = {
            'ID': 100, '还原分级': 70, '喜好分级': 70, '分辨分级': 70,
            'Ra': 55, 'Rf': 55, '(Ra+Rf)/2': 75, 'MCPI': 60, 'CDM': 60,
            'MCPIr': 65, 'CDMr': 65,
            'CCT': 60, 'Duv': 65, 'x': 60, 'y': 60, "u'": 60, "v'": 60,
            'pe': 60, 'hab': 70,
            'Rg': 55, 'CRI2012': 65,
            'CQS Qa': 65, 'CQS Qf': 65, 'CQS Qg': 65, 'CQS Qp': 65,
            'MCRI': 55, 'FCI': 55, 'Sneutral': 70, 'GAI': 55, 'CDI76': 65, 'GAI-CRI': 70,
            'Rd': 55, 'CS': 55, 'CLa': 55
        }
        
        for col in self.result_columns:
            self.result_tree.heading(col, text=display_metric_name(col), command=lambda c=col: self._sort_by_column(c), anchor='center')
            width = column_widths.get(col, 80)
            # 设置列宽度、最小宽度，居中对齐，并允许拉伸
            self.result_tree.column(col, width=width, minwidth=width, stretch=True, anchor='center')
        
        # 添加滚动条
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.result_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # 初始化列宽（根据标题自适应）
        self._initialize_column_widths(self.result_columns)
    
    def _create_config_panel(self):
        """创建配置面板"""
        # 色度坐标显示观察者选择（顶部）
        cmf_frame = ttk.LabelFrame(self.config_frame, text="色度坐标显示观察者（x, y, u\u2019, v\u2019, p_e, h_ab）", padding="10")
        cmf_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cmf_var = tk.StringVar(value=self.config.get('cmf', '1931_2'))
        cmf_options = [
            ('CIE 1931 2° 标准观察者', '1931_2'),
            ('CIE 1964 10° 标准观察者', '1964_10')
        ]

        cmf_desc = ttk.Label(
            cmf_frame,
            text="仅用于结果表中的色度列（x, y, u\u2019, v\u2019, p_e, h_ab）。\nRa/Rf/Qa/CDI/Rd/Sneutral/MCPI/CDM 等指标\n按各自标准固定观察者计算，不受此选项影响。",
            justify=tk.LEFT,
            foreground='gray'
        )
        cmf_desc.pack(anchor=tk.W, pady=(0, 5))

        for text, value in cmf_options:
            rb = ttk.Radiobutton(cmf_frame, text=text, value=value, variable=self.cmf_var)
            rb.pack(anchor=tk.W, padx=10)
        
        # 保存配置按钮（底部，先pack以确保始终可见）
        ttk.Button(self.config_frame, text="保存配置", command=self._save_config).pack(side=tk.BOTTOM, pady=20)
        
        # 指标选择配置（中间，最后pack以填充剩余空间）
        metrics_config_frame = ttk.LabelFrame(self.config_frame, text="指标选择", padding="10")
        metrics_config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 全选/全不选
        select_all_frame = ttk.Frame(metrics_config_frame)
        select_all_frame.pack(fill=tk.X, pady=5)
        
        self.select_all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(select_all_frame, text="全选", variable=self.select_all_var,
                       command=self._toggle_all_metrics).pack(side=tk.LEFT, padx=5)
        ttk.Label(select_all_frame, text="（勾选需要计算的指标）").pack(side=tk.LEFT, padx=10)
        
        # 创建滚动区域来放置指标复选框
        canvas = tk.Canvas(metrics_config_frame, height=400)
        scrollbar = ttk.Scrollbar(metrics_config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮滚动支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # 递归绑定滚轮事件到所有子组件
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        # 绑定到 canvas 和 scrollable_frame
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # 保存引用以便后续绑定新创建的子组件
        self._config_canvas = canvas
        self._config_mousewheel_handler = _on_mousewheel
        
        # 定义所有指标（按新分类）
        self.available_metrics = {
            '分级': ['还原分级', '喜好分级', '分辨分级'],
            '核心指标': ['Ra', 'Rf', '(Ra+Rf)/2', 'MCPI', 'CDM', 'MCPIr', 'CDMr'],
            '基础指标': ['CCT', 'Duv', 'x', 'y', "u'", "v'", 'pe', 'hab'],
            '其他指标': ['Rg', 'CRI2012', 'CQS Qa', 'CQS Qf', 'CQS Qg', 'CQS Qp', 
                       'MCRI', 'FCI', 'Sneutral', 'GAI', 'CDI76', 'GAI-CRI', 'Rd', 'CS', 'CLa']
        }
        
        # 存储每个指标的复选框变量
        self.metric_vars = {}
        
        # 从配置读取已保存的指标选择状态
        saved_metrics = self.config.get('selected_metrics', {})
        
        # 按分类创建复选框
        for category, metrics in self.available_metrics.items():
            # 分类标题
            category_label = ttk.Label(scrollable_frame, text=category, font=('Microsoft YaHei UI', 10, 'bold'))
            category_label.pack(anchor=tk.W, pady=(10, 5))
            category_label.bind("<MouseWheel>", _on_mousewheel)
            
            # 创建该分类下的指标复选框
            for metric in metrics:
                # 从保存的配置读取状态，默认为True
                is_selected = saved_metrics.get(metric, True)
                var = tk.BooleanVar(value=is_selected)
                self.metric_vars[metric] = var
                cb = ttk.Checkbutton(scrollable_frame, text=display_metric_name(metric), variable=var)
                cb.pack(anchor=tk.W, padx=20, pady=2)
                cb.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 根据已保存的配置更新"全选"复选框状态
        all_selected = all(var.get() for var in self.metric_vars.values())
        self.select_all_var.set(all_selected)
    
    def _on_input_type_changed(self):
        """输入方式改变时的处理"""
        input_type = self.input_type.get()
        
        # 隐藏所有输入框
        self.paste_frame.pack_forget()
        self.file_frame.pack_forget()
        
        # 显示对应的输入框
        if input_type == "paste":
            self.paste_frame.pack(fill=tk.BOTH, expand=True)
        elif input_type == "file":
            self.file_frame.pack(fill=tk.BOTH, expand=True)
    
    def _browse_file(self):
        """浏览选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.config.add_recent_file(file_path)
    
    def _start_calculation(self):
        """开始计算"""
        input_type = self.input_type.get()
        
        try:
            if input_type == "paste":
                self._calculate_from_text()
            elif input_type == "file":
                self._calculate_from_file()
        except Exception as e:
            messagebox.showerror("错误", f"计算过程中出现错误：\n{str(e)}")
            self.progress_label.config(text="计算失败")
    
    def _calculate_from_text(self):
        """从粘贴的文本计算"""
        text = self.text_input.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("警告", "请先输入数据")
            return
        
        # 解析数据
        spd_array, sample_names, validation = self.parser.parse_text(text)
        
        if spd_array is None:
            error_msg = "\n".join(validation['messages'])
            messagebox.showerror("错误", f"数据解析失败：\n{error_msg}")
            return
        
        # 如果有负值，显示提示信息
        if validation.get('has_negative', False):
            messagebox.showinfo("数据处理提示", 
                               "检测到SPD数据中包含负值，已自动将负值替换为0。\n"
                               "计算将继续进行。")
        
        # 如果有其他验证问题（非致命错误）
        if not validation['valid']:
            error_msg = "\n".join(validation['messages'])
            result = messagebox.askyesno("数据验证警告", 
                                        f"数据验证发现以下问题：\n{error_msg}\n\n是否继续计算？")
            if not result:
                return
        
        # 执行计算
        self._execute_calculation(spd_array, sample_names)
    
    def _calculate_from_file(self):
        """从文件计算"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showwarning("警告", "请先选择文件")
            return
        
        # 解析文件
        spd_array, sample_names, validation = self.parser.parse_csv_file(file_path)
        
        if spd_array is None:
            error_msg = "\n".join(validation['messages'])
            messagebox.showerror("错误", f"文件解析失败：\n{error_msg}")
            return
        
        # 如果有负值，显示提示信息
        if validation.get('has_negative', False):
            messagebox.showinfo("数据处理提示", 
                               "检测到SPD数据中包含负值，已自动将负值替换为0。\n"
                               "计算将继续进行。")
        
        # 如果有其他验证问题（非致命错误）
        if not validation['valid']:
            error_msg = "\n".join(validation['messages'])
            result = messagebox.askyesno("数据验证警告", 
                                        f"数据验证发现以下问题：\n{error_msg}\n\n是否继续计算？")
            if not result:
                return
        
        # 执行计算
        self._execute_calculation(spd_array, sample_names)
    
    def _execute_calculation(self, spd_array, sample_names, save_to_file=False, output_name=None):
        """
        执行计算
        
        参数:
            spd_array: ndarray - SPD数组
            sample_names: list - 样本名称列表
            save_to_file: bool - 是否自动保存到文件
            output_name: str - 输出文件名
        """
        # 保存当前数据
        self.current_spd = spd_array
        self.current_sample_names = sample_names
        
        # 更新进度：节流 UI 刷新，避免大量样本时频繁触发 Tk 更新拖慢计算。
        progress_state = {'last_time': 0.0, 'last_current': -1, 'last_message': ''}
        def progress_callback(current, total, message):
            progress_percent = (current / total * 100) if total > 0 else 0
            now = time.monotonic()
            min_step = max(1, total // 100) if total > 0 else 1
            is_boundary = current == 0 or current >= total
            enough_time = now - progress_state['last_time'] >= 0.2
            enough_progress = abs(current - progress_state['last_current']) >= min_step
            message_changed = message != progress_state['last_message']

            if not is_boundary and not (enough_time and (enough_progress or message_changed)):
                return

            progress_state.update({
                'last_time': now,
                'last_current': current,
                'last_message': message,
            })

            def apply_progress(percent=progress_percent, text=message):
                self.progress_var.set(percent)
                self.progress_label.config(text=text)

            self.root.after(0, apply_progress)
        
        # 在新线程中执行计算
        def calculate():
            try:
                # 获取选中的指标
                selected_metrics = {metric: var.get() for metric, var in self.metric_vars.items()}
                
                # 获取 CMF 配置
                cieobs = self.cmf_var.get() if hasattr(self, 'cmf_var') else '1931_2'
                
                results_df = self.calculator.calculate_batch(
                    spd_array, sample_names, progress_callback, selected_metrics, cieobs=cieobs
                )
                
                self.current_results = results_df
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self._update_results(results_df))
                
                if save_to_file and output_name:
                    results_df.to_csv(output_name, index=False, encoding='utf-8-sig')
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("计算错误", str(e)))
                self.root.after(0, lambda: self.progress_label.config(text="计算失败"))
        
        # 启动计算线程
        calc_thread = threading.Thread(target=calculate, daemon=True)
        calc_thread.start()
    
    def _update_results(self, results_df):
        """更新结果显示"""
        # 切换到结果标签页
        self.notebook.select(self.result_frame)
        
        # 更新摘要
        total_samples = len(results_df)
        summary_parts = [f"样本数: {total_samples}"]
        grade_cols = ['还原分级', '喜好分级', '分辨分级']
        if all(col in results_df.columns for col in grade_cols):
            aaa_count = len(results_df[
                (results_df['还原分级'] == 'A') & 
                (results_df['喜好分级'] == 'A') & 
                (results_df['分辨分级'] == 'A')
            ])
            summary_parts.append(f"AAA级: {aaa_count}")
        if 'CCT' in results_df.columns:
            avg_cct = int(results_df['CCT'].mean())
            summary_parts.append(f"平均CCT: {avg_cct}K")

        self.summary_label.config(text="  |  ".join(summary_parts))
        
        # 获取选中的指标
        selected_metrics = {metric: var.get() for metric, var in self.metric_vars.items()}
        
        # 构建要显示的列（ID始终显示）
        display_columns = ['ID']

        # 创建简化列名到完整列名的映射
        metric_mappings = {
            'Ra': 'Ra (CIE 13.3-1995 Ra)',
            'Rf': 'Rf (CIE 224-2017 Rf / IES TM 30-18 Rf)',
            'Rg': 'Rg (IES TM30-18 Rg)',
        }
        
        # 按顺序添加选中的指标
        all_ordered_columns = ['还原分级', '喜好分级', '分辨分级',
                              'Ra', 'Rf', '(Ra+Rf)/2', 'MCPI', 'CDM', 'MCPIr', 'CDMr',
                              'CCT', 'Duv', 'x', 'y', "u'", "v'", 'pe', 'hab', 
                              'Rg', 'CRI2012', 
                              'CQS Qa', 'CQS Qf', 'CQS Qg', 'CQS Qp',
                              'MCRI', 'FCI', 'Sneutral', 'GAI', 'CDI76', 'GAI-CRI',
                              'Rd', 'CS', 'CLa']
        
        for col in all_ordered_columns:
            actual_col = metric_mappings.get(col, col)
            if selected_metrics.get(col, True) and actual_col in results_df.columns:  # 默认显示
                display_columns.append(col)
        
        # 重新配置表格列
        self.result_tree['columns'] = display_columns
        
        # 设置列宽（最小宽度，支持自适应）
        column_widths = {
            'ID': 100, '还原分级': 70, '喜好分级': 70, '分辨分级': 70,
            'Ra': 55, 'Rf': 55, '(Ra+Rf)/2': 75, 'MCPI': 60, 'CDM': 60,
            'MCPIr': 65, 'CDMr': 65,
            'CCT': 60, 'Duv': 65, 'x': 60, 'y': 60, "u'": 60, "v'": 60,
            'pe': 60, 'hab': 70,
            'Rg': 55, 'CRI2012': 65,
            'CQS Qa': 65, 'CQS Qf': 65, 'CQS Qg': 65, 'CQS Qp': 65,
            'MCRI': 55, 'FCI': 55, 'Sneutral': 70, 'GAI': 55, 'CDI76': 65, 'GAI-CRI': 70,
            'Rd': 55, 'CS': 55, 'CLa': 55
        }
        
        for col in display_columns:
            self.result_tree.heading(col, text=display_metric_name(col), command=lambda c=col: self._sort_by_column(c), anchor='center')
            width = column_widths.get(col, 70)
            self.result_tree.column(col, width=width, minwidth=width, stretch=True, anchor='center')
        
        # 清空现有结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 填充结果表格
        for _, row in results_df.iterrows():
            values = []
            
            for col in display_columns:
                if col == 'ID':
                    values.append(str(row['ID']))
                elif col in ['还原分级', '喜好分级', '分辨分级']:
                    values.append(row[col])
                else:
                    # 获取实际的列名
                    actual_col = metric_mappings.get(col, col)
                    
                    if actual_col in row:
                        if col == 'CCT':
                            values.append(row[actual_col])
                        elif col in ['Duv', 'x', 'y', "u'", "v'", 'pe']:
                            values.append(format_number(row[actual_col], 4))
                        elif col == 'hab':
                            hab_value = float(row[actual_col])
                            if hab_value != hab_value:
                                values.append('—')
                            else:
                                values.append(format_number(hab_value, 2))
                        elif col in ['Sneutral', 'CS', 'CLa']:
                            values.append(format_number(row[actual_col], 2))
                        else:
                            values.append(format_number(row[actual_col], 1))
                    else:
                        values.append('N/A')
            
            values = tuple(values)
            
            item = self.result_tree.insert('', tk.END, values=values)
            
            # 根据分级设置颜色标记
            if '还原分级' in display_columns and '还原分级' in row:
                grade = row['还原分级']
                if grade == 'A':
                    self.result_tree.item(item, tags=('grade_a',))
                elif grade == 'B':
                    self.result_tree.item(item, tags=('grade_b',))
        
        # 配置颜色标签
        self.result_tree.tag_configure('grade_a', background='#E8F5E9')
        self.result_tree.tag_configure('grade_b', background='#E3F2FD')
        
        # 自动调整列宽以适应内容
        self._auto_adjust_column_widths(display_columns)
        
        messagebox.showinfo("完成", "计算完成！")
    
    def _initialize_column_widths(self, columns):
        """初始化列宽（仅根据标题）"""
        import tkinter.font as tkFont
        
        # 获取标题字体
        style = ttk.Style()
        heading_font = tkFont.Font(font=style.lookup('Treeview.Heading', 'font'))
        
        for col in columns:
            # 计算标题宽度（增加边距确保完整显示）
            header_width = heading_font.measure(display_metric_name(col)) + 35
            optimal_width = max(header_width, 60)  # 最小60像素
            
            # 设置列宽和居中对齐
            self.result_tree.column(col, width=optimal_width, minwidth=optimal_width, anchor='center')
    
    def _auto_adjust_column_widths(self, columns):
        """根据内容自动调整列宽，并设置居中对齐"""
        import tkinter.font as tkFont
        
        # 获取表格使用的字体
        style = ttk.Style()
        tree_font = tkFont.Font(font=style.lookup('Treeview', 'font'))
        heading_font = tkFont.Font(font=style.lookup('Treeview.Heading', 'font'))
        
        for col in columns:
            # 计算标题宽度（增加更多边距确保完整显示）
            header_width = heading_font.measure(display_metric_name(col)) + 35
            
            # 计算内容最大宽度
            max_content_width = 0
            for item in self.result_tree.get_children():
                values = self.result_tree.item(item, 'values')
                col_index = columns.index(col)
                if col_index < len(values):
                    cell_value = str(values[col_index])
                    cell_width = tree_font.measure(cell_value) + 25
                    max_content_width = max(max_content_width, cell_width)
            
            # 取标题和内容宽度的最大值
            optimal_width = max(header_width, max_content_width, 60)  # 最小60像素
            
            # 设置列宽和居中对齐
            self.result_tree.column(col, width=optimal_width, minwidth=optimal_width, anchor='center')
    
    def _sort_by_column(self, col):
        """按列排序"""
        # TODO: 实现表格排序功能
        pass
    
    def _export_excel(self):
        """导出Excel"""
        if self.current_results is None:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 获取选中的指标
                selected_metrics = {metric: var.get() for metric, var in self.metric_vars.items()}
                
                # 导入导出模块（支持直接运行和模块导入）
                try:
                    from .result_exporter import ResultExporter
                except ImportError:
                    from gui_app.result_exporter import ResultExporter
                
                exporter = ResultExporter()
                exporter.export_to_excel(
                    self.current_results,
                    self.current_spd,
                    self.current_sample_names,
                    file_path,
                    selected_metrics
                )
                messagebox.showinfo("成功", f"已导出到：\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出失败", str(e))
    
    def _export_csv(self):
        """导出CSV"""
        if self.current_results is None:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存CSV文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 获取选中的指标
                selected_metrics = {metric: var.get() for metric, var in self.metric_vars.items()}
                
                # 导入导出模块（支持直接运行和模块导入）
                try:
                    from .result_exporter import ResultExporter
                except ImportError:
                    from gui_app.result_exporter import ResultExporter
                
                exporter = ResultExporter()
                exporter.export_to_csv(self.current_results, file_path, selected_metrics)
                messagebox.showinfo("成功", f"已导出到：\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出失败", str(e))
    
    def _show_visualization(self):
        """显示可视化"""
        if self.current_results is None or self.current_spd is None:
            messagebox.showwarning("警告", "没有可视化的数据")
            return
        
        try:
            # 支持直接运行和作为模块导入
            try:
                from .visualizer import VisualizationWindow
            except ImportError:
                from gui_app.visualizer import VisualizationWindow
            
            vis_window = tk.Toplevel(self.root)
            VisualizationWindow(vis_window, self.current_results, self.current_spd, self.current_sample_names)
        except Exception as e:
            messagebox.showerror("错误", f"可视化失败：\n{str(e)}")
    
    def _toggle_all_metrics(self):
        """全选/全不选指标"""
        select_all = self.select_all_var.get()
        for var in self.metric_vars.values():
            var.set(select_all)
    
    def _clear_input(self):
        """清空输入"""
        self.text_input.delete("1.0", tk.END)
        self.file_path_var.set("")
        self.progress_var.set(0)
        self.progress_label.config(text="")
    
    def _load_example_data(self):
        """加载示例数据"""
        example_text = create_example_spd_text()
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", example_text)
        messagebox.showinfo("提示", "已加载示例数据")
    
    def _open_csv_file(self):
        """打开CSV文件"""
        self.input_type.set("file")
        self._on_input_type_changed()
        self._browse_file()
    
    def _save_config(self):
        """保存配置"""
        # 保存选中的指标
        selected = {metric: var.get() for metric, var in self.metric_vars.items()}
        self.config.set('selected_metrics', selected)
        
        # 保存 CMF 设置
        if hasattr(self, 'cmf_var'):
            self.config.set('cmf', self.cmf_var.get())
        
        self.config.save()
        messagebox.showinfo("成功", "配置已保存")
    
    def _show_settings(self):
        """显示设置"""
        self.notebook.select(self.config_frame)
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
LQCV 光品质指标工具箱使用说明

【数据输入】
1. 粘贴数据：从Excel直接复制粘贴SPD数据
2. 上传CSV：选择包含SPD数据的CSV文件
3. 示例数据：点击"示例数据"按钮查看参考数据格式

【数据格式要求】
• 第一列：波长（nm）
• 后续列：各样本的SPD数据
• 建议波长范围：380-780nm 或更宽
• 建议波长间隔：1-5nm
• 第一行可为列标题，也可直接开始数据
• 如包含负值，将自动替换为0

【计算指标】
• 分级指标：还原分级、喜好分级、分辨分级（A/B/C/D）
• 核心指标：Ra, Rf, (Ra+Rf)/2, MCPI, CDM, MCPIr, CDMr
• 基础指标：CCT, Duv, x, y, u', v', p_e, h_ab
  - p_e：激发纯度，无彩色点为等能白 E，无量纲
  - h_ab：光源色品相对 D65 的 CIELAB 色调角，单位度
• 其他指标：Rg, CRI2012, CQS系列, MCRI, FCI, Sneutral, GAI, 
  CDI76, GAI-CRI, Rd, CS, CLa等

【配置选项】
• CMF选择：支持CIE 1931 2°和CIE 1964 10°标准观察者
  - 仅影响结果表中的 x, y, u′, v′, p_e, h_ab；Ra/Rf/MCPI 等核心指标按各自标准固定观察者
• 指标选择：可勾选需要计算和显示的指标
• 配置保存：设置会自动保存，下次启动自动恢复

【结果导出】
• 导出Excel：包含摘要、完整指标、SPD数据等多个Sheet
• 导出CSV：纯文本格式，可用Excel/记事本打开
• 可视化：生成光谱曲线、色温分布等图表
        """
        messagebox.showinfo("使用说明", help_text)
    
    def _show_about(self):
        """显示关于"""
        about_text = """
LQCV 光品质指标工具箱 v1.0.1
LQCV Lighting Quality Metrics Toolbox (LQMT)

武汉大学 LQCV 课题组
用于从 SPD 计算光源光谱颜色质量指标。

技术：Python + Tkinter + LuxPy (GPLv3)
许可：GPL-3.0-only
安装包：https://gitcode.com/WHU-LQCV/LQMT/releases
问题反馈：https://gitcode.com/WHU-LQCV/LQMT/issues

© 2026 LQCV, Wuhan University
        """
        messagebox.showinfo("关于", about_text)
    
    def _on_closing(self):
        """关闭窗口"""
        # 保存窗口大小
        self.config.set('window_width', self.root.winfo_width())
        self.config.set('window_height', self.root.winfo_height())
        self.config.save()
        
        self.root.destroy()


def main():
    """主函数"""
    # 启用 Windows DPI 感知，使界面在高分辨率屏幕上更清晰
    try:
        import ctypes
        # PROCESS_PER_MONITOR_DPI_AWARE = 2 可以获得最佳效果
        # PROCESS_SYSTEM_DPI_AWARE = 1 是更兼容的选项
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        # 非 Windows 系统或不支持，忽略
        pass
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
