# 推荐医学数据源 📊

扩展你的医学知识图谱的高质量数据源

---

## 🎯 药物靶点数据

### 1. TTD (Therapeutic Target Database) ⭐⭐⭐

**网址**: https://ttd.idrblab.cn/full-data-download

**包含内容**:
- ✅ **靶点**: 成功靶点、临床试验靶点、研究靶点
- ✅ **药物**: 已批准药物、临床试验药物、实验药物
- ✅ **疾病**: 疾病分类和关联信息
- ✅ **关系**: 靶点-药物-疾病三元关系

**数据规模**:
- 3,000+ 靶点
- 40,000+ 药物
- 完整的关联关系

**数据格式**: TSV/TXT（易于解析）

**优点**:
- 完全免费，无需注册
- 数据质量高，定期更新
- 中国团队维护，对中文友好
- 包含药物作用机制

**如何使用**:
```bash
# 1. 下载数据
wget https://ttd.idrblab.cn/ttd_download/P1-01-TTD_target_download.txt
wget https://ttd.idrblab.cn/ttd_download/P1-06-Drug_synonyms.txt

# 2. 解析数据（示例）
python scripts/parse_ttd_data.py
```

---

## 💊 药物详细信息

### 2. DrugBank Open Data ⭐⭐⭐

**网址**: https://go.drugbank.com/releases/latest

**包含内容**:
- ✅ 13,000+ 药物
- ✅ 药物结构、分类、靶点
- ✅ 适应症、药代动力学
- ✅ 药物相互作用
- ✅ 不良反应

**数据格式**: XML / CSV

**优点**:
- 免费版包含核心信息
- 数据结构化程度高
- 国际权威标准

**注意**: 需要注册账号，选择 "Open Data" 版本

---

### 3. ChEMBL Database ⭐⭐

**网址**: https://www.ebi.ac.uk/chembl/

**包含内容**:
- 200万+ 化合物
- 生物活性数据
- 药物筛选数据

**数据格式**: SQLite / PostgreSQL dump

**优点**: 完全开放，适合药物发现研究

---

## 🏥 疾病数据

### 4. DisGeNET ⭐⭐⭐

**网址**: https://www.disgenet.org/downloads

**包含内容**:
- ✅ 基因-疾病关联
- ✅ 整合多种数据源（GWAS、文献挖掘）
- ✅ 变异-疾病关联

**数据格式**: TSV（易于解析）

**优点**:
- 数据来源可信
- 关联评分机制
- 定期更新

---

## 🧬 基因与药物基因组学

### 5. PharmGKB ⭐⭐⭐

**网址**: https://www.pharmgkb.org/downloads

**包含内容**:
- 药物-基因-表型关系
- 药物代谢基因标记
- 不良反应基因关联

**优点**: 精准医疗领域权威数据库

**注意**: 需要注册（免费）

---

### 6. Gene Ontology (GO) ⭐⭐

**网址**: http://geneontology.org/

**包含内容**:
- 基因功能注释
- 生物学过程
- 分子功能

**优点**: 标准化的基因功能描述

---

## 💊 药物副作用

### 7. SIDER ⭐⭐

**网址**: http://sideeffects.embl.de/download/

**包含内容**:
- 1,430 种药物
- 140,000+ 药物-副作用关联

**数据格式**: TSV

**优点**: 从药品说明书中提取，可信度高

---

## 🧬 遗传性疾病

### 8. OMIM ⭐

**网址**: https://www.omim.org/downloads

**包含内容**:
- 遗传性疾病-基因关系
- 基因型-表型数据

**优点**: 权威的遗传病数据库

**注意**: 需要申请 API key（免费）

---

## 🚀 快速开始：集成 TTD 数据

### 步骤 1: 下载 TTD 数据

访问 https://ttd.idrblab.cn/full-data-download，下载：

- `P1-01-TTD_target_download.txt` - 靶点信息
- `P1-02-TTD_disease.txt` - 疾病信息
- `P1-05-Drug_disease.txt` - 药物-疾病关系
- `P1-06-Drug_synonyms.txt` - 药物别名

### 步骤 2: 解析并整合

```python
# 示例代码：解析 TTD 靶点数据
import pandas as pd

def parse_ttd_target(file_path):
    """解析 TTD 靶点文件"""
    targets = {}
    current_id = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('TARGETID'):
                current_id = line.split('\t')[1].strip()
                targets[current_id] = {}
            elif current_id and '\t' in line:
                key, value = line.strip().split('\t', 1)
                if key == 'GENENAME':
                    targets[current_id]['gene_name'] = value
                elif key == 'TARGNAME':
                    targets[current_id]['target_name'] = value
                elif key == 'TARGTYPE':
                    targets[current_id]['target_type'] = value
    
    return targets

# 使用
targets = parse_ttd_target('P1-01-TTD_target_download.txt')
print(f"解析到 {len(targets)} 个靶点")
```

### 步骤 3: 整合到你的本体

```python
import json
from ontology.ontology_loader import OntologyLoader

# 加载现有本体
loader = OntologyLoader()

# 添加 TTD 靶点数据
for target_id, target_info in targets.items():
    gene_name = target_info.get('gene_name')
    if gene_name:
        loader.genes[gene_name] = {
            'standard_name': gene_name,
            'type': 'Gene_Target',
            'target_id': target_id,
            'target_type': target_info.get('target_type'),
            'aliases': []
        }

# 保存
with open('ontology/data/genes.json', 'w', encoding='utf-8') as f:
    json.dump(loader.genes, f, ensure_ascii=False, indent=2)

print(f"已添加 {len(loader.genes)} 个基因靶点")
```

---

## 📊 数据源对比

| 数据源 | 药物 | 疾病 | 基因/靶点 | 关系 | 免费 | 难度 |
|--------|------|------|-----------|------|------|------|
| **TTD** | ✅ | ✅ | ✅ | ✅ | 是 | ⭐ 简单 |
| **DrugBank** | ✅ | ✅ | ✅ | ✅ | 部分 | ⭐⭐ 中等 |
| **ChEMBL** | ✅ | ❌ | ✅ | ✅ | 是 | ⭐⭐⭐ 复杂 |
| **DisGeNET** | ❌ | ✅ | ✅ | ✅ | 是 | ⭐⭐ 中等 |
| **PharmGKB** | ✅ | ✅ | ✅ | ✅ | 是 | ⭐⭐ 中等 |
| **SIDER** | ✅ | ❌ | ❌ | 副作用 | 是 | ⭐ 简单 |

---

## 💡 推荐集成顺序

### 第一阶段（已完成）✅
- ✅ NMPA 药品数据（19,551条）
- ✅ ICD-10 疾病数据（35,849条）

### 第二阶段（推荐）
1. **TTD 靶点数据** ← 从这里开始！
   - 简单易用
   - 免费无限制
   - 质量高

2. **SIDER 副作用数据**
   - 数据格式简单
   - 增强药物信息

### 第三阶段（进阶）
3. **DrugBank 详细信息**
   - 药物结构化数据
   - 药物相互作用

4. **DisGeNET 基因-疾病关联**
   - 构建完整的关系网络

---

## 🔧 实用工具脚本

创建 `scripts/parse_ttd_data.py`：

```python
#!/usr/bin/env python3
"""
解析 TTD 数据并整合到本体
"""

import json
from pathlib import Path

def parse_ttd_format(file_path):
    """解析 TTD 的特殊格式"""
    data = {}
    current_id = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
                
            key, value = parts[0], '\t'.join(parts[1:])
            
            # 新记录开始
            if key in ['TARGETID', 'DRUGID', 'DISEASEID']:
                current_id = value
                data[current_id] = {}
            elif current_id:
                data[current_id][key] = value
    
    return data

def main():
    # 解析靶点
    targets = parse_ttd_format('data/ttd/P1-01-TTD_target_download.txt')
    print(f"✅ 解析到 {len(targets)} 个靶点")
    
    # 转换为本体格式
    genes_ontology = {}
    for target_id, info in targets.items():
        gene_name = info.get('GENENAME')
        if gene_name:
            genes_ontology[gene_name] = {
                'standard_name': gene_name,
                'type': 'Gene_Target',
                'target_id': target_id,
                'target_name': info.get('TARGNAME', ''),
                'target_type': info.get('TARGTYPE', ''),
                'aliases': []
            }
    
    # 保存
    output_file = Path('ontology/data/genes.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(genes_ontology, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {len(genes_ontology)} 个基因到 {output_file}")

if __name__ == '__main__':
    main()
```

---

## 📝 注意事项

1. **数据许可**: 使用前请阅读各数据源的许可协议
2. **数据更新**: 建议定期更新数据（TTD 每年更新2-3次）
3. **数据质量**: 不同来源可能有冲突，需要人工审核
4. **存储空间**: ChEMBL 数据库较大（>10GB），按需下载

---

## 🎯 推荐使用 TTD 的理由

1. ✅ **完全免费**: 无需注册，直接下载
2. ✅ **数据质量高**: 人工审核的靶点信息
3. ✅ **易于解析**: TSV 格式，简单清晰
4. ✅ **定期更新**: 每年更新2-3次
5. ✅ **中文友好**: 中国团队维护
6. ✅ **完整关系**: 靶点-药物-疾病三元关系

---

**开始使用**: 访问 [TTD 下载页面](https://ttd.idrblab.cn/full-data-download) 立即下载数据！🚀

