# 预测验证 Cron 任务配置

## 任务说明
每日上午 10:30 自动验证前一天的预测准确性

## Cron 表达式
```
30 10 * * *
```

## 执行命令
```bash
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant && python3 scripts/verify_predictions.py
```

## 创建方法

使用 CoPaw cron skill:

```bash
copaw cron create \
  --agent-id 5aQmuc \
  --schedule "30 10 * * *" \
  --command "cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant && python3 scripts/verify_predictions.py" \
  --name "verify_predictions" \
  --description "每日验证昨日预测准确性"
```

## 查看任务状态
```bash
copaw cron list --agent-id 5aQmuc
```

## 手动运行测试
```bash
copaw cron run --agent-id 5aQmuc --name verify_predictions
```

## 注意事项
1. 确保 Python 环境已安装所有依赖
2. 确保数据目录可写
3. 验证失败不会中断其他任务
4. 日志输出到标准输出，可通过 cron 日志查看
