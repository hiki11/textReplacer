# main.py (新的项目入口)
import tkinter as tk
from gui_app import TextProcessorApp # 导入 GUI 主类

if __name__ == "__main__":
    root = tk.Tk()
    app = TextProcessorApp(root)
    root.mainloop()