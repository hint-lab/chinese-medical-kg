#!/bin/bash
# 使用 uv 快速设置项目环境

echo "=========================================="
echo "   使用 uv 快速设置项目环境"
echo "=========================================="

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo ""
    echo "⚠️  uv 未安装"
    echo ""
    echo "正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 重新加载 shell 配置
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
    
    if ! command -v uv &> /dev/null; then
        echo "❌ uv 安装失败，请手动安装: https://github.com/astral-sh/uv"
        exit 1
    fi
    echo "✅ uv 安装成功"
fi

echo ""
echo "✅ uv 已安装: $(uv --version)"
echo ""

# 使用 uv 同步依赖
echo "📦 同步项目依赖..."
uv sync

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 环境设置完成！"
    echo ""
    echo "📚 使用方式:"
    echo "  # 激活虚拟环境"
    echo "  source .venv/bin/activate"
    echo ""
    echo "  # 或使用 uv run 直接运行命令"
    echo "  uv run python example_ontology_usage.py"
    echo ""
    echo "  # 运行快速开始脚本"
    echo "  ./quick_start.sh"
else
    echo "❌ 依赖同步失败"
    exit 1
fi

