#!/usr/bin/env python3
"""
最简单的使用示例 - 只需要3行核心代码！
"""

# ========== 3行核心代码 ==========
from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker

loader = OntologyLoader()                    # 1. 加载本体
linker = EntityLinker(loader.drugs)          # 2. 创建链接器
result = linker.link("阿司匹林")             # 3. 链接实体
# ==================================

# 查看结果
if result:
    print("✅ 匹配成功！")
    print(f"   标准名称: {result['standard_name']}")
    print(f"   实体类型: {result['type']}")
    print(f"   置信度: {result['confidence']}")
else:
    print("❌ 未找到匹配")

# 更多示例
print("\n" + "="*50)
print("更多示例:")
print("="*50)

test_drugs = ["二甲双胍", "胰岛素", "帕博利珠单抗", "阿斯匹林"]

for drug in test_drugs:
    result = linker.link(drug)
    if result:
        print(f"✅ {drug:10} → {result['standard_name']} (置信度: {result['confidence']:.2f})")
    else:
        print(f"❌ {drug:10} → 未匹配")

