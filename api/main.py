#!/usr/bin/env python3
"""
投资分析系统 API 服务 V1.0
提供 RESTful API 接口，支持前端页面和第三方集成
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import uvicorn
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 创建 FastAPI 应用
app = FastAPI(
    title="投资分析系统 API",
    description="提供金价、基金、股票、预测等投资相关数据的 API 接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
web_static_path = Path(__file__).parent.parent / "web" / "static"
if web_static_path.exists():
    app.mount("/static", StaticFiles(directory=str(web_static_path)), name="static")

# ==================== 数据模型 ====================

class GoldPriceResponse(BaseModel):
    international_usd_per_oz: float
    domestic_cny_per_gram: float
    change_amount: float
    change_percent: float
    source: str
    update_time: str
    status: str

class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    direction: str
    confidence: str
    signal: str
    factors: Dict[str, Any]
    generate_time: str

class AccuracyStatsResponse(BaseModel):
    total_predictions: int
    correct_predictions: int
    accuracy_rate: float
    period_days: int
    recent_accuracy: List[Dict[str, Any]]

# ==================== 辅助函数 ====================

def get_gold_price_from_cache():
    """从缓存文件获取金价"""
    cache_file = Path(__file__).parent.parent / "data" / "gold_price_cache.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_latest_brief_data():
    """获取最新简报数据"""
    brief_dir = Path(__file__).parent.parent / "daily_brief"
    if brief_dir.exists():
        brief_files = sorted(brief_dir.glob("brief_v8_*.md"), reverse=True)
        if brief_files:
            return brief_files[0]
    return None

def get_prediction_from_db():
    """从数据库获取预测"""
    db_path = Path(__file__).parent.parent / "data" / "predictions.db"
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM predictions 
            WHERE symbol='GOLD' 
            ORDER BY predict_date DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    return None

def get_accuracy_stats_from_db(days=30):
    """从数据库获取准确率统计"""
    db_path = Path(__file__).parent.parent / "data" / "predictions.db"
    if db_path.exists():
        import sqlite3
        from datetime import timedelta
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN actual_direction = predicted_direction THEN 1 ELSE 0 END) as correct
            FROM predictions
            WHERE predict_date >= ?
            AND actual_direction IS NOT NULL
        """, (cutoff_date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:
            total, correct = row
            accuracy = (correct / total * 100) if total > 0 else 0
            return {
                "total": total,
                "correct": correct,
                "accuracy_rate": accuracy
            }
    
    return {"total": 0, "correct": 0, "accuracy_rate": 0}

# ==================== API 接口 ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """首页 - 返回仪表盘页面"""
    index_path = Path(__file__).parent.parent / "web" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "message": "投资分析系统 API V1.0",
        "docs": "/docs",
        "endpoints": {
            "gold": "/api/gold/price",
            "prediction": "/api/prediction/today",
            "accuracy": "/api/accuracy/stats"
        }
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0.0"
    }

@app.get("/api/gold/price", response_model=GoldPriceResponse)
async def get_gold_price():
    """获取实时金价"""
    try:
        gold_data = get_gold_price_from_cache()
        
        if not gold_data:
            # 尝试调用金价获取脚本
            import subprocess
            script_path = Path(__file__).parent.parent / "scripts" / "gold_price_auto_v82.py"
            if script_path.exists():
                subprocess.run([sys.executable, str(script_path)], 
                             capture_output=True, timeout=30)
                gold_data = get_gold_price_from_cache()
        
        if not gold_data:
            raise HTTPException(status_code=503, detail="金价数据获取失败")
        
        return GoldPriceResponse(
            international_usd_per_oz=float(gold_data.get('international_usd_per_oz', 0)),
            domestic_cny_per_gram=float(gold_data.get('domestic_cny_per_gram', 0)),
            change_amount=float(gold_data.get('change_amount', 0)),
            change_percent=float(gold_data.get('change_percent', 0)),
            source=gold_data.get('source', '未知'),
            update_time=gold_data.get('update_time', ''),
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取金价失败：{str(e)}")

@app.get("/api/prediction/today", response_model=PredictionResponse)
async def get_today_prediction():
    """获取今日预测"""
    try:
        prediction = get_prediction_from_db()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="今日预测不存在")
        
        return PredictionResponse(
            symbol=prediction.get('symbol', 'GOLD'),
            current_price=float(prediction.get('current_price', 0)),
            predicted_price=float(prediction.get('predicted_price', 0)),
            direction=prediction.get('predicted_direction', '震荡'),
            confidence=prediction.get('confidence', '中'),
            signal=prediction.get('signal', '持有'),
            factors={},
            generate_time=prediction.get('predict_date', '')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预测失败：{str(e)}")

@app.get("/api/accuracy/stats", response_model=AccuracyStatsResponse)
async def get_accuracy_stats(period: int = Query(default=30, ge=7, le=90)):
    """获取预测准确率统计"""
    try:
        stats = get_accuracy_stats_from_db(days=period)
        
        return AccuracyStatsResponse(
            total_predictions=stats.get('total', 0),
            correct_predictions=stats.get('correct', 0),
            accuracy_rate=stats.get('accuracy_rate', 0),
            period_days=period,
            recent_accuracy=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取准确率统计失败：{str(e)}")

@app.get("/api/brief/latest")
async def get_latest_brief():
    """获取最新每日简报文件路径"""
    try:
        brief_file = get_latest_brief_data()
        
        if not brief_file:
            raise HTTPException(status_code=404, detail="未找到最新简报")
        
        return {
            "file_path": str(brief_file),
            "file_name": brief_file.name,
            "generated_time": datetime.fromtimestamp(brief_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取简报失败：{str(e)}")

@app.get("/api/system/info")
async def get_system_info():
    """获取系统信息"""
    return {
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
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ==================== 启动服务 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 投资分析系统 API 服务 V1.0")
    print("=" * 60)
    print()
    print("📍 本地访问：http://localhost:8000")
    print("📚 API 文档：http://localhost:8000/docs")
    print("🔴 ReDoc: http://localhost:8000/redoc")
    print()
    print("⚡ 按 Ctrl+C 停止服务")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
