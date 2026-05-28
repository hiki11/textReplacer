# text_processor/__init__.py
# 包级别的导出，方便外部导入
from .preprocessor import TextPreprocessor
from .strategies import SegmentationStrategy, UnitStrategy, CountStrategy

__all__ = [
    'TextPreprocessor',
    'SegmentationStrategy',
    'UnitStrategy',
    'CountStrategy'
]
