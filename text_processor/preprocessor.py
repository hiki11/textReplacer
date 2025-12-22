import re
from pathlib import Path


class TextPreprocessor:
    def __init__(self):
        self.sensitive_map = {}
        self.sensitive_path = None
        self.replace_all_punctuation = True
        # 自定义字符相关属性
        self.custom_remove_chars = ''  # 用户要移除的字符
        self.custom_keep_chars = ''    # 用户要保留的字符
        self.use_custom_chars = False   # 是否使用自定义字符模式
        self.preprocess_rules_path = None  # 预处理规则文件路径
        # 标点替换规则
        self.punctuation_replace_map = {',': '。', ';': '。', '!': '。', '?': '。', '；': '。', '！': '。', '？': '。'}

    def _replace_punctuation(self, text: str) -> str:
        """将指定的标点符号替换为句号"""
        for punct, replacement in self.punctuation_replace_map.items():
            text = text.replace(punct, replacement)
        return text

    def _clean_text(self, text: str) -> str:
        """统一的文本清理方法，合并多个清理步骤"""
        # 1. 替换特定标点为句号
        text = self._replace_punctuation(text)
        
        # 2. 清理括号内容
        text = re.sub(r'[$（][^$）]*[)）]', '', text)
        
        # 3. 格式化书名号
        text = re.sub(r'(?<!。)《', '。《', text)
        text = re.sub(r'》(?!。)', '》。', text)
        
        # 4. 清理标点符号（根据自定义规则）
        if self.replace_all_punctuation:
            if self.use_custom_chars:
                # 自定义字符模式：保留中文字符、英文字母、数字、句号、换行符，以及用户指定要保留的字符
                keep_pattern = f'[\u4e00-\u9fa5a-zA-Z0-9。\n{re.escape(self.custom_keep_chars)}]'
                # 如果有要移除的字符，先移除这些字符
                if self.custom_remove_chars:
                    remove_pattern = f'[{re.escape(self.custom_remove_chars)}]'
                    text = re.sub(remove_pattern, '', text)
                # 然后只保留指定的字符
                text = re.sub(f'[^{keep_pattern[1:-1]}]', '', text)
            else:
                # 默认模式：只保留中文字符、英文字母、数字、句号和换行符
                text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9。\n]', '', text)
        
        return text

    def load_sensitive_words(self, excel_path: str):
        """返回加载状态和路径"""
        try:
            import pandas as pd  # 延迟导入，减少启动时间
            
            path = Path(excel_path)
            if not path.exists():
                return False, "文件不存在"

            df = pd.read_excel(path)
            self.sensitive_map = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
            self.sensitive_path = str(path.resolve())
            return True, self.sensitive_path
        except Exception as e:
            return False, str(e)

    def process_pipeline(self, text: str) -> str:
        processors = [
            self._clean_text,
            self._replace_sensitive
        ]
        for processor in processors:
            text = processor(text)
        return text

    def _replace_sensitive(self, text: str) -> str:
        for word, replacement in self.sensitive_map.items():
            text = text.replace(word, replacement)
        return text
    
    def save_preprocess_rules(self, file_path: str) -> (bool, str):
        """保存预处理规则到文件
        
        支持的文件格式：
        - .txt: 使用键值对格式
        - .xlsx: 使用Excel表格格式
        
        返回：(成功标志, 消息)
        """
        try:
            path = Path(file_path)
            file_ext = path.suffix.lower()
            
            if file_ext == '.txt':
                # 保存为文本文件，使用键值对格式
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f"remove_chars:{self.custom_remove_chars}\n")
                    f.write(f"keep_chars:{self.custom_keep_chars}\n")
                    f.write(f"use_custom:{str(self.use_custom_chars)}\n")
            
            elif file_ext == '.xlsx':
                # 保存为Excel文件
                import pandas as pd
                data = {
                    'Rule': ['remove_chars', 'keep_chars', 'use_custom'],
                    'Value': [self.custom_remove_chars, self.custom_keep_chars, str(self.use_custom_chars)]
                }
                df = pd.DataFrame(data)
                df.to_excel(path, index=False)
            
            else:
                return False, "不支持的文件格式，仅支持.txt和.xlsx"
            
            self.preprocess_rules_path = str(path.resolve())
            return True, f"预处理规则已保存到：{path.name}"
        
        except Exception as e:
            return False, f"保存失败：{str(e)}"
    
    def load_preprocess_rules(self, file_path: str) -> (bool, str):
        """从文件加载预处理规则
        
        支持的文件格式：
        - .txt: 使用键值对格式
        - .xlsx: 使用Excel表格格式
        
        返回：(成功标志, 消息)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False, "文件不存在"
                
            file_ext = path.suffix.lower()
            rules = {}
            
            if file_ext == '.txt':
                # 从文本文件加载
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if ':' in line:
                            key, value = line.split(':', 1)
                            rules[key.strip()] = value.strip()
            
            elif file_ext == '.xlsx':
                # 从Excel文件加载
                import pandas as pd
                df = pd.read_excel(path)
                for _, row in df.iterrows():
                    if len(row) >= 2:
                        rules[row[0]] = row[1]
            
            else:
                return False, "不支持的文件格式，仅支持.txt和.xlsx"
            
            # 应用加载的规则
            if 'remove_chars' in rules:
                self.custom_remove_chars = rules['remove_chars']
            if 'keep_chars' in rules:
                self.custom_keep_chars = rules['keep_chars']
            if 'use_custom' in rules:
                self.use_custom_chars = rules['use_custom'].lower() == 'true'
            
            self.preprocess_rules_path = str(path.resolve())
            return True, f"预处理规则已加载：{path.name}"
        
        except Exception as e:
            return False, f"加载失败：{str(e)}"
    
    def process(self, text: str) -> str:
        """简化的处理方法，直接调用处理流水线"""
        return self.process_pipeline(text)
