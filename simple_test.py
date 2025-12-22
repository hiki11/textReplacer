# 简单测试脚本，直接验证核心修复功能
print("=== 核心功能修复验证 ===")

# 测试1: SegmentationStrategy.create工厂方法
try:
    from text_processor.strategies import SegmentationStrategy
    print("✓ 成功导入 SegmentationStrategy")
    
    unit_strategy = SegmentationStrategy.create("unit")
    count_strategy = SegmentationStrategy.create("count")
    hybrid_strategy = SegmentationStrategy.create("hybrid")
    print("✓ SegmentationStrategy.create工厂方法工作正常")
    print(f"  - UnitStrategy: {type(unit_strategy).__name__}")
    print(f"  - CountStrategy: {type(count_strategy).__name__}")
    print(f"  - HybridStrategy: {type(hybrid_strategy).__name__}")
except Exception as e:
    print(f"✗ 测试1失败: {str(e)}")

# 测试2: TextPreprocessor.process方法
try:
    from text_processor.preprocessor import TextPreprocessor
    print("✓ 成功导入 TextPreprocessor")
    
    preprocessor = TextPreprocessor()
    test_text = "这是一段测试文本，包含逗号,括号(内容)和标点符号！"
    result = preprocessor.process(test_text)
    print("✓ TextPreprocessor.process方法工作正常")
    print(f"  原始文本: {test_text}")
    print(f"  处理结果: {result}")
except Exception as e:
    print(f"✗ 测试2失败: {str(e)}")

# 测试3: 完整的文本处理流程
try:
    import jieba
    from text_processor.preprocessor import TextPreprocessor
    from text_processor.strategies import SegmentationStrategy
    
    print("✓ 成功导入所有核心模块")
    
    # 创建处理器和策略
    preprocessor = TextPreprocessor()
    strategy = SegmentationStrategy.create("unit")
    
    # 测试文本
    test_text = "这是一段测试文本用于验证完整的处理流程，确保所有修复都能正常工作。"
    
    # 预处理
    cleaned_text = preprocessor.process(test_text)
    print(f"✓ 预处理完成: {cleaned_text}")
    
    # 分词
    segments = list(jieba.cut(cleaned_text))
    print(f"✓ 分词完成: {segments}")
    
    # 断句策略应用
    chunks = strategy.split(segments, max_units=5)
    print(f"✓ 策略分割完成: {chunks}")
    
    # 生成最终结果
    final_result = "。".join(chunks).replace("。。", "。").rstrip('。') + "。"
    print(f"✓ 最终结果: {final_result}")
    
    print("✓ 完整处理流程测试通过")
except Exception as e:
    print(f"✗ 测试3失败: {str(e)}")

print("\n=== 所有验证测试完成 ===")
