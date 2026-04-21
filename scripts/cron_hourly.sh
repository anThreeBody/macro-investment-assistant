#!/bin/bash
# 国内黄金价格小时级采集定时任务
# 每小时运行一次

cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant

# 采集数据（使用v2.0稳定版）
python3 scripts/gold_collector_v2.py >> logs/gold_collector_v2.log 2>&1

# 更新实时分析
python3 scripts/intraday_analyzer.py >> logs/intraday_analyzer.log 2>&1

# 如果采集失败，记录错误
if [ $? -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 采集失败" >> logs/collector_error.log
fi
