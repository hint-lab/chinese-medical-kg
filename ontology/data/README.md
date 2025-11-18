# 本体数据目录

此目录用于存储生成的本体数据文件。

## ⚠️ 重要提示

**这些数据文件不应提交到 Git 仓库**，因为：
- 文件较大（部分文件超过 100MB）
- 可以通过脚本自动生成
- 会占用大量 Git 仓库空间

## 📦 生成数据文件

运行以下命令生成所有数据文件：

```bash
# 方式 1: 使用快速开始脚本（推荐）
./quick_start.sh

# 方式 2: 手动构建
# 1. 解析 Excel 数据
python scripts/parse_official_medical_excel.py

# 2. 解析 TTD 数据
python scripts/parse_ttd_data.py

# 3. 合并数据
python scripts/merge_ontology.py

# 4. 迁移到 SQLite
python scripts/migrate_to_sqlite.py
```

## 📁 文件说明

生成的文件包括：

- `drugs.json` - 药物数据（NMPA）
- `diseases.json` - 疾病数据（ICD-10）
- `genes_ttd.json` - 基因/靶点数据（TTD）
- `drugs_ttd.json` - TTD 药物数据
- `relations_ttd.json` - TTD 关系数据
- `unified_ontology.json` - 统一本体（约 48MB）
- `entity_index.json` - 实体索引（约 153MB，不提交到 Git）
- `enhanced_relations.json` - 增强关系数据
- `medical_kg.db` - SQLite 数据库（约 41MB）

## 🔧 如果遇到 Git 推送问题

如果遇到 "file exceeds GitHub's file size limit" 错误，说明大文件仍在 Git 历史中。

### 解决方案 1: 清理 Git 历史（推荐）

```bash
# 使用 git filter-repo（需要先安装: pip install git-filter-repo）
git filter-repo --path ontology/data/ --invert-paths

# 或者使用 BFG Repo-Cleaner
# 下载: https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-folders ontology/data
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### 解决方案 2: 强制推送（谨慎使用）

```bash
# 注意：这会重写 Git 历史，需要强制推送
git push --force origin main
```

**⚠️ 警告**: 强制推送会重写远程仓库历史，如果其他人也在使用这个仓库，请先协调。

