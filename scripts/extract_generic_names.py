#!/usr/bin/env python3
"""
提取药品通用名
从制剂名称中提取通用名和剂型
例如: "阿司匹林注射液" → 通用名: "阿司匹林", 剂型: "注射液"
"""

import re
import json
from pathlib import Path
from collections import defaultdict


# 常见剂型列表
DOSAGE_FORMS = [
    '注射液', '注射剂', '针剂',
    '片', '片剂',
    '胶囊', '胶囊剂',
    '颗粒', '颗粒剂',
    '散', '散剂',
    '丸', '丸剂',
    '栓', '栓剂',
    '软膏', '软膏剂',
    '乳膏', '乳膏剂',
    '凝胶', '凝胶剂',
    '贴', '贴剂',
    '喷雾', '喷雾剂',
    '吸入', '吸入剂',
    '滴眼', '滴眼液',
    '滴耳', '滴耳液',
    '滴鼻', '滴鼻液',
    '肠溶片', '肠溶胶囊',
    '缓释片', '缓释胶囊',
    '控释片', '控释胶囊',
    '分散片',
    '咀嚼片',
    '泡腾片',
    '口含片',
    '舌下片',
    '薄膜衣片',
    '糖衣片',
    '溶液', '溶液剂',
    '混悬液', '混悬剂',
    '乳剂',
    '糖浆', '糖浆剂',
    '口服液',
    '合剂',
]


def extract_generic_name_and_dosage(drug_name: str) -> tuple:
    """
    从药品名称中提取通用名和剂型
    
    Args:
        drug_name: 药品名称，如"阿司匹林注射液"
    
    Returns:
        (generic_name, dosage_form, is_generic)
        - generic_name: 通用名，如"阿司匹林"
        - dosage_form: 剂型，如"注射液"
        - is_generic: 是否为通用名（无剂型后缀）
    """
    if not drug_name:
        return drug_name, None, True
    
    # 按长度排序，优先匹配长剂型（如"肠溶片"应该在"片"之前）
    sorted_forms = sorted(DOSAGE_FORMS, key=len, reverse=True)
    
    # 尝试匹配剂型
    for form in sorted_forms:
        if drug_name.endswith(form):
            generic_name = drug_name[:-len(form)]
            if generic_name:  # 确保提取到通用名
                return generic_name, form, False
    
    # 如果没有匹配到剂型，可能是通用名
    return drug_name, None, True


def analyze_drugs(data_dir='ontology/data'):
    """分析现有药物数据，提取通用名"""
    data_dir = Path(data_dir)
    
    # 加载药物数据
    drugs_file = data_dir / 'drugs.json'
    if not drugs_file.exists():
        print(f"❌ 文件不存在: {drugs_file}")
        return
    
    with open(drugs_file, 'r', encoding='utf-8') as f:
        drugs = json.load(f)
    
    print("=" * 70)
    print("  药品通用名提取分析")
    print("=" * 70)
    
    # 统计
    generic_to_products = defaultdict(list)
    products_with_generic = {}
    generic_only = []
    
    for drug_name, drug_info in drugs.items():
        generic_name, dosage_form, is_generic = extract_generic_name_and_dosage(drug_name)
        
        if is_generic:
            generic_only.append(drug_name)
        else:
            generic_to_products[generic_name].append({
                'product_name': drug_name,
                'dosage_form': dosage_form
            })
            products_with_generic[drug_name] = {
                'generic_name': generic_name,
                'dosage_form': dosage_form
            }
    
    # 显示统计
    print(f"\n📊 统计信息:")
    print(f"  总药物数: {len(drugs):,}")
    print(f"  通用名（无剂型）: {len(generic_only):,}")
    print(f"  制剂（有剂型）: {len(products_with_generic):,}")
    print(f"  通用名种类: {len(generic_to_products):,}")
    
    # 显示示例
    print(f"\n📋 示例（前10个通用名）:")
    for i, (generic, products) in enumerate(list(generic_to_products.items())[:10], 1):
        print(f"\n  {i}. 通用名: {generic}")
        print(f"     制剂数: {len(products)}")
        print(f"     制剂列表: {', '.join([p['product_name'] for p in products[:5]])}")
        if len(products) > 5:
            print(f"     ... 还有 {len(products) - 5} 个")
    
    # 保存结果
    output_file = data_dir / 'drug_generic_mapping.json'
    mapping = {
        'generic_to_products': {k: v for k, v in generic_to_products.items()},
        'products_with_generic': products_with_generic,
        'generic_only': generic_only,
        'statistics': {
            'total_drugs': len(drugs),
            'generic_count': len(generic_only),
            'product_count': len(products_with_generic),
            'generic_types': len(generic_to_products)
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存到: {output_file}")
    
    return mapping


def update_drugs_with_generic_names(data_dir='ontology/data'):
    """更新药物数据，添加通用名字段"""
    data_dir = Path(data_dir)
    
    # 加载原始数据
    drugs_file = data_dir / 'drugs.json'
    if not drugs_file.exists():
        print(f"❌ 文件不存在: {drugs_file}")
        return
    
    with open(drugs_file, 'r', encoding='utf-8') as f:
        drugs = json.load(f)
    
    # 加载通用名映射
    mapping_file = data_dir / 'drug_generic_mapping.json'
    if mapping_file.exists():
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        products_mapping = mapping.get('products_with_generic', {})
    else:
        products_mapping = {}
        for drug_name in drugs.keys():
            generic_name, dosage_form, is_generic = extract_generic_name_and_dosage(drug_name)
            if not is_generic:
                products_mapping[drug_name] = {
                    'generic_name': generic_name,
                    'dosage_form': dosage_form
                }
    
    # 更新药物数据
    updated_count = 0
    for drug_name, drug_info in drugs.items():
        # 提取通用名
        generic_name, dosage_form, is_generic = extract_generic_name_and_dosage(drug_name)
        
        # 添加字段
        drug_info['generic_name'] = generic_name
        drug_info['is_generic'] = is_generic
        if dosage_form:
            drug_info['dosage_form'] = dosage_form
        
        # 如果是制剂，添加通用名关联
        if not is_generic and generic_name in drugs:
            if 'related_products' not in drugs[generic_name]:
                drugs[generic_name]['related_products'] = []
            if drug_name not in drugs[generic_name]['related_products']:
                drugs[generic_name]['related_products'].append(drug_name)
        
        updated_count += 1
    
    # 保存更新后的数据
    output_file = data_dir / 'drugs_with_generic.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(drugs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {updated_count:,} 个药物，添加通用名字段")
    print(f"✅ 保存到: {output_file}")
    
    return drugs


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='提取药品通用名')
    parser.add_argument('--analyze', action='store_true', help='分析现有数据')
    parser.add_argument('--update', action='store_true', help='更新药物数据，添加通用名字段')
    parser.add_argument('--data-dir', default='ontology/data', help='数据目录')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_drugs(args.data_dir)
    
    if args.update:
        update_drugs_with_generic_names(args.data_dir)
    
    if not args.analyze and not args.update:
        # 默认执行分析和更新
        print("执行分析和更新...")
        analyze_drugs(args.data_dir)
        print("\n" + "=" * 70)
        update_drugs_with_generic_names(args.data_dir)


if __name__ == '__main__':
    main()

