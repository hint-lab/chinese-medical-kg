#!/usr/bin/env python3
"""
整合所有数据源到统一的医学知识图谱本体
"""

import json
from pathlib import Path
from collections import defaultdict


def load_json(file_path):
    """加载JSON文件"""
    if not Path(file_path).exists():
        print(f"⚠️  文件不存在: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def merge_drugs(nmpa_drugs, ttd_drugs):
    """
    合并NMPA和TTD的药物数据
    优先使用NMPA数据，TTD数据作为补充
    """
    merged = {}
    
    # 1. 加载NMPA药物（主要数据源）
    print(f"加载NMPA药物: {len(nmpa_drugs)} 条")
    for drug_name, drug_info in nmpa_drugs.items():
        merged[drug_name] = {
            **drug_info,
            'data_sources': ['NMPA']
        }
    
    # 2. 加载TTD药物（补充数据源）
    print(f"加载TTD药物: {len(ttd_drugs)} 条")
    added_count = 0
    updated_count = 0
    
    for drug_name, drug_info in ttd_drugs.items():
        if drug_name in merged:
            # 已存在，补充TTD信息
            merged[drug_name]['ttd_drug_id'] = drug_info.get('drug_id')
            merged[drug_name]['data_sources'].append('TTD')
            
            # 合并别名
            ttd_aliases = drug_info.get('aliases', [])
            nmpa_aliases = merged[drug_name].get('aliases', [])
            all_aliases = list(set(nmpa_aliases + ttd_aliases))
            merged[drug_name]['aliases'] = all_aliases
            
            updated_count += 1
        else:
            # 新药物，添加
            merged[drug_name] = {
                **drug_info,
                'data_sources': ['TTD']
            }
            added_count += 1
    
    print(f"  - 新增药物: {added_count} 条")
    print(f"  - 更新药物: {updated_count} 条")
    print(f"  - 合并后总计: {len(merged)} 条")
    
    return merged


def merge_diseases(icd_diseases):
    """
    整理ICD-10疾病数据
    """
    print(f"加载ICD-10疾病: {len(icd_diseases)} 条")
    
    merged = {}
    for disease_name, disease_info in icd_diseases.items():
        merged[disease_name] = {
            **disease_info,
            'data_sources': ['ICD-10']
        }
    
    return merged


def merge_genes(ttd_genes):
    """
    整理TTD基因/靶点数据
    """
    print(f"加载TTD基因/靶点: {len(ttd_genes)} 条")
    
    merged = {}
    for gene_name, gene_info in ttd_genes.items():
        merged[gene_name] = {
            **gene_info,
            'data_sources': ['TTD']
        }
    
    return merged


def build_unified_ontology(drugs, diseases, genes):
    """
    构建统一的本体结构
    """
    ontology = {
        'metadata': {
            'version': '1.0.0',
            'created_at': '2025-11-18',
            'description': '中文医学知识图谱统一本体',
            'data_sources': ['NMPA', 'ICD-10', 'TTD'],
            'statistics': {
                'drugs': len(drugs),
                'diseases': len(diseases),
                'genes': len(genes),
                'total_entities': len(drugs) + len(diseases) + len(genes)
            }
        },
        'entities': {
            'drugs': drugs,
            'diseases': diseases,
            'genes': genes
        }
    }
    
    return ontology


def build_entity_index(ontology):
    """
    构建实体索引，用于快速查询
    """
    index = {
        'by_name': {},
        'by_id': {},
        'by_type': defaultdict(list)
    }
    
    # 索引药物
    for name, info in ontology['entities']['drugs'].items():
        index['by_name'][name.lower()] = {'type': 'Drug', 'name': name, 'info': info}
        index['by_type']['Drug'].append(name)
        
        # 索引别名
        for alias in info.get('aliases', []):
            if alias.lower() not in index['by_name']:
                index['by_name'][alias.lower()] = {'type': 'Drug', 'name': name, 'info': info, 'is_alias': True}
        
        # 索引ID
        if 'drug_id' in info:
            index['by_id'][info['drug_id']] = {'type': 'Drug', 'name': name}
        if 'ttd_drug_id' in info:
            index['by_id'][info['ttd_drug_id']] = {'type': 'Drug', 'name': name}
    
    # 索引疾病
    for name, info in ontology['entities']['diseases'].items():
        index['by_name'][name.lower()] = {'type': 'Disease', 'name': name, 'info': info}
        index['by_type']['Disease'].append(name)
        
        # 索引别名
        for alias in info.get('aliases', []):
            if alias.lower() not in index['by_name']:
                index['by_name'][alias.lower()] = {'type': 'Disease', 'name': name, 'info': info, 'is_alias': True}
        
        # 索引ICD编码
        if 'icd_code' in info:
            index['by_id'][info['icd_code']] = {'type': 'Disease', 'name': name}
    
    # 索引基因
    for name, info in ontology['entities']['genes'].items():
        index['by_name'][name.lower()] = {'type': 'Gene', 'name': name, 'info': info}
        index['by_type']['Gene'].append(name)
        
        # 索引靶点ID
        if 'target_id' in info:
            index['by_id'][info['target_id']] = {'type': 'Gene', 'name': name}
    
    return index


def enhance_relations_with_names(relations, index):
    """
    为关系数据添加实体名称（从ID映射到名称）
    """
    enhanced = {
        'target_drug': [],
        'drug_disease': [],
        'target_disease': []
    }
    
    # 靶点-药物关系
    print(f"处理靶点-药物关系: {len(relations.get('target_drug', []))} 条")
    for rel in relations.get('target_drug', []):
        target_id = rel['target_id']
        drug_id = rel['drug_id']
        
        target_info = index['by_id'].get(target_id, {})
        drug_info = index['by_id'].get(drug_id, {})
        
        if target_info and drug_info:
            enhanced['target_drug'].append({
                **rel,
                'target_name': target_info.get('name'),
                'drug_name': drug_info.get('name')
            })
    
    # 药物-疾病关系
    print(f"处理药物-疾病关系: {len(relations.get('drug_disease', []))} 条")
    for rel in relations.get('drug_disease', []):
        drug_id = rel['drug_id']
        disease_id = rel['disease_id']
        
        drug_info = index['by_id'].get(drug_id, {})
        # 疾病ID可能是ICD编码，需要特殊处理
        
        if drug_info:
            enhanced['drug_disease'].append({
                **rel,
                'drug_name': drug_info.get('name')
            })
    
    # 靶点-疾病关系
    print(f"处理靶点-疾病关系: {len(relations.get('target_disease', []))} 条")
    for rel in relations.get('target_disease', []):
        target_id = rel['target_id']
        disease_id = rel['disease_id']
        
        target_info = index['by_id'].get(target_id, {})
        
        if target_info:
            enhanced['target_disease'].append({
                **rel,
                'target_name': target_info.get('name')
            })
    
    return enhanced


def main():
    """主函数"""
    print("=" * 60)
    print("  整合医学知识图谱本体")
    print("=" * 60)
    
    ontology_dir = Path('ontology/data')
    output_dir = Path('ontology/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 加载各数据源
    print("\n[1/5] 加载数据源...")
    
    # NMPA药物数据
    nmpa_drugs = load_json(ontology_dir / 'drugs.json')
    
    # ICD-10疾病数据  
    icd_diseases = load_json(ontology_dir / 'diseases.json')
    
    # TTD数据
    ttd_genes = load_json(ontology_dir / 'genes_ttd.json')
    ttd_drugs = load_json(ontology_dir / 'drugs_ttd.json')
    ttd_relations = load_json(ontology_dir / 'relations_ttd.json')
    
    # 2. 合并数据
    print("\n[2/5] 合并数据...")
    
    merged_drugs = merge_drugs(nmpa_drugs, ttd_drugs)
    merged_diseases = merge_diseases(icd_diseases)
    merged_genes = merge_genes(ttd_genes)
    
    # 3. 构建统一本体
    print("\n[3/5] 构建统一本体...")
    ontology = build_unified_ontology(merged_drugs, merged_diseases, merged_genes)
    
    # 4. 构建索引
    print("\n[4/5] 构建实体索引...")
    index = build_entity_index(ontology)
    print(f"  - 按名称索引: {len(index['by_name'])} 条")
    print(f"  - 按ID索引: {len(index['by_id'])} 条")
    
    # 5. 增强关系数据
    print("\n[5/5] 增强关系数据...")
    enhanced_relations = enhance_relations_with_names(ttd_relations, index)
    
    # 保存结果
    print("\n" + "=" * 60)
    print("  保存整合结果")
    print("=" * 60)
    
    # 保存统一本体
    ontology_file = output_dir / 'unified_ontology.json'
    with open(ontology_file, 'w', encoding='utf-8') as f:
        json.dump(ontology, f, ensure_ascii=False, indent=2)
    print(f"✅ 统一本体: {ontology_file} ({ontology_file.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # 保存索引
    index_file = output_dir / 'entity_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        # 将defaultdict转换为普通dict
        index_to_save = {
            'by_name': index['by_name'],
            'by_id': index['by_id'],
            'by_type': dict(index['by_type'])
        }
        json.dump(index_to_save, f, ensure_ascii=False, indent=2)
    print(f"✅ 实体索引: {index_file} ({index_file.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # 保存增强的关系数据
    relations_file = output_dir / 'enhanced_relations.json'
    with open(relations_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_relations, f, ensure_ascii=False, indent=2)
    print(f"✅ 增强关系: {relations_file} ({relations_file.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("  整合统计")
    print("=" * 60)
    print(f"实体总数: {ontology['metadata']['statistics']['total_entities']:,}")
    print(f"  - 药物: {ontology['metadata']['statistics']['drugs']:,}")
    print(f"  - 疾病: {ontology['metadata']['statistics']['diseases']:,}")
    print(f"  - 基因/靶点: {ontology['metadata']['statistics']['genes']:,}")
    print(f"\n关系总数: {sum(len(v) for v in enhanced_relations.values()):,}")
    print(f"  - 靶点-药物: {len(enhanced_relations['target_drug']):,}")
    print(f"  - 药物-疾病: {len(enhanced_relations['drug_disease']):,}")
    print(f"  - 靶点-疾病: {len(enhanced_relations['target_disease']):,}")
    
    print("\n✅ 整合完成！")
    print("\n下一步:")
    print("  1. 测试查询: python scripts/test_unified_kg.py")
    print("  2. 启动API: python -m src.api.main")
    print("  3. 可视化: python scripts/visualize_kg.py")


if __name__ == '__main__':
    main()

