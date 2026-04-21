#!/usr/bin/env python3
"""
统一看板服务
整合数据资产看板、准确率看板、进化日志
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboards.data_asset_dashboard import DataAssetDashboard
from dashboards.accuracy_dashboard import AccuracyDashboard
from dashboards.evolution_log import EvolutionLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardService:
    """统一看板服务"""
    
    def __init__(self):
        self.data_dashboard = DataAssetDashboard()
        self.accuracy_dashboard = AccuracyDashboard()
        self.evolution_log = EvolutionLog()
        
        self.dashboard_dir = Path(__file__).parent.parent / "dashboards"
        
        logger.info("[看板服务] 初始化完成")
    
    def generate_all_dashboards(self):
        """生成所有看板"""
        print("🎯 生成所有看板...\n")
        
        # 1. 数据资产看板
        print("1️⃣ 生成数据资产看板...")
        data_file = self.data_dashboard.save_dashboard()
        print(f"   ✅ 已保存: {data_file}\n")
        
        # 2. 准确率看板
        print("2️⃣ 生成准确率看板...")
        accuracy_file = self.accuracy_dashboard.save_dashboard()
        print(f"   ✅ 已保存: {accuracy_file}\n")
        
        # 3. 进化日志
        print("3️⃣ 生成进化日志...")
        evolution_file = self.evolution_log.save_changelog()
        print(f"   ✅ 已保存: {evolution_file}\n")
        
        return {
            "data_assets": data_file,
            "accuracy": accuracy_file,
            "evolution": evolution_file
        }
    
    def display_summary(self):
        """显示看板摘要"""
        print("="*70)
        print("📊 系统透明化看板摘要")
        print("="*70)
        
        # 数据资产
        print("\n📁 数据资产:")
        total = self.data_dashboard.calculate_total_stats()
        print(f"  总记录数: {total['total_records']:,}")
        print(f"  每日新增: {total['daily_new']:,}")
        print(f"  平均质量: {total['avg_quality']:.1%}")
        
        # 准确率
        print("\n🎯 预测准确率:")
        overall = self.accuracy_dashboard.calculate_overall_accuracy(days=30)
        print(f"  总体准确率: {overall['overall_accuracy']:.1%}")
        print(f"  总预测数: {overall['total_predictions']}")
        
        # 进化日志
        print("\n🔄 系统进化:")
        records = self.evolution_log.load_records()
        completed = sum(1 for r in records if r.get("status") == "completed")
        print(f"  总变更数: {len(records)}")
        print(f"  已完成: {completed} ✅")
        
        print("\n" + "="*70)
    
    def generate_master_dashboard(self):
        """生成主看板"""
        # 获取各看板数据
        data_assets = self.data_dashboard.get_all_data_assets()
        data_total = self.data_dashboard.calculate_total_stats()
        accuracy_overall = self.accuracy_dashboard.calculate_overall_accuracy(days=30)
        evolution_records = self.evolution_log.get_latest_records(3)
        
        master = f"""# 📊 系统主看板

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📁 数据资产概览

| 指标 | 数值 |
|------|------|
| 总记录数 | {data_total['total_records']:,} |
| 每日新增 | {data_total['daily_new']:,} |
| 数据类别 | {data_total['categories']} 类 |
| 平均质量 | {data_total['avg_quality']:.1%} |

### 各品类数据

| 品类 | 记录数 | 质量 |
|------|--------|------|
"""
        
        for asset in data_assets:
            master += f"| {asset['category']} | {asset['total_records']:,} | {asset['data_quality']:.0%} |\n"
        
        master += f"""
---

## 🎯 预测准确率概览

| 指标 | 数值 |
|------|------|
| 总体准确率 | {accuracy_overall['overall_accuracy']:.1%} |
| 总预测数 | {accuracy_overall['total_predictions']:,} |
| 正确数 | {accuracy_overall['total_correct']:,} |
| 平均误差 | {accuracy_overall['avg_error']:.2f}% |

---

## 🔄 最近变更

"""
        
        for record in evolution_records:
            status = "✅" if record.get("status") == "completed" else "🔄"
            master += f"- {status} **{record['date']}** - {record['title']} ({record['phase']})\n"
        
        master += f"""
---

## 📊 详细看板

- [📁 数据资产看板](./data_assets_{datetime.now().strftime('%Y%m%d')}.md)
- [🎯 准确率看板](./accuracy_{datetime.now().strftime('%Y%m%d')}.md)
- [🔄 进化日志](../docs/EVOLUTION_LOG.md)

---

## 💡 快速链接

### 数据层
- 黄金价格数据: `data/gold_*.json`
- 基金数据: `data/fund_data.db`
- 预测记录: `data/predictions.db`

### 分析层
- 日内分析: `analyzers/intraday_gold.py`
- 准确率追踪: `analyzers/accuracy_tracker.py`
- 基金推荐: `analyzers/fund_recommender.py`

### 服务层
- 黄金服务: `services/gold_intraday_service.py`
- 基金服务: `services/fund_analysis_service.py`
- 股票服务: `services/stock_analysis_service.py`

### 工具层
- 日内CLI: `tools/intraday_cli.py`
- 基金CLI: `tools/fund_cli.py`
- 股票CLI: `tools/stock_cli.py`

---

*主看板生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存主看板
        master_file = self.dashboard_dir / f"master_{datetime.now().strftime('%Y%m%d')}.md"
        with open(master_file, 'w', encoding='utf-8') as f:
            f.write(master)
        
        logger.info(f"[看板服务] 主看板已保存: {master_file}")
        return master_file


def main():
    """主函数"""
    print("="*70)
    print("🎯 统一看板服务")
    print("="*70)
    
    service = DashboardService()
    
    # 显示摘要
    service.display_summary()
    
    # 生成所有看板
    print("\n📄 生成所有看板...")
    print("-"*70)
    
    dashboards = service.generate_all_dashboards()
    
    # 生成主看板
    print("\n📊 生成主看板...")
    master_file = service.generate_master_dashboard()
    print(f"   ✅ 主看板: {master_file}\n")
    
    print("="*70)
    print("✅ 所有看板生成完成!")
    print("="*70)
    
    print("\n📁 生成的看板文件:")
    for name, path in dashboards.items():
        print(f"  - {name}: {path}")
    print(f"  - master: {master_file}")


if __name__ == "__main__":
    main()
