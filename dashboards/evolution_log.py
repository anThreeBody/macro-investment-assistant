#!/usr/bin/env python3
"""
系统进化日志
记录系统的优化调整历史
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EvolutionRecord:
    """进化记录"""
    date: str               # 日期
    version: str            # 版本号
    phase: str              # 阶段
    change_type: str        # 变更类型 (feature/fix/optimize/refactor)
    title: str              # 标题
    description: str        # 描述
    impact: str             # 影响范围
    author: str             # 作者
    status: str             # 状态 (completed/pending)


class EvolutionLog:
    """系统进化日志"""
    
    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = str(Path(__file__).parent.parent / "docs")
        
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / "evolution_log.json"
        
        # 初始化日志文件
        if not self.log_file.exists():
            self._init_log()
        
        logger.info("[进化日志] 初始化完成")
    
    def _init_log(self):
        """初始化日志文件"""
        initial_records = [
            {
                "date": "2026-03-24",
                "version": "V1.0.0",
                "phase": "Phase 1",
                "change_type": "feature",
                "title": "系统初始化",
                "description": "创建基础架构，实现数据获取、分析、预测核心功能",
                "impact": "全部模块",
                "author": "System",
                "status": "completed"
            },
            {
                "date": "2026-03-25",
                "version": "V2.0.0",
                "phase": "Phase 2",
                "change_type": "feature",
                "title": "输出层与通知层",
                "description": "添加简报生成、图表生成、告警通知功能",
                "impact": "presenters/, notifiers/",
                "author": "System",
                "status": "completed"
            },
            {
                "date": "2026-03-26",
                "version": "V3.0.0",
                "phase": "Phase 3",
                "change_type": "feature",
                "title": "数据源增强",
                "description": "添加多层级数据源回退机制 (AKShare → Yahoo → Investing → Web → Browser)",
                "impact": "data_sources/",
                "author": "System",
                "status": "completed"
            },
            {
                "date": "2026-03-27",
                "version": "V4.0.0",
                "phase": "Phase 4",
                "change_type": "feature",
                "title": "时序预测与验证",
                "description": "添加简单时序预测模型和预测验证机制",
                "impact": "predictors/, analyzers/accuracy_tracker.py",
                "author": "System",
                "status": "completed"
            },
            {
                "date": "2026-03-31",
                "version": "V5.0.0",
                "phase": "Phase 5 Stage 1",
                "change_type": "feature",
                "title": "黄金日内分析",
                "description": "添加小时级黄金分析和实时推送功能",
                "impact": "analyzers/intraday_gold.py, notifiers/realtime_pusher.py",
                "author": "System",
                "status": "completed"
            },
            {
                "date": "2026-04-01",
                "version": "V5.1.0",
                "phase": "Phase 5 Stage 2",
                "change_type": "feature",
                "title": "基金分析升级",
                "description": "添加5种风险画像和具体买卖时机建议",
                "impact": "analyzers/fund_recommender.py, analyzers/fund_timing_advisor.py",
                "author": "System",
                "status": "completed"
            },
            {
                "date": "2026-04-01",
                "version": "V5.2.0",
                "phase": "Phase 5 Stage 3",
                "change_type": "feature",
                "title": "股票分析升级",
                "description": "添加具体买卖建议和详细分析理由",
                "impact": "analyzers/stock_recommender.py, analyzers/stock_reason_detailer.py",
                "author": "System",
                "status": "completed"
            },
            {
                "date": "2026-04-01",
                "version": "V5.3.0",
                "phase": "Phase 5 Stage 4",
                "change_type": "feature",
                "title": "系统透明化",
                "description": "添加数据资产看板、准确率看板、进化日志",
                "impact": "dashboards/",
                "author": "System",
                "status": "completed"
            }
        ]
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(initial_records, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[进化日志] 已初始化: {self.log_file}")
    
    def load_records(self) -> List[Dict]:
        """加载所有记录"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[进化日志] 加载失败: {e}")
            return []
    
    def save_records(self, records: List[Dict]):
        """保存记录"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def add_record(self, record: EvolutionRecord):
        """添加新记录"""
        records = self.load_records()
        records.append(asdict(record))
        self.save_records(records)
        logger.info(f"[进化日志] 添加记录: {record.title}")
    
    def get_records_by_phase(self, phase: str) -> List[Dict]:
        """按阶段获取记录"""
        records = self.load_records()
        return [r for r in records if phase in r.get("phase", "")]
    
    def get_records_by_type(self, change_type: str) -> List[Dict]:
        """按类型获取记录"""
        records = self.load_records()
        return [r for r in records if r.get("change_type") == change_type]
    
    def get_latest_records(self, n: int = 10) -> List[Dict]:
        """获取最新记录"""
        records = self.load_records()
        return records[-n:] if len(records) >= n else records
    
    def generate_changelog(self) -> str:
        """生成变更日志"""
        records = self.load_records()
        
        changelog = "# 📋 系统进化日志\n\n"
        changelog += f"**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        changelog += "---\n\n"
        
        # 按版本分组
        versions = {}
        for record in records:
            version = record.get("version", "Unknown")
            if version not in versions:
                versions[version] = []
            versions[version].append(record)
        
        # 按版本倒序
        for version in sorted(versions.keys(), reverse=True):
            changelog += f"## {version}\n\n"
            
            for record in versions[version]:
                status_icon = "✅" if record.get("status") == "completed" else "🔄"
                type_icon = {
                    "feature": "✨",
                    "fix": "🐛",
                    "optimize": "⚡",
                    "refactor": "♻️"
                }.get(record.get("change_type"), "📝")
                
                changelog += f"### {status_icon} {type_icon} {record['title']}\n\n"
                changelog += f"- **日期**: {record['date']}\n"
                changelog += f"- **阶段**: {record['phase']}\n"
                changelog += f"- **类型**: {record['change_type']}\n"
                changelog += f"- **描述**: {record['description']}\n"
                changelog += f"- **影响**: {record['impact']}\n"
                changelog += f"- **状态**: {record['status']}\n\n"
            
            changelog += "---\n\n"
        
        return changelog
    
    def generate_summary(self) -> str:
        """生成进化摘要"""
        records = self.load_records()
        
        # 统计
        total_records = len(records)
        completed = sum(1 for r in records if r.get("status") == "completed")
        pending = total_records - completed
        
        type_counts = {}
        for r in records:
            t = r.get("change_type", "other")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        summary = f"""# 📊 系统进化摘要

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 总体统计

| 指标 | 数值 |
|------|------|
| 总变更数 | {total_records} |
| 已完成 | {completed} ✅ |
| 进行中 | {pending} 🔄 |

### 按类型统计

| 类型 | 数量 | 图标 |
|------|------|------|
"""
        
        for t, count in sorted(type_counts.items()):
            icon = {"feature": "✨", "fix": "🐛", "optimize": "⚡", "refactor": "♻️"}.get(t, "📝")
            summary += f"| {t} | {count} | {icon} |\n"
        
        summary += f"""

---

## 🔄 最近变更

"""
        
        latest = self.get_latest_records(5)
        for record in latest:
            status_icon = "✅" if record.get("status") == "completed" else "🔄"
            summary += f"- {status_icon} **{record['date']}** - {record['title']} ({record['phase']})\n"
        
        summary += f"""

---

## 📊 版本演进

"""
        
        versions = sorted(set(r.get("version", "Unknown") for r in records), reverse=True)
        for i, version in enumerate(versions, 1):
            version_records = [r for r in records if r.get("version") == version]
            summary += f"{i}. **{version}** - {len(version_records)} 项变更\n"
        
        summary += f"""

---

## 💡 关键里程碑

"""
        
        milestones = [
            ("V1.0.0", "系统初始化完成"),
            ("V2.0.0", "输出与通知层完成"),
            ("V3.0.0", "多数据源回退机制完成"),
            ("V4.0.0", "时序预测与验证完成"),
            ("V5.0.0", "黄金日内分析完成"),
            ("V5.3.0", "系统透明化完成")
        ]
        
        for version, desc in milestones:
            status = "✅" if version in versions else "⏳"
            summary += f"- {status} **{version}** - {desc}\n"
        
        summary += f"""

---

*日志生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return summary
    
    def save_changelog(self):
        """保存变更日志"""
        changelog = self.generate_changelog()
        changelog_file = self.log_dir / "EVOLUTION_LOG.md"
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(changelog)
        logger.info(f"[进化日志] 已保存: {changelog_file}")
        return changelog_file
    
    def display_summary(self):
        """显示摘要"""
        summary = self.generate_summary()
        print(summary)


def demo_evolution_log():
    """演示系统进化日志"""
    print("="*70)
    print("📋 系统进化日志演示")
    print("="*70)
    
    log = EvolutionLog()
    
    print("\n📊 总体统计:")
    records = log.load_records()
    completed = sum(1 for r in records if r.get("status") == "completed")
    print(f"  总变更数: {len(records)}")
    print(f"  已完成: {completed} ✅")
    print(f"  进行中: {len(records) - completed} 🔄")
    
    print("\n🔄 最近变更:")
    for record in log.get_latest_records(5):
        status = "✅" if record.get("status") == "completed" else "🔄"
        print(f"  {status} {record['date']} - {record['title']} ({record['phase']})")
    
    print(f"\n{'='*70}")
    print("📄 生成进化摘要")
    print(f"{'='*70}")
    
    log.display_summary()
    
    # 保存变更日志
    changelog_file = log.save_changelog()
    print(f"\n✅ 变更日志已保存: {changelog_file}")
    
    print("\n" + "="*70)
    print("✅ 系统进化日志演示完成!")
    print("="*70)


if __name__ == "__main__":
    demo_evolution_log()
