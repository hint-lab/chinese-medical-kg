#!/usr/bin/env python3
"""
测试统一知识图谱的查询功能
"""

import json
from pathlib import Path


class UnifiedKnowledgeGraph:
    """统一医学知识图谱"""
    
    def __init__(self, data_dir='ontology/data'):
        self.data_dir = Path(data_dir)
        self.ontology = None
        self.index = None
        self.relations = None
        self.load()
    
    def load(self):
        """加载知识图谱数据"""
        print("加载统一知识图谱...")
        
        # 加载本体
        with open(self.data_dir / 'unified_ontology.json', 'r', encoding='utf-8') as f:
            self.ontology = json.load(f)
        
        # 加载索引
        with open(self.data_dir / 'entity_index.json', 'r', encoding='utf-8') as f:
            self.index = json.load(f)
        
        # 加载关系
        with open(self.data_dir / 'enhanced_relations.json', 'r', encoding='utf-8') as f:
            self.relations = json.load(f)
        
        print(f"✅ 加载完成:")
        print(f"  - 实体: {self.ontology['metadata']['statistics']['total_entities']:,} 个")
        print(f"  - 索引: {len(self.index['by_name']):,} 条")
        print(f"  - 关系: {sum(len(v) for v in self.relations.values()):,} 条")
    
    def search_entity(self, name, entity_type=None):
        """搜索实体"""
        name_lower = name.lower()
        
        # 精确匹配
        if name_lower in self.index['by_name']:
            result = self.index['by_name'][name_lower]
            if entity_type is None or result['type'] == entity_type:
                return result
        
        # 模糊匹配
        matches = []
        for key, value in self.index['by_name'].items():
            if name_lower in key:
                if entity_type is None or value['type'] == entity_type:
                    matches.append(value)
        
        return matches if matches else None
    
    def get_drug_targets(self, drug_name):
        """查询药物的靶点"""
        targets = []
        for rel in self.relations['target_drug']:
            if rel.get('drug_name') == drug_name:
                targets.append({
                    'target': rel.get('target_name'),
                    'mode_of_action': rel.get('mode_of_action'),
                    'status': rel.get('highest_status')
                })
        return targets
    
    def get_target_drugs(self, target_name):
        """查询靶点的药物"""
        drugs = []
        for rel in self.relations['target_drug']:
            if rel.get('target_name') == target_name:
                drugs.append({
                    'drug': rel.get('drug_name'),
                    'mode_of_action': rel.get('mode_of_action'),
                    'status': rel.get('highest_status')
                })
        return drugs
    
    def get_drug_diseases(self, drug_name):
        """查询药物治疗的疾病"""
        diseases = []
        for rel in self.relations['drug_disease']:
            if rel.get('drug_name') == drug_name:
                diseases.append({
                    'disease_id': rel.get('disease_id'),
                    'drug_id': rel.get('drug_id')
                })
        return diseases
    
    def get_statistics(self):
        """获取统计信息"""
        return self.ontology['metadata']['statistics']


def demo():
    """演示知识图谱功能"""
    print("=" * 60)
    print("  统一医学知识图谱 - 功能演示")
    print("=" * 60)
    
    # 初始化
    kg = UnifiedKnowledgeGraph()
    
    # 1. 搜索实体
    print("\n【演示 1】搜索药物")
    print("-" * 60)
    drug = kg.search_entity("阿司匹林", "Drug")
    if drug:
        print(f"✅ 找到药物: {drug['name']}")
        print(f"   类型: {drug['type']}")
        if not drug.get('is_alias'):
            info = drug['info']
            print(f"   数据来源: {', '.join(info.get('data_sources', []))}")
            print(f"   别名数量: {len(info.get('aliases', []))}")
    
    # 2. 搜索疾病
    print("\n【演示 2】搜索疾病")
    print("-" * 60)
    disease = kg.search_entity("糖尿病", "Disease")
    if disease:
        if isinstance(disease, list):
            print(f"✅ 找到 {len(disease)} 个相关疾病:")
            for d in disease[:5]:
                print(f"   - {d['name']}")
        else:
            print(f"✅ 找到疾病: {disease['name']}")
    
    # 3. 搜索基因/靶点
    print("\n【演示 3】搜索基因/靶点")
    print("-" * 60)
    gene = kg.search_entity("EGFR", "Gene")
    if gene:
        print(f"✅ 找到靶点: {gene['name']}")
        info = gene['info']
        print(f"   靶点名称: {info.get('target_name', '')}")
        print(f"   靶点类型: {info.get('target_type', '')}")
        print(f"   生化分类: {info.get('bioclass', '')}")
        print(f"   相关药物: {info.get('related_drugs_count', 0)} 个")
        
        # 查询相关药物
        drugs = kg.get_target_drugs("EGFR")
        if drugs:
            print(f"\n   关联的药物:")
            for drug in drugs[:5]:
                print(f"     - {drug['drug']} ({drug['mode_of_action']}, {drug['status']})")
    
    # 4. 查询药物的靶点
    print("\n【演示 4】查询药物的靶点")
    print("-" * 60)
    test_drugs = ["Ibrance", "Rydapt"]
    for drug_name in test_drugs:
        targets = kg.get_drug_targets(drug_name)
        if targets:
            print(f"✅ {drug_name} 的靶点:")
            for target in targets[:3]:
                print(f"   - {target['target']} ({target['mode_of_action']})")
    
    # 5. 统计信息
    print("\n【演示 5】知识图谱统计")
    print("-" * 60)
    stats = kg.get_statistics()
    print(f"实体总数: {stats['total_entities']:,}")
    print(f"  - 药物: {stats['drugs']:,}")
    print(f"  - 疾病: {stats['diseases']:,}")
    print(f"  - 基因/靶点: {stats['genes']:,}")
    
    # 6. 数据来源
    print("\n【演示 6】数据来源")
    print("-" * 60)
    sources = kg.ontology['metadata']['data_sources']
    print(f"数据来源: {', '.join(sources)}")
    
    print("\n" + "=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print("\n提示: 你可以用这个类来构建自己的应用")
    print("示例:")
    print("  kg = UnifiedKnowledgeGraph()")
    print("  result = kg.search_entity('阿司匹林')")
    print("  targets = kg.get_drug_targets('Ibrance')")


if __name__ == '__main__':
    demo()

