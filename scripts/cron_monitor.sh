#!/bin/bash
# 黄金智能监控系统 - 每小时运行
# 整合：数据采集 + 实时分析 + 买卖点告警

cd /Users/chenmengke/Code/macro-investment-assistant

LOG_FILE="logs/cron_$(date '+%Y%m%d').log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== 开始执行 ==========" >> $LOG_FILE

# 1. 采集最新价格
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 1. 采集价格数据..." >> $LOG_FILE
python3 scripts/gold_collector_v2.py >> $LOG_FILE 2>&1
COLLECTOR_STATUS=$?

# 2. 运行买卖点智能告警系统
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 2. 运行买卖点告警..." >> $LOG_FILE
python3 scripts/alert_system.py >> $LOG_FILE 2>&1

# 3. 更新日内统计
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 3. 更新日内统计..." >> $LOG_FILE
python3 scripts/intraday_analyzer.py >> $LOG_FILE 2>&1

# 4. 检查是否需要发送每日计划（仅在9:00执行）
HOUR=$(date '+%H')
if [ "$HOUR" = "09" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 4. 发送今日买卖计划..." >> $LOG_FILE
    python3 -c "
import sys
sys.path.insert(0, 'scripts')
from alert_system import generate_daily_plan, send_feishu_message
plan = generate_daily_plan()
print(plan)
# send_feishu_message(plan, '📅 今日黄金买卖计划')
" >> $LOG_FILE 2>&1
fi

# 5. 如果采集失败，记录错误
if [ $COLLECTOR_STATUS -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 采集失败，请检查数据源" >> $LOG_FILE
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== 执行完成 ==========" >> $LOG_FILE
echo "" >> $LOG_FILE
