# Chinese Medical Knowledge Graph 🏥

> Simple, accurate, and ready-to-use Chinese medical ontology standardization system

[![GitHub](https://img.shields.io/github/stars/hint-lab/chinese-medical-kg?style=social)](https://github.com/hint-lab/chinese-medical-kg)
[English](README_EN.md) | [中文](README.md)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Core Features

- 💊 **19,774** drugs (NMPA 19,551 + TTD 223)
- 🏥 **35,849** diseases (ICD-10 Clinical Edition 2.0)
- 🧬 **3,433** genes/targets (TTD)
- 🔗 **11,562** entity relationships (drug-target-disease)
- 🎯 Smart matching: exact match, alias recognition, fuzzy correction
- ⚡ High performance: < 10ms query speed
- 📦 Zero configuration: ready to use out of the box

---

## 🚀 Quick Start (30 seconds)

### Method 1: One-click run

```bash
./快速开始.sh
```

### Method 2: Three lines of code

```bash
pip install -r requirements.txt
```

```python
from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker

loader = OntologyLoader()                    # Load ontology
linker = EntityLinker(loader.drugs)          # Create linker
result = linker.link("阿司匹林")             # Link entity ✅
```

### Method 3: Run examples

```bash
python 最简单示例.py          # 3-line code example
python 示例_ontology使用.py    # Complete demo
```

### Method 4: Database version (Recommended) ⭐⭐⭐

```bash
# 1. Migrate to SQLite (first run, only 3 seconds)
python scripts/migrate_to_sqlite.py

# 2. Interactive query (10-50x performance boost!)
python kg_query_db.py

# 3. Python API
from ontology.db_loader import MedicalKnowledgeGraphDB
db = MedicalKnowledgeGraphDB()
result = db.search_entity("阿司匹林")  # <1ms ⚡
```

**Performance comparison**:
- ⚡ Load time: 3-5s → <100ms (30-50x faster)
- ⚡ Query speed: 10-50ms → <1ms (10-50x faster)
- 💾 Storage: 200MB → 41MB (80% reduction)

---

## 🎯 SQLite Database Version (Recommended) ⭐⭐⭐

**10-50x performance boost, 80% storage reduction!**

### Why use SQLite?
- ⚡ **Ultra-fast queries**: <1ms (JSON needs 10-50ms)
- 🚀 **Fast loading**: <100ms (JSON needs 3-5s)
- 💾 **Space saving**: 41MB (JSON needs 200MB)
- 🔍 **Powerful queries**: Supports complex SQL queries and indexes
- 📦 **Zero dependencies**: Built into Python, no installation needed

### Data Scale
- 📊 **59,056** medical entities (drugs + diseases + genes)
- 🔗 **11,562** relationships (drug-target, target-disease, etc.)
- 📚 **28,298** aliases (supports fast queries)

### Quick Usage

```python
from ontology.db_loader import MedicalKnowledgeGraphDB

# Initialize database (<100ms)
db = MedicalKnowledgeGraphDB()

# Search entity (<1ms) ⚡
result = db.search_entity("阿司匹林", "Drug")

# Query drug targets (<1ms) ⚡
targets = db.get_drug_targets("Ibrance")
# → [{'target_name': 'CDK4', 'mode_of_action': 'Modulator'}, ...]

# Query target drugs (<5ms) ⚡
drugs = db.get_target_drugs("CDK4")
# → [{'drug_name': 'Ibrance', 'mode_of_action': 'Modulator'}, ...]

# Fuzzy search (<10ms) ⚡
results = db.fuzzy_search("糖尿", limit=10)
```

### Three Usage Methods

#### Method 1: Interactive query tool

```bash
python kg_query_db.py
```

#### Method 2: CLI command-line tool

```bash
# Search entity
python scripts/kg_cli.py search 阿司匹林 --type Drug

# Fuzzy search
python scripts/kg_cli.py fuzzy 糖尿 --limit 5

# Query drug targets
python scripts/kg_cli.py drug-targets Ibrance

# Query target drugs
python scripts/kg_cli.py target-drugs CDK4

# View statistics
python scripts/kg_cli.py stats

# JSON output
python scripts/kg_cli.py search 阿司匹林 --json
```

#### Method 3: FastAPI RESTful API

```bash
# Start service
python -m src.api.main
# or
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

**API Endpoints**:
- `GET /api/entities/search?name=<name>&type=<type>` - Search entity
- `GET /api/entities/fuzzy?keyword=<keyword>` - Fuzzy search
- `GET /api/drugs/{drug_name}/targets` - Query drug targets
- `GET /api/targets/{target_name}/drugs` - Query target drugs
- `GET /api/statistics` - Get statistics

**Detailed documentation**: [`docs/API.md`](docs/API.md) 📖

### Performance Comparison

| Operation | JSON | SQLite | Improvement |
|-----------|------|--------|-------------|
| Load time | 3-5s | <100ms | **30-50x** ⚡ |
| Single query | 10-50ms | <1ms | **10-50x** ⚡ |
| Relation query | 50-200ms | 1-5ms | **10-40x** ⚡ |
| Memory usage | 200MB | 10-20MB | **10x** 💾 |
| File size | 200MB | 41MB | **80% saved** 💾 |

---

## 💡 Feature Showcase

### 1. Exact Match

```python
result = linker.link("阿司匹林")
# → {'standard_name': '阿司匹林', 'type': 'Drug', 'confidence': 1.0}
```

### 2. Alias Recognition

```python
result = linker.link("可瑞达")  # Brand name
# → {'standard_name': '帕博利珠单抗', 'confidence': 1.0}
```

### 3. Fuzzy Match (Auto-correction)

```python
result = linker.link("阿斯匹林")  # Typo
# → {'standard_name': '阿司匹林', 'confidence': 0.95, 'match_type': 'fuzzy'}
```

### 4. Batch Processing

```python
drugs = ["阿司匹林", "二甲双胍", "胰岛素"]
results = linker.link_batch(drugs)
```

### 5. Adjust Match Threshold

```python
result = linker.link("帕单抗", threshold=70)  # Lower threshold, more tolerant
```

---

## 🐳 Docker Deployment (Recommended)

### Quick Deployment

```bash
# 1. Prepare database (first run)
python scripts/migrate_to_sqlite.py

# 2. Start service
docker-compose up -d

# 3. Access API docs
# http://localhost:8000/docs
```

**Detailed deployment guide**: [`Docker部署指南.md`](Docker部署指南.md) 🐳

---

## ⚙️ Installation

### Method 1: Direct use (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Migrate data to SQLite
python scripts/migrate_to_sqlite.py
```

### Method 2: pip package

```bash
# Install base package
pip install -e .

# Install with API support
pip install -e ".[api]"

# Install all features
pip install -e ".[all]"
```

After installation, you can use:
```bash
# CLI tool
medical-kg search 阿司匹林 --type Drug

# Python API
from ontology.db_loader import MedicalKnowledgeGraphDB
db = MedicalKnowledgeGraphDB()
```

Main dependencies:
- `rapidfuzz` - Fast fuzzy matching
- `pandas` - Data processing
- `openpyxl` - Excel parsing
- `fastapi` - API service (optional)
- `uvicorn` - ASGI server (optional)

---

## 📁 Project Structure

```
chinese-medical-kg/
├── README.md                        # This file (complete documentation)
├── README_EN.md                     # English README
├── 最简单示例.py                    # 3-line code example
├── 示例_ontology使用.py              # Complete demo (8 scenarios)
├── 快速开始.sh                      # One-click run script
├── kg_query_db.py                   # Interactive query tool (SQLite) ⭐⭐⭐
│
├── ontology/                        # Core ontology module
│   ├── ontology_loader.py          # Data loader (JSON)
│   ├── db_loader.py                # Database loader (SQLite) ⭐⭐⭐
│   ├── entity_linker.py            # Entity linker (Trie + fuzzy match)
│   ├── README.md                   # Technical details
│   └── data/                       # Ontology data
│       ├── medical_kg.db           # SQLite database (41MB) ⭐⭐⭐
│       ├── drugs.json              # 19,551 drugs (NMPA)
│       ├── diseases.json           # 35,849 diseases (ICD-10)
│       ├── genes_ttd.json          # 3,433 genes/targets (TTD)
│       ├── drugs_ttd.json          # 223 drugs (TTD)
│       ├── relations_ttd.json      # 139K+ relations (TTD)
│       ├── unified_ontology.json   # Unified ontology (47MB)
│       ├── entity_index.json       # Entity index (152MB)
│       └── enhanced_relations.json # Enhanced relations (1.7MB)
│
├── scripts/                         # Data build and integration scripts
│   ├── build_ontology.py           # Build base ontology
│   ├── parse_ttd_data.py           # Parse TTD data
│   ├── merge_ontology.py           # Merge all data sources
│   ├── migrate_to_sqlite.py        # Migrate to SQLite ⭐⭐⭐
│   ├── kg_cli.py                   # CLI tool ⭐⭐⭐
│   ├── test_unified_kg.py          # Test unified KG
│   └── download_ttd_data.sh        # Download TTD data
│
├── src/                             # Python package source
│   ├── __init__.py
│   └── api/                        # FastAPI service ⭐⭐⭐
│       ├── __init__.py
│       └── main.py                 # API main program
│
├── setup.py                         # pip installation config ⭐⭐⭐
├── Dockerfile                       # Docker image config
├── docker-compose.yml               # Docker Compose config
├── data/                            # Raw data
│   └── ttd/                        # TTD data files
│
├── tests/                           # Tests
├── utils/                           # Utility modules
├── docs/                            # Documentation directory
│   └── API.md                      # Complete API documentation ⭐⭐⭐
├── 数据源推荐.md                    # Data source recommendations
└── source.md                        # High-quality data source list
```

---

## 🎯 Use Cases

- ✅ Medical text entity standardization
- ✅ Knowledge graph construction
- ✅ Medical information extraction
- ✅ Data quality checking
- ✅ Clinical decision support
- ✅ Electronic medical record normalization

---

## 📊 Data Sources

### Currently Integrated ✅

| Data Source | Type | Count | Description |
|-------------|------|-------|-------------|
| [NMPA](https://www.nmpa.gov.cn/) | Drugs | 19,551 | National Medical Products Administration (domestic + imported) |
| [ICD-10](http://www.nhc.gov.cn/) | Diseases | 35,849 | National Health Commission Clinical Edition 2.0 |
| **[TTD](https://ttd.idrblab.cn/)** ⭐ | Targets/Drugs/Relations | 3,433 + 223 + 139K | Target database (integrated) |

### Recommended Extended Data Sources

| Data Source | Type | Advantages | Link |
|-------------|------|------------|------|
| **TTD** ⭐⭐⭐ | Targets/Drugs/Diseases | Free, easy to use, high quality | [Download](https://ttd.idrblab.cn/full-data-download) |
| DrugBank | Drug details | 13,000+ drugs, structured | [Official](https://go.drugbank.com/) |
| DisGeNET | Gene-disease associations | Multi-source integration, scoring | [Official](https://www.disgenet.org/) |
| SIDER | Drug side effects | 1,430 drug side effects | [Download](http://sideeffects.embl.de/) |

**View complete data source list and integration guide**: [`数据源推荐.md`](数据源推荐.md) 📊

### TTD Data Integration (Completed) ⭐

```bash
# 1. Download TTD data
./scripts/download_ttd_data.sh

# 2. Parse TTD data
python scripts/parse_ttd_data.py

# 3. Merge into unified ontology
python scripts/merge_ontology.py

# 4. Test
python scripts/test_unified_kg.py
```

**Detailed description**: See [`数据源推荐.md`](数据源推荐.md) 📋

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run example scripts
python 最简单示例.py
python 示例_ontology使用.py
```

---

## 📈 Performance Metrics

### Base Ontology
- **Data scale**: 55,400+ medical entities
- **Memory usage**: ~90 MB (including indexes)
- **Query speed**: 
  - Exact match: < 1 ms
  - Fuzzy match: < 10 ms
- **Match accuracy**:
  - Exact match: 100%
  - Alias match: 95%+
  - Fuzzy match: 85%+ (threshold 85)

### SQLite Database (Recommended) ⭐⭐⭐
- **Total entities**: 59,056 (19,774 drugs + 35,849 diseases + 3,433 genes)
- **Total relations**: 11,562 (drug-target-disease)
- **Total aliases**: 28,298 (supports fast queries)
- **File size**: 41 MB (80% smaller than JSON)
- **Load time**: <100ms (30-50x faster than JSON) ⚡
- **Query speed**: <1ms (10-50x faster than JSON) ⚡

---

## ❓ FAQ

### Q1: Why can't I find a certain drug?

**A**: Possible reasons:
1. The drug is not in the 19,551 NMPA drug database
2. It's a very new drug (data not updated)
3. Name spelling difference is too large

**Solutions**:
```python
# Lower match threshold
result = linker.link("drug_name", threshold=70)

# Check if it's in the ontology
print(list(loader.drugs.keys())[:10])  # View first 10

# Manually add to ontology/data/drugs.json
```

### Q2: How to view all existing entities?

```python
loader = OntologyLoader()
print(f"Total {len(loader.drugs)} drugs")
print(f"Total {len(loader.diseases)} diseases")

# View first 10 drugs
for i, drug_name in enumerate(list(loader.drugs.keys())[:10]):
    print(f"{i+1}. {drug_name}")
```

### Q3: Fuzzy match too loose or too strict?

```python
# Default threshold 85
result = linker.link("drug_name", threshold=85)

# More strict (reduce false matches)
result = linker.link("drug_name", threshold=90)

# More tolerant (increase recall)
result = linker.link("drug_name", threshold=75)
```

### Q4: How to improve query speed?

```python
# Use global singleton pattern (recommended)
_global_linker = None

def get_drug_linker():
    global _global_linker
    if _global_linker is None:
        loader = OntologyLoader()
        _global_linker = EntityLinker(loader.drugs)
    return _global_linker

# Use
linker = get_drug_linker()  # Load once, return directly afterwards
```

### Q5: How to integrate into your own project?

```python
# Method 1: Direct import
from ontology.ontology_loader import OntologyLoader
from ontology.entity_linker import EntityLinker

# Method 2: Copy ontology/ directory to your project
# your_project/
#   ├── ontology/
#   └── your_code.py

# Method 3: Install as package
pip install -e .
```

---

## 🔍 API Documentation

### OntologyLoader

```python
loader = OntologyLoader()

# Attributes
loader.drugs        # Dict[str, Dict] - Drug dictionary
loader.diseases     # Dict[str, Dict] - Disease dictionary
loader.genes        # Dict[str, Dict] - Gene dictionary

# Methods
loader.get_entity_by_type("Drug")      # Get entities by type
loader.validate_relation(...)           # Validate if relation is legal
```

### EntityLinker

```python
linker = EntityLinker(ontology_dict)

# Main methods
linker.link(entity_text, threshold=85)              # Link single entity
linker.link_batch(entity_texts, threshold=85)       # Batch link
linker.get_statistics()                              # Get statistics

# Return format
{
    'standard_name': 'Standard name',
    'type': 'Entity type',
    'confidence': 0.95,           # Confidence (0-1)
    'match_type': 'fuzzy',        # Match type: exact/case_insensitive/fuzzy
    'matched_text': 'Matched text',  # Only for fuzzy match
    # ... other entity attributes
}
```

### MedicalKnowledgeGraphDB

```python
db = MedicalKnowledgeGraphDB()

# Main methods
db.search_entity(name, entity_type=None)      # Search entity (supports partial match)
db.fuzzy_search(keyword, limit=10)            # Fuzzy search
db.get_drug_targets(drug_name)                # Query drug targets
db.get_target_drugs(target_name)              # Query target drugs
db.get_statistics()                           # Get statistics
```

---

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

### How to contribute data

1. Fork this project
2. Add new entities to `ontology/data/*.json`
3. Run tests to ensure format is correct
4. Submit Pull Request

---

## 📄 License

MIT License

---

## 🎓 Learning Path

### Beginner (5 minutes)
1. Run `./快速开始.sh` or `python 最简单示例.py`
2. View output, understand features

### Getting Started (15 minutes)
1. Read the "Complete Usage Examples" section of this document
2. Modify example code, test with your own data

### Intermediate (30 minutes)
1. Run `python 示例_ontology使用.py`
2. Learn 8 practical application scenarios
3. Try extending ontology data

### Advanced (1 hour+)
1. Read `ontology/README.md` technical documentation
2. Study code implementation (Trie tree, fuzzy matching algorithm)
3. Integrate into your own project
4. Contribute new data sources

---

## 📞 Get Help

### Quick Start
- **Simplest example**: `python 最简单示例.py`
- **Complete demo**: `python 示例_ontology使用.py`
- **One-click run**: `./快速开始.sh`

### API and Tools
- **API documentation**: [`docs/API.md`](docs/API.md) ⭐⭐⭐
- **Interactive query**: `python kg_query_db.py`

### Technical Documentation
- **Ontology technology**: `ontology/README.md`
- **Data source recommendations**: [`数据源推荐.md`](数据源推荐.md)
- **High-quality data sources**: `source.md`

### Issue Reporting
- **Submit Issue**: [GitHub Issues](https://github.com/hint-lab/chinese-medical-kg/issues)

---

**Get Started**: 

```bash
# Basic features
./快速开始.sh

# SQLite database version (strongly recommended) ⭐⭐⭐
python scripts/migrate_to_sqlite.py   # First migration (only 3 seconds)
python kg_query_db.py                  # Interactive query (10-50x performance boost)

# CLI tool
python scripts/kg_cli.py search 阿司匹林 --type Drug

# FastAPI service
python -m src.api.main                 # Start API service
# Visit http://localhost:8000/docs

# pip package
pip install -e .                       # Install package
from ontology.db_loader import MedicalKnowledgeGraphDB
```

🚀 **Now supports drug-target-disease three-layer knowledge graph!**
⚡ **SQLite version: 10-50x faster queries, 80% storage reduction!**
📦 **Provides CLI, FastAPI, and pip package - three usage methods!**

*Last updated: 2025-11-18*

