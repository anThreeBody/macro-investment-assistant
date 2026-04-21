#!/bin/bash

# 清理测试文件和临时文件
# 版本：V8.4.0
# 用法：./scripts/cleanup.sh

set -e

echo "🧹 开始清理测试文件和临时文件..."
echo "=========================================="

# 计数器
DELETED_COUNT=0

# 删除测试脚本（tests 目录外）
echo "📋 检查测试脚本..."
for pattern in "test_*.py" "*_test.py" "debug_*.py" "check_*.py"; do
    FILES=$(find . -name "$pattern" -not -path "./tests/*" -not -path "./.git/*" 2>/dev/null || true)
    if [ -n "$FILES" ]; then
        echo "  发现文件：$pattern"
        echo "$FILES" | while read -r file; do
            if [ -n "$file" ] && [ -f "$file" ]; then
                echo "    🗑️  删除：$file"
                rm -f "$file"
                ((DELETED_COUNT++)) || true
            fi
        done
    fi
done

# 删除临时文件
echo "📋 检查临时文件..."
for pattern in "*.bak" "*.backup" "*~" "*.tmp" "*.swp" "*.swo"; do
    FILES=$(find . -name "$pattern" -not -path "./.git/*" 2>/dev/null || true)
    if [ -n "$FILES" ]; then
        COUNT=$(echo "$FILES" | wc -l)
        echo "  发现 $COUNT 个 $pattern 文件"
        echo "$FILES" | while read -r file; do
            if [ -n "$file" ] && [ -f "$file" ]; then
                rm -f "$file"
                ((DELETED_COUNT++)) || true
            fi
        done
    fi
done

# 删除 Python 缓存
echo "📋 清理 Python 缓存..."
find . -type d -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -not -path "./.git/*" -delete 2>/dev/null || true
echo "  ✅ Python 缓存已清理"

# 删除临时数据文件
echo "📋 检查临时数据文件..."
for pattern in "temp_*" "test_data.*"; do
    FILES=$(find . -name "$pattern" -not -path "./tests/*" -not -path "./.git/*" 2>/dev/null || true)
    if [ -n "$FILES" ]; then
        echo "  发现文件：$pattern"
        echo "$FILES" | while read -r file; do
            if [ -n "$file" ] && [ -f "$file" ]; then
                echo "    🗑️  删除：$file"
                rm -f "$file"
                ((DELETED_COUNT++)) || true
            fi
        done
    fi
done

# 清理日志文件（保留最近的）
echo "📋 清理旧日志文件..."
find logs -type f -name "*.log" -mtime +30 -delete 2>/dev/null || true
echo "  ✅ 30 天前的日志已清理"

# 清理简报测试文件
echo "📋 清理简报测试文件..."
find daily_brief -type f -name "*test*" -delete 2>/dev/null || true
find daily_brief -type f -name "*tmp*" -delete 2>/dev/null || true
echo "  ✅ 简报测试文件已清理"

echo "=========================================="
echo "✅ 清理完成！"
echo "   共删除 $DELETED_COUNT 个文件"
echo ""
echo "📊 清理统计:"
echo "   测试脚本：已清理"
echo "   临时文件：已清理"
echo "   Python 缓存：已清理"
echo "   临时数据：已清理"
echo "   旧日志文件：已清理"
echo "   简报测试：已清理"
echo ""
echo "💡 提示:"
echo "   - 正式测试文件保留在 tests/ 目录"
echo "   - 最近 30 天的日志已保留"
echo "   - 建议每周运行一次清理"
