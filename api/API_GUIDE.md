# API 服务使用指南

**版本**: V1.0.0  
**创建日期**: 2026-04-03  
**状态**: ✅ 已部署

---

## 🚀 快速启动

### 方式 1: 使用启动脚本（推荐）

```bash
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant
./api/start.sh
```

### 方式 2: 直接运行

```bash
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant
python3 api/main.py
```

### 方式 3: 使用 uvicorn

```bash
cd ~//workspaces/YOUR_WORKSPACEH/skills/Macro-Investment-Assistant
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📍 访问地址

| 用途 | 地址 |
|------|------|
| **前端仪表盘** | http://localhost:8000 |
| **API 文档** | http://localhost:8000/docs |
| **ReDoc 文档** | http://localhost:8000/redoc |
| **健康检查** | http://localhost:8000/api/health |

---

## 📋 API 端点

### 基础信息

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 前端仪表盘页面 |
| `/api/health` | GET | 健康检查 |
| `/api/system/info` | GET | 系统信息 |

### 金价数据

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/gold/price` | GET | 获取实时金价 |
| `/api/gold/history` | GET | 获取金价历史（待实现） |

### 预测数据

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/prediction/today` | GET | 获取今日预测 |
| `/api/prediction/history` | GET | 获取预测历史（待实现） |
| `/api/accuracy/stats` | GET | 获取准确率统计 |

### 简报数据

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/brief/latest` | GET | 获取最新简报 |
| `/api/brief/list` | GET | 获取简报列表（待实现） |

---

## 💡 使用示例

### 1. 获取实时金价

```bash
curl http://localhost:8000/api/gold/price
```

**响应**:
```json
{
  "international_usd_per_oz": 4989.50,
  "domestic_cny_per_gram": 1163.02,
  "change_amount": -110.40,
  "change_percent": -2.29,
  "source": "东方财富-COMEX 黄金期货",
  "update_time": "2026-04-03 13:51:25",
  "status": "success"
}
```

### 2. 获取今日预测

```bash
curl http://localhost:8000/api/prediction/today
```

**响应**:
```json
{
  "symbol": "GOLD",
  "current_price": 1162.97,
  "predicted_price": 1165.30,
  "direction": "震荡",
  "confidence": "高",
  "signal": "持有",
  "factors": {},
  "generate_time": "2026-04-03"
}
```

### 3. 获取预测准确率

```bash
curl "http://localhost:8000/api/accuracy/stats?period=30"
```

**响应**:
```json
{
  "total_predictions": 30,
  "correct_predictions": 18,
  "accuracy_rate": 60.0,
  "period_days": 30,
  "recent_accuracy": []
}
```

### 4. 获取系统信息

```bash
curl http://localhost:8000/api/system/info
```

**响应**:
```json
{
  "version": "V8.2.0",
  "api_version": "1.0.0",
  "status": "running",
  "data_sources": {
    "gold": "东方财富-COMEX 黄金期货",
    "fund": "AKShare",
    "stock": "AKShare",
    "news": "多源聚合"
  },
  "features": [
    "实时金价获取",
    "多因子预测",
    "预测验证",
    "基金推荐",
    "市场概览",
    "新闻聚合"
  ],
  "timestamp": "2026-04-03 14:30:00"
}
```

---

## 🌐 前端仪表盘

访问 http://localhost:8000 可查看可视化仪表盘，包含：

- 💰 **实时金价** - 国际/国内价格、涨跌幅
- 🔮 **今日预测** - 预测方向、置信度、交易信号
- 📈 **预测准确率** - 历史准确率统计
- 📊 **金价走势图** - 30 天价格趋势（ECharts）
- 📰 **最新新闻** - 财经新闻列表

**特性**:
- ✅ 自动刷新（60 秒）
- ✅ 响应式设计
- ✅ 实时图表
- ✅ 移动端适配

---

## 🔧 开发调试

### 启用热重载

```bash
uvicorn api.main:app --reload --port 8000
```

### 查看日志

API 服务会在控制台输出日志：

```
INFO:     127.0.0.1:50000 - "GET /api/gold/price HTTP/1.1" 200 OK
INFO:     127.0.0.1:50001 - "GET /api/prediction/today HTTP/1.1" 200 OK
```

### 测试 API

使用 Swagger UI (http://localhost:8000/docs) 可以直接测试所有 API 端点。

---

## 📦 依赖安装

```bash
pip install fastapi uvicorn[standard] pydantic python-multipart
```

或使用 requirements.txt:

```bash
pip install -r api/requirements.txt
```

---

## 🚨 故障排查

### 问题 1: 端口被占用

**错误**:
```
OSError: [Errno 48] Address already in use
```

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
python3 api/main.py --port 8001
```

### 问题 2: 依赖未安装

**错误**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决**:
```bash
pip install fastapi uvicorn[standard]
```

### 问题 3: 金价数据为空

**原因**: 缓存文件不存在

**解决**:
```bash
# 先运行金价获取脚本
python3 scripts/gold_price_auto_v82.py

# 再启动 API 服务
python3 api/main.py
```

---

## 🔐 安全建议

### 生产环境部署

1. **添加认证**: 使用 API Key 或 JWT
2. **启用 HTTPS**: 使用 Nginx 反向代理
3. **限制 CORS**: 指定允许的域名
4. **添加限流**: 防止 API 滥用
5. **日志记录**: 记录所有请求

### 示例：添加 API Key 认证

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@app.get("/api/gold/price")
async def get_gold_price(api_key: str = Depends(get_api_key)):
    ...
```

---

## 📊 性能优化

### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_gold_price_cached():
    return get_gold_price_from_cache()
```

### 异步支持

```python
@app.get("/api/gold/price")
async def get_gold_price():
    # 使用异步 IO
    gold_data = await fetch_gold_price_async()
    return gold_data
```

---

## 📝 待实现功能

- [ ] 基金推荐 API
- [ ] 市场概览 API
- [ ] 新闻列表 API
- [ ] 金价历史图表数据
- [ ] 预测历史查询
- [ ] 用户系统
- [ ] 通知推送

---

## 📞 技术支持

### 查看文档

- API 文档：http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 查看日志

```bash
# API 服务日志
tail -f logs/api.log

# 系统日志
tail -f logs/system.log
```

### 问题反馈

如遇问题，请检查：
1. 依赖是否安装
2. 端口是否占用
3. 数据文件是否存在
4. 日志是否有错误

---

*文档位置：api/API_GUIDE.md*  
*最后更新：2026-04-03*  
*版本：V1.0.0*
