from abc import ABC, abstractmethod
from typing import List
import re

import jieba


class SegmentationStrategy(ABC):
    _LATIN_PATTERN = re.compile(r'[a-zA-Z0-9\u00c0-\u024f]')
    _PARTICLE_PATTERN = re.compile(r'^[的们了着过地得]$')

    @abstractmethod
    def split(self, segments: List[str], max_units=8, words_per_segment=3) -> List[str]:
        pass

    @staticmethod
    def _merge_latin_tokens(tokens: List[str]) -> List[str]:
        merged = []
        buf = ""
        for t in tokens:
            if SegmentationStrategy._LATIN_PATTERN.match(t):
                buf += t
            else:
                if buf:
                    merged.append(buf)
                    buf = ""
                merged.append(t)
        if buf:
            merged.append(buf)
        return merged

    @staticmethod
    def _merge_quoted_tokens(tokens: List[str]) -> List[str]:
        result = []
        i = 0
        while i < len(tokens):
            if tokens[i] in ('\u201c', '\u2018'):
                close_char = '\u201d' if tokens[i] == '\u201c' else '\u2019'
                buf = tokens[i]
                i += 1
                while i < len(tokens) and tokens[i] != close_char:
                    buf += tokens[i]
                    i += 1
                if i < len(tokens):
                    buf += tokens[i]
                    i += 1
                result.append(buf)
            else:
                result.append(tokens[i])
                i += 1
        return result

    @staticmethod
    def _merge_particles(tokens: List[str]) -> List[str]:
        result = []
        for t in tokens:
            if result and SegmentationStrategy._PARTICLE_PATTERN.match(t):
                result[-1] += t
            else:
                result.append(t)
        return result

    @staticmethod
    def _merge_trailing_dunhao(tokens: List[str]) -> List[str]:
        result = []
        for t in tokens:
            if t == '\u3001' and result:
                result[-1] += t
            else:
                result.append(t)
        return result
    
    @classmethod
    def create(cls, strategy_type: str) -> 'SegmentationStrategy':
        if strategy_type == "unit":
            return UnitStrategy()
        elif strategy_type == "count":
            return CountStrategy()
        else:
            raise ValueError(f"不支持的策略类型: {strategy_type}")


class UnitStrategy(SegmentationStrategy):
    """单位值断句"""

    def split(self, segments: List[str], max_units=8, **kwargs) -> List[str]:
        combined_text = "".join(segments)
        
        combined_text = re.sub(r'。+', '。', combined_text)
        
        sentences = re.findall(r'[^。！？.!?]*[。！？.!?]', combined_text)
        
        remaining_text = re.sub(r'[^。！？.!?]*[。！？.!?]', '', combined_text)
        
        result = []
        
        for sentence in sentences:
            sentence_units = self._calc_units(sentence)
            if sentence_units <= max_units:
                result.append(sentence)
            else:
                result.extend(self._split_by_units(sentence, max_units))
        
        if remaining_text:
            remaining_units = self._calc_units(remaining_text)
            if remaining_units <= max_units:
                result.append(remaining_text)
            else:
                result.extend(self._split_by_units(remaining_text, max_units))
        
        return result
    
    def _split_by_units(self, text: str, max_units: int) -> List[str]:
        raw_tokens = list(jieba.cut(text))
        sub_segments = self._merge_latin_tokens(raw_tokens)
        sub_segments = self._merge_quoted_tokens(sub_segments)
        sub_segments = self._merge_particles(sub_segments)
        chunks = []
        current = ""
        current_units = 0
        for seg in sub_segments:
            seg_units = self._calc_units(seg)
            if current_units + seg_units > max_units and current:
                chunks.append(current)
                current = seg
                current_units = seg_units
            else:
                current += seg
                current_units += seg_units
        if current.strip():
            chunks.append(current)
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                if not re.search(r'[。！？.!?]$', chunks[i]):
                    chunks[i] += '。'
        return chunks
    
    def _calc_units(self, text: str) -> int:
        """计算文本的单位数"""
        chn = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
        eng_chars = len(re.findall(r'[a-zA-Z0-9\u00c0-\u024f]', text))
        eng = (eng_chars + 1) // 2
        quotes = len(re.findall(r'[\u201c\u201d\u2018\u2019]', text))
        dunhao = len(re.findall(r'\u3001', text))
        return chn + eng + quotes + dunhao


class CountStrategy(SegmentationStrategy):
    """固定词数断句"""

    def split(self, segments: List[str], words_per_segment=3, **kwargs) -> List[str]:
        combined_text = "".join(segments)

        combined_text = re.sub(r'。+', '。', combined_text)

        sentences = re.findall(r'[^。！？.!?]*[。！？.!?]', combined_text)

        remaining_text = re.sub(r'[^。！？.!?]*[。！？.!?]', '', combined_text)

        result = []

        for sentence in sentences:
            tokens = list(jieba.cut(sentence))
            words = [t for t in tokens if not re.fullmatch(r'[。！？.!?]+', t)]
            words = self._merge_latin_tokens(words)
            words = self._merge_quoted_tokens(words)
            words = self._merge_particles(words)
            words = self._merge_trailing_dunhao(words)
            for i in range(0, len(words), words_per_segment):
                chunk = "".join(words[i:i + words_per_segment])
                if chunk.strip():
                    result.append(chunk + '。')

        if remaining_text:
            tokens = list(jieba.cut(remaining_text))
            words = [t for t in tokens if not re.fullmatch(r'[。！？.!?]+', t)]
            words = self._merge_latin_tokens(words)
            words = self._merge_quoted_tokens(words)
            words = self._merge_particles(words)
            words = self._merge_trailing_dunhao(words)
            for i in range(0, len(words), words_per_segment):
                chunk = "".join(words[i:i + words_per_segment])
                if chunk.strip():
                    result.append(chunk + '。')

        return result