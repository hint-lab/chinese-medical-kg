#!/bin/bash
# 中文医学本体 - 一键开始脚本

echo "=========================================="
echo "   中文医学本体（Ontology）快速开始"
echo "=========================================="

# 检查Python版本
echo ""
echo "1️⃣  检查环境..."
python3 --version

# 安装依赖
echo ""
echo "2️⃣  安装依赖..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

# 检查本体数据
echo ""
echo "3️⃣  检查本体数据..."
if [ -f "ontology/data/drugs.json" ] && [ -f "ontology/data/diseases.json" ]; then
    drug_count=$(python3 -c "import json; print(len(json.load(open('ontology/data/drugs.json'))))")
    disease_count=$(python3 -c "import json; print(len(json.load(open('ontology/data/diseases.json'))))")
    echo "✅ 药物数据: $drug_count 条"
    echo "✅ 疾病数据: $disease_count 条"
else
    echo "⚠️  本体数据不存在"
    echo "   请运行: python scripts/build_ontology.py"
    echo "   或者手动准备数据文件"
fi

# 运行演示
echo ""
echo "4️⃣  运行演示脚本..."
echo ""
python3 示例_ontology使用.py

echo ""
echo "=========================================="
echo "  完成！"
echo "=========================================="
echo ""
echo "📚 后续步骤："
echo "  - 查看文档: cat 快速使用指南.md"
echo "  - 运行测试: pytest tests/"
echo "  - 启动API: python -m src.api.main"
echo ""

