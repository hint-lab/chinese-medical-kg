# 医学本体系统使用文档

## 📚 概述

轻量级医学本体系统，专为医学信息抽取任务设计。

**当前规模（2025-11-18）**：
- 药物实体：19,551 条（国家药监局国产/进口药品编码）
- 疾病实体：35,849 条（国家卫健委 ICD-10 临床版 2.0）
- 基因靶点：2 条（示例，待补充）
- **总计**：55,402 条

**内存占用**：约 90 MB（JSON 文件 + 进程内 Trie）

## 🎯 数据来源

1. **ICD-10 临床版 2.0**（国家卫生健康委 / 国家临床版编码）
2. **国家药品编码本位码信息（国产/进口）**（国家药监局 NMPA）
3. **PubChem / NMPA 官网**（补充字段）
4. （可选）MeSH、CCKS、OpenKG 等增量数据源

## 📁 文件结构

```
ontology/
├── README.md                    # 本文件
├── __init__.py                  # 模块初始化
├── ontology_loader.py           # 本体加载器
├── entity_linker.py             # 实体链接器（Trie+模糊匹配）
└── data/                        # 本体数据
    ├── drugs.json               # 药物词典
    ├── diseases.json            # 疾病词典
    ├── genes.json               # 基因词典
    ├── manufacturers.json       # 药企词典
    └── relations.json           # 关系类型定义
```

## 🚀 快速使用

### 1. 加载本体

```python
from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker

# 加载本体（自动加载所有数据文件）
loader = OntologyLoader()

# 为每种实体类型创建链接器
drug_linker = EntityLinker(loader.drugs)
disease_linker = EntityLinker(loader.diseases)
gene_linker = EntityLinker(loader.genes)
```

### 2. 实体链接

```python
# 精确匹配
result = drug_linker.link("帕博利珠单抗")
# 返回: {"standard_name": "帕博利珠单抗", "type": "Drug", "confidence": 1.0, ...}

# 别名匹配
result = drug_linker.link("可瑞达")  # 商品名
# 返回: {"standard_name": "帕博利珠单抗", ...}

# 模糊匹配
result = drug_linker.link("帕博利单抗")  # 拼写错误
# 返回: {"standard_name": "帕博利珠单抗", "confidence": 0.9, "match_type": "fuzzy"}

# 未匹配
result = drug_linker.link("未知药物")
# 返回: None
```

### 3. Schema对齐

```python
from agents.schema_alignment import SchemaAlignmentAgent

aligner = SchemaAlignmentAgent()

# 对提取的实体进行规范化
extraction_result = {
    "entities": [
        {"name": "可瑞达", "type": "Drug", "mentions": 3},  # 别名
        {"name": "NSCLC", "type": "Disease", "mentions": 5}  # 英文缩写
    ],
    "relations": [...]
}

aligned_result = await aligner.align(extraction_result)
# 返回规范化后的实体和验证过的关系
```

### 4. 冲突检测

```python
from agents.conflict_resolution import ConflictResolutionAgent

resolver = ConflictResolutionAgent()

# 检测并消解冲突
final_result = await resolver.detect_and_resolve(aligned_result)
# 返回消解后的结果，包含冲突标记和质量评分
```

## 📊 支持的实体类型

### 药物 (Drug)
- 免疫检查点抑制剂（PD-1/PD-L1抑制剂）
- 靶向治疗药物（EGFR-TKI、ALK抑制剂）
- 常用基础药物（阿司匹林、二甲双胍等）

### 疾病 (Disease)
- 常见肿瘤（非小细胞肺癌、乳腺癌等）
- 慢性病（糖尿病、高血压、冠心病）

### 基因靶点 (Gene_Target)
- 免疫检查点（PD-1、PD-L1）
- 酪氨酸激酶（EGFR、ALK、ROS1）
- 原癌基因（KRAS）

## 🔄 扩展词典

### 方法1：手动添加

编辑 `data/*.json` 文件：

```json
{
  "新药物名称": {
    "standard_name": "标准名称",
    "generic_name": "通用名",
    "type": "Drug",
    "aliases": ["别名1", "别名2"],
    "category": "分类",
    "indications": ["适应症1", "适应症2"]
  }
}
```

### 方法2：使用构建脚本

```bash
cd scripts
# 方式 A：直接解析官方 Excel（推荐）
python3 parse_official_medical_excel.py

# 方式 B：在线获取轻量词典（示例）
python3 download_chinese_medical_ontology.py
```

### 方法3：动态积累（推荐）

系统会自动记录未匹配的实体，定期审核后添加。

## 🧪 测试

```bash
# 运行本体测试
python3 test_ontology.py

# 测试包括：
# 1. 实体链接测试（精确、别名、模糊匹配）
# 2. Schema对齐测试
# 3. 冲突检测测试
```

## ⚡ 性能特点

- **内存占用**：<1MB（当前规模）
- **查询速度**：<10ms（精确匹配）
- **匹配准确率**：
  - 精确匹配：100%
  - 别名匹配：95%+
  - 模糊匹配：85%+（阈值80）

## 📈 扩展计划

1. **短期**（1-2周）：
   - 扩展到100个常用药物
   - 50个常见疾病
   - 30个热门基因

2. **中期**（1-2月）：
   - 整合更多MeSH术语
   - 添加药物-疾病关系
   - 症状和检查指标

3. **长期**（持续）：
   - 实施渐进式学习
   - API回退机制
   - 跨本体映射

## 🔗 外部资源

- MeSH: https://www.ncbi.nlm.nih.gov/mesh
- CCKS: https://www.biendata.xyz/competition/ccks_2019_2/
- OpenKG: http://openkg.cn/
- DrugBank: https://go.drugbank.com/
- Gene Ontology: http://geneontology.org/

## 📝 注意事项

1. **不要直接修改运行时的本体数据**
2. **添加新术语后需要重启服务**
3. **定期备份词典文件**
4. **模糊匹配阈值可调整**（默认85）

## 🐛 故障排查

### 问题1：实体无法匹配

```python
# 检查是否在本体中
print(loader.drugs.keys())

# 调低模糊匹配阈值
result = linker.link(entity_name, threshold=70)
```

### 问题2：内存占用过高

当前不会出现，未来如果词典扩展到10000+条：
- 考虑按需加载
- 使用数据库存储
- 实施缓存策略

### 问题3：加载速度慢

```python
# 预加载并缓存
from ontology import EntityLinker

# 全局单例
_linker_cache = {}

def get_linker(entity_type):
    if entity_type not in _linker_cache:
        _linker_cache[entity_type] = EntityLinker(...)
    return _linker_cache[entity_type]
```

## 📞 反馈

如有问题或建议，请提Issue或PR。

