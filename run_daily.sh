#!/bin/bash
# 每日运行脚本 - 一键生成投资简报 V8.2
# 使用方法：./run_daily.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "📊 Macro Investment Assistant V8.4"
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

# 检查 playwright
if ! python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "⚠️  警告：playwright 未安装"
    echo "   请运行：pip install playwright && playwright install chromium"
    echo ""
fi

# 步骤 0: 验证昨日预测（新增）
echo "🔍 步骤 0: 验证昨日预测..."
python3 scripts/verify_predictions.py 2>&1 | grep -E "(✅|⚠️|验证完成 | 预测 | 实际 | 准确率 | 误差)" || echo "⚠️  验证失败或无昨日预测"
echo ""

# 步骤 1: 获取最新金价（多数据源对比，快速）
echo "📈 步骤 1: 获取最新金价（多数据源对比）..."
python3 scripts/gold_price_auto_v83.py 2>&1 | grep -E "(✅|❌|国际金价 | 国内金价 | 数据来源 | 置信度)" || echo "⚠️  金价获取可能失败"
echo ""

# 步骤 2: 生成每日简报（使用模块化系统）
echo "📰 步骤 2: 生成每日简报..."
python3 main.py brief 2>&1 | tail -15
echo ""

# 步骤 3: 显示最新简报
echo "📄 最新简报:"
ls -t daily_brief/*.md 2>/dev/null | head -1 | xargs -I {} echo "   {}"
echo ""

echo "=========================================="
echo "✅ 每日简报生成完成!"
echo "=========================================="
echo ""
echo "💡 提示:"
echo "   - 简报已保存到 daily_brief/ 目录"
echo "   - 查看详细报告：cat daily_brief/brief_v8_*.md"
echo ""
echo "🔧 其他命令:"
echo "   - 仅获取金价：python3 scripts/gold_price_auto_v82.py"
echo "   - 完整分析：python3 main.py brief"
echo "   - 查看帮助：python3 main.py --help"
echo ""
