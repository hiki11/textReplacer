# gui_app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import jieba  # 保持 jieba 导入用于分词
# 导入我们拆分出的模块
from text_processor.preprocessor import TextPreprocessor
from text_processor.strategies import UnitStrategy, CountStrategy, HybridStrategy, SegmentationStrategy
from config_manager import ConfigManager


class TextProcessorApp:
    """智能文本处理器的主应用类
    
    负责管理整个应用的界面和逻辑流程，包括：
    - 初始化界面组件
    - 加载和保存配置
    - 处理用户交互
    - 执行文本处理任务
    """
    def __init__(self, root):
        self.root = root
        self.preprocessor = TextPreprocessor()
        # 默认使用 UnitStrategy，但运行时会根据配置更新
        self.strategy = SegmentationStrategy.create("unit")
        self._load_config()
        self._create_widgets()

        # 初始化时尝试加载上次保存的敏感词表
        if self.sensitive_path:
            self._load_sensitive(initial_load=True)

    def _load_config(self):
        # ... (与原 main.py 代码相同) ...
        self.max_units = ConfigManager.load_config("max_units", 8)
        self.words_per_segment = ConfigManager.load_config("words_per_segment", 3)
        self.strategy_type = ConfigManager.load_config("strategy_type", "unit")
        self.sensitive_path = ConfigManager.load_config("sensitive_path", "")
        # 加载自定义字符设置
        self.use_custom_chars = ConfigManager.load_config("use_custom_chars", False)
        self.custom_remove_chars = ConfigManager.load_config("custom_remove_chars", "")
        self.custom_keep_chars = ConfigManager.load_config("custom_keep_chars", "")

    def _save_config(self):
        # ... (与原 main.py 代码相同) ...
        try:
            ConfigManager.save_config("max_units", int(self.max_units_spin.get()))
            ConfigManager.save_config("words_per_segment", int(self.words_spin.get()))
            ConfigManager.save_config("strategy_type", self.strategy_var.get())
            ConfigManager.save_config("sensitive_path", self.sensitive_path)
            # 保存自定义字符设置
            ConfigManager.save_config("use_custom_chars", self.use_custom_chars_var.get())
            ConfigManager.save_config("custom_remove_chars", self.remove_chars_entry.get())
            ConfigManager.save_config("custom_keep_chars", self.keep_chars_entry.get())
            messagebox.showinfo("提示", "配置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def _create_widgets(self):
        # ... (与原 main.py 代码相同，创建 GUI 组件) ...
        root = self.root
        root.title("智能文本处理器")
        root.geometry("800x600")

        # ... (创建控制面板、策略选择、参数设置等组件) ...
        control_frame = ttk.LabelFrame(root, text="设置")
        control_frame.pack(pady=10, padx=10, fill="x")

        # 策略选择
        ttk.Label(control_frame, text="断句策略:").grid(row=0, column=0, sticky="w")
        self.strategy_var = tk.StringVar(value=self.strategy_type)
        strategies = [("智能单位", "unit"), ("固定词数", "count"), ("混合模式", "hybrid")]
        for col, (text, val) in enumerate(strategies, 1):
            rb = ttk.Radiobutton(control_frame, text=text, variable=self.strategy_var, value=val)
            rb.grid(row=0, column=col, padx=5)

        # 参数设置
        ttk.Label(control_frame, text="最大单位:").grid(row=1, column=0, sticky="e")
        self.max_units_spin = ttk.Spinbox(control_frame, from_=5, to=20, width=5)
        self.max_units_spin.set(self.max_units)
        self.max_units_spin.grid(row=1, column=1)

        ttk.Label(control_frame, text="词数限制:").grid(row=1, column=2, sticky="e")
        self.words_spin = ttk.Spinbox(control_frame, from_=1, to=10, width=5)
        self.words_spin.set(self.words_per_segment)
        self.words_spin.grid(row=1, column=3)

        # 敏感词管理
        self.sensitive_label = ttk.Label(control_frame, text="敏感词表：未加载")
        self.sensitive_label.grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Button(control_frame, text="加载敏感词表", command=self._open_sensitive_dialog).grid(row=2, column=3)

        # 自定义字符处理
        self.use_custom_chars_var = tk.BooleanVar(value=self.use_custom_chars)
        ttk.Checkbutton(control_frame, text="启用自定义字符处理", variable=self.use_custom_chars_var).grid(row=3, column=0, columnspan=4, sticky="w", pady=5)

        # 移除字符输入框
        ttk.Label(control_frame, text="要移除的字符：").grid(row=4, column=0, sticky="w")
        self.remove_chars_entry = ttk.Entry(control_frame, width=40)
        self.remove_chars_entry.grid(row=4, column=1, columnspan=2, sticky="we")
        self.remove_chars_entry.insert(0, self.custom_remove_chars)

        # 保留字符输入框
        ttk.Label(control_frame, text="要保留的字符：").grid(row=5, column=0, sticky="w")
        self.keep_chars_entry = ttk.Entry(control_frame, width=40)
        self.keep_chars_entry.grid(row=5, column=1, columnspan=2, sticky="we")
        self.keep_chars_entry.insert(0, self.custom_keep_chars)

        # 预处理规则文件管理
        self.preprocess_rules_label = ttk.Label(control_frame, text="预处理规则：未加载")
        self.preprocess_rules_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(control_frame, text="加载预处理规则", command=self._open_preprocess_rules_dialog).grid(row=6, column=2)
        ttk.Button(control_frame, text="保存预处理规则", command=self._save_preprocess_rules_dialog).grid(row=6, column=3)

        # 文本区域
        text_frame = ttk.Frame(root)
        text_frame.pack(padx=10, pady=5, expand=True, fill="both")
        self.input_text = tk.Text(text_frame, wrap="word", height=10)
        self.input_text.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(text_frame, command=self.input_text.yview)
        scroll.pack(side="right", fill="y")
        self.input_text.config(yscrollcommand=scroll.set)

        # 操作按钮
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="处理文本", command=self.process).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="保存配置", command=self._save_config).pack(side="left", padx=5)

        # 结果展示
        result_frame = ttk.LabelFrame(root, text="处理结果")
        result_frame.pack(padx=10, pady=5, expand=True, fill="both")
        self.result_text = tk.Text(result_frame, state="disabled")
        self.result_text.pack(fill="both", expand=True)

    def _open_sensitive_dialog(self):
        """打开文件对话框并调用加载函数"""
        path = filedialog.askopenfilename(filetypes=[("Excel文件", "*.xlsx")])
        if path:
            self.sensitive_path = path
            self._load_sensitive()

    def _load_sensitive(self, initial_load=False):
        """加载敏感词表逻辑"""
        # 路径有效性检查
        if not self.sensitive_path or not Path(self.sensitive_path).exists():
            if not initial_load:
                messagebox.showwarning("警告", "敏感词表路径无效。")
            self.sensitive_path = ""
            self.sensitive_label.config(text="敏感词表：未加载")
            ConfigManager.save_config("sensitive_path", "")
            return

        # 调用 TextPreprocessor 中的专业加载函数
        success, msg = self.preprocessor.load_sensitive_words(self.sensitive_path)

        if success:
            self.sensitive_label.config(text=f"已加载：{Path(self.sensitive_path).name} ({msg})")
            ConfigManager.save_config("sensitive_path", self.sensitive_path)
        else:
            self.sensitive_label.config(text=f"加载失败：{Path(self.sensitive_path).name}")
            messagebox.showerror("错误", msg)
            self.sensitive_path = ""  # 加载失败则清除路径

    def _open_preprocess_rules_dialog(self):
        """打开文件对话框选择预处理规则文件"""
        path = filedialog.askopenfilename(filetypes=[("支持的文件", "*.txt *.xlsx")])
        if path:
            self._load_preprocess_rules(path)

    def _load_preprocess_rules(self, path):
        """加载预处理规则文件"""
        # 调用 TextPreprocessor 中的专业加载函数
        success, msg = self.preprocessor.load_preprocess_rules(path)

        if success:
            # 更新界面控件
            self.use_custom_chars_var.set(self.preprocessor.use_custom_chars)
            self.remove_chars_entry.delete(0, tk.END)
            self.remove_chars_entry.insert(0, self.preprocessor.custom_remove_chars)
            self.keep_chars_entry.delete(0, tk.END)
            self.keep_chars_entry.insert(0, self.preprocessor.custom_keep_chars)
            
            self.preprocess_rules_label.config(text=f"已加载：{Path(path).name}")
            messagebox.showinfo("提示", msg)
        else:
            self.preprocess_rules_label.config(text=f"加载失败：{Path(path).name}")
            messagebox.showerror("错误", msg)

    def _save_preprocess_rules_dialog(self):
        """打开文件对话框保存预处理规则"""
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("Excel文件", "*.xlsx")],
            initialfile="preprocess_rules"
        )
        if path:
            # 更新预处理规则
            self.preprocessor.use_custom_chars = self.use_custom_chars_var.get()
            self.preprocessor.custom_remove_chars = self.remove_chars_entry.get()
            self.preprocessor.custom_keep_chars = self.keep_chars_entry.get()
            
            # 保存预处理规则
            success, msg = self.preprocessor.save_preprocess_rules(path)
            if success:
                self.preprocess_rules_label.config(text=f"已保存：{Path(path).name}")
                messagebox.showinfo("提示", msg)
            else:
                messagebox.showerror("错误", msg)

    def process(self):
        # ... (与原 main.py 代码相同，执行处理流程) ...
        # 获取参数
        try:
            self.max_units = int(self.max_units_spin.get())
            self.words_per_segment = int(self.words_spin.get())
            self.strategy_type = self.strategy_var.get()
            self.strategy = SegmentationStrategy.create(self.strategy_type)
            
            # 应用自定义字符设置
            self.use_custom_chars = self.use_custom_chars_var.get()
            self.custom_remove_chars = self.remove_chars_entry.get()
            self.custom_keep_chars = self.keep_chars_entry.get()
            
            # 将设置应用到preprocessor
            self.preprocessor.use_custom_chars = self.use_custom_chars
            self.preprocessor.custom_remove_chars = self.custom_remove_chars
            self.preprocessor.custom_keep_chars = self.custom_keep_chars
            
        except ValueError:
            messagebox.showerror("错误", "最大单位和词数限制必须是有效的整数。")
            return

        # 获取输入文本
        input_text = self.input_text.get("1.0", "end-1c")
        if not input_text.strip():
            messagebox.showwarning("警告", "请输入需要处理的文本")
            return

        try:
            # 预处理（已包含敏感词处理）
            cleaned = self.preprocessor.process(input_text)

            # 分词处理
            # 注意：这里使用 list(jieba.cut) 以保持兼容性
            segments = list(jieba.cut(cleaned))

            # 执行断句策略
            # 策略类现在只接收它需要的参数
            params = {
                "max_units": self.max_units,
                "words_per_segment": self.words_per_segment
            }
            chunks = self.strategy.split(segments, **params)

            # 生成结果
            result = "。".join(chunks).replace("。。", "。").rstrip('。') + "。"

            # 显示结果
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", result)
            self.result_text.config(state="disabled")

        except Exception as e:
            messagebox.showerror("处理错误", f"发生错误：{str(e)}")

# 不再需要 if __name__ == "__main__": 语句，它被移到主启动文件