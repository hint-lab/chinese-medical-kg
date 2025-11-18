#!/usr/bin/env python3
"""
解析 TTD 数据并整合到本体
使用方法: python scripts/parse_ttd_data.py
"""

import json
from pathlib import Path
from collections import defaultdict


def parse_ttd_format(file_path):
    """
    解析 TTD 的特殊格式
    
    TTD 格式示例:
    T47101	TARGETID	T47101
    T47101	TARGNAME	Fibroblast growth factor receptor 1
    T47101	GENENAME	FGFR1
    
    格式：ID  字段名  值
    """
    data = {}
    current_id = None
    current_record = {}
    
    print(f"正在解析: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('___') or line.startswith('TTD -'):
                    continue
                
                parts = line.split('\t')
                if len(parts) < 3:
                    continue
                
                record_id = parts[0]  # 第一列：记录ID
                field_name = parts[1]  # 第二列：字段名
                field_value = '\t'.join(parts[2:])  # 第三列及后续：值
                
                # 跳过头部说明行
                if field_name in ['Abbreviation Index:', 'Abbreviations:', 'Title', 'Version', 'Provided by']:
                    continue
                
                # 新记录开始（第一列ID变化，或遇到特定字段）
                if field_name in ['TARGETID', 'DRUG__ID', 'TTDDRUID', 'DISEASEID']:
                    if current_id and current_record:
                        data[current_id] = current_record
                    current_id = record_id
                    current_record = {'id': current_id}
                elif record_id != current_id:
                    # ID变化，保存旧记录，开始新记录
                    if current_id and current_record:
                        data[current_id] = current_record
                    current_id = record_id
                    current_record = {'id': current_id}
                
                # 添加字段到当前记录
                if current_id:
                    if field_name in current_record:
                        # 处理多值字段
                        if not isinstance(current_record[field_name], list):
                            current_record[field_name] = [current_record[field_name]]
                        current_record[field_name].append(field_value)
                    else:
                        current_record[field_name] = field_value
            
            # 保存最后一条记录
            if current_id and current_record:
                data[current_id] = current_record
        
        print(f"✅ 解析完成: {len(data)} 条记录")
        return data
    
    except FileNotFoundError:
        print(f"⚠️  文件不存在: {file_path}")
        return {}


def parse_ttd_synonyms(file_path):
    """
    解析药物同义词文件
    
    格式: DRUGID    Synonym
    """
    synonyms = defaultdict(list)
    
    print(f"正在解析: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    drug_id = parts[0]
                    synonym = parts[1]
                    synonyms[drug_id].append(synonym)
        
        print(f"✅ 解析完成: {len(synonyms)} 个药物的同义词")
        return dict(synonyms)
    
    except FileNotFoundError:
        print(f"⚠️  文件不存在: {file_path}")
        return {}


def parse_ttd_mapping(file_path, id1_name='ID1', id2_name='ID2'):
    """
    解析映射关系文件
    
    格式: ID1    ID2    [其他字段]
    """
    mappings = []
    
    print(f"正在解析: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    mapping = {
                        id1_name: parts[0],
                        id2_name: parts[1]
                    }
                    if len(parts) > 2:
                        mapping['extra'] = parts[2:]
                    mappings.append(mapping)
        
        print(f"✅ 解析完成: {len(mappings)} 条映射关系")
        return mappings
    
    except FileNotFoundError:
        print(f"⚠️  文件不存在: {file_path}")
        return []


def build_gene_ontology(targets, target_drug_mapping):
    """构建基因/靶点本体"""
    genes = {}
    
    for target_id, info in targets.items():
        gene_name = info.get('GENENAME')
        if not gene_name:
            continue
        
        # 统计该靶点对应的药物数量（Excel列名是 TargetID）
        related_drugs = [m for m in target_drug_mapping if m.get('TargetID') == target_id]
        
        genes[gene_name] = {
            'standard_name': gene_name,
            'type': 'Gene_Target',
            'target_id': target_id,
            'target_name': info.get('TARGNAME', ''),
            'target_type': info.get('TARGTYPE', ''),
            'uniprot_id': info.get('UNIPROID', ''),
            'bioclass': info.get('BIOCLASS', ''),
            'aliases': [],
            'related_drugs_count': len(related_drugs),
            'source': 'TTD'
        }
    
    return genes


def extract_generic_name_and_dosage(drug_name: str) -> tuple:
    """从药品名称中提取通用名和剂型"""
    if not drug_name:
        return drug_name, None, True
    
    DOSAGE_FORMS = [
        '注射液', '注射剂', '针剂',
        '肠溶片', '肠溶胶囊',
        '缓释片', '缓释胶囊',
        '控释片', '控释胶囊',
        '分散片', '咀嚼片', '泡腾片', '口含片', '舌下片',
        '薄膜衣片', '糖衣片',
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
        '溶液', '溶液剂',
        '混悬液', '混悬剂',
        '乳剂',
        '糖浆', '糖浆剂',
        '口服液',
        '合剂',
    ]
    
    sorted_forms = sorted(DOSAGE_FORMS, key=len, reverse=True)
    
    for form in sorted_forms:
        if drug_name.endswith(form):
            generic_name = drug_name[:-len(form)]
            if generic_name:
                return generic_name, form, False
    
    return drug_name, None, True


def build_drug_ontology(drugs, synonyms):
    """构建药物本体（包含通用名字段）"""
    drug_ontology = {}
    
    for drug_id, info in drugs.items():
        # 尝试不同的字段名
        drug_name = info.get('DRUGNAME') or info.get('TRADNAME') or info.get('DRUGNONE')
        if not drug_name:
            # 如果没有名称，跳过
            continue
        
        # 提取通用名和剂型
        generic_name, dosage_form, is_generic = extract_generic_name_and_dosage(drug_name)
        
        # 获取别名
        aliases = synonyms.get(drug_id, [])
        
        drug_ontology[drug_name] = {
            'standard_name': drug_name,
            'type': 'Drug',
            'drug_id': drug_id,
            'drug_type': info.get('DRUGTYPE', ''),
            'highest_status': info.get('HIGHSTAT', '') or info.get('HIGHERSTA', ''),
            'therapeutic_class': info.get('THERCLAS', ''),
            'company': info.get('DRUGCOMP', ''),
            'aliases': aliases,
            'source': 'TTD',
            'generic_name': generic_name,
            'is_generic': is_generic
        }
        
        if dosage_form:
            drug_ontology[drug_name]['dosage_form'] = dosage_form
    
    return drug_ontology


def build_relations(target_drug_mapping, drug_disease_mapping, target_disease_mapping):
    """构建关系数据"""
    relations = {
        'target_drug': [],
        'drug_disease': [],
        'target_disease': []
    }
    
    # 靶点-药物关系（Excel格式：TargetID, DrugID, Highest_status, MOA）
    for mapping in target_drug_mapping:
        relations['target_drug'].append({
            'target_id': mapping.get('TargetID', ''),
            'drug_id': mapping.get('DrugID', ''),
            'highest_status': mapping.get('Highest_status', ''),
            'mode_of_action': mapping.get('MOA', ''),
            'relation_type': 'targets'
        })
    
    # 药物-疾病关系（TXT格式：drug_id, disease_id）
    for mapping in drug_disease_mapping:
        relations['drug_disease'].append({
            'drug_id': mapping.get('drug_id', mapping.get('DrugID', '')),
            'disease_id': mapping.get('disease_id', mapping.get('DiseaseID', '')),
            'relation_type': 'treats'
        })
    
    # 靶点-疾病关系（TXT格式：target_id, disease_id）
    for mapping in target_disease_mapping:
        relations['target_disease'].append({
            'target_id': mapping.get('target_id', mapping.get('TargetID', '')),
            'disease_id': mapping.get('disease_id', mapping.get('DiseaseID', '')),
            'relation_type': 'associated_with'
        })
    
    return relations


def main():
    """主函数"""
    print("=" * 60)
    print("  TTD 数据解析与整合")
    print("=" * 60)
    
    # 数据目录（优先使用 data/ttd，如果不存在则尝试 data_sources/ttd）
    root_dir = Path(__file__).resolve().parents[1]
    data_dir = root_dir / 'data' / 'ttd'
    if not data_dir.exists():
        data_dir = root_dir / 'data_sources' / 'ttd'
    
    output_dir = root_dir / 'ontology' / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查数据目录
    if not data_dir.exists():
        print(f"\n❌ 数据目录不存在: {data_dir}")
        print(f"请先创建目录并下载 TTD 数据:")
        print(f"  mkdir -p data/ttd")
        print(f"  ./scripts/download_ttd_data.sh")
        print(f"   或访问: https://ttd.idrblab.cn/full-data-download")
        return
    
    print(f"\n数据目录: {data_dir.absolute()}")
    print(f"输出目录: {output_dir.absolute()}")
    
    # 1. 解析靶点数据
    print("\n[1/6] 解析靶点数据...")
    targets = parse_ttd_format(data_dir / 'P1-01-TTD_target_download.txt')
    
    # 2. 解析药物数据
    print("\n[2/6] 解析药物数据...")
    drugs = parse_ttd_format(data_dir / 'P1-02-TTD_drug_download.txt')
    
    # 3. 解析药物同义词
    print("\n[3/6] 解析药物同义词...")
    synonyms = parse_ttd_synonyms(data_dir / 'P1-04-Drug_synonyms.txt')
    
    # 4. 解析药物-靶点映射（Excel格式）
    print("\n[4/6] 解析药物-靶点映射...")
    # Excel 文件需要用 pandas 解析
    try:
        import pandas as pd
        excel_file = data_dir / 'P1-07-Drug-TargetMapping.xlsx'
        if excel_file.exists():
            df = pd.read_excel(excel_file)
            target_drug_mapping = df.to_dict('records')
            print(f"✅ 解析完成: {len(target_drug_mapping)} 条映射关系")
        else:
            print(f"⚠️  文件不存在: {excel_file}")
            target_drug_mapping = []
    except Exception as e:
        print(f"⚠️  解析失败: {e}")
        target_drug_mapping = []
    
    # 5. 解析药物-疾病映射
    print("\n[5/6] 解析药物-疾病映射...")
    drug_disease_mapping = parse_ttd_mapping(
        data_dir / 'P1-05-Drug_disease.txt',
        'drug_id', 'disease_id'
    )
    
    # 6. 解析靶点-疾病映射
    print("\n[6/6] 解析靶点-疾病映射...")
    target_disease_mapping = parse_ttd_mapping(
        data_dir / 'P1-06-Target_disease.txt',
        'target_id', 'disease_id'
    )
    
    # 构建本体
    print("\n" + "=" * 60)
    print("  构建本体数据")
    print("=" * 60)
    
    # 基因/靶点本体
    print("\n构建基因/靶点本体...")
    genes = build_gene_ontology(targets, target_drug_mapping)
    gene_file = output_dir / 'genes_ttd.json'
    with open(gene_file, 'w', encoding='utf-8') as f:
        json.dump(genes, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(genes)} 个基因到: {gene_file}")
    
    # 药物本体（TTD补充数据）
    print("\n构建药物本体（TTD）...")
    drug_ontology = build_drug_ontology(drugs, synonyms)
    drug_file = output_dir / 'drugs_ttd.json'
    with open(drug_file, 'w', encoding='utf-8') as f:
        json.dump(drug_ontology, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(drug_ontology)} 个药物到: {drug_file}")
    
    # 关系数据
    print("\n构建关系数据...")
    relations = build_relations(target_drug_mapping, drug_disease_mapping, target_disease_mapping)
    relation_file = output_dir / 'relations_ttd.json'
    with open(relation_file, 'w', encoding='utf-8') as f:
        json.dump(relations, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存关系数据到: {relation_file}")
    print(f"  - 靶点-药物: {len(relations['target_drug'])} 条")
    print(f"  - 药物-疾病: {len(relations['drug_disease'])} 条")
    print(f"  - 靶点-疾病: {len(relations['target_disease'])} 条")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("  数据统计")
    print("=" * 60)
    print(f"基因/靶点: {len(genes):,} 个")
    print(f"药物: {len(drug_ontology):,} 个")
    print(f"  - 包含同义词的药物: {sum(1 for d in drug_ontology.values() if d['aliases'])}")
    print(f"  - 总同义词数: {sum(len(d['aliases']) for d in drug_ontology.values()):,}")
    print(f"关系总数: {sum(len(v) for v in relations.values()):,} 条")
    
    print("\n✅ TTD 数据解析完成！")
    print("\n下一步:")
    print("  1. 查看生成的文件: ls -lh ontology/data/*_ttd.json")
    print("  2. 将 TTD 数据合并到主本体: python scripts/merge_ontology.py")
    print("  3. 测试: python simple_example.py")


if __name__ == '__main__':
    main()

