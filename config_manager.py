# config_manager.py
import winreg

class ConfigManager:
    """配置管理类（使用Windows注册表）"""
    REG_PATH = r"Software\TextProcessorGUI"

    @classmethod
    def save_config(cls, name, value):
        try:
            # 确保键存在
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH)
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_WRITE)
            # 根据值类型保存
            if isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            elif isinstance(value, bool):
                # 将布尔值转换为字符串保存
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
            else:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
        except WindowsError as e:
            # 简化错误处理，避免在 GUI 应用中直接打印
            print(f"配置保存失败: {str(e)}")

    @classmethod
    def load_config(cls, name, default=None):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            
            # 如果默认值是布尔类型，尝试将加载的值转换为布尔值
            if isinstance(default, bool):
                if isinstance(value, str):
                    return value.lower() == 'true'
                return bool(value)
            
            return value
        except WindowsError:
            # 键不存在时返回默认值
            return default