# API 使用文档

## 🚀 三种使用方式

### 1. CLI命令行工具

```bash
# 安装后使用
medical-kg search 阿司匹林 --type Drug

# 或直接运行
python scripts/kg_cli.py search 阿司匹林 --type Drug
```

**所有命令**:
- `search <name>` - 搜索实体（支持部分匹配）
- `fuzzy <keyword>` - 模糊搜索
- `drug-targets <drug_name>` - 查询药物的靶点
- `target-drugs <target_name>` - 查询靶点的药物
- `stats` - 显示统计信息

**选项**:
- `--type <Drug|Disease|Gene>` - 指定实体类型
- `--json` - JSON格式输出
- `--limit <n>` - 限制结果数量（模糊搜索）
- `--db <path>` - 指定数据库路径

**示例**:
```bash
# 搜索实体
python scripts/kg_cli.py search 替利珠单抗 --type Drug

# 模糊搜索
python scripts/kg_cli.py fuzzy 糖尿 --limit 5

# 查询药物的靶点
python scripts/kg_cli.py drug-targets Ibrance

# JSON格式输出
python scripts/kg_cli.py search 阿司匹林 --json
```

---

### 2. FastAPI RESTful API

#### 启动服务

```bash
# 方式1: 直接启动
python -m src.api.main

# 方式2: 使用uvicorn（推荐，支持reload）
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 方式3: 后台运行
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

# 方式4: Docker部署（推荐）🐳
# 1. 准备数据库（首次运行，仅需3秒）
python scripts/migrate_to_sqlite.py

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down

# 国内用户加速（推荐）⚡
docker-compose -f docker-compose.cn.yml up -d
```

#### 访问文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### API端点

##### 1. 搜索实体

```http
GET /api/entities/search?name={name}&type={type}
```

**参数**:
- `name` (必需): 实体名称（支持部分匹配）
- `type` (可选): 实体类型 (`Drug`, `Disease`, `Gene`)

**示例**:
```bash
curl "http://localhost:8000/api/entities/search?name=替利珠单抗&type=Drug"
```

**响应**:
```json
{
  "id": 12345,
  "name": "替利珠单抗注射液",
  "standard_name": "替利珠单抗注射液",
  "type": "Drug",
  "source": "NMPA",
  "aliases": []
}
```

**搜索优先级**:
1. 精确匹配（名称或标准名称）
2. 别名精确匹配
3. 部分匹配（名称包含关键词）
4. 别名部分匹配

##### 2. 模糊搜索

```http
GET /api/entities/fuzzy?keyword={keyword}&type={type}&limit={limit}
```

**参数**:
- `keyword` (必需): 搜索关键词
- `type` (可选): 实体类型
- `limit` (可选): 返回结果数量限制（默认10，最大100）

**示例**:
```bash
curl "http://localhost:8000/api/entities/fuzzy?keyword=糖尿&limit=5"
```

##### 3. 查询药物的靶点

```http
GET /api/drugs/{drug_name}/targets
```

**示例**:
```bash
curl "http://localhost:8000/api/drugs/Ibrance/targets"
```

**响应**:
```json
[
  {
    "source_name": "Ibrance",
    "target_name": "CDK4",
    "relation_type": "targets",
    "properties": {
      "mode_of_action": "Modulator",
      "highest_status": "Approved"
    }
  }
]
```

##### 4. 查询靶点的药物

```http
GET /api/targets/{target_name}/drugs
```

**示例**:
```bash
curl "http://localhost:8000/api/targets/CDK4/drugs"
```

##### 5. 获取统计信息

```http
GET /api/statistics
```

**示例**:
```bash
curl "http://localhost:8000/api/statistics"
```

**响应**:
```json
{
  "total_entities": 59056,
  "drugs": 19774,
  "diseases": 35849,
  "genes": 3433,
  "total_relations": 11562,
  "total_aliases": 28298,
  "data_sources": "NMPA,ICD-10,TTD",
  "version": "1.0.0"
}
```

---

### 3. Python包（pip安装）

#### 安装

```bash
# 安装基础包
pip install -e .

# 安装包含API支持
pip install -e ".[api]"

# 安装所有功能
pip install -e ".[all]"
```

#### 使用

```python
from ontology.db_loader import MedicalKnowledgeGraphDB

# 初始化数据库
db = MedicalKnowledgeGraphDB()

# 搜索实体（支持部分匹配）
result = db.search_entity("替利珠单抗", "Drug")
if result:
    print(f"找到: {result['name']}")

# 模糊搜索
results = db.fuzzy_search("糖尿", limit=10)
for r in results:
    print(f"{r['name']} ({r['type']})")

# 查询药物的靶点
targets = db.get_drug_targets("Ibrance")
for t in targets:
    print(f"靶点: {t['target_name']}")

# 查询靶点的药物
drugs = db.get_target_drugs("CDK4")
for d in drugs:
    print(f"药物: {d['drug_name']}")

# 获取统计信息
stats = db.get_statistics()
print(f"实体总数: {stats['total_entities']}")

# 关闭连接
db.close()
```

---

## 🔧 故障排除

### API服务无法启动

```bash
# 检查数据库是否存在
ls -lh ontology/data/medical_kg.db

# 如果不存在，先迁移数据
python scripts/migrate_to_sqlite.py
```

### 搜索返回404

1. **检查服务是否运行**:
   ```bash
   ps aux | grep uvicorn
   ```

2. **重启服务**:
   ```bash
   pkill -f "uvicorn.*main:app"
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **验证搜索功能**:
   ```python
   from ontology.db_loader import MedicalKnowledgeGraphDB
   db = MedicalKnowledgeGraphDB()
   result = db.search_entity('替利珠单抗')
   print(result)  # 应该能找到结果
   ```

### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 或使用其他端口
uvicorn src.api.main:app --host 0.0.0.0 --port 8001
```

### Docker部署问题

#### 容器无法启动

```bash
# 检查容器状态
docker-compose ps

# 查看详细日志
docker-compose logs api

# 检查数据库文件是否存在
ls -lh ontology/data/medical_kg.db

# 如果数据库不存在，先迁移数据
python scripts/migrate_to_sqlite.py
```

#### 容器启动后无法访问

```bash
# 检查容器是否运行
docker ps | grep chinese-medical-kg

# 检查端口映射
docker-compose ps

# 测试容器内部服务
docker-compose exec api curl http://localhost:8000/

# 重启容器
docker-compose restart
```

#### 数据库文件权限问题

```bash
# 确保数据库文件有正确的权限
chmod 644 ontology/data/medical_kg.db

# 如果使用Docker，确保挂载目录有正确权限
chmod -R 755 ontology/data/
```

---

## 📊 性能说明

- **查询速度**: <1ms（精确匹配），<10ms（模糊搜索）
- **并发支持**: FastAPI支持异步，可处理高并发请求
- **内存占用**: ~10-20MB（数据库连接）

---

## 🔗 相关文档

- [README.md](../README.md) - 项目主文档
- [data_sources_recommendation.md](../data_sources_recommendation.md) - 数据源说明
- [ontology/README.md](../ontology/README.md) - 技术细节
