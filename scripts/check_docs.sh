#!/bin/bash

# 文档质量检查脚本
# 版本：V8.4.0
# 用法：./scripts/check_docs.sh

set -e

echo "🔍 开始检查文档质量..."
echo "=========================================="

ERRORS=0
WARNINGS=0

# 检查 1: README.md 版本号
echo "📋 检查 1: README.md 版本号..."
README_VERSION=$(grep -m 1 "\*\*版本\*\*" README.md | grep -o "V[0-9.]*" || echo "未知")
echo "   README.md 版本：$README_VERSION"

if [ "$README_VERSION" = "未知" ]; then
    echo "   ❌ 错误：README.md 版本号格式不正确"
    ((ERRORS++))
else
    echo "   ✅ 版本号格式正确"
fi

# 检查 2: 测试文件遗留
echo ""
echo "📋 检查 2: 测试文件遗留..."
TEST_FILES=$(find . -name "test_*.py" -not -path "./tests/*" -not -path "./.git/*" -not -path "./skills/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$TEST_FILES" -gt 0 ]; then
    echo "   ❌ 错误：发现 $TEST_FILES 个测试文件未清理"
    find . -name "test_*.py" -not -path "./tests/*" -not -path "./.git/*" -not -path "./skills/*" 2>/dev/null
    ((ERRORS++))
else
    echo "   ✅ 无测试文件遗留"
fi

# 检查 3: 临时文件
echo ""
echo "📋 检查 3: 临时文件..."
TEMP_FILES=$(find . \( -name "*.bak" -o -name "*.backup" -o -name "*~" -o -name "*.tmp" \) -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$TEMP_FILES" -gt 0 ]; then
    echo "   ❌ 错误：发现 $TEMP_FILES 个临时文件未清理"
    ((ERRORS++))
else
    echo "   ✅ 无临时文件"
fi

# 检查 4: Python 缓存
echo ""
echo "📋 检查 4: Python 缓存..."
PYC_FILES=$(find . -name "*.pyc" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
PYCACHE_DIRS=$(find . -type d -name "__pycache__" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYC_FILES" -gt 0 ] || [ "$PYCACHE_DIRS" -gt 0 ]; then
    echo "   ⚠️  警告：发现 $PYC_FILES 个.pyc 文件和 $PYCACHE_DIRS 个__pycache__目录"
    ((WARNINGS++))
else
    echo "   ✅ Python 缓存已清理"
fi

# 检查 5: 文档过期（超过 90 天未更新）
echo ""
echo "📋 检查 5: 文档过期..."
OLD_DOCS=$(find docs -name "*.md" -mtime +90 -not -path "*/archive/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$OLD_DOCS" -gt 0 ]; then
    echo "   ⚠️  警告：发现 $OLD_DOCS 个文档超过 90 天未更新"
    find docs -name "*.md" -mtime +90 -not -path "*/archive/*" 2>/dev/null | head -5
    ((WARNINGS++))
else
    echo "   ✅ 无过期文档"
fi

# 检查 6: 文档链接检查
echo ""
echo "📋 检查 6: 文档链接..."
BROKEN_LINKS=0
for doc in docs/*.md README.md; do
    if [ -f "$doc" ]; then
        # 检查 Markdown 链接
        LINKS=$(grep -o "\[.*\](docs/[^)]*)" "$doc" 2>/dev/null || true)
        if [ -n "$LINKS" ]; then
            echo "$LINKS" | while read -r link; do
                FILE=$(echo "$link" | grep -o "docs/[^)]*")
                if [ -n "$FILE" ] && [ ! -f "$FILE" ]; then
                    echo "   ⚠️  警告：$doc 中的链接 $FILE 不存在"
                    ((BROKEN_LINKS++)) || true
                fi
            done
        fi
    fi
done

if [ "$BROKEN_LINKS" -gt 0 ]; then
    echo "   ⚠️  警告：发现 $BROKEN_LINKS 个无效链接"
    ((WARNINGS++))
else
    echo "   ✅ 文档链接正常"
fi

# 检查 7: 关键文档是否存在
echo ""
echo "📋 检查 7: 关键文档..."
CRITICAL_DOCS=("README.md" "docs/VERSION_HISTORY.md" "docs/QUICK_REFERENCE.md")
for doc in "${CRITICAL_DOCS[@]}"; do
    if [ ! -f "$doc" ]; then
        echo "   ❌ 错误：关键文档 $doc 不存在"
        ((ERRORS++))
    fi
done
echo "   ✅ 关键文档完整"

# 检查 8: 版本号一致性
echo ""
echo "📋 检查 8: 版本号一致性..."
README_VER=$(grep -m 1 "V[0-9.]*" README.md | grep -o "V[0-9.]*" | head -1 || echo "")
HISTORY_VER=$(grep -m 1 "V[0-9.]*" docs/VERSION_HISTORY.md | grep -o "V[0-9.]*" | head -1 || echo "")

if [ -n "$README_VER" ] && [ -n "$HISTORY_VER" ]; then
    if [ "$README_VER" = "$HISTORY_VER" ]; then
        echo "   ✅ 版本号一致：$README_VER"
    else
        echo "   ⚠️  警告：README.md($README_VER) 与 VERSION_HISTORY.md($HISTORY_VER) 版本不一致"
        ((WARNINGS++))
    fi
else
    echo "   ⚠️  警告：无法提取版本号"
    ((WARNINGS++))
fi

# 总结
echo ""
echo "=========================================="
echo "📊 检查结果:"
echo "   错误：$ERRORS"
echo "   警告：$WARNINGS"
echo ""

if [ "$ERRORS" -gt 0 ]; then
    echo "❌ 检查失败！发现 $ERRORS 个错误"
    echo ""
    echo "请立即修复以下问题:"
    echo "  1. 清理测试文件和临时文件"
    echo "  2. 确保关键文档存在"
    echo "  3. 运行 ./scripts/cleanup.sh 清理"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo "⚠️  检查通过，但有 $WARNINGS 个警告"
    echo ""
    echo "建议处理以下问题:"
    echo "  - 清理 Python 缓存"
    echo "  - 更新过期文档"
    echo "  - 修复无效链接"
    exit 0
else
    echo "✅ 检查通过！文档质量良好"
    exit 0
fi
