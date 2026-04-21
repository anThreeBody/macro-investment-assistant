#!/bin/bash

# 归档过期文档脚本
# 版本：V8.4.0
# 用法：./scripts/archive_docs.sh [文档名...]

set -e

ARCHIVE_DIR="docs/archive/$(date +%Y-%m)"

echo "📦 文档归档工具"
echo "=========================================="

# 如果没有参数，显示使用情况
if [ $# -eq 0 ]; then
    echo "用法：$0 [文档名...]"
    echo ""
    echo "示例:"
    echo "  $0 docs/GOLD_PRICE_FIX.md"
    echo "  $0 docs/GOLD_PRICE_FINAL.md docs/OLD_VERSION.md"
    echo ""
    echo "建议归档的文档:"
    echo "  - 被新版本替代的文档"
    echo "  - 功能已废弃的文档"
    echo "  - 信息已过时的文档"
    exit 0
fi

# 创建归档目录
mkdir -p "$ARCHIVE_DIR"
echo "📁 归档目录：$ARCHIVE_DIR"
echo ""

# 归档计数器
ARCHIVED_COUNT=0

# 处理每个文档
for doc in "$@"; do
    if [ ! -f "$doc" ]; then
        echo "❌ 文件不存在：$doc"
        continue
    fi
    
    # 获取文件名
    FILENAME=$(basename "$doc")
    
    # 检查是否已在归档目录
    if [[ "$doc" == *"/archive/"* ]]; then
        echo "⚠️  已在归档目录：$doc"
        continue
    fi
    
    echo "📄 归档：$doc"
    
    # 移动文件
    mv "$doc" "$ARCHIVE_DIR/$FILENAME"
    echo "   ✅ 已移动到：$ARCHIVE_DIR/$FILENAME"
    
    ((ARCHIVED_COUNT++))
done

echo ""
echo "=========================================="
echo "✅ 归档完成！"
echo "   共归档 $ARCHIVED_COUNT 个文档"
echo "   归档目录：$ARCHIVE_DIR"
echo ""

# 创建或更新归档索引
INDEX_FILE="$ARCHIVE_DIR/README.md"
if [ ! -f "$INDEX_FILE" ]; then
    echo "📝 创建归档索引..."
    cat > "$INDEX_FILE" << EOF
# 归档文档索引

**归档日期**: $(date +%Y-%m)  
**文档数量**: $ARCHIVED_COUNT

---

## 归档文档列表

| 文档 | 归档日期 | 归档原因 |
|------|----------|----------|
EOF
fi

# 更新索引
for doc in "$@"; do
    FILENAME=$(basename "$doc")
    if [ -f "$ARCHIVE_DIR/$FILENAME" ]; then
        # 检查是否已在索引中
        if ! grep -q "$FILENAME" "$INDEX_FILE"; then
            echo "| $FILENAME | $(date +%Y-%m-%d) | 过期文档 |" >> "$INDEX_FILE"
        fi
    fi
done

echo "📋 归档索引已更新：$INDEX_FILE"
echo ""
echo "💡 提示:"
echo "  - 查看归档文档：ls $ARCHIVE_DIR"
echo "  - 查看归档索引：cat $INDEX_FILE"
echo "  - 恢复文档：mv $ARCHIVE_DIR/FILENAME docs/"
