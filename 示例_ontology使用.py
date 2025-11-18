#!/usr/bin/env python3
"""
中文医学本体使用示例
简单、直观的演示代码
"""

from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_basic_usage():
    """演示基础用法"""
    print_section("1. 加载本体数据")
    
    loader = OntologyLoader()
    print(f"✅ 已加载药物: {len(loader.drugs):,} 条")
    print(f"✅ 已加载疾病: {len(loader.diseases):,} 条")
    print(f"✅ 已加载基因: {len(loader.genes):,} 条")
    
    return loader


def demo_exact_match(linker):
    """演示精确匹配"""
    print_section("2. 精确匹配")
    
    test_drugs = ["阿司匹林", "二甲双胍", "帕博利珠单抗"]
    
    for drug_name in test_drugs:
        result = linker.link(drug_name)
        if result:
            print(f"✅ '{drug_name}'")
            print(f"   标准名: {result['standard_name']}")
            print(f"   置信度: {result['confidence']:.2f}")
            print(f"   匹配类型: {result['match_type']}")
        else:
            print(f"❌ '{drug_name}' - 未找到")


def demo_alias_match(linker):
    """演示别名匹配"""
    print_section("3. 别名识别")
    
    # 注意：这里需要实际存在的别名数据
    test_cases = [
        ("帕博利珠单抗", "标准名"),
        ("可瑞达", "如果有别名数据会匹配"),
    ]
    
    for drug_name, note in test_cases:
        result = linker.link(drug_name)
        if result:
            print(f"✅ '{drug_name}' ({note})")
            print(f"   → 标准名: {result['standard_name']}")
            print(f"   → 置信度: {result['confidence']:.2f}")
        else:
            print(f"ℹ️  '{drug_name}' - {note}")


def demo_fuzzy_match(linker):
    """演示模糊匹配"""
    print_section("4. 模糊匹配（容错）")
    
    # 拼写错误的例子
    test_cases = [
        ("阿斯匹林", 85),    # 错误拼写
        ("二甲双瓜", 80),    # 错误拼写
        ("帕博利单抗", 85),  # 少一个字
    ]
    
    for drug_name, threshold in test_cases:
        result = linker.link(drug_name, threshold=threshold)
        if result:
            print(f"✅ '{drug_name}' (阈值: {threshold})")
            print(f"   → 匹配到: {result['standard_name']}")
            print(f"   → 置信度: {result['confidence']:.2f}")
            print(f"   → 类型: {result['match_type']}")
        else:
            print(f"❌ '{drug_name}' - 未匹配（阈值: {threshold}）")


def demo_batch_processing(linker):
    """演示批量处理"""
    print_section("5. 批量处理")
    
    drug_list = [
        "阿司匹林",
        "二甲双胍",
        "胰岛素",
        "未知药物",
        "帕博利珠单抗",
    ]
    
    print(f"批量处理 {len(drug_list)} 个药物名称...")
    results = linker.link_batch(drug_list)
    
    matched = 0
    for drug_name, result in zip(drug_list, results):
        if result:
            matched += 1
            print(f"✅ {drug_name:12} → {result['standard_name']}")
        else:
            print(f"❌ {drug_name:12} → 未匹配")
    
    print(f"\n匹配率: {matched}/{len(drug_list)} ({matched/len(drug_list)*100:.1f}%)")


def demo_statistics(linker):
    """显示统计信息"""
    print_section("6. 统计信息")
    
    stats = linker.get_statistics()
    print(f"实体总数: {stats['total_entities']:,}")
    print(f"别名总数: {stats['total_aliases']:,}")
    print(f"索引键总数: {stats['total_keys']:,}")


def demo_real_world_example(drug_linker, disease_linker):
    """实际应用场景演示"""
    print_section("7. 实际应用：医疗文本标准化")
    
    # 模拟从医疗文本中提取的实体
    extracted_entities = {
        "drugs": ["阿司匹林", "二甲双胍"],
        "diseases": ["糖尿病", "高血压", "冠心病"]
    }
    
    print("原始文本提取结果:")
    print(f"  药物: {', '.join(extracted_entities['drugs'])}")
    print(f"  疾病: {', '.join(extracted_entities['diseases'])}")
    
    print("\n标准化后:")
    
    # 标准化药物
    standardized_drugs = []
    for drug in extracted_entities['drugs']:
        result = drug_linker.link(drug)
        if result:
            standardized_drugs.append(result['standard_name'])
    print(f"  药物: {', '.join(standardized_drugs)}")
    
    # 标准化疾病
    standardized_diseases = []
    for disease in extracted_entities['diseases']:
        result = disease_linker.link(disease)
        if result:
            standardized_diseases.append(result['standard_name'])
        else:
            standardized_diseases.append(f"{disease}(未匹配)")
    print(f"  疾病: {', '.join(standardized_diseases)}")


def demo_quality_check(linker):
    """演示数据质量检查"""
    print_section("8. 数据质量检查")
    
    # 模拟数据库中的药物名称（有标准的也有非标准的）
    database_drugs = [
        "阿司匹林",      # 标准
        "阿斯匹林",      # 拼写错误
        "不存在的药物",   # 不存在
        "二甲双胍",      # 标准
    ]
    
    print("检查数据库中的药物名称规范性：")
    
    issues = 0
    for drug_name in database_drugs:
        result = linker.link(drug_name)
        
        if result is None:
            print(f"❌ '{drug_name}' - 不在标准本体中，需要人工审核")
            issues += 1
        elif result['match_type'] == 'fuzzy':
            print(f"⚠️  '{drug_name}' - 建议改为 '{result['standard_name']}'")
            issues += 1
        else:
            print(f"✅ '{drug_name}' - 已标准化")
    
    print(f"\n质量评估: 发现 {issues} 个问题")


def main():
    """主函数"""
    print("\n" + "🚀" * 30)
    print("      中文医学本体（Ontology）使用演示")
    print("🚀" * 30)
    
    # 1. 加载数据
    loader = demo_basic_usage()
    
    # 创建链接器
    drug_linker = EntityLinker(loader.drugs)
    disease_linker = EntityLinker(loader.diseases)
    
    # 2-6. 各种匹配演示
    demo_exact_match(drug_linker)
    demo_alias_match(drug_linker)
    demo_fuzzy_match(drug_linker)
    demo_batch_processing(drug_linker)
    demo_statistics(drug_linker)
    
    # 7-8. 实际应用场景
    demo_real_world_example(drug_linker, disease_linker)
    demo_quality_check(drug_linker)
    
    print("\n" + "=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print("\n💡 提示：")
    print("  - 查看详细文档: 快速使用指南.md")
    print("  - 查看本体数据: ontology/data/")
    print("  - 运行测试: pytest tests/")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n可能的原因:")
        print("  1. 未安装依赖: pip install -r requirements.txt")
        print("  2. 本体数据未构建: python scripts/build_ontology.py")
        print("  3. 缺少必要的工具模块")
        import traceback
        traceback.print_exc()

