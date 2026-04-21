#!/usr/bin/env python3
"""
基金推荐系统
基于趋势、评分、风险的多维度推荐
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

# 基金数据库路径
FUND_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'fund_data.db')

def init_fund_database():
    """初始化基金数据库"""
    conn = sqlite3.connect(FUND_DB_PATH)
    cursor = conn.cursor()
    
    # 基金基础信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_info (
            fund_code TEXT PRIMARY KEY,
            fund_name TEXT NOT NULL,
            fund_type TEXT,  -- index/active
            category TEXT,  -- 股票型/债券型/混合型/指数型
            manager TEXT,
            company TEXT,
            establish_date TEXT,
            benchmark TEXT,
            risk_level TEXT,  -- low/medium/high
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 基金净值表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_nav (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_code TEXT NOT NULL,
            date TEXT NOT NULL,
            nav REAL,
            accum_nav REAL,
            daily_return REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fund_code, date)
        )
    ''')
    
    # 基金评分表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_scores (
            fund_code TEXT PRIMARY KEY,
            trend_score REAL,  -- 趋势评分 0-100
            risk_score REAL,   -- 风险评分 0-100
            sharpe_score REAL, -- 夏普比率评分 0-100
            alpha_score REAL,  -- 阿尔法评分 0-100
            total_score REAL,  -- 综合评分 0-100
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 推荐记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            fund_name TEXT,
            recommendation_type TEXT,  -- buy/hold/sell
            reason TEXT,
            expected_return REAL,
            risk_level TEXT,
            confidence REAL,  -- 置信度 0-100
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 基金数据库初始化完成: {FUND_DB_PATH}")

def get_sample_funds():
    """获取示例基金数据（实际应从API获取）"""
    # 这里使用一些常见的基金作为示例
    sample_funds = [
        # 指数基金
        {'code': '510300', 'name': '华泰柏瑞沪深300ETF', 'type': 'index', 'category': '指数型', 'risk': 'medium'},
        {'code': '510500', 'name': '南方中证500ETF', 'type': 'index', 'category': '指数型', 'risk': 'medium'},
        {'code': '159915', 'name': '易方达创业板ETF', 'type': 'index', 'category': '指数型', 'risk': 'high'},
        {'code': '512000', 'name': '华宝中证银行ETF', 'type': 'index', 'category': '指数型', 'risk': 'medium'},
        {'code': '512010', 'name': '华宝中证医疗ETF', 'type': 'index', 'category': '指数型', 'risk': 'high'},
        {'code': '515700', 'name': '华夏中证新能源ETF', 'type': 'index', 'category': '指数型', 'risk': 'high'},
        {'code': '512170', 'name': '华宝中证科技龙头ETF', 'type': 'index', 'category': '指数型', 'risk': 'high'},
        {'code': '512200', 'name': '华宝中证军工ETF', 'type': 'index', 'category': '指数型', 'risk': 'high'},
        
        # 主动基金
        {'code': '000001', 'name': '华夏成长混合', 'type': 'active', 'category': '混合型', 'risk': 'high'},
        {'code': '000003', 'name': '中海可转债债券', 'type': 'active', 'category': '债券型', 'risk': 'low'},
        {'code': '000011', 'name': '华夏大盘精选混合', 'type': 'active', 'category': '混合型', 'risk': 'high'},
        {'code': '000025', 'name': '博时信用债券', 'type': 'active', 'category': '债券型', 'risk': 'low'},
        {'code': '000041', 'name': '华夏全球股票', 'type': 'active', 'category': 'QDII', 'risk': 'high'},
        {'code': '000051', 'name': '鹏华价值优势混合', 'type': 'active', 'category': '混合型', 'risk': 'medium'},
        {'code': '000061', 'name': '华夏盛世精选混合', 'type': 'active', 'category': '混合型', 'risk': 'high'},
        {'code': '000083', 'name': '汇添富消费行业混合', 'type': 'active', 'category': '混合型', 'risk': 'high'},
        {'code': '000127', 'name': '农银汇理行业领先混合', 'type': 'active', 'category': '混合型', 'risk': 'high'},
        {'code': '000171', 'name': '易方达裕丰回报债券', 'type': 'active', 'category': '债券型', 'risk': 'low'},
    ]
    return sample_funds

def calculate_fund_scores(fund_code, fund_type):
    """计算基金评分（模拟算法，实际应基于真实数据）"""
    import random
    
    # 模拟评分（实际应从历史净值计算）
    # 趋势评分：基于近期收益率
    trend_score = random.uniform(60, 95)
    
    # 风险评分：基于波动率（越高越好，表示风险控制好）
    risk_score = random.uniform(50, 90)
    
    # 夏普评分：风险调整后收益
    sharpe_score = random.uniform(55, 92)
    
    # 阿尔法评分：超额收益能力
    alpha_score = random.uniform(50, 88)
    
    # 综合评分
    if fund_type == 'index':
        # 指数基金更看重趋势
        total_score = trend_score * 0.4 + risk_score * 0.3 + sharpe_score * 0.2 + alpha_score * 0.1
    else:
        # 主动基金更看重阿尔法
        total_score = trend_score * 0.3 + risk_score * 0.2 + sharpe_score * 0.2 + alpha_score * 0.3
    
    return {
        'trend_score': round(trend_score, 2),
        'risk_score': round(risk_score, 2),
        'sharpe_score': round(sharpe_score, 2),
        'alpha_score': round(alpha_score, 2),
        'total_score': round(total_score, 2)
    }

def generate_recommendation(fund, scores):
    """生成推荐理由"""
    reasons = []
    
    # 基于评分生成原因
    if scores['trend_score'] > 80:
        reasons.append(f"趋势强劲（{scores['trend_score']:.0f}分）")
    elif scores['trend_score'] > 70:
        reasons.append(f"趋势向好（{scores['trend_score']:.0f}分）")
    
    if scores['risk_score'] > 80:
        reasons.append(f"风险控制优秀（{scores['risk_score']:.0f}分）")
    elif scores['risk_score'] > 70:
        reasons.append(f"风险可控（{scores['risk_score']:.0f}分）")
    
    if scores['alpha_score'] > 80:
        reasons.append(f"超额收益能力强（{scores['alpha_score']:.0f}分）")
    elif scores['alpha_score'] > 70:
        reasons.append(f"具备超额收益（{scores['alpha_score']:.0f}分）")
    
    if scores['sharpe_score'] > 80:
        reasons.append(f"风险调整后收益佳（{scores['sharpe_score']:.0f}分）")
    
    # 基金类型特定原因
    if fund['type'] == 'index':
        reasons.append(f"跟踪{fund['category']}，分散风险")
    else:
        reasons.append(f"主动管理，精选{fund['category']}标的")
    
    return "；".join(reasons)

def recommend_funds(risk_preference='medium', top_n=5):
    """
    推荐基金
    
    Args:
        risk_preference: low/medium/high
        top_n: 推荐数量
    """
    funds = get_sample_funds()
    
    # 筛选符合风险偏好的基金
    risk_map = {'low': ['low'], 'medium': ['low', 'medium'], 'high': ['low', 'medium', 'high']}
    filtered_funds = [f for f in funds if f['risk'] in risk_map.get(risk_preference, ['medium'])]
    
    # 计算评分并排序
    scored_funds = []
    for fund in filtered_funds:
        scores = calculate_fund_scores(fund['code'], fund['type'])
        recommendation = generate_recommendation(fund, scores)
        
        # 预期收益率（模拟）
        expected_return = scores['total_score'] / 100 * 0.15  # 假设最高15%年化
        
        scored_funds.append({
            **fund,
            **scores,
            'recommendation': recommendation,
            'expected_return': round(expected_return * 100, 2),  # 百分比
            'confidence': round(scores['total_score'], 0)
        })
    
    # 按综合评分排序
    scored_funds.sort(key=lambda x: x['total_score'], reverse=True)
    
    return scored_funds[:top_n]

def generate_fund_report(risk_preference='medium'):
    """生成基金推荐报告"""
    recommendations = recommend_funds(risk_preference)
    
    report = f"""
{'='*70}
📊 基金推荐报告
{'='*70}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
风险偏好: {'保守' if risk_preference == 'low' else '稳健' if risk_preference == 'medium' else '进取'}

{'='*70}
⭐ 推荐基金（Top {len(recommendations)}）
{'='*70}

"""
    
    for i, fund in enumerate(recommendations, 1):
        report += f"""
【Top {i}】{fund['name']} ({fund['code']})
{'-'*70}
类型: {'指数基金' if fund['type'] == 'index' else '主动基金'} | {fund['category']}
风险等级: {'低' if fund['risk'] == 'low' else '中' if fund['risk'] == 'medium' else '高'}
综合评分: {fund['total_score']:.0f}/100
预期年化收益: {fund['expected_return']:.1f}%
置信度: {fund['confidence']:.0f}%

评分详情:
  - 趋势评分: {fund['trend_score']:.0f}
  - 风险评分: {fund['risk_score']:.0f}
  - 夏普评分: {fund['sharpe_score']:.0f}
  - 阿尔法评分: {fund['alpha_score']:.0f}

推荐理由:
{fund['recommendation']}

"""
    
    report += f"""
{'='*70}
📈 配置建议
{'='*70}
基于当前市场环境，建议配置:

1. 核心仓位（60%）: 沪深300/中证500等宽基指数基金
   - 分散风险，获取市场平均收益

2. 卫星仓位（30%）: 行业主题基金
   - 新能源、医疗、科技等高成长板块
   - 把握结构性机会

3. 防守仓位（10%）: 债券型基金
   - 降低组合波动，提供稳定现金流

{'='*70}
⚠️ 风险提示
{'='*70}
1. 以上推荐基于模拟算法，实际应从真实数据计算
2. 基金投资有风险，过往业绩不代表未来表现
3. 建议分散投资，不要把所有资金投入单一基金
4. 定期审视持仓，根据市场变化调整配置
5. 长期投资，避免频繁申赎

{'='*70}
🔧 待完善功能
{'='*70}
- [ ] 接入真实基金净值数据（AKShare/天天基金）
- [ ] 基于真实历史数据计算评分
- [ ] 添加基金经理业绩分析
- [ ] 添加行业轮动判断
- [ ] 添加市场估值分析
{'='*70}
"""
    
    return report

def save_recommendations(recommendations):
    """保存推荐记录"""
    conn = sqlite3.connect(FUND_DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    for fund in recommendations:
        cursor.execute('''
            INSERT INTO fund_recommendations
            (date, fund_code, fund_name, recommendation_type, reason, expected_return, risk_level, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            now.date(),
            fund['code'],
            fund['name'],
            'buy',
            fund['recommendation'],
            fund['expected_return'],
            fund['risk'],
            fund['confidence']
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ 推荐记录已保存: {len(recommendations)} 只基金")

if __name__ == '__main__':
    init_fund_database()
    report = generate_fund_report('medium')
    print(report)
    
    # 保存推荐
    recommendations = recommend_funds('medium', 5)
    save_recommendations(recommendations)
