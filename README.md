# 中文医学知识图谱 🏥

> 简单、准确、开箱即用的中文医学本体标准化系统

[![GitHub](https://img.shields.io/github/stars/hint-lab/chinese-medical-kg?style=social)](https://github.com/hint-lab/chinese-medical-kg)
[English](README_EN.md) | 中文

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 核心特性

- 💊 **19,774** 种药物（NMPA 19,551 + TTD 223）
- 🏥 **35,849** 种疾病（ICD-10 临床版 2.0）
- 🧬 **3,433** 个基因/靶点（TTD）
- 🔗 **11,562** 条实体关系（药物-靶点-疾病）
- 🎯 智能匹配：精确匹配、别名识别、模糊纠错
- ⚡ 高性能：< 10ms 查询速度
- 📦 零配置：开箱即用

---

## 🚀 快速开始（30秒）

### 方式 1：一键运行

```bash
./快速开始.sh
```

### 方式 2：三行代码

```bash
pip install -r requirements.txt
```

```python
from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker

loader = OntologyLoader()                    # 加载本体
linker = EntityLinker(loader.drugs)          # 创建链接器
result = linker.link("阿司匹林")             # 链接实体 ✅
```

### 方式 3：运行示例

```bash
python 最简单示例.py          # 3行代码示例
python 示例_ontology使用.py    # 完整演示
```

### 方式 4：使用数据库版本（推荐）⭐⭐⭐

```bash
# 1. 迁移到SQLite（首次运行，仅需3秒）
python scripts/migrate_to_sqlite.py

# 2. 交互式查询（10-50倍性能提升！）
python kg_query_db.py

# 3. Python API
from ontology.db_loader import MedicalKnowledgeGraphDB
db = MedicalKnowledgeGraphDB()
result = db.search_entity("阿司匹林")  # <1ms ⚡
```

**性能对比**:
- ⚡ 加载时间: 3-5秒 → <100ms (30-50倍)
- ⚡ 查询速度: 10-50ms → <1ms (10-50倍)
- 💾 存储空间: 200MB → 41MB (节省80%)

---

## 🎯 SQLite数据库版本（推荐）⭐⭐⭐

**性能提升10-50倍，存储空间节省80%！**

### 为什么使用SQLite？
- ⚡ **超快查询**: <1ms（JSON需要10-50ms）
- 🚀 **快速加载**: <100ms（JSON需要3-5秒）
- 💾 **节省空间**: 41MB（JSON需要200MB）
- 🔍 **强大查询**: 支持复杂SQL查询和索引
- 📦 **零依赖**: Python内置，无需安装

### 数据规模
- 📊 **59,056** 个医学实体（药物+疾病+基因）
- 🔗 **11,562** 条关系（药物-靶点、靶点-疾病等）
- 📚 **28,298** 个别名（支持快速查询）

### 快速使用

```python
from ontology.db_loader import MedicalKnowledgeGraphDB

# 初始化数据库（<100ms）
db = MedicalKnowledgeGraphDB()

# 搜索实体（<1ms）⚡
result = db.search_entity("阿司匹林", "Drug")

# 查询药物的靶点（<1ms）⚡
targets = db.get_drug_targets("Ibrance")
# → [{'target_name': 'CDK4', 'mode_of_action': 'Modulator'}, ...]

# 查询靶点的药物（<5ms）⚡
drugs = db.get_target_drugs("CDK4")
# → [{'drug_name': 'Ibrance', 'mode_of_action': 'Modulator'}, ...]

# 模糊搜索（<10ms）⚡
results = db.fuzzy_search("糖尿", limit=10)
```

### 三种使用方式

#### 方式1: 交互式查询工具

```bash
python kg_query_db.py
```

#### 方式2: CLI命令行工具

```bash
# 搜索实体
python scripts/kg_cli.py search 阿司匹林 --type Drug

# 模糊搜索
python scripts/kg_cli.py fuzzy 糖尿 --limit 5

# 查询药物的靶点
python scripts/kg_cli.py drug-targets Ibrance

# 查询靶点的药物
python scripts/kg_cli.py target-drugs CDK4

# 查看统计信息
python scripts/kg_cli.py stats

# JSON格式输出
python scripts/kg_cli.py search 阿司匹林 --json
```

#### 方式3: FastAPI RESTful API

```bash
# 启动服务
python -m src.api.main
# 或
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 访问API文档
# http://localhost:8000/docs
```

**API端点**:
- `GET /api/entities/search?name=<name>&type=<type>` - 搜索实体
- `GET /api/entities/fuzzy?keyword=<keyword>` - 模糊搜索
- `GET /api/drugs/{drug_name}/targets` - 查询药物的靶点
- `GET /api/targets/{target_name}/drugs` - 查询靶点的药物
- `GET /api/statistics` - 获取统计信息

**详细文档**: [`docs/API.md`](docs/API.md) 📖

### 性能对比

| 操作 | JSON | SQLite | 提升 |
|------|------|--------|------|
| 加载时间 | 3-5秒 | <100ms | **30-50x** ⚡ |
| 单次查询 | 10-50ms | <1ms | **10-50x** ⚡ |
| 关系查询 | 50-200ms | 1-5ms | **10-40x** ⚡ |
| 内存占用 | 200MB | 10-20MB | **10x** 💾 |
| 文件大小 | 200MB | 41MB | **80%节省** 💾 |

---

## 💡 功能展示

### 1. 精确匹配

```python
result = linker.link("阿司匹林")
# → {'standard_name': '阿司匹林', 'type': 'Drug', 'confidence': 1.0}
```

### 2. 别名识别

```python
result = linker.link("可瑞达")  # 商品名
# → {'standard_name': '帕博利珠单抗', 'confidence': 1.0}
```

### 3. 模糊匹配（自动纠错）

```python
result = linker.link("阿斯匹林")  # 拼写错误
# → {'standard_name': '阿司匹林', 'confidence': 0.95, 'match_type': 'fuzzy'}
```

### 4. 批量处理

```python
drugs = ["阿司匹林", "二甲双胍", "胰岛素"]
results = linker.link_batch(drugs)
```

### 5. 调整匹配阈值

```python
result = linker.link("帕单抗", threshold=70)  # 降低阈值，更宽容
```

---

## 📖 完整使用示例

### 基础用法

```python
from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker

# 1. 加载本体数据
loader = OntologyLoader()
print(f"已加载药物: {len(loader.drugs):,} 条")
print(f"已加载疾病: {len(loader.diseases):,} 条")

# 2. 创建链接器
drug_linker = EntityLinker(loader.drugs)
disease_linker = EntityLinker(loader.diseases)

# 3. 实体链接
result = drug_linker.link("阿司匹林")
if result:
    print(f"标准名: {result['standard_name']}")
    print(f"置信度: {result['confidence']}")
    print(f"类型: {result['match_type']}")
else:
    print("未找到匹配")
```

### 实际应用场景

#### 场景 1：医疗文本标准化

```python
# 原始文本提取的实体
extracted_drugs = ["可瑞达", "阿斯匹林", "二甲双瓜"]

# 标准化
for drug in extracted_drugs:
    result = drug_linker.link(drug)
    if result:
        print(f"{drug} → {result['standard_name']} (置信度: {result['confidence']:.2f})")
    else:
        print(f"{drug} → 未匹配，需要人工审核")
```

#### 场景 2：数据质量检查

```python
# 检查数据库中的药物名称是否规范
database_drugs = ["阿司匹林", "阿斯匹林", "不存在的药", "二甲双胍"]

issues = 0
for drug_name in database_drugs:
    result = drug_linker.link(drug_name)
    
    if result is None:
        print(f"❌ '{drug_name}' - 不在标准本体中")
        issues += 1
    elif result['match_type'] == 'fuzzy':
        print(f"⚠️  '{drug_name}' - 建议改为 '{result['standard_name']}'")
        issues += 1
    else:
        print(f"✅ '{drug_name}' - 已标准化")

print(f"\n发现 {issues} 个问题")
```

#### 场景 3：知识图谱构建

```python
# 构建三元组 (实体1, 关系, 实体2)
drug = drug_linker.link("帕博利珠单抗")
disease = disease_linker.link("肺癌")

if drug and disease:
    triple = (
        drug['standard_name'],
        "适应症",
        disease['standard_name']
    )
    print(f"关系: {triple}")
```

---

## 🔧 扩展本体数据

### 方法 1：手动添加

编辑 `ontology/data/drugs.json`：

```json
{
  "新药名称": {
    "standard_name": "新药标准名",
    "type": "Drug",
    "aliases": ["商品名1", "商品名2"],
    "category": "药物分类",
    "indications": ["适应症1", "适应症2"]
  }
}
```

保存后重新加载：`loader = OntologyLoader()`

### 方法 2：从官方 Excel 构建

```bash
# 准备好官方数据文件（放在 data/ 目录）：
# - 国家临床版2.0疾病诊断编码（ICD-10）.xlsx
# - 国家药品编码本位码信息（国产药品）.xlsx
# - 国家药品编码本位码信息（进口药品）.xlsx

python scripts/build_ontology.py --data-dir ./data --output-dir ./ontology/data
```

---

## 📁 项目结构

```
chinese-medical-kg/
├── README.md                        # 本文件（完整文档）
├── 最简单示例.py                    # 3行代码示例
├── 示例_ontology使用.py              # 完整演示（8个场景）
├── 快速开始.sh                      # 一键运行脚本
├── kg_query_db.py                   # 交互式查询工具（SQLite版）⭐⭐⭐
│
├── ontology/                        # 核心本体模块
│   ├── ontology_loader.py          # 数据加载器（JSON）
│   ├── db_loader.py                # 数据库加载器（SQLite）⭐⭐⭐
│   ├── entity_linker.py            # 实体链接器（Trie+模糊匹配）
│   ├── README.md                   # 技术细节文档
│   └── data/                       # 本体数据
│       ├── medical_kg.db           # SQLite数据库（41MB）⭐⭐⭐
│       ├── drugs.json              # 19,551 种药物（NMPA）
│       ├── diseases.json           # 35,849 种疾病（ICD-10）
│       ├── genes_ttd.json          # 3,433 个基因/靶点（TTD）
│       ├── drugs_ttd.json          # 223 个药物（TTD）
│       ├── relations_ttd.json      # 139K+ 关系（TTD）
│       ├── unified_ontology.json   # 统一本体（整合，47MB）
│       ├── entity_index.json       # 实体索引（152MB）
│       └── enhanced_relations.json # 增强关系（1.7MB）
│
├── scripts/                         # 数据构建与整合脚本
│   ├── build_ontology.py           # 构建基础本体
│   ├── parse_ttd_data.py           # 解析TTD数据
│   ├── merge_ontology.py           # 整合所有数据源
│   ├── migrate_to_sqlite.py        # 迁移到SQLite ⭐⭐⭐
│   ├── kg_cli.py                   # CLI命令行工具 ⭐⭐⭐
│   ├── test_unified_kg.py          # 测试统一图谱
│   └── download_ttd_data.sh        # 下载TTD数据
│
├── src/                             # Python包源码
│   ├── __init__.py
│   └── api/                        # FastAPI服务 ⭐⭐⭐
│       ├── __init__.py
│       └── main.py                 # API主程序
│
├── setup.py                         # pip安装配置 ⭐⭐⭐
├── data/                            # 原始数据
│   └── ttd/                        # TTD数据文件
│
├── tests/                           # 测试
├── utils/                           # 工具模块
├── docs/                            # 文档目录
│   └── API.md                      # API完整使用文档 ⭐⭐⭐
├── 数据源推荐.md                    # 数据源推荐
└── source.md                        # 高质量数据源列表
```

---

## 🎯 适用场景

- ✅ 医学文本实体标准化
- ✅ 知识图谱构建
- ✅ 医学信息抽取
- ✅ 数据质量检查
- ✅ 临床决策支持
- ✅ 电子病历规范化

---

## 📊 数据来源

### 当前已集成 ✅

| 数据源 | 类型 | 数量 | 说明 |
|--------|------|------|------|
| [NMPA](https://www.nmpa.gov.cn/) | 药物 | 19,551 | 国家药监局（国产+进口） |
| [ICD-10](http://www.nhc.gov.cn/) | 疾病 | 35,849 | 国家卫健委临床版 2.0 |
| **[TTD](https://ttd.idrblab.cn/)** ⭐ | 靶点/药物/关系 | 3,433 + 223 + 139K | 靶点数据库（已整合） |

### 推荐扩展数据源

| 数据源 | 类型 | 优势 | 链接 |
|--------|------|------|------|
| **TTD** ⭐⭐⭐ | 靶点/药物/疾病 | 免费、易用、高质量 | [下载](https://ttd.idrblab.cn/full-data-download) |
| DrugBank | 药物详细信息 | 13,000+ 药物，结构化 | [官网](https://go.drugbank.com/) |
| DisGeNET | 基因-疾病关联 | 多源整合，评分机制 | [官网](https://www.disgenet.org/) |
| SIDER | 药物副作用 | 1,430 种药物副作用 | [下载](http://sideeffects.embl.de/) |

**查看完整数据源列表和集成指南**: [`数据源推荐.md`](数据源推荐.md) 📊

### TTD 数据集成（已完成）⭐

```bash
# 1. 下载TTD数据
./scripts/download_ttd_data.sh

# 2. 解析TTD数据
python scripts/parse_ttd_data.py

# 3. 整合到统一本体
python scripts/merge_ontology.py

# 4. 测试
python scripts/test_unified_kg.py
```

**详细说明**: 见 [`数据源推荐.md`](数据源推荐.md) 📋

---

## 🐳 Docker 部署（推荐）

### 快速部署

```bash
# 1. 准备数据库（首次运行）
python scripts/migrate_to_sqlite.py

# 2. 启动服务
docker-compose up -d

# 3. 访问API文档
# http://localhost:8000/docs
```

**详细部署指南**: [`Docker部署指南.md`](Docker部署指南.md) 🐳

---

## ⚙️ 安装

### 方式1: 直接使用（推荐）

```bash
# 安装依赖
pip install -r requirements.txt

# 迁移数据到SQLite
python scripts/migrate_to_sqlite.py
```

### 方式2: pip安装包

```bash
# 安装基础包
pip install -e .

# 安装包含API支持
pip install -e ".[api]"

# 安装所有功能
pip install -e ".[all]"
```

安装后可以使用：
```bash
# CLI工具
medical-kg search 阿司匹林 --type Drug

# Python API
from ontology.db_loader import MedicalKnowledgeGraphDB
db = MedicalKnowledgeGraphDB()
```

主要依赖：
- `rapidfuzz` - 快速模糊匹配
- `pandas` - 数据处理
- `openpyxl` - Excel解析
- `fastapi` - API服务（可选）
- `uvicorn` - ASGI服务器（可选）

---

## 🧪 测试

```bash
# 运行单元测试
pytest tests/

# 运行示例脚本
python 最简单示例.py
python 示例_ontology使用.py
```

---

## 📈 性能指标

### 基础本体
- **数据规模**: 55,400+ 医学实体
- **内存占用**: ~90 MB（包含索引）
- **查询速度**: 
  - 精确匹配: < 1 ms
  - 模糊匹配: < 10 ms
- **匹配准确率**:
  - 精确匹配: 100%
  - 别名匹配: 95%+
  - 模糊匹配: 85%+（阈值85）

### SQLite数据库（推荐）⭐⭐⭐
- **实体总数**: 59,056（药物19,774 + 疾病35,849 + 基因3,433）
- **关系总数**: 11,562（药物-靶点-疾病）
- **别名总数**: 28,298（支持快速查询）
- **文件大小**: 41 MB（比JSON节省80%）
- **加载时间**: <100ms（比JSON快30-50倍）⚡
- **查询速度**: <1ms（比JSON快10-50倍）⚡

---

## ❓ 常见问题

### Q1: 为什么找不到某个药物？

**A**: 可能原因：
1. 该药物不在19,551条NMPA药品库中
2. 是非常新的药物（数据未更新）
3. 名称拼写差异太大

**解决方案**：
```python
# 降低匹配阈值
result = linker.link("药物名", threshold=70)

# 查看是否在本体中
print(list(loader.drugs.keys())[:10])  # 查看前10个

# 手动添加到 ontology/data/drugs.json
```

### Q2: 如何查看已有的所有实体？

```python
loader = OntologyLoader()
print(f"总共 {len(loader.drugs)} 种药物")
print(f"总共 {len(loader.diseases)} 种疾病")

# 查看前10个药物
for i, drug_name in enumerate(list(loader.drugs.keys())[:10]):
    print(f"{i+1}. {drug_name}")
```

### Q3: 模糊匹配太宽松或太严格？

```python
# 默认阈值 85
result = linker.link("药物名", threshold=85)

# 更严格（减少误匹配）
result = linker.link("药物名", threshold=90)

# 更宽容（增加召回率）
result = linker.link("药物名", threshold=75)
```

### Q4: 如何提高查询速度？

```python
# 使用全局单例模式（推荐）
_global_linker = None

def get_drug_linker():
    global _global_linker
    if _global_linker is None:
        loader = OntologyLoader()
        _global_linker = EntityLinker(loader.drugs)
    return _global_linker

# 使用
linker = get_drug_linker()  # 首次加载，后续直接返回
```

### Q5: 如何集成到自己的项目？

```python
# 方式1: 直接导入
from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker

# 方式2: 复制 ontology/ 目录到你的项目
# your_project/
#   ├── ontology/
#   └── your_code.py

# 方式3: 安装为包
pip install -e .
```

---

## 🔍 API 说明

### OntologyLoader

```python
loader = OntologyLoader()

# 属性
loader.drugs        # Dict[str, Dict] - 药物字典
loader.diseases     # Dict[str, Dict] - 疾病字典
loader.genes        # Dict[str, Dict] - 基因字典

# 方法
loader.get_entity_by_type("Drug")      # 获取指定类型的实体
loader.validate_relation(...)           # 验证关系是否合法
```

### EntityLinker

```python
linker = EntityLinker(ontology_dict)

# 主要方法
linker.link(entity_text, threshold=85)              # 链接单个实体
linker.link_batch(entity_texts, threshold=85)       # 批量链接
linker.get_statistics()                              # 获取统计信息

# 返回值格式
{
    'standard_name': '标准名称',
    'type': '实体类型',
    'confidence': 0.95,           # 置信度 (0-1)
    'match_type': 'fuzzy',        # 匹配类型: exact/case_insensitive/fuzzy
    'matched_text': '匹配到的文本',  # 仅模糊匹配时有
    # ... 其他实体属性
}
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 如何贡献数据

1. Fork 本项目
2. 添加新的实体到 `ontology/data/*.json`
3. 运行测试确保格式正确
4. 提交 Pull Request

---

## 📄 许可证

MIT License

---

## 🎓 学习路径

### 新手（5分钟）
1. 运行 `./快速开始.sh` 或 `python 最简单示例.py`
2. 查看输出，理解功能

### 入门（15分钟）
1. 阅读本文档的"完整使用示例"部分
2. 修改示例代码，测试自己的数据

### 进阶（30分钟）
1. 运行 `python 示例_ontology使用.py`
2. 学习8个实际应用场景
3. 尝试扩展本体数据

### 高级（1小时+）
1. 阅读 `ontology/README.md` 技术文档
2. 研究代码实现（Trie树、模糊匹配算法）
3. 集成到自己的项目
4. 贡献新的数据源

---

## 📞 获取帮助

### 快速入门
- **最简单示例**: `python 最简单示例.py`
- **完整演示**: `python 示例_ontology使用.py`
- **一键运行**: `./快速开始.sh`

### API和工具
- **API文档**: [`docs/API.md`](docs/API.md) ⭐⭐⭐
- **交互查询**: `python kg_query_db.py`

### 技术文档
- **本体技术**: `ontology/README.md`
- **数据源推荐**: [`数据源推荐.md`](数据源推荐.md)
- **高质量数据源**: `source.md`

### 问题反馈
- **提交 Issue**: [GitHub Issues](https://github.com/hint-lab/chinese-medical-kg/issues)

---

**开始使用**: 

```bash
# 方式1: 基础功能
./快速开始.sh

# 方式2: SQLite数据库版本（强烈推荐）⭐⭐⭐
python scripts/migrate_to_sqlite.py   # 首次迁移（仅需3秒）
python kg_query_db.py                  # 交互式查询

# 方式3: CLI命令行工具
python scripts/kg_cli.py search 阿司匹林 --type Drug

# 方式4: FastAPI服务
python -m src.api.main                 # 启动API服务
# 访问 http://localhost:8000/docs

# 方式5: pip安装包
pip install -e .                       # 安装包
from ontology.db_loader import MedicalKnowledgeGraphDB
```

🚀 **现已支持药物-靶点-疾病三层知识图谱！**
⚡ **SQLite版本：查询速度提升10-50倍，存储空间节省80%！**
📦 **提供CLI、FastAPI、pip包三种使用方式！**

*最后更新: 2025-11-18*
