# 测试所有修复是否正常工作
print("=== 测试文本处理器修复 ===")

# 测试1: SegmentationStrategy.create工厂方法
try:
    from text_processor.strategies import SegmentationStrategy
    unit_strategy = SegmentationStrategy.create("unit")
    count_strategy = SegmentationStrategy.create("count")
    hybrid_strategy = SegmentationStrategy.create("hybrid")
    print("✓ 测试1通过: SegmentationStrategy.create工厂方法工作正常")
except Exception as e:
    print(f"✗ 测试1失败: {str(e)}")

# 测试2: TextPreprocessor.process方法
try:
    from text_processor.preprocessor import TextPreprocessor
    preprocessor = TextPreprocessor()
    test_text = "这是一段测试文本，包含逗号,括号(内容)和标点符号！"
    result = preprocessor.process(test_text)
    print("✓ 测试2通过: TextPreprocessor.process方法工作正常")
    print(f"  处理结果: {result}")
except Exception as e:
    print(f"✗ 测试2失败: {str(e)}")

# 测试3: 策略分割功能
try:
    import jieba
    test_text = "这是一段测试文本用于验证策略分割功能"
    segments = list(jieba.cut(test_text))
    chunks = unit_strategy.split(segments, max_units=5)
    print("✓ 测试3通过: 策略分割功能工作正常")
    print(f"  分词结果: {segments}")
    print(f"  分割结果: {chunks}")
except Exception as e:
    print(f"✗ 测试3失败: {str(e)}")

print("=== 所有测试完成 ===")
