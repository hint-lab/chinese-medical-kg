#!/bin/bash
# 重启API服务脚本

echo "🔄 重启API服务..."

# 查找并停止旧的API服务
pkill -f "uvicorn.*main:app" 2>/dev/null
pkill -f "python.*src.api.main" 2>/dev/null
sleep 1

# 启动新的API服务
echo "🚀 启动API服务..."
cd "$(dirname "$0")"
python -m src.api.main &
API_PID=$!

sleep 2

# 检查服务是否启动成功
if ps -p $API_PID > /dev/null; then
    echo "✅ API服务已启动 (PID: $API_PID)"
    echo "📖 API文档: http://localhost:8000/docs"
    echo "🔍 测试: curl 'http://localhost:8000/api/entities/search?name=替利珠单抗'"
else
    echo "❌ API服务启动失败"
    exit 1
fi

