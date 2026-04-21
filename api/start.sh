#!/bin/bash
# API 服务启动脚本
# 使用方法：./api/start.sh

set -e

echo "=========================================="
echo "🚀 投资分析系统 API 服务 V1.0"
echo "=========================================="
echo ""

# 切换到工作目录
cd "$(dirname "$0")/.."

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI 未安装，正在安装..."
    pip3 install -q fastapi uvicorn[standard] pydantic python-multipart
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi
echo ""

# 启动服务
echo "🌐 启动 API 服务..."
echo ""
echo "📍 访问地址："
echo "   首页：http://localhost:8000"
echo "   API 文档：http://localhost:8000/docs"
echo "   ReDoc: http://localhost:8000/redoc"
echo ""
echo "⚡ 按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

python3 api/main.py
