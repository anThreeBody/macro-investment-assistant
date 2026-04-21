#!/bin/bash
# 每日运行脚本 V8.0 - 重构版
# 使用方法：./run_daily_v8.sh

set -e

echo "=========================================="
echo "📊 Macro Investment Assistant V8.0"
echo "=========================================="
echo ""

# 切换到工作目录
cd "$(dirname "$0")"

echo "⏰ 当前时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：Python3 未安装"
    exit 1
fi

echo "✅ Python3 检查通过"
echo ""

# 运行每日简报
echo "📰 生成每日简报..."
python3 main.py brief

echo ""
echo "✅ 每日简报生成完成"
echo ""

# 显示生成的文件
echo "📁 生成的文件:"
ls -lt daily_brief/*.md 2>/dev/null | head -5 || echo "  暂无简报文件"

echo ""
echo "=========================================="
echo "✨ 运行完成"
echo "=========================================="
