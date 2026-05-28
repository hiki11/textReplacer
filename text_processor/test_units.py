#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import jieba
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from strategies import UnitStrategy

def test_unit_calculation():
    """测试各种文本的单位计算"""
    
    strategy = UnitStrategy()
    
    test_cases = [
        # 中文词汇
        "听",
        "我", 
        "举个",
        "例子",
        "听我举个",
        "听我举个例子",
        "听我举个例子。你",
        
        # 包含标点
        "听我举个例子。",
        "你就全明白了。",
        
        # 英文混合
        "hello",
        "hello world",
        "测试hello",
        "hello测试",
        
        # 数字和符号
        "123",
        "2024年",
        "￥100",
    ]
    
    print("=== 单位计算测试 ===")
    for text in test_cases:
        units = strategy._calc_units(text)
        print(f"文本: '{text}' -> 单位: {units}")
    
    print("\n=== 分词后的单位计算 ===")
    text = "听我举个例子。你就全明白了。"
    segments = list(jieba.cut(text))
    print(f"分词结果: {segments}")
    
    cumulative_units = 0
    for word in segments:
        units = strategy._calc_units(word)
        cumulative_units += units
        print(f"词: {word}，单位: {units}，累计单位: {cumulative_units}")

if __name__ == "__main__":
    test_unit_calculation()