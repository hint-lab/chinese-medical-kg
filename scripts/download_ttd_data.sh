#!/bin/bash
# TTD 数据下载脚本（使用正确的URL）

echo "========================================"
echo "  下载 TTD 核心数据"
echo "========================================"

# 创建数据目录
mkdir -p data/ttd
cd data/ttd

echo ""
echo "数据保存位置: $(pwd)"
echo ""

# 正确的下载URL基础路径
BASE_URL="https://ttd.idrblab.cn/files/download"

# 下载核心6个文件
echo "[1/6] 下载靶点信息..."
wget -q --show-progress "${BASE_URL}/P1-01-TTD_target_download.txt" || echo "❌ 下载失败"

echo "[2/6] 下载药物信息..."
wget -q --show-progress "${BASE_URL}/P1-02-TTD_drug_download.txt" || echo "❌ 下载失败"

echo "[3/6] 下载药物同义词（重要！）..."
wget -q --show-progress "${BASE_URL}/P1-04-Drug_synonyms.txt" || echo "❌ 下载失败"

echo "[4/6] 下载药物-疾病映射..."
wget -q --show-progress "${BASE_URL}/P1-05-Drug_disease.txt" || echo "❌ 下载失败"

echo "[5/6] 下载药物-靶点映射（Excel格式）..."
wget -q --show-progress "${BASE_URL}/P1-07-Drug-TargetMapping.xlsx" || echo "❌ 下载失败"

echo "[6/6] 下载靶点-疾病映射..."
wget -q --show-progress "${BASE_URL}/P1-06-Target_disease.txt" || echo "❌ 下载失败"

echo ""
echo "========================================"
echo "  下载完成"
echo "========================================"
echo ""

# 显示下载的文件
ls -lh P1-*.txt P1-*.xlsx 2>/dev/null

echo ""
echo "文件总数: $(ls -1 P1-*.txt P1-*.xlsx 2>/dev/null | wc -l)"
echo ""
echo "下一步:"
echo "  cd ../.."
echo "  python scripts/verify_ttd_data.py  # 验证文件"
echo "  python scripts/parse_ttd_data.py   # 解析数据"
