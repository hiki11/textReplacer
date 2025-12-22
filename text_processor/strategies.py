from abc import ABC, abstractmethod
from typing import List
import re

import jieba


class SegmentationStrategy(ABC):
    @abstractmethod
    def split(self, segments: List[str], max_units=8, words_per_segment=3) -> List[str]:
        pass
    
    @classmethod
    def create(cls, strategy_type: str) -> 'SegmentationStrategy':
        if strategy_type == "unit":
            return UnitStrategy()
        elif strategy_type == "count":
            return CountStrategy()
        elif strategy_type == "hybrid":
            return HybridStrategy()
        else:
            raise ValueError(f"不支持的策略类型: {strategy_type}")


class UnitStrategy(SegmentationStrategy):
    """单位值断句"""

    def split(self, segments: List[str], max_units=8, **kwargs) -> List[str]:
        chunks = []
        current_chunk = []
        current_units = 0

        def calc_units(word):
            chn = len(re.findall(r'[\u4e00-\u9fff]', word))
            eng = (len(word) - chn + 1) // 2
            return chn + eng

        for word in segments:
            units = calc_units(word)
            if current_units + units > max_units:
                if current_chunk:
                    chunks.append("".join(current_chunk))
                    current_chunk = []
                    current_units = 0
                if units > max_units:
                    chunks.append(word)
                    continue
            current_chunk.append(word)
            current_units += units
            if current_units >= max_units:
                chunks.append("".join(current_chunk))
                current_chunk = []
                current_units = 0
        if current_chunk:
            chunks.append("".join(current_chunk))
        return chunks


class CountStrategy(SegmentationStrategy):
    """固定词数断句"""

    def split(self, segments: List[str], words_per_segment=3, **kwargs) -> List[str]:
        return [
            "".join(segments[i:i + words_per_segment])
            for i in range(0, len(segments), words_per_segment)
        ]


class HybridStrategy(SegmentationStrategy):
    """先词数后单位值的混合断句"""

    def split(self, segments: List[str], max_units=8, words_per_segment=3, **kwargs) -> List[str]:
        # 第一级按词数分割
        count_split = CountStrategy().split(segments, words_per_segment)
        # 第二级按单位值处理
        final_chunks = []
        for chunk in count_split:
            sub_segments = list(jieba.cut(chunk))
            unit_split = UnitStrategy().split(sub_segments, max_units)
            final_chunks.extend(unit_split)
        return final_chunks